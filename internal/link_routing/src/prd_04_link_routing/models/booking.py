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
from uuid import UUID
from datetime import datetime
from enum import StrEnum

class BookingStatus(StrEnum):
    SCHEDULED = "scheduled"
    CANCELED = "canceled"

@dataclass(frozen=True, slots=True)
class Booking:
    id: UUID
    source_link_id: UUID
    target_url: str
    starts_at: datetime
    ends_at: datetime
    status: BookingStatus
    created_by_user_id: str
    created_at: datetime
    updated_at: datetime
