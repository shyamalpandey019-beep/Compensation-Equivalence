# src/api.py
import sys
from pathlib import Path

# 0. Path Resolution Fix (Same as our Streamlit fix)
# Forces Python to look in the main project root
project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    sys.path.append(project_root)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.pipeline import run_pipeline

# 1. Initialize the API (This is the 'app' Uvicorn is looking for!)
app = FastAPI(
    title="Compensation Equivalence API",
    description="API for calculating statutory tax, PPP, and benchmarking compensation.",
    version="1.0.0"
)

# 2. Define the format of the data we expect to receive
class SalaryRequest(BaseModel):
    gross_salary: float
    country_code: str
    city_name: str

# 3. Create the endpoint
@app.post("/api/v1/calculate")
def calculate_compensation(request: SalaryRequest):
    try:
        # Pass the incoming data straight into our engine
        result = run_pipeline(
            gross_salary=request.gross_salary,
            country_code=request.country_code,
            city_name=request.city_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))