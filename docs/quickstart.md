# Address Standardizer Quickstart Guide 🚀

Get up and running with **Address Standardizer** in under 5 minutes. This guide covers core address normalization, universal 249-country detection, postal validation, 100% offline rooftop geocoding, corporate risk evaluation, high-throughput streaming batch processing, real-time autocomplete, and the HTTP microservice server.

---

## 1. Installation

Install Address Standardizer from PyPI:

```bash
# Core package (pure-Python acceleration + SQLite R*Tree geocoding)
pip install address-standardizer

# With machine learning parser extra (usaddress CRF)
pip install "address-standardizer[ml]"

# Full enterprise extras (fuzzing, benchmarks, ML)
pip install "address-standardizer[dev,ml,benchmark]"
```

For local repository development or compiling the native Rust SIMD/DFA core:

```bash
git clone https://github.com/Jacob-white/Address-Standardizer.git
cd Address-Standardizer
pip install -e .
maturin develop --release
```

---

## 2. Domestic US Address Standardization

Parse, normalize, and extract secondary units from unstructured or semi-structured US street addresses adhering to **USPS Publication 28**:

```python
from address_standardizer import standardize_address

# Freeform unstructured address
addr = standardize_address("123 north main street suite 400 springfield il 62701")

print(addr.delivery_line_1)       # "123 N MAIN ST"
print(addr.secondary_designator)   # "STE"
print(addr.secondary_number)       # "400"
print(addr.city_name)             # "SPRINGFIELD"
print(addr.state_abbreviation)    # "IL"
print(addr.zip_code)              # "62701"
print(addr.normalized_address_key)# "123-N-MAIN-ST-STE-400-SPRINGFIELD-IL-62701"
print(addr.building_key)          # "123-MAIN-SPRINGFIELD-IL-62701"
```

### Deterministic Matching Keys
Address Standardizer generates two levels of entity clustering keys:
- `normalized_address_key`: Full unique address including normalized secondary units (e.g. `STE 400`).
- `building_key`: Building-level footprint key excluding secondary units, enabling tenant roll-up across multi-tenant properties.

---

## 3. Universal 249-Country ISO-3166-1 Detection & UPU S42 Formatting

Automatically detect destination countries and format envelopes in accordance with **Universal Postal Union (UPU) S42** standards:

```python
from address_standardizer import CountryRegistry, format_upu_address, standardize_address

# Lookup country metadata
country = CountryRegistry.get("DEU")
print(country.official_name)       # "Federal Republic of Germany"
print(country.has_postal_codes)    # True
print(country.postal_format)       # "\\d{5}"

# International address standardization & formatting
de_addr = standardize_address(
    "Unter den Linden 77, 10117 Berlin, Germany",
    country_code="DEU"
)
formatted = format_upu_address(de_addr)
print(formatted)
# Output:
# Unter den Linden 77
# 10117 BERLIN
# GERMANY
```

---

## 4. Global Postal Code Extraction & Strict Validation

Validate postal formats across all 196 postal-issuing countries and gracefully handle 53 non-postal countries:

```python
from address_standardizer import validate_postal_code, extract_postal_code

# Strict postal code pattern validation
res_uk = validate_postal_code("EC1A 1BB", "GBR")
print(res_uk.is_valid)       # True
print(res_uk.postal_code)     # "EC1A 1BB"

# Non-postal country handling (e.g. United Arab Emirates)
res_uae = validate_postal_code("", "ARE")
print(res_uae.is_valid)       # True (non-postal nation)

# Robust extraction from unformatted strings
code, country = extract_postal_code("Send to: 75008 Paris France")
print(code, country)          # "75008", "FRA"
```

---

## 5. 100% Offline Rooftop Spatial Geocoding & Uber H3 Res 10

Resolve spatial coordinates and hexagonal Uber H3 spatial cells with **zero network egress and zero cloud API fees**:

```python
from address_standardizer import resolve_spatial_coordinates, lat_lng_to_h3

# Air-gapped spatial lookup
spatial = resolve_spatial_coordinates("1600 Pennsylvania Ave NW", "Washington", "DC", "20500")

if spatial:
    print(f"Latitude:  {spatial.latitude}")
    print(f"Longitude: {spatial.longitude}")
    print(f"Precision: {spatial.precision.value}")  # "CONFIRMED_ROOFTOP" or "PARCEL_INTERPOLATED"
    print(f"H3 Index:  {spatial.h3_index}")         # e.g., "8a2a1072b59ffff"

# Standalone H3 Resolution 10 Cell Computation (~65m edge)
h3_cell = lat_lng_to_h3(38.8977, -77.0365, resolution=10)
print("H3 Cell:", h3_cell)
```

---

## 6. Corporate Secrecy & FinCEN Anti-Fraud Invariants

Flag offshore formation hubs and protect against illicit entity conflation under the **FinCEN Corporate Transparency Act (CTA/BOI)**:

