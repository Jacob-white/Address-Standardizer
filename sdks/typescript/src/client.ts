/**
 * Address Standardizer HTTP Client.
 */

import {
  AutocompleteRequest,
  AutocompleteResponse,
  AutocompleteSuggestion,
  BatchStandardizeRequest,
  ClientOptions,
  HealthResponse,
  RequestOptions,
  StandardizeRequest,
  StandardizeResponse,
  StreamErrorRecord,
} from "./types.js";

/** Non-2xx response from the service. `message` keeps the "Address Standardizer HTTP <status>: <body>" form. */
export class AddressStandardizerHttpError extends Error {
  readonly status: number;
  readonly body: string;

  constructor(status: number, body: string) {
    super(`Address Standardizer HTTP ${status}: ${body}`);
    this.name = "AddressStandardizerHttpError";
    this.status = status;
    this.body = body;
  }
}

/** True when a streamed record is a per-item error line ({"error": ..., "index": n}) rather than a result. */
export function isStreamError(record: StandardizeResponse | StreamErrorRecord): record is StreamErrorRecord {
  return typeof (record as StreamErrorRecord).error === "string" && !("street1" in record);
}

function trimTrailingSlashes(url: string): string {
  let end = url.length;
  while (end > 0 && url.charCodeAt(end - 1) === 47) end--;
  return url.slice(0, end);
}

export class AddressStandardizerClient {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;
  private readonly fetchFn: typeof fetch;
  private readonly defaultHeaders: Record<string, string>;

  constructor(options: ClientOptions = {}) {
    this.baseUrl = trimTrailingSlashes(options.baseUrl || "http://localhost:8000");
    // 0 (or Infinity) disables the timeout; undefined uses the 10 s default.
    this.timeoutMs = options.timeoutMs ?? 10000;
    this.fetchFn = options.fetch || (typeof globalThis.fetch === "function" ? globalThis.fetch.bind(globalThis) : (null as any));
    this.defaultHeaders = {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(options.headers || {}),
    };
  }

  /**
   * Creates an AbortController that fires on the caller's signal or after `timeoutMs` of inactivity.
   * `touch()` restarts the inactivity timer (used between stream chunks); `dispose()` clears it.
   */
  private abortScope(options: RequestOptions | undefined) {
    const timeoutMs = options?.timeoutMs ?? this.timeoutMs;
    const controller = new AbortController();
    let timer: ReturnType<typeof setTimeout> | null = null;
    let timedOut = false;

    const onCallerAbort = () => controller.abort();
    if (options?.signal) {
      if (options.signal.aborted) controller.abort();
      else options.signal.addEventListener("abort", onCallerAbort, { once: true });
    }

    const touch = () => {
      if (timer) clearTimeout(timer);
      if (timeoutMs > 0 && Number.isFinite(timeoutMs)) {
        timer = setTimeout(() => {
          timedOut = true;
          controller.abort();
        }, timeoutMs);
      }
    };
    const dispose = () => {
      if (timer) clearTimeout(timer);
      options?.signal?.removeEventListener("abort", onCallerAbort);
    };
    const wrap = (err: unknown): unknown =>
      timedOut ? new Error(`Address Standardizer request timed out after ${timeoutMs}ms`) : err;
    return { signal: controller.signal, touch, dispose, wrap };
  }

  private async failFromResponse(response: Response): Promise<never> {
    let body: string;
    try {
      body = await response.text();
    } catch {
      body = response.statusText;
    }
    throw new AddressStandardizerHttpError(response.status, body);
  }

