"""
Multinational Golden Evaluation Dataset Generator for Address Standardizer.
===========================================================================
Compiles and curates the exact 1,000-record multinational golden dataset
conforming to UPU S42, ISO 19160-4, and the Master Architectural Blueprint
(GLOBAL_SPATIAL_ENTERPRISE_BLUEPRINT.md Section 6.1 & 6.2).

Categories (1,000 ground-truth records total):
  - INTL-01 (200 records): UK & Commonwealth (GBR, JEY, GGY, IMN)
  - INTL-02 (150 records): Canadian Bilingual & Rural Delivery (CAN)
  - INTL-03 (200 records): European Union Inverted & Compound (DEU, FRA, NLD, ESP, ITA, POL, SWE, DNK)
  - INTL-04 (150 records): Latin America Compound & Urbanization (MEX, COL, ARG, BRA, CHL, PER, PRI)
  - INTL-05 (150 records): Global Corporate Formation & Secrecy Hubs (CYM, VGB, BMU, PAN, CHE, LUX, GBR, USA)
  - INTL-06 (150 records): Multilingual Diacritic, Non-Latin & Messy Inputs (Global)

Architectural Invariant:
This generator is decoupled from runtime standardizer implementation to prevent
circular validation. All expected outputs derive from authoritative domain templates
and canonical ground-truth specifications, plus the reviewed corrections in
data/multinational_expected_overrides.json (applied last, so the output is reproducible).
"""

import json
import os
import random
import sys
from typing import Any, Dict, List

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from benchmarks.canonical_multinational_data import CANONICAL_INTL_02_TO_06


def make_record(
    test_id: str,
    category: str,
    jurisdiction: str,
    raw_input: Dict[str, Any],
    expected_output: Dict[str, Any],
) -> Dict[str, Any]:
    """Assembles golden evaluation record and validates schema integrity."""
    required_keys = (
        "street1",
        "street2",
        "city",
        "state",
        "postal_code",
        "country",
        "normalized_address_key",
        "building_key",
        "phonetic_key",
        "address_status",
        "is_us",
        "is_registered_agent_hub",
        "dependent_locality",
        "building_name",
        "is_private_residence",
    )
    for k in required_keys:
        if k not in expected_output:
            raise ValueError(f"Missing required key {k} in expected_output for {test_id}")

    # Validate key ASCII purity
    for k in ("normalized_address_key", "building_key", "phonetic_key"):
        val = expected_output.get(k)
        if val and not val.isascii():
            raise ValueError(f"Non-ASCII {k} in {test_id}: {val}")

    return {
        "test_id": test_id,
        "category": category,
        "jurisdiction": jurisdiction,
        "raw_input": raw_input,
        "expected_output": expected_output,
    }


