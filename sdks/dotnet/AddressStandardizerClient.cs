using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading;
using System.Threading.Tasks;

namespace AddressStandardizer.Client
{
    public interface IAddressStandardizerClient
    {
        Task<StandardizedAddress> StandardizeAsync(StandardizeRequest request, CancellationToken cancellationToken = default);
        Task<StandardizedAddress> StandardizeAsync(string address, CancellationToken cancellationToken = default);
        Task<List<StandardizedAddress>> StandardizeBatchAsync(BatchStandardizeRequest request, CancellationToken cancellationToken = default);
        IAsyncEnumerable<StandardizedAddress> StreamBatchAsync(IEnumerable<string> addresses, CancellationToken cancellationToken = default);
        IAsyncEnumerable<StreamRecord> StreamBatchRecordsAsync(BatchStandardizeRequest request, CancellationToken cancellationToken = default);
        Task<List<AutocompleteSuggestion>> AutocompleteAsync(AutocompleteRequest request, CancellationToken cancellationToken = default);
        Task<List<AutocompleteSuggestion>> AutocompleteGetAsync(AutocompleteRequest request, CancellationToken cancellationToken = default);
        Task<HealthResponse> GetHealthAsync(CancellationToken cancellationToken = default);
    }

    public class AddressStandardizerClient : IAddressStandardizerClient, IDisposable
    {
        private readonly HttpClient _httpClient;
        private readonly bool _ownsHttpClient;
        private static readonly JsonSerializerOptions JsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        };

        /// <summary>
        /// Creates a client for the service at <paramref name="baseUrl"/>. <paramref name="timeout"/> bounds each
        /// non-streaming call (default 100 s, the HttpClient default); streaming calls are cancelled through their token.
        /// </summary>
        public AddressStandardizerClient(string baseUrl, TimeSpan? timeout = null)
            : this(CreateHttpClient(baseUrl, timeout), ownsHttpClient: true)
        {
        }

        public AddressStandardizerClient(HttpClient httpClient, bool ownsHttpClient = false)
        {
            _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
            if (_httpClient.BaseAddress == null)
            {
                throw new ArgumentException("The HttpClient must have a BaseAddress (for example http://localhost:8000/).", nameof(httpClient));
            }
            _ownsHttpClient = ownsHttpClient;
        }

        private static HttpClient CreateHttpClient(string baseUrl, TimeSpan? timeout)
        {
            if (string.IsNullOrWhiteSpace(baseUrl))
            {
                throw new ArgumentException("baseUrl is required.", nameof(baseUrl));
            }

            var client = new HttpClient { BaseAddress = new Uri(baseUrl.TrimEnd('/') + "/") };
            if (timeout.HasValue)
            {
                client.Timeout = timeout.Value;
            }
            return client;
        }

        public async Task<StandardizedAddress> StandardizeAsync(StandardizeRequest request, CancellationToken cancellationToken = default)
        {
            using var content = new StringContent(JsonSerializer.Serialize(request, JsonOptions), Encoding.UTF8, "application/json");
            using var response = await _httpClient.PostAsync("v1/standardize", content, cancellationToken).ConfigureAwait(false);
            await EnsureSuccessAsync(response).ConfigureAwait(false);

            var stream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            var result = await JsonSerializer.DeserializeAsync<StandardizedAddress>(stream, JsonOptions, cancellationToken).ConfigureAwait(false);
            return result ?? throw new InvalidOperationException("Empty response received from standardize endpoint.");
        }

        public Task<StandardizedAddress> StandardizeAsync(string address, CancellationToken cancellationToken = default)
        {
            return StandardizeAsync(new StandardizeRequest { Address = address }, cancellationToken);
        }

        public async Task<List<StandardizedAddress>> StandardizeBatchAsync(BatchStandardizeRequest request, CancellationToken cancellationToken = default)
        {
            using var content = new StringContent(JsonSerializer.Serialize(request, JsonOptions), Encoding.UTF8, "application/json");
            using var response = await _httpClient.PostAsync("v1/batch", content, cancellationToken).ConfigureAwait(false);
            await EnsureSuccessAsync(response).ConfigureAwait(false);

            var stream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            var result = await JsonSerializer.DeserializeAsync<List<StandardizedAddress>>(stream, JsonOptions, cancellationToken).ConfigureAwait(false);
            return result ?? new List<StandardizedAddress>();
        }

