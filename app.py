#!/usr/bin/env python3
"""Unified FastAPI application for job analysis and candidate evaluation."""

from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.job_requirements_analyzer import (
    analyze_job_from_url,
    get_project_root,
)
from src.candidate_evaluation_runner import run_candidate_evaluation

app = FastAPI(title="GlobalAI Recruitment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeJobRequest(BaseModel):
    url: str = Field(..., description="Job posting URL")
    company: str = Field(..., description="Company name")
    n: int = Field(5, description="Number of features to extract")
    output_file: Optional[str] = Field(
        None,
        description="Optional path (relative to project root) where the result should be saved",
    )


@app.post("/analyze_job")
def analyze_job(request: AnalyzeJobRequest) -> dict:
    project_root = get_project_root()
    output_path: Optional[str]
    if request.output_file:
        path = Path(request.output_file)
        if not path.is_absolute():
            path = project_root / path
        output_path = str(path)
    else:
        output_path = None

    try:
        result = analyze_job_from_url(
            url=request.url,
            company=request.company,
            n=request.n,
            output_file=output_path,
            project_root=project_root,
        )
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail=f"Feature extraction failed: {exc}"
        ) from exc


class CandidateEvaluationRequest(BaseModel):
    job_file: str = Field(
        "data/job_requirements.json",
        description="Path to job requirements JSON (relative to project root)",
    )
    candidate_ids: Optional[List[int]] = Field(
        None, description="Specific candidate IDs to evaluate"
    )
    output_dir: str = Field(
        "data",
        description="Directory (relative to project root) where results are saved",
    )
    show_details: bool = Field(
        True, description="Include per-feature detail in console output"
    )


@app.get("/evaluate_candidates")
def evaluate_candidates(
) -> dict:
    project_root = get_project_root()
    print(project_root)
    try:
        result = run_candidate_evaluation(
            project_root=project_root,
        )
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500, detail=f"Candidate evaluation failed: {exc}"
        ) from exc
