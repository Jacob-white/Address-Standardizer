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
  StandardizeRequest,
  StandardizeResponse,
} from "./types.js";

export class AddressStandardizerClient {
  private readonly baseUrl: string;
  private readonly timeoutMs: number;
  private readonly fetchFn: typeof fetch;
  private readonly defaultHeaders: Record<string, string>;

  constructor(options: ClientOptions = {}) {
    this.baseUrl = (options.baseUrl || "http://localhost:8000").replace(/\/+$/, "");
    this.timeoutMs = options.timeoutMs || 10000;
    this.fetchFn = options.fetch || (typeof globalThis.fetch === "function" ? globalThis.fetch.bind(globalThis) : (null as any));
    this.defaultHeaders = {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(options.headers || {}),
    };
  }

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${path}`;
    const controller = typeof AbortController !== "undefined" ? new AbortController() : null;
    const timeoutId = controller ? setTimeout(() => controller.abort(), this.timeoutMs) : null;

    try {
      const response = await this.fetchFn(url, {
        ...init,
        headers: {
          ...this.defaultHeaders,
          ...(init.headers || {}),
        },
        signal: controller ? controller.signal : undefined,
      });

      if (!response.ok) {
        let errBody: string;
        try {
          errBody = await response.text();
        } catch {
          errBody = response.statusText;
        }
        throw new Error(`Address Standardizer HTTP ${response.status}: ${errBody}`);
      }

      return (await response.json()) as T;
    } finally {
      if (timeoutId) clearTimeout(timeoutId);
    }
  }

  /**
   * Standardize a single address string or structured address object.
   */
  async standardize(request: StandardizeRequest | string): Promise<StandardizeResponse> {
    const payload: StandardizeRequest = typeof request === "string" ? { address: request } : request;
    return this.request<StandardizeResponse>("/v1/standardize", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  /**
   * Standardize a batch of addresses in a single high-throughput request.
   */
  async standardizeBatch(
    request: BatchStandardizeRequest | (string | StandardizeRequest)[]
  ): Promise<StandardizeResponse[]> {
    const payload: BatchStandardizeRequest = Array.isArray(request)
      ? { addresses: request }
      : request;
    return this.request<StandardizeResponse[]>("/v1/batch", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  /**
   * Stream batch standardized addresses via newline-delimited JSON (NDJSON).
   */
  async *streamBatch(
    addresses: (string | StandardizeRequest)[]
  ): AsyncIterable<StandardizeResponse> {
    const url = `${this.baseUrl}/v1/batch`;
    const response = await this.fetchFn(url, {
      method: "POST",
      headers: {
        ...this.defaultHeaders,
        Accept: "application/x-ndjson",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ addresses }),
    });

    if (!response.ok) {
      throw new Error(`Failed to stream batch: HTTP ${response.status}`);
    }

    if (!response.body) {
      throw new Error("Response body is not readable");
    }

    // Node.js or browser web stream reader
    if (typeof (response.body as any).getReader === "function") {
      const reader = (response.body as any).getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed) {
            yield JSON.parse(trimmed) as StandardizeResponse;
          }
        }
      }
      if (buffer.trim()) {
        yield JSON.parse(buffer.trim()) as StandardizeResponse;
      }
    } else if (typeof (response.body as any)[Symbol.asyncIterator] === "function") {
      // Node.js Readable stream
      let buffer = "";
      const decoder = new TextDecoder("utf-8");
      for await (const chunk of response.body as any) {
        buffer += typeof chunk === "string" ? chunk : decoder.decode(chunk, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          const trimmed = line.trim();
          if (trimmed) {
            yield JSON.parse(trimmed) as StandardizeResponse;
          }
        }
      }
      if (buffer.trim()) {
        yield JSON.parse(buffer.trim()) as StandardizeResponse;
      }
    }
  }

  /**
   * Real-time typeahead autocomplete with proximity radius biasing and secondary prompting.
   */
  async autocomplete(request: AutocompleteRequest | string): Promise<AutocompleteSuggestion[]> {
    const payload: AutocompleteRequest = typeof request === "string" ? { query: request } : request;
    const res = await this.request<AutocompleteResponse>("/v1/autocomplete", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return res.suggestions;
  }

  /**
   * Health and readiness diagnostics check.
   */
  async health(): Promise<HealthResponse> {
    return this.request<HealthResponse>("/health", { method: "GET" });
  }

  /**
   * Performance metrics and telemetry data.
   */
  async metrics(format: "json" | "prometheus" = "json"): Promise<any> {
    if (format === "prometheus") {
      const url = `${this.baseUrl}/metrics?format=prometheus`;
      const res = await this.fetchFn(url, {
        headers: { Accept: "text/plain" },
      });
      return await res.text();
    }
    return this.request<any>("/metrics");
  }
}
