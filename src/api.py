# src/api.py
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# Path resolution fix
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from src.pipeline import (
    run_pipeline, 
    calculate_parity_matrix, 
    load_raw_data, 
    COUNTRY_CURRENCY_MAP, 
    COUNTRY_ISO3_MAP, 
    MAJOR_GLOBAL_HUBS
)
from src.normalize.adjust import COL_DATA
from src.benchmark import BENCHMARK_FILE
import json

app = FastAPI(
    title="EquivPay Global Compensation Normalization Engine API",
    description="Statutory Tax Modeling, PPP Normalization, Cost-of-Living Indexing, and Market Banding REST API.",
    version="1.1.0"
)


class SalaryRequest(BaseModel):
    gross_salary: float = Field(..., gt=0, description="Gross annual salary in local currency", json_schema_extra={"example": 3500000})
    country_code: str = Field(..., description="2-letter ISO country code (IN, US, DE, JP)", json_schema_extra={"example": "IN"})
    city_name: str = Field(..., description="Metropolitan city name", json_schema_extra={"example": "Bangalore"})
    role: str = Field(default="Software Engineer", description="Job role for market benchmarking", json_schema_extra={"example": "Software Engineer"})
    include_parity: bool = Field(default=False, description="Whether to include multi-city global parity matrix")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "equivpay-engine", "version": "1.1.0"}


@app.get("/api/v1/metadata")
def get_metadata():
    fx_data, ppp_data = load_raw_data()
    with open(BENCHMARK_FILE, "r", encoding="utf-8") as f:
        bench_data = json.load(f)

    return {
        "supported_countries": list(COUNTRY_CURRENCY_MAP.keys()),
        "currencies": COUNTRY_CURRENCY_MAP,
        "cities": COL_DATA.get("cities", {}),
        "roles": ["Software Engineer", "Data Scientist", "Data Analyst"],
        "fx_rates": fx_data.get("rates", {}),
        "ppp_factors": {c: ppp_data["latest_per_country"].get(iso3, {}).get("value") for c, iso3 in COUNTRY_ISO3_MAP.items()},
        "major_hubs": MAJOR_GLOBAL_HUBS
    }


@app.post("/api/v1/calculate")
def calculate_compensation(request: SalaryRequest):
    try:
        result = run_pipeline(
            gross_salary=request.gross_salary,
            country_code=request.country_code,
            city_name=request.city_name,
            role=request.role,
            include_parity=request.include_parity
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/parity")
def get_global_parity(
    gross_salary: float = Query(..., gt=0, description="Gross annual salary in local currency"),
    country_code: str = Query(..., description="2-letter ISO country code (IN, US, DE, JP)"),
    city_name: str = Query(..., description="Metropolitan city name")
):
    try:
        matrix = calculate_parity_matrix(gross_salary, country_code, city_name)
        return {
            "source": {
                "gross_salary": gross_salary,
                "country_code": country_code.upper(),
                "city_name": city_name
            },
            "parity_matrix": matrix
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))