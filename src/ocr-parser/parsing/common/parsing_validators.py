"""
라벨에서 분리된 value 문자열을 검증/정규화하는 모듈입니다.

역할:
1) 값 형식이 계약과 맞는지 검사
2) 맞다면 내부 표준값으로 변환(정수 kg, YYYY-MM-DD, HH:MM 등)
3) 맞지 않으면 빈 딕셔너리 반환(= 파싱하지 않음)
"""

from __future__ import annotations

import re
from typing import Any

from parsing.common.normalize import parse_int_kg


# 날짜(YYYY-MM-DD, YYYY/MM/DD, YYYY.MM.DD)를 허용하고 추출합니다.
RE_DATE = re.compile(r"(\d{4}[./-]\d{2}[./-]\d{2})")

# 차량번호 후보(3~12자) 추출용입니다.
RE_VEHICLE = re.compile(r"([0-9A-Za-z가-힣]{3,12})")

# 중량+시간 파싱:
# - 앞 시간: "02:07 13,460 kg"
# - 뒤 시간: "14,230 kg (09:09)"
# - 시간 없이 중량만: "5,900 kg"
RE_WEIGHT_WITH_TIME = re.compile(
    r"(?:(?P<time_front>\d{1,2}:\d{2}(?::\d{2})?)\s+)?"
    r"(?P<kg>[\d, ]+)\s*kg"
    r"(?:\s*\((?P<time_back>\d{1,2}:\d{2}(?::\d{2})?)\))?",
    re.IGNORECASE,
)

# 티켓 ID(영문/숫자/하이픈)를 시작부에서 추출합니다.
RE_TICKET_ID = re.compile(r"([A-Za-z0-9-]{2,20})")
RE_PHONE = re.compile(r"(?:\(?0\d{1,2}\)?[-\s]?\d{3,4}[-\s]?\d{4})")


def _has_meaningful_text(text: str) -> bool:
    """
    문자열이 실질적인 텍스트를 포함하는지 검사합니다.
    콜론/기호만 있는 값은 무효로 간주합니다.
    """
    return re.search(r"[0-9A-Za-z가-힣]", text) is not None


def _normalize_date(date_text: str) -> str:
    """
    날짜 구분자를 '-'로 통일합니다.
    예: 2026/02/01 -> 2026-02-01
    """
    return date_text.replace("/", "-").replace(".", "-")


def parse_measured_date(value_text: str) -> dict[str, Any]:
    """
    계량일자/날짜 value를 검증합니다.
    형식이 맞으면 {'measured_date': 'YYYY-MM-DD'} 반환합니다.
    """
    match = RE_DATE.search(value_text)
    if not match:
        return {}
    return {"measured_date": _normalize_date(match.group(1))}


def parse_vehicle_no(value_text: str) -> dict[str, Any]:
    """
    차량번호 value를 검증합니다.
    가장 먼저 발견되는 차량번호 후보를 사용합니다.
    """
    match = RE_VEHICLE.search(value_text)
    if not match:
        return {}
    return {"vehicle_no": match.group(1)}


def parse_customer_name(value_text: str) -> dict[str, Any]:
    """
    거래처/상호 value를 검증합니다.
    비어 있지 않으면 통과합니다.
    """
    text = value_text.strip()
    if not text or not _has_meaningful_text(text):
        return {}
    return {"customer_name": text}


def parse_item_name(value_text: str) -> dict[str, Any]:
    """
    품명 value를 검증합니다.
    비어 있지 않으면 통과합니다.
    """
    text = value_text.strip()
    # 한 줄에 "품명 ... 구분 ..."이 함께 붙는 OCR 케이스를 분리합니다.
    text = re.split(r"\b구분\b", text, maxsplit=1)[0].strip()
    if not text or not _has_meaningful_text(text):
        return {}
    return {"item_name": text}


def parse_io_type(value_text: str) -> dict[str, Any]:
    """
    입출고 구분을 검증합니다.
    허용값은 '입고', '출고'만 인정합니다.
    """
    text = value_text.strip()
    if "입고" in text:
        return {"io_type": "입고"}
    if "출고" in text:
        return {"io_type": "출고"}
    return {}


def parse_ticket_id(value_text: str) -> dict[str, Any]:
    """
    ID-NO/계량횟수 같은 티켓 식별값을 검증합니다.
    """
    match = RE_TICKET_ID.search(value_text.strip())
    if not match:
        return {}
    return {"ticket_id": match.group(1)}


