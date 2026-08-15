# tests/test_tax.py
import pytest
from src.tax.calculator import get_net_pay

def test_india_rebate_limit():
    # IN New Regime: 700k taxable (750k gross due to 50k standard deduction) pays 0 tax
    assert get_net_pay(750000, "IN") == 750000
    
def test_india_standard_tax():
    # 1.2M gross -> 1.15M taxable
    # 3L@0% + 3L@5% (15k) + 3L@10% (30k) + 2.5L@15% (37.5k) = 82,500
    # + 4% cess = 85,800 tax. Net = 1,114,200
    net = get_net_pay(1200000, "IN")
    assert net == 1200000 - 85800

def test_japan_tax():
    # 6M gross. Emp deduction: (6M * 0.2) + 440k = 1.64M
    # Basic: 480k. Taxable: 6M - 1.64M - 0.48M = 3.88M
    # Tax: (3.88M * 0.2) - 427,500 = 348,500
    # + 2.1% reconstruction = 355,818.5 tax
    net = get_net_pay(6000000, "JP")
    expected_net = 6000000 - 355818.5
    assert abs(net - expected_net) < 1.0 # Allow for minor float precision differences

def test_germany_zones():
    # Zone 1 (0 tax)
    assert get_net_pay(12000, "DE") == 12000
    
    # Zone 2 check (Math formula)
    # zvE = 15000. y = (15000 - 12096) / 10000 = 0.2904
    # ESt = (912.17 * 0.2904 + 1400) * 0.2904 + 0 = 483.48
    net = get_net_pay(15000, "DE")
    expected_net = 15000 - 483.48
    assert abs(net - expected_net) < 1.0

def test_us_federal_tax():
    # $100,000 gross in 2024:
    # FICA = $6,200 (SS) + $1,450 (Medicare) = $7,650
    # Taxable = $100,000 - $14,600 = $85,400
    # Fed Tax = 10% on 11.6k ($1,160) + 12% on (47.15k-11.6k) ($4,266) + 22% on (85.4k-47.15k) ($8,415) = $13,841
    # Total Tax = $21,491 -> Net = $78,509
    net = get_net_pay(100000, "US")
    expected_net = 78509
    assert abs(net - expected_net) < 1.0