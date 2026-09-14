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

from prd_04_link_routing.models import SourceLinkStatus
from prd_04_link_routing.policies.booking_schedule import is_booking_active
from prd_04_link_routing.policies.source_link_path import normalize_source_link_path
from prd_04_link_routing.repositories.booking_repository import BookingRepository
from prd_04_link_routing.repositories.source_link_repository import SourceLinkRepository

class LinkResolutionService:
    def __init__(
        self,
        source_link_repository: SourceLinkRepository,
        booking_repository: BookingRepository,
    ) -> None:
        self._source_link_repository = source_link_repository
        self._booking_repository = booking_repository

    def resolve_destination(
        self,
        path: str,
        *,
        at_utc: datetime | None = None
    ) -> str | None:
        normalized_path = normalize_source_link_path(path)
        source_link = self._source_link_repository.get_by_path(normalized_path)

        if source_link is None or source_link.status is SourceLinkStatus.DISABLED:
            return None

        now = at_utc or datetime.now(UTC)
        bookings = self._booking_repository.list_by_source_link(
            source_link.id,
            starts_at=now,
            ends_at=now,
        )

        for booking in bookings:
            if is_booking_active(booking, now):
                return booking.target_url

        return source_link.default_target_url