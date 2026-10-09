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
        public string? Country { get; set; }

        [JsonPropertyName("enable_geocoding")]
        public bool? EnableGeocoding { get; set; }

        [JsonPropertyName("enable_fuzzy")]
        public bool? EnableFuzzy { get; set; }

        [JsonPropertyName("allow_locality")]
        public bool? AllowLocality { get; set; }

        /// <summary>Replace a US state that contradicts the ZIP with the ZIP's state. Null uses the server default (false).</summary>
        [JsonPropertyName("correct_state_from_zip")]
        public bool? CorrectStateFromZip { get; set; }

        [JsonPropertyName("include_metadata")]
        public bool? IncludeMetadata { get; set; }

        /// <summary>Add <c>explanation</c> and <c>field_confidence</c> to the response (server default: false).</summary>
        [JsonPropertyName("include_explanation")]
        public bool? IncludeExplanation { get; set; }

        /// <summary>Ask for up to this many next-best interpretations (0-5, server default: 0).</summary>
        [JsonPropertyName("alternatives")]
        public int? Alternatives { get; set; }
    }

    /// <summary>One change or decision the engine made, with a stable machine-readable <c>rule</c> id.</summary>
    public class ExplanationRecord
    {
        [JsonPropertyName("field")]
        public string Field { get; set; } = "";

        [JsonPropertyName("before")]
        public string Before { get; set; } = "";

        [JsonPropertyName("after")]
        public string After { get; set; } = "";

        [JsonPropertyName("rule")]
        public string Rule { get; set; } = "";

        [JsonPropertyName("detail")]
        public Dictionary<string, object>? Detail { get; set; }
    }

    /// <summary>A next-best interpretation of an ambiguous input; <c>Score</c> is a relative plausibility, not a probability.</summary>
    public class Alternative
    {
        [JsonPropertyName("changes")]
        public Dictionary<string, string> Changes { get; set; } = new Dictionary<string, string>();

        [JsonPropertyName("reason")]
        public string Reason { get; set; } = "";

        [JsonPropertyName("score")]
        public double Score { get; set; }
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

        /// <summary>Text of a removed "c/o" / "attn" clause, if any.</summary>
        [JsonPropertyName("care_of")]
        public string? CareOf { get; set; }

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

        /// <summary>Only with <c>IncludeExplanation</c>.</summary>
        [JsonPropertyName("explanation")]
        public List<ExplanationRecord>? Explanation { get; set; }

        /// <summary>Only with <c>IncludeExplanation</c>: per-field confidence in [0, 1] (heuristic, not a probability).</summary>
        [JsonPropertyName("field_confidence")]
        public Dictionary<string, double>? FieldConfidence { get; set; }

        /// <summary>Only with <c>Alternatives</c> &gt;= 1.</summary>
        [JsonPropertyName("alternatives")]
        public List<Alternative>? Alternatives { get; set; }
    }

    public class BatchStandardizeRequest
    {
        [JsonPropertyName("addresses")]
        public List<object> Addresses { get; set; } = new List<object>();

        [JsonPropertyName("enable_geocoding")]
        public bool? EnableGeocoding { get; set; }

        [JsonPropertyName("enable_fuzzy")]
        public bool? EnableFuzzy { get; set; }

        [JsonPropertyName("allow_locality")]
        public bool? AllowLocality { get; set; }

        /// <summary>Replace a US state that contradicts the ZIP with the ZIP's state. Null uses the server default (false).</summary>
        [JsonPropertyName("correct_state_from_zip")]
        public bool? CorrectStateFromZip { get; set; }
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
