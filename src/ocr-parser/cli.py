from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
for module_dir in (BASE_DIR / "input", BASE_DIR / "parsing"):
    module_dir_str = str(module_dir)
    if module_dir_str not in sys.path:
        sys.path.insert(0, module_dir_str)

from collect.file_collector import collect_json_files
from out.result_writer import ensure_result_dir
from presentation.console_printer import print_file_report
from services.pipeline_service import run_pipeline_for_file


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="OCR JSON 파일에서 pages[0].lines[].text 라인을 추출합니다."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["data"], # 기본값으로 data 디렉터리를 사용
        help="JSON 파일 또는 JSON 파일이 들어있는 디렉터리 경로",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="디렉터리를 재귀적으로 탐색합니다.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="파일 수집 로그를 출력합니다.",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        # 로그 레벨 설정: -v 옵션이 있으면 DEBUG, 없으면 WARNING
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="[%(levelname)s] %(message)s",
    )

    files = collect_json_files(args.paths, args.recursive)
    if not files:
        print("JSON 파일을 찾지 못했습니다.", file=sys.stderr)
        return 1

    result_dir = ensure_result_dir(BASE_DIR)

    for file_path in files:
        try:
            lines, stage1_schema, stage2_schema, json_path, csv_path = run_pipeline_for_file(
                file_path,
                result_dir,
            )
        except Exception:
            logging.error("파일 처리 실패: %s", file_path)
            logging.debug("예외 정보:", exc_info=True)
            continue

        # 결과 출력
        print_file_report(
            file_path=file_path,
            lines=lines,
            stage1_schema=stage1_schema,
            stage2_schema=stage2_schema,
            json_path=json_path,
            csv_path=csv_path,
        )

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
