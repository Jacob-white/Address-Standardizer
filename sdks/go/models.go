package standardizer

// StandardizeRequest represents a single address standardization payload.
type StandardizeRequest struct {
	Address         string `json:"address,omitempty"`
	Street1         string `json:"street1,omitempty"`
	Street2         string `json:"street2,omitempty"`
	City            string `json:"city,omitempty"`
	State           string `json:"state,omitempty"`
	PostalCode      string `json:"postal_code,omitempty"`
	Country         string `json:"country,omitempty"`
	EnableGeocoding *bool  `json:"enable_geocoding,omitempty"`
	EnableFuzzy     *bool  `json:"enable_fuzzy,omitempty"`
	AllowLocality   *bool  `json:"allow_locality,omitempty"`
	// CorrectStateFromZip replaces a US state that contradicts the ZIP with the ZIP's state (server default: false).
	CorrectStateFromZip *bool `json:"correct_state_from_zip,omitempty"`
	IncludeMetadata     *bool `json:"include_metadata,omitempty"`
	// IncludeExplanation adds Explanation and FieldConfidence to the response (server default: false).
	IncludeExplanation *bool `json:"include_explanation,omitempty"`
	// Alternatives asks for up to this many next-best interpretations (0-5, server default: 0).
	Alternatives *int `json:"alternatives,omitempty"`
}

// ExplanationRecord is one change or decision the engine made, with a stable machine-readable Rule id.
type ExplanationRecord struct {
	Field  string                 `json:"field"`
	Before string                 `json:"before"`
	After  string                 `json:"after"`
	Rule   string                 `json:"rule"`
	Detail map[string]interface{} `json:"detail"`
}

// Alternative is a next-best interpretation of an ambiguous input; Score is a relative plausibility, not a probability.
type Alternative struct {
	Changes map[string]string `json:"changes"`
	Reason  string            `json:"reason"`
	Score   float64           `json:"score"`
}

// StandardizedAddress represents an ISO / USPS Pub 28 standardized address.
type StandardizedAddress struct {
	Street1              string                 `json:"street1"`
	Street2              string                 `json:"street2"`
	City                 string                 `json:"city"`
	State                string                 `json:"state"`
	PostalCode           string                 `json:"postal_code"`
	Country              string                 `json:"country"`
	CountryISO3          string                 `json:"country_iso3"`
	NormalizedAddressKey string                 `json:"normalized_address_key"`
	BuildingKey          string                 `json:"building_key"`
	PhoneticKey          string                 `json:"phonetic_key"`
	AddressStatus        string                 `json:"address_status"`
	IsUS                 bool                   `json:"is_us"`
	IsPrivateResidence   bool                   `json:"is_private_residence"`
	IsRegisteredAgentHub bool                   `json:"is_registered_agent_hub"`
	Deliverability       string                 `json:"deliverability"`
	Latitude             *float64               `json:"latitude"`
	Longitude            *float64               `json:"longitude"`
	Precision            string                 `json:"precision"`
	AccuracyRadiusMeters *float64               `json:"accuracy_radius_meters"`
	CensusTract          string                 `json:"census_tract"`
	FIPSCode             string                 `json:"fips_code"`
	CareOf               *string                `json:"care_of"` // removed "c/o" / "attn" clause, if any
	ConfidenceScore      *float64               `json:"confidence_score"`
	RoutingTier          string                 `json:"routing_tier"`
	RDI                  string                 `json:"rdi"`
	CMRA                 *bool                  `json:"cmra"`
	Vacant               *bool                  `json:"vacant"`
	DPVFootnotes         []string               `json:"dpv_footnotes"`
	CorporateRiskScore   *float64               `json:"corporate_risk_score"`
	CorporateRiskFlags   []string               `json:"corporate_risk_flags"`
	RooftopAddress       string                 `json:"rooftop_address"`
	FullRooftopAddress   string                 `json:"full_rooftop_address"`
	Explanation          []ExplanationRecord    `json:"explanation"`      // only with IncludeExplanation
	FieldConfidence      map[string]float64     `json:"field_confidence"` // per-field, heuristic; only with IncludeExplanation
	Alternatives         []Alternative          `json:"alternatives"`     // only with Alternatives >= 1
	RawStreetAddress     string                 `json:"raw_street_address,omitempty"`
	Extra                map[string]interface{} `json:"-"`
}

// BatchStandardizeRequest contains a list of address items to standardize.
type BatchStandardizeRequest struct {
	Addresses           []interface{} `json:"addresses"`
	EnableGeocoding     *bool         `json:"enable_geocoding,omitempty"`
	EnableFuzzy         *bool         `json:"enable_fuzzy,omitempty"`
	AllowLocality       *bool         `json:"allow_locality,omitempty"`
	CorrectStateFromZip *bool         `json:"correct_state_from_zip,omitempty"`
}

// AutocompleteRequest represents a typeahead query with optional proximity bias.
type AutocompleteRequest struct {
	Query       string   `json:"query"`
	MaxResults  int      `json:"max_results,omitempty"`
	StateFilter string   `json:"state_filter,omitempty"`
	Latitude    *float64 `json:"latitude,omitempty"`
	Longitude   *float64 `json:"longitude,omitempty"`
	RadiusMiles *float64 `json:"radius_miles,omitempty"`
}

// AutocompleteSuggestion represents an individual suggestion with metadata.
type AutocompleteSuggestion struct {
	Text                    string   `json:"text"`
	StreetLine              string   `json:"street_line"`
	City                    string   `json:"city"`
	State                   string   `json:"state"`
	PostalCode              string   `json:"postal_code"`
	SecondaryPromptRequired bool     `json:"secondary_prompt_required"`
	SuggestedSecondaryUnits []string `json:"suggested_secondary_units"`
	PromptMessage           string   `json:"prompt_message,omitempty"`
	Latitude                *float64 `json:"latitude,omitempty"`
	Longitude               *float64 `json:"longitude,omitempty"`
	DistanceMeters          *float64 `json:"distance_meters,omitempty"`
}

// AutocompleteResponse holds the suggestion list and total count.
type AutocompleteResponse struct {
	Suggestions []AutocompleteSuggestion `json:"suggestions"`
	Count       int                      `json:"count"`
}

// HealthResponse represents daemon health and telemetry diagnostics.
type HealthResponse struct {
	Status        string                 `json:"status"`
	Version       string                 `json:"version"`
	Engine        map[string]interface{} `json:"engine"`
	UptimeSeconds float64                `json:"uptime_seconds"`
}

// Bool returns a pointer to v, for setting optional request flags such as
// EnableGeocoding. A nil flag is omitted so the server default applies.
func Bool(v bool) *bool { return &v }
