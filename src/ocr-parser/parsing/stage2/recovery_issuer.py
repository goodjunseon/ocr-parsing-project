from __future__ import annotations

from typing import Any

from parsing.common.patterns import RE_ADDRESS_HINT, RE_FAX_LABEL, RE_TEL_LABEL
from parsing.common.parsing_validators import parse_issuer_fax, parse_issuer_tel
from parsing.stage2.recovery_common import is_empty, set_if_empty

# 회사명 아래로 주소/TEL/FAX가 붙는 빈도가 높아 아래 5줄만 탐색합니다.
ISSUER_CONTEXT_WINDOW = 5


def recover_issuer_contact_fields(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    """
    발행처(issuer) 주변 블록에서 주소/TEL/FAX를 보수적으로 복구합니다.
    """
    issuer_name = str(schema.get("issuer_name", "")).strip()
    if not issuer_name:
        return

    if (
        not is_empty(schema.get("issuer_address"))
        and not is_empty(schema.get("issuer_tel"))
        and not is_empty(schema.get("issuer_fax"))
    ):
        return

    issuer_idx = -1
    for idx, line in enumerate(normalized_lines):
        if line.strip() == issuer_name:
            issuer_idx = idx
            break
    if issuer_idx < 0:
        return

    start = issuer_idx + 1
    end = min(len(normalized_lines), issuer_idx + 1 + ISSUER_CONTEXT_WINDOW)
    for line in normalized_lines[start:end]:
        tel_match = RE_TEL_LABEL.search(line)
        if tel_match and is_empty(schema.get("issuer_tel")):
            parsed_tel = parse_issuer_tel(tel_match.group(1))
            if parsed_tel:
                set_if_empty(schema, "issuer_tel", parsed_tel["issuer_tel"])

        fax_match = RE_FAX_LABEL.search(line)
        if fax_match and is_empty(schema.get("issuer_fax")):
            parsed_fax = parse_issuer_fax(fax_match.group(1))
            if parsed_fax:
                set_if_empty(schema, "issuer_fax", parsed_fax["issuer_fax"])

        if is_empty(schema.get("issuer_address")) and RE_ADDRESS_HINT.search(line):
            set_if_empty(schema, "issuer_address", line)
