# address-standardizer-go 🦫

Official Go client SDK for the **Address Standardizer** HTTP microservice daemon.

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**.

---

## Installation

```bash
go get github.com/jwhite/address-standardizer-go
```

---

## Usage

```go
package main

import (
	"context"
	"fmt"
	"log"

	standardizer "github.com/jwhite/address-standardizer-go"
)

func main() {
	ctx := context.Background()
	client := standardizer.NewClient("http://localhost:8000")

	// Standardize single address
	res, err := client.Standardize(ctx, standardizer.StandardizeRequest{
		Address: "1600 Pennsylvania Ave NW, Washington, DC 20500",
		Geocode: true,
	})
	if err != nil {
		log.Fatalf("Standardization failed: %v", err)
	}

	fmt.Println("Delivery:", res.DeliveryLine1)
	fmt.Println("City/State/Zip:", res.LastLine)
	fmt.Println("Confidence:", res.ConfidenceScore)

	// Interactive autocomplete
	suggestions, err := client.Autocomplete(ctx, standardizer.AutocompleteRequest{
		Query: "1600 Penn",
		Limit: 5,
	})
	if err != nil {
		log.Fatalf("Autocomplete failed: %v", err)
	}

	for _, s := range suggestions {
		fmt.Printf("- %s (Score: %.2f)\n", s.DisplayText, s.RelevanceScore)
	}
}
```

---

## 📄 License & Ownership

Owned and maintained by **HobbyHabbit LLC** under the **MIT License**. See **[LICENSE](../../LICENSE)** for details.
