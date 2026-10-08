# AddressStandardizer.Client (.NET)

Official .NET client SDK for the **Address Standardizer** HTTP microservice daemon, multi-targeting `net8.0` and `netstandard2.0` (C# 12, nullable reference types enabled; depends on `System.Text.Json`, and on `Microsoft.Bcl.AsyncInterfaces` for `netstandard2.0`).

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**.

---

## Installation

```bash
dotnet add package AddressStandardizer.Client
```

---

## Usage

```csharp
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using AddressStandardizer.Client;

using var client = new AddressStandardizerClient("http://localhost:8000");

// Standardize single address
var result = await client.StandardizeAsync(new StandardizeRequest
{
    Address = "350 5th Ave, New York, NY 10118",
    EnableGeocoding = true,
    CorrectStateFromZip = true, // replace a US state that contradicts the ZIP (server default: false)
});

Console.WriteLine($"Street:     {result.Street1}");
Console.WriteLine($"City:       {result.City}, {result.State} {result.PostalCode}");
Console.WriteLine($"Confidence: {result.ConfidenceScore}");
Console.WriteLine($"Lat/Lon:    {result.Latitude}, {result.Longitude}");

// Batch standardization
var batchResults = await client.StandardizeBatchAsync(new BatchStandardizeRequest
{
    Addresses = new List<object>
    {
        "100 Main St, Austin, TX 78701",
        "200 S Wacker Dr, Chicago, IL 60606",
    },
    CorrectStateFromZip = true,
});

// Interactive prefix search
var suggestions = await client.AutocompleteAsync(new AutocompleteRequest
{
    Query = "350 5th",
    MaxResults = 5,
});
foreach (var s in suggestions)
{
    Console.WriteLine($"- {s.Text}");
}
```

### Constructing the client

```csharp
// Owns its HttpClient and disposes it. `timeout` is optional.
using var client = new AddressStandardizerClient("http://localhost:8000", TimeSpan.FromSeconds(10));

// Reuse an HttpClient you manage (for example from IHttpClientFactory). It MUST have a BaseAddress,
// otherwise the constructor throws ArgumentException. The client does not dispose it unless you pass true.
var http = new HttpClient { BaseAddress = new Uri("http://localhost:8000/") };
using var client2 = new AddressStandardizerClient(http, ownsHttpClient: false);
```

`AddressStandardizerClient` also implements `IAddressStandardizerClient` for dependency injection and mocking.

`timeout` sets `HttpClient.Timeout`; when omitted the `HttpClient` default (100 s) applies. Streaming calls read the body
after the response headers arrive, so the timeout does not bound the length of a stream; stop a stream with the
`CancellationToken` you pass. Every method takes an optional `CancellationToken`.

### Optional flags and nullable fields

Request flags are `bool?` (`EnableGeocoding`, `EnableFuzzy`, `AllowLocality`, `CorrectStateFromZip`,
`IncludeMetadata`; the batch request has the first four). `null` is omitted from the JSON so the server default applies.

Response values that can be unknown are nullable: `Latitude`, `Longitude`, `AccuracyRadiusMeters`, `ConfidenceScore`
and `CorporateRiskScore` are `double?`; `Cmra` and `Vacant` are `bool?` (`null` means unknown, not `false`); strings such as
`Precision`, `Deliverability` and `Rdi` are `string?`. Check for `null` (or `HasValue`) before use.

### Streaming batches

`StreamBatchRecordsAsync` streams one `StreamRecord` per input, in order, over NDJSON. Each record has exactly one of
`Address` (a `StandardizedAddress`) or `Error` (a `RecordError` with `Index` and `Message`). A record the server
could not standardize arrives as `Error` and the enumeration continues:

```csharp
var request = new BatchStandardizeRequest
{
    Addresses = new List<object> { "100 Main St, Austin, TX 78701", "not an address" },
};

await foreach (var record in client.StreamBatchRecordsAsync(request, cancellationToken))
{
    if (record.Error != null)
    {
        Console.WriteLine($"record {record.Error.Index} failed: {record.Error.Message}");
        continue;
    }
    Console.WriteLine(record.Address!.Street1);
}
```

A stream that ends before one record per input has arrived throws `InvalidDataException`
(`Stream ended after N of M record(s).`) instead of silently truncating; a malformed line throws it too.

`StreamBatchAsync(IEnumerable<string>)` is the convenience form for plain address strings. It yields
`StandardizedAddress` values and throws `AddressStandardizerRecordException` (with `Index`) on the first record the
server could not standardize:

```csharp
try
{
    await foreach (var address in client.StreamBatchAsync(new[] { "100 Main St, Austin, TX 78701" }))
    {
        Console.WriteLine(address.Street1);
    }
}
catch (AddressStandardizerRecordException ex)
{
    Console.WriteLine($"record {ex.Index}: {ex.Message}");
}
```

### Autocomplete

`AutocompleteAsync` sends a POST; `AutocompleteGetAsync` sends the same `AutocompleteRequest` as a GET (limit, state
filter and proximity bias):

```csharp
var nearby = await client.AutocompleteGetAsync(new AutocompleteRequest
{
    Query = "350 5th",
    MaxResults = 5,
    StateFilter = "NY",
    Latitude = 40.75,
    Longitude = -73.99,
    RadiusMiles = 25,
});
```

`MaxResults` defaults to 10. `GetHealthAsync()` returns the service's `HealthResponse`.

### Error handling

Non-success responses throw `AddressStandardizerException` (a subclass of `HttpRequestException`) carrying
`ResponseStatusCode` and the full `ResponseBody`; the exception message holds only the first 512 characters of the body.

```csharp
try
{
    await client.StandardizeAsync("...");
}
catch (AddressStandardizerException ex) when (ex.ResponseStatusCode == HttpStatusCode.TooManyRequests)
{
    // back off and retry
}
```

---

## 📄 License & Ownership

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../../LICENSE)** for details.
