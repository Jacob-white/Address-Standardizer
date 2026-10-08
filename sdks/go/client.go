package standardizer

import (
	"bufio"
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

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

// Client interacts with the Address Standardizer microservice daemon.
type Client struct {
	baseURL    string
	httpClient *http.Client
	headers    map[string]string
}

// NewClient initializes a new Address Standardizer client.
func NewClient(baseURL string, opts ...Option) *Client {
	c := &Client{
		baseURL: strings.TrimRight(baseURL, "/"),
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
		headers: make(map[string]string),
	}
	for _, opt := range opts {
		opt(c)
	}
	return c
}

func (c *Client) doRequest(ctx context.Context, method, path string, body interface{}, target interface{}) error {
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

// StreamBatch streams standardized addresses over newline-delimited JSON (NDJSON).
func (c *Client) StreamBatch(ctx context.Context, addresses []string) (<-chan StandardizedAddress, <-chan error) {
	outCh := make(chan StandardizedAddress)
	errCh := make(chan error, 1)

	go func() {
		defer close(outCh)
		defer close(errCh)

		payload := BatchStandardizeRequest{
			Addresses: make([]interface{}, len(addresses)),
		}
		for i, a := range addresses {
			payload.Addresses[i] = a
		}

		data, err := json.Marshal(payload)
		if err != nil {
			errCh <- fmt.Errorf("failed to marshal batch payload: %w", err)
			return
		}

		req, err := http.NewRequestWithContext(ctx, http.MethodPost, c.baseURL+"/v1/batch", bytes.NewReader(data))
		if err != nil {
			errCh <- fmt.Errorf("failed to construct streaming request: %w", err)
			return
		}

		req.Header.Set("Content-Type", "application/json")
		req.Header.Set("Accept", "application/x-ndjson")
		for k, v := range c.headers {
			req.Header.Set(k, v)
		}

		resp, err := c.httpClient.Do(req)
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

		scanner := bufio.NewScanner(resp.Body)
		for scanner.Scan() {
			line := bytes.TrimSpace(scanner.Bytes())
			if len(line) == 0 {
				continue
			}
			var item StandardizedAddress
			if err := json.Unmarshal(line, &item); err != nil {
				errCh <- fmt.Errorf("failed to unmarshal ndjson line: %w", err)
				return
			}
			select {
			case <-ctx.Done():
				errCh <- ctx.Err()
				return
			case outCh <- item:
			}
		}

		if err := scanner.Err(); err != nil {
			errCh <- fmt.Errorf("error reading stream: %w", err)
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
	params := url.Values{}
	params.Set("q", query)
	if limit > 0 {
		params.Set("limit", strconv.Itoa(limit))
	}
	if state != "" {
		params.Set("state", state)
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
