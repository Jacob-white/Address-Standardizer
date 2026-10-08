# @address-standardizer/client

Official TypeScript and JavaScript client SDK for the **Address Standardizer** HTTP microservice daemon, featuring React hooks, headless autocomplete state machine, and streaming NDJSON batch support.

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**.

---

## Installation

```bash
npm install @address-standardizer/client
# or
pnpm add @address-standardizer/client
```

Requires Node.js 18+ (or a browser) with a global `fetch`; pass `fetch` in the client options to supply your own.
`react` (>=18) is an **optional peer dependency**: it is only needed if you use `useAddressAutocomplete`. The
client, the streaming API and the headless `AutocompleteController` work without React installed.

---

## Features

- **Typed requests and responses**: `StandardizeRequest`, `StandardizeResponse`, `BatchStandardizeRequest`, `AutocompleteRequest`, `AutocompleteSuggestion`, `StreamErrorRecord`, `RequestOptions`, and more.
- **No runtime dependencies**: native `fetch`, with a per-client default timeout and per-call `AbortSignal` cancellation.
- **Typed HTTP errors**: non-2xx responses throw `AddressStandardizerHttpError` (`status`, `body`).
- **Streaming batches**: `streamBatch()` yields NDJSON records as they arrive, reports per-record errors, and detects truncated streams.
- **Headless autocomplete controller** and an optional **React hook**.

---

## Quickstart

```typescript
import {
  AddressStandardizerClient,
  AddressStandardizerHttpError,
  isStreamError,
} from "@address-standardizer/client";

const client = new AddressStandardizerClient({
  baseUrl: "http://localhost:8000", // default
  timeoutMs: 5000,                  // default 10000; 0 or Infinity disables the timeout
});

// Standardize a single address
const result = await client.standardize({
  address: "1600 Pennsylvania Ave NW, Washington, DC 20500",
  enable_geocoding: true,
  correct_state_from_zip: true, // replace a US state that contradicts the ZIP (server default: false)
});

console.log(result.street1);
console.log(result.latitude);         // number | null | undefined: not every result is geocoded
console.log(result.confidence_score); // number | null | undefined

// Batch standardization (a plain array also works)
const batch = await client.standardizeBatch({
  addresses: [
    "100 Main St, Austin, TX",
    { street1: "350 5th Ave", city: "New York", state: "NY" },
  ],
  correct_state_from_zip: true,
});
```

### Nullable response fields

Optional response fields (`latitude`, `longitude`, `precision`, `confidence_score`, `cmra`, `vacant`,
`dpv_footnotes`, `deliverability`, `rdi`, and others) are typed `... | null | undefined`. `cmra` and `vacant` are
tri-state: `true`, `false`, or `null`/`undefined` when unknown. Do not treat a missing value as `false`.

### Per-call options: cancellation and timeouts

Every client method takes an optional last argument `RequestOptions`:

```typescript
interface RequestOptions {
  signal?: AbortSignal; // abort this call (and any stream) from your side
  timeoutMs?: number;   // override the client timeout for this call; 0 disables it
}
```

```typescript
const controller = new AbortController();
const suggestions = await client.autocomplete("350 5th", {
  signal: controller.signal,
  timeoutMs: 2000,
});
// controller.abort() cancels the in-flight request
```

There is no per-call headers option; set headers for every request with the `headers` client option.
A timeout rejects with `Error("Address Standardizer request timed out after <n>ms")`; a caller abort rejects with
the usual `AbortError` from `fetch`.

### Errors

A non-2xx response throws `AddressStandardizerHttpError`, with `status`, `body`, and a message of the form
`Address Standardizer HTTP <status>: <body>`:

```typescript
try {
  await client.standardize("...");
} catch (err) {
  if (err instanceof AddressStandardizerHttpError && err.status === 429) {
    // back off and retry
  }
}
```

### Streaming large batches

`streamBatch()` is an async generator that sends one request and yields one record per input, in order, as
newline-delimited JSON arrives. It accepts an array of addresses or a full `BatchStandardizeRequest` (to set
batch-wide flags such as `correct_state_from_zip`).

```typescript
for await (const record of client.streamBatch(
  ["100 Main St, Austin, TX", "not an address"],
  { timeoutMs: 15000 }
)) {
  if (isStreamError(record)) {
    // the server could not standardize this input: { error: string, index: number }
    console.warn(`record ${record.index} failed: ${record.error}`);
    continue;
  }
  console.log(record.street1);
}
```

- **Per-record errors**: an input the server could not standardize arrives as a `StreamErrorRecord` (`{ error, index }`), and the stream continues. Narrow with `isStreamError()` before reading result fields.
- **Truncation detection**: if the stream ends before one record per input has arrived, the generator throws (`Address Standardizer stream ended after N of M record(s)`) instead of silently stopping. A malformed NDJSON line also throws.
- **Chunk and line handling**: records split across network chunks are reassembled, and both `
` and `
` line endings are accepted.
- **Cancellation**: breaking out of the loop, throwing, or aborting `signal` cancels the underlying HTTP stream.
- **Timeout**: `timeoutMs` is an *inactivity* timeout for streams. It restarts whenever data arrives, so a long stream is fine as long as it keeps flowing.
- HTTP errors (non-2xx) throw `AddressStandardizerHttpError` before the first record.

### Autocomplete, health and metrics

```typescript
const suggestions = await client.autocomplete({
  query: "350 5th",
  max_results: 5,
  state_filter: "NY",
  latitude: 40.75,
  longitude: -73.99,
  radius_miles: 25,
});

const health = await client.health();
const metrics = await client.metrics();               // JSON
const text = await client.metrics("prometheus");      // Prometheus text format
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

`useAddressAutocomplete` options: `client`, `react`, `minChars` (default 3), `debounceMs` (default 150), `maxResults` (default 10), `stateFilter`, `latitude`, `longitude`, `radiusMiles`. It returns `query`, `setQuery`, `suggestions`, `isLoading`, `error`, `selectedSuggestion`, `selectSuggestion` and `clear`. A newer query cancels the in-flight request and discards stale results.

Outside React (or without React installed), use the headless `AutocompleteController` (`subscribe`, `setQuery`, `selectSuggestion`, `clear`).

---

## 📄 License & Ownership

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../../LICENSE)** for details.
