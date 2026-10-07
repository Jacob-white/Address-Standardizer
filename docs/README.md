# Address Standardizer Documentation & Technical Specifications 📚

Address Standardizer is owned and maintained by **HobbyHabbit LLC** under the **MIT License**. This directory contains the complete developer guides, API specifications, and formal architectural blueprints for the platform across all evolution phases:

---

## Developer Guides & Reference

- **[5-Minute Quickstart Guide](quickstart.md)** — Step-by-step onboarding for address parsing, international detection, offline spatial geocoding, streaming batch, and HTTP daemon.
- **[Complete API Reference](api_reference.md)** — Exhaustive technical reference for all Python models, functions, classes, CLI commands, and microservice endpoints.
- **[Security Policy & Sandboxing Guide](../SECURITY.md)** — Threat model, memory safety, air-gapped spatial execution, FinCEN anti-fraud invariants, and vulnerability disclosure procedures.

---

## Architectural Specifications & Evolution Phases

### [1. Phase 4: Commercial Parity Architecture Plan](COMMERCIAL_PARITY_ARCHITECTURE_PLAN.md) (v4.0.0 — Master Specification)
- **Specification**: [`COMMERCIAL_PARITY_ARCHITECTURE_PLAN.md`](COMMERCIAL_PARITY_ARCHITECTURE_PLAN.md)
- **Status**: Approved Master Technical Architecture Blueprint
- **Key Capabilities**:
  - Direct competitive parity against Smarty, Lob, Melissa Data, Loqate, and Google Maps Address Validation.
  - Complete USPS CASS Cycle N open data derivation and DPV footnote state machine (`AA` through `PB`).
  - High-performance Rust SIMD/DFA native acceleration core (`> 220,000 rec/sec`).
  - Standalone multi-platform client SDKs (TypeScript/React, .NET, Go).
  - Open geospatial ETL ingestion pipelines for US Census TIGER/Line 2026, OpenAddresses, and OpenStreetMap (OSM).

---

### [2. Phase 3: Global Spatial Enterprise Blueprint](GLOBAL_SPATIAL_ENTERPRISE_BLUEPRINT.md) (v3.0.0 — Certified)
- **Specification**: [`GLOBAL_SPATIAL_ENTERPRISE_BLUEPRINT.md`](GLOBAL_SPATIAL_ENTERPRISE_BLUEPRINT.md)
- **Status**: Implemented & Certified (`v3.3.0`)
- **Key Capabilities**:
  - **Universal International & Multilingual Parsing**: Full Universal Postal Union (UPU) S42 and ISO 19160-4 compliance covering 249 ISO-3166-1 countries, regional grammar families (East Asia, LatAm, Nordic/Germanic Europe, Eastern Europe, Middle East/Africa).
  - **Unicode NFKD Diacritic Normalizer**: Ligature folding and diacritic separation preserving clean ASCII keys for deterministic deduplication.
  - **100% Offline Open-Data Spatial & Rooftop Geocoder**: Embedded SQLite `R*Tree` virtual tables + pure-Python Uber `H3` Resolution 10 (~65m) cell indexing with 4-stage cascade resolution in **0.035 ms p99**.
  - **High-Throughput Acceleration Engine**: Pure Python core (`_pure_python_core.py`) delivering **> 5,400 rec/sec** finalized / **> 14,000 rec/sec** unfinalized with 100% bit-for-bit key equivalence.
  - **Cross-Border Corporate Transparency**: Curated international secrecy hubs with 3 enforced anti-fraud invariants (*Skyscraper Suite Isolation*, *Private Residence Protection*, and *Formation Hub Co-Location Isolation*).
  - **Multinational Golden Benchmark Suite**: 1,000-record ground-truth dataset and property-based fuzzing battery (`tests/fuzzing/`).

---

### [3. Phase 2: Enterprise Strategic & Technical Blueprint](ENTERPRISE_STRATEGIC_TECHNICAL_BLUEPRINT.md) (v2.0.0 — Certified)
- **Specification**: [`ENTERPRISE_STRATEGIC_TECHNICAL_BLUEPRINT.md`](ENTERPRISE_STRATEGIC_TECHNICAL_BLUEPRINT.md)
- **Status**: Implemented & Certified (`v2.0.0`)
- **Key Capabilities**:
  - **Confidence Scoring & Routing Tiers**: Multi-factor composite confidence scoring (0.0 to 1.0) routing records to `AUTO_PASS` ($\ge 0.85$), `FUZZY_REVIEW` ($0.70 - 0.85$), or `MANUAL_STEWARDSHIP` ($< 0.70$).
  - **Stewardship Audit Ledger**: Structured SQLite audit ledger logging data quality exceptions, parsing failures, and corporate secrecy flags.
  - **Multi-Tier Reference Caching**: L1 in-memory LRU cache + persistent L2 SQLite WAL cache.
  - **Delivery Intelligence**: USPS DPV diagnostic footnotes (`AA`, `BB`, `CC`, `N1`, `M1`) and Residential Delivery Indicator (RDI Commercial vs Residential).
  - **Typeahead & Autocomplete Engine**: Fast prefix trie with secondary unit prompting (< 8ms latency).

---

### [4. Phase 1: Architecture Optimization Plan](ARCHITECTURE_OPTIMIZATION_PLAN.md) (v1.0.0 — Certified)
- **Specification**: [`ARCHITECTURE_OPTIMIZATION_PLAN.md`](ARCHITECTURE_OPTIMIZATION_PLAN.md)
- **Status**: Implemented & Certified (`v1.0.0`)
- **Key Capabilities**:
  - **Core Parsing Pipeline**: USPS Publication 28 parsing, street suffix and directional normalization.
  - **Deterministic Matching Keys**: Two-tier entity clustering hashes (`normalized_address_key` and `building_key`).
  - **Collision-Free Phonetic Blocking**: Typo-tolerant American Soundex blocking.
  - **Deep Edge-Case Handling**: Rural route / highway contract resolution, Queens hyphenated numbers, and saint street salvage.
  - **Batch Streaming Pipeline**: Memory-efficient chunked CSV processing.
  - **Automated US Benchmark Harness**: 1,000-record US golden evaluation dataset.

---

## 📄 License & Ownership

Address Standardizer is open-source software owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../LICENSE)** for complete details.
