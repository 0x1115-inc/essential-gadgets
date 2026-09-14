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

from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from prd_04_link_routing.models import Booking, BookingStatus
from prd_04_link_routing.policies.booking_schedule import validate_booking_window
from prd_04_link_routing.repositories.booking_repository import BookingRepository
from prd_04_link_routing.repositories.source_link_repository import SourceLinkRepository

class BookingService:
    def __init__(
        self,
        source_link_repository: SourceLinkRepository,
        booking_repository: BookingRepository,
    ) -> None:
        self._source_link_repository = source_link_repository
        self._booking_repository = booking_repository

    def create(
        self,
        *,
        source_link_id: UUID,
        actor_user_id: str,
        target_url: str,
        starts_at: datetime,
        ends_at: datetime,
    ) -> Booking | None:
        source_link = self._source_link_repository.get_by_id(source_link_id)
        if source_link is None or source_link.owner_user_id != actor_user_id:
            return None

        validate_booking_window(starts_at, ends_at)
        now = datetime.now(UTC)

        booking = Booking(
            id=uuid4(),
            source_link_id=source_link_id,
            target_url=target_url,
            starts_at=starts_at,
            ends_at=ends_at,
            status=BookingStatus.SCHEDULED,
            created_by_user_id=actor_user_id,
            created_at=now,
            updated_at=now,
        )

        return self._booking_repository.save_if_no_schedule_overlap(booking)

    def cancel(
        self,
        *,
        booking_id: UUID,
        actor_user_id: str,
    ) -> Booking | None:
        booking = self._booking_repository.get_by_id(booking_id)
        if booking is None:
            return None

        source_link = self._source_link_repository.get_by_id(booking.source_link_id)
        if source_link is None or source_link.owner_user_id != actor_user_id:
            return None

        return self._booking_repository.cancel(booking_id, datetime.now(UTC))

        