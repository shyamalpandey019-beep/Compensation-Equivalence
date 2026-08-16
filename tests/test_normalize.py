# tests/test_normalize.py
import pytest
from src.normalize.adjust import calculate_nominal, calculate_ppp, calculate_col_adjusted

def test_calculate_nominal():
    # 100,000 INR at an FX rate of 83.5 INR/USD should be ~1197.60 USD
    result = calculate_nominal(100000, 83.5)
    assert abs(result - 1197.60) < 0.1

def test_calculate_ppp():
    # 100,000 INR at a PPP factor of 23.0 LCU per Int$ should be ~4347.82 Int$
    result = calculate_ppp(100000, 23.0)
    assert abs(result - 4347.82) < 0.1

def test_calculate_col_adjusted():
    from src.normalize import adjust
    
    # Temporarily mock COL_DATA to establish a clean 50.0 index for easy assertion
    original_data = adjust.COL_DATA
    adjust.COL_DATA = {
        "base_index": 100.0,
        "cities": {"DE": {"Berlin": 50.0}}
    }
    
    # We now pass both the country code ("DE") and the city name ("Berlin")
    result = calculate_col_adjusted(50000, "DE", "Berlin")
    
    # Restore original data structure
    adjust.COL_DATA = original_data
    
    # 50,000 Nominal USD in a city half as expensive as NYC (index 50) 
    # yields a purchasing power equivalent of 100,000 USD.
    assert result == 100000.0