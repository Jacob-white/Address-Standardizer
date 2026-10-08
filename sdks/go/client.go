package standardizer

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

// DefaultTimeout bounds each non-streaming request (including reading the response body).
// Streaming calls are not subject to it; cancel them with their context.
const DefaultTimeout = 10 * time.Second

// APIError is returned when the service responds with a non-2xx status. Use errors.As to branch on StatusCode.
type APIError struct {
	StatusCode int
	// Body is the full response body; it may echo submitted address data.
	Body string
}

func (e *APIError) Error() string {
	body := e.Body
	if len(body) > 512 {
		body = body[:512] + "..."
	}
	return fmt.Sprintf("http %d: %s", e.StatusCode, body)
}

// RecordError reports a record of a batch stream that the server could not standardize.
type RecordError struct {
	// Index is the position of the failed record in the request.
	Index   int
	Message string
}

func (e *RecordError) Error() string {
	return fmt.Sprintf("record %d: %s", e.Index, e.Message)
}

// StreamRecord is one result of a batch stream. Exactly one of Address and Err is set.
type StreamRecord struct {
	Address *StandardizedAddress
	Err     *RecordError
}

// Option defines a functional configuration option for the Client.
type Option func(*Client)

// WithHTTPClient overrides the default http.Client.
func WithHTTPClient(httpClient *http.Client) Option {
	return func(c *Client) {
		c.httpClient = httpClient
	}
}

// WithHeader attaches a persistent custom header to all requests.
func WithHeader(key, value string) Option {
	return func(c *Client) {
		c.headers[key] = value
	}
}

// WithTimeout sets the per-request timeout for non-streaming calls. Zero or negative disables it
// (use the call's context instead).
func WithTimeout(d time.Duration) Option {
	return func(c *Client) {
		c.timeout = d
	}
}

// Client interacts with the Address Standardizer microservice daemon.
type Client struct {
	baseURL    string
	httpClient *http.Client
	headers    map[string]string
	timeout    time.Duration
}

// NewClient initializes a new Address Standardizer client.
//
// The default http.Client has no overall Timeout, because that would also cut long NDJSON streams; instead the
// transport bounds connecting and waiting for response headers, and DefaultTimeout bounds each non-streaming call.
func NewClient(baseURL string, opts ...Option) *Client {
	c := &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		httpClient: &http.Client{
			Transport: &http.Transport{
				Proxy:                 http.ProxyFromEnvironment,
				DialContext:           (&net.Dialer{Timeout: 10 * time.Second, KeepAlive: 30 * time.Second}).DialContext,
				ResponseHeaderTimeout: 30 * time.Second,
				MaxIdleConns:          32,
				IdleConnTimeout:       90 * time.Second,
			},
		},
		headers: make(map[string]string),
		timeout: DefaultTimeout,
	}
	for _, opt := range opts {
		opt(c)
	}
	return c
}

func (c *Client) doRequest(ctx context.Context, method, path string, body interface{}, target interface{}) error {
	if c.timeout > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, c.timeout)
		defer cancel()
	}

	fullURL := c.baseURL + path
	var bodyReader io.Reader
	if body != nil {
		data, err := json.Marshal(body)
		if err != nil {
			return fmt.Errorf("failed to marshal request body: %w", err)
		}
		bodyReader = bytes.NewReader(data)
	}

	req, err := http.NewRequestWithContext(ctx, method, fullURL, bodyReader)
	if err != nil {
		return fmt.Errorf("failed to create http request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")
	for k, v := range c.headers {
		req.Header.Set(k, v)
	}

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		respBytes, _ := io.ReadAll(resp.Body)
		return &APIError{StatusCode: resp.StatusCode, Body: string(respBytes)}
	}

	if target != nil {
		if err := json.NewDecoder(resp.Body).Decode(target); err != nil {
			return fmt.Errorf("failed to decode response: %w", err)
		}
	}
	return nil
}

