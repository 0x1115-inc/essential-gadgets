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
from uuid import UUID, uuid4

import pytest

from prd_04_link_routing.errors import DomainValidationError
from prd_04_link_routing.models import SourceLink, SourceLinkStatus
from prd_04_link_routing.services.source_links import SourceLinkService

class FakeSourceLinkRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, SourceLink] = {}

    def create(self, source_link: SourceLink) -> SourceLink:
        self.items[source_link.id] = source_link
        return source_link

    def get_by_id(self, source_link_id: UUID) -> SourceLink | None:
        return self.items.get(source_link_id)

    def get_by_path(self, path: str) -> SourceLink | None:
        return next(
            (
                source_link
                for source_link in self.items.values()
                if source_link.path == path
            ),
            None,
        )

    def list_by_owner(self, owner_user_id: str) -> list[SourceLink]:
        return [
            source_link
            for source_link in self.items.values()
            if source_link.owner_user_id == owner_user_id
        ]

    def update(self, source_link: SourceLink) -> SourceLink:
        self.items[source_link.id] = source_link
        return source_link

@pytest.fixture
def repository() -> FakeSourceLinkRepository:
    return FakeSourceLinkRepository()


@pytest.fixture
def service(
    repository: FakeSourceLinkRepository,
) -> SourceLinkService:
    return SourceLinkService(repository)


def make_source_link(
    *,
    owner_user_id: str = "user-123",
    path: str = "events/launch",
) -> SourceLink:
    created_at = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)

    return SourceLink(
        id=uuid4(),
        path=path,
        default_target_url="https://example.com/default",
        owner_user_id=owner_user_id,
        status=SourceLinkStatus.ENABLED,
        created_at=created_at,
        updated_at=created_at,
    )

def test_create_normalizes_path(
    service: SourceLinkService,
) -> None:
    source_link = service.create(
        path=" Events/Launch ",
        default_target_url="https://example.com/default",
        owner_user_id="user-123",
    )

    assert source_link.path == "events/launch"


def test_create_assigns_owner_and_default_status(
    service: SourceLinkService,
) -> None:
    source_link = service.create(
        path="events/launch",
        default_target_url="https://example.com/default",
        owner_user_id="user-123",
    )

    assert source_link.owner_user_id == "user-123"
    assert source_link.status is SourceLinkStatus.ENABLED
    assert isinstance(source_link.id, UUID)
    assert source_link.created_at.tzinfo is UTC
    assert source_link.updated_at.tzinfo is UTC


@pytest.mark.parametrize(
    "target_url",
    [
        "example.com",
        "ftp://example.com/file",
        "/relative/path",
        "",
    ],
)
def test_create_rejects_invalid_target_url(
    service: SourceLinkService,
    target_url: str,
) -> None:
    with pytest.raises(DomainValidationError):
        service.create(
            path="events/launch",
            default_target_url=target_url,
            owner_user_id="user-123",
        )

def test_list_for_owner_returns_only_owned_links(
    service: SourceLinkService,
    repository: FakeSourceLinkRepository,
) -> None:
    owned_link = make_source_link(
        owner_user_id="user-123",
        path="owned",
    )
    other_link = make_source_link(
        owner_user_id="user-456",
        path="other",
    )

    repository.create(owned_link)
    repository.create(other_link)

    assert service.list_for_owner("user-123") == [owned_link]


def test_get_for_owner_returns_owned_link(
    service: SourceLinkService,
    repository: FakeSourceLinkRepository,
) -> None:
    source_link = make_source_link(owner_user_id="user-123")
    repository.create(source_link)

    result = service.get_for_owner(source_link.id, "user-123")

    assert result == source_link


def test_get_for_owner_hides_another_users_link(
    service: SourceLinkService,
    repository: FakeSourceLinkRepository,
) -> None:
    source_link = make_source_link(owner_user_id="user-123")
    repository.create(source_link)

    result = service.get_for_owner(source_link.id, "user-456")

    assert result is None


def test_get_for_owner_returns_none_for_unknown_link(
    service: SourceLinkService,
) -> None:
    assert service.get_for_owner(uuid4(), "user-123") is None

def test_update_changes_target_and_status(
    service: SourceLinkService,
    repository: FakeSourceLinkRepository,
) -> None:
    source_link = make_source_link()
    repository.create(source_link)

    updated = service.update_for_owner(
        source_link.id,
        "user-123",
        default_target_url="https://example.com/updated",
        status=SourceLinkStatus.DISABLED,
    )

    assert updated is not None
    assert updated.default_target_url == "https://example.com/updated"
    assert updated.status is SourceLinkStatus.DISABLED

def test_update_preserves_identity_and_creation_fields(
    service: SourceLinkService,
    repository: FakeSourceLinkRepository,
) -> None:
    source_link = make_source_link()
    repository.create(source_link)

    updated = service.update_for_owner(
        source_link.id,
        "user-123",
        default_target_url="https://example.com/updated",
    )

    assert updated is not None
    assert updated.id == source_link.id
    assert updated.path == source_link.path
    assert updated.owner_user_id == source_link.owner_user_id
    assert updated.created_at == source_link.created_at
    assert updated.updated_at >= source_link.updated_at


def test_update_rejects_invalid_target_url(
    service: SourceLinkService,
    repository: FakeSourceLinkRepository,
) -> None:
    source_link = make_source_link()
    repository.create(source_link)

    with pytest.raises(DomainValidationError):
        service.update_for_owner(
            source_link.id,
            "user-123",
            default_target_url="not-a-url",
        )

def test_update_cannot_be_performed_by_another_user(
    service: SourceLinkService,
    repository: FakeSourceLinkRepository,
) -> None:
    source_link = make_source_link(owner_user_id="user-123")
    repository.create(source_link)

    result = service.update_for_owner(
        source_link.id,
        "user-456",
        default_target_url="https://example.com/updated",
    )

    assert result is None
    assert repository.items[source_link.id] == source_link