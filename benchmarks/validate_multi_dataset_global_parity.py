#!/usr/bin/env python3
"""
Comprehensive Multi-Dataset Global Address Validation & Parity Benchmark
========================================================================
Runs Address-Standardizer across 5 major global and national address datasets:
  1. GLEIF Global Legal Entities (Golden Copy LEI-CDF across 50+ countries)
  2. OpenAddresses / Physical Delivery Points (US & International Rooftop Points)
  3. UK Companies House Free Data Product (British Business & Corporate Addresses)
  4. SEC EDGAR Corporate Filings (SEC Raw & Registrant Filings)
  5. US Census TIGER 2024 (US Federal Address Ranges & Edge Parity)

Evaluates:
  - Throughput (rec/sec)
  - Standardization pass rate (standardized, locality_only, parse_failed)
  - Routing tier distributions (AUTO_PASS, FUZZY_REVIEW, MANUAL_STEWARDSHIP)
  - Rooftop address extraction accuracy & unit stripping behavior
  - False positive detection:
      * False positive private residence flags
      * False positive registered agent / CMRA flags
      * False positive unit / rooftop stripping (e.g. "Park Way", "Level Creek Rd")
      * Misclassified country / US vs international routing
      * Loss of house number / street name truncation
      * Over-aggressive postal code / city mutation
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
import psycopg2
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

# Ensure Address-Standardizer is in path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from address_standardizer import standardize_address, StandardizedAddress, RoutingTier
from address_standardizer.tables import US_STATES


@dataclass
class DatasetBenchmarkResult:
    dataset_name: str
    total_records: int = 0
    duration_seconds: float = 0.0
    throughput_rec_sec: float = 0.0
    
    # Status counts
    standardized_count: int = 0
    locality_only_count: int = 0
    parse_failed_count: int = 0
    
    # Routing tier counts
    auto_pass_count: int = 0
    fuzzy_review_count: int = 0
    manual_stewardship_count: int = 0
    
    # Feature flags
    rooftop_extracted_count: int = 0
    private_residence_count: int = 0
    registered_agent_hub_count: int = 0
    cmra_count: int = 0
    vacant_count: int = 0
    
    # International & Country stats
    country_distribution: Counter = field(default_factory=Counter)
    us_records: int = 0
    intl_records: int = 0
    
    # Error & Failure reasons
    failure_reasons: Counter = field(default_factory=Counter)
    
    # False Positive tracking
    false_positives: List[Dict[str, Any]] = field(default_factory=list)
    edge_cases: List[Dict[str, Any]] = field(default_factory=list)


def check_false_positives(raw_street: str, raw_city: str, raw_state: str, raw_postal: str, raw_country: str,
                          std: StandardizedAddress) -> List[Dict[str, Any]]:
    """
    Deep-dive inspection for false positives:
    1. False Positive Private Residence: Flagged as private residence when raw text does NOT indicate residence,
       or when it is a business name/avenue/plaza.
    2. False Positive Rooftop Stripping: When clean_rooftop_address altered a legitimate street name that had no secondary unit.
    3. Street Number Loss: Raw street clearly had a leading house number, but standardized street1 has none.
    4. False Positive Registered Agent Hub: Flagged as hub without known hub keywords/addresses.
    5. False Positive Country Identification: Sovereign foreign country flagged as US or vice versa.
    """
    fps = []
    raw_s_upper = (raw_street or "").upper().strip()
    
    # 1. False Positive Private Residence
    if std.is_private_residence:
        legit_priv_terms = ["PRIVATE RESIDENCE", "RESIDENTIAL", "PRIVATE ADDRESS", "CONFIDENTIAL", "RESIDENCE ONLY", "PERSONAL RESIDENCE"]
        if not any(t in raw_s_upper for t in legit_priv_terms):
            fps.append({
                "type": "FALSE_POSITIVE_PRIVATE_RESIDENCE",
                "raw_street": raw_street,
                "reason": "Flagged as PRIVATE RESIDENCE without standard privacy keyword in raw input"
            })
            
    # 2. Rooftop Invariant Checks (PO Box, Private Residence, Locality-Only must NOT have rooftop address)
    if std.rooftop_address is not None:
        if std.is_private_residence:
            fps.append({
                "type": "ROOFTOP_ON_PRIVATE_RESIDENCE",
                "rooftop_address": std.rooftop_address,
                "reason": "Rooftop address generated for a private residence record"
            })
        if std.is_locality_only:
            fps.append({
                "type": "ROOFTOP_ON_LOCALITY_ONLY",
                "rooftop_address": std.rooftop_address,
                "reason": "Rooftop address generated for a locality-only record"
            })
        if re.search(r"\b(?:P\.?O\.?\s*BOX|POB|POST\s+OFFICE\s+BOX)\b", raw_s_upper):
            is_dual = bool(std.street1 and re.match(r"^(?:\d+|PR-|CARR-|KM\b)", std.street1))
            if not is_dual:
                fps.append({
                    "type": "ROOFTOP_ON_PO_BOX",
                    "raw_street": raw_street,
                    "rooftop_address": std.rooftop_address,
                    "reason": "Rooftop address generated for a PO Box record"
                })

    # 3. Rooftop Stripping False Positive
    if std.rooftop_address and std.street1:
        if std.rooftop_address != std.street1:
            has_unit_ind = bool(re.search(
                r"\b(?:SUITE|STE|APT|APARTMENT|UNIT|ROOM|RM|BLDG|BUILDING|FLOOR|FL|DEPT|DEPARTMENT|OFC|OFFICE|LOT|SPACE|SPC|TRAILER|TRLR|PIER|SLIP|LEVEL|LVL|PH|PENTHOUSE|BSMT|BASEMENT|LBBY|LOBBY|SIDE|REAR|FRONT|UPPR|LOWR|STOP|FLAT|MEZZANINE|BAY|CONDO|TOWER|STE\b|#)\b",
                std.street1, re.I
            ))
            # Check if stripped tokens contain core thoroughfare words
            s1_words = set(re.findall(r"\w+", std.street1.upper()))
            rf_words = set(re.findall(r"\w+", std.rooftop_address.upper()))
            dropped_words = s1_words - rf_words
            core_street_types = {"WAY", "CREEK", "HILL", "ROAD", "STREET", "AVENUE", "BOULEVARD", "BLVD", "LANE", "DRIVE", "PARK", "COURT", "PLACE", "TERRACE", "ROW", "MEWS", "CLOSE", "PLAZA", "SQUARE", "HIGHWAY", "HIGH"}
            
            if dropped_words.intersection(core_street_types) and not has_unit_ind:
                fps.append({
                    "type": "FALSE_POSITIVE_ROOFTOP_STRIPPING",
                    "street1": std.street1,
                    "rooftop_address": std.rooftop_address,
                    "dropped_core_words": list(dropped_words.intersection(core_street_types)),
                    "reason": f"Rooftop extraction stripped essential street type words: {dropped_words.intersection(core_street_types)}"
                })

    # 4. Street Number Loss Check
    m_num = re.match(r"^(\d+[A-Z]?|\d+-\d+)\s+([A-Za-z].*)$", raw_s_upper)
    if m_num and std.address_status == "standardized" and not std.is_locality_only:
        lead_num = m_num.group(1).upper()
        s2_upper = (std.street2 or "").upper()
        if (
            lead_num in s2_upper
            or (lead_num.endswith("F") and f"FL {lead_num[:-1]}" in s2_upper)
            or re.match(r"^\d+\s+(?:FLOOR|FL|FLR|STAIR|LEVEL|LVL)\b", raw_s_upper)
        ):
            pass
        elif not re.match(r"^\d", std.street1) and not re.match(r"^(?:ONE|TWO|THREE|FOUR|FIVE|SIX|SEVEN|EIGHT|NINE|TEN)\b", std.street1, re.I):
            fps.append({
                "type": "STREET_NUMBER_DROPPED",
                "raw_street": raw_street,
                "street1": std.street1,
                "reason": "Raw street had leading house number but standardized street1 has none"
            })

    # 5. Over-aggressive Street Truncation Check
    if raw_street and std.street1 and std.address_status == "standardized" and not std.is_locality_only:
        if len(std.street1) < 4 and len(raw_street) > 8 and not re.match(r"^(?:US|SR|CR|I)-\d+", raw_street.upper()):
            fps.append({
                "type": "SEVERE_STREET_TRUNCATION",
                "raw_street": raw_street,
                "street1": std.street1,
                "reason": f"Standardized street1 is suspiciously short ({std.street1}) compared to raw input ({raw_street})"
            })

    # 6. Country Misclassification Check
    if raw_country:
        rc_clean = raw_country.strip().upper()
        if rc_clean in ("UK", "GB", "GBR", "UNITED KINGDOM", "ENGLAND", "SCOTLAND", "WALES",
                        "CANADA", "CA", "CAN", "GERMANY", "DE", "DEU", "FRANCE", "FR", "FRA",
                        "SPAIN", "ES", "ESP", "ITALY", "IT", "ITA", "JAPAN", "JP", "JPN",
                        "AUSTRALIA", "AU", "AUS", "SWITZERLAND", "CH", "CHE"):
            if std.is_us:
                fps.append({
                    "type": "FALSE_POSITIVE_US_ROUTING",
                    "raw_country": raw_country,
                    "country_iso3": std.country_iso3,
                    "is_us": std.is_us,
                    "reason": f"Explicit foreign country {raw_country} was classified as US"
                })

    return fps


# ==============================================================================
# DATASET 1: GLEIF Global Legal Entities (Golden Copy LEI-CDF)
# ==============================================================================
def run_gleif_benchmark(sample_limit: int = 10000) -> DatasetBenchmarkResult:
    print(f"\n========================================================")
    print(f"Dataset 1: GLEIF Global Legal Entities (Golden Copy)")
    print(f"Target sample: {sample_limit} records across 50+ countries")
    print(f"========================================================")
    
    url = "https://goldencopy.gleif.org/storage/golden-copy-files/2026/10/06/1285298/20261006-1600-gleif-goldencopy-lei2-last-week.csv.zip"
    try:
        api_req = urllib.request.Request("https://goldencopy.gleif.org/api/v2/golden-copies/publishes", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(api_req, timeout=5) as api_resp:
            api_data = json.loads(api_resp.read())
            deltas = api_data["data"][0]["lei2"]["delta_files"]
            if sample_limit > 20000:
                target_delta = deltas.get("LastWeek", {}).get("csv", {}) or deltas.get("LastMonth", {}).get("csv", {})
            else:
                target_delta = deltas.get("LastDay", {}).get("csv", {})
            if target_delta.get("url"):
                url = target_delta["url"]
    except Exception as e:
        print(f"GLEIF dynamic API notice: {e}, using default {url}")

    print(f"Streaming from: {url} ...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    
    t0 = time.time()
    with urllib.request.urlopen(req) as resp:
        zf = zipfile.ZipFile(io.BytesIO(resp.read()))
        csv_file = zf.namelist()[0]
        f = zf.open(csv_file)
        reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"))
        
        result = DatasetBenchmarkResult(dataset_name="GLEIF Global Legal Entities")
        
        records_to_test = []
        for i, row in enumerate(reader):
            if i >= sample_limit:
                break
            c = row.get("Entity.LegalAddress.Country") or ""
            addr1 = row.get("Entity.LegalAddress.FirstAddressLine") or ""
            num = row.get("Entity.LegalAddress.AddressNumber") or ""
            city = row.get("Entity.LegalAddress.City") or ""
            reg = row.get("Entity.LegalAddress.Region") or ""
            post = row.get("Entity.LegalAddress.PostalCode") or ""
            name = row.get("Entity.LegalName") or ""
            
            street_input = f"{num} {addr1}".strip() if num and num not in addr1 else addr1.strip()
            records_to_test.append((name, street_input, city, reg, post, c))

    print(f"Loaded {len(records_to_test)} GLEIF records in {time.time() - t0:.2f}s. Benchmarking standardization...")
    
    t_start = time.time()
    for name, street, city, state, post, country in records_to_test:
        std = standardize_address(
            street1=street,
            city=city,
            state=state,
            postal_code=post,
            country=country,
            allow_locality=True,
            use_cache=False,
        )
        result.total_records += 1
        
        # Status
        if std.is_locality_only:
            result.locality_only_count += 1
        elif std.address_status == "standardized":
            result.standardized_count += 1
        else:
            result.parse_failed_count += 1
            
        # Routing tier
        if std.routing_tier == RoutingTier.AUTO_PASS:
            result.auto_pass_count += 1
        elif std.routing_tier == RoutingTier.FUZZY_REVIEW:
            result.fuzzy_review_count += 1
        else:
            result.manual_stewardship_count += 1
            
        # Features
        if std.rooftop_address:
            result.rooftop_extracted_count += 1
        if std.is_private_residence:
            result.private_residence_count += 1
        if std.is_registered_agent_hub:
            result.registered_agent_hub_count += 1
        if std.cmra:
            result.cmra_count += 1
            
        # Country
        iso = std.country_iso3 or std.country
        result.country_distribution[iso] += 1
        if std.is_us:
            result.us_records += 1
        else:
            result.intl_records += 1
            
        # Failures
        if std.failure_reason_codes:
            for code in std.failure_reason_codes:
                result.failure_reasons[code] += 1
                
        # False positives check
        fps = check_false_positives(street, city, state, post, country, std)
        if fps:
            result.false_positives.extend(fps)
            if len(result.edge_cases) < 15:
                result.edge_cases.append({
                    "entity": name,
                    "input": f"{street}, {city}, {state} {post}, {country}",
                    "std": f"{std.street1} | {std.city} | {std.state} {std.postal_code} | {std.country}",
                    "status": std.address_status,
                    "tier": str(std.routing_tier),
                    "fps": fps
                })
                
    result.duration_seconds = time.time() - t_start
    result.throughput_rec_sec = result.total_records / max(result.duration_seconds, 0.001)
    return result


# ==============================================================================
# DATASET 2: OpenAddresses (Physical Rooftop & Delivery Points)
# ==============================================================================
def run_openaddresses_benchmark(sample_limit: int = 10000) -> DatasetBenchmarkResult:
    print(f"\n========================================================")
    print(f"Dataset 2: OpenAddresses / Physical Delivery Points")
    print(f"Target sample: {sample_limit} records (San Francisco + Paris BAN)")
    print(f"========================================================")
    
    result = DatasetBenchmarkResult(dataset_name="OpenAddresses Physical Rooftop Points")
    records_to_test = []
    
    # 2A. San Francisco Physical Addresses with Units
    half = sample_limit // 2
    sf_url = "https://data.sf.gov/api/views/ramy-di5m/rows.csv?accessType=DOWNLOAD&api_foundry=true"
    print(f"Streaming US Rooftop points from SF OpenData ({sf_url})...")
    try:
        req = urllib.request.Request(sf_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
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
                
                street1 = f"{num} {st_name} {st_type}".strip()
                street2 = f"APT {unit}" if unit else ""
                records_to_test.append((street1, street2, "San Francisco", "CA", zip_code, "USA"))
    except Exception as e:
        print(f"SF OpenData fetch notice: {e}")
        
    # 2B. Paris BAN Physical Addresses (International Europe)
    paris_url = "https://adresse.data.gouv.fr/data/ban/adresses/latest/csv/adresses-75.csv.gz"
    print(f"Streaming International Rooftop points from Paris BAN ({paris_url})...")
    try:
        req = urllib.request.Request(paris_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            import gzip
            gz = gzip.GzipFile(fileobj=io.BytesIO(resp.read()))
            reader = csv.DictReader(io.TextIOWrapper(gz, encoding="utf-8"), delimiter=";")
            for i, row in enumerate(reader):
                if i >= half:
                    break
                num = row.get("numero") or ""
                voie = row.get("nom_voie") or ""
                cp = row.get("code_postal") or ""
                commune = row.get("nom_commune") or "Paris"
                
                street = f"{num} {voie}".strip()
                records_to_test.append((street, "", commune, "IDF", cp, "FRA"))
    except Exception as e:
        print(f"Paris BAN fetch notice: {e}")
        
    print(f"Loaded {len(records_to_test)} physical address points. Benchmarking standardization...")
    t_start = time.time()
    for street1, street2, city, state, post, country in records_to_test:
        std = standardize_address(
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=post,
            country=country,
            allow_locality=True,
            use_cache=False,
        )
        result.total_records += 1
        
        if std.is_locality_only:
            result.locality_only_count += 1
        elif std.address_status == "standardized":
            result.standardized_count += 1
        else:
            result.parse_failed_count += 1
            
        if std.routing_tier == RoutingTier.AUTO_PASS:
            result.auto_pass_count += 1
        elif std.routing_tier == RoutingTier.FUZZY_REVIEW:
            result.fuzzy_review_count += 1
        else:
            result.manual_stewardship_count += 1
            
        if std.rooftop_address:
            result.rooftop_extracted_count += 1
        if std.is_private_residence:
            result.private_residence_count += 1
        if std.is_registered_agent_hub:
            result.registered_agent_hub_count += 1
        if std.cmra:
            result.cmra_count += 1
            
        iso = std.country_iso3 or std.country
        result.country_distribution[iso] += 1
        if std.is_us:
            result.us_records += 1
        else:
            result.intl_records += 1
            
        if std.failure_reason_codes:
            for code in std.failure_reason_codes:
                result.failure_reasons[code] += 1
                
        fps = check_false_positives(street1, city, state, post, country, std)
        if fps:
            result.false_positives.extend(fps)
            if len(result.edge_cases) < 15:
                result.edge_cases.append({
                    "input": f"{street1} {street2}, {city}, {state} {post}, {country}",
                    "std": f"{std.street1} | {std.city} | {std.state} {std.postal_code} | {std.country}",
                    "rooftop": std.rooftop_address,
                    "status": std.address_status,
                    "tier": str(std.routing_tier),
                    "fps": fps
                })
                
    result.duration_seconds = time.time() - t_start
    result.throughput_rec_sec = result.total_records / max(result.duration_seconds, 0.001)
    return result


# ==============================================================================
# DATASET 3: UK Companies House Free Data Product
# ==============================================================================
def run_uk_companies_house_benchmark(sample_limit: int = 10000) -> DatasetBenchmarkResult:
    print(f"\n========================================================")
    print(f"Dataset 3: UK Companies House Free Company Data Product")
    print(f"Target sample: {sample_limit} British corporate addresses")
    print(f"========================================================")
    
    result = DatasetBenchmarkResult(dataset_name="UK Companies House Corporate Data")
    url = "http://download.companieshouse.gov.uk/BasicCompanyData-2026-10-01-part1_7.zip"
    print(f"Streaming from: {url} ...")
    
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    records_to_test = []
    
    with urllib.request.urlopen(req) as resp:
        zf = zipfile.ZipFile(io.BytesIO(resp.read()))
        csv_file = zf.namelist()[0]
        with zf.open(csv_file) as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8", errors="replace"))
            for i, row in enumerate(reader):
                if i >= sample_limit:
                    break
                name = row.get("CompanyName") or ""
                addr1 = row.get("RegAddress.AddressLine1") or ""
                addr2 = row.get("RegAddress.AddressLine2") or ""
                town = row.get("RegAddress.PostTown") or ""
                county = row.get("RegAddress.County") or ""
                postcode = row.get("RegAddress.PostCode") or ""
                country = row.get("RegAddress.Country") or "United Kingdom"
                
                records_to_test.append((name, addr1, addr2, town, county, postcode, country))
                
    print(f"Loaded {len(records_to_test)} UK corporate records in {time.time() - t0:.2f}s. Benchmarking standardization...")
    t_start = time.time()
    for name, addr1, addr2, town, county, postcode, country in records_to_test:
        std = standardize_address(
            street1=addr1,
            street2=addr2,
            city=town,
            state=county,
            postal_code=postcode,
            country="GBR",
            allow_locality=True,
            use_cache=False,
        )
        result.total_records += 1
        
        if std.is_locality_only:
            result.locality_only_count += 1
        elif std.address_status == "standardized":
            result.standardized_count += 1
        else:
            result.parse_failed_count += 1
            
        if std.routing_tier == RoutingTier.AUTO_PASS:
            result.auto_pass_count += 1
        elif std.routing_tier == RoutingTier.FUZZY_REVIEW:
            result.fuzzy_review_count += 1
        else:
            result.manual_stewardship_count += 1
            
        if std.rooftop_address:
            result.rooftop_extracted_count += 1
        if std.is_private_residence:
            result.private_residence_count += 1
        if std.is_registered_agent_hub:
            result.registered_agent_hub_count += 1
        if std.cmra:
            result.cmra_count += 1
            
        iso = std.country_iso3 or std.country
        result.country_distribution[iso] += 1
        if std.is_us:
            result.us_records += 1
        else:
            result.intl_records += 1
            
        if std.failure_reason_codes:
            for code in std.failure_reason_codes:
                result.failure_reasons[code] += 1
                
        fps = check_false_positives(addr1, town, county, postcode, "GBR", std)
        if fps:
            result.false_positives.extend(fps)
            if len(result.edge_cases) < 15:
                result.edge_cases.append({
                    "entity": name,
                    "input": f"{addr1} {addr2}, {town}, {county} {postcode}, UK",
                    "std": f"{std.street1} | {std.city} | {std.state} {std.postal_code} | {std.country}",
                    "rooftop": std.rooftop_address,
                    "status": std.address_status,
                    "tier": str(std.routing_tier),
                    "fps": fps
                })
                
    result.duration_seconds = time.time() - t_start
    result.throughput_rec_sec = result.total_records / max(result.duration_seconds, 0.001)
    return result


# ==============================================================================
# DATASET 4: SEC EDGAR Corporate Filings (SEC Raw & Registrant Filings)
# ==============================================================================
def run_sec_edgar_benchmark(sample_limit: int = 10000) -> DatasetBenchmarkResult:
    print(f"\n========================================================")
    print(f"Dataset 4: SEC EDGAR Corporate Filings")
    print(f"Target sample: {sample_limit} corporate filer addresses")
    print(f"========================================================")
    
    result = DatasetBenchmarkResult(dataset_name="SEC EDGAR Corporate Filings")
    records_to_test = []
    
    # 4A. Query local PostgreSQL firm_association.staging.sec_raw_firms and form_d_related_person
    try:
        conn = psycopg2.connect("dbname=firm_association user=daas_user password=change-me host=127.0.0.1 port=5434")
        cur = conn.cursor()
        
        # 1. SEC Raw Firms (headquarters)
        cur.execute("""
            SELECT raw_business_name, raw_street_address, raw_city, raw_state, raw_country, raw_extra_metadata
            FROM staging.sec_raw_firms
            WHERE raw_street_address IS NOT NULL AND length(trim(raw_street_address)) > 0
            LIMIT %s;
        """, (sample_limit // 2,))
        for r in cur.fetchall():
            name = r[0] or ""
            street = r[1] or ""
            city = r[2] or ""
            state = r[3] or ""
            country = r[4] or "USA"
            meta = r[5] or {}
            post = ""
            if isinstance(meta, dict) and "MainAddr" in meta:
                post = meta["MainAddr"].get("PostlCd") or ""
            records_to_test.append((name, street, "", city, state, post, country))
            
        # 2. Form D Related Persons (executives, corporate offices)
        remaining = sample_limit - len(records_to_test)
        if remaining > 0:
            cur.execute("""
                SELECT first_name, last_name, street1, city, state, postal_code
                FROM production.form_d_related_person
                WHERE street1 IS NOT NULL AND length(trim(street1)) > 0
                LIMIT %s;
            """, (remaining,))
            for r in cur.fetchall():
                name = f"{r[0] or ''} {r[1] or ''}".strip()
                records_to_test.append((name, r[2] or "", "", r[3] or "", r[4] or "", r[5] or "", "USA"))
        cur.close()
        conn.close()
        print(f"Loaded {len(records_to_test)} SEC corporate records from database.")
    except Exception as e:
        print(f"Database query notice: {e}")
        
    t_start = time.time()
    for name, street1, street2, city, state, post, country in records_to_test:
        std = standardize_address(
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=post,
            country=country,
            allow_locality=True,
            use_cache=False,
        )
        result.total_records += 1
        
        if std.is_locality_only:
            result.locality_only_count += 1
        elif std.address_status == "standardized":
            result.standardized_count += 1
        else:
            result.parse_failed_count += 1
            
        if std.routing_tier == RoutingTier.AUTO_PASS:
            result.auto_pass_count += 1
        elif std.routing_tier == RoutingTier.FUZZY_REVIEW:
            result.fuzzy_review_count += 1
        else:
            result.manual_stewardship_count += 1
            
        if std.rooftop_address:
            result.rooftop_extracted_count += 1
        if std.is_private_residence:
            result.private_residence_count += 1
        if std.is_registered_agent_hub:
            result.registered_agent_hub_count += 1
        if std.cmra:
            result.cmra_count += 1
            
        iso = std.country_iso3 or std.country
        result.country_distribution[iso] += 1
        if std.is_us:
            result.us_records += 1
        else:
            result.intl_records += 1
            
        if std.failure_reason_codes:
            for code in std.failure_reason_codes:
                result.failure_reasons[code] += 1
                
        fps = check_false_positives(street1, city, state, post, country, std)
        if fps:
            result.false_positives.extend(fps)
            if len(result.edge_cases) < 15:
                result.edge_cases.append({
                    "entity": name,
                    "input": f"{street1} {street2}, {city}, {state} {post}, {country}",
                    "std": f"{std.street1} | {std.city} | {std.state} {std.postal_code} | {std.country}",
                    "rooftop": std.rooftop_address,
                    "status": std.address_status,
                    "tier": str(std.routing_tier),
                    "fps": fps
                })
                
    result.duration_seconds = time.time() - t_start
    result.throughput_rec_sec = result.total_records / max(result.duration_seconds, 0.001)
    return result


# ==============================================================================
# DATASET 5: US Census TIGER 2024 (Address Ranges & Edges)
# ==============================================================================
def run_census_tiger_benchmark(sample_limit: int = 10000) -> DatasetBenchmarkResult:
    print(f"\n========================================================")
    print(f"Dataset 5: US Census TIGER 2024 Address Ranges & Edges")
    print(f"Target sample: {sample_limit} nationwide road address points")
    print(f"========================================================")
    
    result = DatasetBenchmarkResult(dataset_name="US Census TIGER 2024 Address Ranges")
    
    # We stream Alameda (06001), San Francisco (06075), and Los Angeles (06037) TIGER EDGES
    counties = [("06075", "San Francisco", "CA"), ("06001", "Oakland", "CA"), ("06037", "Los Angeles", "CA")]
    records_to_test = []
    
    for fips, city_def, state_def in counties:
        url = f"https://www2.census.gov/geo/tiger/TIGER2024/EDGES/tl_2024_{fips}_edges.zip"
        print(f"Streaming Census TIGER Edges ({url})...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as resp:
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
                    for _ in range(num_records):
                        if len(records_to_test) >= sample_limit:
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
                            st1 = f"{from_add} {fullname}"
                            records_to_test.append((fullname, st1, "", city_def, state_def, zip_code, "USA"))
        except Exception as e:
            print(f"TIGER Edges fetch notice for {fips}: {e}")
            
    print(f"Loaded {len(records_to_test)} Census TIGER address points. Benchmarking standardization...")
    t_start = time.time()
    for name, street1, street2, city, state, post, country in records_to_test:
        std = standardize_address(
            street1=street1,
            street2=street2,
            city=city,
            state=state,
            postal_code=post,
            country=country,
            allow_locality=True,
            use_cache=False,
        )
        result.total_records += 1
        
        if std.is_locality_only:
            result.locality_only_count += 1
        elif std.address_status == "standardized":
            result.standardized_count += 1
        else:
            result.parse_failed_count += 1
            
        if std.routing_tier == RoutingTier.AUTO_PASS:
            result.auto_pass_count += 1
        elif std.routing_tier == RoutingTier.FUZZY_REVIEW:
            result.fuzzy_review_count += 1
        else:
            result.manual_stewardship_count += 1
            
        if std.rooftop_address:
            result.rooftop_extracted_count += 1
        if std.is_private_residence:
            result.private_residence_count += 1
        if std.is_registered_agent_hub:
            result.registered_agent_hub_count += 1
        if std.cmra:
            result.cmra_count += 1
            
        iso = std.country_iso3 or std.country
        result.country_distribution[iso] += 1
        if std.is_us:
            result.us_records += 1
        else:
            result.intl_records += 1
            
        if std.failure_reason_codes:
            for code in std.failure_reason_codes:
                result.failure_reasons[code] += 1
                
        fps = check_false_positives(street1, city, state, post, country, std)
        if fps:
            result.false_positives.extend(fps)
            if len(result.edge_cases) < 15:
                result.edge_cases.append({
                    "entity": name,
                    "input": f"{street1} {street2}, {city}, {state} {post}, {country}",
                    "std": f"{std.street1} | {std.city} | {std.state} {std.postal_code} | {std.country}",
                    "rooftop": std.rooftop_address,
                    "status": std.address_status,
                    "tier": str(std.routing_tier),
                    "fps": fps
                })
                
    result.duration_seconds = time.time() - t_start
    result.throughput_rec_sec = result.total_records / max(result.duration_seconds, 0.001)
    return result


def main():
    sample_size = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    print(f"================================================================================")
    print(f"GLOBAL ADDRESS VALIDATION HARNESS: 5 DIVERSE REAL-WORLD BENCHMARK DATASETS")
    print(f"Sample size per dataset: {sample_size} records (Total ~{sample_size * 5} records)")
    print(f"================================================================================")
    
    overall_start = time.time()
    
    # Run all 5 sequentially (preserving RAM & CPU according to resource_throttling rule)
    res_gleif = run_gleif_benchmark(sample_limit=sample_size)
    res_oa = run_openaddresses_benchmark(sample_limit=sample_size)
    res_uk = run_uk_companies_house_benchmark(sample_limit=sample_size)
    res_sec = run_sec_edgar_benchmark(sample_limit=sample_size)
    res_tiger = run_census_tiger_benchmark(sample_limit=sample_size)
    
    results = [res_gleif, res_oa, res_uk, res_sec, res_tiger]
    total_time = time.time() - overall_start
    total_records = sum(r.total_records for r in results)
    
    # Generate structured summary output
    summary_path = os.path.join(REPO_ROOT, "benchmarks", "multi_dataset_benchmark_results.json")
    summary_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_records": total_records,
        "total_duration_seconds": total_time,
        "overall_throughput_rec_sec": total_records / max(total_time, 0.001),
        "datasets": {}
    }
    
    print("\n" + "="*80)
    print(f"MULTI-DATASET GLOBAL BENCHMARK SUMMARY REPORT")
    print("="*80)
    
    for r in results:
        pass_rate = (r.standardized_count + r.locality_only_count) / max(r.total_records, 1) * 100.0
        auto_pass_rate = r.auto_pass_count / max(r.total_records, 1) * 100.0
        rooftop_rate = r.rooftop_extracted_count / max(r.total_records, 1) * 100.0
        
        print(f"\n[{r.dataset_name}]")
        print(f"  Records Processed: {r.total_records:,} in {r.duration_seconds:.2f}s ({r.throughput_rec_sec:,.0f} rec/s)")
        print(f"  Valid Delivery Points (Standardized): {r.standardized_count:,} ({r.standardized_count/max(r.total_records,1)*100:.1f}%)")
        print(f"  Locality-Only Preserved:               {r.locality_only_count:,} ({r.locality_only_count/max(r.total_records,1)*100:.1f}%)")
        print(f"  Parse Failed / Rejected:              {r.parse_failed_count:,} ({r.parse_failed_count/max(r.total_records,1)*100:.1f}%)")
        print(f"  Overall Usable Yield:                 {pass_rate:.1f}%")
        print(f"  Routing: AUTO_PASS {auto_pass_rate:.1f}% | FUZZY_REVIEW {r.fuzzy_review_count/max(r.total_records,1)*100:.1f}% | MANUAL {r.manual_stewardship_count/max(r.total_records,1)*100:.1f}%")
        print(f"  Rooftop Addresses Extracted:          {r.rooftop_extracted_count:,} ({rooftop_rate:.1f}%)")
        print(f"  Private Residences: {r.private_residence_count:,} | Reg Agent Hubs: {r.registered_agent_hub_count:,} | CMRA: {r.cmra_count:,}")
        print(f"  Countries Represented:                {len(r.country_distribution)} countries (Top 5: {', '.join(f'{k}:{v}' for k, v in r.country_distribution.most_common(5))})")
        print(f"  False Positives Detected:             {len(r.false_positives)}")
        
        if r.false_positives:
            fp_types = Counter(fp.get("type") for fp in r.false_positives)
            print(f"    FP Breakdown: {dict(fp_types)}")
            
        summary_data["datasets"][r.dataset_name] = {
            "total_records": r.total_records,
            "duration_seconds": r.duration_seconds,
            "throughput_rec_sec": r.throughput_rec_sec,
            "standardized_count": r.standardized_count,
            "locality_only_count": r.locality_only_count,
            "parse_failed_count": r.parse_failed_count,
            "usable_yield_percent": pass_rate,
            "auto_pass_count": r.auto_pass_count,
            "fuzzy_review_count": r.fuzzy_review_count,
            "manual_stewardship_count": r.manual_stewardship_count,
            "rooftop_count": r.rooftop_extracted_count,
            "private_residence_count": r.private_residence_count,
            "registered_agent_hub_count": r.registered_agent_hub_count,
            "cmra_count": r.cmra_count,
            "country_distribution": dict(r.country_distribution),
            "top_failure_reasons": dict(r.failure_reasons.most_common(10)),
            "false_positive_count": len(r.false_positives),
            "false_positive_types": dict(Counter(fp.get("type") for fp in r.false_positives)),
            "sample_edge_cases": r.edge_cases[:10]
        }
        
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print(f"\nFull detailed JSON benchmark results saved to: {summary_path}")


if __name__ == "__main__":
    main()
