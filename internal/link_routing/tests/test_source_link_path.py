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

import pytest

from prd_04_link_routing.errors import DomainValidationError
from prd_04_link_routing.policies.source_link_path import (
    normalize_source_link_path,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("launch", "launch"),
        ("team_alpha", "team_alpha"),
        ("event-01", "event-01"),
        ("events/launch", "events/launch"),
        ("campaigns/2026/keynote", "campaigns/2026/keynote"),
        (" Promo/Summer ", "promo/summer"),
    ],
)
def test_normalize_source_link_path_accepts_and_normalizes_valid_paths(
    value: str,
    expected: str,
) -> None:
    assert normalize_source_link_path(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "",
        "   ",
        "/launch",
        "launch/",
        "launch//daily",
        "launch?ref=email",
        "launch#overview",
        "launch space",
        "launch.example",
        "launch%2Fdaily",
        "launch:daily",
        "launch/daily!",
        "launch/daily@team",
        "caf\u00e9",
    ],
)
def test_normalize_source_link_path_rejects_invalid_characters_or_structure(
    value: str,
) -> None:
    with pytest.raises(DomainValidationError):
        normalize_source_link_path(value)


@pytest.mark.parametrize(
    "value",
    [
        None,
        123,
        ["launch"],
    ],
)
def test_normalize_source_link_path_requires_a_string(value: object) -> None:
    with pytest.raises(DomainValidationError, match="must be a string"):
        normalize_source_link_path(value)  # type: ignore[arg-type]


def test_normalize_source_link_path_accepts_a_path_at_the_maximum_length() -> None:
    value = "a" * 255

    assert normalize_source_link_path(value) == value


def test_normalize_source_link_path_rejects_a_path_longer_than_the_maximum_length() -> None:
    with pytest.raises(DomainValidationError, match="must not exceed 255 characters"):
        normalize_source_link_path("a" * 256)

