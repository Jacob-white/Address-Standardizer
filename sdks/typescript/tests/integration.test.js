import test from "node:test";
import assert from "node:assert/strict";
import { AddressStandardizerClient } from "../dist/index.js";

// Runs only against a live server, e.g.:
//   ADDRESS_STANDARDIZER_URL=http://127.0.0.1:8000 npm test
const baseUrl = process.env.ADDRESS_STANDARDIZER_URL;
const opts = { skip: baseUrl ? false : "ADDRESS_STANDARDIZER_URL not set" };

test("live: standardize returns flat USPS fields", opts, async () => {
  const client = new AddressStandardizerClient({ baseUrl });
  const res = await client.standardize({
    address: "1600 Pennsylvania Ave NW, Washington, DC 20500",
    enable_geocoding: true,
  });
  assert.equal(res.state, "DC");
  assert.equal(res.postal_code, "20500");
  assert.equal(typeof res.street1, "string");
});

test("live: batch and streamBatch agree", opts, async () => {
  const client = new AddressStandardizerClient({ baseUrl });
  const addresses = ["100 Main St, Austin, TX 78701", "350 5th Ave, New York, NY 10118"];
  const batch = await client.standardizeBatch({ addresses });
  assert.equal(batch.length, 2);

  const streamed = [];
  for await (const rec of client.streamBatch(addresses)) streamed.push(rec);
  assert.equal(streamed.length, 2);
  assert.deepEqual(
    streamed.map((r) => r.street1),
    batch.map((r) => r.street1)
  );
});

test("live: autocomplete and health", opts, async () => {
  const client = new AddressStandardizerClient({ baseUrl });
  const suggestions = await client.autocomplete({ query: "100 Wall", max_results: 3 });
  assert.ok(Array.isArray(suggestions));
  for (const s of suggestions) assert.equal(typeof s.text, "string");

  const health = await client.health();
  assert.equal(typeof health.version, "string");
});

test("live: HTTP errors include the response body", opts, async () => {
  const client = new AddressStandardizerClient({ baseUrl });
  await assert.rejects(() => client.autocomplete({ query: "" }), /HTTP 422/);
});
