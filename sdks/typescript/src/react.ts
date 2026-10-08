/**
 * React Hooks for Address Standardizer.
 */

import { AutocompleteSuggestion } from "./types.js";
import { AddressStandardizerClient } from "./client.js";

export interface UseAddressAutocompleteOptions {
  client?: AddressStandardizerClient;
  /** The React module (`import React from "react"`). Falls back to `globalThis.React`. */
  react?: ReactLike;
  minChars?: number;
  debounceMs?: number;
  stateFilter?: string;
  latitude?: number;
  longitude?: number;
  radiusMiles?: number;
  maxResults?: number;
}

export interface UseAddressAutocompleteReturn {
  query: string;
  setQuery: (q: string) => void;
  suggestions: AutocompleteSuggestion[];
  isLoading: boolean;
  error: Error | null;
  selectedSuggestion: AutocompleteSuggestion | null;
  selectSuggestion: (s: AutocompleteSuggestion | null) => void;
  clear: () => void;
}

/**
 * Headless autocomplete state machine controller.
 * Can be bound to React hooks or invoked directly in state management.
 */
export class AutocompleteController {
  private client: AddressStandardizerClient;
  private options: UseAddressAutocompleteOptions;
  private timer: any = null;
  private requestId = 0;
  private inflight: AbortController | null = null;
  private listeners: Set<() => void> = new Set();

  public query: string = "";
  public suggestions: AutocompleteSuggestion[] = [];
  public isLoading: boolean = false;
  public error: Error | null = null;
  public selectedSuggestion: AutocompleteSuggestion | null = null;

  constructor(options: UseAddressAutocompleteOptions = {}) {
    this.options = options;
    this.client = options.client || new AddressStandardizerClient();
  }

  private abortInflight(): void {
    if (this.inflight) {
      this.inflight.abort();
      this.inflight = null;
    }
  }

  public subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    for (const l of this.listeners) l();
  }

  public setQuery(q: string): void {
    this.query = q;
    this.selectedSuggestion = null;
    this.error = null;
    const requestId = ++this.requestId;
    this.abortInflight();

    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }

    const minChars = this.options.minChars ?? 3;
    if (q.trim().length < minChars) {
      this.suggestions = [];
      this.isLoading = false;
      this.notify();
      return;
    }

    this.isLoading = true;
    this.notify();

    const debounceMs = this.options.debounceMs ?? 150;
    this.timer = setTimeout(async () => {
      try {
        const controller = new AbortController();
        this.inflight = controller;
        const results = await this.client.autocomplete(
          {
            query: q,
            max_results: this.options.maxResults ?? 10,
            state_filter: this.options.stateFilter,
            latitude: this.options.latitude,
            longitude: this.options.longitude,
            radius_miles: this.options.radiusMiles,
          },
          { signal: controller.signal }
        );
        if (requestId !== this.requestId) return; // superseded by a newer query or clear()
        this.suggestions = results;
        this.isLoading = false;
      } catch (err: any) {
        if (requestId !== this.requestId) return;
        this.error = err instanceof Error ? err : new Error(String(err));
        this.suggestions = [];
        this.isLoading = false;
      }
      this.notify();
    }, debounceMs);
  }

  public selectSuggestion(suggestion: AutocompleteSuggestion | null): void {
    this.selectedSuggestion = suggestion;
    if (suggestion) {
      // The query is resolved: drop any pending/in-flight lookup so it cannot reopen stale results.
      this.requestId++;
      this.abortInflight();
      if (this.timer) {
        clearTimeout(this.timer);
        this.timer = null;
      }
      this.isLoading = false;
      this.query = suggestion.text;
    }
    this.notify();
  }

  public clear(): void {
    this.requestId++;
    this.abortInflight();
    if (this.timer) {
      clearTimeout(this.timer);
      this.timer = null;
    }
    this.query = "";
    this.suggestions = [];
    this.isLoading = false;
    this.error = null;
    this.selectedSuggestion = null;
    this.notify();
  }
}

export interface ReactLike {
  useState<T>(initial: T | (() => T)): [T, (val: T | ((prev: T) => T)) => void];
  useRef<T>(initial: T): { current: T };
  useCallback<T extends (...args: any[]) => any>(fn: T, deps: any[]): T;
  /** Optional: when present the hook cancels pending work on unmount. Real React always provides it. */
  useEffect?(effect: () => void | (() => void), deps?: any[]): void;
}

