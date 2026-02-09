"""
1단계 라벨 규칙과 후보 추출 로직입니다.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Callable

from parsing.common.normalize import normalize_line
from parsing.common.parsing_labels import (
    RE_LABEL_CUSTOMER,
    RE_LABEL_GROSS,
    RE_LABEL_ISSUER_ADDRESS,
    RE_LABEL_ISSUER_FAX,
    RE_LABEL_ISSUER_TEL,
    RE_LABEL_IO_TYPE,
    RE_LABEL_ITEM,
    RE_LABEL_MEASURE_COUNT,
    RE_LABEL_MEASURED_DATE,
    RE_LABEL_NET,
    RE_LABEL_TARE,
    RE_LABEL_TICKET_ID,
    RE_LABEL_VEHICLE,
)
from parsing.common.parsing_validators import (
    parse_customer_name,
    parse_gross,
    parse_issuer_address,
    parse_issuer_fax,
    parse_issuer_tel,
    parse_io_type,
    parse_item_name,
    parse_measure_count,
    parse_measured_date,
    parse_net,
    parse_tare,
    parse_ticket_id,
    parse_vehicle_no,
)

Validator = Callable[[str], dict[str, Any]]


@dataclass(frozen=True)
class ParseRule:
    """
    단일 라벨 규칙 정의 객체입니다.
    """

    rule_id: str
    label_pattern: re.Pattern[str]
    validator: Validator


RULES: tuple[ParseRule, ...] = (
    ParseRule("LABEL_MEASURED_DATE", RE_LABEL_MEASURED_DATE, parse_measured_date),
    ParseRule("LABEL_VEHICLE", RE_LABEL_VEHICLE, parse_vehicle_no),
    ParseRule("LABEL_CUSTOMER", RE_LABEL_CUSTOMER, parse_customer_name),
    ParseRule("LABEL_ITEM", RE_LABEL_ITEM, parse_item_name),
    ParseRule("LABEL_IO_TYPE", RE_LABEL_IO_TYPE, parse_io_type),
    ParseRule("LABEL_TICKET_ID", RE_LABEL_TICKET_ID, parse_ticket_id),
    ParseRule("LABEL_MEASURE_COUNT", RE_LABEL_MEASURE_COUNT, parse_measure_count),
    ParseRule("LABEL_ISSUER_ADDRESS", RE_LABEL_ISSUER_ADDRESS, parse_issuer_address),
    ParseRule("LABEL_ISSUER_TEL", RE_LABEL_ISSUER_TEL, parse_issuer_tel),
    ParseRule("LABEL_ISSUER_FAX", RE_LABEL_ISSUER_FAX, parse_issuer_fax),
    ParseRule("LABEL_GROSS", RE_LABEL_GROSS, parse_gross),
    ParseRule("LABEL_TARE", RE_LABEL_TARE, parse_tare),
    ParseRule("LABEL_NET", RE_LABEL_NET, parse_net),
)


def _candidate(
    field: str,
    value: Any,
    raw_line: str,
    normalized_line: str,
    line_idx: int | None,
    rule_id: str,
) -> dict[str, Any]:
    return {
        "field": field,
        "value": value,
        "raw_line": raw_line,
        "normalized_line": normalized_line,
        "line_idx": line_idx,
        "rule_id": rule_id,
    }


def _extract_with_rule(
    normalized_line: str,
    raw_line: str,
    line_idx: int | None,
    rule: ParseRule,
) -> list[dict[str, Any]]:
    """
    규칙 1개를 적용해서 후보를 추출합니다.
    """
    match = rule.label_pattern.match(normalized_line)
    if not match:
        return []

    value_text = match.group("value").strip()
    if not value_text:
        return []

    parsed = rule.validator(value_text)
    if not parsed:
        return []

    out: list[dict[str, Any]] = []
    for field, value in parsed.items():
        out.append(
            _candidate(
                field=field,
                value=value,
                raw_line=raw_line,
                normalized_line=normalized_line,
                line_idx=line_idx,
                rule_id=rule.rule_id,
            )
        )
    return out


def extract_same_line_label_values(line: str, line_idx: int | None = None) -> list[dict[str, Any]]:
    """
    단일 라인에서 라벨-값 후보를 추출합니다.
    """
    normalized_line = normalize_line(line)
    if not normalized_line:
        return []

    out: list[dict[str, Any]] = []
    for rule in RULES:
        out.extend(_extract_with_rule(normalized_line, line, line_idx, rule))
    return out


def extract_same_line_label_values_from_lines(lines: list[str]) -> list[dict[str, Any]]:
    """
    라인 목록에서 라벨-값 후보를 누적 추출합니다.
    """
    out: list[dict[str, Any]] = []
    for idx, line in enumerate(lines):
        out.extend(extract_same_line_label_values(line, idx))
    return out