def generate_intl_01_uk(rng: random.Random) -> List[Dict[str, Any]]:
    """INTL-01: UK & Commonwealth Postcodes & Premise House Names (200 records).

    Constructed independently according to BS 7666 / Royal Mail PAF canonical domain rules.
    """
    records: List[Dict[str, Any]] = []
    category = "uk_commonwealth_postcodes"

    uk_cities_postcodes = [
        ("London", "SW1A 1AA", "GBR"),
        ("London", "EC1A 1BB", "GBR"),
        ("London", "W1A 0AX", "GBR"),
        ("London", "NW1 4NP", "GBR"),
        ("London", "SE1 7PB", "GBR"),
        ("London", "E1 6AN", "GBR"),
        ("London", "WC2H 9JQ", "GBR"),
        ("Leeds", "LS6 2AA", "GBR"),
        ("Leeds", "LS1 2TW", "GBR"),
        ("Leeds", "LS2 9JT", "GBR"),
        ("Manchester", "M1 1AA", "GBR"),
        ("Manchester", "M4 4BF", "GBR"),
        ("Manchester", "M20 2RN", "GBR"),
        ("Birmingham", "B33 8TH", "GBR"),
        ("Birmingham", "B1 1BB", "GBR"),
        ("Birmingham", "B15 2TT", "GBR"),
        ("Edinburgh", "EH1 1YZ", "GBR"),
        ("Edinburgh", "EH2 2ER", "GBR"),
        ("Glasgow", "G1 1XQ", "GBR"),
        ("Glasgow", "G2 8DL", "GBR"),
        ("Bristol", "BS1 4ST", "GBR"),
        ("Bristol", "BS8 1TH", "GBR"),
        ("Belfast", "BT1 5GS", "GBR"),
        ("Belfast", "BT2 8DN", "GBR"),
        ("Cardiff", "CF10 1AA", "GBR"),
        ("Cardiff", "CF11 9BZ", "GBR"),
        ("Newcastle", "NE1 7RU", "GBR"),
        ("Liverpool", "L1 8JQ", "GBR"),
        ("Sheffield", "S1 2GE", "GBR"),
        ("Oxford", "OX1 1DP", "GBR"),
        ("Cambridge", "CB2 1TN", "GBR"),
        ("St Helier", "JE2 3XX", "JEY"),
        ("St Helier", "JE1 1AA", "JEY"),
        ("St Peter Port", "GY1 2YY", "GGY"),
        ("St Peter Port", "GY1 1AA", "GGY"),
        ("Douglas", "IM1 1ZZ", "IMN"),
        ("Douglas", "IM2 4RW", "IMN"),
    ]

    thoroughfares = [
        "High Street", "Park Road", "Victoria Street", "Station Road", "Church Street",
        "King Street", "Queen Street", "London Road", "Green Lane", "Manor Road",
        "Bank Street", "Mill Lane", "North Street", "Market Place", "George Street",
        "Bridge Street", "Broad Street", "Castle Street", "New Road", "Commercial Road",
    ]

    premises = [
        "The Mansions", "Victoria House", "St Andrews Court", "Windsor House",
        "Kings Court", "Albany House", "Clarendon House", "Queens Court",
        "Alexandra House", "Richmond House", "Wellington Court", "Manor House",
    ]

    sec_units = ["Flat 1", "Flat 2", "Flat 3", "Apt 4", "Suite 5", ""]

    st_suffix_norm = {
        "High Street": "HIGH ST", "Park Road": "PARK RD", "Victoria Street": "VICTORIA ST",
        "Station Road": "STATION RD", "Church Street": "CHURCH ST", "King Street": "KING ST",
        "Queen Street": "QUEEN ST", "London Road": "LONDON RD", "Green Lane": "GREEN LN",
        "Manor Road": "MANOR RD", "Bank Street": "BANK ST", "Mill Lane": "MILL LN",
        "North Street": "N ST", "Market Place": "MARKET PL", "George Street": "GEORGE ST",
        "Bridge Street": "BRIDGE ST", "Broad Street": "BROAD ST", "Castle Street": "CASTLE ST",
        "New Road": "NEW RD", "Commercial Road": "COMMERCIAL RD",
    }

    st_soundex = {
        "High Street": "H200", "Park Road": "P620", "Victoria Street": "V236",
        "Station Road": "S300", "Church Street": "C620", "King Street": "K520",
        "Queen Street": "Q500", "London Road": "L535", "Green Lane": "G650",
        "Manor Road": "M600", "Bank Street": "B520", "Mill Lane": "M400",
        "North Street": "N000", "Market Place": "M623", "George Street": "G620",
        "Bridge Street": "B620", "Broad Street": "B630", "Castle Street": "C234",
        "New Road": "N000", "Commercial Road": "C562",
    }

    sec_norm = {
        "Flat 1": "APT 1", "Flat 2": "APT 2", "Flat 3": "APT 3",
        "Apt 4": "APT 4", "Suite 5": "STE 5", "": "",
    }

    count = 0
    while count < 200:
        city, pc, jur = uk_cities_postcodes[count % len(uk_cities_postcodes)]
        st_name = thoroughfares[(count * 3) % len(thoroughfares)]
        st_num = str(10 + (count * 7) % 180)
        sec = sec_units[count % len(sec_units)]
        has_premise = (count % 3 == 0)
        prem = premises[(count * 2) % len(premises)] if has_premise else None

        country_name = "United Kingdom" if jur == "GBR" else (
            "Jersey" if jur == "JEY" else ("Guernsey" if jur == "GGY" else "Isle of Man")
        )

        if has_premise:
            st1_str = f"{prem}, {st_num} {st_name}"
        else:
            st1_str = f"{st_num} {st_name}"

        count += 1
        test_id = f"INTL-01-{count:03d}"

        if test_id == "INTL-01-042":
            # Authoritative Blueprint Section 6.2 fixture INTL-01-042
            raw = {
                "street1": "Flat 2, The Mansions, 15 High Street",
                "street2": "Headingley",
                "city": "Leeds",
                "state": "",
                "postal_code": "LS6 2AA",
                "country": "United Kingdom",
            }
            expected = {
                "street1": "15 HIGH ST",
                "street2": "APT 2 THE MANSIONS",
                "city": "LEEDS",
                "state": "",
                "postal_code": "LS6 2AA",
                "country": "GBR",
                "normalized_address_key": "15 HIGH ST|APT 2 THE MANSIONS|LEEDS||LS6 2AA|GBR",
                "building_key": "15 HIGH ST||LEEDS||LS6 2AA|GBR",
                "phonetic_key": "15|H200|LS6 2AA",
                "address_status": "standardized",
                "is_us": False,
                "is_registered_agent_hub": False,
                "dependent_locality": "HEADINGLEY",
                "building_name": "THE MANSIONS",
                "is_private_residence": False,
            }
        else:
            if count % 2 == 1:
                raw = {
                    "street1": st1_str,
                    "street2": sec if sec else None,
                    "city": city,
                    "state": None,
                    "postal_code": pc,
                    "country": country_name,
                }
                eff_jur = jur
            else:
                sec_part = f"{sec}, " if sec else ""
                line = f"{sec_part}{st1_str}, {city}, {pc}, {country_name}"
                raw = {
                    "street1": line,
                    "street2": None,
                    "city": None,
                    "state": None,
                    "postal_code": None,
                    "country": None,
                }
                eff_jur = jur if jur not in ("JEY", "GGY", "IMN") else "GBR"

            street1_exp = f"{st_num} {st_suffix_norm[st_name]}"
            prem_norm = prem.upper() if prem else None
            unit_norm = sec_norm[sec]
            if unit_norm and prem_norm:
                street2_exp = f"{unit_norm} {prem_norm}"
            elif unit_norm:
                street2_exp = unit_norm
            elif prem_norm:
                street2_exp = prem_norm
            else:
                street2_exp = ""

            city_exp = city.upper()
            postal_exp = pc.upper()
            country_exp = eff_jur
            norm_key = f"{street1_exp}|{street2_exp}|{city_exp}||{postal_exp}|{country_exp}"
            bld_key = f"{street1_exp}||{city_exp}||{postal_exp}|{country_exp}"
            phon_key = f"{st_num}|{st_soundex[st_name]}|{postal_exp}"
            # "Clarendon House" in the UK is not the Bermuda offshore hub: a premise name alone is not a hub signal.
            is_hub = False

            expected = {
                "street1": street1_exp,
                "street2": street2_exp,
                "city": city_exp,
                "state": "",
                "postal_code": postal_exp,
                "country": country_exp,
                "normalized_address_key": norm_key,
                "building_key": bld_key,
                "phonetic_key": phon_key,
                "address_status": "standardized",
                "is_us": False,
                "is_registered_agent_hub": is_hub,
                "dependent_locality": None,
                "building_name": prem_norm,
                "is_private_residence": False,
            }

        records.append(make_record(test_id, category, jur, raw, expected))

    return records


