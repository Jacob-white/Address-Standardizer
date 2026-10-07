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
	EnableGeocoding bool   `json:"enable_geocoding"`
	EnableFuzzy     bool   `json:"enable_fuzzy"`
	AllowLocality   bool   `json:"allow_locality"`
	IncludeMetadata bool   `json:"include_metadata"`
}

// StandardizedAddress represents an ISO / USPS Pub 28 standardized address.
type StandardizedAddress struct {
	Street1               string                 `json:"street1"`
	Street2               string                 `json:"street2"`
	City                  string                 `json:"city"`
	State                 string                 `json:"state"`
	PostalCode            string                 `json:"postal_code"`
	Country               string                 `json:"country"`
	CountryISO3           string                 `json:"country_iso3"`
	NormalizedAddressKey  string                 `json:"normalized_address_key"`
	BuildingKey           string                 `json:"building_key"`
	PhoneticKey           string                 `json:"phonetic_key"`
	AddressStatus         string                 `json:"address_status"`
	IsUS                  bool                   `json:"is_us"`
	IsPrivateResidence    bool                   `json:"is_private_residence"`
	IsRegisteredAgentHub  bool                   `json:"is_registered_agent_hub"`
	Deliverability        string                 `json:"deliverability"`
	Latitude              *float64               `json:"latitude"`
	Longitude             *float64               `json:"longitude"`
	Precision             string                 `json:"precision"`
	AccuracyRadiusMeters  *float64               `json:"accuracy_radius_meters"`
	CensusTract           string                 `json:"census_tract"`
	FIPSCode              string                 `json:"fips_code"`
	ConfidenceScore       *float64               `json:"confidence_score"`
	RoutingTier           string                 `json:"routing_tier"`
	RDI                   string                 `json:"rdi"`
	CMRA                  bool                   `json:"cmra"`
	Vacant                bool                   `json:"vacant"`
	DPVFootnotes          []string               `json:"dpv_footnotes"`
	CorporateRiskScore    *float64               `json:"corporate_risk_score"`
	CorporateRiskFlags    []string               `json:"corporate_risk_flags"`
	RooftopAddress        string                 `json:"rooftop_address"`
	FullRooftopAddress    string                 `json:"full_rooftop_address"`
	RawStreetAddress      string                 `json:"raw_street_address,omitempty"`
	Extra                 map[string]interface{} `json:"-"`
}

// BatchStandardizeRequest contains a list of address items to standardize.
type BatchStandardizeRequest struct {
	Addresses       []interface{} `json:"addresses"`
	EnableGeocoding bool          `json:"enable_geocoding"`
	EnableFuzzy     bool          `json:"enable_fuzzy"`
	AllowLocality   bool          `json:"allow_locality"`
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
