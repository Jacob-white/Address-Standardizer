"""
Confidence Scoring & Routing Engine.
=====================================
Implements composite confidence scoring (0.0 to 1.0) and automated 3-tier routing:
  - Tier 1: Auto-Pass Queue (S >= 0.95)
  - Tier 2: Fuzzy Review & Automated Enrichment (0.80 <= S < 0.95)
  - Tier 3: Manual Stewardship Queue (S < 0.80 or address_status == 'parse_failed')

Formula:
  S = 0.35 * S_parse + 0.35 * S_ref_match + 0.15 * S_geo + 0.15 * S_cross_field
"""

import re
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from address_standardizer.tables import (
    US_STATES,
    STREET_SUFFIXES,
    DIRECTIONALS,
    ZIP3_TO_STATE,
    METRO_ZIP3_CENTROIDS,
    STATE_CENTROIDS,
    LANDMARK_CAMPUS_KEYWORDS,
)


class RoutingTier:
    AUTO_PASS = "AUTO_PASS"
    FUZZY_REVIEW = "FUZZY_REVIEW"
    MANUAL_STEWARDSHIP = "MANUAL_STEWARDSHIP"


# Operational Failure & Warning Reason Codes (Blueprint Section 1.4.2)
ERR_ZIP_STATE_MISMATCH = "ERR_ZIP_STATE_MISMATCH"
ERR_MISSING_HOUSE_NUM = "ERR_MISSING_HOUSE_NUM"
ERR_UNRESOLVED_SUFFIX = "ERR_UNRESOLVED_SUFFIX"
ERR_AMBIGUOUS_DUAL_ADDR = "ERR_AMBIGUOUS_DUAL_ADDR"
ERR_DPV_UNCONFIRMED = "ERR_DPV_UNCONFIRMED"
WARN_CRA_HUB_DETECTED = "WARN_CRA_HUB_DETECTED"
WARN_PMB_DISGUISED = "WARN_PMB_DISGUISED"
WARN_RESIDENTIAL_COMM = "WARN_RESIDENTIAL_COMM"
WARN_TYPO_HEALED = "WARN_TYPO_HEALED"
WARN_STATE_CORRECTED_FROM_ZIP = "WARN_STATE_CORRECTED_FROM_ZIP"
WARN_CMRA_DETECTED = "WARN_CMRA_DETECTED"
WARN_MISSING_SECONDARY_UNIT = "WARN_MISSING_SECONDARY_UNIT"
WARN_VACANT_DELIVERY_POINT = "WARN_VACANT_DELIVERY_POINT"
WARN_LANDMARK_CAMPUS_PREMISE = "WARN_LANDMARK_CAMPUS_PREMISE"
WARN_LOCALITY_ONLY = "WARN_LOCALITY_ONLY"
NO_STREET_NUMBER = "NO_STREET_NUMBER"
ERR_PARSE_FAILED = "ERR_PARSE_FAILED"
ERR_EMPTY_ADDRESS = "ERR_EMPTY_ADDRESS"
ERR_EMPTY_STREET = "ERR_EMPTY_STREET"


@dataclass
class ConfidenceResult:
    """Structured confidence evaluation and routing result."""
    composite_score: float
    routing_tier: str
    s_parse: float
    s_ref_match: float
    s_geo: float
    s_cross_field: float
    failure_reason_codes: List[str]
    # Only set when a fitted calibrator is passed to compute_confidence_score(); never changes composite_score.
    calibrated_score: Optional[float] = None

    def as_dict(self) -> Dict[str, Any]:
        d = {
            "composite_score": self.composite_score,
            "routing_tier": self.routing_tier,
            "s_parse": self.s_parse,
            "s_ref_match": self.s_ref_match,
            "s_geo": self.s_geo,
            "s_cross_field": self.s_cross_field,
            "failure_reason_codes": list(self.failure_reason_codes),
        }
        if self.calibrated_score is not None:
            d["calibrated_score"] = self.calibrated_score
        return d


PROPER_THOROUGHFARES_NO_SUFFIX = {
    "BROADWAY",
    "BOWERY",
    "THE EMBARCADERO",
    "EMBARCADERO",
    "EL CAMINO REAL",
}

WORD_NUMBERS = {
    "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX",
    "SEVEN", "EIGHT", "NINE", "TEN", "ELEVEN", "TWELVE"
}

