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
from prd_04_link_routing.models import Booking, BookingStatus

from persistence.mongo_booking_repository import MongoBookingRepository


def make_booking(
    *,
    source_link_id: UUID | None = None,
    booking_id: UUID | None = None,
    starts_at: datetime | None = None,
    ends_at: datetime | None = None,
    status: BookingStatus = BookingStatus.SCHEDULED,
) -> Booking:
    now = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)
    booking_starts_at = starts_at or datetime(2026, 9, 13, 9, 0, tzinfo=UTC)
    booking_ends_at = ends_at or booking_starts_at + timedelta(hours=1)

    return Booking(
        id=booking_id or uuid4(),
        source_link_id=source_link_id or uuid4(),
        target_url="https://example.com/campaign",
        starts_at=booking_starts_at,
        ends_at=booking_ends_at,
        status=status,
        created_by_user_id="firebase-user-id",
        created_at=now,
        updated_at=now,
    )


def test_get_by_id_returns_none_for_unknown_booking(
    booking_repository: MongoBookingRepository,
) -> None:
    assert booking_repository.get_by_id(uuid4()) is None


def test_save_and_get_by_id(
    booking_repository: MongoBookingRepository,
) -> None:
    booking = make_booking()

    assert booking_repository.save_if_no_schedule_overlap(booking) == booking
    assert booking_repository.get_by_id(booking.id) == booking


def test_list_by_source_link_returns_bookings_in_start_time_order(
    booking_repository: MongoBookingRepository,
) -> None:
    source_link_id = uuid4()
    later_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=datetime(2026, 9, 13, 11, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 12, 0, tzinfo=UTC),
    )
    earlier_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
    )

    booking_repository.save_if_no_schedule_overlap(later_booking)
    booking_repository.save_if_no_schedule_overlap(earlier_booking)

    assert booking_repository.list_by_source_link(source_link_id) == [
        earlier_booking,
        later_booking,
    ]


def test_list_by_source_link_returns_only_the_requested_source_link_bookings(
    booking_repository: MongoBookingRepository,
) -> None:
    source_link_id = uuid4()
    matching_booking = make_booking(source_link_id=source_link_id)
    other_booking = make_booking()

    booking_repository.save_if_no_schedule_overlap(matching_booking)
    booking_repository.save_if_no_schedule_overlap(other_booking)

    assert booking_repository.list_by_source_link(source_link_id) == [
        matching_booking,
    ]


def test_list_by_source_link_filters_bookings_that_overlap_a_time_range(
    booking_repository: MongoBookingRepository,
) -> None:
    source_link_id = uuid4()
    overlapping_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
    )
    outside_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=datetime(2026, 9, 13, 11, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 12, 0, tzinfo=UTC),
    )

    booking_repository.save_if_no_schedule_overlap(overlapping_booking)
    booking_repository.save_if_no_schedule_overlap(outside_booking)

    bookings = booking_repository.list_by_source_link(
        source_link_id,
        starts_at=datetime(2026, 9, 13, 9, 30, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 10, 30, tzinfo=UTC),
    )

    assert bookings == [overlapping_booking]


def test_save_rejects_overlapping_scheduled_bookings(
    booking_repository: MongoBookingRepository,
) -> None:
    source_link_id = uuid4()
    existing_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
    )
    conflicting_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=datetime(2026, 9, 13, 9, 30, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 10, 30, tzinfo=UTC),
    )

    booking_repository.save_if_no_schedule_overlap(existing_booking)

    with pytest.raises(BookingOverlapError, match="overlaps"):
        booking_repository.save_if_no_schedule_overlap(conflicting_booking)


def test_save_allows_adjacent_booking_windows(
    booking_repository: MongoBookingRepository,
) -> None:
    source_link_id = uuid4()
    first_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
    )
    adjacent_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
        ends_at=datetime(2026, 9, 13, 11, 0, tzinfo=UTC),
    )

    booking_repository.save_if_no_schedule_overlap(first_booking)

    assert (
        booking_repository.save_if_no_schedule_overlap(adjacent_booking)
        == adjacent_booking
    )


def test_save_allows_overlapping_bookings_for_different_source_links(
    booking_repository: MongoBookingRepository,
) -> None:
    first_booking = make_booking()
    second_booking = make_booking(
        starts_at=first_booking.starts_at,
        ends_at=first_booking.ends_at,
    )

    booking_repository.save_if_no_schedule_overlap(first_booking)

    assert (
        booking_repository.save_if_no_schedule_overlap(second_booking)
        == second_booking
    )


def test_save_ignores_a_canceled_booking_when_checking_conflicts(
    booking_repository: MongoBookingRepository,
) -> None:
    source_link_id = uuid4()
    canceled_booking = make_booking(
        source_link_id=source_link_id,
        status=BookingStatus.CANCELED,
    )
    candidate_booking = make_booking(
        source_link_id=source_link_id,
        starts_at=canceled_booking.starts_at,
        ends_at=canceled_booking.ends_at,
    )

    booking_repository.save_if_no_schedule_overlap(canceled_booking)

    assert (
        booking_repository.save_if_no_schedule_overlap(candidate_booking)
        == candidate_booking
    )


def test_save_updates_the_same_booking_without_conflicting_with_itself(
    booking_repository: MongoBookingRepository,
) -> None:
    booking = make_booking()
    booking_repository.save_if_no_schedule_overlap(booking)

    updated_booking = Booking(
        id=booking.id,
        source_link_id=booking.source_link_id,
        target_url="https://example.com/updated",
        starts_at=booking.starts_at,
        ends_at=booking.ends_at + timedelta(hours=1),
        status=booking.status,
        created_by_user_id=booking.created_by_user_id,
        created_at=booking.created_at,
        updated_at=datetime(2026, 9, 13, 8, 30, tzinfo=UTC),
    )

    assert (
        booking_repository.save_if_no_schedule_overlap(updated_booking)
        == updated_booking
    )
    assert booking_repository.get_by_id(booking.id) == updated_booking


def test_cancel_marks_a_booking_as_canceled(
    booking_repository: MongoBookingRepository,
) -> None:
    booking = make_booking()
    booking_repository.save_if_no_schedule_overlap(booking)
    canceled_at = datetime(2026, 9, 13, 8, 30, tzinfo=UTC)

    canceled_booking = booking_repository.cancel(booking.id, canceled_at)

    assert canceled_booking is not None
    assert canceled_booking.status is BookingStatus.CANCELED
    assert canceled_booking.updated_at == canceled_at


def test_cancel_returns_none_for_an_unknown_booking(
    booking_repository: MongoBookingRepository,
) -> None:
    assert (
        booking_repository.cancel(
            uuid4(),
            datetime(2026, 9, 13, 8, 30, tzinfo=UTC),
        )
        is None
    )