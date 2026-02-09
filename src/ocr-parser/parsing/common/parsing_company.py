"""
회사명 역할 추론(issuer/counterparty) 모듈입니다.

왜 별도 모듈인가:
- 기존 stage1/stage2 파싱 흐름을 크게 바꾸지 않기 위해
- "후보 수집 -> 점수화 -> 최종 결정"을 독립 단계로 추가하기 위해

샘플 기반 근거:
- sample_03: "회 사 명 :" 값이 비어 있지만 "정우리사이클링 (주)" + 주소/Tel 블록이 있어 issuer는 추론 가능
- sample_04: "(주) 하 은 펄 프" + 주소/TEL/FAX는 issuer, "신성(푸디스트) 귀하"는 counterparty로 분리 가능
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


# 점수 계산 시 주변 줄을 보는 범위입니다.
# OCR 문서는 회사명, 주소, 연락처가 3~5줄 이내에 모이는 경우가 많아 ±4를 사용합니다.
NEAR_LINE_WINDOW = 4

# 증명 문구 직후 회사명이 붙는 패턴(sample_01, sample_03, sample_04)을 반영한 범위입니다.
PROOF_NEAR_WINDOW = 2


# 주소/연락처/증명 문구 패턴(너무 과도하지 않게, 샘플 기반으로 적당한 폭만 허용)
RE_ADDRESS_HINT = re.compile(r"(도|시|군|구|읍|면|동|로|길|번길)\b")
RE_TEL = re.compile(r"(?:TEL|전화|연락처)\s*[:)]?\s*[\d\-()]+", re.IGNORECASE)
RE_FAX = re.compile(r"(?:FAX)\s*[:)]?\s*[\d\-()]+", re.IGNORECASE)
RE_PHONE_ONLY = re.compile(r"\b0\d{1,2}-\d{3,4}-\d{4}\b")
RE_PROOF_PHRASE = re.compile(r"(확인함|증명함|증명합니다)")


# 회사명스멜 키워드
RE_COMPANY_SMELL = re.compile(
    r"(\(주\)|주식회사|유한회사|합자회사|Inc\.?|Co\.?|Corp\.?|C&S)",
    re.IGNORECASE,
)

# 거래상대방 라벨 힌트
RE_COUNTERPARTY_LABEL = re.compile(r"^(?:거래처|상호|회사명|수신)\s*[:\-]?\s*(?P<name>.+)$")

# "귀하"는 상대방 시그널이 매우 강함
RE_HONORIFIC = re.compile(r"^(?P<name>.+?)\s*귀하$")

# 문서 헤더/표 영역 힌트
RE_TABLE_AREA_HINT = re.compile(r"(품명|구분|차량|계량|일시|날짜)")

# 중량/시간/좌표 등 노이즈 제거용
RE_WEIGHT_OR_TIME = re.compile(r"(kg|\d{1,2}:\d{2}(?::\d{2})?)", re.IGNORECASE)
RE_COORDINATE = re.compile(r"^-?\d{1,3}\.\d+\s*,\s*-?\d{1,3}\.\d+$")


@dataclass
class CompanyCandidate:
    """
    회사명 후보 1건입니다.

    fields:
    - text: 후보 문자열
    - line_idx: 원문 라인 번호
    - rule_id: 어떤 규칙으로 후보가 만들어졌는지 추적용
    """

    text: str
    line_idx: int
    rule_id: str


def _dedupe_candidates(candidates: list[CompanyCandidate]) -> list[CompanyCandidate]:
    """
    동일 문자열 후보를 중복 제거합니다.
    """
    out: list[CompanyCandidate] = []
    seen: set[str] = set()
    for candidate in candidates:
        key = candidate.text.strip()
        if key in seen:
            continue
        seen.add(key)
        out.append(candidate)
    return out


def _is_meaningful_company_text(text: str) -> bool:
    """
    회사명 후보로 의미 있는 텍스트인지 필터링합니다.
    """
    stripped = text.strip()
    if len(stripped) <= 2:
        return False
    if RE_COORDINATE.search(stripped):
        return False
    # 주소/연락처 라인은 회사명 후보에서 제외합니다.
    if RE_ADDRESS_HINT.search(stripped) and not RE_COMPANY_SMELL.search(stripped):
        return False
    if RE_TEL.search(stripped) or RE_FAX.search(stripped) or RE_PHONE_ONLY.search(stripped):
        return False
    if RE_WEIGHT_OR_TIME.search(stripped) and not RE_COMPANY_SMELL.search(stripped):
        return False
    if not re.search(r"[A-Za-z가-힣]", stripped):
        return False
    return True


def extract_company_candidates(lines: list[str], normalized_lines: list[str]) -> list[dict[str, Any]]:
    """
    회사명 후보를 0~N개 수집합니다.

    반환 형식:
    - 기존 candidate 스타일과 맞추기 위해 dict 리스트로 반환
    - 필수 키: text, line_idx, rule_id
    """
    collected: list[CompanyCandidate] = []

    for idx, line in enumerate(normalized_lines):
        # 1) "거래처/상호/회사명/수신: 값" 라벨 기반 후보
        match = RE_COUNTERPARTY_LABEL.match(line)
        if match:
            name = match.group("name").strip()
            if _is_meaningful_company_text(name):
                collected.append(CompanyCandidate(name, idx, "COMPANY_CANDIDATE_LABEL"))

        # 2) "... 귀하" 후보 (counterparty 강한 신호)
        honorific = RE_HONORIFIC.match(line)
        if honorific:
            name = honorific.group("name").strip()
            if _is_meaningful_company_text(name):
                collected.append(CompanyCandidate(name, idx, "COMPANY_CANDIDATE_HONORIFIC"))

        # 3) 일반 회사명 스멜 후보
        if RE_COMPANY_SMELL.search(line) and _is_meaningful_company_text(line):
            collected.append(CompanyCandidate(line.strip(), idx, "COMPANY_CANDIDATE_SMELL"))

        # 4) 주소/전화 바로 앞 줄은 issuer 후보일 확률이 높음 (sample_03, sample_04 케이스)
        if idx + 1 < len(normalized_lines):
            next_line = normalized_lines[idx + 1]
            if (
                (RE_ADDRESS_HINT.search(next_line) or RE_TEL.search(next_line) or RE_FAX.search(next_line))
                and not RE_ADDRESS_HINT.search(line)
                and not RE_TEL.search(line)
                and not RE_FAX.search(line)
                and _is_meaningful_company_text(line)
            ):
                collected.append(CompanyCandidate(line.strip(), idx, "COMPANY_CANDIDATE_BEFORE_CONTACT"))

    deduped = _dedupe_candidates(collected)
    return [{"text": c.text, "line_idx": c.line_idx, "rule_id": c.rule_id} for c in deduped]


def _has_contact_or_address_near(normalized_lines: list[str], idx: int) -> bool:
    start = max(0, idx - NEAR_LINE_WINDOW)
    end = min(len(normalized_lines), idx + NEAR_LINE_WINDOW + 1)
    for i in range(start, end):
        line = normalized_lines[i]
        if RE_ADDRESS_HINT.search(line) or RE_TEL.search(line) or RE_FAX.search(line) or RE_PHONE_ONLY.search(line):
            return True
    return False


def _is_near_proof_phrase(normalized_lines: list[str], idx: int) -> bool:
    start = max(0, idx - PROOF_NEAR_WINDOW)
    end = min(len(normalized_lines), idx + PROOF_NEAR_WINDOW + 1)
    for i in range(start, end):
        if RE_PROOF_PHRASE.search(normalized_lines[i]):
            return True
    return False


def _header_contact_chain(normalized_lines: list[str], idx: int) -> bool:
    """
    상단 회사명 -> 주소/TEL/FAX 연쇄 패턴을 체크합니다.
    """
    if idx > 5:
        return False
    next_span = normalized_lines[idx + 1 : idx + 5]
    if not next_span:
        return False
    has_address = any(RE_ADDRESS_HINT.search(line) for line in next_span)
    has_contact = any(RE_TEL.search(line) or RE_FAX.search(line) or RE_PHONE_ONLY.search(line) for line in next_span)
    return has_address and has_contact


def score_company_role(
    candidates: list[dict[str, Any]],
    lines: list[str],
    idx: int | None = None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[dict[str, Any]]]:
    """
    후보마다 issuer/counterparty 점수를 계산합니다.

    반환:
    - issuer_best: issuer 최고점 후보(dict)
    - counterparty_best: counterparty 최고점 후보(dict)
    - debug_scores: 후보별 점수/근거 리스트
    """
    _ = lines  # 시그니처를 요구사항에 맞추기 위해 유지 (현재는 normalized line 중심 사용)
    _ = idx

    normalized_lines = [line.strip() for line in lines]
    debug_scores: list[dict[str, Any]] = []
    scored: list[dict[str, Any]] = []

    for candidate in candidates:
        text = str(candidate["text"]).strip()
        line_idx = int(candidate["line_idx"])
        rule_id = str(candidate["rule_id"])

        issuer_score = 0
        counterparty_score = 0
        reasons: list[str] = []

        if RE_COMPANY_SMELL.search(text):
            issuer_score += 2
            reasons.append("ISSUER_COMPANY_SMELL")

        if rule_id == "COMPANY_CANDIDATE_HONORIFIC" or RE_HONORIFIC.match(text):
            counterparty_score += 6
            reasons.append("COUNTERPARTY_HONORIFIC")

        if rule_id == "COMPANY_CANDIDATE_LABEL" or RE_COUNTERPARTY_LABEL.match(normalized_lines[line_idx]):
            counterparty_score += 4
            reasons.append("COUNTERPARTY_LABEL_DIRECT")

        if _has_contact_or_address_near(normalized_lines, line_idx):
            issuer_score += 4
            counterparty_score -= 1
            reasons.append("ISSUER_NEAR_CONTACT_BLOCK")

        if _is_near_proof_phrase(normalized_lines, line_idx):
            issuer_score += 3
            reasons.append("ISSUER_NEAR_PROOF_PHRASE")

        if _header_contact_chain(normalized_lines, line_idx):
            issuer_score += 4
            reasons.append("ISSUER_HEADER_CONTACT_CHAIN")

        if RE_TABLE_AREA_HINT.search(" ".join(normalized_lines[max(0, line_idx - 2) : line_idx + 3])):
            counterparty_score += 1
            reasons.append("COUNTERPARTY_NEAR_TABLE_AREA")

        entry = {
            "text": text,
            "line_idx": line_idx,
            "rule_id": rule_id,
            "issuer_score": issuer_score,
            "counterparty_score": counterparty_score,
            "reasons": reasons,
        }
        debug_scores.append(entry)
        scored.append(entry)

    issuer_best: dict[str, Any] | None = None
    counterparty_best: dict[str, Any] | None = None

    if scored:
        issuer_best = max(scored, key=lambda row: row["issuer_score"])
        counterparty_best = max(scored, key=lambda row: row["counterparty_score"])

    return issuer_best, counterparty_best, debug_scores


def resolve_companies(
    schema: dict[str, Any],
    lines: list[str],
    normalized_lines: list[str],
) -> dict[str, Any]:
    """
    회사명 최종 결정을 수행하고 schema에 반영합니다.

    우선순위:
    1) 기존 라벨 기반 값(customer_name) 유지
    2) 빈 값만 후보/스코어링으로 보강
    3) issuer/counterparty 중복 시 경고
    4) issuer 존재 + counterparty 부재 시 누락 경고
    """
    warnings: list[str] = []
    existing_warnings = schema.get("warnings")
    if isinstance(existing_warnings, list):
        warnings = [str(w) for w in existing_warnings if str(w)]
    elif existing_warnings:
        warnings = [w for w in str(existing_warnings).split("|") if w]

    candidates = extract_company_candidates(lines, normalized_lines)
    issuer_best, counterparty_best, debug_scores = score_company_role(
        candidates=candidates,
        lines=normalized_lines,
        idx=None,
    )

    # 기존 customer_name(라벨 기반)이 이미 있으면 counterparty로 우선 사용합니다.
    if not schema.get("customer_name") and counterparty_best and counterparty_best["counterparty_score"] > 0:
        schema["customer_name"] = counterparty_best["text"]
        warnings.append(f"COUNTERPARTY_FROM_SCORE:{counterparty_best['rule_id']}")

    if not schema.get("issuer_name") and issuer_best and issuer_best["issuer_score"] > 0:
        schema["issuer_name"] = issuer_best["text"]
        warnings.append(f"ISSUER_FROM_SCORE:{issuer_best['rule_id']}")

    issuer_name = str(schema.get("issuer_name", "")).strip()
    counterparty_name = str(schema.get("customer_name", "")).strip()

    if issuer_name and counterparty_name and issuer_name == counterparty_name:
        # 같은 문자열이 양쪽 역할로 뽑힌 경우는 모호하므로 counterparty를 비웁니다.
        # (발행처/수신처를 분리해야 하는 업무 요구사항 반영)
        schema["customer_name"] = ""
        warnings.append("COMPANY_ROLE_DUPLICATE_AMBIGUOUS")

    # sample_03처럼 issuer는 존재하지만 counterparty가 OCR 누락될 수 있는 케이스를 경고로 남깁니다.
    if str(schema.get("issuer_name", "")).strip() and not str(schema.get("customer_name", "")).strip():
        warnings.append("COUNTERPARTY_MISSING_POSSIBLE_OCR_DROP")

    # 디버깅 추적용: 후보 개수와 최고점 정보를 warnings에 축약 기록합니다.
    # (기존 스키마를 크게 흔들지 않기 위해 별도 필드 대신 warning key로 남깁니다.)
    warnings.append(f"COMPANY_CANDIDATE_COUNT:{len(candidates)}")
    if debug_scores:
        top_issuer = max(debug_scores, key=lambda row: row["issuer_score"])
        top_counterparty = max(debug_scores, key=lambda row: row["counterparty_score"])
        warnings.append(
            f"COMPANY_TOP_ISSUER:{top_issuer['rule_id']}:{top_issuer['issuer_score']}"
        )
        warnings.append(
            f"COMPANY_TOP_COUNTERPARTY:{top_counterparty['rule_id']}:{top_counterparty['counterparty_score']}"
        )

    # 중복 warning 키 제거
    uniq_warnings: list[str] = []
    seen: set[str] = set()
    for warning in warnings:
        if warning in seen:
            continue
        seen.add(warning)
        uniq_warnings.append(warning)

    schema["warnings"] = uniq_warnings
    return schema
