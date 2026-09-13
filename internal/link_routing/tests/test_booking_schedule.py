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

from prd_04_link_routing.errors import DomainValidationError
from prd_04_link_routing.models import Booking, BookingStatus
from prd_04_link_routing.policies.booking_schedule import (
    is_booking_active,
    validate_booking_window,
)


def make_booking(
    starts_at_utc: datetime,
    ends_at_utc: datetime,
    status: BookingStatus = BookingStatus.SCHEDULED,
) -> Booking:
    now = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)

    return Booking(
        id=uuid4(),
        source_link_id=uuid4(),
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