# Address Standardizer Quickstart

This guide takes you from install to a running HTTP service. Every snippet below was run against version 3.3.0 and
the output shown is the real output (long output is cut with `...`). For the full reference see
[api_reference.md](api_reference.md).

---

## 1. Installation

Address Standardizer needs **Python 3.11 or newer**. The core package depends only on `requests`.

From a source checkout (works today):

```bash
pip install -e .                 # core: standardization, keys, spatial engine, CLI, batch streaming
pip install -e ".[server]"       # + FastAPI / uvicorn / pydantic / httpx for the HTTP service
pip install -e ".[arrow]"        # + pyarrow / polars / duckdb integrations
```

Once a release is published to PyPI the same extras are available as `pip install "address-standardizer[server]"`.

| Extra | Installs | Needed for |
| :--- | :--- | :--- |
| `server` | `fastapi`, `uvicorn`, `pydantic`, `httpx` | `address-standardizer serve`, `create_app()`, the REST API |
| `arrow` | `pyarrow`, `polars`, `duckdb` | `standardize_arrow`, `standardize_polars`, `register_duckdb_udfs` |
| `ml` | `usaddress` | optional statistical (CRF) parser fallback |
| `benchmark` | `psutil` | the `benchmark` CLI command |
| `dev` | `pytest`, `pytest-cov`, `ruff`, `usaddress`, `hypothesis`, `h3` | running the test suite |

Extras can be combined: `pip install -e ".[server,arrow]"`.

The package installs a console script `address-standardizer`. `python -m address_standardizer` is equivalent and works
without installing the script. All CLI examples below use the console script name.

### Optional native module

`_address_standardizer_rs` is an optional Rust (PyO3) extension. It is **not** installed by `pip install` and it
**only accelerates American Soundex**; parsing, normalization and key building are always pure Python, so results are
identical with or without it. Build it with a Rust toolchain and `pip install maturin`, then `maturin develop --release`.
Set `ADDRESS_STANDARDIZER_FORCE_PURE=1` to disable it at runtime. Check what is active:

```python
from address_standardizer import get_engine_info

print(get_engine_info())
```

```text
{'engine': 'PurePythonCore', 'is_native': False, 'native_available': False, 'force_pure_python': False, 'version': '3.3.0', 'native_functions': [], 'throughput_sla_target': '>= 2,000 rec/s', 'simd_acceleration': False, 'zero_copy_slices': False}
```

---

## 2. Standardize one address

`standardize_address` accepts either a single free-form line in `street1` (as the first positional argument), or
separate fields.

```python
from address_standardizer import standardize_address

addr = standardize_address("100 Wall St, Ste 400, New York, NY 10005")
print(addr.street1, "|", addr.street2, "|", addr.city, addr.state, addr.postal_code, addr.country)
print(addr.normalized_address_key)
print(addr.building_key)
print(addr.phonetic_key)
print(addr.address_status, addr.deliverability.value)

# Structured input gives the same result.
same = standardize_address(
    street1="100 Wall St", street2="Ste 400", city="New York", state="NY", postal_code="10005"
)
print(same.normalized_address_key == addr.normalized_address_key)
```

```text
100 WALL ST | STE 400 | NEW YORK NY 10005 USA
100 WALL ST|STE 400|NEW YORK|NY|10005|USA
100 WALL ST||NEW YORK|NY|10005|USA
100|W400|10005
standardized DELIVERABLE
True
```

The three keys are deterministic and are meant for matching and de-duplication:

- `normalized_address_key`: `STREET1|STREET2|CITY|STATE|ZIP5_OR_POSTAL|COUNTRY_ALPHA3` (suite level)
- `building_key`: the same without the secondary unit (building level)
- `phonetic_key`: a Soundex-based blocking key for typo-tolerant candidate matching

### Library defaults differ from the HTTP service

The Python function defaults to `enable_geocoding=False`; the HTTP API defaults `enable_geocoding` to `true`. Pass
`enable_geocoding=True` in Python to get coordinates.

