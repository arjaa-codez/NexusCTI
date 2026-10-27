"""
FastAPI Server for NexusCTI.
Exposes REST endpoints for SOC incident attribution, graph visualization,
and benchmark analytics.
"""

from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from pydantic import BaseModel
from pathlib import Path

from ..service import get_service
from ..eval.benchmark_cases import get_benchmark_dataset
from ..fusion.report_generator import AttributionReportGenerator
from ..config import WEB_DIR

app = FastAPI(
    title="NexusCTI: Hybrid Multi-Modal Threat Attribution Engine",
    description="Structural GNN relational reasoning + Contextual text-grounded RAG",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IncidentAnalysisRequest(BaseModel):
    query: str
    ioc_override: Optional[str] = None


@app.get("/api/health")
def health_check():
    return {"status": "online", "engine": "NexusCTI v1.0", "gnn": "HeteroThreatGNN", "rag": "Dense-Sparse-RRF"}


@app.post("/api/analyze")
def analyze_incident(req: IncidentAnalysisRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    service = get_service()
    result = service.analyze(req.query, ioc_override=req.ioc_override)

    # Generate reports
    md_report = AttributionReportGenerator.generate_markdown_report(result)
    json_report = AttributionReportGenerator.generate_json_report(result)

    return {
        "analysis": json_report,
        "markdown_report": md_report
    }


@app.get("/api/graph")
def get_knowledge_graph():
    service = get_service()
    return service.get_graph_data()


@app.get("/api/cases")
def get_cases():
    cases = get_benchmark_dataset()
    return [case.dict() for case in cases]


@app.get("/api/benchmark")
def run_benchmark():
    service = get_service()
    return service.run_benchmark()


# Mount Web UI static directory
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def serve_index():
        index_file = WEB_DIR / "index.html"
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>NexusCTI Web UI Loading...</h1>"
