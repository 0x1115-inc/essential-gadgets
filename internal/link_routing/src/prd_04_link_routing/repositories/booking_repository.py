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

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol
from uuid import UUID

from prd_04_link_routing.models import Booking


class BookingRepository(Protocol):
    def get_by_id(self, booking_id: UUID) -> Booking | None:
        """Retrieve a booking by its ID.
        Args:
            booking_id (UUID): The ID of the booking to retrieve.

        Returns:
            Booking | None: The booking with the specified ID, or None if not found.

        """

    def list_by_source_link(
            self,
            source_link_id: UUID,
            *,
            starts_at: datetime | None = None,
            ends_at: datetime | None = None,
    ) -> Sequence[Booking]:
        """List bookings by the source link ID, optionally filtered by start and end times.
        Args:
            source_link_id (UUID): The ID of the source link to filter bookings by.
            starts_at (datetime | None, optional): The start time to filter bookings. Defaults to None.
            ends_at (datetime | None, optional): The end time to filter bookings. Defaults to None.

        Returns:
            Sequence[Booking]: A sequence of bookings matching the specified criteria.

        """

    def save_if_no_schedule_overlap(self, booking: Booking) -> Booking:
        """Save the booking if there is no schedule overlap.
        The conflict check and write must occur in one datastore transaction or
        equivalent atomic operation to ensure consistency.

        Args:
            booking (Booking): The booking to save.

        Returns:
            Booking: The saved booking.

        Raises:
            BookingOverlapError: If there is a schedule overlap with an existing booking.

        """

    def cancel(self, booking_id: UUID, canceled_at: datetime) -> Booking | None:
        """Cancel the booking with the specified ID at the given time.
        Args:
            booking_id (UUID): The ID of the booking to cancel.
            canceled_at (datetime): The time at which the booking is canceled.

        Returns:
            Booking | None: The canceled booking, or None if the booking was not found.

        """