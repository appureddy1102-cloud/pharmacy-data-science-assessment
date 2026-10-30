"""Deterministic fixtures: tests generate their own temporary input data."""

import pytest

from pharmacy_ds.cleaning import clean_data
from pharmacy_ds.generate import generate_sample_data


@pytest.fixture
def raw(tmp_path):
    return generate_sample_data(tmp_path / "sample.csv")


@pytest.fixture
def cleaned(raw):
    return clean_data(raw)
