# Address Standardizer API Reference

Reference for version 3.3.0: the Python API, the REST API, the command line and the environment variables. For a
guided tour with runnable examples see [quickstart.md](quickstart.md).

Contents

1. [Installation and requirements](#1-installation-and-requirements)
2. [Python API: standardization](#2-python-api-standardization)
3. [`StandardizedAddress`](#3-standardizedaddress)
4. [ZIP / state policy](#4-zip--state-policy)
5. [Python API: batch and streaming](#5-python-api-batch-and-streaming)
6. [Python API: columnar integrations (Arrow, Polars, DuckDB)](#6-python-api-columnar-integrations)
7. [Python API: autocomplete](#7-python-api-autocomplete)
8. [Python API: international, postal codes, spatial](#8-python-api-international-postal-codes-spatial)
9. [Python API: scoring, delivery, risk, audit, cache, engine](#9-python-api-scoring-delivery-risk-audit-cache-engine)
10. [REST API](#10-rest-api)
11. [Command line](#11-command-line)
12. [Environment variables](#12-environment-variables)
13. [Client SDKs](#13-client-sdks)

---

## 1. Installation and requirements

Python **3.11 or newer**. The core package depends only on `requests`.

| Install | Adds | Needed for |
| :--- | :--- | :--- |
| `pip install -e .` (source checkout) | core | everything except the items below |
| `pip install -e ".[server]"` | `fastapi`, `uvicorn`, `pydantic`, `httpx` | REST API, `address-standardizer serve`, `create_app()` |
| `pip install -e ".[arrow]"` | `pyarrow`, `polars`, `duckdb` | `standardize_arrow`, `standardize_polars`, `register_duckdb_udfs` |
| `pip install -e ".[ml]"` | `usaddress` | optional statistical parser fallback |
| `pip install -e ".[benchmark]"` | `psutil` | `address-standardizer benchmark` |
| `pip install -e ".[dev]"` | `pytest`, `pytest-cov`, `ruff`, `usaddress`, `hypothesis`, `h3` | tests and linting |

Extras combine (`".[server,arrow]"`). After a PyPI release the same extras are available as
`pip install "address-standardizer[server]"`. Without the matching extra, `standardize_arrow`, `standardize_polars`,
`register_duckdb_udfs` and `create_app` are `None` in `address_standardizer` (the import is optional).

**Optional native module.** `_address_standardizer_rs` (Rust, PyO3) is not installed by `pip install`; build it with
`maturin develop --release` (needs a Rust toolchain). It **only accelerates American Soundex**
(`compute_soundex` / phonetic keys); parsing, normalization and key assembly are Python in all cases, so results do
not depend on it. `ADDRESS_STANDARDIZER_FORCE_PURE=1` disables it. See [`get_engine_info`](#engine-introspection).

The console script is `address-standardizer`; `python -m address_standardizer` is equivalent.

---

## 2. Python API: standardization

Everything below is importable from `address_standardizer`.

### `standardize_address`

```python
standardize_address(
    street1=None, street2=None, city=None, state=None, postal_code=None, country=None,
    is_vacant=None, enable_fuzzy=True, enable_geocoding=False, use_cache=True,
    allow_locality=False, finalize=True, correct_state_from_zip=None, **kwargs,
) -> StandardizedAddress
```

| Parameter | Default | Meaning |
| :--- | :--- | :--- |
| `street1` | `None` | Street line, **or a complete single-line address** (street, city, state, ZIP, even country). |
| `street2` | `None` | Secondary unit (Suite, Apt, Floor). |
| `city`, `state`, `postal_code` | `None` | Components. `state` may be a code or a name. |
| `country` | `None` | Country name or ISO code; omitted is treated as the US. |
| `is_vacant` | `None` | Caller-supplied vacancy flag copied to `vacant`. |
| `enable_fuzzy` | `True` | Closed-vocabulary typo recovery (edit distance <= 1 for suffixes and similar tokens). |
| `enable_geocoding` | **`False`** | Resolve coordinates with the offline spatial engine and fill `latitude`, `longitude`, `precision`, `accuracy_radius_meters`, `census_tract`, `fips_code`, `spatial_result`. (The REST API defaults this to `true`.) |
| `use_cache` | `True` | Use the process-wide L1/L2 result cache. |
| `allow_locality` | `False` | Permit a result with no street (city/state only). It is returned with `address_status == "locality_only"`. Also enabled by `ADDRESS_STANDARDIZER_ALLOW_LOCALITY=1`. |
| `finalize` | `True` | When `False`, skip confidence scoring, delivery intelligence, corporate risk, spatial resolution and the cache (fast normalization only). |
| `correct_state_from_zip` | `None` | `True`: replace a state that contradicts the ZIP with the ZIP's state. `False`: never. `None`: follow `ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP`. See [section 4](#4-zip--state-policy). |
| `**kwargs` | | Aliases: `street` (for `street1`), `vacant` (for `is_vacant`), and `allow_locality_only` / `allow_city_level` (for `allow_locality`). |

Inputs are coerced to text first: `None` and NaN become empty, integral floats lose their `.0`, bytes are decoded.
A field longer than 600 characters yields an `address_status == "parse_failed"` result.

Country handling: placeholders such as `N/A`, `none` or `unknown` mean "no country given" (a bare `NA` is Namibia, its ISO code). A country name that nothing recognises is reported as `ZZZ` (ISO 3166 "user-assigned") instead of being silently turned into `USA`; US evidence such as a US state with a ZIP still wins over an unreadable country name.

```python
>>> a = standardize_address("100 Wall St, Ste 400, New York, NY 10005")
>>> a.normalized_address_key
'100 WALL ST|STE 400|NEW YORK|NY|10005|USA'
```

### Key and helper functions

| Function | Signature | Notes |
| :--- | :--- | :--- |
| `generate_normalized_address_key` | `(street1=None, street2=None, city=None, state=None, postal_code=None, country=None, allow_locality=False, **kwargs) -> Optional[str]` | Suite-level key `STREET1\|STREET2\|CITY\|STATE\|ZIP5_OR_POSTAL\|COUNTRY_ALPHA3`. Extra kwargs go to `standardize_address`. |
| `generate_building_key` | `(street1=None, city=None, state=None, postal_code=None, country=None, allow_locality=False, **kwargs) -> Optional[str]` | Same key without the secondary unit. |
| `generate_phonetic_address_key` | `(street1, postal_or_zip='', city='') -> Optional[str]` | Soundex-based blocking key such as `100\|W400\|10005`. |
| `compute_soundex` | `(token) -> str` | American Soundex (`compute_soundex("Washington") == "W252"`). The only function the native module accelerates. |
| `is_registered_agent_hub_address` | `(street1, street2='', city='', state='', postal_code='', country='USA', raw_street='') -> bool` | |
| `clean_rooftop_address` | `(street_line) -> Optional[str]` | Street line without the secondary unit. |
| `normalize_country_code` / `normalize_country` | `(country_raw, state_raw=None, postal_raw=None, raw_street=None, city_raw=None) -> str` | ISO alpha-3 code (`"Germany"` -> `"DEU"`). |
| `normalize_us_state` | `(state_raw, zip5=None) -> str` | |
| `normalize_us_postal_code` | `(postal_raw) -> Tuple[str, str]` | `(formatted_postal_code, zip5)`. |
| `get_state_from_zip3` | `(zip5) -> Optional[str]` | State for the first three ZIP digits. |
| `num_to_ordinal` | `(n: int) -> str` | |

Typo-recovery helpers (`damerau_levenshtein_distance(s1, s2)`, `heal_street_suffix(token, max_distance=2)`,
`heal_city_token(city_raw, state=None, zip3=None, max_distance=2)`, `heal_street_name(name_raw, max_distance=1)`,
`heal_postal_code_transposition(postal_code, state=None)`, `heal_street_number_transposition(number_str, valid_ranges=None)`)
return the corrected string or `None` when no safe correction exists:

```python
>>> damerau_levenshtein_distance("kitten", "sitting")
3
>>> heal_city_token("Nwe York", "NY")
'NEW YORK'
```

---

## 3. `StandardizedAddress`

A dataclass returned by `standardize_address` and `batch_standardize` (`from address_standardizer import StandardizedAddress`).

**Constructor fields**

| Field | Type | Description |
| :--- | :--- | :--- |
| `street1` | `str` | Standardized street line (upper case, USPS Pub 28 abbreviations). |
| `street2` | `str` | Standardized secondary unit, `""` if none. |
| `city`, `state`, `postal_code` | `str` | Standardized components. |
| `country` | `str` | `"USA"` for US addresses; otherwise the ISO alpha-3 code (e.g. `"DEU"`). |
| `normalized_address_key` | `Optional[str]` | Suite-level matching key. |
| `building_key` | `Optional[str]` | Building-level matching key. |
| `phonetic_key` | `Optional[str]` | Phonetic blocking key. |
| `address_status` | `str` | `standardized`, `pending`, `parse_failed`, `manual_override`, `locality_only` or `city_level`. |
| `raw_street_address` | `str` | The input as received. |
| `is_us` | `bool` | |
| `is_private_residence` | `bool` | Privacy placeholders such as "Private Residence" are detected and not published. |
| `is_registered_agent_hub` | `bool` | |
| `dependent_locality`, `building_name` | `Optional[str]` | International fields. |
| `rooftop_address` | `Optional[str]` | Street line without the unit (`None` for PO boxes, private residences, locality-only and failed parses). |

**Computed properties** (set by `finalize=True` processing; all settable)

| Property | Type | Description |
| :--- | :--- | :--- |
| `confidence_score` | `Optional[float]` | Composite score 0.0 to 1.0. |
| `routing_tier` | `Optional[str]` | `AUTO_PASS`, `FUZZY_REVIEW` or `MANUAL_STEWARDSHIP`. |
| `failure_reason_codes` | `List[str]` | e.g. `ERR_ZIP_STATE_MISMATCH`, `WARN_STATE_CORRECTED_FROM_ZIP` (see below). |
| `deliverability` | `Deliverability` (a `str` enum) | `DELIVERABLE`, `REQUIRES_SECONDARY` or `UNDELIVERABLE`; use `.value` for the plain string. |
| `dpv_footnotes` | `List[str]` | `AA`, `A1`, `BB`, `CC`, `N1`, `M1`, `M3`, `P1`, `PB`, `RR`, `F1`, `G1`, `U1`. |
| `rdi` | `RDI` (a `str` enum) | `Residential`, `Commercial` or `Unknown`. |
| `cmra`, `is_cmra` | `bool` | Commercial mail receiving agency. |
| `vacant`, `is_vacant` | `bool` | |
| `secondary_prompt_required` | `bool` | `True` when a unit number is missing at a multi-unit building (`N1`). |
| `prompt_message` | `Optional[str]` | |
| `suggested_secondary_units` | `List[str]` | |
| `corporate_risk_score` | `float` | |
| `corporate_risk_flags` | `List[str]` | `RISK_CRA_CO_LOCATION`, `RISK_VIRTUAL_OFFICE`, `RISK_CMRA_MAIL_DROP`, `RISK_OFFSHORE_SECRECY_HUB`, `RISK_TRUST_FIDUCIARY`, `RISK_MISSING_SECONDARY_AT_HUB`, `RISK_DISGUISED_PMB`, `RISK_RESIDENTIAL_COMMERCIAL`. |
| `latitude`, `longitude` | `Optional[float]` | Only with `enable_geocoding=True`. |
| `precision` | `Optional[str]` | `CONFIRMED_ROOFTOP`, `RANGE_INTERPOLATED`, `POSTAL_CENTROID`, `MUNICIPAL_CENTROID` or `UNRESOLVED`. |
| `accuracy_radius_meters`, `census_tract`, `fips_code` | `Optional` | |
| `spatial_result` | `Optional[SpatialResolutionResult]` | |
| `country_iso3` | `str` | |
| `is_locality_only`, `is_city_level` | `bool` | |
| `full_rooftop_address` | `Optional[str]` | Single-line rooftop address (read-only). |
| `audit_record`, `cascade_result` | `Optional` | Attached when produced. |

**Reason codes** (`failure_reason_codes`): `ERR_ZIP_STATE_MISMATCH`, `ERR_MISSING_HOUSE_NUM`, `ERR_UNRESOLVED_SUFFIX`,
`ERR_AMBIGUOUS_DUAL_ADDR`, `ERR_DPV_UNCONFIRMED`, `ERR_PARSE_FAILED`, `ERR_EMPTY_ADDRESS`, `ERR_EMPTY_STREET`,
`NO_STREET_NUMBER`, `WARN_STATE_CORRECTED_FROM_ZIP`, `WARN_CRA_HUB_DETECTED`, `WARN_PMB_DISGUISED`, `WARN_RESIDENTIAL_COMM`,
`WARN_TYPO_HEALED`, `WARN_CMRA_DETECTED`, `WARN_MISSING_SECONDARY_UNIT`, `WARN_VACANT_DELIVERY_POINT`,
`WARN_LANDMARK_CAMPUS_PREMISE`, `WARN_LOCALITY_ONLY`.

**Routing tiers.** Composite score >= 0.95 with no `ERR_*` code is `AUTO_PASS`; >= 0.80 is `FUZZY_REVIEW`; lower, or a
missing house number, or a failed parse, is `MANUAL_STEWARDSHIP`.

**Methods**

- `as_dict(include_metadata=False, include_rooftop=False) -> dict`. The base dict has `street1`, `street2`, `city`,
  `state`, `postal_code`, `country`, `normalized_address_key`, `building_key`, `phonetic_key`, `address_status`,
  `raw_street_address`, `is_us`, `is_private_residence`, `is_registered_agent_hub`. `include_rooftop=True` adds
  `rooftop_address` and `full_rooftop_address`. `include_metadata=True` also adds `is_locality_only`, `is_city_level`,
  `dependent_locality`, `building_name`, `confidence_score`, `routing_tier`, `failure_reason_codes`, `rdi`, `cmra`,
  `is_cmra`, `vacant`, `is_vacant`, `dpv_footnotes`, `corporate_risk_score`, `corporate_risk_flags`, `audit_id` (when an
  audit record exists), `cascade` (when present), `deliverability`, `secondary_prompt_required`, `prompt_message`,
  `suggested_secondary_units`, `latitude`, `longitude`, `precision`, `accuracy_radius_meters`, `census_tract`,
  `fips_code`, `spatial_result` and `country_iso3`. `rdi` and `deliverability` are `str` enums (they compare equal to,
  and JSON-serialize as, plain strings). **If the geocode is `UNRESOLVED`, `latitude`, `longitude` and
  `accuracy_radius_meters` are `None`**, never `0.0`.
- `as_extended_dict()`: `as_dict(include_metadata=True)`.
- `format_upu(recipient=None, include_country_name=True) -> str`: Universal Postal Union (UPU S42) envelope layout.

---

## 4. ZIP / state policy

When a US ZIP belongs to a different state than the one supplied:

- **Default.** The supplied state is kept; the address stays `address_status == "standardized"`. The result carries
  `ERR_ZIP_STATE_MISMATCH` in `failure_reason_codes`, the DPV footnote `A1`, and `deliverability == UNDELIVERABLE`. The
  `A1`-driven `UNDELIVERABLE` applies only when a ZIP is present but malformed or belonging to another state; an absent
  ZIP does not trigger it.
- **Opt-in correction.** With `correct_state_from_zip=True` (or the environment variable), a recognizable US state that
  differs from the state of a valid 5-digit (or ZIP+4) ZIP is replaced with the ZIP's state, and
  `WARN_STATE_CORRECTED_FROM_ZIP` is reported. Missing or unrecognized states and non-US addresses are untouched.
  Correction works when `state` and `postal_code` are supplied as separate fields, and also when both are empty and the
  single-line `street1` ends with `<2-letter state> <ZIP>` (for example `"100 Main St, Austin, CA 78701"`; the state in
  the text is replaced). For other free-form shapes the state is kept and `ERR_ZIP_STATE_MISMATCH` is still reported.

| Surface | Control |
| :--- | :--- |
| `standardize_address`, `batch_standardize`, `stream_standardize_csv`, `stream_standardize_jsonl`, `stream_standardize_json` | keyword `correct_state_from_zip` (`None` = environment). For the batch functions the option is applied by setting the environment variable for the duration of the call. |
| `standardize_arrow`, `standardize_polars`, DuckDB UDFs | environment variable only |
| REST `POST /v1/standardize` | body field `correct_state_from_zip` |
| REST `POST /v1/batch` | top-level body field (object form) and per-item field |
| CLI `parse`, `batch`, shorthand | `--correct-state-from-zip` |
| Everything | `ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP` = `1`, `true`, `yes` or `on` |

An explicit `correct_state_from_zip=False` overrides the environment variable.

---

## 5. Python API: batch and streaming

### `batch_standardize`

```python
batch_standardize(addresses, enable_fuzzy=True, enable_geocoding=False, country=None,
                  batch_size=1000, use_cache=False, *, correct_state_from_zip=None, **kwargs)
    -> Iterator[StandardizedAddress]
```

A **generator**. `addresses` is an iterable of strings and/or dicts. Dict keys are matched with aliases:
`street1` / `street` / `address` / `address1`; `street2` / `suite` / `apt` / `unit` / `address2`; `city`;
`state` / `province`; `postal_code` / `zip` / `zipcode` / `postcode`; `country`; and `is_vacant` / `vacant`.
`country` is the default for items that carry none. `use_cache=False` keeps memory bounded; with `use_cache=True` the
cache is cleared every `batch_size` items. Extra `kwargs` (for example `allow_locality=True`) go to
`standardize_address`.

### File streaming

```python
stream_standardize_csv(input_path, output_path, chunk_size=5000, max_workers=2,
    street_col="street1", street2_col="street2", city_col="city", state_col="state",
    zip_col="postal_code", country_col="country", mapping=None, geocode=False, geocoder=None,
    include_confidence=False, audit_csv_path=None, enable_geocoding=False, spatial_db=None,
    include_intl=False, country=None, *, correct_state_from_zip=None) -> int
```

`stream_standardize_jsonl(...)` and `stream_standardize_json(...)` have the identical signature. All three return the
number of rows processed.

- Output keeps every input column and appends `std_street1`, `std_street2`, `std_city`, `std_state`,
  `std_postal_code`, `std_country`, `rooftop_address`, `std_rooftop_address`, `normalized_address_key`, `building_key`,
  `phonetic_key`, `is_registered_agent_hub`, `is_private_residence`, `address_status`. Option columns:
  `include_confidence` adds `confidence_score` and `routing_tier`; `include_intl` adds `std_dependent_locality`,
  `std_building_name`, `std_country_iso3`; `geocode=True` (US Census API, needs network) adds `latitude`, `longitude`,
  `geocode_precision`; `enable_geocoding=True` (offline engine, optionally `spatial_db=<path>`) adds `latitude`,
  `longitude`, `geocode_precision`, `spatial_precision`, `spatial_source`, `accuracy_radius_meters`, `h3_r10_index`.
  CSV cells are text (booleans appear as `True` / `False`); JSONL and JSON output write the boolean flags
  (`is_registered_agent_hub`, `is_private_residence`) as real JSON booleans.
- `mapping` renames columns, e.g. `{"address": "street1", "zip": "postal_code"}`; it takes precedence over the
  `*_col` arguments. `audit_csv_path` writes the stewardship records produced while processing.
- Input and output (and audit) paths must be distinct files. Output is written atomically via a temporary file.
- `max_workers` is capped at 2. Worker processes are used, so **scripts that call these functions must be guarded
  with `if __name__ == "__main__":`** on Windows and macOS (spawn start method), or they will hang re-importing.
- CSV and JSONL are streamed in constant memory; `stream_standardize_json` reads the whole file into memory.

Lower-level helpers: `chunk_generator(reader, chunk_size=5000)`, `buffered_chunk_generator(reader, chunk_size=5000)` and
`process_chunk(chunk, street_col=..., ..., include_confidence=False, include_intl=False, country=None)`.

---

## 6. Python API: columnar integrations

Require the `arrow` extra.

```python
standardize_arrow(table_or_batch, street1_col="street1", street2_col=None, city_col="city",
                  state_col="state", postal_code_col="postal_code", country_col=None,
                  enable_geocoding=False, enable_fuzzy=True, allow_locality=False,
                  output_prefix="std_", as_struct=False)
standardize_polars(df, <same keyword arguments>)      # DataFrame or LazyFrame in, same kind out
register_duckdb_udfs(connection=None)                  # returns the connection
```

- `standardize_arrow` accepts a `pyarrow.Table` or `RecordBatch` and returns the same kind with new columns appended. A
  missing optional column triggers a warning and is treated as empty; a missing `street1_col` raises `ValueError`.
- Appended columns (prefix `std_` by default): `street1`, `street2`, `city`, `state`, `postal_code`, `country`,
  `normalized_address_key`, `building_key`, `phonetic_key`, `address_status`, `deliverability`, `latitude`, `longitude`,
  `precision`, `accuracy_radius_meters`, `census_tract`, `fips_code`, `confidence_score`, `routing_tier`, `rdi`, `cmra`.
  With `as_struct=True` a single struct column `standardized_address` is appended with the same fields (no prefix).
- There is no `correct_state_from_zip` parameter here; use the environment variable.
- `register_duckdb_udfs` registers: `standardize_address(street1, city, state, postal_code)`,
  `standardize_address_full(street1, street2, city, state, postal_code, country)` and
  `standardize_address_text(address_text)` (all return a STRUCT with `street1, street2, city, state, postal_code,
  country, normalized_address_key, building_key, address_status, deliverability, latitude, longitude, precision,
  confidence_score, rdi, cmra`; these three geocode); and the VARCHAR functions `standardize_address_key(street1, city,
  state, postal_code)`, `standardize_address_key_text(address_text)`, `standardize_deliverability(street1, city, state,
  postal_code)` and `standardize_deliverability_text(address_text)`. With no argument it registers on DuckDB's default
  connection.

```python
>>> con = duckdb.connect(); register_duckdb_udfs(con)
>>> con.sql("SELECT standardize_address_key_text('100 Wall St, New York, NY 10005')").fetchall()
[('100 WALL ST||NEW YORK|NY|10005|USA',)]
```

---

## 7. Python API: autocomplete

```python
autocomplete_address(query, max_results=5, state_filter=None, client_lat=None, client_lon=None,
                     radius_km=None, latitude=None, longitude=None, radius_miles=None,
                     typo_tolerance=True, engine=None) -> List[AutocompleteSuggestion]
```

`latitude`/`longitude` (or the `client_*` aliases) bias ranking by proximity and fill `distance_meters`;
`radius_miles` / `radius_km` bound the search. `engine` selects a custom `AutocompleteEngine(seed=True)`.

`AutocompleteSuggestion` fields: `text`, `street1`, `street2`, `city`, `state`, `postal_code`, `country` (`"USA"`),
`secondary_prompt_required`, `suggested_secondary_units`, `highlight_ranges`, `score`, `prompt_message`, `latitude`,
`longitude`, `distance_meters`; property `street_line` (= `street1`); `as_dict()`.

```python
>>> s = autocomplete_address("100 wall", max_results=1)[0]
>>> s.text, s.secondary_prompt_required, s.suggested_secondary_units
('100 WALL ST, NEW YORK, NY 10005', True, ['STE 400', 'STE 800', 'FL 12', 'FL 20'])
```

---

## 8. Python API: international, postal codes, spatial

**International** (`address_standardizer`)

- `validate_postal_code(postal_code, country_code=None, return_details=False, *, country=None) -> bool | PostalValidationResult`.
  `PostalValidationResult` fields: `is_valid`, `postal_code`, `country_code` (alpha-3), `reason`, `formatted_code`,
  `is_non_postal_country`. Countries without postal codes (for example the UAE) validate gracefully.
- `extract_postal_code(text, country_hint=None, *, country=None) -> Optional[str]`.
- `format_upu_address(parsed, recipient=None, include_country_name=True) -> str` (also `StandardizedAddress.format_upu`).
- `CountryRegistry` (class methods): `get(query) -> Optional[CountryInfo]`, `detect_country(text, country_hint=None)`,
  `has_postal_codes(query) -> bool`, `all_countries() -> List[CountryInfo]` (249), `all_iso3() -> Set[str]`.
  `CountryInfo` fields: `alpha2`, `alpha3`, `numeric`, `name`, `native_names`, `aliases`, `has_postal_codes`, `region`.

**Spatial** (offline, SQLite R\*Tree, no network)

- `SpatialEngine(db_path=None, seed=True)`: `resolve(address) -> SpatialResolutionResult`, `query_radius(lon, lat,
  radius_meters=1000.0, limit=50)`, `query_bounding_box(min_lon, min_lat, max_lon, max_lat, limit=100)`,
  `query_street_segments(...)`, `insert_point(...)`, `insert_street_segment(...)`, `insert_postal_centroid(...)`,
  `insert_municipal_centroid(...)`, `hot_swap(new_db_path)`, `count()`, `close()`. `db_path=None` means in-memory;
  with `seed=True` an empty database receives a small built-in seed set.
- `resolve` runs a 4-stage cascade: (1) rooftop / parcel match, (2) street-range interpolation, (3) postal centroid,
  (4) municipal / state centroid; otherwise `UNRESOLVED` (stage 0).
- `SpatialResolutionResult` fields: `latitude`, `longitude`, `precision`, `accuracy_radius_meters`, `stage`, `source`,
  `h3_res10`, `parcel_id`, `execution_time_ms`, `metadata`; `as_dict()` reports `null` coordinates for `UNRESOLVED`.
  (The attributes themselves hold `0.0` for an unresolved result; use `as_dict()` or check `precision`.)
- `get_default_spatial_engine()` / `resolve_spatial_coordinates(address)`: a process-wide engine. It opens the file named
  by `SPATIAL_DB_PATH`, else `data/spatial_index.db` if it exists, else uses an in-memory seeded database.
- `lat_lng_to_h3(lat, lng, resolution=10) -> str`. More H3 helpers (`h3_to_int`, `int_to_h3`, `is_valid_h3`, `k_ring`,
  `h3_distance`, `h3_to_parent`) and ingestors (`OpenAddressesIngestor`,
  `TigerLineIngestor`, `OsmBuildingIngestor`, `build_spatial_database`) are in `address_standardizer.spatial`.
- `OfflineReferenceIndex`, `get_default_offline_index()`, `resolve_offline_coordinates(address)`,
  `validate_parcel_offline(address)` expose the offline rooftop reference index (`RooftopRecord`, `ParcelValidationResult`).
- `CensusGeocoder(timeout_seconds=45)` calls the US Census geocoder over the network (the only networked component);
  `VerificationCascade` / `resolve_verification_cascade(...)` combine the offline index and the Census geocoder
  (`CascadeResult`, `CascadePrecision`); `get_fallback_centroid(zip5=None, state=None)` returns a `(lat, lon)` tuple.

---

## 9. Python API: scoring, delivery, risk, audit, cache, engine

- **Confidence.** `compute_confidence_score(std_address, raw_input=None, dpv_confirmed=None, cascade_precision=None) ->
  ConfidenceResult` with `composite_score`, `routing_tier`, `s_parse`, `s_ref_match`, `s_geo`, `s_cross_field`,
  `failure_reason_codes`. `ConfidenceScorer` is the underlying class (weights 0.35 parse, 0.35 reference match, 0.15
  geo, 0.15 cross-field). `RoutingTier` holds the three tier names.
- **Delivery intelligence.** `evaluate_delivery_intelligence(std_address=None, raw_input=None, is_vacant_override=None, *,
  street1=None, ..., address_status=None) -> DeliveryIntelligenceResult` (`rdi`, `cmra`, `vacant`, `dpv_footnotes`,
  `deliverability`, `secondary_prompt_required`, `prompt_message`, `suggested_secondary_units`). Constants: `DPVFootnote`,
  `RDI`.
- **Corporate registry and risk.** `lookup_corporate_registry(street1, street2='', city='', state='', postal_code='',
  country='USA', raw_street='') -> Optional[CorporateRegistryEntry]`; `evaluate_corporate_risk(std_address, raw_input=None)
  -> (score, flags)`; `can_safely_merge_corporate_entities(addr1, addr2) -> (bool, reason)`; `RegistryCategory`,
  `CorporateRiskFlag`, `CURATED_CORPORATE_REGISTRY`.
- **Audit ledger.** `get_audit_ledger() -> StewardshipAuditLedger` is a process-wide, **in-memory** ledger
  (`StewardshipAuditLedger(db_path=None, max_rows=None)`; a file-backed ledger keeps everything, the in-memory one is
  capped by `ADDRESS_STANDARDIZER_AUDIT_MAX_ROWS`, default 100000). Low-confidence results (those that route to manual
  stewardship) create `PENDING` records automatically. `routing_tier` describes parse/deliverability confidence, while a
  record's `review_status` is the stewardship queue: a registered-agent hub address can be `AUTO_PASS` (it parsed and
  verified cleanly) yet still be `PENDING` because the hub flag needs a human decision. The two are deliberately independent. Methods: `list_records(review_status=None, action_type=None,
  limit=None)`, `get_record(audit_id)`, `apply_manual_override(audit_id, steward_id, overrides, commentary="")`,
  `history(audit_id)`, `export(format="dict"|"json"|"sql")`, `clear()`. `ActionType`: `AUTO_PASS`, `AUTO_HEAL`,
  `MANUAL_OVERRIDE`, `REJECT_UNPARSEABLE`. `ReviewStatus`: `PENDING`, `APPROVED`, `MODIFIED`, `REJECTED`.

  ```python
  standardize_address("xyz", city="Nowhere")
  ledger = get_audit_ledger()
  for rec in ledger.list_records(review_status="PENDING"):
      print(rec.action_type, rec.review_status, rec.failure_reason_codes, rec.confidence_score)
  done = ledger.apply_manual_override(rec.audit_id, steward_id="jdoe", overrides={"street1": "1 MAIN ST"}, commentary="fixed by hand")
  print(done.review_status, done.reviewed_by, done.final_committed_payload["street1"])
  ```

  ```text
  REJECT_UNPARSEABLE PENDING ['ERR_MISSING_HOUSE_NUM'] 0.4375
  MODIFIED jdoe 1 MAIN ST
  ```

- **Cache.** A two-tier cache (L1 in-memory LRU, L2 SQLite) is used by `standardize_address` when `use_cache=True`.
  `configure_cache(enabled=True, l1_maxsize=50000, l2_db_path=None, l2_max_entries=50000) -> MultiTierCache`,
  `get_default_cache()`, `clear_cache()`, `get_cache_stats() -> dict`, `make_cache_key(...)`; classes `MultiTierCache`,
  `LRUCache`, `SQLiteCache`.

<a id="engine-introspection"></a>
- **Engine introspection.** `get_engine_info() -> dict` with `engine` (`"PurePythonCore"` or `"Rust_PyO3"`), `is_native`,
  `native_available`, `force_pure_python`, `version`, `native_functions`, `throughput_sla_target`, `simd_acceleration`,
  `zero_copy_slices`. `is_native_available()`, `is_using_native()`, `standardize_record_dispatch(...)`,
  `standardize_batch_dispatch(records, chunk_size=5000, **kwargs)`.

---

## 10. REST API

Install the `server` extra and start the service with `address-standardizer serve` (binds **127.0.0.1:8000** by default;
`--host 0.0.0.0` to expose it), or `python -m uvicorn address_standardizer.server:app --port 8000`, or embed it with
`from address_standardizer import create_app`. Unless `ADDRESS_STANDARDIZER_DISABLE_DOCS` is set, OpenAPI documents are
served at `/docs`, `/redoc` and `/openapi.json`. Responses carry an `X-Response-Time-Ms` header.

| Method and path | Purpose |
| :--- | :--- |
| `POST /v1/standardize` | Standardize one address |
| `POST /v1/batch` | Standardize many addresses (JSON array response or NDJSON stream) |
| `POST /v1/autocomplete` | Typeahead suggestions (JSON body) |
| `GET /v1/autocomplete` | Typeahead suggestions (query string) |
| `GET /health` | Health, version, engine and cache telemetry |
| `GET /metrics` | Request metrics (JSON or Prometheus text) |

### `POST /v1/standardize`

Request body (`application/json`; unknown fields are ignored):

| Field | Type | Default | Notes |
| :--- | :--- | :--- | :--- |
| `address` | string | `null` | Single-line address. Used as `street1` when `street1` is empty. |
| `street1`, `street2`, `city`, `state`, `postal_code` | string | `null` | Components. |
| `country` | string | `"USA"` | Name or ISO code. |
| `enable_geocoding` | bool | **`true`** | Offline geocoding. |
| `enable_fuzzy` | bool | `true` | Typo recovery. |
| `allow_locality` | bool | `false` | Allow locality-only results. |
| `correct_state_from_zip` | bool | `false` | See [section 4](#4-zip--state-policy). |
| `include_metadata` | bool | `true` | When `false`, only the base fields plus `rooftop_address` and `full_rooftop_address` are returned. |

Response `200`: the object produced by `StandardizedAddress.as_dict(include_metadata=include_metadata, include_rooftop=True)`
(field list in [section 3](#3-standardizedaddress)), as JSON. Enum values are plain strings. Unresolved geocodes have
`"latitude": null`, `"longitude": null`, `"accuracy_radius_meters": null` (and `"precision": "UNRESOLVED"`).

```bash
curl -s -X POST localhost:8000/v1/standardize -H 'Content-Type: application/json' \
  -d '{"street1":"100 Main St","city":"Austin","state":"CA","postal_code":"78701","include_metadata":false}'
```

```json
{"street1":"100 MAIN ST","street2":"","city":"AUSTIN","state":"CA","postal_code":"78701","country":"USA","normalized_address_key":"100 MAIN ST||AUSTIN|CA|78701|USA","building_key":"100 MAIN ST||AUSTIN|CA|78701|USA","phonetic_key":"100|M500|78701","address_status":"standardized","raw_street_address":"100 Main St, Austin, CA, 78701, USA","is_us":true,"is_private_residence":false,"is_registered_agent_hub":false,"rooftop_address":"100 MAIN ST","full_rooftop_address":"100 MAIN ST, AUSTIN, CA 78701"}
```

An address that cannot be resolved to a location (`enable_geocoding` true):

```bash
curl -s -X POST localhost:8000/v1/standardize -H 'Content-Type: application/json' \
  -d '{"street1":"xyz","city":"Nowhere","enable_geocoding":true}'
```

```text
{"street1":"XYZ", ... "confidence_score":0.4375,"routing_tier":"MANUAL_STEWARDSHIP","failure_reason_codes":["ERR_MISSING_HOUSE_NUM"], ... "deliverability":"UNDELIVERABLE", ... "latitude":null,"longitude":null,"precision":"UNRESOLVED","accuracy_radius_meters":null,"census_tract":null,"fips_code":null,"spatial_result":{"latitude":null,"longitude":null,"precision":"UNRESOLVED","accuracy_radius_meters":null,"stage":0,"source":"NONE","h3_res10":"","parcel_id":null,...},"country_iso3":"USA"}
```

### `POST /v1/batch`

Accepted request bodies:

1. A JSON array: `["100 Wall St, New York, NY 10005", {"street1": "350 5th Ave", "city": "New York", "state": "NY"}]`
2. A JSON object `{"addresses": [...], "enable_geocoding": true, "enable_fuzzy": true, "allow_locality": false,
   "correct_state_from_zip": false}`. The four flags (all booleans, else HTTP 400) are defaults for every item.
3. NDJSON (`Content-Type: application/x-ndjson` or `application/jsonlines`): one JSON value per line. A line may be a
   string or an object.

Each item is a string (a single-line address) or an object with the `/v1/standardize` fields (`address`, `street1`,
`street2`, `city`, `state`, `postal_code`, `country`, `enable_geocoding`, `enable_fuzzy`, `allow_locality`,
`correct_state_from_zip`, `include_metadata`); per-item values override the defaults. Only those field names are read
(for example use `postal_code`, not `zip`).

Responses:

- **Default**: HTTP 200, a JSON array with one object per input, in order, shaped like the `/v1/standardize` response.
  Processing runs off the event loop. An item with invalid field types fails the whole request with HTTP 400
  (`addresses[i] has invalid fields: ...`).
- **NDJSON stream** (`Accept: application/x-ndjson` or `application/jsonlines`, `?format=ndjson`, or an NDJSON
  request body): `Content-Type: application/x-ndjson`, one result object per line, in order. A record that fails
  yields a generic error line and the stream continues: `{"error": "invalid record", "index": N}` for a malformed or
  invalid record, or `{"error": "engine failure", "index": N}` for an internal failure. `index` is the zero-based
  position of the record; the error never echoes the input.

```bash
printf '{"address":"100 Wall St, New York, NY 10005","enable_geocoding":false}\nnot json\n{"enable_fuzzy":"maybe"}\n' \
  | curl -s -X POST localhost:8000/v1/batch -H 'Content-Type: application/x-ndjson' --data-binary @-
```

```text
{"street1": "100 WALL ST", "street2": "", "city": "NEW YORK", "state": "NY", "postal_code": "10005", "country": "USA", ...
{"error": "invalid record", "index": 1}
{"error": "invalid record", "index": 2}
```

**Limits** (both applied to every request form, including NDJSON streaming):

| Limit | Default | Setting | Result when exceeded |
| :--- | :--- | :--- | :--- |
| Items per request | 10,000 | `ADDRESS_STANDARDIZER_MAX_BATCH` | HTTP **413** |
| Request body | 16 MiB | `ADDRESS_STANDARDIZER_MAX_BODY_BYTES` (minimum 1024) | HTTP **413** |

The body limit is checked from `Content-Length` and again while reading; it is enforced on `/v1/batch` only.
Split large jobs into several requests.

### `POST /v1/autocomplete` and `GET /v1/autocomplete`

| POST body field | GET query parameter | Type | Default | Constraint |
| :--- | :--- | :--- | :--- | :--- |
| `query` | `q` | string | required | at least 1 character |
| `max_results` | `limit` | integer | 10 | 1 to 50 |
| `state_filter` | `state` | string | `null` | state code |
| `latitude` | `lat` | number | `null` | -90 to 90 |
| `longitude` | `lon` | number | `null` | -180 to 180 |
| `radius_miles` | `radius_miles` | number | `null` | greater than 0, at most 25000 |

Response `200`: `{"suggestions": [...], "count": N}`. Each suggestion has `text`, `street_line`, `city`, `state`,
`postal_code`, `secondary_prompt_required`, `suggested_secondary_units`, `prompt_message`, `latitude`, `longitude`,
`distance_meters` (set when a client position is given).

```bash
curl -s -X POST localhost:8000/v1/autocomplete -H 'Content-Type: application/json' \
  -d '{"query":"100 wall","max_results":1,"latitude":40.7,"longitude":-74.0,"radius_miles":10}'
```

```json
{"suggestions":[{"text":"100 WALL ST, NEW YORK, NY 10005","street_line":"100 WALL ST","city":"NEW YORK","state":"NY","postal_code":"10005","secondary_prompt_required":true,"suggested_secondary_units":["STE 400","STE 800","FL 12","FL 20"],"prompt_message":"Requires Suite / Apartment Number","latitude":40.7061,"longitude":-74.006,"distance_meters":846.1}],"count":1}
```

### `GET /health`

```json
{"status":"healthy","version":"3.3.0","engine":{"native_acceleration":false,"using_native":false,"capabilities":{"engine":"PurePythonCore",...},"cache":{"enabled":true,"l1":{...},"l2":{...},...}},"uptime_seconds":4.42}
```

### `GET /metrics`

JSON by default: `uptime_seconds`, `total_requests`, `total_addresses_processed`, `average_latency_ms`,
`requests_by_endpoint` (route templates, so labels stay bounded) and `requests_by_status`. With `?format=prometheus`
or an `Accept` header containing `text/plain`, Prometheus text exposition (`address_standardizer_requests_total`,
`address_standardizer_addresses_processed_total`, `address_standardizer_uptime_seconds`,
`address_standardizer_avg_latency_ms`, `address_standardizer_endpoint_requests_total{endpoint=...}`,
`address_standardizer_status_requests_total{code=...}`). Note that `total_addresses_processed` currently increments once
per HTTP request, not once per address in a batch.

### Errors

Errors use FastAPI's `{"detail": ...}` body.

| Status | When | Example body |
| :--- | :--- | :--- |
| 400 | Malformed JSON; body is neither array nor `{"addresses": [...]}`; `addresses` not an array; an item that is not a string/object; a flag that is not a boolean; an item with invalid field types | `{"detail":"Invalid JSON body"}`, `{"detail":"addresses[0] must be a string or an object, got int"}` |
| 404 | Unknown path | `{"detail":"Not Found"}` |
| 413 | Too many items or body too large (`/v1/batch`) | `{"detail":"Batch of 4 addresses exceeds the limit of 3; split it or use NDJSON streaming in smaller requests."}` |
| 422 | Request fails schema validation (`/v1/standardize`, `/v1/autocomplete`) | `{"detail":[{"type":"bool_parsing","loc":["body","enable_fuzzy"],"msg":"Input should be a valid boolean, unable to interpret input","input":"maybe"}]}` |
| 500 | Engine failure | `{"detail":"Standardization engine failure"}` |

**CORS.** By default any origin is allowed, without credentials. Setting `ADDRESS_STANDARDIZER_CORS_ORIGINS` to a
comma-separated list restricts the allowed origins and enables credentialed requests for them.

---

## 11. Command line

```text
address-standardizer [--format {json,text,table,csv,upu}] [--country COUNTRY]
                     {parse,batch,benchmark,spatial,audit,cache,autocomplete,validate-postal,serve} ...
```

**Shorthand.** With no subcommand, the remaining arguments are a single address (`address-standardizer "100 Wall St, New
York, NY 10005"`), or, when stdin is piped, one address per line. Only `--format`, `--country/-c` and
`--correct-state-from-zip` are accepted in this form; any other option is an error (use `parse`).

| Command | Synopsis |
| :--- | :--- |
| `parse` | `parse [address ...] [--street1 S] [--street2 S] [--city C] [--state S] [--zip Z] [--country/-c C] [--format {json,text,table,csv,upu}] [--enable-geocoding] [--spatial-db/--db PATH] [--geocode] [--cascade] [--confidence] [--audit] [--audit-db PATH] [--no-cache] [--correct-state-from-zip]` |
| `batch` | `batch input_csv output_csv [--format {auto,csv,jsonl,ndjson,json}] [--mapping JSON_OR_FILE] [--street-col C] [--street2-col C] [--city-col C] [--state-col C] [--zip-col C] [--country-col C] [--country/-c C] [--chunk-size N] [--workers N] [--enable-geocoding] [--spatial-db/--db PATH] [--include-intl] [--geocode] [--confidence] [--audit-csv PATH] [--no-cache] [--correct-state-from-zip]` |
| `benchmark` | `benchmark [--dataset {domestic,multi_national,all,FILE}] [--iterations N] [--format {text,json}]` |
| `spatial build` | `spatial build [--output/--output-db/--db/--spatial-db PATH] [--openaddresses CSV] [--tiger CSV] [--osm GEOJSON]` (default output `data/spatial_index.db`) |
| `spatial lookup` | `spatial lookup [address ...] [--address A] [--lat L --lon L [--radius METERS]] [--bbox min_lon,min_lat,max_lon,max_lat] [--min-lat/--min-lon/--max-lat/--max-lon V] [--limit N] [--spatial-db/--db PATH] [--format {json,text}]` |
| `spatial info`, `spatial stats` | `spatial info [--spatial-db/--db PATH] [--format {text,json}]` (`stats` is an alias) |
| `audit` | `audit [--list] [--status {PENDING,APPROVED,MODIFIED,REJECTED}] [--export {json,sql,dict}] [--clear] [--audit-db PATH]` |
| `cache` | `cache [--stats] [--clear]` (prints stats unless `--clear`) |
| `autocomplete` | `autocomplete QUERY [--limit 1-50] [--state S] [--format {json,text}]` (default limit 5, default format `text`) |
| `validate-postal` | `validate-postal [code_or_text ...] [--country/-c C] [--format {json,text,table}]` (stdin supported; `-` reads stdin) |
| `serve` | `serve [--host HOST] [--port PORT] [--workers N] [--reload]` (default `127.0.0.1:8000`, 1 worker) |

Notes:

- `parse` accepts a free-form address, or components via `--street1/--street2/--city/--state/--zip`. With piped stdin
  (or `-` as the address), each line is standardized. `--enable-geocoding` uses the offline spatial engine; `--geocode`
  and `--cascade` use the US Census API (network). JSON output (the default) is indented; its keys are those of
  `as_dict()` without metadata, plus `country_iso3`, any `dependent_locality`/`building_name`, and the options you request
  (`--confidence` adds `confidence_score`, `routing_tier`, `failure_reason_codes`; `--audit` adds `audit_record`; geocoding adds
  `latitude`, `longitude`, `spatial_precision`, `geocode_precision`, `spatial_source`, `accuracy_radius_meters`,
  `h3_r10_index`, `spatial_result`).
- `batch` takes **positional** `input_csv` and `output_csv`. The format is inferred from either file's extension when
  `--format auto`: `.jsonl`/`.ndjson` is JSONL, `.json` is JSON, anything else is CSV. `--workers` is capped at 2.
  `--mapping` is a JSON object or a path to a JSON file. It prints `Standardized N record(s) -> OUT`.
- `benchmark` runs the harness in `benchmarks/run_benchmarks.py` and works only from a source checkout (not from an
  installed wheel). It needs the `benchmark` extra (`psutil`). `text` prints a throughput and accuracy report; the
  throughput SLA rows depend on the machine and can report FAIL on slow hardware.
- `audit` reads the default in-memory ledger, which is empty at the start of every CLI process. Pass
  `--audit-db PATH` (or set `ADDRESS_STANDARDIZER_AUDIT_DB`) to `parse --audit` and `audit` to keep records in a SQLite
  file that persists between invocations.
- `cache --stats` prints the L1/L2 statistics as JSON.
- `serve` requires the `server` extra (`uvicorn`).
- Errors from bad paths or malformed rows print `Error: ...` to stderr and exit with status 2.

---

## 12. Environment variables

| Variable | Effect | Default |
| :--- | :--- | :--- |
| `ADDRESS_STANDARDIZER_MAX_BATCH` | Maximum addresses per `/v1/batch` request; exceeding returns HTTP 413. Invalid values fall back to the default; minimum 1. | `10000` |
| `ADDRESS_STANDARDIZER_MAX_BODY_BYTES` | Maximum `/v1/batch` body size in bytes; exceeding returns HTTP 413. Minimum 1024. | `16777216` |
| `ADDRESS_STANDARDIZER_CORS_ORIGINS` | Comma-separated CORS origin allow-list; also enables credentialed CORS for those origins. | unset: `*`, no credentials |
| `ADDRESS_STANDARDIZER_DISABLE_DOCS` | `1`, `true` or `yes` (case-insensitive) disables `/docs`, `/redoc` and `/openapi.json`. | docs on |
| `ADDRESS_STANDARDIZER_FORCE_PURE` | `1`, `true`, `yes` or `on` disables the optional native module (read at import time). | unset |
| `ADDRESS_STANDARDIZER_AUDIT_DB` | Path of a SQLite audit ledger used by the CLI `parse --audit` / `audit` commands when `--audit-db` is not given. | unset (in-memory) |
| `ADDRESS_STANDARDIZER_AUDIT_MAX_ROWS` | Row cap of the default in-memory audit ledger. | `100000` |
| `ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP` | `1`, `true`, `yes` or `on` turns on ZIP-based state correction when no explicit argument is given. The CLI flag sets it for the process. | off |
| `ADDRESS_STANDARDIZER_ALLOW_LOCALITY` | The value `1` makes every `standardize_address` call allow locality-only results. | off |
| `SPATIAL_DB_PATH` | Path of the SQLite spatial database the default spatial engine opens. | unset |

---

## 13. Client SDKs

TypeScript, .NET and Go clients for the REST API live under [`sdks/`](../sdks/README.md); see that README and the
README in each SDK directory for installation and usage.

---

Address Standardizer is owned and maintained by HobbyHabbit LLC under the MIT License; see [LICENSE](../LICENSE).