### Geocoding and delivery metadata

Confidence, delivery intelligence and corporate-risk fields are filled in by default (`finalize=True`). Coordinates are
resolved only with `enable_geocoding=True`, using the offline spatial engine:

```python
from address_standardizer import standardize_address

addr = standardize_address("1600 Pennsylvania Ave NW, Washington, DC 20500", enable_geocoding=True)
print(addr.latitude, addr.longitude, addr.precision, addr.accuracy_radius_meters)
print(addr.confidence_score, addr.routing_tier, addr.rdi.value, addr.dpv_footnotes)

meta = standardize_address("100 Wall St, Ste 400, New York, NY 10005").as_dict(include_metadata=True)
print(meta["deliverability"].value, meta["confidence_score"], meta["routing_tier"], meta["dpv_footnotes"])
print(meta["failure_reason_codes"], meta["is_us"], meta["country_iso3"])
```

```text
38.89511 -77.03637 MUNICIPAL_CENTROID 50000.0
0.9775 AUTO_PASS Unknown ['AA', 'BB']
DELIVERABLE 0.988 AUTO_PASS ['AA', 'BB', 'CC']
[] True USA
```

The built-in spatial index is a small seed set, so many addresses resolve to a coarse centroid
(`MUNICIPAL_CENTROID`, a 50 km radius here) rather than a rooftop. Build your own index from open data with
`address-standardizer spatial build` (section 7). When nothing can be resolved the precision is `UNRESOLVED` and
`latitude`/`longitude` are `null` in `as_dict()` and in the API.

---

## 3. ZIP / state policy

A ZIP code that belongs to a different state than the one supplied is treated as a data-quality problem, not silently
"fixed":

- **Default:** the supplied state is kept. The address stays `address_status == "standardized"`, the failure reason
  `ERR_ZIP_STATE_MISMATCH` is reported, the DPV footnote is `A1`, and `deliverability` is `UNDELIVERABLE`. (`UNDELIVERABLE`
  from `A1` applies only when a ZIP was supplied but is malformed or belongs to another state; a missing ZIP does not
  trigger it.)
- **Opt-in `correct_state_from_zip`:** a US state that contradicts the ZIP is replaced with the ZIP's state and the change
  is reported as `WARN_STATE_CORRECTED_FROM_ZIP`.

```python
from address_standardizer import standardize_address

kwargs = dict(street1="100 Main St", city="Austin", state="CA", postal_code="78701")  # 78701 is a Texas ZIP

kept = standardize_address(**kwargs)
print(kept.state, kept.address_status, kept.deliverability.value, kept.dpv_footnotes, kept.failure_reason_codes)

fixed = standardize_address(**kwargs, correct_state_from_zip=True)
print(fixed.state, fixed.address_status, fixed.deliverability.value, fixed.dpv_footnotes, fixed.failure_reason_codes)
```

```text
CA standardized UNDELIVERABLE ['A1', 'BB'] ['ERR_ZIP_STATE_MISMATCH']
TX standardized DELIVERABLE ['AA', 'BB'] ['WARN_STATE_CORRECTED_FROM_ZIP']
```

Ways to turn the correction on:

| Where | How |
| :--- | :--- |
| `standardize_address`, `batch_standardize`, `stream_standardize_csv/jsonl/json` | keyword `correct_state_from_zip=True` (default `None`: use the environment variable) |
| REST `/v1/standardize` and `/v1/batch` | JSON field `"correct_state_from_zip": true` |
| CLI `parse`, `batch` and the shorthand form | `--correct-state-from-zip` |
| Everywhere (process wide) | environment variable `ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP=1` (`1`, `true`, `yes` or `on`) |
| `standardize_arrow`, `standardize_polars`, DuckDB UDFs | environment variable only (no parameter) |

