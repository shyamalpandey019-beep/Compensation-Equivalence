# src/normalize/adjust.py
import yaml
from pathlib import Path

def load_col_data():
    yaml_path = Path(__file__).resolve().parents[2] / "data" / "reference" / "col_index.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

COL_DATA = load_col_data()

def calculate_nominal(net_local: float, fx_rate: float) -> float:
    """Converts local currency to USD via standard FX rate."""
    return net_local / fx_rate

def calculate_ppp(net_local: float, ppp_conversion_factor: float) -> float:
    """Converts local currency to International Dollars using World Bank PPP."""
    return net_local / ppp_conversion_factor

def calculate_col_adjusted(nominal_usd: float, country_code: str, city_name: str) -> float:
    """Adjusts nominal USD based on the specific city's Cost of Living index relative to NYC."""
    country_code = country_code.upper()
    
    if country_code not in COL_DATA["cities"]:
        raise ValueError(f"No COL data for country: {country_code}")
        
    if city_name not in COL_DATA["cities"][country_code]:
        raise ValueError(f"No COL data for city: {city_name} in {country_code}")
        
    city_index = COL_DATA["cities"][country_code][city_name]
    base_index = COL_DATA["base_index"]
    
    # Purchasing power multiplier relative to the NYC baseline
    purchasing_power_multiplier = base_index / city_index
    return nominal_usd * purchasing_power_multiplier