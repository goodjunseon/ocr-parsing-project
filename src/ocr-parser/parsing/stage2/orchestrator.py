"""
2단계(Recovery) 파싱 오케스트레이션입니다.
"""

from __future__ import annotations

from typing import Any

from parsing.common.normalize import normalize_line
from parsing.common.parsing_company import resolve_companies
from parsing.stage2.recovery_geo import recover_gps
from parsing.stage2.recovery_identity import (
    recover_customer_name,
    recover_io_type,
    recover_measure_count_from_next_line,
    recover_ticket_id_from_next_line,
)
from parsing.stage2.recovery_issuer import recover_issuer_contact_fields
from parsing.stage2.recovery_weight import (
    recover_weight_with_inline_hints,
    recover_weight_with_next_line_value,
    recover_weight_with_unlabeled_pair,
)


def recover_missing_schema_fields(stage1_schema: dict[str, Any], lines: list[str]) -> dict[str, Any]:
    """
    2단계 복구 파이프라인 진입점입니다.
    """
    recovered = dict(stage1_schema)
    normalized_lines: list[str] = []
    for line in lines:
        normalized = normalize_line(line)
        if normalized:
            normalized_lines.append(normalized)

    recover_weight_with_inline_hints(recovered, normalized_lines)
    recover_weight_with_next_line_value(recovered, normalized_lines)
    recover_weight_with_unlabeled_pair(recovered, normalized_lines)
    recover_io_type(recovered, normalized_lines)
    recover_ticket_id_from_next_line(recovered, normalized_lines)
    recover_measure_count_from_next_line(recovered, normalized_lines)
    recover_customer_name(recovered, normalized_lines)
    recover_gps(recovered, normalized_lines)
    recovered = resolve_companies(recovered, lines, normalized_lines)
    recover_issuer_contact_fields(recovered, normalized_lines)

    return recovered
