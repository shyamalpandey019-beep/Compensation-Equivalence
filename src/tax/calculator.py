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

def calculate_us_tax(gross: float, data: dict) -> float:
    # 1. FICA (Calculated on GROSS wages)
    fica_data = data["fica"]
    social_security = min(gross, fica_data["ss_cap"]) * fica_data["ss_rate"]
    medicare = gross * fica_data["medicare_rate"]
    
    additional_medicare = 0.0
    if gross > fica_data["additional_medicare_threshold"]:
        additional_medicare = (gross - fica_data["additional_medicare_threshold"]) * fica_data["additional_medicare_rate"]
        
    total_fica = social_security + medicare + additional_medicare

    # 2. Federal Income Tax (Calculated on TAXABLE income after standard deduction)
    taxable = max(0.0, gross - data["standard_deduction"])
    federal_tax = 0.0
    prev_max = 0.0
    
    for bracket in data["brackets"]:
        cap = bracket["max_taxable"]
        if cap is None or taxable <= cap:
            federal_tax += (taxable - prev_max) * bracket["rate"]
            break
        else:
            federal_tax += (cap - prev_max) * bracket["rate"]
            prev_max = cap

    return federal_tax + total_fica

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
    elif country_code == "US":
        tax = calculate_us_tax(gross, data)
    else:
        raise NotImplementedError()
        
    return gross - tax

def get_tax_breakdown(gross: float, country_code: str) -> dict:
    country_code = country_code.upper()
    if country_code not in TAX_DATA:
        raise ValueError(f"No tax data for {country_code}")
        
    data = TAX_DATA[country_code]
    currency = data.get("currency", "USD")
    items = []
    
    if country_code == "IN":
        std_ded = data["standard_deduction"]
        taxable = max(0, gross - std_ded)
        items.append({"label": "Standard Deduction", "amount": std_ded, "type": "deduction", "note": "Statutory relief"})
        
        if taxable <= 700000:
            raw_tax = 0.0
            cess = 0.0
            items.append({"label": "Income Tax (Sec 87A Rebate)", "amount": 0.0, "type": "tax", "note": "100% rebate under ₹7L taxable"})
        else:
            raw_tax = 0.0
            prev_max = 0.0
            for bracket in data["brackets"]:
                cap = bracket["max_taxable"]
                if cap is None or taxable <= cap:
                    raw_tax += (taxable - prev_max) * bracket["rate"]
                    break
                else:
                    raw_tax += (cap - prev_max) * bracket["rate"]
                    prev_max = cap
            cess = raw_tax * 0.04
            items.append({"label": "Income Tax (Slabs)", "amount": raw_tax, "type": "tax", "note": "New Regime progressive slabs"})
            items.append({"label": "Health & Education Cess (4%)", "amount": cess, "type": "tax", "note": "4% on income tax"})
        total_tax = raw_tax + cess
        
    elif country_code == "US":
        std_ded = data["standard_deduction"]
        taxable = max(0.0, gross - std_ded)
        items.append({"label": "Standard Deduction", "amount": std_ded, "type": "deduction", "note": "Single filer baseline"})
        
        fica_data = data["fica"]
        ss_tax = min(gross, fica_data["ss_cap"]) * fica_data["ss_rate"]
        med_tax = gross * fica_data["medicare_rate"]
        addl_med = (gross - fica_data["additional_medicare_threshold"]) * fica_data["additional_medicare_rate"] if gross > fica_data["additional_medicare_threshold"] else 0.0
        
        fed_tax = 0.0
        prev_max = 0.0
        for bracket in data["brackets"]:
            cap = bracket["max_taxable"]
            if cap is None or taxable <= cap:
                fed_tax += (taxable - prev_max) * bracket["rate"]
                break
            else:
                fed_tax += (cap - prev_max) * bracket["rate"]
                prev_max = cap
                
        items.append({"label": "Federal Income Tax", "amount": fed_tax, "type": "tax", "note": "Progressive 7-bracket model"})
        items.append({"label": "FICA Social Security (6.2%)", "amount": ss_tax, "type": "tax", "note": f"Capped at ${fica_data['ss_cap']:,}"})
        items.append({"label": "FICA Medicare (1.45%)", "amount": med_tax + addl_med, "type": "tax", "note": "Hospital insurance" + (" + 0.9% high income" if addl_med > 0 else "")})
        total_tax = fed_tax + ss_tax + med_tax + addl_med
        
    elif country_code == "DE":
        total_tax = calculate_de_tax(gross, data)
        items.append({"label": "Progressive Income Tax (ESt)", "amount": total_tax, "type": "tax", "note": "Tarif 2024 (Zones 1-5 formula)"})
        
    elif country_code == "JP":
        emp_deduction = 0.0
        for tier in data["employment_income_deduction"]:
            if tier["max_gross"] is None or gross <= tier["max_gross"]:
                emp_deduction = gross * tier["multiplier"] + tier["base"]
                break
        basic_ded = data["basic_deduction"]
        items.append({"label": "Employment Income Deduction", "amount": emp_deduction, "type": "deduction", "note": "Salaried earner deduction"})
        items.append({"label": "Basic Deduction", "amount": basic_ded, "type": "deduction", "note": "Standard personal exemption"})
        
        taxable = max(0, gross - emp_deduction - basic_ded)
        taxable = math.floor(taxable / 1000) * 1000
        
        if taxable <= 0:
            nat_tax = 0.0
            recon_tax = 0.0
        else:
            nat_tax = 0.0
            for bracket in data["brackets"]:
                if bracket["max_taxable"] is None or taxable <= bracket["max_taxable"]:
                    nat_tax = (taxable * bracket["rate"]) - bracket["deduction"]
                    break
            recon_tax = nat_tax * 0.021
            
        items.append({"label": "National Income Tax", "amount": nat_tax, "type": "tax", "note": "National progressive brackets"})
        items.append({"label": "Special Reconstruction Tax (2.1%)", "amount": recon_tax, "type": "tax", "note": "2.1% on income tax"})
        total_tax = nat_tax + recon_tax
        
    net_pay = gross - total_tax
    return {
        "gross": gross,
        "currency": currency,
        "total_tax": round(total_tax, 2),
        "net_pay": round(net_pay, 2),
        "effective_rate_pct": round((total_tax / gross) * 100, 2) if gross > 0 else 0.0,
        "items": items
    }