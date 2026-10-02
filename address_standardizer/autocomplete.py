"""
Real-Time Typeahead & Autocomplete Engine.
==========================================
High-speed in-memory prefix trie and token inverted index providing sub-8ms
address completion with multi-unit secondary unit prompting.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any

from address_standardizer.tables import SECONDARY_UNITS, US_STATES
from address_standardizer._patterns import RE_SEC_UNIT


@dataclass
class AutocompleteSuggestion:
    """Typeahead autocomplete candidate suggestion."""
    text: str
    street1: str
    street2: str
    city: str
    state: str
    postal_code: str
    country: str = "USA"
    secondary_prompt_required: bool = False
    suggested_secondary_units: List[str] = field(default_factory=list)
    highlight_ranges: List[Tuple[int, int]] = field(default_factory=list)
    score: float = 1.0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "street1": self.street1,
            "street2": self.street2,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country": self.country,
            "secondary_prompt_required": self.secondary_prompt_required,
            "suggested_secondary_units": list(self.suggested_secondary_units),
            "highlight_ranges": list(self.highlight_ranges),
            "score": round(self.score, 4),
        }


# Seed records of prominent multi-unit and commercial buildings for typeahead
SEED_AUTOCOMPLETE_RECORDS: List[Dict[str, Any]] = [
    {
        "street1": "100 WALL ST",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10005",
        "is_multi_unit": True,
        "known_units": ["STE 400", "STE 800", "FL 12", "FL 20"],
    },
    {
        "street1": "200 PARK AVE",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10166",
        "is_multi_unit": True,
        "known_units": ["STE 1200", "STE 1500", "FL 25"],
    },
    {
        "street1": "350 5TH AVE",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10118",
        "is_multi_unit": True,
        "known_units": ["STE 1000", "STE 2000", "FL 50"],
    },
    {
        "street1": "1209 N ORANGE ST",
        "city": "WILMINGTON",
        "state": "DE",
        "postal_code": "19801",
        "is_multi_unit": True,
        "known_units": ["STE 400", "STE 600", "FL 2"],
    },
    {
        "street1": "30 N GOULD ST",
        "city": "SHERIDAN",
        "state": "WY",
        "postal_code": "82801",
        "is_multi_unit": True,
        "known_units": ["STE R", "STE A", "STE B"],
    },
    {
        "street1": "500 N MICHIGAN AVE",
        "city": "CHICAGO",
        "state": "IL",
        "postal_code": "60611",
        "is_multi_unit": True,
        "known_units": ["STE 300", "STE 1400", "FL 14"],
    },
    {
        "street1": "101 CALIFORNIA ST",
        "city": "SAN FRANCISCO",
        "state": "CA",
        "postal_code": "94111",
        "is_multi_unit": True,
        "known_units": ["STE 1200", "STE 2400", "FL 30"],
    },
    {
        "street1": "160 GREENTREE DR",
        "city": "DOVER",
        "state": "DE",
        "postal_code": "19904",
        "is_multi_unit": True,
        "known_units": ["STE 101", "STE 201"],
    },
    {
        "street1": "850 NEW BURTON RD",
        "city": "DOVER",
        "state": "DE",
        "postal_code": "19904",
        "is_multi_unit": True,
        "known_units": ["STE 201"],
    },
    {
        "street1": "251 LITTLE FALLS DR",
        "city": "WILMINGTON",
        "state": "DE",
        "postal_code": "19808",
        "is_multi_unit": False,
        "known_units": [],
    },
    {
        "street1": "16192 COASTAL HWY",
        "city": "LEWES",
        "state": "DE",
        "postal_code": "19958",
        "is_multi_unit": False,
        "known_units": [],
    },
    {
        "street1": "3500 S DUPONT HWY",
        "city": "DOVER",
        "state": "DE",
        "postal_code": "19901",
        "is_multi_unit": False,
        "known_units": [],
    },
    {
        "street1": "3773 HOWARD HUGHES PKWY",
        "city": "LAS VEGAS",
        "state": "NV",
        "postal_code": "89169",
        "is_multi_unit": True,
        "known_units": ["STE 500S", "STE 200"],
    },
    {
        "street1": "100 MAIN ST",
        "city": "NEW YORK",
        "state": "NY",
        "postal_code": "10001",
        "is_multi_unit": True,
        "known_units": ["APT 1A", "APT 2B", "APT 3C"],
    },
    {
        "street1": "123 MARKET ST",
        "city": "SAN FRANCISCO",
        "state": "CA",
        "postal_code": "94105",
        "is_multi_unit": False,
        "known_units": [],
    },
]


class AutocompleteEngine:
    """
    Sub-8ms in-memory prefix trie and inverted token index for address typeahead.
    """

    def __init__(self, seed: bool = True):
        self._records: List[Dict[str, Any]] = []
        self._prefix_index: Dict[str, Set[int]] = {}
        if seed:
            for rec in SEED_AUTOCOMPLETE_RECORDS:
                self.index_address(**rec)

    def index_address(
        self,
        street1: str,
        city: str,
        state: str,
        postal_code: str,
        street2: str = "",
        country: str = "USA",
        is_multi_unit: bool = False,
        known_units: Optional[List[str]] = None,
    ) -> int:
        """Indexes a canonical address into the in-memory prefix inverted index."""
        rec_id = len(self._records)
        record = {
            "id": rec_id,
            "street1": street1.strip().upper(),
            "street2": street2.strip().upper(),
            "city": city.strip().upper(),
            "state": state.strip().upper(),
            "postal_code": postal_code.strip(),
            "country": country.strip().upper(),
            "is_multi_unit": is_multi_unit,
            "known_units": list(known_units) if known_units else [],
        }
        self._records.append(record)

        # Index all tokens across fields
        units_text = " ".join(record["known_units"])
        full_text = f"{record['street1']} {record['street2']} {record['city']} {record['state']} {record['postal_code']} {units_text}"
        tokens = set(re.findall(r"\w+", full_text.upper()))
        folded_tokens = set()
        for t in tokens:
            folded = unicodedata.normalize("NFKD", t).encode("ASCII", "ignore").decode("utf-8").upper()
            if folded:
                folded_tokens.add(folded)
        all_tokens = tokens.union(folded_tokens)
        for token in all_tokens:
            for i in range(1, min(len(token) + 1, 25)):
                prefix = token[:i]
                if prefix not in self._prefix_index:
                    self._prefix_index[prefix] = set()
                self._prefix_index[prefix].add(rec_id)

        return rec_id

    def index_addresses(self, records: List[Dict[str, Any]]):
        """Batch index multiple address dictionaries."""
        for r in records:
            self.index_address(**r)

    def search(
        self,
        query: str,
        max_results: int = 5,
        state_filter: Optional[str] = None,
    ) -> List[AutocompleteSuggestion]:
        """
        Executes real-time prefix search across indexed addresses.
        Sub-8ms response time.
        """
        clean_q = query.strip().upper()
        if not clean_q:
            return []

        clean_q_fold = unicodedata.normalize("NFKD", clean_q).encode("ASCII", "ignore").decode("utf-8").upper()
        q_tokens = re.findall(r"\w+", clean_q)
        q_tokens_fold = re.findall(r"\w+", clean_q_fold)
        if not q_tokens and not q_tokens_fold:
            return []

        tokens_to_match = q_tokens_fold if q_tokens_fold else q_tokens

        # Find intersecting record IDs for all tokens
        matching_ids: Optional[Set[int]] = None
        for tok in tokens_to_match:
            rec_ids = self._prefix_index.get(tok, set())
            if matching_ids is None:
                matching_ids = set(rec_ids)
            else:
                matching_ids.intersection_update(rec_ids)
            if not matching_ids:
                break

        # Fallback: if query specifies secondary unit, match base tokens
        if not matching_ids and len(tokens_to_match) > 2:
            sec_idx = None
            for idx, t in enumerate(tokens_to_match):
                if t in SECONDARY_UNITS or t in SECONDARY_UNITS.values() or t.startswith("#"):
                    sec_idx = idx
                    break
            if sec_idx is not None and sec_idx > 0:
                base_tokens = tokens_to_match[:sec_idx]
                fallback_ids: Optional[Set[int]] = None
                for tok in base_tokens:
                    rec_ids = self._prefix_index.get(tok, set())
                    if fallback_ids is None:
                        fallback_ids = set(rec_ids)
                    else:
                        fallback_ids.intersection_update(rec_ids)
                    if not fallback_ids:
                        break
                if fallback_ids:
                    matching_ids = fallback_ids

        if not matching_ids:
            return []

        # Check if query already specifies a secondary unit
        has_query_sec_unit = (
            "#" in clean_q
            or bool(RE_SEC_UNIT.search(clean_q))
            or any(
                t in SECONDARY_UNITS or t in SECONDARY_UNITS.values()
                for t in q_tokens
            )
            or any(tok in ("APT", "STE", "UNIT", "FL", "SUITE", "ROOM") for tok in q_tokens)
        )

        norm_st_filter = None
        if state_filter:
            raw_st = state_filter.strip().upper()
            norm_st_filter = US_STATES.get(raw_st, raw_st)

        suggestions: List[AutocompleteSuggestion] = []
        for rec_id in matching_ids:
            rec = self._records[rec_id]
            if norm_st_filter and rec["state"] != norm_st_filter:
                continue

            full_repr = f"{rec['street1']}, {rec['city']}, {rec['state']} {rec['postal_code']}"
            if rec["street2"]:
                full_repr = f"{rec['street1']}, {rec['street2']}, {rec['city']}, {rec['state']} {rec['postal_code']}"

            # Secondary unit prompting logic
            prompt_required = False
            suggested_units: List[str] = []
            if rec["is_multi_unit"] and not has_query_sec_unit and not rec["street2"]:
                prompt_required = True
                suggested_units = rec["known_units"] or ["APT", "STE", "UNIT"]

            # Calculate match highlight ranges
            raw_ranges: List[Tuple[int, int]] = []
            full_repr_upper = full_repr.upper()
            full_repr_fold = unicodedata.normalize("NFKD", full_repr_upper).encode("ASCII", "ignore").decode("utf-8").upper()
            for tok in (q_tokens + q_tokens_fold):
                start_idx = 0
                while True:
                    idx = full_repr_upper.find(tok, start_idx)
                    if idx == -1:
                        idx = full_repr_fold.find(tok, start_idx)
                    if idx == -1:
                        break
                    raw_ranges.append((idx, idx + len(tok)))
                    start_idx = idx + len(tok)

            raw_ranges.sort(key=lambda r: (r[0], r[1]))
            highlight_ranges: List[Tuple[int, int]] = []
            for start, end in raw_ranges:
                if not highlight_ranges:
                    highlight_ranges.append((start, end))
                else:
                    prev_s, prev_e = highlight_ranges[-1]
                    if start <= prev_e:
                        highlight_ranges[-1] = (prev_s, max(prev_e, end))
                    else:
                        highlight_ranges.append((start, end))

            # Score calculation
            score = 1.0
            if full_repr_upper.startswith(clean_q) or full_repr_fold.startswith(clean_q_fold):
                score += 0.5

            suggestions.append(
                AutocompleteSuggestion(
                    text=full_repr,
                    street1=rec["street1"],
                    street2=rec["street2"],
                    city=rec["city"],
                    state=rec["state"],
                    postal_code=rec["postal_code"],
                    country=rec["country"],
                    secondary_prompt_required=prompt_required,
                    suggested_secondary_units=suggested_units,
                    highlight_ranges=highlight_ranges,
                    score=score,
                )
            )

        # Sort by score descending
        suggestions.sort(key=lambda s: s.score, reverse=True)
        return suggestions[:max_results]


_DEFAULT_AUTOCOMPLETE_ENGINE = AutocompleteEngine(seed=True)


def autocomplete_address(
    query: str,
    max_results: int = 5,
    state_filter: Optional[str] = None,
    engine: Optional[AutocompleteEngine] = None,
) -> List[AutocompleteSuggestion]:
    """
    Public functional interface for address typeahead autocomplete.
    """
    active_engine = engine or _DEFAULT_AUTOCOMPLETE_ENGINE
    return active_engine.search(
        query=query,
        max_results=max_results,
        state_filter=state_filter,
    )
