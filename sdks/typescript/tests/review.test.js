import test from "node:test";
import assert from "node:assert/strict";
import {
  AddressStandardizerClient,
  AddressStandardizerHttpError,
  isStreamError,
  useAddressAutocomplete,
} from "../dist/index.js";

const enc = new TextEncoder();

/** A fetch mock returning an NDJSON web stream; records whether the consumer cancelled it. */
function streamingFetch(chunks, state = {}) {
  return async (url, init) => {
    state.requests = (state.requests || 0) + 1;
    state.signal = init.signal;
    let i = 0;
    const body = new ReadableStream({
      start(controller) {
        // Like a real fetch body: aborting the request errors the stream.
        init.signal?.addEventListener("abort", () => {
          try {
            controller.error(new DOMException("aborted", "AbortError"));
          } catch {
            /* already closed */
          }
        });
      },
      async pull(controller) {
        if (i >= chunks.length) return controller.close();
        const chunk = chunks[i++];
        if (chunk === "HANG") return new Promise(() => {}); // never resolves: simulates a stalled server
        controller.enqueue(enc.encode(chunk));
      },
      cancel() {
        state.cancelled = true;
      },
    });
    return { ok: true, status: 200, body, text: async () => "", json: async () => ({}) };
  };
}

const rec = (street) => JSON.stringify({ street1: street, city: "X" }) + "\n";

test("streamBatch handles records split across chunks, CRLF and a final line without a newline", async () => {
  const client = new AddressStandardizerClient({
    fetch: streamingFetch([rec("A").slice(0, 10), rec("A").slice(10) + rec("B").replace("\n", "\r\n"), rec("C").trim()]),
  });
  const got = [];
  for await (const r of client.streamBatch(["a", "b", "c"])) got.push(r.street1);
  assert.deepEqual(got, ["A", "B", "C"]);
});

test("streamBatch cancels the HTTP stream when the consumer breaks early", async () => {
  const state = {};
  const client = new AddressStandardizerClient({ fetch: streamingFetch([rec("A"), rec("B"), rec("C")], state) });
  for await (const r of client.streamBatch(["a", "b", "c"])) {
    assert.equal(r.street1, "A");
    break;
  }
  assert.equal(state.cancelled, true);
});

test("streamBatch inactivity timeout aborts a stalled stream", async () => {
  const client = new AddressStandardizerClient({ fetch: streamingFetch([rec("A"), "HANG"]), timeoutMs: 50 });
  const got = [];
  await assert.rejects(async () => {
    for await (const r of client.streamBatch(["a", "b"])) got.push(r.street1);
  }, /timed out|abort/i);
  assert.deepEqual(got, ["A"]);
});

test("streamBatch honours a caller AbortSignal", async () => {
  const controller = new AbortController();
  const client = new AddressStandardizerClient({ fetch: streamingFetch([rec("A"), "HANG"]), timeoutMs: 0 });
  const iter = client.streamBatch(["a", "b"], { signal: controller.signal });
  const first = await iter.next();
  assert.equal(first.value.street1, "A");
  controller.abort();
  await assert.rejects(() => iter.next());
});

test("streamBatch surfaces server per-record errors and detects truncated streams", async () => {
  const errLine = JSON.stringify({ error: "invalid record", index: 1 }) + "\n";
  const client = new AddressStandardizerClient({ fetch: streamingFetch([rec("A"), errLine, rec("C")]) });
  const kinds = [];
  for await (const r of client.streamBatch(["a", "b", "c"])) kinds.push(isStreamError(r) ? "error" : "ok");
  assert.deepEqual(kinds, ["ok", "error", "ok"]);

  const truncated = new AddressStandardizerClient({ fetch: streamingFetch([rec("A")]) });
  await assert.rejects(async () => {
    for await (const _ of truncated.streamBatch(["a", "b", "c"])) {
      /* drain */
    }
  }, /ended after 1 of 3/);
});

test("streamBatch reports invalid NDJSON lines clearly and HTTP errors with their body", async () => {
  const bad = new AddressStandardizerClient({ fetch: streamingFetch(["not json\n"]) });
  await assert.rejects(async () => {
    for await (const _ of bad.streamBatch(["a"])) {
      /* drain */
    }
  }, /invalid NDJSON line/);

  const http = new AddressStandardizerClient({
    fetch: async () => ({ ok: false, status: 413, text: async () => '{"detail":"too big"}' }),
  });
  await assert.rejects(
    async () => {
      for await (const _ of http.streamBatch(["a"])) {
        /* drain */
      }
    },
    (err) => err instanceof AddressStandardizerHttpError && err.status === 413 && /too big/.test(err.body)
  );
});