// Standardize parses and standardizes a single address.
func (c *Client) Standardize(ctx context.Context, req StandardizeRequest) (*StandardizedAddress, error) {
	var out StandardizedAddress
	if err := c.doRequest(ctx, http.MethodPost, "/v1/standardize", req, &out); err != nil {
		return nil, err
	}
	return &out, nil
}

// StandardizeBatch standardizes multiple addresses in a single batch request.
func (c *Client) StandardizeBatch(ctx context.Context, req BatchStandardizeRequest) ([]StandardizedAddress, error) {
	var out []StandardizedAddress
	if err := c.doRequest(ctx, http.MethodPost, "/v1/batch", req, &out); err != nil {
		return nil, err
	}
	return out, nil
}

// StreamBatchRecords streams one result per request item over newline-delimited JSON (NDJSON), in order.
// The request may carry plain strings or StandardizeRequest-shaped objects plus batch-wide flags.
//
// Records the server could not standardize arrive as StreamRecord.Err and the stream continues. The error channel
// receives at most one value (transport failure, HTTP error, malformed line, or a stream that ended before one
// record per item arrived) and both channels are closed when the call finishes. Cancel ctx to stop early: the
// goroutine exits and the connection is released even if the caller stops reading.
func (c *Client) StreamBatchRecords(ctx context.Context, req BatchStandardizeRequest) (<-chan StreamRecord, <-chan error) {
	outCh := make(chan StreamRecord)
	errCh := make(chan error, 1)

	go func() {
		defer close(outCh)
		defer close(errCh)

		data, err := json.Marshal(req)
		if err != nil {
			errCh <- fmt.Errorf("failed to marshal batch payload: %w", err)
			return
		}

		httpReq, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/v1/batch", bytes.NewReader(data))
		if err != nil {
			errCh <- fmt.Errorf("failed to construct streaming request: %w", err)
			return
		}
		httpReq.Header.Set("Content-Type", "application/json")
		httpReq.Header.Set("Accept", "application/x-ndjson")
		for k, v := range c.headers {
			httpReq.Header.Set(k, v)
		}

		resp, err := c.httpClient.Do(httpReq)
		if err != nil {
			errCh <- fmt.Errorf("streaming request failed: %w", err)
			return
		}
		defer resp.Body.Close()

		if resp.StatusCode < 200 || resp.StatusCode >= 300 {
			respBytes, _ := io.ReadAll(resp.Body)
			errCh <- &APIError{StatusCode: resp.StatusCode, Body: string(respBytes)}
			return
		}

		// bufio.Reader (not Scanner) so a single very long record cannot hit a token-size limit.
		reader := bufio.NewReader(resp.Body)
		received := 0
		for {
			line, readErr := reader.ReadBytes('\n')
			line = bytes.TrimSpace(line)
			if len(line) > 0 {
				record, parseErr := parseStreamLine(line, received)
				if parseErr != nil {
					errCh <- parseErr
					return
				}
				received++
				select {
				case <-ctx.Done():
					errCh <- ctx.Err()
					return
				case outCh <- record:
				}
			}
			if readErr != nil {
				if !errors.Is(readErr, io.EOF) {
					errCh <- fmt.Errorf("error reading stream: %w", readErr)
					return
				}
				break
			}
		}
		if received < len(req.Addresses) {
			errCh <- fmt.Errorf("stream ended after %d of %d record(s)", received, len(req.Addresses))
		}
	}()

	return outCh, errCh
}

func parseStreamLine(line []byte, index int) (StreamRecord, error) {
	var probe struct {
		Error *string `json:"error"`
		Index *int    `json:"index"`
	}
	if err := json.Unmarshal(line, &probe); err != nil {
		return StreamRecord{}, fmt.Errorf("invalid NDJSON line after %d record(s): %w", index, err)
	}
	if probe.Error != nil {
		idx := index
		if probe.Index != nil {
			idx = *probe.Index
		}
		return StreamRecord{Err: &RecordError{Index: idx, Message: *probe.Error}}, nil
	}
	var item StandardizedAddress
	if err := json.Unmarshal(line, &item); err != nil {
		return StreamRecord{}, fmt.Errorf("failed to unmarshal ndjson line: %w", err)
	}
	return StreamRecord{Address: &item}, nil
}

