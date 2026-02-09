from __future__ import annotations

from typing import Any

from parsing.common.patterns import RE_COORDINATE_LINE
from parsing.stage2.recovery_common import append_warning, is_empty, set_if_empty


def recover_gps(schema: dict[str, Any], normalized_lines: list[str]) -> None:
    """
    라벨 없는 좌표 라인을 찾아 gps_lat/gps_lon을 복구합니다.
    """
    if not is_empty(schema.get("gps_lat")) or not is_empty(schema.get("gps_lon")):
        return

    for line in normalized_lines:
        match = RE_COORDINATE_LINE.match(line)
        if not match:
            continue

        first = float(match.group(1))
        second = float(match.group(2))

        first_is_lat = -90 <= first <= 90
        second_is_lon = -180 <= second <= 180
        first_is_lon = -180 <= first <= 180
        second_is_lat = -90 <= second <= 90

        if first_is_lat and second_is_lon and abs(second) > 90:
            set_if_empty(schema, "gps_lat", first)
            set_if_empty(schema, "gps_lon", second)
            return

        if first_is_lon and second_is_lat and abs(first) > 90:
            set_if_empty(schema, "gps_lat", second)
            set_if_empty(schema, "gps_lon", first)
            append_warning(schema, "GPS_ORDER_SWAPPED_BY_RANGE_HEURISTIC")
            return

        if first_is_lat and second_is_lat:
            append_warning(schema, "GPS_AMBIGUOUS_LAT_LON_ORDER")
            continue

        append_warning(schema, "GPS_CANDIDATE_OUT_OF_RANGE")

