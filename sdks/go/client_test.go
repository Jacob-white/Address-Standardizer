package standardizer_test

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	standardizer "github.com/Jacob-white/Address-Standardizer/sdks/go"
)

func TestStandardize(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/standardize" {
			t.Errorf("unexpected path: %s", r.URL.Path)
		}
		if r.Method != http.MethodPost {
			t.Errorf("unexpected method: %s", r.Method)
		}

		var req standardizer.StandardizeRequest
		if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
			t.Fatalf("failed to decode request: %v", err)
		}

		lat := 38.898
		lon := -77.036
		conf := 0.985
		resp := standardizer.StandardizedAddress{
			Street1:              "1600 PENNSYLVANIA AVE NW",
			City:                 "WASHINGTON",
			State:                "DC",
			PostalCode:           "20500",
			Country:              "USA",
			CountryISO3:          "USA",
			NormalizedAddressKey: "1600 PENNSYLVANIA AVE NW||WASHINGTON|DC|20500|USA",
			AddressStatus:        "standardized",
			Deliverability:       "DELIVERABLE",
			Latitude:             &lat,
			Longitude:            &lon,
			Precision:            "RANGE_INTERPOLATED",
			ConfidenceScore:      &conf,
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))
	defer server.Close()

	client := standardizer.NewClient(server.URL)
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()

	res, err := client.Standardize(ctx, standardizer.StandardizeRequest{
		Address: "1600 Pennsylvania Ave NW, Washington, DC 20500",
	})
	if err != nil {
		t.Fatalf("Standardize returned error: %v", err)
	}

	if res.Street1 != "1600 PENNSYLVANIA AVE NW" {
		t.Errorf("expected Street1 '1600 PENNSYLVANIA AVE NW', got %s", res.Street1)
	}
	if res.City != "WASHINGTON" {
		t.Errorf("expected City 'WASHINGTON', got %s", res.City)
	}
	if res.Deliverability != "DELIVERABLE" {
		t.Errorf("expected Deliverability 'DELIVERABLE', got %s", res.Deliverability)
	}
	if res.Latitude == nil || *res.Latitude != 38.898 {
		t.Errorf("expected latitude 38.898, got %v", res.Latitude)
	}
}

func TestAutocomplete(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/v1/autocomplete" {
			t.Errorf("unexpected path: %s", r.URL.Path)
		}

		dist := 450.0
		resp := standardizer.AutocompleteResponse{
			Count: 1,
			Suggestions: []standardizer.AutocompleteSuggestion{
				{
					Text:                    "100 WALL ST, NEW YORK, NY 10005",
					StreetLine:              "100 WALL ST",
					City:                    "NEW YORK",
					State:                   "NY",
					PostalCode:              "10005",
					SecondaryPromptRequired: true,
					SuggestedSecondaryUnits: []string{"STE", "APT"},
					PromptMessage:           "Requires Suite / Apartment Number",
					DistanceMeters:          &dist,
				},
			},
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))
	defer server.Close()

	client := standardizer.NewClient(server.URL)
	suggestions, err := client.Autocomplete(context.Background(), standardizer.AutocompleteRequest{
		Query: "100 Wall",
	})
	if err != nil {
		t.Fatalf("Autocomplete failed: %v", err)
	}

	if len(suggestions) != 1 {
		t.Fatalf("expected 1 suggestion, got %d", len(suggestions))
	}
	if !suggestions[0].SecondaryPromptRequired {
		t.Errorf("expected secondary prompt required")
	}
	if suggestions[0].PromptMessage != "Requires Suite / Apartment Number" {
		t.Errorf("unexpected prompt message: %s", suggestions[0].PromptMessage)
	}
}

func TestHealth(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		resp := standardizer.HealthResponse{
			Status:        "healthy",
			Version:       "3.2.0",
			Engine:        map[string]interface{}{"native_acceleration": true},
			UptimeSeconds: 12.34,
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(resp)
	}))
	defer server.Close()

	client := standardizer.NewClient(server.URL)
	h, err := client.Health(context.Background())
	if err != nil {
		t.Fatalf("Health failed: %v", err)
	}
	if h.Status != "healthy" || h.Version != "3.2.0" {
		t.Errorf("unexpected health response: %+v", h)
	}
}

func TestAPIErrorCarriesStatusAndBody(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusTooManyRequests)
		_, _ = w.Write([]byte(`{"detail":"slow down"}`))
	}))
	defer server.Close()

	client := standardizer.NewClient(server.URL)
	_, err := client.Standardize(context.Background(), standardizer.StandardizeRequest{Address: "x"})

	var apiErr *standardizer.APIError
	if !errors.As(err, &apiErr) {
		t.Fatalf("expected *APIError, got %T: %v", err, err)
	}
	if apiErr.StatusCode != http.StatusTooManyRequests || !strings.Contains(apiErr.Body, "slow down") {
		t.Fatalf("unexpected APIError: %+v", apiErr)
	}
}
