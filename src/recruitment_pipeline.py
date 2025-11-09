#!/usr/bin/env python3
"""
Main Pipeline: Job Analysis → Candidate Ranking
Complete pipeline that analyzes a job posting and ranks candidates by affinity score.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from job_requirements_analyzer import (
    analyze_job_from_url,
    analyze_job,
    save_job_analysis,
    load_job_analysis,
    display_results,
    get_project_root
)
from candidate_evaluator import (
    get_candidate_ids,
    convert_weights_to_requirements,
    evaluate_all_candidates,
    rank_candidates_by_affinity,
    print_ranking
)


def run_full_pipeline(
    job_url: Optional[str] = None,
    job_description: Optional[str] = None,
    job_analysis_file: Optional[str] = None,
    company_name: Optional[str] = None,
    candidate_ids: Optional[list] = None,
    output_dir: str = "data"
) -> dict:
    """
    Run the complete pipeline: job analysis → candidate evaluation → ranking.
    
    Args:
        job_url: URL of job posting to analyze
        job_description: Direct job description text (alternative to URL)
        job_analysis_file: Path to existing job analysis file (skip analysis step)
        company_name: Optional company name for culture analysis
        candidate_ids: List of candidate IDs to evaluate (defaults to auto-discover)
        output_dir: Directory for output files (relative to project root)
        
    Returns:
        Dictionary containing pipeline results
    """
    project_root = get_project_root()
    output_path = project_root / output_dir
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("CANDIDATE RANKING PIPELINE")
    print("=" * 80)
    print()
    
    # Step 1: Job Analysis
    print("STEP 1: Job Analysis")
    print("-" * 80)
    
    if job_analysis_file:
        # Load existing job analysis
        print(f"Loading job analysis from: {job_analysis_file}")
        job_analysis = load_job_analysis(job_analysis_file)
        print("✓ Job analysis loaded")
    elif job_url:
        # Analyze from URL
        print(f"Analyzing job posting from URL: {job_url}")
        if company_name:
            print(f"Company: {company_name}")
        job_analysis = analyze_job_from_url(job_url, company_name=company_name)
        job_analysis_path = save_job_analysis(job_analysis, 
                                             output_file=f"{output_dir}/job_requirements.json")
        print(f"✓ Job analysis saved to: {job_analysis_path}")
    elif job_description:
        # Analyze from text
        print("Analyzing job description from text")
        if company_name:
            print(f"Company: {company_name}")
        job_analysis = analyze_job(job_description, company_name=company_name)
        job_analysis["url"] = "text_input"
        job_analysis_path = save_job_analysis(job_analysis,
                                             output_file=f"{output_dir}/job_requirements.json")
        print(f"✓ Job analysis saved to: {job_analysis_path}")
    else:
        raise ValueError(
            "Must provide one of: job_url, job_description, or job_analysis_file"
        )
    
    print()
    display_results(job_analysis)
    print()
    
    # Step 2: Convert weights to requirements format
    print("STEP 2: Preparing Candidate Evaluation Requirements")
    print("-" * 80)
    weights = job_analysis["weights"]
    requirements = convert_weights_to_requirements(weights)
    print(f"✓ Converted {len(weights)} feature weights to requirements format")
    print()
    
    # Step 3: Get candidate IDs
    print("STEP 3: Discovering Candidates")
    print("-" * 80)
    if candidate_ids is None:
        candidate_ids = get_candidate_ids()
    
    if not candidate_ids:
        raise ValueError("No candidates found in the data directory!")
    
    print(f"✓ Found {len(candidate_ids)} candidates: {candidate_ids}")
    print()
    
    # Step 4: Evaluate all candidates
    print("STEP 4: Evaluating Candidates")
    print("-" * 80)
    profiles_file = f"{output_dir}/candidate_evaluations.json"
    all_profiles = evaluate_all_candidates(
        candidate_ids=candidate_ids,
        requirements=requirements,
        output_file=profiles_file
    )
    print()
    
    # Step 5: Rank candidates
    print("STEP 5: Ranking Candidates by Affinity Score")
    print("-" * 80)
    ranked_candidates = rank_candidates_by_affinity(profiles_file=profiles_file)
    print_ranking(ranked_candidates, show_details=True)
    
    # Return summary
    return {
        "job_analysis": job_analysis,
        "requirements": requirements,
        "candidate_ids": candidate_ids,
        "total_evaluated": len(all_profiles),
        "ranked_candidates": ranked_candidates,
        "top_candidate": ranked_candidates[0] if ranked_candidates else None
    }


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Candidate Ranking Pipeline: Analyze job and rank candidates"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="URL of job posting to analyze"
    )
    parser.add_argument(
        "--job-file",
        type=str,
        help="Path to existing job analysis JSON file (skip analysis step)"
    )
    parser.add_argument(
        "--company",
        type=str,
        help="Company name for culture analysis"
    )
    parser.add_argument(
        "--candidates",
        type=int,
        nargs="+",
        help="Specific candidate IDs to evaluate (defaults to all found)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data",
        help="Output directory for results (default: data)"
    )
    
    args = parser.parse_args()
    
    try:
        result = run_full_pipeline(
            job_url=args.url,
            job_analysis_file=args.job_file,
            company_name=args.company,
            candidate_ids=args.candidates,
            output_dir=args.output_dir
        )
        
        print("=" * 80)
        print("PIPELINE COMPLETE")
        print("=" * 80)
        if result["top_candidate"]:
            print(f"Top Candidate: #{result['top_candidate']['candidate_id']} "
                  f"(Affinity Score: {result['top_candidate']['affinity_score']:.4f})")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

