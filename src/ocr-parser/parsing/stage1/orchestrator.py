"""
1단계(Strict) 파싱 오케스트레이션입니다.
"""

from __future__ import annotations

from typing import Any

from parsing.common.parsing_labels import PARSE_SCHEMA_FIELDS
from parsing.stage1.rules import extract_same_line_label_values_from_lines
from parsing.stage2.orchestrator import recover_missing_schema_fields


def _has_schema_value(value: Any) -> bool:
    """
    스키마 필드 값이 유효한지 검사합니다.
    리스트인 경우 비어있지 않은지, 문자열이나 기타 값인 경우 빈 문자열이나 None이 아닌지 확인합니다.
    """
    if isinstance(value, list):
        return len(value) > 0
    return value not in ("", None)


def _build_stage1_schema(lines: list[str]) -> dict[str, Any]:
    """
    라인 목록을 파싱해서 1단계 스키마를 만듭니다.
    1단계 스키마는 PARSE_SCHEMA_FIELDS에 정의된 필드들을 포함하며,
    각 필드에 대해 동일 라인에서 라벨과 값을 추출한 결과를 사용합니다.
    이미 값이 있는 필드는 덮어쓰지 않습니다.
    1단계 스키마를 반환합니다.
    """
    stage1_schema: dict[str, Any] = {}
    for field in PARSE_SCHEMA_FIELDS:
        stage1_schema[field] = [] if field == "warnings" else ""

    stage1_candidates = extract_same_line_label_values_from_lines(lines)
    for item in stage1_candidates:
        field = item["field"]
        if field not in stage1_schema:
            # 알 수 없는 필드 무시
            continue
        if _has_schema_value(stage1_schema[field]):
            # 이미 값이 있으면 덮어쓰지 않음
            continue
        stage1_schema[field] = item["value"]

    return stage1_schema


def parse_lines_to_stage_schemas(lines: list[str]) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    라인 목록을 받아서 1단계 및 2단계 스키마를 파싱합니다.
    1단계 스키마는 _build_stage1_schema를 사용하여 생성되고,
    2단계 스키마는 recover_missing_schema_fields를 사용하여 1단계 스키마에서 누락된 필드를 복구합니다.
    1단계 및 2단계 스키마를 튜플로 반환합니다.
    """
    stage1_schema = _build_stage1_schema(lines) # 1단계 스키마 생성
    stage2_schema = recover_missing_schema_fields(stage1_schema, lines) # 2단계 스키마 복구
    return stage1_schema, stage2_schema
