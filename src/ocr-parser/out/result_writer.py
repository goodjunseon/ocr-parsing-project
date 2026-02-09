"""
파싱 결과를 파일(JSON/CSV)로 내보내는 모듈입니다.

역할:
1) 결과 저장 폴더(result) 생성
2) 파일별 출력 경로 계산
3) JSON/CSV 포맷으로 결과 저장
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from parsing.common.parsing_labels import PARSE_SCHEMA_FIELDS


def ensure_result_dir(base_dir: Path) -> Path:
    """
    결과 저장 폴더를 보장합니다.

    생성 위치:
    - 프로젝트 루트/result
    - 예: /.../ocr-parsing-project/result
    """
    project_root = base_dir.parent.parent
    result_dir = project_root / "result"
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir


def _safe_stem(source_file: Path) -> str:
    """
    출력 파일명으로 사용 가능한 안전한 stem을 생성합니다.
    """
    return source_file.stem.replace(" ", "_")


def build_output_paths(result_dir: Path, source_file: Path) -> tuple[Path, Path]:
    """
    입력 파일 기준 JSON/CSV 출력 경로를 계산합니다.
    """
    stem = _safe_stem(source_file)
    json_path = result_dir / f"{stem}_parsed.json"
    csv_path = result_dir / f"{stem}_parsed.csv"
    return json_path, csv_path


def write_parsed_json(
    json_path: Path,
    source_file: Path,
    stage1_schema: dict[str, Any],
    stage2_schema: dict[str, Any],
) -> None:
    """
    파싱 결과를 JSON 파일로 저장합니다.

    구조:
    - source_file: 원본 파일 경로
    - stage1: 1단계 파싱 결과
    - stage2: 2단계 파싱 결과(보강 포함)
    """
    payload = {
        "source_file": str(source_file),
        "stage1": {field: stage1_schema.get(field, "") for field in PARSE_SCHEMA_FIELDS},
        "stage2": {field: stage2_schema.get(field, "") for field in PARSE_SCHEMA_FIELDS},
    }
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_parsed_csv(
    csv_path: Path,
    stage1_schema: dict[str, Any],
    stage2_schema: dict[str, Any],
) -> None:
    """
    파싱 결과를 CSV 파일로 저장합니다.

    행 단위 의미:
    - field: 라벨명
    - stage1_value: 1단계 값
    - stage2_value: 2단계 최종 값
    """
    with csv_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["field", "stage1_value", "stage2_value"])

        for field in PARSE_SCHEMA_FIELDS:
            stage1_value = stage1_schema.get(field, "")
            stage2_value = stage2_schema.get(field, "")
            writer.writerow([field, stage1_value, stage2_value])
