"""
Tests for SQL templates used by the pipeline_orchestrator DAG.

These tests validate that the SQL files under include/sql/ exist, are non-empty,
and contain expected keywords and correct dataset references. They do not execute
SQL against BigQuery -- they are static checks that catch broken or missing
templates before the DAG runs.
"""

from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "include" / "sql"

REQUIRED_SQL_FILES = [
    "validate_raw.sql",
    "transform_staging.sql",
    "dq_check_staging.sql",
    "transform_mart.sql",
    "publish_reporting.sql",
]

EXPECTED_DATASETS = ["raw", "staging", "mart", "reporting"]


@pytest.fixture(scope="module")
def sql_file_contents():
    """Load all required SQL files into a dict of {filename: content}."""
    contents = {}
    for filename in REQUIRED_SQL_FILES:
        path = SQL_DIR / filename
        if path.exists():
            contents[filename] = path.read_text(encoding="utf-8")
    return contents


def test_sql_dir_exists():
    assert SQL_DIR.exists(), f"Missing directory: {SQL_DIR}"


@pytest.mark.parametrize("filename", REQUIRED_SQL_FILES)
def test_sql_file_exists(filename):
    path = SQL_DIR / filename
    assert path.exists(), f"Missing SQL file: {filename}"


@pytest.mark.parametrize("filename", REQUIRED_SQL_FILES)
def test_sql_file_not_empty(filename):
    path = SQL_DIR / filename
    if not path.exists():
        pytest.skip(f"{filename} does not exist yet")
    text = path.read_text(encoding="utf-8").strip()
    assert len(text) > 0, f"{filename} is empty"


@pytest.mark.parametrize("filename", REQUIRED_SQL_FILES)
def test_sql_file_has_no_placeholder_todo(filename):
    path = SQL_DIR / filename
    if not path.exists():
        pytest.skip(f"{filename} does not exist yet")
    text = path.read_text(encoding="utf-8").upper()
    assert "TODO" not in text, f"{filename} still contains a TODO placeholder"
    assert "FIXME" not in text, f"{filename} still contains a FIXME placeholder"


def test_validate_raw_references_raw_dataset(sql_file_contents):
    text = sql_file_contents.get("validate_raw.sql", "")
    if not text:
        pytest.skip("validate_raw.sql not found")
    assert "raw." in text.lower() or "`raw`" in text.lower(), (
        "validate_raw.sql should reference the raw dataset"
    )


def test_transform_staging_references_staging_dataset(sql_file_contents):
    text = sql_file_contents.get("transform_staging.sql", "")
    if not text:
        pytest.skip("transform_staging.sql not found")
    assert "staging." in text.lower() or "`staging`" in text.lower(), (
        "transform_staging.sql should write to the staging dataset"
    )


def test_dq_check_staging_references_dq_failures(sql_file_contents):
    text = sql_file_contents.get("dq_check_staging.sql", "")
    if not text:
        pytest.skip("dq_check_staging.sql not found")
    assert "dq_failures" in text.lower(), (
        "dq_check_staging.sql should reference the dq_failures table"
    )


def test_transform_mart_references_mart_tables(sql_file_contents):
    text = sql_file_contents.get("transform_mart.sql", "").lower()
    if not text:
        pytest.skip("transform_mart.sql not found")
    expected_tables = ["dim_customer", "dim_event", "fct_registrations"]
    for table in expected_tables:
        assert table in text, f"transform_mart.sql should reference {table}"


def test_publish_reporting_references_reporting_dataset(sql_file_contents):
    text = sql_file_contents.get("publish_reporting.sql", "")
    if not text:
        pytest.skip("publish_reporting.sql not found")
    assert "reporting." in text.lower() or "`reporting`" in text.lower(), (
        "publish_reporting.sql should write to the reporting dataset"
    )


@pytest.mark.parametrize("filename", REQUIRED_SQL_FILES)
def test_sql_file_uses_fully_qualified_or_dataset_prefixed_names(filename, sql_file_contents):
    """
    Sanity check: every SQL file should reference at least one of the four
    known dataset names (raw, staging, mart, reporting), confirming it points
    at the correct project layer rather than an undefined or renamed dataset.
    """
    text = sql_file_contents.get(filename, "").lower()
    if not text:
        pytest.skip(f"{filename} not found")
    assert any(f"{ds}." in text or f"`{ds}`" in text for ds in EXPECTED_DATASETS), (
        f"{filename} does not reference any known dataset: {EXPECTED_DATASETS}"
    )