# AddressStandardizer.Client (.NET) 🚀

Official .NET client SDK for the **Address Standardizer** HTTP microservice daemon, targeting .NET 8.0 and .NET Standard 2.0.

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**.

---

## Installation

```bash
dotnet add package AddressStandardizer.Client
```

---

## Usage

```csharp
using AddressStandardizer.Client;

// Initialize client
using var client = new AddressStandardizerClient("http://localhost:8000");

// Standardize single address
var result = await client.StandardizeAsync(new StandardizeRequest
{
    Address = "350 5th Ave, New York, NY 10118",
    Geocode = true,
});

Console.WriteLine($"Delivery: {result.DeliveryLine1}");
Console.WriteLine($"City/State/Zip: {result.LastLine}");

// Batch standardization
var batchResults = await client.StandardizeBatchAsync(new BatchStandardizeRequest
{
    Addresses = new List<string>
    {
        "100 Main St, Austin, TX 78701",
        "200 S Wacker Dr, Chicago, IL 60606",
    },
});

// Autocomplete prefix suggestions
var suggestions = await client.AutocompleteAsync(new AutocompleteRequest
{
    Query = "100 Main",
    Limit = 5,
});
foreach (var s in suggestions)
{
    Console.WriteLine($"Suggestion: {s.DisplayText}");
}
```

---

## 📄 License & Ownership

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../../LICENSE)** for details.
