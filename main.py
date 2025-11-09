#!/usr/bin/env python3
"""Run job analysis, candidate evaluation, and feedback generation."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from job_requirements_analyzer import analyze_job_from_url, get_project_root
from candidate_evaluation_runner import run_candidate_evaluation
from candidate_feedback_generator import generate_feedback_for_rejected_candidates


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run job analysis, candidate ranking, and feedback generation"
    )
    parser.add_argument("job_url", help="URL of the job posting to analyze")
    parser.add_argument(
        "--company",
        required=True,
        help="Company name associated with the job posting",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=5,
        help="Number of technical/behavioral features to extract (default: 5)",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory where outputs (requirements, evaluations, feedback) are stored",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=1,
        help="Number of top-ranked candidates to exclude from feedback",
    )
    parser.add_argument(
        "--candidates",
        type=int,
        nargs="+",
        help="Specific candidate IDs to evaluate (defaults to all discovered)",
    )
    parser.add_argument(
        "--hide-details",
        action="store_true",
        help="Hide detailed feature scores when printing rankings",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    project_root = get_project_root()

    output_dir = (project_root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    job_requirements_path = output_dir / "job_requirements.json"
    candidate_evaluations_path = output_dir / "candidate_evaluations.json"
    feedback_summary_path = output_dir / "candidate_feedback.json"
    feedback_dir = output_dir / "feedback"

    print("=" * 80)
    print("AGENT A: Job Requirements Analysis")
    print("=" * 80)
    job_result = analyze_job_from_url(
        url=args.job_url,
        company=args.company,
        n=args.n,
        output_file=str(job_requirements_path.relative_to(project_root)),
        project_root=project_root,
    )
    saved_requirements = job_result.get("saved_path")
    if saved_requirements:
        job_requirements_path = Path(saved_requirements)
        if not job_requirements_path.is_absolute():
            job_requirements_path = project_root / job_requirements_path

    print("\n" + "=" * 80)
    print("AGENT B: Candidate Evaluation")
    print("=" * 80)
    evaluation_result = run_candidate_evaluation(
        job_file=str(job_requirements_path.relative_to(project_root)),
        candidate_ids=args.candidates,
        output_dir=str(output_dir.relative_to(project_root)),
        show_details=not args.hide_details,
        project_root=project_root,
    )

    print("\n" + "=" * 80)
    print("AGENT C: Feedback Generation")
    print("=" * 80)
    eval_file = Path(evaluation_result["output_file"])
    if not eval_file.is_absolute():
        eval_file = project_root / eval_file
    candidate_evaluations_path = eval_file

    generate_feedback_for_rejected_candidates(
        top_n=args.top_n,
        evaluations_file=eval_file,
        requirements_file=job_requirements_path,
        output_summary_file=feedback_summary_path,
        feedback_dir=feedback_dir,
        project_root=project_root,
    )

    print("\nWorkflow complete.")
    print(f"Job requirements saved to: {job_requirements_path}")
    print(f"Candidate evaluations saved to: {candidate_evaluations_path}")
    print(f"Feedback summary saved to: {feedback_summary_path}")
    print(f"Individual feedback stored in: {feedback_dir}")


if __name__ == "__main__":
    main()
