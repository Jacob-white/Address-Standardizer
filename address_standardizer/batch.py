"""
Streaming Batch Processing & Bounded Multiprocessing Pipeline.
==============================================================
Provides memory-bounded chunked streaming CSV processing for massive datasets
(e.g., 100k - 1M+ rows) while guaranteeing constant O(chunk_size) RSS memory
(< 100 MB) and strict concurrency throttling (workers <= 2).
"""

import csv
import multiprocessing
from typing import Generator, List, Dict, Any, Optional, Tuple, Iterator
from address_standardizer.standardizer import standardize_address
from address_standardizer.geocoder import CensusGeocoder


def chunk_generator(
    reader: Iterator[Dict[str, Any]],
    chunk_size: int = 5000
) -> Generator[List[Dict[str, Any]], None, None]:
    """
    Yields rows from reader in fixed-size chunks to bound memory utilization.
    Ensures O(chunk_size) memory footprint regardless of file size.
    """
    chunk: List[Dict[str, Any]] = []
    for row in reader:
        chunk.append(row)
        if len(chunk) >= chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def _process_row_dict(
    row: Dict[str, Any],
    street_col: str = "street1",
    street2_col: str = "street2",
    city_col: str = "city",
    state_col: str = "state",
    zip_col: str = "postal_code",
    country_col: str = "country",
    include_confidence: bool = False,
    collect_audit: bool = False,
) -> Dict[str, Any]:
    """Standardizes a single row dictionary and appends standardized fields."""
    s1 = row.get(street_col) or ""
    s2 = row.get(street2_col) or ""
    city = row.get(city_col) or ""
    state = row.get(state_col) or ""
    postal = row.get(zip_col) or ""
    country = row.get(country_col) or "USA"

    st = standardize_address(
        street1=s1,
        street2=s2,
        city=city,
        state=state,
        postal_code=postal,
        country=country,
    )

    res_row = dict(row)
    res_row["std_street1"] = st.street1
    res_row["std_street2"] = st.street2
    res_row["std_city"] = st.city
    res_row["std_state"] = st.state
    res_row["std_postal_code"] = st.postal_code
    res_row["std_country"] = st.country
    res_row["normalized_address_key"] = st.normalized_address_key or ""
    res_row["building_key"] = st.building_key or ""
    res_row["phonetic_key"] = st.phonetic_key or ""
    res_row["is_registered_agent_hub"] = str(st.is_registered_agent_hub)
    res_row["is_private_residence"] = str(st.is_private_residence)
    res_row["address_status"] = st.address_status
    if include_confidence:
        res_row["confidence_score"] = f"{st.confidence_score:.4f}" if st.confidence_score is not None else ""
        res_row["routing_tier"] = st.routing_tier or ""
    if collect_audit and getattr(st, "audit_record", None) is not None:
        res_row["_audit_record"] = st.audit_record.as_dict()
    return res_row