        /// <summary>
        /// Streams standardized addresses for plain address strings. The first record the server could not
        /// standardize ends the enumeration with an <see cref="AddressStandardizerRecordException"/>; use
        /// <see cref="StreamBatchRecordsAsync"/> to receive per-record errors and keep going.
        /// </summary>
        public async IAsyncEnumerable<StandardizedAddress> StreamBatchAsync(
            IEnumerable<string> addresses,
            [EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            var request = new BatchStandardizeRequest { Addresses = new List<object>(addresses) };
            await foreach (var record in StreamBatchRecordsAsync(request, cancellationToken).ConfigureAwait(false))
            {
                if (record.Error != null)
                {
                    throw new AddressStandardizerRecordException(record.Error.Index, record.Error.Message);
                }
                yield return record.Address!;
            }
        }

        /// <summary>
        /// Streams one result per request item (NDJSON), in order. Records the server could not standardize arrive
        /// as <see cref="StreamRecord.Error"/> and the enumeration continues. A stream that ends before one record
        /// per item has arrived throws <see cref="InvalidDataException"/> instead of silently truncating.
        /// </summary>
        public async IAsyncEnumerable<StreamRecord> StreamBatchRecordsAsync(
            BatchStandardizeRequest request,
            [EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            using var message = new HttpRequestMessage(HttpMethod.Post, "v1/batch");
            message.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/x-ndjson"));
            message.Content = new StringContent(JsonSerializer.Serialize(request, JsonOptions), Encoding.UTF8, "application/json");

            using var response = await _httpClient.SendAsync(message, HttpCompletionOption.ResponseHeadersRead, cancellationToken).ConfigureAwait(false);
            await EnsureSuccessAsync(response).ConfigureAwait(false);

            using var responseStream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            using var reader = new StreamReader(responseStream, Encoding.UTF8);

            var received = 0;
            while (true)
            {
                cancellationToken.ThrowIfCancellationRequested();
#if NET7_0_OR_GREATER
                var line = await reader.ReadLineAsync(cancellationToken).ConfigureAwait(false);
#else
                var line = await reader.ReadLineAsync().ConfigureAwait(false);
#endif
                if (line == null)
                {
                    break;
                }

                var trimmed = line.Trim();
                if (trimmed.Length == 0)
                {
                    continue;
                }

                StreamRecord record;
                try
                {
                    record = ParseStreamLine(trimmed, received);
                }
                catch (JsonException ex)
                {
                    throw new InvalidDataException($"Invalid NDJSON line after {received} record(s).", ex);
                }

                received++;
                yield return record;
            }

            if (received < request.Addresses.Count)
            {
                throw new InvalidDataException($"Stream ended after {received} of {request.Addresses.Count} record(s).");
            }
        }

        private static StreamRecord ParseStreamLine(string line, int index)
        {
            using var doc = JsonDocument.Parse(line);
            if (doc.RootElement.ValueKind == JsonValueKind.Object && doc.RootElement.TryGetProperty("error", out var error))
            {
                var idx = doc.RootElement.TryGetProperty("index", out var i) && i.TryGetInt32(out var parsed) ? parsed : index;
                return new StreamRecord { Error = new RecordError(idx, error.GetString() ?? "error") };
            }

            var item = JsonSerializer.Deserialize<StandardizedAddress>(line, JsonOptions);
            return new StreamRecord { Address = item ?? throw new JsonException("Empty record.") };
        }

        public async Task<List<AutocompleteSuggestion>> AutocompleteAsync(AutocompleteRequest request, CancellationToken cancellationToken = default)
        {
            using var content = new StringContent(JsonSerializer.Serialize(request, JsonOptions), Encoding.UTF8, "application/json");
            using var response = await _httpClient.PostAsync("v1/autocomplete", content, cancellationToken).ConfigureAwait(false);
            await EnsureSuccessAsync(response).ConfigureAwait(false);

            var stream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            var result = await JsonSerializer.DeserializeAsync<AutocompleteResponse>(stream, JsonOptions, cancellationToken).ConfigureAwait(false);
            return result?.Suggestions ?? new List<AutocompleteSuggestion>();
        }

        /// <summary>GET-based typeahead query supporting limit, state filter and proximity bias.</summary>
        public async Task<List<AutocompleteSuggestion>> AutocompleteGetAsync(AutocompleteRequest request, CancellationToken cancellationToken = default)
        {
            var query = new List<string> { "q=" + Uri.EscapeDataString(request.Query) };
            if (request.MaxResults > 0) query.Add("limit=" + request.MaxResults);
            if (!string.IsNullOrEmpty(request.StateFilter)) query.Add("state=" + Uri.EscapeDataString(request.StateFilter!));
            if (request.Latitude.HasValue) query.Add("lat=" + request.Latitude.Value.ToString(System.Globalization.CultureInfo.InvariantCulture));
            if (request.Longitude.HasValue) query.Add("lon=" + request.Longitude.Value.ToString(System.Globalization.CultureInfo.InvariantCulture));
            if (request.RadiusMiles.HasValue) query.Add("radius_miles=" + request.RadiusMiles.Value.ToString(System.Globalization.CultureInfo.InvariantCulture));

            using var response = await _httpClient.GetAsync("v1/autocomplete?" + string.Join("&", query), cancellationToken).ConfigureAwait(false);
            await EnsureSuccessAsync(response).ConfigureAwait(false);

            var stream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            var result = await JsonSerializer.DeserializeAsync<AutocompleteResponse>(stream, JsonOptions, cancellationToken).ConfigureAwait(false);
            return result?.Suggestions ?? new List<AutocompleteSuggestion>();
        }

        public async Task<HealthResponse> GetHealthAsync(CancellationToken cancellationToken = default)
        {
            using var response = await _httpClient.GetAsync("health", cancellationToken).ConfigureAwait(false);
            await EnsureSuccessAsync(response).ConfigureAwait(false);

            var stream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            var result = await JsonSerializer.DeserializeAsync<HealthResponse>(stream, JsonOptions, cancellationToken).ConfigureAwait(false);
            return result ?? throw new InvalidOperationException("Failed to deserialize health response.");
        }

        private static async Task EnsureSuccessAsync(HttpResponseMessage response)
        {
            if (response.IsSuccessStatusCode)
                return;

            string body;
            try
            {
                body = await response.Content.ReadAsStringAsync().ConfigureAwait(false);
            }
            catch (Exception)
            {
                body = response.ReasonPhrase ?? string.Empty;
            }

            var snippet = body.Length > AddressStandardizerException.MaxMessageBodyLength
                ? body.Substring(0, AddressStandardizerException.MaxMessageBodyLength) + "..."
                : body;
            throw new AddressStandardizerException(
                $"Address Standardizer HTTP {(int)response.StatusCode}: {snippet}",
                response.StatusCode,
                body);
        }

        public void Dispose()
        {
            if (_ownsHttpClient)
            {
                _httpClient.Dispose();
            }
        }
    }
}
