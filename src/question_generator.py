#!/usr/bin/env python3
"""
Question Generator Module
Generates interview questions for a single candidate based on evaluation scores
and job requirements.
"""
import os
import argparse
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
# Google GenAI imports
from google import genai
from google.genai import types


# -----------------------------------------------------------------------------
# Pydantic models
# -----------------------------------------------------------------------------


class Question(BaseModel):
    question_text: str
    question_type: str
    target_skill: str
    difficulty_level: str
    rationale: str
    expected_signals: List[str]


class CandidateQuestionSet(BaseModel):
    candidate_id: int
    candidate_affinity_score: float
    generated_at: str
    questions: List[Question]


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
if not PROJECT_ID:
    raise ValueError("Environment variable GOOGLE_CLOUD_PROJECT is required")

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION,
)

MODEL_NAME = "gemini-2.5-flash"


def build_prompt(
    candidate_id: int,
    affinity_score: float,
    feature_scores: List[Dict],
    job_requirements: Dict,
    max_questions: int,
) -> str:
    features_text = "\n".join(
        f"- {fs['name']}: score {fs['score']:.2f} (weight {fs['weight']:.2f})"
        for fs in feature_scores
    )
    return f"""You are an expert interviewer. Design {max_questions} targeted questions.

Candidate ID: {candidate_id}
Affinity Score: {affinity_score:.2f}
Role Company: {job_requirements.get('company', 'Unknown')}
Role Description (truncated): {job_requirements.get('job_description', '')[:400]}
Key Features:
{features_text}

Produce diverse questions (gap probing, behavioral, technical, role-specific).
Return JSON array of:
{{
  "question_text": "...",
  "question_type": "gap_probing|behavioral|technical|role_specific|depth_validation",
  "target_skill": "...",
  "difficulty_level": "easy|medium|hard",
  "rationale": "...",
  "expected_signals": ["...", "...", "..."]
}}
"""


def extract_feature_scores(evaluation: Dict) -> List[Dict]:
    return evaluation.get("feature_scores", [])


# -----------------------------------------------------------------------------
# Core generation function
# -----------------------------------------------------------------------------


def generate_questions_for_candidate(
    candidate_id: int,
    evaluations_file: str = "data/candidate_evaluations.json",
    job_requirements_file: str = "data/job_requirements.json",
    output_dir: str = "data/questions",
    max_questions: int = 10,
    project_id: str = "globalai-446020",
    location: str = "us-central1",
) -> CandidateQuestionSet:
    evaluations_data = json.loads(Path(evaluations_file).read_text())
    job_requirements = json.loads(Path(job_requirements_file).read_text())

    candidate = evaluations_data.get("candidates", {}).get(str(candidate_id))
    if not candidate:
        raise ValueError(f"Candidate {candidate_id} not found in {evaluations_file}")

    feature_scores = extract_feature_scores(candidate)
    prompt = build_prompt(
        candidate_id=candidate_id,
        affinity_score=candidate.get("affinity_score", 0.0),
        feature_scores=feature_scores,
        job_requirements=job_requirements,
        max_questions=max_questions,
    )

    config = types.GenerateContentConfig(
        temperature=0.3,
        response_mime_type="application/json",
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt],
        config=config,
    )

    try:
        questions_data = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Could not parse model response: {exc}\n{response.text}")

    questions = [Question(**q) for q in questions_data[:max_questions]]

    result = CandidateQuestionSet(
        candidate_id=candidate_id,
        candidate_affinity_score=candidate.get("affinity_score", 0.0),
        generated_at=datetime.utcnow().isoformat(),
        questions=questions,
    )

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path / f"candidate_{candidate_id}_questions.json"
    file_path.write_text(result.model_dump_json(indent=2))

    return result


# -----------------------------------------------------------------------------
# Runner helper (imported from question_generation_runner)
# -----------------------------------------------------------------------------


def run_question_generation(
    candidate_id: int,
    evaluations_file: str = "data/candidate_evaluations.json",
    job_requirements_file: str = "data/job_requirements.json",
    output_dir: str = "data/questions",
    max_questions: int = 10,
    project_root: Optional[Path] = None,
) -> CandidateQuestionSet:
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent

    def resolve(path: str) -> str:
        p = Path(path)
        if not p.is_absolute():
            p = project_root / p
        return str(p)

    return generate_questions_for_candidate(
        candidate_id=candidate_id,
        evaluations_file=resolve(evaluations_file),
        job_requirements_file=resolve(job_requirements_file),
        output_dir=resolve(output_dir),
        max_questions=max_questions,
    )


# -----------------------------------------------------------------------------
# CLI entry point
# -----------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate questions for one candidate")
    parser.add_argument("candidate_id", type=int)
    parser.add_argument("--evaluations", default="data/candidate_evaluations.json")
    parser.add_argument("--job-requirements", default="data/job_requirements.json")
    parser.add_argument("--output-dir", default="data/questions")
    parser.add_argument("--max-questions", type=int, default=10)

    args = parser.parse_args()

    result = run_question_generation(
        candidate_id=args.candidate_id,
        evaluations_file=args.evaluations,
        job_requirements_file=args.job_requirements,
        output_dir=args.output_dir,
        max_questions=args.max_questions,
    )

    display = [
        "=" * 80,
        f"QUESTIONS FOR CANDIDATE {result.candidate_id}",
        f"Affinity Score: {result.candidate_affinity_score:.2f}",
        f"Generated: {result.generated_at}",
        "=" * 80,
    ]
    for idx, q in enumerate(result.questions, 1):
        display.extend(
            [
                f"\n{idx}. {q.question_text}",
                f"   Type: {q.question_type}",
                f"   Skill: {q.target_skill}",
                f"   Difficulty: {q.difficulty_level}",
                f"   Rationale: {q.rationale}",
                "   Expected Signals:",
            ]
        )
        display.extend(f"      • {signal}" for signal in q.expected_signals)

    print("\n".join(display))
