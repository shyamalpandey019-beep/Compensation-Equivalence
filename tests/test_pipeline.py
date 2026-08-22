# tests/test_pipeline.py
# pyrefly: ignore [missing-import]
import pytest
from src.pipeline import run_pipeline

def test_run_pipeline_in_bangalore():
    # Testing 2,500,000 INR for Bangalore, IN.
    # Note: Nominal and PPP conversions depend on the live fetched data in data/raw.
    # We assert structural integrity and the deterministic tax math.
    
    result = run_pipeline(2500000, "IN", "Bangalore")
    
    # 1. Check Input
    assert result["input"]["gross_salary"] == 2500000
    assert result["input"]["currency"] == "INR"
    assert result["input"]["city"] == "Bangalore"
    assert result["input"]["country"] == "IN"
    
    # 2. Check Tax Breakdown keys
    assert "net_local" in result["tax"]
    assert "tax_deducted" in result["tax"]
    assert "effective_tax_rate_pct" in result["tax"]
    
    # 3. Check Normalized Equivalence Metrics
    assert "nominal_usd" in result["normalized"]
    assert "ppp_int_dollars" in result["normalized"]
    assert "col_adjusted_usd" in result["normalized"]
    
   # 4. Math assertion (The IN net pay for 2.5M INR should be exactly 2,047,600)
    assert result["tax"]["net_local"] == 2047600.0

def test_run_pipeline_invalid_country():
    with pytest.raises(ValueError):
        run_pipeline(100000, "FR", "Paris")