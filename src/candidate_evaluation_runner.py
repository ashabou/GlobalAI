#!/usr/bin/env python3
"""
Candidate Evaluation Runner
Reads precomputed job requirements and evaluates candidates.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

# Ensure sibling modules are importable when running as a script
sys.path.insert(0, str(Path(__file__).parent))

from job_requirements_analyzer import (
    load_job_analysis,
    display_results,
    get_project_root,
)
from candidate_evaluator import (
    get_candidate_ids,
    convert_weights_to_requirements,
    evaluate_all_candidates,
    rank_candidates_by_affinity,
    print_ranking,
)


def run_candidate_evaluation(
    job_file: str = "data/job_requirements.json",
    candidate_ids: Optional[List[int]] = None,
    output_dir: str = "data",
    show_details: bool = True,
    project_root: Optional[Path] = None,
) -> dict:
    """Load job requirements, evaluate candidates, and return a summary."""
    if project_root is None:
        project_root = get_project_root()

    job_path = Path(job_file)
    if not job_path.is_absolute():
        job_path = project_root / job_path

    if not job_path.exists():
        raise FileNotFoundError(
            f"Job requirements file not found: {job_path}\n"
            "Run job_requirements_analyzer first to generate it."
        )

    print("=" * 80)
    print("CANDIDATE EVALUATION")
    print("=" * 80)
    print(f"Loading job requirements from: {job_path}")

    try:
        rel_job_path = job_path.relative_to(project_root)
        load_path = str(rel_job_path)
    except ValueError:
        load_path = str(job_path)

    job_analysis = load_job_analysis(load_path, project_root=project_root)
    print("✓ Job requirements loaded\n")
    display_results(job_analysis)

    weights = job_analysis.get("weights_dict")
    if not weights:
        raise ValueError("No weights found in job requirements file")

    requirements = convert_weights_to_requirements(weights)

    if candidate_ids is None:
        candidate_ids = get_candidate_ids()

    if not candidate_ids:
        raise ValueError("No candidates found in the data directory!")

    print("\n" + "=" * 80)
    print("STEP 1: Evaluating candidates")
    print("=" * 80)
    output_dir_path = project_root / output_dir
    output_dir_path.mkdir(parents=True, exist_ok=True)
    output_file = output_dir_path / "candidate_evaluations.json"

    # Evaluate and persist results
    try:
        output_rel = output_file.relative_to(project_root)
        output_rel_str = str(output_rel)
    except ValueError:
        output_rel_str = str(output_file)

    evaluations = evaluate_all_candidates(
        candidate_ids=candidate_ids,
        requirements=requirements,
        output_file=output_rel_str,
        project_root=project_root,
    )

    print("\n" + "=" * 80)
    print("STEP 2: Ranking candidates by affinity score")
    print("=" * 80)
    ranked_candidates = rank_candidates_by_affinity(
        profiles_file=output_rel_str,
        project_root=project_root,
    )
    print_ranking(ranked_candidates, show_details=show_details)

    return {
        "job_requirements": job_analysis,
        "requirements": requirements,
        "candidate_ids": candidate_ids,
        "total_evaluated": len(evaluations),
        "ranked_candidates": ranked_candidates,
        "top_candidate": ranked_candidates[0] if ranked_candidates else None,
        "output_file": str(output_file),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate candidates using precomputed job requirements."
    )
    parser.add_argument(
        "--job-file",
        default="data/job_requirements.json",
        help="Path to the job requirements JSON file (default: data/job_requirements.json)",
    )
    parser.add_argument(
        "--candidates",
        type=int,
        nargs="+",
        help="Specific candidate IDs to evaluate (defaults to all discovered candidates)",
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Directory to store evaluation outputs (default: data)",
    )
    parser.add_argument(
        "--hide-details",
        action="store_true",
        help="Hide detailed feature scores in ranking output",
    )

    args = parser.parse_args()

    try:
        result = run_candidate_evaluation(
            job_file=args.job_file,
            candidate_ids=args.candidates,
            output_dir=args.output_dir,
            show_details=not args.hide_details,
        )

        print("=" * 80)
        print("CANDIDATE EVALUATION COMPLETE")
        print("=" * 80)
        if result["top_candidate"]:
            top = result["top_candidate"]
            print(
                f"Top Candidate: #{top['candidate_id']} "
                f"(Affinity Score: {top['affinity_score']:.4f})"
            )
        print(f"Results saved to: {result['output_file']}")
        print("=" * 80)

    except Exception as exc:
        print(f"\n❌ Error: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)




if __name__ == "__main__":
    main()

