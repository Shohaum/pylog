from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

def freeze_mapping(mapping: Mapping[str, Any] | None) -> Mapping[str, Any]:
    """
    Return an imuutable snapshot of a mapping.

    If 'mapping ' is None, an empty immutable mapping is returned
    """

    if mapping is None:
        return MappingProxyType({})

    return MappingProxyType(dict(mapping))