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
        const results = await this.client.autocomplete({
          query: q,
          max_results: this.options.maxResults ?? 10,
          state_filter: this.options.stateFilter,
          latitude: this.options.latitude,
          longitude: this.options.longitude,
          radius_miles: this.options.radiusMiles,
        });
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
}

/**
 * Standard React hook useAddressAutocomplete.
 * Requires react in host environment.
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

  const clientRef = React.useRef(options.client || new AddressStandardizerClient());
  const timerRef = React.useRef<any>(null);
  const requestIdRef = React.useRef(0);

  const setQuery = React.useCallback((newQuery: string) => {
    setQueryState(newQuery);
    setSelectedSuggestion(null);
    const requestId = ++requestIdRef.current;

    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }

    const minChars = options.minChars ?? 3;
    if (newQuery.trim().length < minChars) {
      setSuggestions([]);
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    const debounceMs = options.debounceMs ?? 150;
    timerRef.current = setTimeout(async () => {
      try {
        const results = await clientRef.current.autocomplete({
          query: newQuery,
          max_results: options.maxResults ?? 10,
          state_filter: options.stateFilter,
          latitude: options.latitude,
          longitude: options.longitude,
          radius_miles: options.radiusMiles,
        });
        if (requestId !== requestIdRef.current) return; // superseded by a newer query or clear()
        setSuggestions(results);
        setError(null);
        setIsLoading(false);
      } catch (err: any) {
        if (requestId !== requestIdRef.current) return;
        setError(err instanceof Error ? err : new Error(String(err)));
        setSuggestions([]);
        setIsLoading(false);
      }
    }, debounceMs);
  }, [options.minChars, options.debounceMs, options.maxResults, options.stateFilter, options.latitude, options.longitude, options.radiusMiles]);

  const selectSuggestion = React.useCallback((s: AutocompleteSuggestion | null) => {
    setSelectedSuggestion(s);
    if (s) {
      // The query is resolved: drop any pending/in-flight lookup so it cannot reopen stale results.
      requestIdRef.current++;
      if (timerRef.current) {
        clearTimeout(timerRef.current);
        timerRef.current = null;
      }
      setIsLoading(false);
      setQueryState(s.text);
    }
  }, []);

  const clear = React.useCallback(() => {
    requestIdRef.current++;
    if (timerRef.current) {
      clearTimeout(timerRef.current);
      timerRef.current = null;
    }
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
