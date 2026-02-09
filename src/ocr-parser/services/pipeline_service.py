from __future__ import annotations

from pathlib import Path

from input.load_json import extract_lines, load_json
from out.result_writer import build_output_paths, write_parsed_csv, write_parsed_json
from parsing.stage1.orchestrator import parse_lines_to_stage_schemas


def run_pipeline_for_file(
    file_path: Path,
    result_dir: Path,
) -> tuple[list[str], dict[str, object], dict[str, object], Path, Path]:
    """
    입력 파일 1건에 대해 전체 파이프라인을 실행합니다.

    처리 단계:
    1) JSON 로드
    2) OCR 라인 추출
    3) 1단계/2단계 파싱
    4) JSON/CSV 결과 파일 저장
    """
    ocr = load_json(file_path)
    lines = extract_lines(ocr)
    stage1_schema, stage2_schema = parse_lines_to_stage_schemas(lines)

    json_path, csv_path = build_output_paths(result_dir, file_path)
    write_parsed_json(json_path, file_path, stage1_schema, stage2_schema)
    write_parsed_csv(csv_path, stage1_schema, stage2_schema)

    return lines, stage1_schema, stage2_schema, json_path, csv_path
