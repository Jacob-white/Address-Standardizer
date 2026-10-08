/**
 * Type definitions for Address Standardizer Client SDK.
 */

export type Deliverability = "DELIVERABLE" | "REQUIRES_SECONDARY" | "UNDELIVERABLE";

export interface StandardizeRequest {
  address?: string;
  street1?: string;
  street2?: string;
  city?: string;
  state?: string;
  postal_code?: string;
  country?: string;
  enable_geocoding?: boolean;
  enable_fuzzy?: boolean;
  allow_locality?: boolean;
  /** Replace a US state that contradicts the ZIP with the ZIP's state (default false). */
  correct_state_from_zip?: boolean;
  include_metadata?: boolean;
}

export interface StandardizeResponse {
  street1: string;
  street2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  country_iso3: string;
  normalized_address_key?: string | null;
  building_key?: string | null;
  phonetic_key?: string | null;
  address_status: string;
  is_us: boolean;
  is_private_residence: boolean;
  is_registered_agent_hub: boolean;
  deliverability?: Deliverability | string | null;
  latitude?: number | null;
  longitude?: number | null;
  precision?: string | null;
  accuracy_radius_meters?: number | null;
  census_tract?: string | null;
  fips_code?: string | null;
  /** Text of a removed "c/o" / "attn" clause (the delivery address itself never contains it). */
  care_of?: string | null;
  confidence_score?: number | null;
  routing_tier?: string | null;
  rdi?: string | null;
  cmra?: boolean | null;
  vacant?: boolean | null;
  dpv_footnotes?: string[] | null;
  corporate_risk_score?: number | null;
  corporate_risk_flags?: string[] | null;
  rooftop_address?: string | null;
  full_rooftop_address?: string | null;
  [key: string]: any;
}

export interface BatchStandardizeRequest {
  addresses: (string | StandardizeRequest)[];
  enable_geocoding?: boolean;
  enable_fuzzy?: boolean;
  allow_locality?: boolean;
  correct_state_from_zip?: boolean;
}

export interface AutocompleteRequest {
  query: string;
  max_results?: number;
  state_filter?: string;
  latitude?: number;
  longitude?: number;
  radius_miles?: number;
}

export interface AutocompleteSuggestion {
  text: string;
  street_line: string;
  city: string;
  state: string;
  postal_code: string;
  secondary_prompt_required: boolean;
  suggested_secondary_units: string[];
  prompt_message?: string | null;
  latitude?: number | null;
  longitude?: number | null;
  distance_meters?: number | null;
}

export interface AutocompleteResponse {
  suggestions: AutocompleteSuggestion[];
  count: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  engine: Record<string, any>;
  uptime_seconds: number;
}

export interface ClientOptions {
  baseUrl?: string;
  timeoutMs?: number;
  fetch?: typeof fetch;
  headers?: Record<string, string>;
}

/** Per-call options accepted by every client method. */
export interface RequestOptions {
  /** Abort the call (and any stream) from the caller's side. */
  signal?: AbortSignal;
  /** Override the client timeout for this call. For streams this is an inactivity timeout. 0 disables it. */
  timeoutMs?: number;
}

/** A record of an NDJSON batch stream the server could not standardize. */
export interface StreamErrorRecord {
  error: string;
  index: number;
}
