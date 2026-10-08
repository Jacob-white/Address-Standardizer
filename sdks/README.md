# Address Standardizer Client SDKs 🌐

Address Standardizer provides official, type-safe client SDKs for integrating the HTTP microservice daemon into modern web, mobile, desktop, and backend platforms. All SDKs are open-source and owned by **HobbyHabbit LLC** under the **MIT License**.

---

## Available SDKs

| Platform / Language | Package Name | Directory | Compatibility |
| :--- | :--- | :--- | :--- |
| **TypeScript / JavaScript** | [`@address-standardizer/client`](typescript/) | `sdks/typescript` | Node.js 18+, Modern Browsers, React 18+ |
| **.NET / C#** | [`AddressStandardizer.Client`](dotnet/) | `sdks/dotnet` | .NET 8.0, .NET Standard 2.0 / C# 12 |
| **Go** | [`github.com/Jacob-white/Address-Standardizer/sdks/go`](go/) | `sdks/go` | Go 1.21+ |

> **Note:** the npm, NuGet and Go install commands below work once a release has been published (see [Releasing](#-releasing)). Until then, build from source in this repository.

---

## 1. TypeScript / React SDK (`@address-standardizer/client`)

### Installation

```bash
npm install @address-standardizer/client
# or
pnpm add @address-standardizer/client
```

### Usage (TypeScript / Node.js)

```typescript
import { AddressStandardizerClient, isStreamError } from "@address-standardizer/client";

const client = new AddressStandardizerClient({
  baseUrl: "http://localhost:8000",
  timeoutMs: 5000,
});

// Standardize single address
const result = await client.standardize({
  address: "1600 Pennsylvania Ave NW, Washington, DC 20500",
  enable_geocoding: true,
});

console.log(result.street1);          // "1600 PENNSYLVANIA AVE NW"
console.log(result.latitude);
console.log(result.confidence_score);

// Batch standardization
const batch = await client.standardizeBatch({
  addresses: [
    "100 Main St, Austin, TX",
    { street1: "350 5th Ave", city: "New York", state: "NY" },
  ],
});

// Stream large batches as NDJSON
// (the stream also yields per-record error objects; narrow them with isStreamError)
for await (const record of client.streamBatch(["100 Main St, Austin, TX"])) {
  if (isStreamError(record)) {
    console.error(`record ${record.index} failed: ${record.error}`);
  } else {
    console.log(record.street1);
  }
}
```

### React Hook Typeahead Autocomplete

```tsx
import React from "react";
import { useAddressAutocomplete, AddressStandardizerClient } from "@address-standardizer/client";

const client = new AddressStandardizerClient({ baseUrl: "http://localhost:8000" });

export function AddressTypeahead() {
  // Pass React explicitly (or set globalThis.React) so the hook can use its state primitives.
  const { query, setQuery, suggestions, isLoading, selectSuggestion } = useAddressAutocomplete({
    react: React,
    client,
    debounceMs: 150,
  });

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Start typing an address..."
      />
      {isLoading && <span>Loading...</span>}
      <ul>
        {suggestions.map((s) => (
          <li key={s.text} onClick={() => selectSuggestion(s)}>
            {s.text}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 2. .NET / C# SDK (`AddressStandardizer.Client`)

### Installation

```bash
dotnet add package AddressStandardizer.Client
```

### Usage (C# 12 / .NET 8)

```csharp
using AddressStandardizer.Client;

using var client = new AddressStandardizerClient("http://localhost:8000");

// Standardize single address
var result = await client.StandardizeAsync(new StandardizeRequest
{
    Address = "350 5th Ave, New York, NY 10118",
    EnableGeocoding = true,
});

Console.WriteLine($"Street:     {result.Street1}");
Console.WriteLine($"City:       {result.City}, {result.State} {result.PostalCode}");
Console.WriteLine($"Confidence: {result.ConfidenceScore}");
Console.WriteLine($"Lat/Lon:    {result.Latitude}, {result.Longitude}");

// Batch standardization
var batchResults = await client.StandardizeBatchAsync(new BatchStandardizeRequest
{
    Addresses = new List<object>
    {
        "100 Main St, Austin, TX 78701",
        "200 S Wacker Dr, Chicago, IL 60606",
    },
});

// Interactive prefix search
var suggestions = await client.AutocompleteAsync(new AutocompleteRequest
{
    Query = "350 5th",
    MaxResults = 5,
});
foreach (var s in suggestions)
{
    Console.WriteLine($"- {s.Text}");
}
```

---

## 3. Go SDK (`Address-Standardizer/sdks/go`)

### Installation

```bash
go get github.com/Jacob-white/Address-Standardizer/sdks/go
```

### Usage (Go 1.21+)

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

---

## 🧪 Testing the SDKs

Set `ADDRESS_STANDARDIZER_URL` (for example `http://127.0.0.1:8000`, with `python -m uvicorn address_standardizer.server:app` running) to also run the live-server integration tests in each SDK; without it they are skipped.

```bash
# TypeScript / Node.js
cd sdks/typescript
npm install
npm test   # builds first via the pretest script

# .NET (requires dotnet SDK)
cd sdks/dotnet
dotnet test tests/AddressStandardizer.Client.Tests

# Go (requires Go toolchain)
cd sdks/go
go test -v ./...
```

---

## 🚀 Releasing

One-time account setup (PyPI, npm, NuGet, GitHub environment) is listed in **[docs/RELEASING.md](../docs/RELEASING.md)**.

- **Python, npm, NuGet:** bump the version in `pyproject.toml`, `address_standardizer/__init__.py`, `sdks/typescript/package.json` and `sdks/dotnet/AddressStandardizer.Client.csproj` (`python scripts/check_versions.py` verifies they match), then push a `vX.Y.Z` tag. `.github/workflows/release.yml` runs CI and publishes after approval of the `release` environment.
- **Go:** Go modules at v2+ must carry a `/vN` path suffix, so the Go SDK is versioned independently from `v1`. Release it by pushing a `sdks/go/v1.Y.Z` tag.

---

## 📄 License & Ownership

The Address Standardizer client SDKs are open-source software owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../LICENSE)** for complete details.
