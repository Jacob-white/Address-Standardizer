package standardizer_test

import (
	"context"
	"os"
	"strings"
	"testing"
	"time"

	standardizer "github.com/Jacob-white/Address-Standardizer/sdks/go"
)

// Integration tests run only against a live server, e.g.:
//
//	ADDRESS_STANDARDIZER_URL=http://127.0.0.1:8000 go test ./...
func liveClient(t *testing.T) (*standardizer.Client, context.Context) {
	t.Helper()
	url := os.Getenv("ADDRESS_STANDARDIZER_URL")
	if url == "" {
		t.Skip("ADDRESS_STANDARDIZER_URL not set")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	t.Cleanup(cancel)
	return standardizer.NewClient(url), ctx
}

func TestLiveStandardizeBatchStream(t *testing.T) {
	client, ctx := liveClient(t)

	res, err := client.Standardize(ctx, standardizer.StandardizeRequest{
		Address:         "1600 Pennsylvania Ave NW, Washington, DC 20500",
		EnableGeocoding: standardizer.Bool(true),
	})
	if err != nil {
		t.Fatalf("Standardize: %v", err)
	}
	if res.State != "DC" || res.PostalCode != "20500" {
		t.Fatalf("unexpected result: %+v", res)
	}

	addrs := []string{"100 Main St, Austin, TX 78701", "350 5th Ave, New York, NY 10118"}
	batchReq := standardizer.BatchStandardizeRequest{}
	for _, a := range addrs {
		batchReq.Addresses = append(batchReq.Addresses, a)
	}
	batch, err := client.StandardizeBatch(ctx, batchReq)
	if err != nil {
		t.Fatalf("StandardizeBatch: %v", err)
	}
	if len(batch) != 2 {
		t.Fatalf("expected 2 batch results, got %d", len(batch))
	}

	out, errs := client.StreamBatch(ctx, addrs)
	n := 0
	for item := range out {
		if item.Street1 != batch[n].Street1 {
			t.Errorf("stream[%d]=%q, batch=%q", n, item.Street1, batch[n].Street1)
		}
		n++
	}
	if err := <-errs; err != nil {
		t.Fatalf("StreamBatch: %v", err)
	}
	if n != 2 {
		t.Fatalf("expected 2 streamed results, got %d", n)
	}
}

func TestLiveAutocompleteHealthAndErrors(t *testing.T) {
	client, ctx := liveClient(t)

	if _, err := client.Autocomplete(ctx, standardizer.AutocompleteRequest{Query: "100 Wall", MaxResults: 3}); err != nil {
		t.Fatalf("Autocomplete: %v", err)
	}

	health, err := client.Health(ctx)
	if err != nil {
		t.Fatalf("Health: %v", err)
	}
	if health.Version == "" {
		t.Fatal("expected a version in the health response")
	}

	_, err = client.Autocomplete(ctx, standardizer.AutocompleteRequest{Query: ""})
	if err == nil || !strings.Contains(err.Error(), "422") {
		t.Fatalf("expected HTTP 422 error with body, got %v", err)
	}
}