An explicit `correct_state_from_zip=False` beats the environment variable. The correction applies to a valid 5-digit (or
ZIP+4) US ZIP, either when `state` and `postal_code` are supplied as separate fields, or when `state` and `postal_code`
are both empty and the single-line `street1` ends with `ST ZIP`:

```python
from address_standardizer import standardize_address

line = "100 Main St, Austin, CA 78701"
print(standardize_address(line).state, standardize_address(line, correct_state_from_zip=True).state)
```

```text
CA TX
```

---

## 4. Batch processing

### In memory: `batch_standardize`

`batch_standardize` is a generator. It takes strings or dictionaries (accepted keys include `street1`/`street`/`address`,
`street2`/`suite`/`apt`/`unit`, `city`, `state`/`province`, `postal_code`/`zip`/`zipcode`/`postcode`, `country`).

```python
from address_standardizer import batch_standardize

rows = list(batch_standardize([
    "100 Wall St, New York, NY 10005",
    {"street1": "350 5th Ave", "city": "New York", "state": "NY", "zip": "10118"},
]))
for r in rows:
    print(r.normalized_address_key)
```

```text
100 WALL ST||NEW YORK|NY|10005|USA
350 5TH AVE||NEW YORK|NY|10118|USA
```

### Files: CSV, JSONL and JSON

The streaming functions read a file in chunks and write a new file; they return the number of rows processed. Output
keeps every input column and appends `std_*` columns plus keys. They use worker processes (at most 2), so **on Windows and
macOS your script must be guarded by `if __name__ == "__main__":`**, otherwise the spawned workers re-import it and it
will hang.

```python
from address_standardizer import stream_standardize_csv

if __name__ == "__main__":
    n = stream_standardize_csv("addresses.csv", "out.csv")
    print(n)
    print(open("out.csv").read())
```

With this `addresses.csv`:

```text
street1,city,state,postal_code
100 Wall St Ste 400,New York,NY,10005
350 5th Ave,New York,NY,10118
100 Main St,Austin,CA,78701
```

the output is:

```text
3
street1,city,state,postal_code,std_street1,std_street2,std_city,std_state,std_postal_code,std_country,rooftop_address,std_rooftop_address,normalized_address_key,building_key,phonetic_key,is_registered_agent_hub,is_private_residence,address_status
100 Wall St Ste 400,New York,NY,10005,100 WALL ST,STE 400,NEW YORK,NY,10005,USA,100 WALL ST,100 WALL ST,100 WALL ST|STE 400|NEW YORK|NY|10005|USA,100 WALL ST||NEW YORK|NY|10005|USA,100|W400|10005,False,False,standardized
350 5th Ave,New York,NY,10118,350 5TH AVE,,NEW YORK,NY,10118,USA,350 5TH AVE,350 5TH AVE,350 5TH AVE||NEW YORK|NY|10118|USA,350 5TH AVE||NEW YORK|NY|10118|USA,350|#5|10118,False,False,standardized
100 Main St,Austin,CA,78701,100 MAIN ST,,AUSTIN,CA,78701,USA,100 MAIN ST,100 MAIN ST,100 MAIN ST||AUSTIN|CA|78701|USA,100 MAIN ST||AUSTIN|CA|78701|USA,100|M500|78701,False,False,standardized
```

`stream_standardize_jsonl` and `stream_standardize_json` have the same signature. JSONL is streamed in constant memory;
`stream_standardize_json` loads the whole array into memory, so use JSONL for very large inputs. Column names can be
remapped with `street_col=`, `zip_col=`, etc., or with `mapping={"address": "street1", "zip": "postal_code"}`.

### From the CLI

`batch` takes two **positional** arguments, input then output. The format is chosen from the file extension (`.jsonl` /
`.ndjson` -> JSONL, `.json` -> JSON, anything else -> CSV) or with `--format`.

```bash
address-standardizer batch addresses.csv out.csv --confidence
```

```text
Standardized 3 record(s) -> out.csv
```

