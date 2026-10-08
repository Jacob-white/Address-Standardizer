"""
Secondary-unit (suite/apt/flat) normalization helpers (split out of standardizer.py).
"""

import logging
import re
from typing import Tuple

from address_standardizer.tables import (
    DIRECTIONALS,
    STREET_SUFFIXES,
    SECONDARY_UNITS,
)
from address_standardizer._patterns import (
    RE_WHITESPACE,
    RE_NON_ALPHANUMERIC,
    RE_GLUED_HASH,
    RE_GLUED_UNIT,
    RE_GLUED_HOUSE_NUM,
    clean_repetitive_cycles,
    RE_ATTACHED_SUFFIX_EXPLICIT_UNIT,
    RE_ATTACHED_SUFFIX_BARE_UNIT,
    RE_SAINT_HYPHEN,
    RE_PRIVATE_MAILBOX,
    RE_HYPHENATED_UNIT,
    RE_INTL_FLAT,
    RE_INTL_SEC_INLINE,
    RE_INTL_SEC_START,
)

logger = logging.getLogger(__name__)


def _pre_normalize_address_string(text: str) -> str:
    """Pre-normalizes glued punctuation, symbols, formatting, and repetitive cycles."""
    text = clean_repetitive_cycles(text)
    # Split glued house numbers: '3340PEACHTREE ROAD' -> '3340 PEACHTREE ROAD'
    text = RE_GLUED_HOUSE_NUM.sub(r"\1 \2", text.strip())
    # Split glued hashtags: 'Main St#101' -> 'Main St # 101'
    text = RE_GLUED_HASH.sub(" # ", text)
    # Split glued unit prefixes: 'Apt.4B' -> 'Apt 4B'
    text = RE_GLUED_UNIT.sub(r"\1 ", text)
    # Normalize Saint hyphenation e.g. 'St-Charles' -> 'St Charles', 'Saint-Gaudens' -> 'Saint Gaudens'
    text = RE_SAINT_HYPHEN.sub(r"\1 \2", text)
    # Suffix-attached unit: 'Main St-Ste 200' -> 'Main St STE 200', 'Main St-4B' -> 'Main St APT 4B'
    text = RE_ATTACHED_SUFFIX_EXPLICIT_UNIT.sub(r"\1 \2 \3", text)
    text = RE_ATTACHED_SUFFIX_BARE_UNIT.sub(r"\1 APT \2", text)
    # Normalize Private Mailbox to PMB
    text = RE_PRIVATE_MAILBOX.sub("PMB", text)
    # Normalize STE-400 -> STE 400
    text = RE_HYPHENATED_UNIT.sub(r"\1 \2", text)
    return text