// StreamBatch streams standardized addresses for plain address strings. It is a convenience wrapper over
// StreamBatchRecords: the first record the server could not standardize ends the stream with a *RecordError on
// the error channel. Use StreamBatchRecords to receive per-record errors and keep going.
func (c *Client) StreamBatch(ctx context.Context, addresses []string) (<-chan StandardizedAddress, <-chan error) {
	outCh := make(chan StandardizedAddress)
	errCh := make(chan error, 1)

	req := BatchStandardizeRequest{Addresses: make([]interface{}, len(addresses))}
	for i, a := range addresses {
		req.Addresses[i] = a
	}

	go func() {
		defer close(outCh)
		defer close(errCh)

		inner, innerErr := c.StreamBatchRecords(ctx, req)
		for record := range inner {
			if record.Err != nil {
				errCh <- record.Err
				// drain so the producer goroutine can finish and release the connection
				for range inner {
				}
				<-innerErr
				return
			}
			select {
			case <-ctx.Done():
				errCh <- ctx.Err()
				for range inner {
				}
				<-innerErr
				return
			case outCh <- *record.Address:
			}
		}
		if err := <-innerErr; err != nil {
			errCh <- err
		}
	}()

	return outCh, errCh
}

// Autocomplete retrieves address typeahead suggestions with proximity ranking and secondary unit prompts.
func (c *Client) Autocomplete(ctx context.Context, req AutocompleteRequest) ([]AutocompleteSuggestion, error) {
	var out AutocompleteResponse
	if err := c.doRequest(ctx, http.MethodPost, "/v1/autocomplete", req, &out); err != nil {
		return nil, err
	}
	return out.Suggestions, nil
}

// AutocompleteGet performs GET-based typeahead query.
func (c *Client) AutocompleteGet(ctx context.Context, query string, limit int, state string) ([]AutocompleteSuggestion, error) {
	return c.AutocompleteGetRequest(ctx, AutocompleteRequest{Query: query, MaxResults: limit, StateFilter: state})
}

// AutocompleteGetRequest performs a GET-based typeahead query with every option the server supports
// (limit, state filter and proximity bias).
func (c *Client) AutocompleteGetRequest(ctx context.Context, req AutocompleteRequest) ([]AutocompleteSuggestion, error) {
	params := url.Values{}
	params.Set("q", req.Query)
	if req.MaxResults > 0 {
		params.Set("limit", strconv.Itoa(req.MaxResults))
	}
	if req.StateFilter != "" {
		params.Set("state", req.StateFilter)
	}
	if req.Latitude != nil {
		params.Set("lat", strconv.FormatFloat(*req.Latitude, 'f', -1, 64))
	}
	if req.Longitude != nil {
		params.Set("lon", strconv.FormatFloat(*req.Longitude, 'f', -1, 64))
	}
	if req.RadiusMiles != nil {
		params.Set("radius_miles", strconv.FormatFloat(*req.RadiusMiles, 'f', -1, 64))
	}

	path := "/v1/autocomplete?" + params.Encode()
	var out AutocompleteResponse
	if err := c.doRequest(ctx, http.MethodGet, path, nil, &out); err != nil {
		return nil, err
	}
	return out.Suggestions, nil
}

// Health checks the health and readiness of the microservice daemon.
func (c *Client) Health(ctx context.Context) (*HealthResponse, error) {
	var out HealthResponse
	if err := c.doRequest(ctx, http.MethodGet, "/health", nil, &out); err != nil {
		return nil, err
	}
	return &out, nil
}
