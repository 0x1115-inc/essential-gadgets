#  Copyright 0x1115 Inc <info@0x1115.com>
# 
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from prd_04_link_routing.errors import SourceLinkPathConflictError
from prd_04_link_routing.models import SourceLink, SourceLinkStatus

from persistence.mongo_source_link_repository import MongoSourceLinkRepository


def make_source_link(
    *,
    path: str = "events/launch",
    owner_user_id: str | None = "user-123",
    default_target_url: str = "https://example.com/default",
) -> SourceLink:
    now = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)

    return SourceLink(
        id=uuid4(),
        path=path,
        default_target_url=default_target_url,
        owner_user_id=owner_user_id,
        status=SourceLinkStatus.ENABLED,
        created_at=now,
        updated_at=now,
    )


def test_create_and_get_by_id(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    source_link = make_source_link()

    created = source_link_repository.create(source_link)

    assert created == source_link
    assert source_link_repository.get_by_id(source_link.id) == source_link


def test_get_by_id_returns_none_for_unknown_source_link(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    assert source_link_repository.get_by_id(uuid4()) is None


def test_get_by_path_returns_the_source_link(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    source_link = make_source_link(path="events/keynote")
    source_link_repository.create(source_link)

    assert source_link_repository.get_by_path("events/keynote") == source_link


def test_get_by_path_returns_none_for_an_unknown_path(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    assert source_link_repository.get_by_path("unknown-path") is None


def test_list_by_owner_returns_only_owned_links_sorted_by_path(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    later_path = make_source_link(path="zeta", owner_user_id="user-123")
    earlier_path = make_source_link(path="alpha", owner_user_id="user-123")
    other_owner_link = make_source_link(
        path="other",
        owner_user_id="user-456",
    )
    unowned_link = make_source_link(path="unowned", owner_user_id=None)

    for source_link in (
        later_path,
        earlier_path,
        other_owner_link,
        unowned_link,
    ):
        source_link_repository.create(source_link)

    assert source_link_repository.list_by_owner("user-123") == [
        earlier_path,
        later_path,
    ]


def test_create_rejects_a_duplicate_path(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    source_link_repository.create(make_source_link(path="events/launch"))

    with pytest.raises(SourceLinkPathConflictError, match="already assigned"):
        source_link_repository.create(make_source_link(path="events/launch"))


def test_update_replaces_an_existing_source_link(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    source_link = make_source_link()
    source_link_repository.create(source_link)

    updated = SourceLink(
        id=source_link.id,
        path=source_link.path,
        default_target_url="https://example.com/updated",
        owner_user_id="user-456",
        status=SourceLinkStatus.DISABLED,
        created_at=source_link.created_at,
        updated_at=datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
    )

    assert source_link_repository.update(updated) == updated
    assert source_link_repository.get_by_id(updated.id) == updated


def test_update_rejects_an_unknown_source_link(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    with pytest.raises(LookupError, match="not found"):
        source_link_repository.update(make_source_link())


def test_update_rejects_a_path_assigned_to_another_source_link(
    source_link_repository: MongoSourceLinkRepository,
) -> None:
    existing = make_source_link(path="events/launch")
    source_link = make_source_link(path="events/keynote")

    source_link_repository.create(existing)
    source_link_repository.create(source_link)

    conflicting_update = SourceLink(
        id=source_link.id,
        path=existing.path,
        default_target_url=source_link.default_target_url,
        owner_user_id=source_link.owner_user_id,
        status=source_link.status,
        created_at=source_link.created_at,
        updated_at=source_link.updated_at,
    )

    with pytest.raises(SourceLinkPathConflictError, match="already assigned"):
        source_link_repository.update(conflicting_update)