using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Xunit;

namespace AddressStandardizer.Client.Tests
{
    public class AddressStandardizerClientTests
    {
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
        public async Task Standardize_ParsesFlatResponse()
        {
            using var client = ClientFor(req =>
            {
                Assert.EndsWith("v1/standardize", req.RequestUri!.AbsolutePath);
                return Json("{\"street1\":\"1600 PENNSYLVANIA AVE NW\",\"city\":\"WASHINGTON\",\"state\":\"DC\",\"postal_code\":\"20500\",\"country\":\"USA\",\"country_iso3\":\"USA\",\"deliverability\":\"DELIVERABLE\",\"latitude\":38.898,\"longitude\":-77.036,\"precision\":\"RANGE_INTERPOLATED\"}");
            });

            var res = await client.StandardizeAsync("1600 Pennsylvania Ave NW, Washington, DC 20500");

            Assert.Equal("1600 PENNSYLVANIA AVE NW", res.Street1);
            Assert.Equal("20500", res.PostalCode);
            Assert.Equal("DELIVERABLE", res.Deliverability);
            Assert.Equal(38.898, res.Latitude);
        }

        [Fact]
        public async Task Standardize_SendsSnakeCaseRequestBody()
        {
            string? body = null;
            using var client = ClientFor(req =>
            {
                body = req.Content!.ReadAsStringAsync().GetAwaiter().GetResult();
                return Json("{\"street1\":\"\",\"city\":\"\"}");
            });

            await client.StandardizeAsync(new StandardizeRequest { Address = "100 Main St", EnableGeocoding = false });

            Assert.Contains("\"enable_geocoding\":false", body);
            Assert.Contains("\"address\":\"100 Main St\"", body);
        }

        [Fact]
        public async Task StandardizeBatch_ReturnsList()
        {
            using var client = ClientFor(_ => Json("[{\"street1\":\"A\"},{\"street1\":\"B\"}]"));

            var res = await client.StandardizeBatchAsync(new BatchStandardizeRequest
            {
                Addresses = new List<object> { "a", "b" },
            });

            Assert.Equal(new[] { "A", "B" }, res.Select(r => r.Street1).ToArray());
        }

        [Fact]
        public async Task StreamBatch_ReadsNdjson()
        {
            using var client = ClientFor(req =>
            {
                Assert.Contains("application/x-ndjson", req.Headers.Accept.ToString());
                return Json("{\"street1\":\"A\"}\n\n{\"street1\":\"B\"}\n", mediaType: "application/x-ndjson");
            });

            var got = new List<string>();
            await foreach (var item in client.StreamBatchAsync(new[] { "a", "b" }))
            {
                got.Add(item.Street1);
            }

            Assert.Equal(new[] { "A", "B" }, got.ToArray());
        }

        [Fact]
        public async Task Autocomplete_ParsesSuggestions()
        {
            using var client = ClientFor(_ => Json("{\"count\":1,\"suggestions\":[{\"text\":\"100 WALL ST, NEW YORK, NY 10005\",\"street_line\":\"100 WALL ST\",\"city\":\"NEW YORK\",\"state\":\"NY\",\"postal_code\":\"10005\",\"secondary_prompt_required\":true,\"suggested_secondary_units\":[\"STE\"],\"prompt_message\":\"Requires Suite / Apartment Number\"}]}"));

            var suggestions = await client.AutocompleteAsync(new AutocompleteRequest { Query = "100 Wall" });

            Assert.Single(suggestions);
            Assert.True(suggestions[0].SecondaryPromptRequired);
            Assert.Equal("Requires Suite / Apartment Number", suggestions[0].PromptMessage);
        }

        [Fact]
        public async Task ErrorResponse_IncludesStatusAndBody()
        {
            using var client = ClientFor(_ => Json("{\"detail\":\"bad request\"}", HttpStatusCode.BadRequest));

            var ex = await Assert.ThrowsAsync<HttpRequestException>(() => client.StandardizeAsync("x"));

            Assert.Contains("400", ex.Message);
            Assert.Contains("bad request", ex.Message);
        }

        /// <summary>Runs against a live server when ADDRESS_STANDARDIZER_URL is set (CI starts one).</summary>
        [Fact]
        public async Task LiveServer_StandardizeBatchStreamAndHealth()
        {
            var url = Environment.GetEnvironmentVariable("ADDRESS_STANDARDIZER_URL");
            if (string.IsNullOrEmpty(url))
            {
                return;
            }

            using var client = new AddressStandardizerClient(url);

            var res = await client.StandardizeAsync("1600 Pennsylvania Ave NW, Washington, DC 20500");
            Assert.Equal("DC", res.State);
            Assert.Equal("20500", res.PostalCode);

            var batch = await client.StandardizeBatchAsync(new BatchStandardizeRequest
            {
                Addresses = new List<object> { "100 Main St, Austin, TX 78701", "350 5th Ave, New York, NY 10118" },
            });
            Assert.Equal(2, batch.Count);

            var streamed = 0;
            await foreach (var _ in client.StreamBatchAsync(new[] { "100 Main St, Austin, TX 78701" }))
            {
                streamed++;
            }
            Assert.Equal(1, streamed);

            var health = await client.GetHealthAsync();
            Assert.False(string.IsNullOrEmpty(health.Version));
        }
    }
}
