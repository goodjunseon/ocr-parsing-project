# 파일 경로: src/ocr-parser/load_json.py
"""
JSON 파일을 읽고 pages[0].lines[].text에서 텍스트 라인들을 추출하는 유틸리티 함수들.
"""
from __future__ import annotations # 미래 버전 호환성 확보

import json
from pathlib import Path # 파일 경로 조작을 위한 Path 클래스
from typing import Any # Any 타입 힌팅을 위해

def load_json(path: str | Path) -> dict[str, Any]:
    """
    주어진 경로에서 JSON 파일을 읽고 파싱하여 딕셔너리로 반환합니다.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def extract_lines(ocr: dict[str, Any]) -> list[str]:
    """
    ocr JSON에서 pages[0].lines[].text를 꺼내서 문자열 리스트로 반환합니다.
    없으면 빈 리스트를 반환합니다.
    """
    pages = ocr.get("pages", [])
    if not pages:
        return []
    
    first_page = pages[0]
    lines = first_page.get("lines", [])
    out: list[str] = []

    for line in lines:
        text = line.get("text")
        if isinstance(text, str) and text.strip():
            out.append(text.strip())
    return out

