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
  normalized_address_key?: string;
  building_key?: string;
  phonetic_key?: string;
  address_status: string;
  is_us: boolean;
  is_private_residence: boolean;
  is_registered_agent_hub: boolean;
  deliverability?: Deliverability | string;
  latitude?: number;
  longitude?: number;
  precision?: string;
  accuracy_radius_meters?: number;
  census_tract?: string;
  fips_code?: string;
  confidence_score?: number;
  routing_tier?: string;
  rdi?: string;
  cmra?: boolean;
  vacant?: boolean;
  dpv_footnotes?: string[];
  corporate_risk_score?: number;
  corporate_risk_flags?: string[];
  rooftop_address?: string;
  full_rooftop_address?: string;
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
  prompt_message?: string;
  latitude?: number;
  longitude?: number;
  distance_meters?: number;
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
