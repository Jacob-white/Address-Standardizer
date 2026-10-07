"""
Test Suite for Modern Data Stack Plugins: Apache Arrow, Polars, and DuckDB.
===========================================================================
"""

import duckdb
import polars as pl
import pyarrow as pa
import pytest

from address_standardizer.arrow import (
    register_duckdb_udfs,
    standardize_arrow,
    standardize_polars,
)


@pytest.fixture
def sample_arrow_table():
    return pa.Table.from_pydict({
        "street1": ["100 Wall St", "350 5th Ave", "1600 Pennsylvania Ave NW"],
        "city": ["New York", "New York", "Washington"],
        "state": ["NY", "NY", "DC"],
        "postal_code": ["10005", "10118", "20500"],
    })


def test_standardize_arrow_columns(sample_arrow_table):
    out_table = standardize_arrow(sample_arrow_table, enable_geocoding=True)
    assert isinstance(out_table, pa.Table)
    assert out_table.num_rows == 3

    assert "std_street1" in out_table.column_names
    assert "std_deliverability" in out_table.column_names
    assert "std_latitude" in out_table.column_names
    assert "std_precision" in out_table.column_names
    assert "std_census_tract" in out_table.column_names

    st1_list = out_table.column("std_street1").to_pylist()
    assert st1_list[0] == "100 WALL ST"
    assert st1_list[1] == "350 5TH AVE"
    assert st1_list[2] == "1600 PENNSYLVANIA AVE NW"

    deliv_list = out_table.column("std_deliverability").to_pylist()
    assert deliv_list[0] == "REQUIRES_SECONDARY"
    assert deliv_list[1] == "DELIVERABLE"
    assert deliv_list[2] == "DELIVERABLE"


def test_standardize_arrow_as_struct(sample_arrow_table):
    out_table = standardize_arrow(sample_arrow_table, as_struct=True)
    assert "standardized_address" in out_table.column_names
    struct_col = out_table.column("standardized_address")
    assert pa.types.is_struct(struct_col.type)

    first_val = struct_col[0].as_py()
    assert first_val["street1"] == "100 WALL ST"
    assert first_val["city"] == "NEW YORK"
    assert first_val["deliverability"] == "REQUIRES_SECONDARY"


def test_standardize_arrow_record_batch(sample_arrow_table):
    batch = sample_arrow_table.to_batches()[0]
    out_batch = standardize_arrow(batch)
    assert isinstance(out_batch, pa.RecordBatch)
    assert out_batch.num_rows == 3
    assert "std_street1" in out_batch.schema.names


def test_standardize_polars_dataframe():
    df = pl.DataFrame({
        "street1": ["100 Wall St", "200 Park Ave"],
        "city": ["New York", "New York"],
        "state": ["NY", "NY"],
        "postal_code": ["10005", "10166"],
    })
    res_df = standardize_polars(df, enable_geocoding=True)
    assert isinstance(res_df, pl.DataFrame)
    assert res_df.shape[0] == 2
    assert "std_street1" in res_df.columns
    assert "std_deliverability" in res_df.columns
    assert res_df["std_street1"].to_list() == ["100 WALL ST", "200 PARK AVE"]
    assert res_df["std_deliverability"].to_list() == ["REQUIRES_SECONDARY", "REQUIRES_SECONDARY"]


def test_standardize_polars_lazyframe():
    df = pl.DataFrame({
        "street1": ["100 Wall St"],
        "city": ["New York"],
        "state": ["NY"],
        "postal_code": ["10005"],
    }).lazy()

    res_lazy = standardize_polars(df)
    assert isinstance(res_lazy, pl.LazyFrame)
    collected = res_lazy.collect()
    assert collected.shape[0] == 1
    assert collected["std_street1"][0] == "100 WALL ST"


def test_duckdb_udf_registration_and_queries():
    con = duckdb.connect()
    register_duckdb_udfs(con)

    # 1. Test 4-arg struct function
    q1 = "SELECT standardize_address('100 Wall St', 'New York', 'NY', '10005') as res"
    row1 = con.execute(q1).fetchone()
    assert row1 is not None
    res_struct = row1[0]
    assert res_struct["street1"] == "100 WALL ST"
    assert res_struct["deliverability"] == "REQUIRES_SECONDARY"
    assert res_struct["latitude"] == 40.7061
    assert res_struct["precision"] in ("ROOFTOP", "CONFIRMED_ROOFTOP")

    # 2. Test deliverability scalar function
    q2 = "SELECT standardize_deliverability('100 Wall St', 'New York', 'NY', '10005') as d"
    row2 = con.execute(q2).fetchone()
    assert row2[0] == "REQUIRES_SECONDARY"

    # 3. Test address key scalar function
    q3 = "SELECT standardize_address_key('100 Wall St', 'New York', 'NY', '10005') as k"
    row3 = con.execute(q3).fetchone()
    assert "100 WALL ST" in row3[0]

    # 4. Test single text argument function
    q4 = "SELECT standardize_address_text('1600 Pennsylvania Ave NW, Washington, DC 20500') as res"
    row4 = con.execute(q4).fetchone()
    assert row4[0]["street1"] == "1600 PENNSYLVANIA AVE NW"
    assert row4[0]["deliverability"] == "DELIVERABLE"
