# src/tax/calculator.py
import yaml
import math
from pathlib import Path

def load_tax_data():
    yaml_path = Path(__file__).parent.parent.parent / "data" / "reference" / "tax_brackets.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

TAX_DATA = load_tax_data()

def calculate_in_tax(gross: float, data: dict) -> float:
    # India New Regime
    taxable = max(0, gross - data["standard_deduction"])
    # 2024 rebate under Section 87A for New Regime
    if taxable <= 700000:
        return 0.0
        
    tax = 0.0
    prev_max = 0.0
    for bracket in data["brackets"]:
        cap = bracket["max_taxable"]
        if cap is None or taxable <= cap:
            tax += (taxable - prev_max) * bracket["rate"]
            break
        else:
            tax += (cap - prev_max) * bracket["rate"]
            prev_max = cap
            
    # 4% Health & Education Cess
    return tax * 1.04

def calculate_jp_tax(gross: float, data: dict) -> float:
    # 1. Employment Income Deduction
    emp_deduction = 0.0
    for tier in data["employment_income_deduction"]:
        if tier["max_gross"] is None or gross <= tier["max_gross"]:
            emp_deduction = gross * tier["multiplier"] + tier["base"]
            break
            
    # 2. Taxable Income
    taxable = max(0, gross - emp_deduction - data["basic_deduction"])
    # Round down to nearest 1,000 JPY
    taxable = math.floor(taxable / 1000) * 1000
    
    if taxable <= 0:
        return 0.0

    # 3. Apply brackets (Rate * Taxable - Deduction)
    tax = 0.0
    for bracket in data["brackets"]:
        if bracket["max_taxable"] is None or taxable <= bracket["max_taxable"]:
            tax = (taxable * bracket["rate"]) - bracket["deduction"]
            break
            
    # 2.1% Special Income Tax for Reconstruction
    return tax * 1.021

def calculate_de_tax(gross: float, data: dict) -> float:
    # Simplified taxable income (assuming standard deductions apply to reach zvE)
    # In a full model, we'd calculate social security deductions first, but 
    # for equivalence benchmarking, we map Gross directly to zvE for income tax bounds.
    zve = math.floor(gross)
    
    if zve <= data["zones"][0]["max_taxable"]:
        return 0.0
        
    # Zone 2
    if zve <= data["zones"][1]["max_taxable"]:
        z = data["zones"][1]
        y = (zve - z["y_offset"]) / 10000
        return (z["a"] * y + z["b"]) * y + z["c"]
        
    # Zone 3
    if zve <= data["zones"][2]["max_taxable"]:
        z = data["zones"][2]
        y = (zve - z["y_offset"]) / 10000
        return (z["a"] * y + z["b"]) * y + z["c"]
        
    # Zone 4
    if zve <= data["zones"][3]["max_taxable"]:
        z = data["zones"][3]
        return (zve * z["rate"]) - z["deduction"]
        
    # Zone 5
    z = data["zones"][4]
    return (zve * z["rate"]) - z["deduction"]

def get_net_pay(gross: float, country_code: str) -> float:
    country_code = country_code.upper()
    if country_code not in TAX_DATA:
        raise ValueError(f"No tax data for {country_code}")
        
    data = TAX_DATA[country_code]
    
    if country_code == "IN":
        tax = calculate_in_tax(gross, data)
    elif country_code == "JP":
        tax = calculate_jp_tax(gross, data)
    elif country_code == "DE":
        tax = calculate_de_tax(gross, data)
    else:
        raise NotImplementedError()
        
    return gross - tax