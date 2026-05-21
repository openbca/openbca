import logging
import os
import traceback
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException

from api import calculator, precompute
from api.models import CalculateRequest, CalculateResponse
from config.env import setup_env_vars
from config.paths import get_output_dir

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_env_vars()
    db_path = os.environ.get("DB", str(get_output_dir() / "openbca.db"))
    app.state.precomputed = precompute.load(db_path)
    yield


app = FastAPI(title="OpenBCA API", lifespan=lifespan)


def _run(request: CalculateRequest, outputs: set[str]) -> dict:
    measures = [m.model_dump() for m in request.measures]
    try:
        return calculator.run(measures, app.state.precomputed, outputs=outputs)
    except Exception as exc:
        logger.error("Error running %s:\n%s", outputs, traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health")
def health():
    return {"status": "ok", "precomputed": hasattr(app.state, "precomputed")}


@app.post("/calculate", response_model=CalculateResponse)
def calculate(request: CalculateRequest):
    return _run(request, outputs={
        "jst_ratio",
        "results_summary_by_id",
        "final_value_calculations_ts",
        "final_savings_calculations_ts",
    })


@app.post("/calculate/jst-ratio")
def calculate_jst_ratio(request: CalculateRequest) -> dict[str, Any]:
    return _run(request, outputs={"jst_ratio"})


@app.post("/calculate/results-summary")
def calculate_results_summary(request: CalculateRequest) -> list[dict[str, Any]]:
    return _run(request, outputs={"results_summary_by_id"})["results_summary"]


@app.post("/calculate/final-value-calculations")
def calculate_final_value_calculations(request: CalculateRequest) -> list[dict[str, Any]]:
    return _run(request, outputs={"final_value_calculations_ts"})["final_value_calculations"]


@app.post("/calculate/net-energy-savings")
def calculate_net_energy_savings(request: CalculateRequest) -> list[dict[str, Any]]:
    return _run(request, outputs={"final_savings_calculations_ts"})["net_energy_savings"]
