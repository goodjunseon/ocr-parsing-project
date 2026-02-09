"""
파싱 라벨 계약(Contract)을 정의하는 모듈입니다.

역할:
1) 어떤 라벨을 허용할지(회사에서 필요한 필드)
2) 라벨 문법을 어떻게 허용할지(콜론/공백 구분 허용)
3) 파서가 재사용할 수 있는 컴파일된 정규식 제공
"""

from __future__ import annotations

import re


def _compile_labeled_value_pattern(label_alias_regex: str) -> re.Pattern[str]:
    """
    라벨 + 값 구조를 강제하는 패턴을 만듭니다.

    허용 형태:
    - 라벨: 값
    - 라벨 - 값
    - 라벨 값

    핵심 제약:
    - 반드시 라벨이 줄의 시작에 있어야 함
    - 라벨 뒤에는 구분자(:,-) 또는 공백이 있어야 함
    - 값은 최소 1글자 이상이어야 함
    """

    return re.compile(
        rf"^(?:{label_alias_regex})(?:\s*[:\-]\s*|\s+)(?P<value>.+)$",
        re.IGNORECASE,
    )


# 계량일자/날짜 관련 라벨
RE_LABEL_MEASURED_DATE = _compile_labeled_value_pattern(
    r"계량일자|계량\s*일자|날짜|일시|일\s*시"
)

# 차량번호 라벨
RE_LABEL_VEHICLE = _compile_labeled_value_pattern(
    r"차량번호|차량\s*번호|차번호|차량\s*No\.?"
)

# 거래처 라벨
RE_LABEL_CUSTOMER = _compile_labeled_value_pattern(r"거래처|상호")

# 품명 라벨
RE_LABEL_ITEM = _compile_labeled_value_pattern(r"품명|품\s*명|제품명|제\s*품\s*명")

# 입고/출고 구분 라벨
RE_LABEL_IO_TYPE = _compile_labeled_value_pattern(r"구분")

# 티켓/전표 식별 라벨
RE_LABEL_TICKET_ID = _compile_labeled_value_pattern(r"ID\s*-\s*NO|ID\s*NO")

# 계량 횟수 라벨
RE_LABEL_MEASURE_COUNT = _compile_labeled_value_pattern(r"계량횟수|계량\s*횟수")

# 발행처 주소 라벨
RE_LABEL_ISSUER_ADDRESS = _compile_labeled_value_pattern(
    r"주소|소재지|사업장\s*주소|발행처\s*주소"
)

# 발행처 전화 라벨
RE_LABEL_ISSUER_TEL = _compile_labeled_value_pattern(r"TEL|전화|전화번호|연락처")

# 발행처 팩스 라벨
RE_LABEL_ISSUER_FAX = _compile_labeled_value_pattern(r"FAX|팩스|팩스번호")

# 총중량 라벨
RE_LABEL_GROSS = _compile_labeled_value_pattern(r"총중량|총\s*중량|총\s*중\s*량")

# 공차중량(또는 차중량) 라벨
RE_LABEL_TARE = _compile_labeled_value_pattern(
    r"공차중량|공차\s*중량|차중량|차\s*중량"
)

# 실중량 라벨
RE_LABEL_NET = _compile_labeled_value_pattern(r"실중량|실\s*중량|실\s*중\s*량")


# 최종 출력 스키마(출력 순서 포함)
# 파싱 실패/미검출 필드는 빈값으로 출력합니다.
PARSE_SCHEMA_FIELDS: tuple[str, ...] = (
    "measured_date",
    "vehicle_no",
    "issuer_name",
    "customer_name",
    "item_name",
    "io_type",
    "ticket_id",
    "measure_count",
    "issuer_address",
    "issuer_tel",
    "issuer_fax",
    "gross_kg",
    "gross_time",
    "tare_kg",
    "tare_time",
    "net_kg",
    "net_time",
    "gps_lat",
    "gps_lon",
    "warnings",
)
