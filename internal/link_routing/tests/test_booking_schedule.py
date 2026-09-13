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
from uuid import uuid4, UUID

import pytest

from prd_04_link_routing.errors import DomainValidationError, BookingOverlapError
from prd_04_link_routing.models import Booking, BookingStatus
from prd_04_link_routing.policies.booking_schedule import (
    booking_windows_overlap,
    ensure_no_scheduled_booking_overlap,    
    is_booking_active,
    validate_booking_window,
)


def make_booking(
    starts_at_utc: datetime,
    ends_at_utc: datetime,
    status: BookingStatus = BookingStatus.SCHEDULED,
    source_link_id: UUID | None = None,
    booking_id: UUID | None = None
) -> Booking:
    now = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)

    return Booking(
        id=booking_id or uuid4(),
        source_link_id=source_link_id or uuid4(),
        target_url="https://example.com/temporary",
        starts_at=starts_at_utc,
        ends_at=ends_at_utc,
        status=status,
        created_by_user_id="firebase-user-id",
        created_at=now,
        updated_at=now,
    )


def test_validate_booking_window_accepts_a_valid_utc_window() -> None:
    starts_at_utc = datetime(2026, 9, 13, 9, 0, tzinfo=UTC)
    ends_at_utc = starts_at_utc + timedelta(hours=1)

    validate_booking_window(starts_at_utc, ends_at_utc)


@pytest.mark.parametrize(
    ("starts_at_utc", "ends_at_utc"),
    [
        (
            datetime(2026, 9, 13, 9, 0),
            datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
        ),
        (
            datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
            datetime(2026, 9, 13, 10, 0),
        ),
    ],
)
def test_validate_booking_window_rejects_naive_timestamps(
    starts_at_utc: datetime,
    ends_at_utc: datetime,
) -> None:
    with pytest.raises(DomainValidationError, match="must be in UTC"):
        validate_booking_window(starts_at_utc, ends_at_utc)


def test_validate_booking_window_rejects_equal_start_and_end() -> None:
    at_utc = datetime(2026, 9, 13, 9, 0, tzinfo=UTC)

    with pytest.raises(DomainValidationError, match="must be after"):
        validate_booking_window(at_utc, at_utc)


def test_booking_is_active_at_start_but_not_at_end() -> None:
    starts_at_utc = datetime(2026, 9, 13, 9, 0, tzinfo=UTC)
    ends_at_utc = starts_at_utc + timedelta(hours=1)
    booking = make_booking(starts_at_utc, ends_at_utc)

    assert is_booking_active(booking, starts_at_utc)
    assert not is_booking_active(booking, ends_at_utc)


def test_canceled_booking_is_not_active() -> None:
    starts_at_utc = datetime(2026, 9, 13, 9, 0, tzinfo=UTC)
    ends_at_utc = starts_at_utc + timedelta(hours=1)
    booking = make_booking(
        starts_at_utc,
        ends_at_utc,
        status=BookingStatus.CANCELED,
    )

    assert not is_booking_active(booking, starts_at_utc)

def test_adjacent_booking_windows_do_not_overlap() -> None:
    first_starts_at_utc = datetime(2026, 9, 13, 9, 0, tzinfo=UTC)
    first_ends_at_utc = first_starts_at_utc + timedelta(hours=1)
    second_starts_at_utc = first_ends_at_utc
    second_ends_at_utc = second_starts_at_utc + timedelta(hours=1)

    assert not booking_windows_overlap(
        first_starts_at_utc,
        first_ends_at_utc,
        second_starts_at_utc,
        second_ends_at_utc,
    )


def test_overlapping_booking_windows_overlap() -> None:
    first_starts_at_utc = datetime(2026, 9, 13, 9, 0, tzinfo=UTC)
    first_ends_at_utc = first_starts_at_utc + timedelta(hours=2)
    second_starts_at_utc = first_starts_at_utc + timedelta(hours=1)
    second_ends_at_utc = second_starts_at_utc + timedelta(hours=2)

    assert booking_windows_overlap(
        first_starts_at_utc,
        first_ends_at_utc,
        second_starts_at_utc,
        second_ends_at_utc,
    )


def test_ensure_no_scheduled_booking_overlap_rejects_same_source_link() -> None:
    source_link_id = uuid4()
    existing = make_booking(
        datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
        source_link_id=source_link_id,
    )
    candidate = make_booking(
        datetime(2026, 9, 13, 9, 30, tzinfo=UTC),
        datetime(2026, 9, 13, 10, 30, tzinfo=UTC),
        source_link_id=source_link_id,
    )

    with pytest.raises(BookingOverlapError, match="overlaps"):
        ensure_no_scheduled_booking_overlap(candidate, [existing])


def test_ensure_no_scheduled_booking_overlap_allows_different_source_links() -> None:
    existing = make_booking(
        datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
    )
    candidate = make_booking(
        datetime(2026, 9, 13, 9, 30, tzinfo=UTC),
        datetime(2026, 9, 13, 10, 30, tzinfo=UTC),
    )

    ensure_no_scheduled_booking_overlap(candidate, [existing])


def test_ensure_no_scheduled_booking_overlap_ignores_canceled_booking() -> None:
    source_link_id = uuid4()
    existing = make_booking(
        datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
        status=BookingStatus.CANCELED,
        source_link_id=source_link_id,
    )
    candidate = make_booking(
        datetime(2026, 9, 13, 9, 30, tzinfo=UTC),
        datetime(2026, 9, 13, 10, 30, tzinfo=UTC),
        source_link_id=source_link_id,
    )

    ensure_no_scheduled_booking_overlap(candidate, [existing])


def test_ensure_no_scheduled_booking_overlap_ignores_the_booking_being_edited() -> None:
    source_link_id = uuid4()
    booking_id = uuid4()
    existing = make_booking(
        datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
        source_link_id=source_link_id,
        booking_id=booking_id,
    )
    candidate = make_booking(
        datetime(2026, 9, 13, 9, 0, tzinfo=UTC),
        datetime(2026, 9, 13, 10, 0, tzinfo=UTC),
        source_link_id=source_link_id,
        booking_id=booking_id,
    )

    ensure_no_scheduled_booking_overlap(candidate, [existing])