def parse_measure_count(value_text: str) -> dict[str, Any]:
    """
    계량횟수 value를 검증합니다.
    OCR에서 앞 0이 의미 있는 경우가 있어 문자열 그대로 보존합니다.
    """
    match = RE_TICKET_ID.search(value_text.strip())
    if not match:
        return {}
    return {"measure_count": match.group(1)}


def _normalize_phone(phone_text: str) -> str:
    """
    전화번호 표기를 CSV/JSON에서 다루기 쉽도록 단순 정규화합니다.
    - 공백/괄호 제거 후 숫자만 추출
    - 한국 전화번호 관례에 맞춰 하이픈 형태로 통일
      예) 0313599127 -> 031-359-9127
          01012345678 -> 010-1234-5678
    """
    digits = re.sub(r"\D", "", phone_text)
    if len(digits) < 9:
        return digits

    # 서울 지역번호(02): 02-XXX(또는 XXXX)-XXXX
    if digits.startswith("02"):
        if len(digits) == 9:
            return f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"
        if len(digits) == 10:
            return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
        return digits

    # 휴대폰(010/011/016/017/018/019): 3-3/4-4
    if digits.startswith(("010", "011", "016", "017", "018", "019")):
        if len(digits) == 10:
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        if len(digits) == 11:
            return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
        return digits

    # 일반 유선 번호(지역번호 3자리 가정): 3-3/4-4
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    if len(digits) == 11:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    return digits


def parse_issuer_address(value_text: str) -> dict[str, Any]:
    """
    발행처 주소를 검증합니다.
    라벨 기반 1차 파싱에서만 사용하며, 비어 있지 않은 텍스트를 그대로 보존합니다.
    """
    text = value_text.strip()
    if not text or not _has_meaningful_text(text):
        return {}
    return {"issuer_address": text}


def parse_issuer_tel(value_text: str) -> dict[str, Any]:
    """
    발행처 전화번호를 검증합니다.
    라벨 뒤 value에서 전화번호 패턴을 찾으면 issuer_tel로 반환합니다.
    """
    match = RE_PHONE.search(value_text)
    if not match:
        return {}
    return {"issuer_tel": _normalize_phone(match.group(0))}


def parse_issuer_fax(value_text: str) -> dict[str, Any]:
    """
    발행처 팩스번호를 검증합니다.
    라벨 뒤 value에서 전화번호 패턴을 찾으면 issuer_fax로 반환합니다.
    """
    match = RE_PHONE.search(value_text)
    if not match:
        return {}
    return {"issuer_fax": _normalize_phone(match.group(0))}


def _extract_weight_and_time(value_text: str) -> tuple[int | None, str | None]:
    """
    중량(kg)과 시간(HH:MM[:SS])을 같이 추출합니다.

    반환 규칙:
    - 중량 파싱 실패: (None, None)
    - 중량만 성공: (kg, None)
    - 중량+시간 성공: (kg, time)
    """
    match = RE_WEIGHT_WITH_TIME.search(value_text)
    if not match:
        return None, None

    kg_value = parse_int_kg(match.group("kg"))
    if kg_value is None:
        return None, None

    time_value = match.group("time_front") or match.group("time_back")
    return kg_value, time_value


def parse_gross(value_text: str) -> dict[str, Any]:
    """
    총중량 value를 검증합니다.
    - gross_kg는 필수
    - gross_time은 있으면 추가
    """
    kg_value, time_value = _extract_weight_and_time(value_text)
    if kg_value is None:
        return {}

    out: dict[str, Any] = {"gross_kg": kg_value}
    if time_value:
        out["gross_time"] = time_value
    return out


def parse_tare(value_text: str) -> dict[str, Any]:
    """
    공차중량/차중량 value를 검증합니다.
    - tare_kg는 필수
    - tare_time은 있으면 추가
    """
    kg_value, time_value = _extract_weight_and_time(value_text)
    if kg_value is None:
        return {}

    out: dict[str, Any] = {"tare_kg": kg_value}
    if time_value:
        out["tare_time"] = time_value
    return out


def parse_net(value_text: str) -> dict[str, Any]:
    """
    실중량 value를 검증합니다.
    - net_kg는 필수
    - net_time은 있으면 추가
    """
    kg_value, time_value = _extract_weight_and_time(value_text)
    if kg_value is None:
        return {}

    out: dict[str, Any] = {"net_kg": kg_value}
    if time_value:
        out["net_time"] = time_value
    return out
