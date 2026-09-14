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
from uuid import UUID, uuid4

import pytest

from prd_04_link_routing.errors import BookingOverlapError
from prd_04_link_routing.models import (
    Booking,
    BookingStatus,
    SourceLink,
    SourceLinkStatus,
)
from prd_04_link_routing.services.bookings import BookingService


class FakeSourceLinkRepository:
    def __init__(self, source_links: list[SourceLink]) -> None:
        self.items = {source_link.id: source_link for source_link in source_links}

    def get_by_id(self, source_link_id: UUID) -> SourceLink | None:
        return self.items.get(source_link_id)


class FakeBookingRepository:
    def __init__(self) -> None:
        self.items: dict[UUID, Booking] = {}

    def get_by_id(self, booking_id: UUID) -> Booking | None:
        return self.items.get(booking_id)

    def save_if_no_schedule_overlap(self, booking: Booking) -> Booking:
        for existing in self.items.values():
            if (
                existing.source_link_id == booking.source_link_id
                and existing.status is BookingStatus.SCHEDULED
                and booking.status is BookingStatus.SCHEDULED
                and existing.starts_at < booking.ends_at
                and booking.starts_at < existing.ends_at
                and existing.id != booking.id
            ):
                raise BookingOverlapError("Booking overlaps with an existing booking.")

        self.items[booking.id] = booking
        return booking

    def cancel(
        self,
        booking_id: UUID,
        canceled_at: datetime,
    ) -> Booking | None:
        booking = self.items.get(booking_id)

        if booking is None:
            return None

        canceled = Booking(
            id=booking.id,
            source_link_id=booking.source_link_id,
            target_url=booking.target_url,
            starts_at=booking.starts_at,
            ends_at=booking.ends_at,
            status=BookingStatus.CANCELED,
            created_by_user_id=booking.created_by_user_id,
            created_at=booking.created_at,
            updated_at=canceled_at,
        )
        self.items[booking_id] = canceled
        return canceled

    def list_by_source_link(
        self,
        source_link_id: UUID,
        *,
        starts_at: datetime | None = None,
        ends_at: datetime | None = None,
    ) -> list[Booking]:
        return [
            booking
            for booking in self.items.values()
            if booking.source_link_id == source_link_id
        ]

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


@pytest.fixture
def repositories(
    source_link: SourceLink,
) -> tuple[FakeSourceLinkRepository, FakeBookingRepository]:
    return (
        FakeSourceLinkRepository([source_link]),
        FakeBookingRepository(),
    )


@pytest.fixture
def service(
    repositories: tuple[
        FakeSourceLinkRepository,
        FakeBookingRepository,
    ],
) -> BookingService:
    source_links, bookings = repositories
    return BookingService(source_links, bookings)


def test_create_booking_for_owner(
    service: BookingService,
    source_link: SourceLink,
) -> None:
    starts_at = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)
    ends_at = datetime(2026, 9, 14, 13, 0, tzinfo=UTC)

    booking = service.create(
        source_link_id=source_link.id,
        actor_user_id="user-123",
        target_url="https://example.com/campaign",
        starts_at=starts_at,
        ends_at=ends_at,
    )

    assert booking is not None
    assert booking.source_link_id == source_link.id
    assert booking.created_by_user_id == "user-123"
    assert booking.status is BookingStatus.SCHEDULED
    assert booking.starts_at == starts_at
    assert booking.ends_at == ends_at

def test_create_booking_rejects_non_owner(
    service: BookingService,
    source_link: SourceLink,
) -> None:
    booking = service.create(
        source_link_id=source_link.id,
        actor_user_id="different-user",
        target_url="https://example.com/campaign",
        starts_at=datetime(2026, 9, 14, 12, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 14, 13, 0, tzinfo=UTC),
    )

    assert booking is None

def test_create_booking_rejects_invalid_window(
    service: BookingService,
    source_link: SourceLink,
) -> None:
    with pytest.raises(ValueError):
        service.create(
            source_link_id=source_link.id,
            actor_user_id="user-123",
            target_url="https://example.com/campaign",
            starts_at=datetime(2026, 9, 14, 13, 0, tzinfo=UTC),
            ends_at=datetime(2026, 9, 14, 12, 0, tzinfo=UTC),
        )

def test_create_booking_rejects_overlap(
    service: BookingService,
    source_link: SourceLink,
) -> None:
    starts_at = datetime(2026, 9, 14, 12, 0, tzinfo=UTC)
    ends_at = datetime(2026, 9, 14, 13, 0, tzinfo=UTC)

    service.create(
        source_link_id=source_link.id,
        actor_user_id="user-123",
        target_url="https://example.com/first",
        starts_at=starts_at,
        ends_at=ends_at,
    )

    with pytest.raises(BookingOverlapError):
        service.create(
            source_link_id=source_link.id,
            actor_user_id="user-123",
            target_url="https://example.com/second",
            starts_at=starts_at + timedelta(minutes=30),
            ends_at=ends_at + timedelta(minutes=30),
        )

def test_create_booking_allows_adjacent_windows(
    service: BookingService,
    source_link: SourceLink,
) -> None:
    service.create(
        source_link_id=source_link.id,
        actor_user_id="user-123",
        target_url="https://example.com/first",
        starts_at=datetime(2026, 9, 14, 12, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 14, 13, 0, tzinfo=UTC),
    )

    second = service.create(
        source_link_id=source_link.id,
        actor_user_id="user-123",
        target_url="https://example.com/second",
        starts_at=datetime(2026, 9, 14, 13, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 14, 14, 0, tzinfo=UTC),
    )

    assert second is not None

def test_owner_can_cancel_booking(
    service: BookingService,
    source_link: SourceLink,
) -> None:
    booking = service.create(
        source_link_id=source_link.id,
        actor_user_id="user-123",
        target_url="https://example.com/campaign",
        starts_at=datetime(2026, 9, 14, 12, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 14, 13, 0, tzinfo=UTC),
    )
    assert booking is not None

    canceled = service.cancel(
        booking_id=booking.id,
        actor_user_id="user-123",
    )

    assert canceled is not None
    assert canceled.status is BookingStatus.CANCELED

def test_non_owner_cannot_cancel_booking(
    service: BookingService,
    source_link: SourceLink,
) -> None:
    booking = service.create(
        source_link_id=source_link.id,
        actor_user_id="user-123",
        target_url="https://example.com/campaign",
        starts_at=datetime(2026, 9, 14, 12, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 14, 13, 0, tzinfo=UTC),
    )
    assert booking is not None

    canceled = service.cancel(
        booking_id=booking.id,
        actor_user_id="different-user",
    )

    assert canceled is None