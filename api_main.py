"""
London Schools API
FastAPI backend serving school data with filtering, search, and scoring.
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
from typing import Optional, List
from pathlib import Path

app = FastAPI(
    title="London Schools API",
    description="Explore and rank London schools using Ofsted data, IMD, and composite scoring.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data at startup
DATA_PATH = Path(__file__).parent.parent / "data" / "schools.json"

def load_schools():
    with open(DATA_PATH) as f:
        return json.load(f)

SCHOOLS = load_schools()


# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "schools_loaded": len(SCHOOLS)}


@app.get("/schools")
def list_schools(
    q: Optional[str] = Query(None, description="Search school name"),
    phase: Optional[str] = Query(None, description="Primary, Secondary, Special, etc."),
    local_authority: Optional[str] = Query(None),
    score_band: Optional[str] = Query(None, description="Outstanding, Good, Requires improvement, Inadequate"),
    min_score: Optional[float] = Query(None),
    has_sixth_form: Optional[bool] = Query(None),
    sort_by: str = Query("ofsted_score", description="Field to sort by"),
    sort_dir: str = Query("desc", description="asc or desc"),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
):
    results = SCHOOLS[:]

    if q:
        q_lower = q.lower()
        results = [s for s in results if q_lower in s["name"].lower()]

    if phase:
        results = [s for s in results if s.get("phase", "").lower() == phase.lower()]

    if local_authority:
        results = [s for s in results if s.get("local_authority", "").lower() == local_authority.lower()]

    if score_band:
        results = [s for s in results if s.get("score_band", "").lower() == score_band.lower()]

    if min_score is not None:
        results = [s for s in results if s.get("ofsted_score") is not None and s["ofsted_score"] >= min_score]

    if has_sixth_form is not None:
        target = "Has a sixth form"
        results = [
            s for s in results
            if (s.get("sixth_form") == target) == has_sixth_form
        ]

    # Sort
    reverse = sort_dir == "desc"
    results.sort(
        key=lambda s: (s.get(sort_by) is None, s.get(sort_by) or 0),
        reverse=reverse
    )

    total = len(results)
    paginated = results[offset: offset + limit]

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "schools": paginated,
    }


@app.get("/schools/{urn}")
def get_school(urn: int):
    school = next((s for s in SCHOOLS if s["urn"] == urn), None)
    if not school:
        return JSONResponse(status_code=404, content={"error": "School not found"})
    return school


@app.get("/filters")
def get_filter_options():
    phases = sorted({s["phase"] for s in SCHOOLS if s.get("phase")})
    local_authorities = sorted({s["local_authority"] for s in SCHOOLS if s.get("local_authority")})
    score_bands = ["Outstanding", "Good", "Requires improvement", "Inadequate", "Unknown"]
    return {
        "phases": phases,
        "local_authorities": local_authorities,
        "score_bands": score_bands,
    }


@app.get("/stats")
def get_stats():
    rated = [s for s in SCHOOLS if s.get("ofsted_score") is not None]
    by_band = {}
    for s in SCHOOLS:
        band = s.get("score_band", "Unknown")
        by_band[band] = by_band.get(band, 0) + 1

    by_phase = {}
    for s in SCHOOLS:
        phase = s.get("phase", "Unknown")
        by_phase[phase] = by_phase.get(phase, 0) + 1

    by_la = {}
    for s in SCHOOLS:
        la = s.get("local_authority", "Unknown")
        by_la[la] = by_la.get(la, 0) + 1

    avg_score = sum(s["ofsted_score"] for s in rated) / len(rated) if rated else 0

    return {
        "total_schools": len(SCHOOLS),
        "rated_schools": len(rated),
        "average_score": round(avg_score, 1),
        "by_band": by_band,
        "by_phase": by_phase,
        "by_local_authority": by_la,
    }
