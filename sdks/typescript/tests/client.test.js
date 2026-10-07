import test from "node:test";
import assert from "node:assert/strict";
import { AddressStandardizerClient, AutocompleteController } from "../dist/index.js";

test("AddressStandardizerClient - standardize single address", async () => {
  const mockFetch = async (url, options) => {
    assert.equal(url, "http://localhost:8000/v1/standardize");
    assert.equal(options.method, "POST");
    const body = JSON.parse(options.body);
    assert.equal(body.address, "1600 Pennsylvania Ave NW, Washington, DC 20500");

    return {
      ok: true,
      status: 200,
      json: async () => ({
        street1: "1600 PENNSYLVANIA AVE NW",
        street2: "",
        city: "WASHINGTON",
        state: "DC",
        postal_code: "20500",
        country: "USA",
        country_iso3: "USA",
        normalized_address_key: "1600 PENNSYLVANIA AVE NW||WASHINGTON|DC|20500|USA",
        address_status: "standardized",
        is_us: true,
        is_private_residence: false,
        is_registered_agent_hub: false,
        deliverability: "DELIVERABLE",
        latitude: 38.898,
        longitude: -77.036,
        precision: "RANGE_INTERPOLATED",
      }),
    };
  };

  const client = new AddressStandardizerClient({ fetch: mockFetch });
  const result = await client.standardize("1600 Pennsylvania Ave NW, Washington, DC 20500");

  assert.equal(result.street1, "1600 PENNSYLVANIA AVE NW");
  assert.equal(result.city, "WASHINGTON");
  assert.equal(result.state, "DC");
  assert.equal(result.postal_code, "20500");
  assert.equal(result.deliverability, "DELIVERABLE");
  assert.equal(result.precision, "RANGE_INTERPOLATED");
  assert.equal(result.latitude, 38.898);
});

test("AddressStandardizerClient - standardize batch request", async () => {
  const mockFetch = async (url, options) => {
    assert.equal(url, "http://localhost:8000/v1/batch");
    assert.equal(options.method, "POST");
    const body = JSON.parse(options.body);
    assert.equal(body.addresses.length, 2);

    return {
      ok: true,
      status: 200,
      json: async () => [
        {
          street1: "100 WALL ST",
          city: "NEW YORK",
          state: "NY",
          postal_code: "10005",
          deliverability: "DELIVERABLE",
          latitude: 40.7061,
          longitude: -74.006,
        },
        {
          street1: "350 5TH AVE",
          city: "NEW YORK",
          state: "NY",
          postal_code: "10118",
          deliverability: "DELIVERABLE",
          latitude: 40.7484,
          longitude: -73.9857,
        },
      ],
    };
  };

  const client = new AddressStandardizerClient({ fetch: mockFetch });
  const results = await client.standardizeBatch(["100 Wall St, NY", "350 5th Ave, NY"]);

  assert.equal(results.length, 2);
  assert.equal(results[0].street1, "100 WALL ST");
  assert.equal(results[1].street1, "350 5TH AVE");
});

test("AddressStandardizerClient - stream batch NDJSON", async () => {
  const ndjsonContent =
    JSON.stringify({ street1: "100 WALL ST", deliverability: "DELIVERABLE" }) +
    "\n" +
    JSON.stringify({ street1: "200 PARK AVE", deliverability: "DELIVERABLE" }) +
    "\n";

  const mockFetch = async (url, options) => {
    assert.equal(url, "http://localhost:8000/v1/batch");
    assert.equal(options.headers.Accept, "application/x-ndjson");

    async function* makeChunks() {
      yield Buffer.from(ndjsonContent);
    }

    return {
      ok: true,
      status: 200,
      body: makeChunks(),
    };
  };

  const client = new AddressStandardizerClient({ fetch: mockFetch });
  const streamed = [];
  for await (const item of client.streamBatch(["100 Wall St", "200 Park Ave"])) {
    streamed.push(item);
  }

  assert.equal(streamed.length, 2);
  assert.equal(streamed[0].street1, "100 WALL ST");
  assert.equal(streamed[1].street1, "200 PARK AVE");
});

test("AddressStandardizerClient - autocomplete with proximity biasing", async () => {
  const mockFetch = async (url, options) => {
    assert.equal(url, "http://localhost:8000/v1/autocomplete");
    const body = JSON.parse(options.body);
    assert.equal(body.query, "100 Wall");
    assert.equal(body.latitude, 40.7);
    assert.equal(body.longitude, -74.0);

    return {
      ok: true,
      status: 200,
      json: async () => ({
        count: 1,
        suggestions: [
          {
            text: "100 WALL ST, NEW YORK, NY 10005",
            street_line: "100 WALL ST",
            city: "NEW YORK",
            state: "NY",
            postal_code: "10005",
            secondary_prompt_required: true,
            suggested_secondary_units: ["STE", "APT", "FL"],
            prompt_message: "Requires Suite / Apartment Number",
            latitude: 40.7061,
            longitude: -74.006,
            distance_meters: 678.5,
          },
        ],
      }),
    };
  };

  const client = new AddressStandardizerClient({ fetch: mockFetch });
  const suggestions = await client.autocomplete({
    query: "100 Wall",
    latitude: 40.7,
    longitude: -74.0,
  });

  assert.equal(suggestions.length, 1);
  assert.equal(suggestions[0].street_line, "100 WALL ST");
  assert.equal(suggestions[0].secondary_prompt_required, true);
  assert.equal(suggestions[0].prompt_message, "Requires Suite / Apartment Number");
  assert.equal(suggestions[0].distance_meters, 678.5);
});

test("AddressStandardizerClient - health diagnostics", async () => {
  const mockFetch = async (url) => {
    assert.equal(url, "http://localhost:8000/health");
    return {
      ok: true,
      status: 200,
      json: async () => ({
        status: "healthy",
        version: "3.2.0",
        engine: { native_acceleration: true },
        uptime_seconds: 42.5,
      }),
    };
  };

  const client = new AddressStandardizerClient({ fetch: mockFetch });
  const h = await client.health();
  assert.equal(h.status, "healthy");
  assert.equal(h.version, "3.2.0");
  assert.equal(h.engine.native_acceleration, true);
});

test("AutocompleteController - headless state machine", async () => {
  const mockFetch = async () => ({
    ok: true,
    status: 200,
    json: async () => ({
      count: 1,
      suggestions: [
        {
          text: "100 WALL ST, NEW YORK, NY 10005",
          street_line: "100 WALL ST",
          city: "NEW YORK",
          state: "NY",
          postal_code: "10005",
          secondary_prompt_required: false,
          suggested_secondary_units: [],
        },
      ],
    }),
  });

  const client = new AddressStandardizerClient({ fetch: mockFetch });
  const controller = new AutocompleteController({ client, debounceMs: 10, minChars: 3 });

  controller.setQuery("10"); // Under minChars
  assert.equal(controller.suggestions.length, 0);

  controller.setQuery("100 Wall");
  assert.equal(controller.isLoading, true);

  await new Promise((resolve) => setTimeout(resolve, 30));

  assert.equal(controller.isLoading, false);
  assert.equal(controller.suggestions.length, 1);
  assert.equal(controller.suggestions[0].street_line, "100 WALL ST");

  controller.selectSuggestion(controller.suggestions[0]);
  assert.equal(controller.selectedSuggestion?.street_line, "100 WALL ST");
  assert.equal(controller.query, "100 WALL ST, NEW YORK, NY 10005");

  controller.clear();
  assert.equal(controller.query, "");
  assert.equal(controller.suggestions.length, 0);
  assert.equal(controller.selectedSuggestion, null);
});
