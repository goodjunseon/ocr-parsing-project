"""
ocr-parser.normalize의 Docstring
파일 경로: src/ocr-parser/normalize.py
OCR 노이즈 정리(라벨 붙이기, 숫자/시간 정규화)
"""

from __future__ import annotations

import re


def _normalize_korean_time(text: str) -> str:
    """
    "11시 33분", "11시 33분 10초" 같은 한글 시간 표기를
    "11:33", "11:33:10" 형태로 표준화합니다.
    """

    def _replace(match: re.Match[str]) -> str:
        hour = int(match.group(1))
        minute = int(match.group(2))
        second = match.group(3)
        if second is None:
            return f"{hour:02d}:{minute:02d}"
        return f"{hour:02d}:{minute:02d}:{int(second):02d}"

    return re.sub(
        r"(\d{1,2})\s*시\s*(\d{1,2})\s*분(?:\s*(\d{1,2})\s*초)?",
        _replace,
        text,
    )


def normalize_line(s: str) -> str:
    """
    OCR 텍스트 라인 노이즈 정리
    앞뒤 공백 제거, 여러 공백을 하나로,
    자주 깨지는 라벨 붙이기, 숫자/시간 정규화 등
    """
    s = s.strip() # 앞뒤 공백 제거
    s = re.sub(r"\s+", " ", s) # 여러 공백을 하나의 공백으로
    
    # 자주 깨지는 라벨 붙이기(샘플 보면서 계속 보강해야한다)
    s = s.replace("거 래 처", "거래처")
    s = s.replace("계 량 일자", "계량일자")
    s = s.replace("계 량", "계량")
    s = s.replace("실 중 량", "실중량")
    s = s.replace("총 중 량", "총중량")
    s = s.replace("공차 중량", "공차중량")
    s = s.replace("차 중량", "차중량")
    s = s.replace("날 짜", "날짜")
    s = s.replace("상 호", "상호")
    s = s.replace("구 분", "구분")
    s = s.replace("품 명", "품명")
    s = s.replace("제 품 명", "제품명")
    s = s.replace("일 시", "일시")

    # 시간 "02 : 13" -> "02:13"
    s = re.sub(r"(\d{1,2})\s*:\s*(\d{2})", r"\1:\2", s)
    # 시간 "11시 33분" -> "11:33", "11시 33분 10초" -> "11:33:10"
    s = _normalize_korean_time(s)

    # 숫자 내부 공백은 이 단계에서 강제로 제거하지 않습니다.
    # (시간+중량이 붙어버리는 부작용이 있어, 파서 단계에서 안전하게 처리)

    return s

def parse_int_kg(s: str) -> int | None:
    """
    "1,234 kg" 같은 문자열에서 숫자 부분만 추출하여 int로 반환.
    숫자가 아니면 None 반환.
    """
    s = s.replace(",", "").replace(" ", "")
    
    # 숫자가 아니면 None 반환
    if not s.isdigit():
        return None
    
    return int(s)
