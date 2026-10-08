# address-standardizer-go

Official Go client SDK for the **Address Standardizer** HTTP microservice daemon.

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**.

---

## Installation

```bash
go get github.com/Jacob-white/Address-Standardizer/sdks/go
```

Requires Go 1.21 or newer (`go 1.21` in `go.mod`). The package name is `standardizer`; it has no third-party dependencies.

---

## Usage

```go
package main

import (
	"context"
	"fmt"
	"log"

	standardizer "github.com/Jacob-white/Address-Standardizer/sdks/go"
)

func main() {
	ctx := context.Background()
	client := standardizer.NewClient("http://localhost:8000")

	// Standardize single address. Flags are optional pointers: leave them nil
	// to use the server defaults (geocoding and fuzzy matching enabled).
	result, err := client.Standardize(ctx, standardizer.StandardizeRequest{
		Address:         "100 Main St, Austin, TX 78701",
		EnableGeocoding: standardizer.Bool(true),
	})
	if err != nil {
		log.Fatalf("Standardization failed: %v", err)
	}

	fmt.Printf("Street: %s\n", result.Street1)
	fmt.Printf("City/State/Zip: %s, %s %s\n", result.City, result.State, result.PostalCode)
	fmt.Printf("Precision: %s\n", result.Precision)

	// Interactive autocomplete
	suggestions, err := client.Autocomplete(ctx, standardizer.AutocompleteRequest{
		Query:      "100 Mai",
		MaxResults: 5,
	})
	if err != nil {
		log.Fatalf("Autocomplete failed: %v", err)
	}

	for _, s := range suggestions {
		fmt.Printf("- %s\n", s.Text)
	}
}
```

### Optional flags are tri-state pointers

Request flags (`EnableGeocoding`, `EnableFuzzy`, `AllowLocality`, `CorrectStateFromZip`, `IncludeMetadata`) are `*bool`.
`nil` is omitted from the JSON so the server default applies; use `standardizer.Bool(v)` to set one explicitly.
`CorrectStateFromZip` replaces a US state that contradicts the ZIP with the ZIP's state (server default: false).
`BatchStandardizeRequest` carries the batch-wide flags `EnableGeocoding`, `EnableFuzzy`, `AllowLocality` and
`CorrectStateFromZip`.

Response fields that can be unknown are pointers too: `Latitude`, `Longitude`, `AccuracyRadiusMeters`,
`ConfidenceScore` and `CorporateRiskScore` are `*float64`, and `CMRA` and `Vacant` are `*bool`
(`nil` means unknown, not `false`). Always check for `nil` before dereferencing:

```go
if result.Latitude != nil && result.Longitude != nil {
	fmt.Printf("%.6f, %.6f
", *result.Latitude, *result.Longitude)
}
if result.CMRA != nil && *result.CMRA {
	fmt.Println("commercial mail receiving agency")
}
```

String fields such as `Precision`, `Deliverability` and `RDI` decode a JSON `null` as the empty string.

### Timeouts and cancellation

`NewClient` applies a default timeout of `standardizer.DefaultTimeout` (10 s) to each non-streaming call, including
reading the response body. Change it with `WithTimeout`; zero or negative disables it, leaving the call's `context`
in charge:

```go
client := standardizer.NewClient(
	"http://localhost:8000",
	standardizer.WithTimeout(5*time.Second),
	standardizer.WithHeader("X-Api-Key", "secret"),
)
```

`WithTimeout` is **not** applied to streaming calls (`StreamBatch`, `StreamBatchRecords`), because it would cut long
streams. Cancel a stream through its context. The default `http.Client` has no overall `Timeout`; its transport
bounds connecting (10 s) and waiting for response headers (30 s). `WithHTTPClient` replaces that client entirely.

### Batches

```go
batch, err := client.StandardizeBatch(ctx, standardizer.BatchStandardizeRequest{
	Addresses: []interface{}{
		"100 Main St, Austin, TX 78701",
		standardizer.StandardizeRequest{Street1: "350 5th Ave", City: "New York", State: "NY"},
	},
	CorrectStateFromZip: standardizer.Bool(true),
})
```

