#!/usr/bin/env python3
"""Run job analysis, candidate evaluation, and single-candidate feedback generation."""

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
from candidate_feedback_generator import generate_feedback_for_candidate


def _as_relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run job analysis, candidate ranking, and single-candidate feedback generation"
    )
    parser.add_argument("job_url", help="URL of the job posting to analyze")
    parser.add_argument(
        "--company",
        required=True,
        help="Company name associated with the job posting",
    )
    parser.add_argument(
        "--candidate-id",
        type=int,
        required=True,
        help="Candidate ID to generate feedback for",
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
        output_file=_as_relative(job_requirements_path, project_root),
        project_root=project_root,
    )
    saved_requirements = job_result.get("saved_path")
    if saved_requirements:
        job_requirements_path = Path(saved_requirements)
        if not job_requirements_path.is_absolute():
            job_requirements_path = (project_root / job_requirements_path).resolve()

    print("\n" + "=" * 80)
    print("AGENT B: Candidate Evaluation")
    print("=" * 80)
    evaluation_result = run_candidate_evaluation(
        job_file=_as_relative(job_requirements_path, project_root),
        candidate_ids=args.candidates,
        output_dir=_as_relative(output_dir, project_root),
        show_details=not args.hide_details,
        project_root=project_root,
    )

    eval_file = Path(evaluation_result["output_file"])
    if not eval_file.is_absolute():
        eval_file = (project_root / eval_file).resolve()
    candidate_evaluations_path = eval_file

    print("\n" + "=" * 80)
    print("AGENT C: Feedback Generation")
    print("=" * 80)
    feedback = generate_feedback_for_candidate(
        candidate_id=args.candidate_id,
        evaluations_file=candidate_evaluations_path,
        requirements_file=job_requirements_path,
        output_file=feedback_summary_path,
        feedback_dir=feedback_dir,
        project_root=project_root,
    )

    individual_feedback_path = feedback_dir / f"candidate_{args.candidate_id}_feedback.json"

    print("\nWorkflow complete.")
    print(f"Job requirements saved to: {job_requirements_path}")
    print(f"Candidate evaluations saved to: {candidate_evaluations_path}")
    print(f"Feedback summary saved to: {feedback_summary_path}")
    print(f"Individual feedback saved to: {individual_feedback_path}")


if __name__ == "__main__":
    main()
