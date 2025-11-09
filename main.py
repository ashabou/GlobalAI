#!/usr/bin/env python3
"""Unified CLI for job analysis and candidate evaluation."""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

# Ensure src/ modules are importable when running from repo root
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from job_requirements_analyzer import (
    analyze_job_from_url,
    load_job_analysis,
    display_results,
    get_project_root,
)
from candidate_evaluation_runner import run_candidate_evaluation


def run_job_analysis(
    job_url: str,
    company: str,
    n: int,
    output_file: str,
    project_root: Path,
) -> dict:
    """Run job analysis from URL and persist results."""
    result = analyze_job_from_url(
        url=job_url,
        company=company,
        n=n,
        output_file=output_file,
        project_root=project_root,
    )
    display_results(result)
    saved_path = result.get("saved_path", output_file)
    print(f"Job requirements saved to: {saved_path}")
    return result


def ensure_job_file(job_file: str, project_root: Path) -> Path:
    job_path = Path(job_file)
    if not job_path.is_absolute():
        job_path = project_root / job_path
    if not job_path.exists():
        raise FileNotFoundError(
            f"Job requirements file not found: {job_path}\n"
            "Use --job-url/--company to generate it first."
        )
    return job_path


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="End-to-end recruitment workflow")
    job_source = parser.add_mutually_exclusive_group()
    job_source.add_argument("--job-url", help="URL of the job posting to analyze")
    parser.add_argument("--company", help="Company name (required with --job-url)")
    parser.add_argument(
        "--n",
        type=int,
        default=5,
        help="Number of technical/behavioral features to extract (default: 5)",
    )
    parser.add_argument(
        "--job-file",
        default="data/job_requirements.json",
        help="Path to job requirements JSON (default: data/job_requirements.json)",
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
        help="Directory to store candidate evaluation outputs (default: data)",
    )
    parser.add_argument(
        "--hide-details",
        action="store_true",
        help="Hide detailed feature scores in ranking output",
    )
    parser.add_argument(
        "--skip-evaluation",
        action="store_true",
        help="Only run job analysis, skip candidate evaluation",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)
    project_root = get_project_root()

    job_file = args.job_file
    if args.job_url:
        if not args.company:
            raise ValueError("--company is required when --job-url is provided")
        run_job_analysis(
            job_url=args.job_url,
            company=args.company,
            n=args.n,
            output_file=job_file,
            project_root=project_root,
        )
    else:
        # If not generating, ensure file exists before continuing
        ensure_job_file(job_file, project_root)

    if args.skip_evaluation:
        print("Candidate evaluation skipped by request.")
        return

    run_candidate_evaluation(
        job_file=job_file,
        candidate_ids=args.candidates,
        output_dir=args.output_dir,
        show_details=not args.hide_details,
        project_root=project_root,
    )


if __name__ == "__main__":
    main()