### Streaming batches

`StreamBatchRecords` streams one result per input, in order, over NDJSON. It returns a record channel and an error
channel; both are closed when the call finishes, and the error channel receives at most one value. Read the record
channel until it closes, then the error channel:

```go
ctx, cancel := context.WithCancel(context.Background())
defer cancel() // cancelling ctx stops the stream and releases the connection

records, errs := client.StreamBatchRecords(ctx, standardizer.BatchStandardizeRequest{
	Addresses: []interface{}{"100 Main St, Austin, TX 78701", "not an address"},
})
for rec := range records {
	if rec.Err != nil {
		// the server could not standardize this input; the stream continues
		fmt.Printf("record %d failed: %s
", rec.Err.Index, rec.Err.Message)
		continue
	}
	fmt.Println(rec.Address.Street1)
}
if err := <-errs; err != nil {
	log.Fatalf("stream failed: %v", err)
}
```

- Each `StreamRecord` has exactly one of `Address` (`*StandardizedAddress`) and `Err` (`*RecordError` with `Index` and `Message`).
- The error channel reports transport failures, non-2xx responses (`*APIError`), malformed lines, context cancellation, and a **truncated stream** (`stream ended after N of M record(s)`), so a short stream is never mistaken for a complete one.
- Long records are fine: lines are read without a token-size limit.

`StreamBatch(ctx, []string)` is a convenience wrapper for plain address strings that returns
`(<-chan StandardizedAddress, <-chan error)`. The first record the server could not standardize ends the stream with
a `*RecordError` on the error channel; use `StreamBatchRecords` to receive per-record errors and keep going.

```go
out, errs := client.StreamBatch(ctx, []string{"100 Main St, Austin, TX 78701"})
for addr := range out {
	fmt.Println(addr.Street1)
}
if err := <-errs; err != nil {
	var recErr *standardizer.RecordError
	if errors.As(err, &recErr) {
		fmt.Printf("record %d: %s
", recErr.Index, recErr.Message)
	}
}
```

### Autocomplete

`Autocomplete` sends a POST. `AutocompleteGet` and `AutocompleteGetRequest` send the same query as a GET. The
request carries optional proximity bias (`Latitude`, `Longitude`, `RadiusMiles` are `*float64`):

```go
lat, lon := 40.75, -73.99
radius := 25.0
suggestions, err := client.AutocompleteGetRequest(ctx, standardizer.AutocompleteRequest{
	Query:       "350 5th",
	MaxResults:  5,
	StateFilter: "NY",
	Latitude:    &lat,
	Longitude:   &lon,
	RadiusMiles: &radius,
})
```

`AutocompleteGet(ctx, query, limit, state)` is the shorthand without proximity. Suggestions expose
`DistanceMeters` (`*float64`) when proximity was supplied. `Health(ctx)` returns the service's `HealthResponse`.

### Error handling

Non-2xx responses return `*standardizer.APIError` with `StatusCode` and the full `Body` (its `Error()` text is
truncated to 512 bytes):

```go
var apiErr *standardizer.APIError
if errors.As(err, &apiErr) && apiErr.StatusCode == http.StatusTooManyRequests {
	// back off and retry
}
```

---

## Tests

`go test ./...` runs unit tests plus wire-format tests that decode the JSON fixtures in `testdata/`. Those fixtures
are recorded responses of the real Python server (per the comment in `wire_test.go`), so they exercise the actual
field names and nulls. Separately, `tests/test_sdk_contract.py` in the repository root checks the Go models'
field names against the server's OpenAPI schema. Set `ADDRESS_STANDARDIZER_URL` (for example `http://127.0.0.1:8000`) to also run the
live-server integration test; without it that test is skipped.

---

## 📄 License & Ownership

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../../LICENSE)** for details.