def _standardize_secondary_unit(sec: str) -> str:
    """Standardizes secondary units according to USPS Pub 28, deduplicates repeated tokens, and enforces FL <num>."""
    if not sec:
        return ""
    # Strip any leading STE or SUITE if followed by other unit types (FL, APT, UNIT, DEPT, PH, SUITE, STE) or ordinal floor
    s = re.sub(
        r"^(?:STE|SUITE)\s+(?=(?:\d+(?:ST|ND|RD|TH)\s+)?(?:FL|FLOOR|FLR|APT|APARTMENT|UNIT|DEPT|DEPARTMENT|PH|PENTHOUSE|SUITE|STE)\b)",
        "",
        sec.strip().upper(),
        flags=re.IGNORECASE,
    )
    # Clean separator punctuation between tokens, preserving hyphens in unit identifiers like 4-B or PH-A
    s = re.sub(r"[,;]+", " ", s)
    s = re.sub(r"\s+[\-–—\/]\s+", " ", s)
    raw_tokens = s.split()
    if not raw_tokens:
        return ""

    tokens = []
    for t in raw_tokens:
        if t in ("SUITE", "SUIT"):
            tokens.append("STE")
        elif t in ("FLOOR", "FLR"):
            tokens.append("FL")
        elif t in ("APARTMENT", "APPT"):
            tokens.append("APT")
        else:
            tokens.append(t)

    # Token-level repeat deduplication
    for rlen in range(1, len(tokens) // 2 + 1):
        if len(tokens) % rlen == 0:
            chunk = tokens[:rlen]
            if chunk * (len(tokens) // rlen) == tokens:
                tokens = chunk
                break

    # Floor normalization: Pub 28 strict format FL <num>
    if len(tokens) == 2 and tokens[1] in ("FL", "FLOOR", "FLR"):
        m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[0])
        if m:
            tokens = ["FL", m.group(1)]
    elif len(tokens) == 2 and tokens[0] in ("FL", "FLOOR", "FLR"):
        m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[1])
        if m:
            tokens = ["FL", m.group(1)]
    else:
        new_toks = []
        i = 0
        while i < len(tokens):
            if i + 1 < len(tokens) and tokens[i+1] in ("FL", "FLOOR", "FLR"):
                is_preceded_by_unit = (i > 0 and tokens[i-1] in ("STE", "APT", "UNIT", "DEPT", "RM", "ROOM", "BLDG", "PH"))
                is_ordinal = bool(re.search(r"(?:ST|ND|RD|TH)$", tokens[i]))
                m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[i])
                if m and (not is_preceded_by_unit or is_ordinal):
                    new_toks.extend(["FL", m.group(1)])
                    i += 2
                    continue
            if tokens[i] in ("FL", "FLOOR", "FLR") and i + 1 < len(tokens):
                m = re.match(r"^(\d+)(?:ST|ND|RD|TH)?$", tokens[i+1])
                if m:
                    new_toks.extend(["FL", m.group(1)])
                    i += 2
                    continue
            new_toks.append(tokens[i])
            i += 1
        tokens = new_toks

    # Final repeat check after normalization
    for rlen in range(1, len(tokens) // 2 + 1):
        if len(tokens) % rlen == 0:
            chunk = tokens[:rlen]
            if chunk * (len(tokens) // rlen) == tokens:
                tokens = chunk
                break

    res = " ".join(tokens)
    # Strip any STE or SUITE prepended to FL, APT, UNIT, DEPT, PH
    res = re.sub(r"^(?:STE|SUITE)\s+(FL|APT|UNIT|DEPT|PH)\b", r"\1", res)
    return res


def _split_international_secondary_unit(street1: str, street2: str) -> Tuple[str, str]:
    """Helper to detect and split secondary unit in international street string, and normalize suffixes."""
    st1 = (street1 or "").upper()
    st2 = (street2 or "").upper()

    # Pre-split Flat / Apt at start: "Flat 4 150 High Street" -> st1="150 High Street", st2="APT 4"
    m_flat = RE_INTL_FLAT.match(st1)
    if m_flat:
        st2_cand = f"APT {m_flat.group(1).upper()}"
        st2 = f"{st2_cand} {st2}".strip() if st2 else st2_cand
        st1 = m_flat.group(2).strip()

    if not st2:
        m = RE_INTL_SEC_INLINE.search(st1)
        if m:
            sec_type = m.group(1).upper()
            sec_id = m.group(2).upper()
            sec_type_norm = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
            st2 = f"{sec_type_norm} {sec_id}"
            st1 = st1[:m.start()] + st1[m.end():]
            st1 = RE_WHITESPACE.sub(" ", st1.strip(" ,.-"))
    elif st2:
        m2 = RE_INTL_SEC_START.match(st2)
        if m2:
            sec_type = m2.group(1).upper()
            sec_type_norm = SECONDARY_UNITS.get(sec_type, "APT" if sec_type == "FLAT" else sec_type)
            st2 = f"{sec_type_norm} {m2.group(2).strip()}"

    words = st1.split()
    norm_words = []
    for w in words:
        w_clean = RE_NON_ALPHANUMERIC.sub("", w).upper()
        if w_clean in STREET_SUFFIXES:
            norm_words.append(STREET_SUFFIXES[w_clean])
        elif w_clean in DIRECTIONALS:
            norm_words.append(DIRECTIONALS[w_clean])
        else:
            norm_words.append(w)
    st1 = " ".join(norm_words)

    return st1, st2
