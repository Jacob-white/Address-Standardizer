package standardizer_test

import (
	"context"
	"errors"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"sync/atomic"
	"testing"
	"time"

	standardizer "github.com/Jacob-white/Address-Standardizer/sdks/go"
)

// The fixtures in testdata/ are responses captured from the real Python server (see tests/test_sdk_contract.py),
// so these tests exercise the actual wire format (nulls, field names) rather than the SDK's own structs.

func fixture(t *testing.T, name string) []byte {
	t.Helper()
	data, err := os.ReadFile("testdata/" + name)
	if err != nil {
		t.Fatalf("read fixture %s: %v", name, err)
	}
	return data
}

func serveFixture(t *testing.T, name string) *httptest.Server {
	t.Helper()
	body := fixture(t, name)
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_, _ = w.Write(body)
	}))
	t.Cleanup(srv.Close)
	return srv
}

func TestStandardizeDecodesRealServerPayload(t *testing.T) {
	srv := serveFixture(t, "standardize_response.json")
	res, err := standardizer.NewClient(srv.URL).Standardize(context.Background(), standardizer.StandardizeRequest{Address: "x"})
	if err != nil {
		t.Fatalf("Standardize: %v", err)
	}
	if res.State != "DC" || res.PostalCode != "20500" || res.Street1 == "" {
		t.Fatalf("unexpected result: %+v", res)
	}
	if res.CMRA == nil || res.Vacant == nil {
		t.Fatalf("tri-state flags should decode when the server sends booleans: %+v", res)
	}
}

func TestUnresolvedGeocodeHasNoCoordinates(t *testing.T) {
	srv := serveFixture(t, "standardize_unresolved.json")
	res, err := standardizer.NewClient(srv.URL).Standardize(context.Background(), standardizer.StandardizeRequest{Address: "x"})
	if err != nil {
		t.Fatalf("Standardize: %v", err)
	}
	if res.Latitude != nil && *res.Latitude == 0 && res.Longitude != nil && *res.Longitude == 0 {
		t.Fatalf("an unresolved lookup must not look like a real point at (0, 0): %+v", res)
	}
}

func TestAutocompleteAndHealthDecodeRealPayloads(t *testing.T) {
	srv := serveFixture(t, "autocomplete_response.json")
	suggestions, err := standardizer.NewClient(srv.URL).AutocompleteGet(context.Background(), "100 Wall", 3, "")
	if err != nil {
		t.Fatalf("AutocompleteGet: %v", err)
	}
	for _, s := range suggestions {
		if s.Text == "" {
			t.Fatalf("empty suggestion text: %+v", s)
		}
	}

	hsrv := serveFixture(t, "health_response.json")
	health, err := standardizer.NewClient(hsrv.URL).Health(context.Background())
	if err != nil || health.Version == "" {
		t.Fatalf("Health: %v %+v", err, health)
	}
}

func TestAutocompleteGetSendsProximityParameters(t *testing.T) {
	var gotQuery string
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		gotQuery = r.URL.RawQuery
		_, _ = w.Write([]byte(`{"suggestions":[],"count":0}`))
	}))
	defer srv.Close()

	lat, lon, radius := 40.7, -74.0, 5.0
	_, err := standardizer.NewClient(srv.URL).AutocompleteGetRequest(context.Background(), standardizer.AutocompleteRequest{
		Query: "100 wall", MaxResults: 7, StateFilter: "NY", Latitude: &lat, Longitude: &lon, RadiusMiles: &radius,
	})
	if err != nil {
		t.Fatalf("AutocompleteGetRequest: %v", err)
	}
	for _, want := range []string{"q=100+wall", "limit=7", "state=NY", "lat=40.7", "lon=-74", "radius_miles=5"} {
		if !strings.Contains(gotQuery, want) {
			t.Errorf("query %q is missing %q", gotQuery, want)
		}
	}
}

func ndjsonServer(t *testing.T, lines []string, hang bool) *httptest.Server {
	t.Helper()
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/x-ndjson")
		flusher, _ := w.(http.Flusher)
		for _, l := range lines {
			_, _ = w.Write([]byte(l))
			if flusher != nil {
				flusher.Flush()
			}
		}
		if hang {
			<-r.Context().Done()
		}
	}))
	t.Cleanup(srv.Close)
	return srv
}

