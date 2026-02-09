from __future__ import annotations

import re

# stage2 중량 보강 힌트 패턴
RE_HINT_GROSS = re.compile(r"총\s*중\s*량")
RE_HINT_TARE = re.compile(r"공차\s*중량|차\s*중량|차중량")
RE_HINT_NET = re.compile(r"실\s*중\s*량|실중량")

# stage2 "라벨만 있는 줄" 트리거 패턴
RE_ONLY_GROSS_LABEL = re.compile(r"^(?:총\s*중\s*량)\s*[:\-]?\s*$")
RE_ONLY_TARE_LABEL = re.compile(r"^(?:공차\s*중량|차\s*중량|차중량)\s*[:\-]?\s*$")
RE_ONLY_NET_LABEL = re.compile(r"^(?:실\s*중\s*량|실중량)\s*[:\-]?\s*$")
RE_ONLY_TICKET_LABEL = re.compile(r"^(?:ID\s*-\s*NO|ID\s*NO)\s*[:\-]?\s*$", re.IGNORECASE)
RE_ONLY_MEASURE_COUNT_LABEL = re.compile(r"^(?:계량횟수|계량\s*횟수)\s*[:\-]?\s*$")

# 거래처/좌표 복구용 패턴
RE_CUSTOMER_HONORIFIC = re.compile(r"^(?P<name>.+?)\s*귀하$")
RE_COORDINATE_LINE = re.compile(r"^\s*(-?\d{1,3}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)\s*$")

# issuer 주변 블록 보강 패턴
RE_TEL_LABEL = re.compile(r"(?:TEL|전화|전화번호|연락처)\s*[:)]?\s*(.+)$", re.IGNORECASE)
RE_FAX_LABEL = re.compile(r"(?:FAX|팩스|팩스번호)\s*[:)]?\s*(.+)$", re.IGNORECASE)
RE_ADDRESS_HINT = re.compile(r"(도|시|군|구|읍|면|동|로|길|번길)")

