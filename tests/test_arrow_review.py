"""Regressions from the whole-codebase review of the Arrow/Polars plugin."""

import warnings

import pytest

from tests._deps import require

pa = require("pyarrow")

from address_standardizer.arrow import standardize_arrow  # noqa: E402


def _table(rows=1):
    return pa.table(
        {
            "street1": ["100 Wall St"] * rows,
            "city": ["New York"] * rows,
            "state": ["NY"] * rows,
            "postal_code": ["10005"] * rows,
        }
    )


def test_empty_record_batch_returns_an_empty_batch_with_the_output_schema():
    batch = _table(0).to_batches()[0] if _table(0).to_batches() else pa.RecordBatch.from_pylist(
        [], schema=_table(0).schema
    )
    out = standardize_arrow(batch)
    assert isinstance(out, pa.RecordBatch)
    assert out.num_rows == 0
    assert "std_street1" in out.schema.names


def test_reapplying_replaces_instead_of_duplicating_columns():
    once = standardize_arrow(_table())
    twice = standardize_arrow(once)
    assert twice.column_names.count("std_street1") == 1
    assert len(twice.column_names) == len(once.column_names)
    struct_once = standardize_arrow(_table(), as_struct=True)
    struct_twice = standardize_arrow(struct_once, as_struct=True)
    assert struct_twice.column_names.count("standardized_address") == 1


def test_missing_street_column_raises_and_other_missing_columns_warn():
    with pytest.raises(ValueError, match="street1_col"):
        standardize_arrow(_table(), street1_col="nope")
    with pytest.warns(UserWarning, match="not found"):
        standardize_arrow(pa.table({"street1": ["100 Wall St"]}))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        standardize_arrow(_table())
