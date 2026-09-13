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
from uuid import UUID

from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError

from prd_04_link_routing.models import SourceLink
from prd_04_link_routing.errors import SourceLinkPathConflictError

from .mongo_serializers import (
    source_link_to_document,
    source_link_from_document,
)

class MongoSourceLinkRepository:
    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    def ensure_indexes(self) -> None:
        self._collection.create_index("path", unique=True)
        self._collection.create_index("owner_user_id")

    def create(self, source_link: SourceLink) -> SourceLink:
        try:
            self._collection.insert_one(source_link_to_document(source_link))
        except DuplicateKeyError as error:
            raise SourceLinkPathConflictError(
                f"Source link path '{source_link.path}' is already assigned."
            ) from error
        
        return source_link

    def get_by_id(self, source_link_id: UUID) -> SourceLink | None:
        document = self._collection.find_one({"_id": str(source_link_id)})

        if document is None:
            return None
        
        return source_link_from_document(document)

    def get_by_path(self, path: str) -> SourceLink | None:
        document = self._collection.find_one({"path": path})

        if document is None:
            return None
        
        return source_link_from_document(document)

    def list_by_owner(self, owner_user_id: str) -> Sequence[SourceLink]:
        documents = self._collection.find(
            {"owner_user_id": owner_user_id}
        ).sort("path", 1)        

        return [source_link_from_document(document) for document in documents]

    def update(self, source_link: SourceLink) -> SourceLink:
        try:
            result = self._collection.replace_one(
                {"_id": str(source_link.id)},
                source_link_to_document(source_link),
            )
        except DuplicateKeyError as error:
            raise SourceLinkPathConflictError(
                f"Source link path '{source_link.path}' is already assigned."
            ) from error
        
        if result.matched_count == 0:
            raise LookupError(
                f"Source link with ID '{source_link.id}' not found."
            )

        return source_link