DUAL_ADDR_STREET_INDICATORS = [
    " ST", " STREET", " AVE", " AVENUE", " RD", " ROAD",
    " BLVD", " BOULEVARD", " CT", " COURT", " DR", " DRIVE",
    " LN", " LANE", " WAY", " PKWY", " PARKWAY", " CIR", " CIRCLE",
    " PL", " PLACE", " HWY", " HIGHWAY", " RTE", " ROUTE", " RT"
]


class ConfidenceScorer:
    """Calculates composite confidence scores and routing decisions for standardized addresses."""

    WEIGHT_PARSE = 0.35
    WEIGHT_REF = 0.35
    WEIGHT_GEO = 0.15
    WEIGHT_CROSS = 0.15

    TIER_AUTO_PASS_THRESHOLD = 0.95
    TIER_FUZZY_REVIEW_THRESHOLD = 0.80

    def score(
        self,
        std_address: Any,
        raw_input: Optional[Dict[str, Any]] = None,
        dpv_confirmed: Optional[str] = None,
        cascade_precision: Optional[str] = None,
    ) -> ConfidenceResult:
        """
        Calculates composite confidence score S in [0.0, 1.0] and determines routing tier.
        """
        raw = raw_input or {}
        raw_s1 = (raw.get("street1") or "").strip()
        raw_s2 = (raw.get("street2") or "").strip()
        raw_combined = f"{raw_s1} {raw_s2}".strip().upper()

        reason_codes: List[str] = []
        if raw.get("state_corrected_from"):
            reason_codes.append(WARN_STATE_CORRECTED_FROM_ZIP)

        # 0. Check for locality-only / city-level addresses
        is_locality = getattr(std_address, "is_locality_only", False) or getattr(std_address, "address_status", "") in ("locality_only", "city_level")
        if is_locality:
            reason_codes.append(NO_STREET_NUMBER)
            reason_codes.append(WARN_LOCALITY_ONLY)

            if getattr(std_address, "is_registered_agent_hub", False):
                reason_codes.append(WARN_CRA_HUB_DETECTED)
            if getattr(std_address, "is_private_residence", False):
                reason_codes.append(WARN_RESIDENTIAL_COMM)
            if getattr(std_address, "is_cmra", False):
                reason_codes.append(WARN_CMRA_DETECTED)
            if getattr(std_address, "is_vacant", False):
                reason_codes.append(WARN_VACANT_DELIVERY_POINT)

            s_parse = 0.85
            s_ref = 0.90 if (std_address.state or std_address.postal_code) else 0.70
            s_geo = 0.90 if (std_address.postal_code or std_address.state) else 0.70
            s_cross = 0.85
            composite = round(
                self.WEIGHT_PARSE * s_parse
                + self.WEIGHT_REF * s_ref
                + self.WEIGHT_GEO * s_geo
                + self.WEIGHT_CROSS * s_cross,
                4,
            )
            return ConfidenceResult(
                composite_score=composite,
                routing_tier=RoutingTier.FUZZY_REVIEW,
                s_parse=round(s_parse, 4),
                s_ref_match=round(s_ref, 4),
                s_geo=round(s_geo, 4),
                s_cross_field=round(s_cross, 4),
                failure_reason_codes=reason_codes,
            )

        # 0. Check for empty street or empty/parse_failed addresses
        raw_s1_val = raw.get("street1")
        is_empty_street = False
        if not (std_address.street1 or "").strip():
            is_empty_street = True
        elif raw_s1_val is not None and not raw_s1_val.strip():
            is_empty_street = True

        if is_empty_street or std_address.address_status == "parse_failed":
            if is_empty_street:
                reason_codes.append(ERR_EMPTY_STREET)
            if (
                not (raw_s1_val and raw_s1_val.strip())
                and not raw.get("city")
                and not raw.get("state")
                and not raw.get("postal_code")
            ):
                reason_codes.append(ERR_EMPTY_ADDRESS)
            else:
                reason_codes.append(ERR_PARSE_FAILED)
            return ConfidenceResult(
                composite_score=0.0,
                routing_tier=RoutingTier.MANUAL_STEWARDSHIP,
                s_parse=0.0,
                s_ref_match=0.0,
                s_geo=0.0,
                s_cross_field=0.0,
                failure_reason_codes=reason_codes,
            )

        # 1. S_parse: Parsing Quality (0.0 to 1.0)
        s_parse = 1.0
        has_dual_address = False
        is_landmark_campus = False
        if std_address.is_us:
            # Check for leading house number if street1 present
            st1 = std_address.street1.strip()
            is_po_box = st1.startswith("PO BOX")
            is_rural = st1.startswith("RR ") or st1.startswith("HC ")
            is_priv = std_address.is_private_residence or st1 == "PRIVATE RESIDENCE"
            is_intersection = " & " in st1 or " / " in st1

            if st1 and not (is_po_box or is_rural or is_priv or is_intersection):
                tokens = st1.split()
                first_tok = tokens[0] if tokens else ""
                if first_tok in ("URB", "URB.", "URBANIZACION") and len(tokens) > 1:
                    for tok in tokens[1:]:
                        tok_clean = re.sub(r"[^\w]", "", tok)
                        if any(ch.isdigit() for ch in tok_clean) or tok_clean in WORD_NUMBERS:
                            first_tok = tok_clean
                            break
                has_num = any(ch.isdigit() for ch in first_tok) or first_tok.upper() in WORD_NUMBERS
                if not has_num:
                    st1_tokens = set(re.findall(r"\b[A-Z0-9]+\b", st1.upper()))
                    raw_tokens = set(re.findall(r"\b[A-Z0-9]+\b", raw_combined.upper()))
                    if bool((st1_tokens | raw_tokens) & LANDMARK_CAMPUS_KEYWORDS):
                        is_landmark_campus = True
                        s_parse -= 0.15
                        reason_codes.append(WARN_LANDMARK_CAMPUS_PREMISE)
                    else:
                        s_parse -= 0.35
                        reason_codes.append(ERR_MISSING_HOUSE_NUM)

            # Check for dual address lines in raw input
            if ("PO BOX" in raw_combined or "P.O. BOX" in raw_combined or "P O BOX" in raw_combined) and (
                any(s in raw_combined for s in DUAL_ADDR_STREET_INDICATORS)
            ):
                s_parse -= 0.10
                has_dual_address = True
                reason_codes.append(ERR_AMBIGUOUS_DUAL_ADDR)

            # Check for typo healing (e.g. state abbreviation healed, suffix fuzzy matched)
            if raw_s1 and std_address.street1 and not has_dual_address:
                norm_raw_s1 = re.sub(r"[^\w\s]", "", raw_s1.upper()).strip()
                norm_std_s1 = re.sub(r"[^\w\s]", "", std_address.street1.upper()).strip()
                if norm_raw_s1 and norm_std_s1 and norm_raw_s1 != norm_std_s1:
                    raw_words = norm_raw_s1.split()
                    std_words = norm_std_s1.split()
                    if len(raw_words) == len(std_words) and any(
                        rw != sw and rw not in STREET_SUFFIXES and rw not in DIRECTIONALS
                        for rw, sw in zip(raw_words, std_words)
                    ):
                        s_parse -= 0.05
                        reason_codes.append(WARN_TYPO_HEALED)
        else:
            # International parse
            pass

        s_parse = max(0.0, min(1.0, s_parse))

        # 2. S_ref_match: Reference / Dictionary Concordance (0.0 to 1.0)
        s_ref = 1.0
        if std_address.is_us:
            # Check state validity
            if std_address.state not in US_STATES.values() and std_address.state not in US_STATES:
                s_ref -= 0.40
            # Check postal code format
            zip_clean = re.sub(r"[^\d]", "", std_address.postal_code or "")
            if len(zip_clean) != 5 and len(zip_clean) != 9:
                is_valid_state = std_address.state in US_STATES.values() or std_address.state in US_STATES
                has_city = bool(std_address.city and len(std_address.city.strip()) >= 2)
                if is_valid_state and has_city:
                    s_ref -= 0.15
                else:
                    s_ref -= 0.30

            # Check suffix recognition
            st1 = std_address.street1.strip().upper() if std_address.street1 else ""
            st1_tokens = st1.split() if st1 else []
            if len(st1_tokens) >= 2 and not (
                st1.startswith("PO BOX")
                or st1.startswith("RR ")
                or st1.startswith("HC ")
                or std_address.is_private_residence
            ):
                last_tok = st1_tokens[-1]
                prev_tok = st1_tokens[-2] if len(st1_tokens) >= 3 else ""

                # Suffix checks:
                # 1. Last token or second to last token (before directional) is standard suffix
                # 2. Well-known thoroughfares without suffixes (Broadway, Bowery, Embarcadero)
                # 3. Thoroughfare type appears as prefix or intermediate token (Highway 101, Route 66, Avenue of the Americas)
                is_ordinal_thoroughfare = bool(
                    re.match(r"^\d+(?:ST|ND|RD|TH)$", last_tok)
                    or (last_tok in DIRECTIONALS.values() and re.match(r"^\d+(?:ST|ND|RD|TH)$", prev_tok))
                )
                has_valid_suf = (
                    is_ordinal_thoroughfare
                    or last_tok in STREET_SUFFIXES.values()
                    or last_tok in STREET_SUFFIXES
                    or (last_tok in DIRECTIONALS.values() and (prev_tok in STREET_SUFFIXES.values() or prev_tok in STREET_SUFFIXES))
                    or any(name in st1 for name in PROPER_THOROUGHFARES_NO_SUFFIX)
                    or any(t in STREET_SUFFIXES.values() or t in STREET_SUFFIXES for t in st1_tokens[1:])
                    or any(t in ["WAY", "WALK", "MALL", "LOOP", "PASS", "ROW", "RUN"] for t in st1_tokens)
                    or any(t in LANDMARK_CAMPUS_KEYWORDS for t in st1_tokens)
                    or any(t in {"CALLE", "AVENIDA", "CARR", "PASEO", "CAMINO", "CALZADA", "CARRETERA", "RUTA"} for t in st1_tokens)
                )
                if not has_valid_suf:
                    s_ref -= 0.20
                    reason_codes.append(ERR_UNRESOLVED_SUFFIX)

            # DPV check
            if dpv_confirmed == "N":
                s_ref -= 0.25
                reason_codes.append(ERR_DPV_UNCONFIRMED)
        else:
            if not std_address.country or len(std_address.country) != 3:
                s_ref -= 0.30

        s_ref = max(0.0, min(1.0, s_ref))

        # 3. S_geo: Geographic Concordance (0.0 to 1.0)
        s_geo = 1.0
        if std_address.is_us:
            zip5 = std_address.postal_code[:5] if std_address.postal_code and len(std_address.postal_code) >= 5 else ""
            z3 = zip5[:3] if len(zip5) >= 3 else ""

            if cascade_precision:
                if cascade_precision == "CONFIRMED_ROOFTOP":
                    s_geo = 1.0
                elif cascade_precision == "FALLBACK_TIGER":
                    s_geo = 0.95
                elif cascade_precision == "FALLBACK_ZIP3":
                    s_geo = 0.92
                elif cascade_precision == "FALLBACK_STATE":
                    s_geo = 0.85
                else:
                    s_geo = 0.50
            elif dpv_confirmed == "Y":
                s_geo = 1.0
            elif z3 in METRO_ZIP3_CENTROIDS:
                s_geo = 0.92
            elif z3 in ZIP3_TO_STATE or std_address.state in STATE_CENTROIDS:
                s_geo = 0.85
            else:
                s_geo = 0.50
        else:
            s_geo = 0.90 if std_address.city and std_address.country else 0.60

        s_geo = max(0.0, min(1.0, s_geo))

        # 4. S_cross_field: Cross-Field Consistency (0.0 to 1.0)
        s_cross = 1.0
        if std_address.is_us:
            zip5 = std_address.postal_code[:5] if std_address.postal_code and len(std_address.postal_code) >= 5 else ""
            z3 = zip5[:3] if len(zip5) >= 3 else ""

            if z3 and z3 in ZIP3_TO_STATE:
                expected_st = ZIP3_TO_STATE[z3]
                raw_st = (raw.get("state") or "").strip().upper()
                if raw_st.startswith("USA-"):
                    raw_st = raw_st[4:].strip()
                elif raw_st.startswith("US-"):
                    raw_st = raw_st[3:].strip()

                std_st = (std_address.state or "").strip().upper()
                if std_st.startswith("USA-"):
                    std_st = std_st[4:].strip()
                elif std_st.startswith("US-"):
                    std_st = std_st[3:].strip()

                is_raw_mismatch = bool(raw_st and raw_st != expected_st and US_STATES.get(raw_st, raw_st) != expected_st)
                is_std_mismatch = bool(std_st and std_st != expected_st and US_STATES.get(std_st, std_st) != expected_st)

                if is_raw_mismatch or is_std_mismatch:
                    reason_codes.append(ERR_ZIP_STATE_MISMATCH)
                    s_cross = 0.20
                elif std_st == expected_st:
                    s_cross = 1.0
                else:
                    s_cross = 0.50
            elif not z3 and not std_address.state:
                s_cross = 0.20
            else:
                s_cross = 0.80
        else:
            s_cross = 1.0

        s_cross = max(0.0, min(1.0, s_cross))

        # Risk hub & residence warnings
        if std_address.is_registered_agent_hub:
            reason_codes.append(WARN_CRA_HUB_DETECTED)
        if std_address.is_private_residence:
            reason_codes.append(WARN_RESIDENTIAL_COMM)
        # (no de-duplication needed: none of these codes can already be present on the non-locality path)
        if getattr(std_address, "is_cmra", False):
            reason_codes.append(WARN_CMRA_DETECTED)
        if getattr(std_address, "is_vacant", False):
            reason_codes.append(WARN_VACANT_DELIVERY_POINT)
        if "N1" in getattr(std_address, "dpv_footnotes", []):
            reason_codes.append(WARN_MISSING_SECONDARY_UNIT)

        # Disguised PMB check
        raw_has_pmb = "PMB" in raw_combined or "PRIVATE MAILBOX" in raw_combined
        std_has_ste = any(t in (std_address.street2 or "").upper() for t in ["STE", "SUITE", "APT", "UNIT", "FL"])
        raw_has_ste = any(t in raw_combined for t in ["SUITE", "STE", "#"])
        std_has_pmb = "PMB" in (std_address.street2 or "").upper()

        if (raw_has_pmb and std_has_ste) or (raw_has_ste and std_has_pmb):
            reason_codes.append(WARN_PMB_DISGUISED)

        # Composite score calculation
        composite = (
            self.WEIGHT_PARSE * s_parse
            + self.WEIGHT_REF * s_ref
            + self.WEIGHT_GEO * s_geo
            + self.WEIGHT_CROSS * s_cross
        )
        composite = round(max(0.0, min(1.0, composite)), 4)

        # Routing tier decision:
        # Critical failure reasons (e.g. ERR_MISSING_HOUSE_NUM, parse_failed) mandate Tier 3
        if (
            ERR_MISSING_HOUSE_NUM in reason_codes
            or std_address.address_status == "parse_failed"
        ):
            routing_tier = RoutingTier.MANUAL_STEWARDSHIP
        elif is_landmark_campus:
            if composite >= self.TIER_FUZZY_REVIEW_THRESHOLD:
                routing_tier = RoutingTier.FUZZY_REVIEW
            else:
                routing_tier = RoutingTier.MANUAL_STEWARDSHIP
        elif composite >= self.TIER_AUTO_PASS_THRESHOLD and not any(
            c.startswith("ERR_") for c in reason_codes
        ):
            routing_tier = RoutingTier.AUTO_PASS
        elif composite >= self.TIER_FUZZY_REVIEW_THRESHOLD:
            routing_tier = RoutingTier.FUZZY_REVIEW
        else:
            routing_tier = RoutingTier.MANUAL_STEWARDSHIP

        return ConfidenceResult(
            composite_score=composite,
            routing_tier=routing_tier,
            s_parse=round(s_parse, 4),
            s_ref_match=round(s_ref, 4),
            s_geo=round(s_geo, 4),
            s_cross_field=round(s_cross, 4),
            failure_reason_codes=reason_codes,
        )


_DEFAULT_SCORER = ConfidenceScorer()


def compute_confidence_score(
    std_address: Any,
    raw_input: Optional[Dict[str, Any]] = None,
    dpv_confirmed: Optional[str] = None,
    cascade_precision: Optional[str] = None,
    calibrator: Optional[Any] = None,
) -> ConfidenceResult:
    """Convenience functional interface to compute confidence score and routing tier.

    ``calibrator`` (optional, default off) is a fitted ``address_standardizer.calibration.Calibrator``; when given,
    ``result.calibrated_score`` holds the calibrated value. ``composite_score`` and routing are never altered.
    """
    result = _DEFAULT_SCORER.score(
        std_address=std_address,
        raw_input=raw_input,
        dpv_confirmed=dpv_confirmed,
        cascade_precision=cascade_precision,
    )
    if calibrator is not None:
        result.calibrated_score = calibrator.calibrate(result.composite_score)
    return result