`--confidence` appends `confidence_score` and `routing_tier` columns (`0.9880 AUTO_PASS` for the first row,
`0.8575 FUZZY_REVIEW` for the Austin/CA row, because of the ZIP/state mismatch). Other flags: `--street-col`,
`--street2-col`, `--city-col`, `--state-col`, `--zip-col`, `--country-col`, `--mapping`, `--country`, `--chunk-size`,
`--workers` (max 2), `--enable-geocoding`, `--spatial-db`, `--include-intl`, `--geocode` (calls the US Census API over the
network), `--audit-csv`, `--no-cache`, `--correct-state-from-zip`.

```bash
address-standardizer batch addresses.csv fixed.csv --correct-state-from-zip
```

The last row's `std_state` is now `TX`.

---

## 5. Command line

Standardize a single address with the `parse` subcommand (the subcommand is `parse`, not `standardize`):

```bash
address-standardizer parse "100 Wall St, Ste 400, New York, NY 10005"
```

```json
{
  "street1": "100 WALL ST",
  "street2": "STE 400",
  "city": "NEW YORK",
  "state": "NY",
  "postal_code": "10005",
  "country": "USA",
  "normalized_address_key": "100 WALL ST|STE 400|NEW YORK|NY|10005|USA",
  "building_key": "100 WALL ST||NEW YORK|NY|10005|USA",
  "phonetic_key": "100|W400|10005",
  "address_status": "standardized",
  "raw_street_address": "100 Wall St, Ste 400, New York, NY 10005",
  "is_us": true,
  "is_private_residence": false,
  "is_registered_agent_hub": false,
  "country_iso3": "USA"
}
```

Structured input and the `text` output format (other formats: `json`, `table`, `csv`, `upu`):

```bash
address-standardizer parse --street1 "350 5th Ave" --city "New York" --state NY --zip 10118 --format text
```

```text
STANDARDIZED ADDRESS
====================
Street 1:              350 5TH AVE
Street 2:              
Rooftop Address:       
City:                  NEW YORK
State:                 NY
Postal Code:           10118
Country:               USA (ISO3: USA)
Address Key:           350 5TH AVE||NEW YORK|NY|10118|USA
Building Key:          350 5TH AVE||NEW YORK|NY|10118|USA
Phonetic Key:          350|#5|10118
Status:                standardized
Is US Address:         True
Private Residence:     False
Registered Agent Hub:  False
```

```bash
address-standardizer parse --format csv "100 Wall St, New York, NY 10005"
```

```text
street1,street2,city,state,postal_code,country,address_status,confidence_score,normalized_address_key
100 WALL ST,,NEW YORK,NY,10005,USA,standardized,,100 WALL ST||NEW YORK|NY|10005|USA
```

Confidence and the ZIP/state policy. A state that contradicts the ZIP is kept by default:

```bash
address-standardizer parse --confidence --street1 "100 Main St" --city Austin --state CA --zip 78701
```

The JSON ends with:

```text
  "confidence_score": 0.8575,
  "routing_tier": "FUZZY_REVIEW",
  "failure_reason_codes": [
    "ERR_ZIP_STATE_MISMATCH"
  ]
```

With `--correct-state-from-zip` the state becomes `TX` and the JSON ends with:

```bash
address-standardizer parse --confidence --correct-state-from-zip --street1 "100 Main St" --city Austin --state CA --zip 78701
```

```text
  "confidence_score": 0.9775,
  "routing_tier": "AUTO_PASS",
  "failure_reason_codes": [
    "WARN_STATE_CORRECTED_FROM_ZIP"
  ]
```

Other `parse` flags: `--enable-geocoding` (offline spatial engine), `--spatial-db`, `--geocode` (US Census API, network),
`--cascade`, `--audit`, `--no-cache`, `--country`.

**Shorthand and pipes.** With no subcommand, the arguments are treated as an address, and lines on stdin are standardized
one per line. Only `--format`, `--country` and `--correct-state-from-zip` are accepted in this form.