def generate_intl_02_canada(rng: random.Random) -> List[Dict[str, Any]]:
    """INTL-02: Canadian Bilingual & Rural Delivery Modes (150 records)."""
    return [
        make_record(
            r["test_id"],
            r["category"],
            r["jurisdiction"],
            r["raw_input"],
            r["expected_output"],
        )
        for r in CANONICAL_INTL_02_TO_06
        if r["test_id"].startswith("INTL-02-")
    ]


def generate_intl_03_eu(rng: random.Random) -> List[Dict[str, Any]]:
    """INTL-03: European Union Inverted & Compound Streets (200 records)."""
    return [
        make_record(
            r["test_id"],
            r["category"],
            r["jurisdiction"],
            r["raw_input"],
            r["expected_output"],
        )
        for r in CANONICAL_INTL_02_TO_06
        if r["test_id"].startswith("INTL-03-")
    ]


def generate_intl_04_latam(rng: random.Random) -> List[Dict[str, Any]]:
    """INTL-04: Latin America Compound & Urbanization (150 records)."""
    return [
        make_record(
            r["test_id"],
            r["category"],
            r["jurisdiction"],
            r["raw_input"],
            r["expected_output"],
        )
        for r in CANONICAL_INTL_02_TO_06
        if r["test_id"].startswith("INTL-04-")
    ]


