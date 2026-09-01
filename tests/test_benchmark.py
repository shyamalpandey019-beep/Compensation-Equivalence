# tests/test_benchmark.py
import pytest
from src.benchmark import calculate_percentile

def test_benchmark_known_roles():
    # India Software Engineer (p25: 15L, p50: 25L, p75: 40L)
    assert calculate_percentile(1500000, "IN", "Software Engineer") == 25.0
    assert calculate_percentile(2500000, "IN", "Software Engineer") == 50.0
    assert calculate_percentile(4000000, "IN", "Software Engineer") == 75.0

def test_benchmark_interpolation():
    # Midpoint between p25 (15L) and p50 (25L) -> 37.5
    p = calculate_percentile(2000000, "IN", "Software Engineer")
    assert p == 37.5

def test_benchmark_out_of_bounds():
    # Below p25
    low_p = calculate_percentile(750000, "IN", "Software Engineer")
    assert low_p == 12.5
    
    # Above p75
    high_p = calculate_percentile(8000000, "IN", "Software Engineer")
    assert high_p > 75.0
    assert high_p <= 99.9

def test_benchmark_missing_country_or_role():
    # Missing country fallback
    assert calculate_percentile(100000, "ZZ", "Software Engineer") == 50.0
    # Missing role fallback
    assert calculate_percentile(100000, "IN", "Chief Executive Officer") == 50.0
