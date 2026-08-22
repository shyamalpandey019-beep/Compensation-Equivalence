# src/api.py
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Path resolution fix
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from src.pipeline import run_pipeline

app = FastAPI(
    title="Compensation Equivalence API",
    description="API for calculating statutory tax, PPP, and benchmarking compensation.",
    version="1.0.0"
)

# Added 'role' to the expected payload with a default value
class SalaryRequest(BaseModel):
    gross_salary: float
    country_code: str
    city_name: str
    role: str = "Software Engineer"

@app.post("/api/v1/calculate")
def calculate_compensation(request: SalaryRequest):
    try:
        result = run_pipeline(
            gross_salary=request.gross_salary,
            country_code=request.country_code,
            city_name=request.city_name,
            role=request.role
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))