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

from typing import Any
from uuid import UUID

from prd_04_link_routing.models import (
    SourceLink,
    SourceLinkStatus,
    Booking,
    BookingStatus
)


def source_link_to_document(source_link: SourceLink) -> dict[str, Any]:
    return {
        "_id": str(source_link.id),
        "path": source_link.path,
        "default_target_url": source_link.default_target_url,
        "owner_user_id": source_link.owner_user_id,
        "status": source_link.status.value,
        "created_at": source_link.created_at,
        "updated_at": source_link.updated_at,
        "version": 1
    }

def source_link_from_document(document: dict[str, Any]) -> SourceLink:
    return SourceLink(
        id=UUID(document["_id"]),
        path=document["path"],
        default_target_url=document["default_target_url"],
        owner_user_id=document.get("owner_user_id"),
        status=SourceLinkStatus(document["status"]),
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )

def booking_to_document(booking: Booking) -> dict[str, Any]:
    return {
        "_id": str(booking.id),
        "source_link_id": str(booking.source_link_id),
        "target_url": booking.target_url,
        "starts_at": booking.starts_at,
        "ends_at": booking.ends_at,
        "status": booking.status.value,
        "created_by_user_id": booking.created_by_user_id,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at,
        "version": 1
    }

def booking_from_document(document: dict[str, Any]) -> Booking:
    return Booking(
        id=UUID(document["_id"]),
        source_link_id=UUID(document["source_link_id"]),
        target_url=document["target_url"],
        starts_at=document["starts_at"],
        ends_at=document["ends_at"],
        status=BookingStatus(document["status"]),
        created_by_user_id=document["created_by_user_id"],
        created_at=document["created_at"],
        updated_at=document["updated_at"],
    )