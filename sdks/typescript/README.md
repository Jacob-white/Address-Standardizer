# @address-standardizer/client 📦

Official TypeScript and JavaScript client SDK for the **Address Standardizer** HTTP microservice daemon, featuring React hooks, headless autocomplete state machine, and streaming NDJSON batch support.

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**.

---

## Installation

```bash
npm install @address-standardizer/client
# or
pnpm add @address-standardizer/client
```

---

## Features

- **Full TypeScript Type Safety**: Complete typings for `StandardizedAddress`, `SpatialResolutionResult`, `DeliveryIntelligence`, `CorporateRiskEvaluation`, and `AutocompleteSuggestion`.
- **Zero Heavy Dependencies**: Native `fetch` with configurable timeout and `AbortController` cancellation.
- **Headless Autocomplete Controller**: State machine managing debouncing, active selection index, query caching, and keyboard navigation.
- **React Hooks**: Turnkey `useAddressAutocomplete` hook with reactive updates.
- **High-Throughput Streaming**: `streamBatch()` for reading NDJSON streams without buffering large responses in memory.

---

## Quickstart

```typescript
import { AddressStandardizerClient } from "@address-standardizer/client";

const client = new AddressStandardizerClient({
  baseUrl: "http://localhost:8000",
  timeoutMs: 5000,
});

// Single address
const res = await client.standardize({
  address: "1600 Pennsylvania Ave NW, Washington, DC 20500",
  geocode: true,
});

console.log(res.delivery_line_1);       // "1600 PENNSYLVANIA AVE NW"
console.log(res.spatial?.latitude);     // 38.8977
console.log(res.confidence_score);      // 1.0

// Batch requests
const batch = await client.batch({
  records: [
    { address: "100 Main St, Austin, TX" },
    { address: "350 5th Ave, New York, NY" },
  ],
});
```

---

## React Integration

```tsx
import React from "react";
import { useAddressAutocomplete } from "@address-standardizer/client";

export function AddressSearch() {
  const { query, setQuery, suggestions, loading, selectSuggestion } = useAddressAutocomplete({
    baseUrl: "http://localhost:8000",
    debounceMs: 200,
  });

  return (
    <div className="address-search">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter address..."
      />
      {loading && <div className="spinner">Searching...</div>}
      <ul className="suggestions">
        {suggestions.map((item) => (
          <li key={item.id} onClick={() => selectSuggestion(item)}>
            {item.display_text}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 📄 License & Ownership

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../../LICENSE)** for details.
