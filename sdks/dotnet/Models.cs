using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace AddressStandardizer.Client
{
    public class StandardizeRequest
    {
        [JsonPropertyName("address")]
        public string? Address { get; set; }

        [JsonPropertyName("street1")]
        public string? Street1 { get; set; }

        [JsonPropertyName("street2")]
        public string? Street2 { get; set; }

        [JsonPropertyName("city")]
        public string? City { get; set; }

        [JsonPropertyName("state")]
        public string? State { get; set; }

        [JsonPropertyName("postal_code")]
        public string? PostalCode { get; set; }

        [JsonPropertyName("country")]
        public string? Country { get; set; } = "USA";

        [JsonPropertyName("enable_geocoding")]
        public bool EnableGeocoding { get; set; } = true;

        [JsonPropertyName("enable_fuzzy")]
        public bool EnableFuzzy { get; set; } = true;

        [JsonPropertyName("allow_locality")]
        public bool AllowLocality { get; set; } = false;

        [JsonPropertyName("include_metadata")]
        public bool IncludeMetadata { get; set; } = true;
    }

    public class StandardizedAddress
    {
        [JsonPropertyName("street1")]
        public string Street1 { get; set; } = string.Empty;

        [JsonPropertyName("street2")]
        public string Street2 { get; set; } = string.Empty;

        [JsonPropertyName("city")]
        public string City { get; set; } = string.Empty;

        [JsonPropertyName("state")]
        public string State { get; set; } = string.Empty;

        [JsonPropertyName("postal_code")]
        public string PostalCode { get; set; } = string.Empty;

        [JsonPropertyName("country")]
        public string Country { get; set; } = string.Empty;

        [JsonPropertyName("country_iso3")]
        public string CountryIso3 { get; set; } = string.Empty;

        [JsonPropertyName("normalized_address_key")]
        public string? NormalizedAddressKey { get; set; }

        [JsonPropertyName("building_key")]
        public string? BuildingKey { get; set; }

        [JsonPropertyName("phonetic_key")]
        public string? PhoneticKey { get; set; }

        [JsonPropertyName("address_status")]
        public string AddressStatus { get; set; } = string.Empty;

        [JsonPropertyName("is_us")]
        public bool IsUs { get; set; }

        [JsonPropertyName("is_private_residence")]
        public bool IsPrivateResidence { get; set; }

        [JsonPropertyName("is_registered_agent_hub")]
        public bool IsRegisteredAgentHub { get; set; }

        [JsonPropertyName("deliverability")]
        public string? Deliverability { get; set; }

        [JsonPropertyName("latitude")]
        public double? Latitude { get; set; }

        [JsonPropertyName("longitude")]
        public double? Longitude { get; set; }

        [JsonPropertyName("precision")]
        public string? Precision { get; set; }

        [JsonPropertyName("accuracy_radius_meters")]
        public double? AccuracyRadiusMeters { get; set; }

        [JsonPropertyName("census_tract")]
        public string? CensusTract { get; set; }

        [JsonPropertyName("fips_code")]
        public string? FipsCode { get; set; }

        [JsonPropertyName("confidence_score")]
        public double? ConfidenceScore { get; set; }

        [JsonPropertyName("routing_tier")]
        public string? RoutingTier { get; set; }

        [JsonPropertyName("rdi")]
        public string? Rdi { get; set; }

        [JsonPropertyName("cmra")]
        public bool? Cmra { get; set; }

        [JsonPropertyName("vacant")]
        public bool? Vacant { get; set; }

        [JsonPropertyName("dpv_footnotes")]
        public List<string>? DpvFootnotes { get; set; }

        [JsonPropertyName("corporate_risk_score")]
        public double? CorporateRiskScore { get; set; }

        [JsonPropertyName("corporate_risk_flags")]
        public List<string>? CorporateRiskFlags { get; set; }

        [JsonPropertyName("rooftop_address")]
        public string? RooftopAddress { get; set; }

        [JsonPropertyName("full_rooftop_address")]
        public string? FullRooftopAddress { get; set; }
    }

    public class BatchStandardizeRequest
    {
        [JsonPropertyName("addresses")]
        public List<object> Addresses { get; set; } = new List<object>();

        [JsonPropertyName("enable_geocoding")]
        public bool EnableGeocoding { get; set; } = true;

        [JsonPropertyName("enable_fuzzy")]
        public bool EnableFuzzy { get; set; } = true;

        [JsonPropertyName("allow_locality")]
        public bool AllowLocality { get; set; } = false;
    }

    public class AutocompleteRequest
    {
        [JsonPropertyName("query")]
        public string Query { get; set; } = string.Empty;

        [JsonPropertyName("max_results")]
        public int MaxResults { get; set; } = 10;

        [JsonPropertyName("state_filter")]
        public string? StateFilter { get; set; }

        [JsonPropertyName("latitude")]
        public double? Latitude { get; set; }

        [JsonPropertyName("longitude")]
        public double? Longitude { get; set; }

        [JsonPropertyName("radius_miles")]
        public double? RadiusMiles { get; set; }
    }

    public class AutocompleteSuggestion
    {
        [JsonPropertyName("text")]
        public string Text { get; set; } = string.Empty;

        [JsonPropertyName("street_line")]
        public string StreetLine { get; set; } = string.Empty;

        [JsonPropertyName("city")]
        public string City { get; set; } = string.Empty;

        [JsonPropertyName("state")]
        public string State { get; set; } = string.Empty;

        [JsonPropertyName("postal_code")]
        public string PostalCode { get; set; } = string.Empty;

        [JsonPropertyName("secondary_prompt_required")]
        public bool SecondaryPromptRequired { get; set; }

        [JsonPropertyName("suggested_secondary_units")]
        public List<string> SuggestedSecondaryUnits { get; set; } = new List<string>();

        [JsonPropertyName("prompt_message")]
        public string? PromptMessage { get; set; }

        [JsonPropertyName("latitude")]
        public double? Latitude { get; set; }

        [JsonPropertyName("longitude")]
        public double? Longitude { get; set; }

        [JsonPropertyName("distance_meters")]
        public double? DistanceMeters { get; set; }
    }

    public class AutocompleteResponse
    {
        [JsonPropertyName("suggestions")]
        public List<AutocompleteSuggestion> Suggestions { get; set; } = new List<AutocompleteSuggestion>();

        [JsonPropertyName("count")]
        public int Count { get; set; }
    }

    public class HealthResponse
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = string.Empty;

        [JsonPropertyName("version")]
        public string Version { get; set; } = string.Empty;

        [JsonPropertyName("engine")]
        public Dictionary<string, object>? Engine { get; set; }

        [JsonPropertyName("uptime_seconds")]
        public double UptimeSeconds { get; set; }
    }
}
