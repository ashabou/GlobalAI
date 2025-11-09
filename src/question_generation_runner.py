#!/usr/bin/env python3
"""
Question Generation Runner
Generates targeted interview questions for top-K candidates.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Ensure sibling modules are importable when running as a script
sys.path.insert(0, str(Path(__file__).parent))

from job_requirements_analyzer import get_project_root
from top_k_question_generator import (
    generate_questions_for_top_k_candidates,
    get_questions_for_candidate,
    format_questions_as_text,
)


def run_question_generation(
    top_k: int = 3,
    evaluations_file: str = "data/candidate_evaluations.json",
    job_requirements_file: str = "data/job_requirements.json",
    output_file: str = "data/interview_questions.json",
    project_root: Optional[Path] = None,
    display_candidate_id: Optional[int] = None,
) -> dict:
    """
    Generate interview questions for top-K candidates.

    Args:
        top_k: Number of top candidates to generate questions for
        evaluations_file: Path to candidate evaluations JSON
        job_requirements_file: Path to job requirements JSON
        output_file: Output path for interview questions
        project_root: Project root directory
        display_candidate_id: If provided, display questions for this candidate

    Returns:
        Dictionary with generation results
    """
    if project_root is None:
        project_root = get_project_root()

    # Handle display mode (showing existing questions for a candidate)
    if display_candidate_id is not None:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = project_root / output_path

        if not output_path.exists():
            raise FileNotFoundError(
                f"Interview questions file not found: {output_path}\n"
                "Run question generation first to create it."
            )

        try:
            rel_output_path = output_path.relative_to(project_root)
            load_path = str(rel_output_path)
        except ValueError:
            load_path = str(output_path)

        candidate_questions = get_questions_for_candidate(
            display_candidate_id,
            load_path
        )

        if candidate_questions:
            print(format_questions_as_text(candidate_questions))
            return {
                "mode": "display",
                "candidate_id": display_candidate_id,
                "total_questions": candidate_questions.total_questions,
            }
        else:
            raise ValueError(f"No questions found for candidate {display_candidate_id}")

    # Handle generation mode
    evaluations_path = Path(evaluations_file)
    if not evaluations_path.is_absolute():
        evaluations_path = project_root / evaluations_path

    job_reqs_path = Path(job_requirements_file)
    if not job_reqs_path.is_absolute():
        job_reqs_path = project_root / job_reqs_path

    output_path = Path(output_file)
    if not output_path.is_absolute():
        output_path = project_root / output_file

    # Verify input files exist
    if not evaluations_path.exists():
        raise FileNotFoundError(
            f"Candidate evaluations file not found: {evaluations_path}\n"
            "Run candidate evaluation first to generate it."
        )

    if not job_reqs_path.exists():
        raise FileNotFoundError(
            f"Job requirements file not found: {job_reqs_path}\n"
            "Run job requirements analysis first to generate it."
        )

    # Convert to relative paths for the module
    try:
        rel_eval_path = evaluations_path.relative_to(project_root)
        rel_job_path = job_reqs_path.relative_to(project_root)
        rel_output_path = output_path.relative_to(project_root)
    except ValueError:
        rel_eval_path = evaluations_path
        rel_job_path = job_reqs_path
        rel_output_path = output_path

    # Generate questions
    interview_guide = generate_questions_for_top_k_candidates(
        top_k=top_k,
        evaluations_file=str(rel_eval_path),
        job_requirements_file=str(rel_job_path),
        output_file=str(rel_output_path),
    )

    total_questions = sum(c.total_questions for c in interview_guide.candidates)

    return {
        "mode": "generate",
        "top_k": top_k,
        "total_candidates": len(interview_guide.candidates),
        "total_questions": total_questions,
        "output_file": str(output_path),
        "interview_guide": interview_guide,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Generate targeted interview questions for top-K candidates."
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top candidates to generate questions for (default: 3)",
    )
    parser.add_argument(
        "--evaluations",
        default="data/candidate_evaluations.json",
        help="Path to candidate evaluations JSON file (default: data/candidate_evaluations.json)",
    )
    parser.add_argument(
        "--job-requirements",
        default="data/job_requirements.json",
        help="Path to job requirements JSON file (default: data/job_requirements.json)",
    )
    parser.add_argument(
        "--output",
        default="data/interview_questions.json",
        help="Output file path for interview guide (default: data/interview_questions.json)",
    )
    parser.add_argument(
        "--display-candidate",
        type=int,
        metavar="ID",
        help="Display questions for a specific candidate (requires existing interview guide)",
    )

    args = parser.parse_args()

    try:
        result = run_question_generation(
            top_k=args.top_k,
            evaluations_file=args.evaluations,
            job_requirements_file=args.job_requirements,
            output_file=args.output,
            display_candidate_id=args.display_candidate,
        )

        if result["mode"] == "generate":
            print("\n" + "=" * 80)
            print("QUESTION GENERATION COMPLETE")
            print("=" * 80)
            print(f"Top-K Candidates: {result['top_k']}")
            print(f"Total Questions Generated: {result['total_questions']}")
            print(f"Results saved to: {result['output_file']}")
            print("=" * 80)
            print("\nTip: Use --display-candidate <ID> to view questions for a specific candidate")
            print("=" * 80)

    except Exception as exc:
        print(f"\n❌ Error: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