test("metrics(prometheus) throws on a failing response instead of returning the error body", async () => {
  const client = new AddressStandardizerClient({
    fetch: async () => ({ ok: false, status: 500, text: async () => "oops" }),
  });
  await assert.rejects(() => client.metrics("prometheus"), /HTTP 500: oops/);
});

test("request timeouts say so, and 0 disables the timeout", async () => {
  const slow = (delay) => async (url, init) =>
    new Promise((resolve, reject) => {
      const t = setTimeout(() => resolve({ ok: true, status: 200, json: async () => ({ ok: 1 }) }), delay);
      init.signal.addEventListener("abort", () => {
        clearTimeout(t);
        reject(new DOMException("aborted", "AbortError"));
      });
    });
  await assert.rejects(() => new AddressStandardizerClient({ fetch: slow(200), timeoutMs: 20 }).health(), /timed out after 20ms/);
  assert.deepEqual(await new AddressStandardizerClient({ fetch: slow(40), timeoutMs: 0 }).health(), { ok: 1 });
});

// ---- React hook, driven by a minimal fake React so hook semantics can be checked without react itself.
function fakeReact() {
  const slots = [];
  const effects = [];
  let cursor = 0;
  const api = {
    useState(initial) {
      const i = cursor++;
      if (!(i in slots)) slots[i] = typeof initial === "function" ? initial() : initial;
      return [slots[i], (v) => (slots[i] = typeof v === "function" ? v(slots[i]) : v)];
    },
    useRef(initial) {
      const i = cursor++;
      if (!(i in slots)) slots[i] = { current: initial };
      return slots[i];
    },
    useCallback(fn) {
      const i = cursor++;
      if (!(i in slots)) slots[i] = fn;
      return slots[i];
    },
    useEffect(fn) {
      const i = cursor++;
      if (!(i in slots)) {
        slots[i] = true;
        effects.push(fn);
      }
    },
  };
  return {
    api,
    render(fn) {
      cursor = 0;
      return fn();
    },
    mount() {
      return effects.map((e) => e()).filter(Boolean);
    },
  };
}

const suggestion = (text) => ({
  text,
  street_line: text,
  city: "X",
  state: "NY",
  postal_code: "1",
  secondary_prompt_required: false,
  suggested_secondary_units: [],
});

test("hook uses the latest client option and clears errors on a new query", async () => {
  const calls = [];
  const mk = (name, fail = false) =>
    new AddressStandardizerClient({
      fetch: async () => {
        calls.push(name);
        if (fail) return { ok: false, status: 500, text: async () => "boom" };
        return { ok: true, status: 200, json: async () => ({ count: 1, suggestions: [suggestion(name)] }) };
      },
    });
  const rt = fakeReact();
  let clientA = mk("A", true);
  const run = () => rt.render(() => useAddressAutocomplete({ react: rt.api, client: clientA, debounceMs: 1, minChars: 2 }));

  let h = run();
  h.setQuery("100");
  await new Promise((r) => setTimeout(r, 30));
  h = run();
  assert.ok(h.error, "first lookup failed");

  clientA = mk("B"); // the caller swaps the client between renders
  h = run();
  h.setQuery("100 W");
  h = run();
  assert.equal(h.error, null, "a new query clears the previous error");
  await new Promise((r) => setTimeout(r, 30));
  h = run();
  assert.deepEqual(calls, ["A", "B"]);
  assert.equal(h.suggestions[0].text, "B");
});

test("hook drops pending work on unmount", async () => {
  let called = 0;
  const client = new AddressStandardizerClient({
    fetch: async () => {
      called += 1;
      return { ok: true, status: 200, json: async () => ({ count: 0, suggestions: [] }) };
    },
  });
  const rt = fakeReact();
  const run = () => rt.render(() => useAddressAutocomplete({ react: rt.api, client, debounceMs: 20, minChars: 2 }));
  const h = run();
  const cleanups = rt.mount();
  h.setQuery("100 Wall");
  cleanups.forEach((c) => c()); // unmount before the debounce fires
  await new Promise((r) => setTimeout(r, 60));
  assert.equal(called, 0);
});
