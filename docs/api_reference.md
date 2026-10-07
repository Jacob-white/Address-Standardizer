# Address Standardizer API Reference 📖

Complete, exhaustive reference documentation for the **Address Standardizer** platform across Python, Native FFI, CLI, and HTTP microservice interfaces.

---

# Table of Contents
1. [Volume 1: Core Normalization & Data Models (`address_standardizer.models`, `standardizer`)](#volume-1-core-normalization--data-models)
2. [Volume 2: Universal International Engine (`address_standardizer.international`)](#volume-2-universal-international-engine)
3. [Volume 3: Geospatial Subsystem & Offline Rooftop Indexing (`address_standardizer.spatial`, `geocoder`, `offline_index`)](#volume-3-geospatial-subsystem--offline-rooftop-indexing)
4. [Volume 4: Corporate Risk & FinCEN Anti-Fraud Invariants (`address_standardizer.registry`)](#volume-4-corporate-risk--fincen-anti-fraud-invariants)
5. [Volume 5: Delivery Intelligence & Confidence Scoring (`address_standardizer.delivery`, `confidence`)](#volume-5-delivery-intelligence--confidence-scoring)
6. [Volume 6: Typo Recovery & Fuzzy Correction (`address_standardizer.fuzzy`)](#volume-6-typo-recovery--fuzzy-correction)
7. [Volume 7: High-Throughput Streaming Batch & Columnar Ingestion (`address_standardizer.batch`, `arrow`)](#volume-7-high-throughput-streaming-batch--columnar-ingestion)
8. [Volume 8: Multi-Tier Caching & Stewardship Audit Ledger (`address_standardizer.cache`, `audit`)](#volume-8-multi-tier-caching--stewardship-audit-ledger)
9. [Volume 9: Real-Time Autocomplete Engine (`address_standardizer.autocomplete`)](#volume-9-real-time-autocomplete-engine)
10. [Volume 10: Native FFI & Acceleration Dispatch (`address_standardizer._native_dispatch`)](#volume-10-native-ffi--acceleration-dispatch)
11. [Volume 11: Microservice Server & Command Line Interface (`address_standardizer.server`, `cli`)](#volume-11-microservice-server--command-line-interface)

---

# Volume 1: Core Normalization & Data Models

## `StandardizedAddress`
The canonical standardized address dataclass returned by all parsing and standardization pipelines.

### Fields
| Attribute | Type | Description |
| :--- | :--- | :--- |
| `primary_number` | `Optional[str]` | Street number or house number (e.g., `"123"`, `"742"`). |
| `street_predirectional` | `Optional[str]` | Normalized street prefix directional (e.g., `"N"`, `"SW"`). |
| `street_name` | `Optional[str]` | Primary street name in uppercase (e.g., `"MAIN"`, `"BROADWAY"`). |
| `street_suffix` | `Optional[str]` | Normalized USPS Pub 28 street suffix (e.g., `"ST"`, `"AVE"`, `"BLVD"`). |
| `street_postdirectional` | `Optional[str]` | Normalized street suffix directional (e.g., `"NW"`, `"SE"`). |
| `secondary_designator` | `Optional[str]` | Unit type abbreviation (e.g., `"APT"`, `"STE"`, `"FL"`, `"UNIT"`). |
| `secondary_number` | `Optional[str]` | Unit/apartment/suite number (e.g., `"4B"`, `"1200"`). |
| `pmb_designator` | `Optional[str]` | Private mailbox designator (e.g., `"PMB"`). |
| `pmb_number` | `Optional[str]` | Private mailbox box number. |
| `city_name` | `Optional[str]` | Standardized city/municipality name in uppercase. |
| `state_abbreviation` | `Optional[str]` | Standardized 2-letter state or province code (e.g., `"CA"`, `"NY"`). |
| `zip_code` | `Optional[str]` | 5-digit US ZIP code or primary international postal code. |
| `plus4_code` | `Optional[str]` | 4-digit US ZIP+4 extension. |
| `country_code` | `str` | ISO 3166-1 alpha-2 or alpha-3 country code (default: `"US"`). |
| `delivery_line_1` | `str` | Assembled USPS Pub 28 primary delivery address line. |
| `delivery_line_2` | `Optional[str]` | Assembled secondary unit delivery line. |
| `last_line` | `str` | Assembled city, state, and postal code line (`"SPRINGFIELD, IL 62701"`). |
| `normalized_address_key` | `str` | Deterministic unit-level unique key for clustering and deduplication. |
| `building_key` | `str` | Deterministic building-level key omitting unit numbers. |
| `confidence_score` | `float` | Multi-factor quality score ranging from `0.0` to `1.0`. |
| `spatial_result` | `Optional[SpatialResolutionResult]` | Geocoded latitude, longitude, precision, and Uber H3 cell. |

### Methods
- `as_dict(include_metadata: bool = True) -> dict[str, Any]`: Serializes model into a Python dictionary. When `include_metadata=False`, returns strict 14-key backward-compatible dictionary.
- `to_line() -> str`: Formats single-line comma-delimited representation.
- `to_multiline() -> str`: Formats standard mailing label with newline separators.

---

## `standardize_address()`
Primary functional entry point for address standardization.

```python
def standardize_address(
    address_line: str,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    country_code: Optional[str] = None,
    use_ml: bool = False,
    geocode: bool = False,
    return_raw: bool = False,
    enable_fuzzy: bool = True,
) -> StandardizedAddress:
    ...
```

### Parameters
- `address_line` (`str`): Raw single-line or street address string.
- `city` (`Optional[str]`): Optional explicit city name.
- `state` (`Optional[str]`): Optional explicit state or province name/abbreviation.
- `zip_code` (`Optional[str]`): Optional explicit postal or ZIP code.
- `country_code` (`Optional[str]`): Optional ISO country code. Defaults to `"US"` or contextual auto-detection.
- `use_ml` (`bool`): Enables conditional ML (CRF) tokenization fallback when heuristic parsing confidence is low.
- `geocode` (`bool`): Triggers synchronous offline spatial rooftop geocoding during standardization.
- `return_raw` (`bool`): Preserves original untransformed input tokens in metadata.
- `enable_fuzzy` (`bool`): Enables Damerau-Levenshtein typo correction for street suffixes and cities.

---

# Volume 2: Universal International Engine

## `CountryRegistry`
Singleton registry covering all 249 ISO-3166-1 sovereign nations and dependent territories.

```python
class CountryRegistry:
    @classmethod
    def get(cls, code_or_name: str) -> Optional[CountryInfo]: ...
    @classmethod
    def detect_country(cls, text: str) -> Optional[str]: ...
    @classmethod
    def is_postal_issuing(cls, alpha2_or_alpha3: str) -> bool: ...
```

## `PostalValidationResult`
Data model holding international postal validation outcomes.
- `is_valid` (`bool`): Indicates whether the postal code matches national formatting rules.
- `postal_code` (`str`): Normalized postal code string.
- `country_code` (`str`): Detected ISO 3166-1 alpha-3 nation code.
- `formatted` (`str`): Nationally styled representation (e.g., `"SW1A 1AA"`, `"100-0001"`).

## Functions
- `format_upu_address(addr: StandardizedAddress) -> str`: Formats address into envelope layout complying with UPU S42 conventions.
- `validate_postal_code(code: str, country_code: str) -> PostalValidationResult`: Validates postal structure across 196 postal systems.
- `extract_postal_code(text: str, hint_country: Optional[str] = None) -> tuple[Optional[str], Optional[str]]`: Extracts embedded postal codes from noisy raw strings.

---

# Volume 3: Geospatial Subsystem & Offline Rooftop Indexing

## `SpatialEngine`
Air-gapped SQLite `R*Tree` and Uber H3 spatial indexing engine.

```python
class SpatialEngine:
    def __init__(self, db_path: Optional[str] = None): ...
    def resolve(
        self,
        street: str,
        city: str,
        state: str,
        zip_code: str,
    ) -> Optional[SpatialResolutionResult]: ...
```

## `SpatialResolutionResult`
- `latitude` (`float`): WGS84 decimal latitude.
- `longitude` (`float`): WGS84 decimal longitude.
- `precision` (`CascadePrecision`): Resolution level (`CONFIRMED_ROOFTOP`, `PARCEL_INTERPOLATED`, `POSTAL_CENTROID`, `CITY_CENTROID`).
- `h3_index` (`str`): Pure-Python computed Uber H3 hexagonal index (Resolution 10: ~65m).
- `confidence` (`float`): Spatial resolution match score.

## Spatial Functions
- `lat_lng_to_h3(lat: float, lng: float, resolution: int = 10) -> str`: Computes Uber H3 hexagonal grid cell index without external C bindings.
- `resolve_spatial_coordinates(street, city, state, zip_code) -> Optional[SpatialResolutionResult]`: Quick resolution using default spatial index.

---

# Volume 4: Corporate Risk & FinCEN Anti-Fraud Invariants

## `CorporateRiskFlag`
Enumeration of corporate formation hubs and risk categories:
- `DOMESTIC_DELAWARE_HUB`: Registered agent formation hubs in Delaware (e.g. 1209 Orange St).
- `DOMESTIC_WYOMING_HUB`: Registered agent centers in Wyoming (e.g. 1712 Pioneer Ave).
- `OFFSHORE_SECRECY_JURISDICTION`: Addresses located in Cayman Islands, BVI, Panama, Channel Islands.
- `COMMERCIAL_MAIL_RECEIVING_AGENCY`: Commercial CMRA / UPS Store locations.
- `ANONYMOUS_SHELL_HUB`: High-density multi-entity shell company co-location facilities.

## Anti-Fraud Functions
- `lookup_corporate_registry(address_or_key: str) -> Optional[CorporateRegistryEntry]`: Inspects curated registry of formation hubs.
- `can_safely_merge_corporate_entities(addr1: StandardizedAddress, addr2: StandardizedAddress) -> bool`: Enforces the 3 mandatory FinCEN CTA anti-fraud invariants (Skyscraper Suite Isolation, Private Residence Protection, Formation Hub Co-Location Isolation).
- `evaluate_corporate_risk(address: str | StandardizedAddress) -> CorporateRiskAssessment`: Evaluates entity formation risk flags.

---

# Volume 5: Delivery Intelligence & Confidence Scoring

## `DPVFootnote` & `RDI`
- `DPVFootnote`: Standard USPS Delivery Point Validation footnotes (`AA` confirmed, `BB` street & number confirmed, `CC` secondary number confirmed, `N1` missing secondary, `M1` missing primary number).
- `RDI`: Residential Delivery Indicator (`RESIDENTIAL`, `COMMERCIAL`, `UNKNOWN`).

## `ConfidenceScorer` & `compute_confidence_score()`
Evaluates standardization quality and assigns routing classifications:
- `AUTO_PASS` ($\ge 0.85$): Safe for automatic ingestion and automated billing.
- `FUZZY_REVIEW` ($0.70 - 0.84$): Requires light automated heuristic reconciliation.
- `MANUAL_STEWARDSHIP` ($< 0.70$): Routed to human stewardship queues.

---

# Volume 6: Typo Recovery & Fuzzy Correction

- `damerau_levenshtein_distance(s1: str, s2: str) -> int`: Fast edit distance algorithm with adjacent character transposition detection.
- `heal_street_suffix(token: str) -> Optional[str]`: Corrects misspelled street suffixes (e.g. `"Avneu"` $\rightarrow$ `"AVE"`).
- `heal_city_token(token: str, state: str) -> Optional[str]`: Resolves typographical errors against gazetteer tables.
- `heal_postal_code_transposition(zip5: str, state: str) -> Optional[str]`: Detects transposed digits in US ZIP codes.

---

# Volume 7: High-Throughput Streaming Batch & Columnar Ingestion

## Batch Streaming Functions
- `stream_standardize_csv(input_path, output_path, chunk_size=5000, ...)`: Memory-bounded (< 35MB RSS) multi-process CSV processor.
- `stream_standardize_jsonl(input_path, output_path, chunk_size=5000, ...)`: High-throughput JSONL streaming pipeline.
- `batch_standardize(records: list[dict], workers: int = 2) -> list[StandardizedAddress]`: In-memory parallel batch executor.

## Columnar Integrations (`address_standardizer.arrow`)
- `standardize_arrow(table: pyarrow.Table, ...) -> pyarrow.Table`: Direct PyArrow columnar batch transformer.
- `standardize_polars(df: polars.DataFrame, ...) -> polars.DataFrame`: Zero-copy Polars vectorized standardization.
- `register_duckdb_udfs(con: duckdb.DuckDBPyConnection)`: Registers native SQL scalar function `standardize_address(str)` inside DuckDB.

---

# Volume 8: Multi-Tier Caching & Stewardship Audit Ledger

## `MultiTierCache`
Two-tier reference cache combining L1 process memory and L2 persistent SQLite WAL store.
- `get(key: str) -> Optional[StandardizedAddress]`
- `set(key: str, value: StandardizedAddress) -> None`
- `stats() -> dict[str, int]` (returns hits, misses, evictions)

## `StewardshipAuditLedger`
Append-only audit trail logging manual reviews, automated corrections, and FinCEN compliance events.
- `log_action(action: ActionType, record_key: str, details: dict) -> int`
- `get_audit_history(record_key: str) -> list[StewardshipAuditRecord]`

---

# Volume 9: Real-Time Autocomplete Engine

## `AutocompleteEngine`
Sub-8ms prefix search trie with secondary unit prompt heuristics.
- `index_address(street, city, state, zip_code)`: Indexes an address candidate.
- `suggest(query: str, limit: int = 5) -> list[AutocompleteSuggestion]`

---

# Volume 10: Native FFI & Acceleration Dispatch

- `is_native_available() -> bool`: Returns `True` if compiled Rust SIMD/DFA core is present.
- `is_using_native() -> bool`: Returns `True` if active thread is executing via native dispatch.
- `get_engine_info() -> dict[str, Any]`: Returns engine telemetry, compiler versions, and acceleration status.

---

# Volume 11: Microservice Server & Command Line Interface

## REST Server (`create_app()`)
FastAPI microservice endpoints:
- `POST /standardize`: Standardize a single address payload.
- `POST /batch`: Process a JSON array of up to 1,000 addresses.
- `GET /autocomplete?q={prefix}`: Interactive typeahead completions.
- `GET /health`: Healthcheck endpoint reporting engine version and cache status.
- `GET /metrics`: Prometheus-compatible latency and throughput metrics.

## CLI Commands
- `address-standardizer standardize "<address>"`
- `address-standardizer batch -i input.csv -o output.csv --chunk-size 5000`
- `address-standardizer serve --host 0.0.0.0 --port 8000`
- `address-standardizer benchmark --records 10000`

---

## 📄 License & Ownership

Address Standardizer is open-source software owned and maintained by **HobbyHabbit LLC** under the **MIT License**. For security disclosures, see **[SECURITY.md](../SECURITY.md)**.
