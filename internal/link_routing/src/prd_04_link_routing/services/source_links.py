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
from datetime import datetime, UTC
from urllib.parse import urlparse
from uuid import UUID, uuid4

from prd_04_link_routing.errors import DomainValidationError
from prd_04_link_routing.models import SourceLink, SourceLinkStatus
from prd_04_link_routing.policies.source_link_path import normalize_source_link_path
from prd_04_link_routing.repositories.source_link_repository import SourceLinkRepository

def require_http_url(value: str, field_name: str) -> str:
    parsed = urlparse(value)

    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise DomainValidationError(
            f"{field_name} must be a valid HTTP or HTTPS URL"
        )

    return value

class SourceLinkService:
    def __init__(self, repository: SourceLinkRepository) -> None:
        self._repository = repository

    def create(
        self,
        *,
        path: str,
        default_target_url: str,
        owner_user_id: str,
    ) -> SourceLink:
        normalized_path = normalize_source_link_path(path)
        validated_target_url = require_http_url(
            default_target_url,
            "default_target_url"
        )
        
        now = datetime.now(UTC)
        source_link = SourceLink(
            id=uuid4(),
            path=normalized_path,
            default_target_url=validated_target_url,
            owner_user_id=owner_user_id,
            status=SourceLinkStatus.ENABLED,
            created_at=now,
            updated_at=now        
        )

        return self._repository.create(source_link)

    def list_for_owner(self, owner_user_id: str) -> list[SourceLink]:
        return list(self._repository.list_by_owner(owner_user_id))

    def get_for_owner(
        self,
        source_link_id: UUID,
        owner_user_id: str,
    ) -> SourceLink | None:
        source_link = self._repository.get_by_id(source_link_id)

        if source_link is None or source_link.owner_user_id != owner_user_id:
            return None
        
        return source_link

    def update_for_owner(
        self,
        source_link_id: UUID,
        owner_user_id: str,
        *,
        default_target_url: str | None = None,
        status: SourceLinkStatus | None = None,
    ) -> SourceLink | None:
        source_link = self.get_for_owner(
            source_link_id, 
            owner_user_id
        )

        if source_link is None:
            return None

        updated_target_url = source_link.default_target_url
        if default_target_url is not None:
            updated_target_url = require_http_url(
                default_target_url,
                "default_target_url"
            )

        updated_source_link = replace(
            source_link,
            default_target_url=updated_target_url,
            status=status or source_link.status,
            updated_at=datetime.now(UTC),
        )

        return self._repository.update(updated_source_link)
    
