# Address Standardizer Client SDKs 🌐

Address Standardizer provides official, type-safe client SDKs for integrating the HTTP microservice daemon into modern web, mobile, desktop, and backend platforms. All SDKs are open-source and owned by **HobbyHabbit LLC** under the **MIT License**.

---

## Available SDKs

| Platform / Language | Package Name | Directory | Compatibility |
| :--- | :--- | :--- | :--- |
| **TypeScript / JavaScript** | [`@address-standardizer/client`](typescript/) | `sdks/typescript` | Node.js 18+, Modern Browsers, React 18+ |
| **.NET / C#** | [`AddressStandardizer.Client`](dotnet/) | `sdks/dotnet` | .NET 8.0, .NET Standard 2.0 / C# 12 |
| **Go** | [`github.com/jwhite/address-standardizer-go`](go/) | `sdks/go` | Go 1.21+ |

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
import { AddressStandardizerClient } from "@address-standardizer/client";

const client = new AddressStandardizerClient({
  baseUrl: "http://localhost:8000",
  timeoutMs: 5000,
});

// Standardize single address
const result = await client.standardize({
  address: "1600 Amphitheatre Pkwy, Mountain View, CA 94043",
  geocode: true,
});

console.log(result.delivery_line_1);       // "1600 AMPHITHEATRE PKWY"
console.log(result.spatial?.latitude);     // 37.422
console.log(result.spatial?.h3_index);     // "8a283082a97ffff"
```

### React Hook Typeahead Autocomplete

```tsx
import React from "react";
import { useAddressAutocomplete } from "@address-standardizer/client";

export function AddressTypeahead() {
  const { query, setQuery, suggestions, loading, selectSuggestion } = useAddressAutocomplete({
    baseUrl: "http://localhost:8000",
    debounceMs: 150,
  });

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Start typing an address..."
      />
      {loading && <span>Loading...</span>}
      <ul>
        {suggestions.map((s) => (
          <li key={s.id} onClick={() => selectSuggestion(s)}>
            {s.display_text}
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
    Geocode = true,
});

Console.WriteLine($"Delivery Line: {result.DeliveryLine1}");
Console.WriteLine($"Confidence:    {result.ConfidenceScore}");
Console.WriteLine($"H3 Cell:       {result.SpatialResult?.H3Index}");

// Interactive prefix search
var suggestions = await client.AutocompleteAsync(new AutocompleteRequest
{
    Query = "350 5th",
    Limit = 5,
});
foreach (var s in suggestions)
{
    Console.WriteLine($"- {s.DisplayText}");
}
```

---

## 3. Go SDK (`address-standardizer-go`)

### Installation

```bash
go get github.com/jwhite/address-standardizer-go
```

### Usage (Go 1.21+)

```go
package main

import (
	"context"
	"fmt"
	"log"

	standardizer "github.com/jwhite/address-standardizer-go"
)

func main() {
	ctx := context.Background()
	client := standardizer.NewClient("http://localhost:8000")

	// Standardize single address
	result, err := client.Standardize(ctx, standardizer.StandardizeRequest{
		Address: "100 Main St, Austin, TX 78701",
		Geocode: true,
	})
	if err != nil {
		log.Fatalf("Standardization failed: %v", err)
	}

	fmt.Printf("Delivery: %s, %s\n", result.DeliveryLine1, result.LastLine)
	fmt.Printf("Precision: %s\n", result.SpatialResult.Precision)

	// Interactive autocomplete
	suggestions, err := client.Autocomplete(ctx, standardizer.AutocompleteRequest{
		Query: "100 Mai",
		Limit: 5,
	})
	if err != nil {
		log.Fatalf("Autocomplete failed: %v", err)
	}

	for _, s := range suggestions {
		fmt.Printf("- %s (Score: %.2f)\n", s.DisplayText, s.RelevanceScore)
	}
}
```

---

## 🧪 Testing the SDKs

```bash
# TypeScript / Node.js
cd sdks/typescript
npm test

# .NET (requires dotnet SDK)
cd sdks/dotnet
dotnet test

# Go (requires Go toolchain)
cd sdks/go
go test -v ./...
```

---

## 📄 License & Ownership

The Address Standardizer client SDKs are open-source software owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../LICENSE)** for complete details.