func TestStreamBatchRecordsReadsTheRealStreamAndSurfacesRecordErrors(t *testing.T) {
	raw := string(fixture(t, "batch_stream.ndjson"))
	lines := strings.SplitAfter(raw, "\n")
	srv := ndjsonServer(t, lines, false)

	req := standardizer.BatchStandardizeRequest{Addresses: []interface{}{"a", "b", "c"}}
	out, errs := standardizer.NewClient(srv.URL).StreamBatchRecords(context.Background(), req)
	var ok, failed int
	for rec := range out {
		switch {
		case rec.Err != nil:
			failed++
			if rec.Err.Index != 1 {
				t.Errorf("record error index = %d, want 1", rec.Err.Index)
			}
		case rec.Address != nil:
			ok++
		default:
			t.Fatal("record with neither Address nor Err")
		}
	}
	if err := <-errs; err != nil {
		t.Fatalf("stream error: %v", err)
	}
	if ok != 2 || failed != 1 {
		t.Fatalf("ok=%d failed=%d, want 2 and 1", ok, failed)
	}
}

func TestStreamBatchStopsWithRecordErrorAndHandlesVeryLongLines(t *testing.T) {
	long := `{"street1":"` + strings.Repeat("A", 200_000) + `"}` + "\n"
	srv := ndjsonServer(t, []string{long, `{"error":"invalid record","index":1}` + "\n"}, false)

	out, errs := standardizer.NewClient(srv.URL).StreamBatch(context.Background(), []string{"a", "b"})
	count := 0
	for range out {
		count++
	}
	err := <-errs
	var recErr *standardizer.RecordError
	if !errors.As(err, &recErr) || recErr.Index != 1 {
		t.Fatalf("want *RecordError for record 1, got %v", err)
	}
	if count != 1 {
		t.Fatalf("expected the 200 KB record to be delivered, got %d records", count)
	}
}

func TestStreamBatchDetectsTruncatedStreams(t *testing.T) {
	srv := ndjsonServer(t, []string{`{"street1":"A"}` + "\n"}, false)
	out, errs := standardizer.NewClient(srv.URL).StreamBatch(context.Background(), []string{"a", "b", "c"})
	for range out {
	}
	if err := <-errs; err == nil || !strings.Contains(err.Error(), "ended after 1 of 3") {
		t.Fatalf("expected a truncation error, got %v", err)
	}
}

func TestStreamBatchRejectsMalformedLines(t *testing.T) {
	srv := ndjsonServer(t, []string{"not json\n"}, false)
	out, errs := standardizer.NewClient(srv.URL).StreamBatch(context.Background(), []string{"a"})
	for range out {
	}
	if err := <-errs; err == nil || !strings.Contains(err.Error(), "invalid NDJSON line") {
		t.Fatalf("expected an invalid-line error, got %v", err)
	}
}

func TestStreamBatchSurvivesTheDefaultRequestTimeoutAndStopsOnContextCancel(t *testing.T) {
	var served int32
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		flusher := w.(http.Flusher)
		for i := 0; i < 3; i++ {
			_, _ = w.Write([]byte(`{"street1":"A"}` + "\n"))
			flusher.Flush()
			atomic.AddInt32(&served, 1)
			time.Sleep(60 * time.Millisecond)
		}
		<-r.Context().Done()
	}))
	defer srv.Close()

	// A 50 ms whole-request timeout would kill this stream if it applied to streaming calls.
	client := standardizer.NewClient(srv.URL, standardizer.WithTimeout(50*time.Millisecond))
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	out, errs := client.StreamBatch(ctx, []string{"a", "b", "c", "d"})
	got := 0
	for range out {
		got++
		if got == 3 {
			cancel()
			break
		}
	}
	for range out {
	}
	<-errs
	if got != 3 {
		t.Fatalf("expected 3 records before cancel, got %d", got)
	}
}

func TestNonStreamingCallsHonourWithTimeout(t *testing.T) {
	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(300 * time.Millisecond)
		_, _ = w.Write([]byte(`{}`))
	}))
	defer srv.Close()

	_, err := standardizer.NewClient(srv.URL, standardizer.WithTimeout(40*time.Millisecond)).
		Standardize(context.Background(), standardizer.StandardizeRequest{Address: "x"})
	if err == nil {
		t.Fatal("expected a timeout error")
	}
}
