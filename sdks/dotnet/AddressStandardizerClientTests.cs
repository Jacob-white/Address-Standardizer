using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace AddressStandardizer.Client.Tests
{
    public class MockHttpMessageHandler : HttpMessageHandler
    {
        private readonly Func<HttpRequestMessage, Task<HttpResponseMessage>> _handler;

        public MockHttpMessageHandler(Func<HttpRequestMessage, Task<HttpResponseMessage>> handler)
        {
            _handler = handler;
        }

        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            return _handler(request);
        }
    }

    public static class AddressStandardizerClientVerification
    {
        public static async Task RunVerificationAsync()
        {
            // 1. Test Standardize Single
            var mockHandler = new MockHttpMessageHandler(req =>
            {
                if (req.RequestUri?.AbsolutePath.EndsWith("standardize") == true)
                {
                    var json = "{\"street1\":\"1600 PENNSYLVANIA AVE NW\",\"city\":\"WASHINGTON\",\"state\":\"DC\",\"postal_code\":\"20500\",\"country\":\"USA\",\"country_iso3\":\"USA\",\"deliverability\":\"DELIVERABLE\",\"latitude\":38.898,\"longitude\":-77.036,\"precision\":\"RANGE_INTERPOLATED\"}";
                    return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
                    {
                        Content = new StringContent(json, Encoding.UTF8, "application/json")
                    });
                }
                return Task.FromResult(new HttpResponseMessage(HttpStatusCode.NotFound));
            });

            using var httpClient = new HttpClient(mockHandler) { BaseAddress = new Uri("http://localhost:8000/") };
            using var client = new AddressStandardizerClient(httpClient);

            var res = await client.StandardizeAsync("1600 Pennsylvania Ave NW, Washington, DC 20500");
            if (res.Street1 != "1600 PENNSYLVANIA AVE NW") throw new Exception("Unexpected street1");
            if (res.Deliverability != "DELIVERABLE") throw new Exception("Unexpected deliverability");
            if (res.Latitude != 38.898) throw new Exception("Unexpected latitude");

            // 2. Test Autocomplete
            var autoMockHandler = new MockHttpMessageHandler(req =>
            {
                var json = "{\"count\":1,\"suggestions\":[{\"text\":\"100 WALL ST, NEW YORK, NY 10005\",\"street_line\":\"100 WALL ST\",\"city\":\"NEW YORK\",\"state\":\"NY\",\"postal_code\":\"10005\",\"secondary_prompt_required\":true,\"suggested_secondary_units\":[\"STE\"],\"prompt_message\":\"Requires Suite / Apartment Number\"}]}";
                return Task.FromResult(new HttpResponseMessage(HttpStatusCode.OK)
                {
                    Content = new StringContent(json, Encoding.UTF8, "application/json")
                });
            });

            using var autoHttpClient = new HttpClient(autoMockHandler) { BaseAddress = new Uri("http://localhost:8000/") };
            using var autoClient = new AddressStandardizerClient(autoHttpClient);

            var suggestions = await autoClient.AutocompleteAsync(new AutocompleteRequest { Query = "100 Wall" });
            if (suggestions.Count != 1) throw new Exception("Expected 1 suggestion");
            if (!suggestions[0].SecondaryPromptRequired) throw new Exception("Expected secondary prompt");
            if (suggestions[0].PromptMessage != "Requires Suite / Apartment Number") throw new Exception("Unexpected prompt message");
        }
    }
}