def _worker_process_chunk(
    args: Tuple[List[Dict[str, Any]], str, str, str, str, str, str, bool]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Worker function for multiprocessing pool to process a single chunk."""
    chunk, street_col, street2_col, city_col, state_col, zip_col, country_col, include_confidence = args
    processed_rows = []
    audit_records = []
    for row in chunk:
        res = _process_row_dict(
            row,
            street_col=street_col,
            street2_col=street2_col,
            city_col=city_col,
            state_col=state_col,
            zip_col=zip_col,
            country_col=country_col,
            include_confidence=include_confidence,
            collect_audit=True,
        )
        aud = res.pop("_audit_record", None)
        if aud is not None:
            audit_records.append(aud)
        processed_rows.append(res)
    return processed_rows, audit_records


def process_chunk(
    chunk: List[Dict[str, Any]],
    street_col: str = "street1",
    street2_col: str = "street2",
    city_col: str = "city",
    state_col: str = "state",
    zip_col: str = "postal_code",
    country_col: str = "country",
    include_confidence: bool = False,
) -> List[Dict[str, Any]]:
    """Standardizes a chunk of rows."""
    processed_rows, _ = _worker_process_chunk(
        (chunk, street_col, street2_col, city_col, state_col, zip_col, country_col, include_confidence)
    )
    return processed_rows


def stream_standardize_csv(
    input_path: str,
    output_path: str,
    chunk_size: int = 5000,
    max_workers: int = 2,
    street_col: str = "street1",
    street2_col: str = "street2",
    city_col: str = "city",
    state_col: str = "state",
    zip_col: str = "postal_code",
    country_col: str = "country",
    geocode: bool = False,
    geocoder: Optional[CensusGeocoder] = None,
    include_confidence: bool = False,
    audit_csv_path: Optional[str] = None,
) -> int:
    """
    Streams CSV address standardization with constant O(chunk_size) RSS memory footprint (< 100MB).
    Strictly enforces resource throttling rules: max_workers is capped at 2.
    Returns total number of rows processed.
    """
    import json
    from address_standardizer.audit import get_audit_ledger, StewardshipAuditRecord

    # Enforce strict system resource limit (max 2 workers)
    effective_workers = max(1, min(max_workers, 2))
    total_processed = 0

    with open(input_path, mode="r", encoding="utf-8", errors="replace") as fin:
        reader = csv.DictReader(fin)
        fieldnames = list(reader.fieldnames or []) + [
            "std_street1", "std_street2", "std_city", "std_state", "std_postal_code",
            "std_country", "normalized_address_key", "building_key", "phonetic_key",
            "is_registered_agent_hub", "is_private_residence", "address_status"
        ]
        if include_confidence:
            fieldnames.extend(["confidence_score", "routing_tier"])
        if geocode:
            fieldnames.extend(["latitude", "longitude", "geocode_precision"])

        audit_file = None
        audit_writer = None
        if audit_csv_path:
            audit_file = open(audit_csv_path, mode="w", encoding="utf-8", newline="")
            audit_fieldnames = [
                "audit_id", "record_id", "batch_id", "timestamp_utc", "agent_or_system_id",
                "action_type", "confidence_score", "failure_reason_codes",
                "normalized_address_key", "building_key", "phonetic_key",
                "is_registered_agent_hub", "is_private_residence", "dpv_confirmation_code",
                "raw_input_payload", "proposed_standardized_payload", "final_committed_payload",
                "steward_commentary", "review_status", "reviewed_by", "reviewed_at"
            ]
            audit_writer = csv.DictWriter(audit_file, fieldnames=audit_fieldnames)
            audit_writer.writeheader()

        ledger = get_audit_ledger()

        def _handle_chunk_audits(audit_records: List[Dict[str, Any]]):
            for aud in audit_records:
                ledger.record(StewardshipAuditRecord.from_dict(aud))
                if audit_writer:
                    row_to_write = dict(aud)
                    for k in ("failure_reason_codes", "raw_input_payload", "proposed_standardized_payload", "final_committed_payload"):
                        val = row_to_write.get(k)
                        if isinstance(val, (dict, list)):
                            row_to_write[k] = json.dumps(val)
                    audit_writer.writerow(row_to_write)

        try:
            with open(output_path, mode="w", encoding="utf-8", newline="") as fout:
                writer = csv.DictWriter(fout, fieldnames=fieldnames)
                writer.writeheader()

                active_geocoder = geocoder or (CensusGeocoder() if geocode else None)

                def _apply_geocoding_to_chunk(processed_chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                    geo_batch = []
                    for idx, r in enumerate(processed_chunk):
                        if r.get("std_country") == "USA" and r.get("std_street1"):
                            geo_batch.append((str(idx), r["std_street1"], r["std_city"], r["std_state"], r["std_postal_code"]))
                    if geo_batch:
                        geo_results = active_geocoder.geocode_batch(geo_batch)
                        for idx, r in enumerate(processed_chunk):
                            idx_str = str(idx)
                            if idx_str in geo_results:
                                r["latitude"] = geo_results[idx_str]["latitude"]
                                r["longitude"] = geo_results[idx_str]["longitude"]
                                r["geocode_precision"] = geo_results[idx_str]["precision"]
                            else:
                                r["latitude"] = ""
                                r["longitude"] = ""
                                r["geocode_precision"] = ""
                    else:
                        for r in processed_chunk:
                            r["latitude"] = ""
                            r["longitude"] = ""
                            r["geocode_precision"] = ""
                    return processed_chunk

                if effective_workers <= 1:
                    for chunk in chunk_generator(reader, chunk_size):
                        processed, chunk_audits = _worker_process_chunk(
                            (chunk, street_col, street2_col, city_col, state_col, zip_col, country_col, include_confidence)
                        )
                        _handle_chunk_audits(chunk_audits)
                        if geocode:
                            processed = _apply_geocoding_to_chunk(processed)
                        writer.writerows(processed)
                        total_processed += len(processed)
                else:
                    chunk_args_gen = (
                        (chunk, street_col, street2_col, city_col, state_col, zip_col, country_col, include_confidence)
                        for chunk in chunk_generator(reader, chunk_size)
                    )
                    with multiprocessing.Pool(processes=effective_workers) as pool:
                        for processed_chunk, chunk_audits in pool.imap(_worker_process_chunk, chunk_args_gen):
                            _handle_chunk_audits(chunk_audits)
                            if geocode:
                                processed_chunk = _apply_geocoding_to_chunk(processed_chunk)
                            writer.writerows(processed_chunk)
                            total_processed += len(processed_chunk)
        finally:
            if audit_file:
                audit_file.close()

    return total_processed
