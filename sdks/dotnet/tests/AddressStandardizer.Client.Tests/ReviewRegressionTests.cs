using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Xunit;

namespace AddressStandardizer.Client.Tests
{
    /// <summary>A [Fact] that is reported as skipped (not passed) unless ADDRESS_STANDARDIZER_URL is set.</summary>
    public sealed class LiveServerFactAttribute : FactAttribute
    {
        public LiveServerFactAttribute()
        {
            if (string.IsNullOrEmpty(Environment.GetEnvironmentVariable("ADDRESS_STANDARDIZER_URL")))
            {
                Skip = "ADDRESS_STANDARDIZER_URL is not set";
            }
        }
    }

    /// <summary>Regressions from the whole-codebase review of the .NET SDK.</summary>
    public class ReviewRegressionTests
    {
        private const string Ndjson = "application/x-ndjson";

        private static HttpResponseMessage Json(string json, HttpStatusCode status = HttpStatusCode.OK, string mediaType = "application/json")
        {
            return new HttpResponseMessage(status) { Content = new StringContent(json, Encoding.UTF8, mediaType) };
        }

        private static AddressStandardizerClient ClientFor(Func<HttpRequestMessage, HttpResponseMessage> respond)
        {
            var http = new HttpClient(new MockHttpMessageHandler(req => Task.FromResult(respond(req))))
            {
                BaseAddress = new Uri("http://localhost:8000/"),
            };
            return new AddressStandardizerClient(http, ownsHttpClient: true);
        }

        [Fact]
        public async Task UnsetFlagsAreOmittedSoTheServerDefaultsApply()
        {
            string? body = null;
            using var client = ClientFor(req =>
            {
                body = req.Content!.ReadAsStringAsync().GetAwaiter().GetResult();
                return Json("{\"street1\":\"\"}");
            });

            await client.StandardizeAsync(new StandardizeRequest { Address = "100 Main St" });

            Assert.DoesNotContain("enable_geocoding", body);
            Assert.DoesNotContain("enable_fuzzy", body);
            Assert.DoesNotContain("country", body);
        }

        [Fact]
        public async Task BatchFlagsAreNotOverriddenByDefaultsOnItems()
        {
            string? body = null;
            using var client = ClientFor(req =>
            {
                body = req.Content!.ReadAsStringAsync().GetAwaiter().GetResult();
                return Json("[]");
            });

            await client.StandardizeBatchAsync(new BatchStandardizeRequest
            {
                EnableGeocoding = false,
                CorrectStateFromZip = true,
                Addresses = new List<object> { new StandardizeRequest { Address = "100 Main St" } },
            });

            Assert.Contains("\"enable_geocoding\":false", body);
            Assert.Contains("\"correct_state_from_zip\":true", body);
            // the per-item request must not re-state flags the caller did not set
            Assert.Single(Regex.Matches(body!, "enable_geocoding"));
        }

        [Fact]
        public async Task StreamBatchRecords_SurfacesServerRecordErrorsAndContinues()
        {
            using var client = ClientFor(_ => Json(
                "{\"street1\":\"A\"}\n{\"error\":\"invalid record\",\"index\":1}\n{\"street1\":\"C\"}\n", mediaType: Ndjson));

            var kinds = new List<string>();
            await foreach (var record in client.StreamBatchRecordsAsync(new BatchStandardizeRequest { Addresses = new List<object> { "a", "b", "c" } }))
            {
                kinds.Add(record.Error != null ? "error:" + record.Error.Index : record.Address!.Street1);
            }

            Assert.Equal(new[] { "A", "error:1", "C" }, kinds.ToArray());
        }

        [Fact]
        public async Task StreamBatch_ThrowsOnTheFirstRecordError()
        {
            using var client = ClientFor(_ => Json("{\"street1\":\"A\"}\n{\"error\":\"invalid record\",\"index\":1}\n", mediaType: Ndjson));

            var ex = await Assert.ThrowsAsync<AddressStandardizerRecordException>(async () =>
            {
                await foreach (var _ in client.StreamBatchAsync(new[] { "a", "b" })) { }
            });

            Assert.Equal(1, ex.Index);
        }

        [Fact]
        public async Task StreamBatch_DetectsTruncatedStreamsAndMalformedLines()
        {
            using var truncated = ClientFor(_ => Json("{\"street1\":\"A\"}\n", mediaType: Ndjson));
            var ex = await Assert.ThrowsAsync<InvalidDataException>(async () =>
            {
                await foreach (var _ in truncated.StreamBatchAsync(new[] { "a", "b", "c" })) { }
            });
            Assert.Contains("1 of 3", ex.Message);

            using var malformed = ClientFor(_ => Json("not json\n", mediaType: Ndjson));
            await Assert.ThrowsAsync<InvalidDataException>(async () =>
            {
                await foreach (var _ in malformed.StreamBatchAsync(new[] { "a" })) { }
            });
        }

        [Fact]
        public async Task StreamBatch_HonoursCancellation()
        {
            using var client = ClientFor(_ => Json("{\"street1\":\"A\"}\n{\"street1\":\"B\"}\n", mediaType: Ndjson));
            using var cts = new CancellationTokenSource();

            await Assert.ThrowsAnyAsync<OperationCanceledException>(async () =>
            {
                await foreach (var _ in client.StreamBatchAsync(new[] { "a", "b" }, cts.Token))
                {
                    cts.Cancel();
                }
            });
        }

        [Fact]
        public void HttpClientWithoutBaseAddressIsRejected()
        {
            Assert.Throws<ArgumentException>(() => new AddressStandardizerClient(new HttpClient()));
        }

        [Fact]
        public async Task AutocompleteGet_SendsProximityParameters()
        {
            string? query = null;
            using var client = ClientFor(req =>
            {
                query = req.RequestUri!.Query;
                return Json("{\"count\":0,\"suggestions\":[]}");
            });

            await client.AutocompleteGetAsync(new AutocompleteRequest
            {
                Query = "100 wall", MaxResults = 7, StateFilter = "NY", Latitude = 40.7, Longitude = -74.0, RadiusMiles = 5,
            });

            Assert.Contains("q=100%20wall", query);
            Assert.Contains("limit=7", query);
            Assert.Contains("state=NY", query);
            Assert.Contains("lat=40.7", query);
            Assert.Contains("radius_miles=5", query);
        }
    }
}