  private async request<T>(path: string, init: RequestInit = {}, options?: RequestOptions, asText = false): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const scope = this.abortScope(options);
    scope.touch();
    try {
      const response = await this.fetchFn(url, {
        ...init,
        headers: {
          ...this.defaultHeaders,
          ...(init.headers || {}),
        },
        signal: scope.signal,
      });

      if (!response.ok) {
        await this.failFromResponse(response);
      }

      return (asText ? await response.text() : await response.json()) as T;
    } catch (err) {
      throw scope.wrap(err);
    } finally {
      scope.dispose();
    }
  }

  /**
   * Standardize a single address string or structured address object.
   */
  async standardize(request: StandardizeRequest | string, options?: RequestOptions): Promise<StandardizeResponse> {
    const payload: StandardizeRequest = typeof request === "string" ? { address: request } : request;
    return this.request<StandardizeResponse>("/v1/standardize", {
      method: "POST",
      body: JSON.stringify(payload),
    }, options);
  }

  /**
   * Standardize a batch of addresses in a single high-throughput request.
   */
  async standardizeBatch(
    request: BatchStandardizeRequest | (string | StandardizeRequest)[],
    options?: RequestOptions
  ): Promise<StandardizeResponse[]> {
    const payload: BatchStandardizeRequest = Array.isArray(request)
      ? { addresses: request }
      : request;
    return this.request<StandardizeResponse[]>("/v1/batch", {
      method: "POST",
      body: JSON.stringify(payload),
    }, options);
  }

  /**
   * Stream batch results as newline-delimited JSON (NDJSON), one record per input, in order.
   *
   * - Breaking out of the loop (or throwing) cancels the underlying HTTP stream.
   * - `timeoutMs` is an *inactivity* timeout: the stream may run as long as data keeps arriving.
   * - A record the server could not standardize arrives as a {@link StreamErrorRecord}; use {@link isStreamError}.
   * - A stream that ends before one record per input has arrived throws instead of silently truncating.
   *
   * Pass a {@link BatchStandardizeRequest} to set batch-wide flags such as `correct_state_from_zip`.
   */
  async *streamBatch(
    addresses: (string | StandardizeRequest)[] | BatchStandardizeRequest,
    options?: RequestOptions
  ): AsyncGenerator<StandardizeResponse | StreamErrorRecord, void, undefined> {
    const payload: BatchStandardizeRequest = Array.isArray(addresses) ? { addresses } : addresses;
    const expected = payload.addresses.length;
    const url = `${this.baseUrl}/v1/batch`;
    const scope = this.abortScope(options);
    scope.touch();
    let reader: any = null;
    let received = 0;

    try {
      const response = await this.fetchFn(url, {
        method: "POST",
        headers: {
          ...this.defaultHeaders,
          Accept: "application/x-ndjson",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        signal: scope.signal,
      });

      if (!response.ok) {
        await this.failFromResponse(response);
      }
      if (!response.body) {
        throw new Error("Address Standardizer response body is not readable");
      }

      const parse = (line: string): StandardizeResponse | StreamErrorRecord => {
        try {
          return JSON.parse(line) as StandardizeResponse | StreamErrorRecord;
        } catch {
          throw new Error(`Address Standardizer returned an invalid NDJSON line after ${received} record(s)`);
        }
      };

      const body: any = response.body;
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      const chunks: AsyncIterable<Uint8Array | string> =
        typeof body.getReader === "function"
          ? (async function* () {
              reader = body.getReader();
              while (true) {
                const { done, value } = await reader.read();
                if (done) return;
                yield value as Uint8Array;
              }
            })()
          : typeof body[Symbol.asyncIterator] === "function"
            ? (body as AsyncIterable<Uint8Array | string>)
            : (() => {
                throw new Error("Address Standardizer response body is not a readable stream");
              })();

      for await (const chunk of chunks) {
        scope.touch();
        buffer += typeof chunk === "string" ? chunk : decoder.decode(chunk, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed) {
            received += 1;
            yield parse(trimmed);
          }
        }
      }
      buffer += decoder.decode();
      if (buffer.trim()) {
        received += 1;
        yield parse(buffer.trim());
      }

      if (received < expected) {
        throw new Error(`Address Standardizer stream ended after ${received} of ${expected} record(s)`);
      }
    } catch (err) {
      throw scope.wrap(err);
    } finally {
      scope.dispose();
      try {
        // Early exit (break/throw) must release the connection.
        if (reader) await reader.cancel();
      } catch {
        /* the stream may already be closed */
      }
    }
  }

  /**
   * Real-time typeahead autocomplete with proximity radius biasing and secondary prompting.
   */
  async autocomplete(request: AutocompleteRequest | string, options?: RequestOptions): Promise<AutocompleteSuggestion[]> {
    const payload: AutocompleteRequest = typeof request === "string" ? { query: request } : request;
    const res = await this.request<AutocompleteResponse>("/v1/autocomplete", {
      method: "POST",
      body: JSON.stringify(payload),
    }, options);
    return res.suggestions;
  }

  /**
   * Health and readiness diagnostics check.
   */
  async health(options?: RequestOptions): Promise<HealthResponse> {
    return this.request<HealthResponse>("/health", { method: "GET" }, options);
  }

  /**
   * Performance metrics and telemetry data.
   */
  async metrics(format: "json" | "prometheus" = "json", options?: RequestOptions): Promise<any> {
    if (format === "prometheus") {
      return this.request<string>("/metrics?format=prometheus", { method: "GET", headers: { Accept: "text/plain" } }, options, true);
    }
    return this.request<any>("/metrics", { method: "GET" }, options);
  }
}
