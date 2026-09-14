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

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from prd_04_link_routing.models import (
    Booking,
    BookingStatus,
    SourceLink,
    SourceLinkStatus,
)
from prd_04_link_routing.services.link_resolution import (
    LinkResolutionService,
)

class FakeSourceLinkRepository:
    def __init__(self) -> None:
        self.items: dict[str, SourceLink] = {}

    def add(self, source_link: SourceLink) -> None:
        self.items[source_link.path] = source_link

    def get_by_path(self, path: str) -> SourceLink | None:
        return self.items.get(path)


class FakeBookingRepository:
    def __init__(self) -> None:
        self.items: list[Booking] = []

    def add(self, booking: Booking) -> None:
        self.items.append(booking)

    def list_by_source_link(
        self,
        source_link_id,
        *,
        starts_at=None,
        ends_at=None,
    ) -> list[Booking]:
        return [
            booking
            for booking in self.items
            if booking.source_link_id == source_link_id
        ]

@pytest.fixture
def now() -> datetime:
    return datetime(2026, 9, 14, 12, 0, tzinfo=UTC)


@pytest.fixture
def source_link() -> SourceLink:
    timestamp = datetime(2026, 9, 14, 8, 0, tzinfo=UTC)

    return SourceLink(
        id=uuid4(),
        path="events/launch",
        default_target_url="https://example.com/default",
        owner_user_id="user-123",
        status=SourceLinkStatus.ENABLED,
        created_at=timestamp,
        updated_at=timestamp,
    )


def make_booking(
    source_link: SourceLink,
    *,
    starts_at: datetime,
    ends_at: datetime,
    status: BookingStatus = BookingStatus.SCHEDULED,
    target_url: str = "https://example.com/booked",
) -> Booking:
    timestamp = datetime(2026, 9, 14, 8, 0, tzinfo=UTC)

    return Booking(
        id=uuid4(),
        source_link_id=source_link.id,
        target_url=target_url,
        starts_at=starts_at,
        ends_at=ends_at,
        status=status,
        created_by_user_id="user-123",
        created_at=timestamp,
        updated_at=timestamp,
    )

def test_resolve_uses_active_booking_target(
    source_link: SourceLink,
    now: datetime,
) -> None:
    source_links = FakeSourceLinkRepository()
    bookings = FakeBookingRepository()

    source_links.add(source_link)
    bookings.add(
        make_booking(
            source_link,
            starts_at=now - timedelta(hours=1),
            ends_at=now + timedelta(hours=1),
        )
    )

    service = LinkResolutionService(source_links, bookings)

    assert (
        service.resolve_destination("events/launch", at_utc=now)
        == "https://example.com/booked"
    )

def test_resolve_uses_booking_at_exact_start_time(
    source_link: SourceLink,
    now: datetime,
) -> None:
    source_links = FakeSourceLinkRepository()
    bookings = FakeBookingRepository()

    source_links.add(source_link)
    bookings.add(
        make_booking(
            source_link,
            starts_at=now,
            ends_at=now + timedelta(hours=1),
        )
    )

    service = LinkResolutionService(source_links, bookings)

    assert (
        service.resolve_destination("events/launch", at_utc=now)
        == "https://example.com/booked"
    )

def test_resolve_falls_back_at_exact_end_time(
    source_link: SourceLink,
    now: datetime,
) -> None:
    source_links = FakeSourceLinkRepository()
    bookings = FakeBookingRepository()

    source_links.add(source_link)
    bookings.add(
        make_booking(
            source_link,
            starts_at=now - timedelta(hours=1),
            ends_at=now,
        )
    )

    service = LinkResolutionService(source_links, bookings)

    assert (
        service.resolve_destination("events/launch", at_utc=now)
        == "https://example.com/default"
    )

@pytest.mark.parametrize(
    "status, starts_offset, ends_offset",
    [
        (
            BookingStatus.CANCELED,
            timedelta(hours=-1),
            timedelta(hours=1),
        ),
        (
            BookingStatus.SCHEDULED,
            timedelta(hours=1),
            timedelta(hours=2),
        ),
        (
            BookingStatus.SCHEDULED,
            timedelta(hours=-2),
            timedelta(hours=-1),
        ),
    ],
)
def test_resolve_falls_back_when_booking_is_not_active(
    source_link: SourceLink,
    now: datetime,
    status: BookingStatus,
    starts_offset: timedelta,
    ends_offset: timedelta,
) -> None:
    source_links = FakeSourceLinkRepository()
    bookings = FakeBookingRepository()

    source_links.add(source_link)
    bookings.add(
        make_booking(
            source_link,
            starts_at=now + starts_offset,
            ends_at=now + ends_offset,
            status=status,
        )
    )

    service = LinkResolutionService(source_links, bookings)

    assert (
        service.resolve_destination("events/launch", at_utc=now)
        == "https://example.com/default"
    )

def test_resolve_returns_none_for_unknown_path(
    now: datetime,
) -> None:
    service = LinkResolutionService(
        FakeSourceLinkRepository(),
        FakeBookingRepository(),
    )

    assert service.resolve_destination("unknown", at_utc=now) is None

def test_resolve_returns_none_for_disabled_source_link(
    source_link: SourceLink,
    now: datetime,
) -> None:
    source_links = FakeSourceLinkRepository()
    source_links.add(
        SourceLink(
            id=source_link.id,
            path=source_link.path,
            default_target_url=source_link.default_target_url,
            owner_user_id=source_link.owner_user_id,
            status=SourceLinkStatus.DISABLED,
            created_at=source_link.created_at,
            updated_at=source_link.updated_at,
        )
    )

    service = LinkResolutionService(
        source_links,
        FakeBookingRepository(),
    )

    assert service.resolve_destination(source_link.path, at_utc=now) is None

def test_resolve_normalizes_path_before_lookup(
    source_link: SourceLink,
    now: datetime,
) -> None:
    source_links = FakeSourceLinkRepository()
    source_links.add(source_link)

    service = LinkResolutionService(
        source_links,
        FakeBookingRepository(),
    )

    assert (
        service.resolve_destination(" Events/Launch ", at_utc=now)
        == "https://example.com/default"
    )