def generate_intl_05_formation_hubs(rng: random.Random) -> List[Dict[str, Any]]:
    """INTL-05: Global Corporate Formation & Secrecy Hubs (150 records)."""
    return [
        make_record(
            r["test_id"],
            r["category"],
            r["jurisdiction"],
            r["raw_input"],
            r["expected_output"],
        )
        for r in CANONICAL_INTL_02_TO_06
        if r["test_id"].startswith("INTL-05-")
    ]


def generate_intl_06_diacritics_messy(rng: random.Random) -> List[Dict[str, Any]]:
    """INTL-06: Multilingual Diacritic, Non-Latin & Messy Inputs (150 records)."""
    return [
        make_record(
            r["test_id"],
            r["category"],
            r["jurisdiction"],
            r["raw_input"],
            r["expected_output"],
        )
        for r in CANONICAL_INTL_02_TO_06
        if r["test_id"].startswith("INTL-06-")
    ]


def generate_multinational_golden_dataset(seed: int = 42) -> List[Dict[str, Any]]:
    """Generates complete 1,000-record Multinational Golden Evaluation Dataset."""
    rng = random.Random(seed)
    records: List[Dict[str, Any]] = []

    records.extend(generate_intl_01_uk(rng))
    records.extend(generate_intl_02_canada(rng))
    records.extend(generate_intl_03_eu(rng))
    records.extend(generate_intl_04_latam(rng))
    records.extend(generate_intl_05_formation_hubs(rng))
    records.extend(generate_intl_06_diacritics_messy(rng))

    if len(records) != 1000:
        raise ValueError(f"Expected exactly 1,000 records, generated {len(records)}")

    return apply_expected_overrides(records)


OVERRIDES_PATH = os.path.join(os.path.dirname(__file__), "data", "multinational_expected_overrides.json")


def apply_expected_overrides(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply reviewed corrections (data/multinational_expected_overrides.json) on top of the template expectations.

    The overlay records every place where a template expectation encoded a bug and was corrected after review, so
    the committed dataset is exactly reproducible: ``generate -> compare`` must be a no-op.
    """
    with open(OVERRIDES_PATH, encoding="utf-8") as f:
        overrides = json.load(f)["overrides"]
    known = {r["test_id"] for r in records}
    unknown = sorted(set(overrides) - known)
    if unknown:
        raise ValueError(f"Overrides reference unknown test ids: {unknown[:5]}")
    for rec in records:
        patch = overrides.get(rec["test_id"])
        if patch:
            unexpected = set(patch) - set(rec["expected_output"])
            if unexpected:
                raise ValueError(f"{rec['test_id']}: override sets unknown fields {sorted(unexpected)}")
            rec["expected_output"].update(patch)
    return records


def main() -> None:
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "golden_dataset_multinational.json")

    print("Generating 1,000-record Multinational Golden Dataset (independent domain templates)...")
    dataset = generate_multinational_golden_dataset()

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated and wrote {len(dataset)} records to {output_path}")

    # Integrity verification
    flat_corruptions = [r["test_id"] for r in dataset if "FL AT" in json.dumps(r["expected_output"])]
    if flat_corruptions:
        print(f"WARNING: Found {len(flat_corruptions)} records with 'FL AT' corruption: {flat_corruptions[:5]}")
    else:
        print("Integrity check passed: 0 records with 'FL AT' secondary unit corruption.")

    intl_042 = next((r for r in dataset if r["test_id"] == "INTL-01-042"), None)
    if intl_042:
        print(f"Blueprint fixture INTL-01-042 verified: street1={intl_042['expected_output']['street1']}, street2={intl_042['expected_output']['street2']}, dep_loc={intl_042['expected_output']['dependent_locality']}")


if __name__ == "__main__":
    main()
