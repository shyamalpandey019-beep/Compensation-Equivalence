# tests/test_score.py
import pytest
from src.score import calculate_score

def test_calculate_score_balanced():
    # 50th percentile (50 * 0.5 = 25) + $100k COL (100 * 0.5 = 50) = 75
    score = calculate_score(percentile=50.0, col_adjusted_usd=100000.0)
    assert score == 75

def test_calculate_score_cap():
    # 90th percentile (45) + $300k COL (capped at 100 -> 50) = 95
    score = calculate_score(percentile=90.0, col_adjusted_usd=300000.0)
    assert score == 95

def test_calculate_score_low():
    # 10th percentile (5) + $20k COL (20 * 0.5 = 10) = 15
    score = calculate_score(percentile=10.0, col_adjusted_usd=20000.0)
    assert score == 15
