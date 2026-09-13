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

import re

from prd_04_link_routing.errors import DomainValidationError


_SOURCE_LINK_PATH_PATTERN = re.compile(
    r"^(?!.*//)[a-z0-9](?:[a-z0-9_/-]*[a-z0-9_-])?$"
)
_MAX_SOURCE_LINK_PATH_LENGTH = 255

def normalize_source_link_path(path: str) -> str:
    if not isinstance(path, str):
        raise DomainValidationError("Source link path must be a string.")

    path = path.strip().lower()

    if not path:
        raise DomainValidationError("Source link path cannot be empty.")

    if len(path) > _MAX_SOURCE_LINK_PATH_LENGTH:
        raise DomainValidationError(
            f"Source link path must not exceed {_MAX_SOURCE_LINK_PATH_LENGTH} characters."
        )

    if not _SOURCE_LINK_PATH_PATTERN.fullmatch(path):
        raise DomainValidationError(  
            "Source link path may contain lowercase letters, digits, hyphens, "
            "underscores, and single forward slashes only. It cannot start or "
            "end with a slash."
        )

    return path