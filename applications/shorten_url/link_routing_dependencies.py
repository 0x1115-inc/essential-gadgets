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

from dataclasses import dataclass
from functools import lru_cache
import os
import re

from pymongo import MongoClient

from persistence import MongoBookingRepository, MongoSourceLinkRepository


@dataclass(frozen=True, slots=True)
class LinkRoutingDependencies:
    source_link_repository: MongoSourceLinkRepository
    booking_repository: MongoBookingRepository

@lru_cache
def get_link_routing_dependencies() -> LinkRoutingDependencies:
    mongodb_uri = os.environ["MONGODB_URI"]
    database_name = os.environ["MONGODB_DATABASE_NAME"]
    hostname = os.getenv("APP_HOSTNAME", "localhost:8080")
    collection_prefix = re.sub(r"[^a-zA-Z0-9]", "_", hostname)

    client = MongoClient(mongodb_uri, tz_aware=True)
    database = client[database_name]

    source_link_repository = MongoSourceLinkRepository(
        database[f"{collection_prefix}_source_links"]
    )
    booking_repository = MongoBookingRepository(
        database,
        database[f"{collection_prefix}_bookings"]
    )

    source_link_repository.ensure_indexes()
    booking_repository.ensure_indexes()

    return LinkRoutingDependencies(
        source_link_repository=source_link_repository,
        booking_repository=booking_repository,
    )