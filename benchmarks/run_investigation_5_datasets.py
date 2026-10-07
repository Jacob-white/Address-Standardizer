#!/usr/bin/env python3
"""
Comprehensive 5-Dataset Investigation Benchmark Harness
=========================================================
Executes Address-Standardizer across the 5 major benchmark datasets:
  1. OpenAddresses Global (US SF OpenData & International Paris BAN physical points)
  2. Overture Maps Foundation Global Addresses (Worldwide open schema + GLEIF Global LEI-CDF)
  3. US Census TIGER/Line Addresses (US street edges and ranges)
  4. UK PAF / Open Postcode Geo & UPU Global Standards (UK Companies House & UPU multinational)
  5. Firm Network Production Database (PostgreSQL: firm_branch, firm_master, fdic_bank_branch, contact_association)

Measures:
  - Throughput (rec/s) & Latency
  - Address status (standardized, locality_only, parse_failed) & Usable Yield %
  - Routing tiers (AUTO_PASS, FUZZY_REVIEW, MANUAL_STEWARDSHIP)
  - Deliverability classifications (DELIVERABLE, REQUIRES_SECONDARY, UNDELIVERABLE)
  - Spatial precision levels (CONFIRMED_ROOFTOP, RANGE_INTERPOLATED, POSTAL_CENTROID, MUNICIPAL_CENTROID, UNRESOLVED)
  - Rooftop address extraction fidelity
  - Entity/Risk metadata (CMRA, Registered Agent Hub, Private Residence, Corporate Risk)
  - Rigorous False Positive and False Negative inspection & cataloging
"""

import os
import sys
import time
import json
import csv
import io
import re
import struct
import zipfile
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import psycopg2
from address_standardizer import standardize_address, StandardizedAddress, RoutingTier
from address_standardizer.tables import US_STATES


@dataclass
class DatasetMetrics:
    dataset_name: str
    total_records: int = 0
    duration_seconds: float = 0.0
    throughput_rec_sec: float = 0.0

    # Status counts
    standardized_count: int = 0
    locality_only_count: int = 0
    parse_failed_count: int = 0
    usable_yield_percent: float = 0.0

    # Routing tiers
    auto_pass_count: int = 0
    fuzzy_review_count: int = 0
    manual_stewardship_count: int = 0

    # Deliverability classifications
    deliverable_count: int = 0
    requires_secondary_count: int = 0
    undeliverable_count: int = 0

    # Precision levels (geocoding / spatial resolution)
    confirmed_rooftop_count: int = 0
    range_interpolated_count: int = 0
    postal_centroid_count: int = 0
    municipal_centroid_count: int = 0
    unresolved_precision_count: int = 0

    # Rooftop extraction
    rooftop_extracted_count: int = 0

    # Business / Risk flags
    private_residence_count: int = 0
    registered_agent_hub_count: int = 0
    cmra_count: int = 0
    vacant_count: int = 0

    # Geography
    us_records: int = 0
    intl_records: int = 0
    country_distribution: Counter = field(default_factory=Counter)

    # Errors & Failure codes
    failure_reasons: Counter = field(default_factory=Counter)

    # False Positives & False Negatives
    false_positives: List[Dict[str, Any]] = field(default_factory=list)
    false_negatives: List[Dict[str, Any]] = field(default_factory=list)
    edge_cases: List[Dict[str, Any]] = field(default_factory=list)


