from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)


def collect_json_files(paths: Iterable[str], recursive: bool) -> list[Path]:
    """
    주어진 경로들에서 JSON 파일들을 수집하여 Path 리스트로 반환합니다.
    디렉터리가 주어지면 해당 디렉터리 내(재귀적으로)의 JSON 파일들을 포함합니다.
    중복된 파일 경로는 제거됩니다.
    """
    path_list = list(paths)
    logger.debug("collect_json_files 호출: paths=%s recursive=%s", path_list, recursive)

    files: list[Path] = []
    glob_pattern = "**/*.json" if recursive else "*.json"

    for raw in path_list:
        path_obj = Path(raw)
        logger.debug("경로 검사 중: %s", path_obj)
        if path_obj.is_file() and path_obj.suffix.lower() == ".json":
            logger.debug("일치하는 JSON 파일: %s", path_obj)
            files.append(path_obj)
        elif path_obj.is_dir():
            matched = sorted(path_obj.glob(glob_pattern))
            logger.debug("디렉터리에서 %d개의 JSON 파일을 찾음: %s", len(matched), path_obj)
            files.extend(matched)
        else:
            logger.warning("경로 무시됨 (JSON 파일 또는 디렉터리가 아님): %s", path_obj)

    deduped: list[Path] = []
    seen: set[Path] = set()
    for file_path in files:
        key = file_path.resolve()
        if key in seen:
            logger.debug("중복 건너뜀: %s", file_path)
            continue
        seen.add(key)
        deduped.append(file_path)

    logger.info("총 %d개의 JSON 파일 수집됨.", len(deduped))
    return deduped