```bash
address-standardizer --format text "100 Wall St, New York, NY 10005"
echo "100 Wall St, New York, NY 10005" | address-standardizer parse --format csv
```

**Other subcommands:** `validate-postal`, `autocomplete`, `spatial` (`build`, `lookup`, `info`, `stats`), `cache`
(`--stats`, `--clear`), `audit`, `benchmark` and `serve`. Run `address-standardizer <command> --help` for each.

```bash
address-standardizer validate-postal "SW1A 1AA" --country GB
address-standardizer autocomplete "100 wall" --limit 2
```

```text
{
  "is_valid": true,
  "country": "GBR",
  "postal_code": "SW1A 1AA",
  "formatted_code": "SW1A 1AA",
  "is_non_postal_country": false,
  "reason": "Valid postal code format"
}
1. 100 WALL ST, NEW YORK, NY 10005 [Secondary Unit Required: STE 400, STE 800, FL 12, FL 20]
```

---

## 6. International addresses and postal codes

```python
from address_standardizer import (
    CountryRegistry, extract_postal_code, standardize_address, validate_postal_code,
)

addr = standardize_address("Unter den Linden 77, 10117 Berlin", country="Germany")
print(addr.street1, addr.postal_code, addr.country, addr.country_iso3)
print(addr.format_upu())

print(validate_postal_code("SW1A 1AA", "GB"))
print(validate_postal_code("12345", "GB"))
print(validate_postal_code("SW1A 1AA", "GB", return_details=True))
print(extract_postal_code("Unter den Linden 77, 10117 Berlin", "DE"))
print(CountryRegistry.get("DE").name, len(CountryRegistry.all_countries()))
```

```text
UNTER DEN LINDEN 77 10117 DEU DEU
UNTER DEN LINDEN 77
10117 BERLIN
GERMANY
True
False
PostalValidationResult(is_valid=True, postal_code='SW1A 1AA', country_code='GBR', reason='Valid postal code format', formatted_code='SW1A 1AA', is_non_postal_country=False)
10117
Germany 249
```

Note that for non-US addresses `country` in the result is the ISO alpha-3 code (`DEU`).

---

## 7. Offline spatial geocoding

The spatial engine is an embedded SQLite R\*Tree database with a 4-stage cascade (rooftop point, street-segment
interpolation, postal centroid, municipal/state centroid). It needs no network. With no database file it uses a small
built-in seed set; set `SPATIAL_DB_PATH` (or place `data/spatial_index.db` in the working directory) to use your own.

Build a database from an OpenAddresses-style CSV (columns `LONGITUDE`, `LATITUDE`, `NUMBER`, `STREET`, `CITY`, `REGION`,
`POSTCODE`, `ID`; lower-case names also work) and query it:

```text
LONGITUDE,LATITUDE,NUMBER,STREET,CITY,REGION,POSTCODE,ID
-97.7431,30.2672,100,MAIN ST,AUSTIN,TX,78701,TX-AUS-0001
```

```bash
address-standardizer spatial build --db sp2.db --openaddresses oa.csv
address-standardizer parse --enable-geocoding --spatial-db sp2.db --street1 "100 Main St" --city Austin --state TX --zip 78701
```

```text
Spatial SQLite index built successfully: sp2.db
Total spatial points: 6
Ingested OpenAddresses points: 1
  "latitude": 30.2672,
  "longitude": -97.7431,
  "spatial_precision": "CONFIRMED_ROOFTOP",
  "spatial_source": "OPENADDRESSES",
  "accuracy_radius_meters": 3.0,
```

