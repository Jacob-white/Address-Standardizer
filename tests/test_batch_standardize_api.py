"""
Unit tests for the public batch_standardize Python API.
"""

from typing import Iterator
from address_standardizer import batch_standardize, StandardizedAddress


class TestBatchStandardizeAPI:
    def test_batch_standardize_string_iterable(self):
        addresses = [
            "100 Wall Street, Suite 400, New York, NY 10005",
            "200 Park Ave, New York, NY 10166",
            "PSC 1004 BOX 500, APO, AE 09724",
        ]
        gen = batch_standardize(addresses)
        assert isinstance(gen, Iterator)

        results = list(gen)
        assert len(results) == 3
        assert all(isinstance(r, StandardizedAddress) for r in results)

        assert results[0].street1 == "100 WALL ST"
        assert results[0].street2 == "STE 400"
        assert results[0].city == "NEW YORK"

        assert results[1].street1 == "200 PARK AVE"
        assert results[1].city == "NEW YORK"

        assert results[2].street1 == "PSC 1004 BOX 500"
        assert results[2].city == "APO"
        assert results[2].state == "AE"

    def test_batch_standardize_dict_iterable(self):
        records = [
            {
                "street1": "100 Wall St",
                "street2": "Suite 400",
                "city": "New York",
                "state": "NY",
                "postal_code": "10005",
                "country": "USA",
            },
            {
                "address": "350 5th Ave",
                "city": "New York",
                "state": "NY",
                "zip": "10118",
            },
        ]
        results = list(batch_standardize(records))
        assert len(results) == 2
        assert results[0].street1 == "100 WALL ST"
        assert results[0].street2 == "STE 400"
        assert results[1].street1 == "350 5TH AVE"
        assert results[1].postal_code == "10118"

    def test_batch_standardize_generator_laziness(self):
        call_count = 0

        def input_generator():
            nonlocal call_count
            for addr in ["100 Wall St, NY, NY 10005", "200 Park Ave, NY, NY 10166"]:
                call_count += 1
                yield addr

        gen = batch_standardize(input_generator())
        assert call_count == 0  # not yet consumed
        first = next(gen)
        assert call_count == 1
        assert first.street1 == "100 WALL ST"

    def test_batch_standardize_with_kwargs(self):
        records = [
            {"street1": "100 Main St VACANT", "city": "New York", "state": "NY", "postal_code": "10001", "is_vacant": True}
        ]
        results = list(batch_standardize(records, enable_fuzzy=True))
        assert len(results) == 1
        assert results[0].street1 == "100 MAIN ST"
        assert results[0].is_vacant is True

    def test_batch_standardize_empty_iterable(self):
        results = list(batch_standardize([]))
        assert results == []
