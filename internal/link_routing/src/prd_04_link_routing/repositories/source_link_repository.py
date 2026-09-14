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
from typing import Protocol

from uuid import UUID

from prd_04_link_routing.models import SourceLink

class SourceLinkRepository(Protocol):
    def create(self, source_link: SourceLink) -> SourceLink:
        """Store a new source link in the repository.
        Args:
            source_link (SourceLink): The source link to store.

        Returns:
            SourceLink: The stored source link with any updates applied (e.g., assigned ID).
        
        """

    def get_by_id(self, source_link_id: UUID) -> SourceLink | None:
        """Retrieve a source link by its ID.
        Args:
            source_link_id (UUID): The ID of the source link to retrieve.

        Returns:
            SourceLink | None: The source link with the specified ID, or None if not found.

        """

    def get_by_path(self, path: str) -> SourceLink | None:
        """Retrieve a source link by its path.
        Args:
            path (str): The path of the source link to retrieve.

        Returns:
            SourceLink | None: The source link with the specified path, or None if not found.

        """

    def list_by_owner(self, owner_user_id: str) -> Sequence[SourceLink]:
        """List all source links owned by a specific user.
        Args:
            owner_user_id (str): The ID of the owner user.

        Returns:
            Sequence[SourceLink]: A sequence of source links owned by the specified user.

        """

    def update(self, source_link: SourceLink) -> SourceLink:
        """Update an existing source link in the repository.
        Args:
            source_link (SourceLink): The source link to update.

        Returns:
            SourceLink: The updated source link.

        """