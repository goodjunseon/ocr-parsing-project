from __future__ import annotations

from typing import Any

from parsing.common.patterns import (
    RE_HINT_GROSS,
    RE_HINT_NET,
    RE_HINT_TARE,
    RE_ONLY_GROSS_LABEL,
    RE_ONLY_NET_LABEL,
    RE_ONLY_TARE_LABEL,
)
from parsing.common.parsing_validators import parse_gross, parse_net, parse_tare
from parsing.stage2.recovery_common import is_empty, set_if_empty


def _apply_weight_parse_result(
    schema: dict[str, Any],
    parsed: dict[str, Any],
    kg_field: str,
    time_field: str,
) -> None:
    kg_value = parsed.get(kg_field)
    if kg_value is None:
        return

    set_if_empty(schema, kg_field, kg_value)
    if time_field in parsed:
        set_if_empty(schema, time_field, parsed[time_field])


def recover_weight_with_inline_hints(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    for line in normalized_lines:
        if is_empty(schema["gross_kg"]) and RE_HINT_GROSS.search(line):
            _apply_weight_parse_result(schema, parse_gross(line), "gross_kg", "gross_time")

        if is_empty(schema["tare_kg"]) and RE_HINT_TARE.search(line):
            _apply_weight_parse_result(schema, parse_tare(line), "tare_kg", "tare_time")

        if is_empty(schema["net_kg"]) and RE_HINT_NET.search(line):
            _apply_weight_parse_result(schema, parse_net(line), "net_kg", "net_time")


def recover_weight_with_next_line_value(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    for idx in range(len(normalized_lines) - 1):
        label_line = normalized_lines[idx]
        value_line = normalized_lines[idx + 1]

        if is_empty(schema["gross_kg"]) and RE_ONLY_GROSS_LABEL.match(label_line):
            _apply_weight_parse_result(schema, parse_gross(value_line), "gross_kg", "gross_time")

        if is_empty(schema["tare_kg"]) and RE_ONLY_TARE_LABEL.match(label_line):
            _apply_weight_parse_result(schema, parse_tare(value_line), "tare_kg", "tare_time")

        if is_empty(schema["net_kg"]) and RE_ONLY_NET_LABEL.match(label_line):
            _apply_weight_parse_result(schema, parse_net(value_line), "net_kg", "net_time")


def recover_weight_with_unlabeled_pair(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    """
    (보수적) 라벨 없는 중량+시간 라인 2개가 명확할 때만 gross/tare를 복구합니다.
    """
    if not is_empty(schema["gross_kg"]) or not is_empty(schema["tare_kg"]):
        return

    candidates: list[tuple[int, str]] = []
    for line in normalized_lines:
        if RE_HINT_GROSS.search(line) or RE_HINT_TARE.search(line) or RE_HINT_NET.search(line):
            continue

        parsed = parse_gross(line)
        kg_value = parsed.get("gross_kg")
        time_value = parsed.get("gross_time")
        if kg_value is None or time_value is None:
            continue
        candidates.append((kg_value, time_value))

    if len(candidates) != 2:
        return

    candidates.sort(key=lambda item: item[0], reverse=True)
    gross_kg, gross_time = candidates[0]
    tare_kg, tare_time = candidates[1]

    set_if_empty(schema, "gross_kg", gross_kg)
    set_if_empty(schema, "gross_time", gross_time)
    set_if_empty(schema, "tare_kg", tare_kg)
    set_if_empty(schema, "tare_time", tare_time)