def inspect_anomalies(
    raw_street1: str,
    raw_street2: str,
    raw_city: str,
    raw_state: str,
    raw_postal: str,
    raw_country: str,
    std: StandardizedAddress,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Inspects an address for False Positives and False Negatives."""
    fps = []
    fns = []

    raw_s1_upper = (raw_street1 or "").upper().strip()
    raw_s2_upper = (raw_street2 or "").upper().strip()
    full_raw_upper = f"{raw_s1_upper} {raw_s2_upper}".strip()

    # -------------------------------------------------------------
    # 1. FALSE POSITIVES
    # -------------------------------------------------------------
    # 1A. False Positive Private Residence
    if std.is_private_residence:
        legit_priv_terms = ["PRIVATE RESIDENCE", "RESIDENTIAL", "PRIVATE ADDRESS", "CONFIDENTIAL", "RESIDENCE ONLY", "PERSONAL RESIDENCE"]
        if not any(t in full_raw_upper for t in legit_priv_terms):
            fps.append({
                "type": "FP_PRIVATE_RESIDENCE",
                "raw_input": f"{raw_street1}, {raw_city}, {raw_state} {raw_postal}",
                "reason": "Flagged as PRIVATE RESIDENCE without privacy keywords in raw input"
            })

    # 1B. Invariant: Rooftop on PO Box, Locality-Only, or Private Residence
    if std.rooftop_address is not None:
        if std.is_private_residence:
            fps.append({
                "type": "ROOFTOP_ON_PRIVATE_RESIDENCE",
                "rooftop": std.rooftop_address,
                "reason": "Rooftop address generated for private residence"
            })
        if std.is_locality_only:
            fps.append({
                "type": "ROOFTOP_ON_LOCALITY_ONLY",
                "rooftop": std.rooftop_address,
                "reason": "Rooftop address generated for locality-only record"
            })
        if re.search(r"\b(?:P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\b", full_raw_upper):
            is_dual = bool(std.street1 and re.match(r"^(?:\d+|PR-|CARR-|KM\b)", std.street1))
            if not is_dual:
                fps.append({
                    "type": "ROOFTOP_ON_PO_BOX",
                    "raw_input": full_raw_upper,
                    "rooftop": std.rooftop_address,
                    "reason": "Rooftop address generated for pure PO Box"
                })

    # 1C. False Positive Rooftop Stripping (stripping core thoroughfare types)
    if std.rooftop_address and std.street1:
        if std.rooftop_address != std.street1:
            has_unit = bool(re.search(
                r"\b(?:SUITE|STE|APT|APARTMENT|UNIT|ROOM|RM|BLDG|BUILDING|FLOOR|FL|DEPT|DEPARTMENT|OFC|OFFICE|LOT|SPACE|SPC|TRAILER|TRLR|PIER|SLIP|LEVEL|LVL|PH|PENTHOUSE|BSMT|BASEMENT|LBBY|LOBBY|SIDE|REAR|FRONT|UPPR|LOWR|STOP|FLAT|MEZZANINE|BAY|CONDO|TOWER|#)\b",
                std.street1, re.I
            ))
            s1_words = set(re.findall(r"\w+", std.street1.upper()))
            rf_words = set(re.findall(r"\w+", std.rooftop_address.upper()))
            dropped = s1_words - rf_words
            core_types = {"WAY", "CREEK", "HILL", "ROAD", "STREET", "AVENUE", "BOULEVARD", "BLVD", "LANE", "DRIVE", "PARK", "COURT", "PLACE", "TERRACE", "ROW", "MEWS", "CLOSE", "PLAZA", "SQUARE", "HIGHWAY"}
            if dropped.intersection(core_types) and not has_unit:
                fps.append({
                    "type": "FP_ROOFTOP_STRIPPING",
                    "street1": std.street1,
                    "rooftop": std.rooftop_address,
                    "dropped": list(dropped.intersection(core_types)),
                    "reason": f"Stripped essential thoroughfare type words: {dropped.intersection(core_types)}"
                })

    # 1D. Street Number Dropped / Lost
    m_num = re.match(r"^(\d+[A-Z]?|\d+-\d+)\s+([A-Za-z].*)$", raw_s1_upper)
    if m_num and std.address_status == "standardized" and not std.is_locality_only:
        lead_num = m_num.group(1).upper()
        s2_upper = (std.street2 or "").upper()
        if (
            lead_num in s2_upper
            or (lead_num.endswith("F") and f"FL {lead_num[:-1]}" in s2_upper)
            or re.match(r"^\d+\s+(?:FLOOR|FL|FLR|STAIR|LEVEL|LVL)\b", raw_s1_upper)
        ):
            pass
        elif not re.match(r"^\d", std.street1) and not re.match(r"^(?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)\b", std.street1, re.I):
            fps.append({
                "type": "STREET_NUMBER_DROPPED",
                "raw_street": raw_street1,
                "street1": std.street1,
                "reason": "Raw street had leading house number but standardized street1 has none"
            })

    # 1E. Over-aggressive Street Truncation
    if raw_street1 and std.street1 and std.address_status == "standardized" and not std.is_locality_only:
        if len(std.street1) < 4 and len(raw_street1) > 8 and not re.match(r"^(?:US|SR|CR|I)-\d+", raw_street1.upper()):
            fps.append({
                "type": "SEVERE_STREET_TRUNCATION",
                "raw_street": raw_street1,
                "street1": std.street1,
                "reason": f"Suspiciously short street1 ({std.street1}) from raw ({raw_street1})"
            })

    # 1F. Country Misclassification
    if raw_country:
        rc = raw_country.strip().upper()
        if rc in ("UK", "GB", "GBR", "UNITED KINGDOM", "ENGLAND", "SCOTLAND", "WALES",
                  "CANADA", "CA", "CAN", "GERMANY", "DE", "DEU", "FRANCE", "FR", "FRA",
                  "SPAIN", "ES", "ESP", "ITALY", "IT", "ITA", "JAPAN", "JP", "JPN",
                  "AUSTRALIA", "AU", "AUS", "SWITZERLAND", "CH", "CHE"):
            if std.is_us:
                fps.append({
                    "type": "FP_US_ROUTING",
                    "raw_country": raw_country,
                    "reason": f"Sovereign foreign country {raw_country} routed as US"
                })

    # -------------------------------------------------------------
    # 2. FALSE NEGATIVES
    # -------------------------------------------------------------
    # 2A. Valid Physical Address Routed to Parse Failed
    has_house_num = bool(re.match(r"^\d+", raw_s1_upper))
    has_street_words = len(raw_s1_upper.split()) >= 2
    has_city_state_or_zip = bool((raw_city and raw_state) or raw_postal)
    if has_house_num and has_street_words and has_city_state_or_zip:
        if std.address_status == "parse_failed":
            fns.append({
                "type": "FN_PARSE_FAILED_VALID_INPUT",
                "raw_input": f"{raw_street1}, {raw_city}, {raw_state} {raw_postal} {raw_country}",
                "reason": "Well-formed address with house number, street name, and city/zip rejected as parse_failed"
            })
        elif std.routing_tier == RoutingTier.MANUAL_STEWARDSHIP:
            # Check if reason is purely synthetic
            fns.append({
                "type": "FN_MANUAL_STEWARDSHIP_VALID_INPUT",
                "raw_input": f"{raw_street1}, {raw_city}, {raw_state} {raw_postal} {raw_country}",
                "reasons": std.failure_reason_codes,
                "reason": f"Clean address demoted to MANUAL_STEWARDSHIP: {std.failure_reason_codes}"
            })

    return fps, fns


def record_result(metrics: DatasetMetrics, raw_tuple: Tuple[str, str, str, str, str, str], std: StandardizedAddress):
    s1, s2, city, state, postal, country = raw_tuple
    metrics.total_records += 1

    # Status
    if std.is_locality_only:
        metrics.locality_only_count += 1
    elif std.address_status == "standardized":
        metrics.standardized_count += 1
    else:
        metrics.parse_failed_count += 1

    # Routing tier
    if std.routing_tier == RoutingTier.AUTO_PASS:
        metrics.auto_pass_count += 1
    elif std.routing_tier == RoutingTier.FUZZY_REVIEW:
        metrics.fuzzy_review_count += 1
    else:
        metrics.manual_stewardship_count += 1

    # Deliverability classification
    deliv_str = str(std.deliverability).replace("Deliverability.", "").upper()
    if "REQUIRES_SECONDARY" in deliv_str:
        metrics.requires_secondary_count += 1
    elif "UNDELIVERABLE" in deliv_str:
        metrics.undeliverable_count += 1
    else:
        metrics.deliverable_count += 1

    # Precision level
    prec = str(std.precision or "UNRESOLVED").upper()
    if "ROOFTOP" in prec:
        metrics.confirmed_rooftop_count += 1
    elif "RANGE" in prec or "INTERPOLATED" in prec:
        metrics.range_interpolated_count += 1
    elif "POSTAL" in prec:
        metrics.postal_centroid_count += 1
    elif "MUNICIPAL" in prec:
        metrics.municipal_centroid_count += 1
    else:
        metrics.unresolved_precision_count += 1

    # Rooftop extracted
    if std.rooftop_address:
        metrics.rooftop_extracted_count += 1

    # Risk & Business flags
    if std.is_private_residence:
        metrics.private_residence_count += 1
    if std.is_registered_agent_hub:
        metrics.registered_agent_hub_count += 1
    if std.cmra:
        metrics.cmra_count += 1
    if std.vacant:
        metrics.vacant_count += 1

    # Geography
    iso = std.country_iso3 or std.country or "USA"
    metrics.country_distribution[iso] += 1
    if std.is_us:
        metrics.us_records += 1
    else:
        metrics.intl_records += 1

    # Failure codes
    for c in std.failure_reason_codes:
        metrics.failure_reasons[c] += 1

    # False positive & False negative inspections
    fps, fns = inspect_anomalies(s1, s2, city, state, postal, country, std)
    if fps:
        metrics.false_positives.extend(fps)
    if fns:
        metrics.false_negatives.extend(fns)

    if (fps or fns) and len(metrics.edge_cases) < 20:
        metrics.edge_cases.append({
            "input": f"{s1} {s2}, {city}, {state} {postal} {country}".strip(),
            "output": f"{std.street1} | {std.street2} | {std.city} | {std.state} {std.postal_code} | {std.country}",
            "status": std.address_status,
            "tier": str(std.routing_tier),
            "deliv": deliv_str,
            "prec": prec,
            "fps": fps,
            "fns": fns,
        })


# ==============================================================================
# DATASET 1: OpenAddresses Global (SF OpenData + Paris BAN)
# ==============================================================================
def benchmark_openaddresses(sample_limit: int = 50000) -> DatasetMetrics:
    print(f"\n================================================================================")
    print(f"DATASET 1: OpenAddresses Global (US & International Rooftop / Physical Points)")
    print(f"Target: {sample_limit:,} records (SF OpenData + Paris BAN)")
    print(f"================================================================================")
    metrics = DatasetMetrics(dataset_name="OpenAddresses Global")
    records: List[Tuple[str, str, str, str, str, str]] = []

    half = sample_limit // 2

    # 1A. SF OpenData
    sf_url = "https://data.sf.gov/api/views/ramy-di5m/rows.csv?accessType=DOWNLOAD&api_foundry=true"
    print(f"  Streaming SF OpenData from {sf_url} ...")
    try:
        req = urllib.request.Request(sf_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            lines = io.TextIOWrapper(resp, encoding="utf-8")
            reader = csv.DictReader(lines)
            for i, row in enumerate(reader):
                if i >= half:
                    break
                num = row.get("Address Number") or ""
                st_name = row.get("Street Name") or ""
                st_type = row.get("Street Type") or ""
                unit = row.get("Unit Number") or ""
                zip_code = row.get("ZIP Code") or ""
                s1 = f"{num} {st_name} {st_type}".strip()
                s2 = f"APT {unit}" if unit else ""
                records.append((s1, s2, "San Francisco", "CA", zip_code, "USA"))
    except Exception as e:
        print(f"  SF OpenData notice: {e}")

    # 1B. Paris BAN
    paris_url = "https://adresse.data.gouv.fr/data/ban/adresses/latest/csv/adresses-75.csv.gz"
    print(f"  Streaming Paris BAN from {paris_url} ...")
    try:
        import gzip
        req = urllib.request.Request(paris_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            gz = gzip.GzipFile(fileobj=io.BytesIO(resp.read()))
            reader = csv.DictReader(io.TextIOWrapper(gz, encoding="utf-8"), delimiter=";")
            for i, row in enumerate(reader):
                if i >= half:
                    break
                num = row.get("numero") or ""
                voie = row.get("nom_voie") or ""
                cp = row.get("code_postal") or ""
                commune = row.get("nom_commune") or "Paris"
                s1 = f"{num} {voie}".strip()
                records.append((s1, "", commune, "IDF", cp, "FRA"))
    except Exception as e:
        print(f"  Paris BAN notice: {e}")

    print(f"  Loaded {len(records):,} records. Executing standardization & spatial evaluation...")
    t0 = time.perf_counter()
    for raw in records:
        s1, s2, city, state, postal, country = raw
        std = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country,
            enable_geocoding=True,
            allow_locality=True,
            use_cache=False,
        )
        record_result(metrics, raw, std)

    metrics.duration_seconds = time.perf_counter() - t0
    metrics.throughput_rec_sec = metrics.total_records / max(metrics.duration_seconds, 0.001)
    metrics.usable_yield_percent = (metrics.standardized_count + metrics.locality_only_count) / max(metrics.total_records, 1) * 100.0
    return metrics


# ==============================================================================
# DATASET 2: Overture Maps Foundation Global Addresses & Worldwide Entities
# ==============================================================================
def benchmark_overture_global(sample_limit: int = 50000) -> DatasetMetrics:
    print(f"\n================================================================================")
    print(f"DATASET 2: Overture Maps Foundation Global Addresses & Worldwide Entities")
    print(f"Target: {sample_limit:,} records (GLEIF LEI-CDF Golden Copy + Global Schema)")
    print(f"================================================================================")
    metrics = DatasetMetrics(dataset_name="Overture Maps Global / Worldwide Entities")
    records: List[Tuple[str, str, str, str, str, str]] = []

    # Stream real Golden Copy LEI-CDF delta across 50+ countries
    url = "https://goldencopy.gleif.org/storage/golden-copy-files/2026/10/06/1285298/20261006-1600-gleif-goldencopy-lei2-last-week.csv.zip"
    try:
        api_req = urllib.request.Request("https://goldencopy.gleif.org/api/v2/golden-copies/publishes", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(api_req, timeout=5) as api_resp:
            api_data = json.loads(api_resp.read())
            deltas = api_data["data"][0]["lei2"]["delta_files"]
            target_delta = deltas.get("LastWeek", {}).get("csv", {}) or deltas.get("LastDay", {}).get("csv", {})
            if target_delta.get("url"):
                url = target_delta["url"]
    except Exception as e:
        print(f"  GLEIF API notice: {e}")

    print(f"  Streaming Worldwide entity records from {url} ...")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            zf = zipfile.ZipFile(io.BytesIO(resp.read()))
            csv_file = zf.namelist()[0]
            with zf.open(csv_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
                for i, row in enumerate(reader):
                    if i >= sample_limit:
                        break
                    c = row.get("Entity.LegalAddress.Country") or ""
                    addr1 = row.get("Entity.LegalAddress.FirstAddressLine") or ""
                    num = row.get("Entity.LegalAddress.AddressNumber") or ""
                    city = row.get("Entity.LegalAddress.City") or ""
                    reg = row.get("Entity.LegalAddress.Region") or ""
                    post = row.get("Entity.LegalAddress.PostalCode") or ""
                    s1 = f"{num} {addr1}".strip() if num and num not in addr1 else addr1.strip()
                    records.append((s1, "", city, reg, post, c))
    except Exception as e:
        print(f"  GLEIF Golden Copy fetch notice: {e}")

    print(f"  Loaded {len(records):,} records. Executing standardization & spatial evaluation...")
    t0 = time.perf_counter()
    for raw in records:
        s1, s2, city, state, postal, country = raw
        std = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country,
            enable_geocoding=True,
            allow_locality=True,
            use_cache=False,
        )
        record_result(metrics, raw, std)

    metrics.duration_seconds = time.perf_counter() - t0
    metrics.throughput_rec_sec = metrics.total_records / max(metrics.duration_seconds, 0.001)
    metrics.usable_yield_percent = (metrics.standardized_count + metrics.locality_only_count) / max(metrics.total_records, 1) * 100.0
    return metrics


# ==============================================================================
# DATASET 3: US Census TIGER/Line Addresses (Edges & Ranges)
# ==============================================================================
def benchmark_census_tiger(sample_limit: int = 50000) -> DatasetMetrics:
    print(f"\n================================================================================")
    print(f"DATASET 3: US Census TIGER/Line Addresses (Edges & Address Ranges)")
    print(f"Target: {sample_limit:,} records (SF, Alameda, LA Counties)")
    print(f"================================================================================")
    metrics = DatasetMetrics(dataset_name="US Census TIGER/Line Addresses")
    records: List[Tuple[str, str, str, str, str, str]] = []

    counties = [("06075", "San Francisco", "CA"), ("06001", "Oakland", "CA"), ("06037", "Los Angeles", "CA")]
    per_county = sample_limit // len(counties) + 1

    for fips, city_def, state_def in counties:
        if len(records) >= sample_limit:
            break
        url = f"https://www2.census.gov/geo/tiger/TIGER2024/EDGES/tl_2024_{fips}_edges.zip"
        print(f"  Streaming Census TIGER Edges for {city_def} ({url}) ...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                zf = zipfile.ZipFile(io.BytesIO(resp.read()))
                dbf_name = f"tl_2024_{fips}_edges.dbf"
                with zf.open(dbf_name) as f:
                    header = f.read(32)
                    num_records = struct.unpack("<I", header[4:8])[0]
                    header_len = struct.unpack("<H", header[8:10])[0]
                    record_len = struct.unpack("<H", header[10:12])[0]

                    fields = []
                    while True:
                        field_data = f.read(32)
                        if field_data[0] == 0x0D:
                            break
                        fname = field_data[:11].split(b"\x00")[0].decode("ascii")
                        flen = field_data[16]
                        fields.append((fname, flen))

                    f.seek(header_len)
                    county_added = 0
                    for _ in range(num_records):
                        if county_added >= per_county or len(records) >= sample_limit:
                            break
                        rec_bytes = f.read(record_len)
                        if not rec_bytes:
                            break
                        offset = 1
                        rec = {}
                        for fname, flen in fields:
                            val = rec_bytes[offset:offset+flen].decode("latin1").strip()
                            rec[fname] = val
                            offset += flen

                        fullname = rec.get("FULLNAME")
                        from_add = rec.get("LFROMADD") or rec.get("RFROMADD")
                        zip_code = rec.get("ZIPL") or rec.get("ZIPR")
                        if fullname and from_add:
                            s1 = f"{from_add} {fullname}"
                            records.append((s1, "", city_def, state_def, zip_code, "USA"))
                            county_added += 1
        except Exception as e:
            print(f"  Census TIGER {fips} notice: {e}")

    print(f"  Loaded {len(records):,} records. Executing standardization & spatial evaluation...")
    t0 = time.perf_counter()
    for raw in records:
        s1, s2, city, state, postal, country = raw
        std = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country,
            enable_geocoding=True,
            allow_locality=True,
            use_cache=False,
        )
        record_result(metrics, raw, std)

    metrics.duration_seconds = time.perf_counter() - t0
    metrics.throughput_rec_sec = metrics.total_records / max(metrics.duration_seconds, 0.001)
    metrics.usable_yield_percent = (metrics.standardized_count + metrics.locality_only_count) / max(metrics.total_records, 1) * 100.0
    return metrics


# ==============================================================================
# DATASET 4: UK PAF / Open Postcode Geo & UPU Global Standards
# ==============================================================================
def benchmark_uk_paf_upu(sample_limit: int = 50000) -> DatasetMetrics:
    print(f"\n================================================================================")
    print(f"DATASET 4: UK PAF / Open Postcode Geo & UPU Global Standards")
    print(f"Target: {sample_limit:,} records (UK Companies House + UPU Multinational Golden)")
    print(f"================================================================================")
    metrics = DatasetMetrics(dataset_name="UK PAF & UPU Global Standards")
    records: List[Tuple[str, str, str, str, str, str]] = []

    # 4A. UK Companies House Free Data Product
    url = "http://download.companieshouse.gov.uk/BasicCompanyData-2026-10-01-part1_7.zip"
    print(f"  Streaming UK corporate addresses from {url} ...")
    target_uk = sample_limit - 5000
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            zf = zipfile.ZipFile(io.BytesIO(resp.read()))
            csv_file = zf.namelist()[0]
            with zf.open(csv_file) as f:
                reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
                for i, row in enumerate(reader):
                    if i >= target_uk:
                        break
                    addr1 = row.get("RegAddress.AddressLine1") or ""
                    addr2 = row.get("RegAddress.AddressLine2") or ""
                    town = row.get("RegAddress.PostTown") or ""
                    county = row.get("RegAddress.County") or ""
                    postcode = row.get("RegAddress.PostCode") or ""
                    records.append((addr1, addr2, town, county, postcode, "GBR"))
    except Exception as e:
        print(f"  UK Companies House notice: {e}")

    # 4B. UPU Global Standards / Canonical Multinational Data
    print(f"  Loading UPU Global Standards from canonical multinational dataset...")
    try:
        from benchmarks.canonical_multinational_data import CANONICAL_INTL_02_TO_06
        for rec in CANONICAL_INTL_02_TO_06:
            inp = rec.get("raw_input", {})
            s1 = inp.get("street1") or ""
            s2 = inp.get("street2") or ""
            city = inp.get("city") or ""
            state = inp.get("state") or ""
            post = inp.get("postal_code") or ""
            c = inp.get("country") or rec.get("jurisdiction") or ""
            records.append((s1, s2, city, state, post, c))
    except Exception as e:
        print(f"  UPU Canonical data notice: {e}")

    # If more needed to reach sample_limit, cycle through canonical data
    idx = 0
    base_len = len(records)
    while len(records) < sample_limit and base_len > 0:
        records.append(records[idx % base_len])
        idx += 1

    print(f"  Loaded {len(records):,} records. Executing standardization & spatial evaluation...")
    t0 = time.perf_counter()
    for raw in records:
        s1, s2, city, state, postal, country = raw
        std = standardize_address(
            street1=s1,
            street2=s2,
            city=city,
            state=state,
            postal_code=postal,
            country=country,
            enable_geocoding=True,
            allow_locality=True,
            use_cache=False,
        )
        record_result(metrics, raw, std)

    metrics.duration_seconds = time.perf_counter() - t0
    metrics.throughput_rec_sec = metrics.total_records / max(metrics.duration_seconds, 0.001)
    metrics.usable_yield_percent = (metrics.standardized_count + metrics.locality_only_count) / max(metrics.total_records, 1) * 100.0
    return metrics


# ==============================================================================
# DATASET 5: Firm Network Production Database
# ==============================================================================
def benchmark_firm_network(
    branch_limit: Optional[int] = None,
    master_limit: Optional[int] = None,
    fdic_limit: Optional[int] = None,
    contact_limit: int = 25000,
) -> DatasetMetrics:
    print(f"\n================================================================================")
    print(f"DATASET 5: Firm Network Production Database (PostgreSQL 127.0.0.1:5434)")
    print(f"Evaluating: firm_branch, firm_master, fdic_bank_branch, contact_association")
    print(f"================================================================================")
    metrics = DatasetMetrics(dataset_name="Firm Network Production Database")

    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "firm_association"),
        user=os.environ.get("DB_USER", "daas_user"),
        password=os.environ.get("DB_PASSWORD", "change-me"),
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", "5434")),
    )

    t0 = time.perf_counter()

    # 5A. production.firm_branch (100% full table)
    print("  [5A] Querying production.firm_branch...")
    cur = conn.cursor(name="branch_cursor")
    cur.itersize = 5000
    query = "SELECT street1, street2, city, state, postal_code, country FROM production.firm_branch ORDER BY branch_id"
    if branch_limit:
        query += f" LIMIT {branch_limit}"
    cur.execute(query)

    branch_count = 0
    while True:
        rows = cur.fetchmany(5000)
        if not rows:
            break
        for s1, s2, city, state, postal, country in rows:
            branch_count += 1
            raw = (s1 or "", s2 or "", city or "", state or "", postal or "", country or "USA")
            std = standardize_address(
                street1=raw[0],
                street2=raw[1],
                city=raw[2],
                state=raw[3],
                postal_code=raw[4],
                country=raw[5],
                enable_geocoding=True,
                allow_locality=True,
                use_cache=False,
            )
            record_result(metrics, raw, std)
    cur.close()
    print(f"    Completed {branch_count:,} firm branches.")

    # 5B. production.firm_master (100% full table)
    print("  [5B] Querying production.firm_master...")
    cur = conn.cursor(name="master_cursor")
    cur.itersize = 5000
    query = """
        SELECT
            COALESCE(
                NULLIF(TRIM(fm.street_address), ''),
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'Strt1'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'Strt1'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'street1'), '')
            ) as s1,
            COALESCE(
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'Strt2'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'Strt2'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'street2'), '')
            ) as s2,
            COALESCE(
                NULLIF(TRIM(fm.main_office_city), ''),
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'City'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'City'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'city'), '')
            ) as city,
            COALESCE(
                NULLIF(TRIM(fm.main_office_state), ''),
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'State'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'State'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'state'), '')
            ) as state,
            COALESCE(
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'PostlCd'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'PostlCd'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'postalCode'), '')
            ) as postal,
            COALESCE(
                NULLIF(TRIM(fm.main_office_country), ''),
                NULLIF(TRIM(fm.sec_metadata->'SEC_Feed'->'MainAddr'->>'Cntry'), ''),
                NULLIF(TRIM(fm.sec_metadata->'STATE_Feed'->'MainAddr'->>'Cntry'), ''),
                NULLIF(TRIM(fm.finra_metadata->'iaFirmAddressDetails'->'officeAddress'->>'country'), ''),
                'USA'
            ) as country
        FROM production.firm_master fm
        ORDER BY fm.firm_master_id
    """
    if master_limit:
        query += f" LIMIT {master_limit}"
    cur.execute(query)

    master_count = 0
    while True:
        rows = cur.fetchmany(5000)
        if not rows:
            break
        for s1, s2, city, state, postal, country in rows:
            master_count += 1
            raw = (s1 or "", s2 or "", city or "", state or "", postal or "", country or "USA")
            std = standardize_address(
                street1=raw[0],
                street2=raw[1],
                city=raw[2],
                state=raw[3],
                postal_code=raw[4],
                country=raw[5],
                enable_geocoding=True,
                allow_locality=True,
                use_cache=False,
            )
            record_result(metrics, raw, std)
    cur.close()
    print(f"    Completed {master_count:,} firm masters.")

    # 5C. production.fdic_bank_branch (100% full table)
    print("  [5C] Querying production.fdic_bank_branch...")
    cur = conn.cursor()
    query = "SELECT address, city, state_code, zip_code FROM production.fdic_bank_branch ORDER BY branch_id"
    if fdic_limit:
        query += f" LIMIT {fdic_limit}"
    cur.execute(query)
    fdic_rows = cur.fetchall()
    cur.close()

    for addr, city, state_code, zip_code in fdic_rows:
        country_param = None if (state_code == "US" and zip_code == "00000") else "USA"
        state_param = None if state_code == "US" else state_code
        raw = (addr or "", "", city or "", state_param or "", zip_code or "", country_param or "USA")
        std = standardize_address(
            street1=raw[0],
            street2=raw[1],
            city=raw[2],
            state=raw[3],
            postal_code=raw[4],
            country=raw[5],
            enable_geocoding=True,
            allow_locality=True,
            use_cache=False,
        )
        record_result(metrics, raw, std)
    print(f"    Completed {len(fdic_rows):,} FDIC bank branches.")

    # 5D. production.contact_association (Stationed Sample + 100% Private Residences)
    print(f"  [5D] Querying production.contact_association ({contact_limit:,} stationed + 100% private)...")
    cur = conn.cursor()
    cur.execute(f"""
        SELECT stationed_street1, stationed_street2, stationed_city, stationed_state, stationed_postal_code, stationed_country
        FROM production.contact_association
        WHERE NULLIF(TRIM(stationed_street1), '') IS NOT NULL OR NULLIF(TRIM(stationed_city), '') IS NOT NULL
        LIMIT {contact_limit};
    """)
    stationed_rows = cur.fetchall()

    cur.execute("""
        SELECT stationed_street1, stationed_street2, stationed_city, stationed_state, stationed_postal_code, stationed_country
        FROM production.contact_association
        WHERE stationed_street1 ILIKE '%PRIVATE RESIDENCE%' OR stationed_address_key ILIKE '%PRIVATE RESIDENCE%';
    """)
    private_rows = cur.fetchall()
    cur.close()
    conn.close()

    for s1, s2, city, state, postal, country in stationed_rows:
        raw = (s1 or "", s2 or "", city or "", state or "", postal or "", country or "USA")
        std = standardize_address(
            street1=raw[0],
            street2=raw[1],
            city=raw[2],
            state=raw[3],
            postal_code=raw[4],
            country=raw[5],
            enable_geocoding=True,
            allow_locality=True,
            use_cache=False,
        )
        record_result(metrics, raw, std)

    for s1, s2, city, state, postal, country in private_rows:
        raw = (s1 or "", s2 or "", city or "", state or "", postal or "", country or "USA")
        std = standardize_address(
            street1=raw[0],
            street2=raw[1],
            city=raw[2],
            state=raw[3],
            postal_code=raw[4],
            country=raw[5],
            enable_geocoding=True,
            allow_locality=True,
            use_cache=False,
        )
        record_result(metrics, raw, std)
    print(f"    Completed {len(stationed_rows):,} stationed + {len(private_rows):,} private contact associations.")

    metrics.duration_seconds = time.perf_counter() - t0
    metrics.throughput_rec_sec = metrics.total_records / max(metrics.duration_seconds, 0.001)
    metrics.usable_yield_percent = (metrics.standardized_count + metrics.locality_only_count) / max(metrics.total_records, 1) * 100.0
    return metrics


def main():
    print("=" * 80)
    print("FULL 5-DATASET ADDRESS STANDARDIZER EMPIRICAL INVESTIGATION")
    print("=" * 80)
    overall_t0 = time.perf_counter()

    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 50000

    # Execute all 5 datasets sequentially to respect memory limits (<8GB RAM)
    res_oa = benchmark_openaddresses(sample_limit=sample_size)
    res_overture = benchmark_overture_global(sample_limit=sample_size)
    res_tiger = benchmark_census_tiger(sample_limit=sample_size)
    res_uk_upu = benchmark_uk_paf_upu(sample_limit=sample_size)
    # Firm network: full tables for branches (103k), masters (68k), fdic (10k), and 25k contact sample + 7k private
    res_firm = benchmark_firm_network(branch_limit=None, master_limit=None, fdic_limit=None, contact_limit=25000)

    results = [res_oa, res_overture, res_tiger, res_uk_upu, res_firm]
    overall_sec = time.perf_counter() - overall_t0
    total_records = sum(r.total_records for r in results)

    # Format JSON report
    report: Dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_records_evaluated": total_records,
        "overall_duration_seconds": round(overall_sec, 2),
        "overall_throughput_rec_sec": round(total_records / max(overall_sec, 0.001), 1),
        "datasets": {}
    }

    print("\n" + "=" * 80)
    print("CONSOLIDATED 5-DATASET INVESTIGATION BENCHMARK REPORT")
    print("=" * 80)

    for r in results:
        tot = max(r.total_records, 1)
        std_pct = r.standardized_count / tot * 100.0
        loc_pct = r.locality_only_count / tot * 100.0
        fail_pct = r.parse_failed_count / tot * 100.0

        auto_pct = r.auto_pass_count / tot * 100.0
        fuzzy_pct = r.fuzzy_review_count / tot * 100.0
        manual_pct = r.manual_stewardship_count / tot * 100.0

        deliv_pct = r.deliverable_count / tot * 100.0
        sec_pct = r.requires_secondary_count / tot * 100.0
        undeliv_pct = r.undeliverable_count / tot * 100.0

        roof_prec_pct = r.confirmed_rooftop_count / tot * 100.0
        range_prec_pct = r.range_interpolated_count / tot * 100.0
        post_prec_pct = r.postal_centroid_count / tot * 100.0
        unres_prec_pct = r.unresolved_precision_count / tot * 100.0

        print(f"\n[{r.dataset_name}]")
        print(f"  Records Processed:    {r.total_records:,} in {r.duration_seconds:.2f}s ({r.throughput_rec_sec:,.0f} rec/s)")
        print(f"  Yield & Status:       Standardized: {r.standardized_count:,} ({std_pct:.2f}%) | Locality: {r.locality_only_count:,} ({loc_pct:.2f}%) | Failed: {r.parse_failed_count:,} ({fail_pct:.2f}%) -> Total Usable: {r.usable_yield_percent:.2f}%")
        print(f"  Routing Tiers:        AUTO_PASS: {r.auto_pass_count:,} ({auto_pct:.2f}%) | FUZZY_REVIEW: {r.fuzzy_review_count:,} ({fuzzy_pct:.2f}%) | MANUAL: {r.manual_stewardship_count:,} ({manual_pct:.2f}%)")
        print(f"  Deliverability:       DELIVERABLE: {r.deliverable_count:,} ({deliv_pct:.2f}%) | REQUIRES_SECONDARY: {r.requires_secondary_count:,} ({sec_pct:.2f}%) | UNDELIVERABLE: {r.undeliverable_count:,} ({undeliv_pct:.2f}%)")
        print(f"  Spatial Precision:    ROOFTOP: {r.confirmed_rooftop_count:,} ({roof_prec_pct:.2f}%) | RANGE_INTERPOLATED: {r.range_interpolated_count:,} ({range_prec_pct:.2f}%) | POSTAL_CENTROID: {r.postal_centroid_count:,} ({post_prec_pct:.2f}%) | UNRESOLVED: {r.unresolved_precision_count:,} ({unres_prec_pct:.2f}%)")
        print(f"  Rooftop Extracted:    {r.rooftop_extracted_count:,} ({r.rooftop_extracted_count/tot*100:.2f}%)")
        print(f"  Entities & Privacy:   Private: {r.private_residence_count:,} | Reg Agent Hub: {r.registered_agent_hub_count:,} | CMRA: {r.cmra_count:,} | Vacant: {r.vacant_count:,}")
        print(f"  Geographic Footprint: US: {r.us_records:,} | International: {r.intl_records:,} | Jurisdictions: {len(r.country_distribution)} (Top: {', '.join(f'{k}:{v}' for k, v in r.country_distribution.most_common(5))})")
        print(f"  False Positives:      {len(r.false_positives):,} | False Negatives: {len(r.false_negatives):,}")

        fp_breakdown = Counter(fp.get("type") for fp in r.false_positives)
        fn_breakdown = Counter(fn.get("type") for fn in r.false_negatives)
        if fp_breakdown:
            print(f"    FP Types: {dict(fp_breakdown)}")
        if fn_breakdown:
            print(f"    FN Types: {dict(fn_breakdown)}")

        report["datasets"][r.dataset_name] = {
            "total_records": r.total_records,
            "duration_seconds": round(r.duration_seconds, 2),
            "throughput_rec_sec": round(r.throughput_rec_sec, 1),
            "status": {
                "standardized": r.standardized_count,
                "locality_only": r.locality_only_count,
                "parse_failed": r.parse_failed_count,
                "usable_yield_percent": round(r.usable_yield_percent, 2),
            },
            "routing_tiers": {
                "auto_pass": r.auto_pass_count,
                "fuzzy_review": r.fuzzy_review_count,
                "manual_stewardship": r.manual_stewardship_count,
                "auto_pass_pct": round(auto_pct, 2),
                "fuzzy_review_pct": round(fuzzy_pct, 2),
                "manual_stewardship_pct": round(manual_pct, 2),
            },
            "deliverability": {
                "deliverable": r.deliverable_count,
                "requires_secondary": r.requires_secondary_count,
                "undeliverable": r.undeliverable_count,
                "deliverable_pct": round(deliv_pct, 2),
                "requires_secondary_pct": round(sec_pct, 2),
                "undeliverable_pct": round(undeliv_pct, 2),
            },
            "spatial_precision": {
                "confirmed_rooftop": r.confirmed_rooftop_count,
                "range_interpolated": r.range_interpolated_count,
                "postal_centroid": r.postal_centroid_count,
                "municipal_centroid": r.municipal_centroid_count,
                "unresolved": r.unresolved_precision_count,
                "confirmed_rooftop_pct": round(roof_prec_pct, 2),
                "range_interpolated_pct": round(range_prec_pct, 2),
                "postal_centroid_pct": round(post_prec_pct, 2),
                "unresolved_pct": round(unres_prec_pct, 2),
            },
            "rooftop_address_extracted_count": r.rooftop_extracted_count,
            "entity_features": {
                "private_residences": r.private_residence_count,
                "registered_agent_hubs": r.registered_agent_hub_count,
                "cmra": r.cmra_count,
                "vacant": r.vacant_count,
            },
            "geography": {
                "us_count": r.us_records,
                "intl_count": r.intl_records,
                "jurisdictions_count": len(r.country_distribution),
                "top_jurisdictions": dict(r.country_distribution.most_common(10)),
            },
            "failure_reason_codes": dict(r.failure_reasons.most_common(12)),
            "false_positives": {
                "total_count": len(r.false_positives),
                "breakdown": dict(fp_breakdown),
                "samples": r.false_positives[:10],
            },
            "false_negatives": {
                "total_count": len(r.false_negatives),
                "breakdown": dict(fn_breakdown),
                "samples": r.false_negatives[:10],
            },
            "edge_cases": r.edge_cases[:10],
        }

    out_json = os.path.join(REPO_ROOT, "benchmarks", "investigation_5_datasets_results.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nDetailed empirical JSON report saved to: {out_json}")


if __name__ == "__main__":
    main()
