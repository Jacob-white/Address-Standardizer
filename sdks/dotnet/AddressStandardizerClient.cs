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
        IAsyncEnumerable<StandardizedAddress> StreamBatchAsync(IEnumerable<string> addresses, [EnumeratorCancellation] CancellationToken cancellationToken = default);
        Task<List<AutocompleteSuggestion>> AutocompleteAsync(AutocompleteRequest request, CancellationToken cancellationToken = default);
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

        public AddressStandardizerClient(string baseUrl)
            : this(new HttpClient { BaseAddress = new Uri(baseUrl.TrimEnd('/') + "/") }, ownsHttpClient: true)
        {
        }

        public AddressStandardizerClient(HttpClient httpClient, bool ownsHttpClient = false)
        {
            _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
            _ownsHttpClient = ownsHttpClient;
        }

        public async Task<StandardizedAddress> StandardizeAsync(StandardizeRequest request, CancellationToken cancellationToken = default)
        {
            var content = new StringContent(JsonSerializer.Serialize(request, JsonOptions), Encoding.UTF8, "application/json");
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
            var content = new StringContent(JsonSerializer.Serialize(request, JsonOptions), Encoding.UTF8, "application/json");
            using var response = await _httpClient.PostAsync("v1/batch", content, cancellationToken).ConfigureAwait(false);
            await EnsureSuccessAsync(response).ConfigureAwait(false);

            var stream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            var result = await JsonSerializer.DeserializeAsync<List<StandardizedAddress>>(stream, JsonOptions, cancellationToken).ConfigureAwait(false);
            return result ?? new List<StandardizedAddress>();
        }

        public async IAsyncEnumerable<StandardizedAddress> StreamBatchAsync(
            IEnumerable<string> addresses,
            [EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            var payload = new { addresses = new List<string>(addresses) };
            using var request = new HttpRequestMessage(HttpMethod.Post, "v1/batch");
            request.Headers.Accept.Add(new MediaTypeWithQualityHeaderValue("application/x-ndjson"));
            request.Content = new StringContent(JsonSerializer.Serialize(payload, JsonOptions), Encoding.UTF8, "application/json");

            using var response = await _httpClient.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, cancellationToken).ConfigureAwait(false);
            await EnsureSuccessAsync(response).ConfigureAwait(false);

            using var responseStream = await response.Content.ReadAsStreamAsync().ConfigureAwait(false);
            using var reader = new StreamReader(responseStream, Encoding.UTF8);

            string? line;
            while ((line = await reader.ReadLineAsync().ConfigureAwait(false)) != null)
            {
                cancellationToken.ThrowIfCancellationRequested();
                var trimmed = line.Trim();
                if (string.IsNullOrEmpty(trimmed))
                    continue;

                var item = JsonSerializer.Deserialize<StandardizedAddress>(trimmed, JsonOptions);
                if (item != null)
                {
                    yield return item;
                }
            }
        }

        public async Task<List<AutocompleteSuggestion>> AutocompleteAsync(AutocompleteRequest request, CancellationToken cancellationToken = default)
        {
            var content = new StringContent(JsonSerializer.Serialize(request, JsonOptions), Encoding.UTF8, "application/json");
            using var response = await _httpClient.PostAsync("v1/autocomplete", content, cancellationToken).ConfigureAwait(false);
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

            throw new HttpRequestException(
                $"Address Standardizer HTTP {(int)response.StatusCode}: {body}");
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