/**
 * Standard React hook useAddressAutocomplete.
 *
 * Pass React in explicitly (`useAddressAutocomplete({ react: React })`) or expose it as `globalThis.React`.
 * The latest `options` are always used (changing `client`, `debounceMs`, ... takes effect on the next keystroke),
 * pending timers and in-flight lookups are dropped on unmount, and stale responses never overwrite newer state.
 */
export function useAddressAutocomplete(options: UseAddressAutocompleteOptions = {}): UseAddressAutocompleteReturn {
  const React = options.react ?? ((globalThis as any).React as ReactLike | undefined);
  if (!React || !React.useState) {
    throw new Error(
      "useAddressAutocomplete requires React: pass it as `useAddressAutocomplete({ react: React })`, " +
        "or use AutocompleteController for non-React environments."
    );
  }

  const [query, setQueryState] = React.useState("");
  const [suggestions, setSuggestions] = React.useState<AutocompleteSuggestion[]>([]);
  const [isLoading, setIsLoading] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);
  const [selectedSuggestion, setSelectedSuggestion] = React.useState<AutocompleteSuggestion | null>(null);

  // Always read the newest options inside the (stable) callbacks.
  const optionsRef = React.useRef(options);
  optionsRef.current = options;
  const defaultClientRef = React.useRef<AddressStandardizerClient | null>(null);
  const timerRef = React.useRef<any>(null);
  const requestIdRef = React.useRef(0);
  const abortRef = React.useRef<AbortController | null>(null);
  const mountedRef = React.useRef(true);

  const getClient = React.useCallback((): AddressStandardizerClient => {
    const supplied = optionsRef.current.client;
    if (supplied) return supplied;
    if (!defaultClientRef.current) defaultClientRef.current = new AddressStandardizerClient();
    return defaultClientRef.current;
  }, []);

  const cancelPending = React.useCallback(() => {
    requestIdRef.current += 1;
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
  }, []);

  if (React.useEffect) {
    React.useEffect(() => {
      mountedRef.current = true;
      return () => {
        mountedRef.current = false;
        cancelPending();
      };
    }, []);
  }

  const setQuery = React.useCallback((newQuery: string) => {
    const opts = optionsRef.current;
    cancelPending();
    const requestId = requestIdRef.current;
    setQueryState(newQuery);
    setSelectedSuggestion(null);
    setError(null);

    const minChars = opts.minChars ?? 3;
    if (newQuery.trim().length < minChars) {
      setSuggestions([]);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    timerRef.current = setTimeout(async () => {
      timerRef.current = null;
      const live = optionsRef.current;
      const controller = new AbortController();
      abortRef.current = controller;
      try {
        const results = await getClient().autocomplete(
          {
            query: newQuery,
            max_results: live.maxResults ?? 10,
            state_filter: live.stateFilter,
            latitude: live.latitude,
            longitude: live.longitude,
            radius_miles: live.radiusMiles,
          },
          { signal: controller.signal }
        );
        if (!mountedRef.current || requestId !== requestIdRef.current) return; // unmounted or superseded
        setSuggestions(results);
        setError(null);
        setIsLoading(false);
      } catch (err: any) {
        if (!mountedRef.current || requestId !== requestIdRef.current) return;
        setError(err instanceof Error ? err : new Error(String(err)));
        setSuggestions([]);
        setIsLoading(false);
      } finally {
        if (abortRef.current === controller) abortRef.current = null;
      }
    }, opts.debounceMs ?? 150);
  }, []);

  const selectSuggestion = React.useCallback((s: AutocompleteSuggestion | null) => {
    setSelectedSuggestion(s);
    if (s) {
      // The query is resolved: drop any pending/in-flight lookup so it cannot reopen stale results.
      cancelPending();
      setIsLoading(false);
      setQueryState(s.text);
    }
  }, []);

  const clear = React.useCallback(() => {
    cancelPending();
    setQueryState("");
    setSuggestions([]);
    setIsLoading(false);
    setError(null);
    setSelectedSuggestion(null);
  }, []);

  return {
    query,
    setQuery,
    suggestions,
    isLoading,
    error,
    selectedSuggestion,
    selectSuggestion,
    clear,
  };
}
