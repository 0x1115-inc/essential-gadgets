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

from datetime import datetime, UTC
from collections.abc import Iterable

from prd_04_link_routing.errors import DomainValidationError
from prd_04_link_routing.models import Booking, BookingStatus

def require_utc(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DomainValidationError(f"Datetime value for '{field_name}' must be in UTC.")

    if value.utcoffset() != UTC.utcoffset(value):
        raise DomainValidationError(f"Datetime value for '{field_name}' must be in UTC.")

    return value

def validate_booking_window(
        starts_at_utc: datetime,
        ends_at_utc: datetime
) -> None:
    require_utc(starts_at_utc, "starts_at_utc")
    require_utc(ends_at_utc, "ends_at_utc")

    if ends_at_utc <= starts_at_utc:
        raise DomainValidationError("Booking window 'ends_at_utc' must be after 'starts_at_utc'.")

def is_booking_active(booking: Booking, at_utc: datetime) -> bool:
    require_utc(at_utc, "at_utc")
    return (
        booking.status is BookingStatus.SCHEDULED
        and booking.starts_at <= at_utc < booking.ends_at
    )

def booking_windows_overlap(
        first_starts_at_utc: datetime,
        first_ends_at_utc: datetime,
        second_starts_at_utc: datetime,
        second_ends_at_utc: datetime
) -> bool:
    validate_booking_window(first_starts_at_utc, first_ends_at_utc)
    validate_booking_window(second_starts_at_utc, second_ends_at_utc)

    return (
        first_starts_at_utc < second_ends_at_utc
        and second_starts_at_utc < first_ends_at_utc
    )

def ensure_no_scheduled_booking_overlap(
        candidate: Booking,
        existing_bookings: Iterable[Booking]
) -> None:
    validate_booking_window(candidate.starts_at, candidate.ends_at)

    if candidate.status is BookingStatus.CANCELED:
        return

    for existing in existing_bookings:
        if existing.id == candidate.id:
            continue

        if (
            existing.source_link_id == candidate.source_link_id
            and existing.status is BookingStatus.SCHEDULED
            and booking_windows_overlap(
                candidate.starts_at,
                candidate.ends_at,
                existing.starts_at,
                existing.ends_at
            )
        ):
            raise DomainValidationError("Candidate booking overlaps with an existing scheduled booking.")