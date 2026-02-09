from __future__ import annotations

from typing import Any


def is_empty(value: Any) -> bool:
    """
    스키마 필드 값이 비어 있는지 검사합니다.
    빈 문자열이나 None인 경우에만 비어있다고 간주합니다.
    """
    return value == "" or value is None


def append_warning(schema: dict[str, Any], warning: str) -> None:
    """
    warnings 필드(list)에 경고 키를 중복 없이 추가합니다.
    """
    warnings = schema.get("warnings")
    # warnings 필드가 없거나 리스트가 아니면 새 리스트로 초기화
    if not isinstance(warnings, list):
        warnings = []
    # 중복 없이 경고 추가
    if warning not in warnings:
        warnings.append(warning)
    schema["warnings"] = warnings


def set_if_empty(schema: dict[str, Any], field: str, value: Any) -> None:
    """
    스키마 필드가 비어 있을 때만 값을 채웁니다.
    """
    if field not in schema:
        return
    if not is_empty(schema[field]):
        return
    schema[field] = value