```python
from address_standardizer import (
    evaluate_corporate_risk,
    can_safely_merge_corporate_entities,
    standardize_address,
)

# 1. Evaluate registered agent hub risk
risk = evaluate_corporate_risk("1209 North Orange St, Wilmington, DE 19801")
print(risk.is_flagged)        # True
print(risk.category.value)     # "DOMESTIC_DELAWARE_HUB"
print(risk.notes)              # Corporation Trust Center

# 2. Hardened Anti-Fraud Invariant: Skyscraper Suite Isolation
addr_a = standardize_address("1209 N Orange St Ste 100 Wilmington DE 19801")
addr_b = standardize_address("1209 N Orange St Ste 400 Wilmington DE 19801")

can_merge = can_safely_merge_corporate_entities(addr_a, addr_b)
print("Can Merge Entities?", can_merge)  # False (different suites at formation hub!)
```

---

## 7. Delivery Intelligence & Confidence Scoring

Evaluate USPS Delivery Point Validation (DPV) footnotes, Residential Delivery Indicator (RDI), and automated stewardship routing:

```python
from address_standardizer import (
    standardize_address,
    evaluate_delivery_intelligence,
    compute_confidence_score,
)

addr = standardize_address("742 Evergreen Terrace, Springfield, OR 97477")

# Delivery point validation & RDI
delivery = evaluate_delivery_intelligence(addr)
print("DPV Footnotes:", [f.value for f in delivery.footnotes])  # ['AA', 'BB']
print("RDI:", delivery.rdi.value)                              # "RESIDENTIAL"

# Composite multi-factor confidence scoring
confidence = compute_confidence_score(addr)
print("Score:", confidence.score)               # 0.95
print("Routing Tier:", confidence.tier.value)    # "AUTO_PASS"
```

---

## 8. High-Throughput Streaming Batch Processing

Process massive CSV and JSONL datasets with bounded memory consumption (< 35 MB RSS):

```python
from address_standardizer import stream_standardize_csv

# Stream-standardize a multi-million row address file
stats = stream_standardize_csv(
    input_path="raw_customers.csv",
    output_path="standardized_customers.csv",
    address_col="street_address",
    city_col="city",
    state_col="state",
    zip_col="postal_code",
    chunk_size=5000,
)

print(f"Processed {stats['total_records']} addresses in {stats['elapsed_seconds']:.2f}s")
print(f"Throughput: {stats['records_per_second']:.0f} rec/sec")
```

---

## 9. Real-Time Interactive Autocomplete Engine

Deliver sub-8ms address typeahead suggestions for web forms and mobile apps:

```python
from address_standardizer import AutocompleteEngine

engine = AutocompleteEngine()
engine.index_address("100 Main Street", "Austin", "TX", "78701")
engine.index_address("100 Main Street", "Boston", "MA", "02108")
engine.index_address("100 Market Street", "San Francisco", "CA", "94105")

# Interactive prefix search
suggestions = engine.suggest("100 Mai", limit=5)
for s in suggestions:
    print(f"- {s.display_text} (Score: {s.relevance_score})")
```

---

## 10. Standalone HTTP Microservice Daemon

Deploy Address Standardizer as a containerized microservice:

```bash
# Start FastAPI REST daemon on port 8000
address-standardizer serve --host 0.0.0.0 --port 8000 --workers 4
```

Test with curl:
```bash
curl -X POST "http://localhost:8000/standardize" \
     -H "Content-Type: application/json" \
     -d '{"address": "350 5th Ave, New York, NY 10118"}'
```

---

## 11. Multi-Platform Client SDKs (TypeScript, .NET, Go)

For applications consuming the microservice daemon across external web, mobile, or backend microservices, use the official client SDKs:

### TypeScript / React
```typescript
import { AddressStandardizerClient } from "@address-standardizer/client";

const client = new AddressStandardizerClient({ baseUrl: "http://localhost:8000" });
const result = await client.standardize({ address: "1600 Pennsylvania Ave NW, Washington, DC" });
console.log(result.delivery_line_1, result.last_line);
```

### .NET / C#
```csharp
using AddressStandardizer.Client;

using var client = new AddressStandardizerClient("http://localhost:8000");
var result = await client.StandardizeAsync("1600 Pennsylvania Ave NW, Washington, DC");
Console.WriteLine(result.DeliveryLine1);
```

### Go
```go
client := standardizer.NewClient("http://localhost:8000")
result, err := client.Standardize(ctx, standardizer.StandardizeRequest{Address: "1600 Pennsylvania Ave NW"})
```

See the **[Client SDKs Documentation](../sdks/README.md)** for detailed installation and advanced usage.

---

## Next Steps

- Consult the **[Complete API Reference](api_reference.md)** for detailed parameters, class definitions, and return types.
- Review our **[Security Policy & Sandboxing Guide](../SECURITY.md)** for threat modeling and vulnerability disclosure.
- Explore the **[Enterprise Architectural Blueprints](README.md)** for deep-dive technical roadmaps.
- Integrate via the **[Multi-Platform Client SDKs](../sdks/README.md)** (TypeScript/React, .NET, Go).

---

*Address Standardizer is developed and maintained by **HobbyHabbit LLC** under the **MIT License**.*