(The second command's JSON is shown filtered to the geocode fields.) The same lookup from Python:

```python
from address_standardizer import SpatialEngine, standardize_address

engine = SpatialEngine(db_path="sp2.db")
r = engine.resolve(standardize_address("100 Main St, Austin, TX 78701"))
print(r.latitude, r.longitude, r.precision, r.source, r.stage, r.parcel_id)
engine.close()
```

```text
30.2672 -97.7431 CONFIRMED_ROOFTOP OPENADDRESSES 1 TX-AUS-0001
```

`address-standardizer spatial lookup` also supports `--lat/--lon/--radius`, `--bbox min_lon,min_lat,max_lon,max_lat`
and `--min-lat/--min-lon/--max-lat/--max-lon`; `spatial info` prints index statistics. `TIGER` street segments
(`--tiger`) and OSM GeoJSON (`--osm`) can be ingested too. `lat_lng_to_h3(lat, lng)` returns an H3 resolution-10 cell.

---

## 8. HTTP service

Install the `server` extra, then start the daemon. `serve` binds to **127.0.0.1** by default (use `--host 0.0.0.0` to
listen on all interfaces) on port 8000:

```bash
address-standardizer serve --port 8000
# or: python -m uvicorn address_standardizer.server:app --port 8000
```

Interactive docs are at `/docs` (Swagger UI), `/redoc` and `/openapi.json` unless `ADDRESS_STANDARDIZER_DISABLE_DOCS=1`.

Standardize one address (the request may carry `address`, a single line, or `street1`/`street2`/`city`/`state`/`postal_code`/`country`):

```bash
curl -s -X POST localhost:8000/v1/standardize -H 'Content-Type: application/json' \
  -d '{"address": "100 Wall St, Ste 400, New York, NY 10005"}'
```

```json
{"street1":"100 WALL ST","street2":"STE 400","city":"NEW YORK","state":"NY","postal_code":"10005","country":"USA","normalized_address_key":"100 WALL ST|STE 400|NEW YORK|NY|10005|USA","building_key":"100 WALL ST||NEW YORK|NY|10005|USA","phonetic_key":"100|W400|10005","address_status":"standardized","raw_street_address":"100 Wall St, Ste 400, New York, NY 10005","is_us":true,"is_private_residence":false,"is_registered_agent_hub":false,"rooftop_address":"100 WALL ST","full_rooftop_address":"100 WALL ST, NEW YORK, NY 10005","is_locality_only":false,"is_city_level":false,"dependent_locality":null,"building_name":null,"confidence_score":0.988,"routing_tier":"AUTO_PASS","failure_reason_codes":[],"rdi":"Commercial","cmra":false,"is_cmra":false,"vacant":false,"is_vacant":false,"dpv_footnotes":["AA","BB","CC"],"corporate_risk_score":0.0,"corporate_risk_flags":[],"deliverability":"DELIVERABLE","secondary_prompt_required":false,"prompt_message":null,"suggested_secondary_units":[],"latitude":40.7061,"longitude":-74.006,"precision":"CONFIRMED_ROOFTOP","accuracy_radius_meters":3.0,"census_tract":"000900","fips_code":"36061","spatial_result":{"latitude":40.7061,"longitude":-74.006,"precision":"CONFIRMED_ROOFTOP","accuracy_radius_meters":3.0,"stage":1,"source":"OPENADDRESSES","h3_res10":"8a2a1072885ffff","parcel_id":"NY-MAN-00100","execution_time_ms":0.0839,"metadata":{"census_tract":"000900","fips_code":"36061"}},"country_iso3":"USA"}
```

Send `"include_metadata": false` to get only the base fields (street, keys, status, flags and the rooftop address).

Batch, as a JSON array of strings and/or objects (an object body with an `"addresses"` array can also carry the flags
`enable_geocoding`, `enable_fuzzy`, `allow_locality`, `correct_state_from_zip`):

```bash
curl -s -X POST localhost:8000/v1/batch -H 'Content-Type: application/json' \
  -d '{"addresses": ["100 Main St, Austin, CA 78701", {"street1": "100 Main St", "city": "Austin", "state": "CA", "postal_code": "78701", "correct_state_from_zip": true}], "enable_geocoding": false}'
```

The response is a JSON array of the same objects as `/v1/standardize` returns. For this request, the first element has
`"state":"CA"`, `"deliverability":"UNDELIVERABLE"` and `ERR_ZIP_STATE_MISMATCH`; the second (per-item override) has
`"state":"TX"`, `"deliverability":"DELIVERABLE"` and `WARN_STATE_CORRECTED_FROM_ZIP`.

Stream the results as NDJSON (one JSON object per line) by sending `Accept: application/x-ndjson` (or `?format=ndjson`, or
an NDJSON request body with `Content-Type: application/x-ndjson`). A record that cannot be processed becomes an error line
and the stream continues:

```bash
printf '{"address":"100 Wall St, New York, NY 10005","enable_geocoding":false}\nnot json\n{"enable_fuzzy":"maybe"}\n' \
  | curl -s -X POST localhost:8000/v1/batch -H 'Content-Type: application/x-ndjson' --data-binary @-
```

```text
{"street1": "100 WALL ST", "street2": "", "city": "NEW YORK", "state": "NY", "postal_code": "10005", "country": "USA", ...
{"error": "invalid record", "index": 1}
{"error": "invalid record", "index": 2}
```

Autocomplete (`GET` with `q`, `limit`, `state`, `lat`, `lon`, `radius_miles`; or `POST` with a JSON body):

```bash
curl -s "localhost:8000/v1/autocomplete?q=100%20wall&limit=1&state=NY"
```

```json
{"suggestions":[{"text":"100 WALL ST, NEW YORK, NY 10005","street_line":"100 WALL ST","city":"NEW YORK","state":"NY","postal_code":"10005","secondary_prompt_required":true,"suggested_secondary_units":["STE 400","STE 800","FL 12","FL 20"],"prompt_message":"Requires Suite / Apartment Number","latitude":40.7061,"longitude":-74.006,"distance_meters":null}],"count":1}
```

Health and metrics: `GET /health` returns `{"status":"healthy","version":"3.3.0","engine":{...},"uptime_seconds":...}`;
`GET /metrics` returns JSON, or Prometheus text with `?format=prometheus` / `Accept: text/plain`.

### Limits and errors

| Condition | Result |
| :--- | :--- |
| More than 10,000 addresses in one `/v1/batch` request (`ADDRESS_STANDARDIZER_MAX_BATCH`) | HTTP **413** `{"detail":"Batch of N addresses exceeds the limit of L; ..."}` |
| `/v1/batch` body larger than 16 MiB (`ADDRESS_STANDARDIZER_MAX_BODY_BYTES`) | HTTP **413** `{"detail":"Request body ... exceeds the limit of ... bytes."}` |
| Malformed JSON or a non-string/non-object item in a JSON batch | HTTP **400** `{"detail":"Invalid JSON body"}` / `{"detail":"addresses[0] must be a string or an object, got int"}` |
| Invalid field type in `/v1/standardize` or `/v1/autocomplete` | HTTP **422** with FastAPI's `{"detail":[{...}]}` list |

Unknown paths return HTTP 404 `{"detail":"Not Found"}`.

---

## 9. Apache Arrow, Polars and DuckDB

Install the `arrow` extra. `standardize_arrow` / `standardize_polars` append `std_*` columns (or one struct column with
`as_struct=True`); `register_duckdb_udfs` adds SQL functions to a DuckDB connection.

```python
import pyarrow as pa
import polars as pl
import duckdb
from address_standardizer import standardize_arrow, standardize_polars, register_duckdb_udfs

t = pa.table({
    "street1": ["100 Wall St Ste 400", "350 5th Ave"],
    "city": ["New York", "New York"],
    "state": ["NY", "NY"],
    "postal_code": ["10005", "10118"],
})
out = standardize_arrow(t)
print(out.column_names)
print(out.select(["std_street1", "std_deliverability"]).to_pylist())

df = pl.DataFrame({"street1": ["100 Wall St Ste 400"], "city": ["New York"], "state": ["NY"], "postal_code": ["10005"]})
print(standardize_polars(df).select(["std_street1", "std_normalized_address_key"]).to_dicts())

con = duckdb.connect()
register_duckdb_udfs(con)
print(con.sql("SELECT standardize_address_key_text('100 Wall St, New York, NY 10005') AS k").fetchall())
print(con.sql("SELECT standardize_deliverability_text('100 Wall St, New York, NY 10005') AS d").fetchall())
print(con.sql("SELECT standardize_address('100 Wall St','New York','NY','10005').street1 AS s").fetchall())
```

```text
['street1', 'city', 'state', 'postal_code', 'std_street1', 'std_street2', 'std_city', 'std_state', 'std_postal_code', 'std_country', 'std_normalized_address_key', 'std_building_key', 'std_phonetic_key', 'std_address_status', 'std_deliverability', 'std_latitude', 'std_longitude', 'std_precision', 'std_accuracy_radius_meters', 'std_census_tract', 'std_fips_code', 'std_confidence_score', 'std_routing_tier', 'std_rdi', 'std_cmra']
[{'std_street1': '100 WALL ST', 'std_deliverability': 'DELIVERABLE'}, {'std_street1': '350 5TH AVE', 'std_deliverability': 'DELIVERABLE'}]
[{'std_street1': '100 WALL ST', 'std_normalized_address_key': '100 WALL ST|STE 400|NEW YORK|NY|10005|USA'}]
[('100 WALL ST||NEW YORK|NY|10005|USA',)]
[('REQUIRES_SECONDARY',)]
[('100 WALL ST',)]
```

The `*_text` DuckDB functions parse a single-line address. The sample address has no suite and 100 Wall St is a
multi-unit building, hence `REQUIRES_SECONDARY`. The column arguments of `standardize_arrow` / `standardize_polars` are
`street1_col`, `street2_col`, `city_col`, `state_col`, `postal_code_col` and `country_col`.

---

## 10. Environment variables

| Variable | Effect | Default |
| :--- | :--- | :--- |
| `ADDRESS_STANDARDIZER_MAX_BATCH` | Max addresses per `/v1/batch` request (HTTP 413 above it) | `10000` |
| `ADDRESS_STANDARDIZER_MAX_BODY_BYTES` | Max `/v1/batch` request body in bytes (HTTP 413 above it; minimum 1024) | `16777216` (16 MiB) |
| `ADDRESS_STANDARDIZER_CORS_ORIGINS` | Comma-separated allowed CORS origins; credentials are only allowed when this list is set | unset: all origins, no credentials |
| `ADDRESS_STANDARDIZER_DISABLE_DOCS` | `1`, `true` or `yes` removes `/docs`, `/redoc` and `/openapi.json` | docs enabled |
| `ADDRESS_STANDARDIZER_FORCE_PURE` | `1`, `true`, `yes` or `on` disables the optional native module | unset |
| `ADDRESS_STANDARDIZER_AUDIT_MAX_ROWS` | Cap on rows kept by the default in-memory audit ledger | `100000` |
| `ADDRESS_STANDARDIZER_CORRECT_STATE_FROM_ZIP` | `1`, `true`, `yes` or `on` enables ZIP-based state correction globally | off |
| `ADDRESS_STANDARDIZER_ALLOW_LOCALITY` | exactly `1` allows locality-only (city-level) results for every call | off |
| `SPATIAL_DB_PATH` | Path to the offline spatial SQLite database used by default | unset (built-in seed data) |

---

## Next steps

- [API reference](api_reference.md): every public function, class, REST endpoint, CLI command and field.
- [Client SDKs](https://github.com/Jacob-white/Address-Standardizer/tree/main/sdks#readme): TypeScript, .NET and Go clients for the HTTP service.
- [Security policy](https://github.com/Jacob-white/Address-Standardizer/blob/main/SECURITY.md).
