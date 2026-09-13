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
from uuid import UUID

from pymongo import ReturnDocument
from pymongo.database import Database
from pymongo.collection import Collection

from prd_04_link_routing.errors import BookingOverlapError
from prd_04_link_routing.models.booking import Booking, BookingStatus
from prd_04_link_routing.policies.booking_schedule import (
    require_utc,
    validate_booking_window
)

from .mongo_serializers import booking_from_document, booking_to_document

class MongoBookingRepository:
    def __init__(
        self,
        database: Database,
        collection: Collection,
    ) -> None:
        self._database = database
        self._collection = collection

    def ensure_indexes(self) -> None:
        self._collection.create_index(
            [
                ("source_link_id", 1),
                ("status", 1),
                ("starts_at", 1),
                ("ends_at", 1),
            ]
        )

    def get_by_id(self, booking_id: UUID) -> Booking | None:
        document = self._collection.find_one({"_id": str(booking_id)})

        if document is None:
        
            return None
        return booking_from_document(document)

    def list_by_source_link(
        self,
        source_link_id: UUID,
        *,
        starts_at: datetime | None = None,
        ends_at: datetime | None = None,
    ) -> Sequence[Booking]:
        query: dict[str, object] = {
            "source_link_id": str(source_link_id)
        }

        if starts_at is not None:
            require_utc(starts_at, "starts_at")
            query["ends_at"] = {"$gt": starts_at}

        if ends_at is not None:
            require_utc(ends_at, "ends_at")
            starts_at_filter = query.setdefault("starts_at", {})

            if not isinstance(starts_at_filter, dict):
                raise TypeError("Invalid starts_at query filter.")

            starts_at_filter["$lt"] = ends_at
        

        documents = self._collection.find(query).sort(
            [("starts_at", 1), ("_id", 1)]
        )

        return [booking_from_document(doc) for doc in documents]


    def save_if_no_schedule_overlap(self, booking: Booking) -> Booking:
        validate_booking_window(booking.starts_at, booking.ends_at)

        with self._database.client.start_session() as session:
            with session.start_transaction():
                if booking.status is BookingStatus.SCHEDULED:
                    conflicting_booking = self._collection.find_one(
                        {
                            "source_link_id": str(booking.source_link_id),
                            "status": BookingStatus.SCHEDULED.value,
                            "_id": {"$ne": str(booking.id)},
                            "starts_at": {"$lt": booking.ends_at},
                            "ends_at": {"$gt": booking.starts_at},
                        },
                        session=session
                    )

                    if conflicting_booking is not None:
                        raise BookingOverlapError(
                            "Candidate booking overlaps with an existing scheduled booking."
                        )

                self._collection.replace_one(
                    {"_id": str(booking.id)},
                    booking_to_document(booking),
                    upsert=True,
                    session=session
                )

        return booking

    def cancel(self, booking_id: UUID, canceled_at: datetime) -> Booking | None:
        require_utc(canceled_at, "canceled_at")

        document = self._collection.find_one_and_update(
            {"_id": str(booking_id)},
            {
                "$set": {
                    "status": BookingStatus.CANCELED.value,
                    "updated_at": canceled_at
                }
            },
            return_document=ReturnDocument.AFTER
        )

        if document is None:
            return None

        return booking_from_document(document)
    