from __future__ import annotations

from pathlib import Path

from parsing.common.parsing_labels import PARSE_SCHEMA_FIELDS


def _format_schema_value(value: object) -> str:
    """
    스키마 값을 CLI 출력 문자열로 변환합니다.
    """
    if value == "" or value is None:
        return ""
    return str(value)


def print_schema_block(title: str, schema: dict[str, object]) -> None:
    """
    1개 스키마를 필드 순서대로 출력합니다.
    """
    print(title)
    for field in PARSE_SCHEMA_FIELDS:
        value = _format_schema_value(schema.get(field, ""))
        print(f"{field}: {value}")


def print_stage2_block(stage1_schema: dict[str, object], stage2_schema: dict[str, object]) -> None:
    """
    2단계 결과를 출력합니다.
    1단계에서 비어 있었는데 2단계에서 채워진 값은 '[2단계 보강]' 태그를 표시합니다.
    """
    print("[파싱-2단계]")
    for field in PARSE_SCHEMA_FIELDS:
        stage1_value = _format_schema_value(stage1_schema.get(field, ""))
        stage2_value = _format_schema_value(stage2_schema.get(field, ""))
        tag = " [2단계 보강]" if stage1_value == "" and stage2_value != "" else ""
        print(f"{field}: {stage2_value}{tag}")


def print_file_report(
    file_path: Path,
    lines: list[str],
    stage1_schema: dict[str, object],
    stage2_schema: dict[str, object],
    json_path: Path,
    csv_path: Path,
) -> None:
    """
    파일 1건에 대한 콘솔 출력 묶음을 담당합니다.
    """
    print()
    print(f"== {file_path} ==")
    print("[📌 원본]")
    for line in lines:
        print(line)

    print_schema_block("[파싱-1단계]", stage1_schema)
    print_stage2_block(stage1_schema, stage2_schema)
    print("[결과파일]")
    print(f"json: {json_path}")
    print(f"csv: {csv_path}")
