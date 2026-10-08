# address-standardizer-go 🦫

Official Go client SDK for the **Address Standardizer** HTTP microservice daemon.

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**.

---

## Installation

```bash
go get github.com/Jacob-white/Address-Standardizer/sdks/go
```

---

## Usage

```go
package main

import (
	"context"
	"fmt"
	"log"

	standardizer "github.com/Jacob-white/Address-Standardizer/sdks/go"
)

func main() {
	ctx := context.Background()
	client := standardizer.NewClient("http://localhost:8000")

	// Standardize single address. Flags are optional pointers: leave them nil
	// to use the server defaults (geocoding and fuzzy matching enabled).
	result, err := client.Standardize(ctx, standardizer.StandardizeRequest{
		Address:         "100 Main St, Austin, TX 78701",
		EnableGeocoding: standardizer.Bool(true),
	})
	if err != nil {
		log.Fatalf("Standardization failed: %v", err)
	}

	fmt.Printf("Street: %s\n", result.Street1)
	fmt.Printf("City/State/Zip: %s, %s %s\n", result.City, result.State, result.PostalCode)
	fmt.Printf("Precision: %s\n", result.Precision)

	// Interactive autocomplete
	suggestions, err := client.Autocomplete(ctx, standardizer.AutocompleteRequest{
		Query:      "100 Mai",
		MaxResults: 5,
	})
	if err != nil {
		log.Fatalf("Autocomplete failed: %v", err)
	}

	for _, s := range suggestions {
		fmt.Printf("- %s\n", s.Text)
	}
}
```

---

## 📄 License & Ownership

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../../LICENSE)** for details.
