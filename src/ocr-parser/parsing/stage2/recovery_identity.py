from __future__ import annotations

from typing import Any

from parsing.common.patterns import (
    RE_CUSTOMER_HONORIFIC,
    RE_ONLY_MEASURE_COUNT_LABEL,
    RE_ONLY_TICKET_LABEL,
)
from parsing.common.parsing_validators import (
    parse_customer_name,
    parse_io_type,
    parse_measure_count,
    parse_ticket_id,
)
from parsing.stage2.recovery_common import is_empty, set_if_empty


def recover_io_type(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    if not is_empty(schema["io_type"]):
        return

    for line in normalized_lines:
        compact = line.replace(" ", "")
        if "입고" in compact and "출고" not in compact:
            set_if_empty(schema, "io_type", "입고")
            return
        if "출고" in compact and "입고" not in compact:
            set_if_empty(schema, "io_type", "출고")
            return

        if ("입고" in line) ^ ("출고" in line):
            parsed = parse_io_type(line)
            if parsed:
                set_if_empty(schema, "io_type", parsed["io_type"])
                return


def recover_ticket_id_from_next_line(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    if not is_empty(schema["ticket_id"]):
        return

    for idx in range(len(normalized_lines) - 1):
        if not RE_ONLY_TICKET_LABEL.match(normalized_lines[idx]):
            continue
        parsed = parse_ticket_id(normalized_lines[idx + 1])
        if not parsed:
            continue
        set_if_empty(schema, "ticket_id", parsed["ticket_id"])
        return


def recover_measure_count_from_next_line(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    if not is_empty(schema.get("measure_count")):
        return

    for idx in range(len(normalized_lines) - 1):
        if not RE_ONLY_MEASURE_COUNT_LABEL.match(normalized_lines[idx]):
            continue
        parsed = parse_measure_count(normalized_lines[idx + 1])
        if not parsed:
            continue
        set_if_empty(schema, "measure_count", parsed["measure_count"])
        return


def recover_customer_name(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    if not is_empty(schema["customer_name"]):
        return

    for line in normalized_lines:
        match = RE_CUSTOMER_HONORIFIC.match(line)
        if not match:
            continue
        parsed = parse_customer_name(match.group("name"))
        if not parsed:
            continue
        set_if_empty(schema, "customer_name", parsed["customer_name"])
        return
