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

import os
from collections.abc import Iterator

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection

from persistence.mongo_source_link_repository import MongoSourceLinkRepository
from persistence.mongo_booking_repository import MongoBookingRepository 

@pytest.fixture
def source_link_repository() -> Iterator[MongoSourceLinkRepository]:
    mongodb_uri = os.getenv(
        "TEST_MONGODB_URI",
        "mongodb://localhost:27017",
    )
    client = MongoClient(mongodb_uri, tz_aware=True)
    database = client["prd_04_link_routing_test"]
    collection: Collection = database["source_links"]

    collection.drop()

    repository = MongoSourceLinkRepository(collection)
    repository.ensure_indexes()

    yield repository

    collection.drop()
    client.close()

@pytest.fixture
def booking_repository() -> Iterator[MongoBookingRepository]:
    mongodb_uri = os.getenv(
        "TEST_MONGODB_URI",
        "mongodb://localhost:27017",
    )
    client = MongoClient(mongodb_uri, tz_aware=True)
    database = client["prd_04_link_routing_test"]
    collection: Collection = database["bookings"]

    collection.drop()

    repository = MongoBookingRepository(database, collection)
    repository.ensure_indexes()

    yield repository

    collection.drop()
    client.close()