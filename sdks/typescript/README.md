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

- **Full TypeScript Type Safety**: Complete typings for `StandardizeRequest`, `StandardizeResponse`, `BatchStandardizeRequest`, `AutocompleteRequest`, and `AutocompleteSuggestion`.
- **Zero Heavy Dependencies**: Native `fetch` with configurable timeout and `AbortController` cancellation.
- **Headless Autocomplete Controller**: State machine managing debouncing, loading/error state, and the selected suggestion.
- **React Hooks**: Turnkey `useAddressAutocomplete` hook (pass React in via the `react` option).
- **High-Throughput Streaming**: `streamBatch()` for reading NDJSON streams without buffering large responses in memory.

---

## Quickstart

```typescript
import { AddressStandardizerClient } from "@address-standardizer/client";

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
for await (const record of client.streamBatch(["100 Main St, Austin, TX"])) {
  console.log(record.street1);
}
```

---

## React Integration

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

Outside React, use the headless `AutocompleteController` (`subscribe`, `setQuery`, `selectSuggestion`, `clear`).

---

## 📄 License & Ownership

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../../LICENSE)** for details.
