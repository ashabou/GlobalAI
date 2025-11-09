#!/usr/bin/env python3
"""
Candidate Ranking Module
Evaluates candidates against job requirements and ranks them by affinity score.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

# Add parent directory to path to allow imports
import sys
sys.path.insert(0, str(Path(__file__).parent))

from candidate_profile_evaluator import evaluate_candidate, CandidateEvaluation, FeatureScore


def ensure_evaluation_model(evaluation) -> CandidateEvaluation:
    """
    Ensure evaluation is a CandidateEvaluation Pydantic model.
    Converts dict to model if necessary.
    
    Args:
        evaluation: Either a CandidateEvaluation model or a dict
        
    Returns:
        CandidateEvaluation Pydantic model
        
    Raises:
        TypeError: If evaluation is not a dict or CandidateEvaluation
        ValueError: If dict cannot be converted to CandidateEvaluation
    """
    if isinstance(evaluation, CandidateEvaluation):
        return evaluation
    elif isinstance(evaluation, dict):
        # Convert dict to Pydantic model
        # Pydantic will automatically convert nested dicts to FeatureScore objects
        try:
            return CandidateEvaluation(**evaluation)
        except Exception as e:
            # Provide more helpful error message
            raise ValueError(
                f"Failed to convert dict to CandidateEvaluation: {e}\n"
                f"Dict keys: {list(evaluation.keys())}\n"
                f"Dict content: {evaluation}"
            ) from e
    else:
        raise TypeError(
            f"Expected CandidateEvaluation or dict, got {type(evaluation)}: {evaluation}"
        )


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_candidate_ids(project_root: Path, data_dir: Optional[Path] = None) -> List[int]:
    """
    Discover candidate IDs from the data directory.
    
    Args:
        data_dir: Optional path to data directory (defaults to project_root/data)
        
    Returns:
        List of candidate IDs found
    """
    if data_dir is None:
        data_dir = project_root / "data"
    
    candidate_ids = []
    
    if not data_dir.exists():
        return candidate_ids
    
    for item in data_dir.iterdir():
        if item.is_dir() and item.name.startswith("candidate_"):
            try:
                candidate_id = int(item.name.split("_")[1])
                candidate_ids.append(candidate_id)
            except (ValueError, IndexError):
                continue
    
    return sorted(candidate_ids)


def convert_weights_to_requirements(weights: Dict[str, float]) -> dict:
    """
    Convert job_requirements_analyzer weight format to requirements format for candidate_profile_evaluator.
    
    Args:
        weights: Dictionary mapping feature names to weights (from job_requirements_analyzer)
        
    Returns:
        Requirements dictionary in format expected by candidate_profile_evaluator
    """
    features = [
        {"name": feature_name, "weight": weight}
        for feature_name, weight in weights.items()
    ]
    return {"features": features}


def evaluate_all_candidates(
    candidate_ids: List[int],
    requirements: dict,
    output_file: str = "data/candidate_evaluations.json",
    project_root: Path = None
) -> Dict[int, CandidateEvaluation]:
    """
    Evaluate all candidates and save their profiles to a JSON file.
    
    Args:
        candidate_ids: List of candidate IDs to evaluate
        requirements: Dictionary containing requirements with features and weights
        output_file: Path to the output JSON file (relative to project root)
        project_root: Optional project root path (defaults to auto-detected)
        
    Returns:
        Dictionary mapping candidate IDs to their evaluations
    """
    if project_root is None:
        project_root = get_project_root()
    output_path = project_root / output_file
    
    all_profiles = {}
    
    print(f"Evaluating {len(candidate_ids)} candidates...")
    
    for candidate_id in candidate_ids:
        print(f"\n{'='*60}")
        print(f"Evaluating Candidate {candidate_id}...")
        print(f"{'='*60}")
        
        try:
            # Check what documents are available for this candidate
            candidate_dir = project_root / "data" / f"candidate_{candidate_id}"
            
            if candidate_dir.exists():
                # List available documents
                available_files = [f.name for f in candidate_dir.iterdir() if f.is_file()]
                if available_files:
                    print(f"   Documents found: {', '.join(available_files)}")
                else:
                    print(f"   ⚠ No documents found in candidate directory")
            
            evaluation = evaluate_candidate(candidate_id, requirements)
            # Ensure evaluation is a Pydantic model (defensive programming)
            evaluation = ensure_evaluation_model(evaluation)
            all_profiles[candidate_id] = evaluation
            
            print(f"✅ Candidate {candidate_id} evaluated successfully")
            print(f"   Affinity Score: {evaluation.affinity_score:.4f}")
            print(f"   Feature Scores:")
            for feature in evaluation.feature_scores:
                print(f"     - {feature.name}: {feature.score:.4f} (weight: {feature.weight:.2f})")
                
        except Exception as e:
            print(f"❌ Error evaluating candidate {candidate_id}: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            continue
    
    # Convert to serializable format (evaluation is a Pydantic model)
    profiles_data = {
        "metadata": {
            "evaluation_date": datetime.now().isoformat(),
            "total_candidates": len(all_profiles),
            "requirements": requirements
        },
        "candidates": {}
    }
    
    for candidate_id, evaluation in all_profiles.items():
        # Ensure evaluation is a Pydantic model (defensive programming)
        evaluation = ensure_evaluation_model(evaluation)
        
        # evaluation is a CandidateEvaluation Pydantic model
        profiles_data["candidates"][str(candidate_id)] = {
            "candidate_id": candidate_id,
            "feature_scores": [
                {
                    "name": feature.name,
                    "weight": feature.weight,
                    "score": feature.score
                }
                for feature in evaluation.feature_scores
            ],
            "affinity_score": evaluation.affinity_score
        }
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to file
    with open(output_path, "w") as f:
        json.dump(profiles_data, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ All profiles saved to {output_path}")
    print(f"{'='*60}")
    
    return all_profiles


def rank_candidates_by_affinity(
    profiles_file: str = "data/candidate_evaluations.json",
    project_root: Path = None
) -> List[Dict]:
    """
    Read candidate profiles from a JSON file and rank them by affinity score.
    
    Args:
        profiles_file: Path to the JSON file containing candidate profiles (relative to project root)
        project_root: Optional project root path (defaults to auto-detected)
        
    Returns:
        List of candidate profiles sorted by affinity score (descending)
    """
    if project_root is None:
        project_root = get_project_root()
    profiles_path = project_root / profiles_file
    
    if not profiles_path.exists():
        raise FileNotFoundError(
            f"Profiles file not found: {profiles_path}\n"
            f"Please run evaluate_all_candidates() first to generate the profiles file."
        )
    
    with open(profiles_path, "r") as f:
        profiles_data = json.load(f)
    
    # Extract candidates and sort by affinity score
    candidates = list(profiles_data["candidates"].values())
    ranked_candidates = sorted(
        candidates,
        key=lambda x: x["affinity_score"],
        reverse=True
    )
    
    return ranked_candidates


def print_ranking(ranked_candidates: List[Dict], show_details: bool = False):
    """
    Print the candidate ranking in a formatted way.
    
    Args:
        ranked_candidates: List of ranked candidate profiles
        show_details: If True, show detailed feature scores for each candidate
    """
    print(f"\n{'='*80}")
    print(f"CANDIDATE RANKING BY AFFINITY SCORE")
    print(f"{'='*80}\n")
    
    for rank, candidate in enumerate(ranked_candidates, 1):
        candidate_id = candidate["candidate_id"]
        affinity_score = candidate["affinity_score"]
        
        print(f"Rank {rank}: Candidate {candidate_id}")
        print(f"  Affinity Score: {affinity_score:.4f}")
        
        if show_details:
            print(f"  Feature Scores:")
            for feature in candidate["feature_scores"]:
                print(f"    - {feature['name']}: {feature['score']:.4f} "
                      f"(weight: {feature['weight']:.2f})")
        print()
    
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Example usage with manual requirements
    requirements = {
        "features": [
            {"name": "Machine Learning", "weight": 0.4},
            {"name": "Python programming", "weight": 0.3},
            {"name": "Communication skills", "weight": 0.2},
            {"name": "Leadership", "weight": 0.1}
        ]
    }
    
    from candidate_profile_evaluator import get_project_root as _get_root

    project_root = _get_root()

    candidate_ids = get_candidate_ids(project_root)
    
    if not candidate_ids:
        print("❌ No candidates found in the data directory!")
        sys.exit(1)
    
    print(f"Found {len(candidate_ids)} candidates: {candidate_ids}")
    
    # Evaluate all candidates
    print("\n" + "="*80)
    print("STEP 1: Evaluating all candidates")
    print("="*80)
    all_profiles = evaluate_all_candidates(candidate_ids, requirements, project_root=project_root)
    
    # Rank candidates by affinity score
    print("\n" + "="*80)
    print("STEP 2: Ranking candidates by affinity score")
    print("="*80)
    ranked_candidates = rank_candidates_by_affinity(project_root=project_root)
    
    # Print the ranking
    print_ranking(ranked_candidates, show_details=True)
