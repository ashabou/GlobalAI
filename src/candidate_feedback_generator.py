#!/usr/bin/env python3
"""
Candidate Feedback Generator Module
Generates personalized, actionable feedback for rejected candidates.
Focuses on technical skills, strengths, and improvement areas.
"""

import argparse
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

# Google GenAI imports
from google import genai
from google.genai import types

# Import existing modules for data access
from candidate_profile_evaluator import (
    scan_candidate_documents,
    format_candidate_information
)

# -------------------------------
# 1️⃣ Pydantic models for structured feedback
# -------------------------------

class TechnicalStrength(BaseModel):
    skill_area: str = Field(description="The technical skill or competency area")
    evidence: str = Field(description="Specific evidence from the candidate's profile demonstrating this strength")
    proficiency_level: str = Field(description="Assessed proficiency level: Foundational, Intermediate, Advanced, or Expert")

class ImprovementArea(BaseModel):
    dimension: str = Field(description="The evaluation dimension or skill area needing improvement")
    current_gap: str = Field(description="Specific gap identified between candidate's profile and industry/role requirements")
    importance_context: str = Field(description="Why this area is important for the target role and industry")
    actionable_recommendations: List[str] = Field(description="3-5 specific, actionable steps to improve in this area")
    estimated_timeline: str = Field(description="Realistic timeline for meaningful improvement: Short-term (1-3 months), Medium-term (3-6 months), or Long-term (6-12+ months)")

class ProfileSummary(BaseModel):
    overall_assessment: str = Field(description="Brief 2-3 sentence summary of the candidate's profile strengths")
    standout_qualities: List[str] = Field(description="2-3 key qualities or achievements that distinguish this candidate")
    career_stage_assessment: str = Field(description="Assessment of candidate's current career stage and readiness level")

class CandidateFeedback(BaseModel):
    candidate_id: int = Field(description="The candidate's ID")
    profile_summary: ProfileSummary = Field(description="High-level profile assessment")
    technical_strengths: List[TechnicalStrength] = Field(description="Top 3-5 technical strengths identified")
    improvement_areas: List[ImprovementArea] = Field(description="Top 3-4 areas for improvement, prioritized by impact")
    industry_alignment_score: float = Field(description="Score from 0.0 to 1.0 indicating overall industry readiness")
    next_steps_summary: str = Field(description="Concise summary of recommended next steps for career development")

# -------------------------------
# 2️⃣ Load environment and initialize client
# -------------------------------

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


# -------------------------------
# 3️⃣ Core feedback generation function
# -------------------------------

def generate_candidate_feedback(
    candidate_id: int,
    evaluation_data: dict,
    job_requirements: dict,
    project_root: Path = None
) -> CandidateFeedback:
    """
    Generate comprehensive, actionable feedback for a rejected candidate.

    This function analyzes the candidate's complete profile, their evaluation scores,
    and the job requirements to generate personalized feedback focused on:
    - Technical strengths with evidence
    - Areas for improvement with actionable recommendations
    - Industry alignment and career development guidance

    Args:
        candidate_id: The candidate's ID
        evaluation_data: Dictionary containing the candidate's evaluation results
        job_requirements: Dictionary containing job requirements, technical skills, and weights
        project_root: Optional project root path (defaults to auto-detected)

    Returns:
        CandidateFeedback object with structured feedback

    Raises:
        ValueError: If candidate documents or evaluation data is missing
    """
    if project_root is None:
        project_root = get_project_root()

    candidate_dir = project_root / "data" / f"candidate_{candidate_id}"

    # Load candidate documents
    documents = scan_candidate_documents(candidate_dir)

    if not documents['all_content']:
        raise ValueError(
            f"No documents found for candidate {candidate_id}. "
            f"Cannot generate feedback without candidate profile data."
        )

    # Format candidate information
    candidate_profile = format_candidate_information(documents)

    # Extract relevant data from evaluation
    feature_scores = evaluation_data.get('feature_scores', [])
    affinity_score = evaluation_data.get('affinity_score', 0.0)

    # Extract job context
    tech_skills = job_requirements.get('tech_skills', [])
    company_name = job_requirements.get('company_name', 'the target company')
    company_culture = job_requirements.get('company_culture', '')
    job_description = job_requirements.get('job_description', '')
    feature_weights_raw = (
        job_requirements.get('weights_dict')
        or job_requirements.get('weights')
        or {}
    )

    if isinstance(feature_weights_raw, dict):
        feature_weights = feature_weights_raw
    elif isinstance(feature_weights_raw, list):
        features_meta = job_requirements.get('features', [])
        if features_meta and len(features_meta) == len(feature_weights_raw):
            if isinstance(features_meta[0], dict) and 'name' in features_meta[0]:
                feature_names = [f['name'] for f in features_meta]
            else:
                feature_names = features_meta
            feature_weights = {
                name: weight for name, weight in zip(feature_names, feature_weights_raw)
            }
        else:
            feature_weights = {}
    else:
        feature_weights = {}

    # Identify high-importance features (weight >= 0.8)
    critical_features = [
        {"name": name, "weight": weight}
        for name, weight in feature_weights.items()
        if weight >= 0.8
    ]

    # Identify underperforming features (score < 0.7) in high-weight areas
    weak_areas = [
        fs for fs in feature_scores
        if fs['score'] < 0.7 and fs['weight'] >= 0.6
    ]

    # Build context sections for the prompt
    tech_skills_context = f"Technical Skills Required: {', '.join(tech_skills[:15])}" if tech_skills else ""

    culture_context = f"\n\nCompany Culture Context:\n{company_culture}" if company_culture else ""

    critical_features_text = "\n".join([
        f"- {f['name']} (weight: {f['weight']:.1f})"
        for f in critical_features
    ])

    scores_summary = "\n".join([
        f"- {fs['name']}: {fs['score']:.2f} (weight: {fs['weight']:.1f})"
        for fs in feature_scores
    ])

    weak_areas_text = "\n".join([
        f"- {wa['name']}: {wa['score']:.2f} (weight: {wa['weight']:.1f})"
        for wa in weak_areas
    ]) if weak_areas else "No significant weak areas identified"

    # -------------------------------
    # 4️⃣ Expert-level feedback prompt
    # -------------------------------

    prompt = f"""You are a senior technical talent consultant and hiring systems expert with 15+ years of experience in candidate assessment and career development coaching. Your expertise includes:
- Analyzing technical competencies across diverse industries and roles
- Identifying skill gaps and creating actionable development roadmaps
- Providing evidence-based, objective feedback focused on professional growth
- Understanding industry standards and competitive benchmarks for technical roles

Your task is to generate comprehensive, constructive feedback for a candidate who was not selected for a position. This feedback should be:
- **Objective and evidence-based**: Grounded in specific observations from their profile
- **Actionable and practical**: Include concrete steps they can take to improve
- **Technical-focused**: Emphasize technical skills, competencies, and professional capabilities
- **Industry-aligned**: Reference current industry standards and market expectations
- **Developmentally constructive**: Frame areas for improvement as growth opportunities
- **NO psychological or personality-based feedback**: Focus strictly on skills, experience, and professional competencies

---

**CANDIDATE PROFILE DATA:**

{candidate_profile}

---

**EVALUATION RESULTS:**

Overall Affinity Score: {affinity_score:.2f} / 1.0

Feature Scores:
{scores_summary}

---

**JOB CONTEXT:**

Company: {company_name}
{tech_skills_context}
{culture_context}

Critical Success Factors for This Role:
{critical_features_text}

---

**IDENTIFIED GAPS:**

Areas Scoring Below Competitive Threshold:
{weak_areas_text}

---

**YOUR FEEDBACK GENERATION INSTRUCTIONS:**

1. **Profile Summary:**
   - Provide an honest, balanced 2-3 sentence assessment of the candidate's overall profile
   - Highlight 2-3 standout qualities or achievements that distinguish them
   - Assess their career stage and current readiness level for roles like this

2. **Technical Strengths (identify 3-5):**
   For each strength:
   - Specify the technical skill or competency area
   - Provide specific evidence from their CV, LinkedIn, or other documents
   - Assess their proficiency level: Foundational, Intermediate, Advanced, or Expert
   - Focus on concrete skills (technologies, methodologies, domain knowledge)

3. **Improvement Areas (identify 3-4, prioritized by impact):**
   For each area:
   - Name the specific dimension or skill area needing development
   - Explain the current gap between their profile and industry/role requirements
   - Clarify why this area is important for their target industry/roles
   - Provide 3-5 **specific, actionable recommendations** such as:
     * Specific courses, certifications, or training programs to pursue
     * Projects or experiences to seek out (with examples)
     * Technical communities, publications, or resources to engage with
     * Measurable milestones to demonstrate progress
     * Networking or mentorship opportunities to explore
   - Provide a realistic timeline: Short-term (1-3 months), Medium-term (3-6 months), or Long-term (6-12+ months)

   **Prioritization criteria:**
   - Weight the importance based on the feature weights (higher weight = higher priority)
   - Consider the candidate's current score vs. requirement (bigger gaps = higher priority)
   - Focus on high-impact skills that significantly affect competitiveness

4. **Industry Alignment Score (0.0 to 1.0):**
   - Assess overall industry readiness considering current market standards
   - Factor in: technical skill currency, experience relevance, professional development trajectory
   - Be realistic: 0.6-0.7 = needs development, 0.7-0.8 = competitive with growth areas, 0.8-0.9 = strong candidate, 0.9+ = exceptional

5. **Next Steps Summary:**
   - Provide a concise 2-3 sentence summary of the most important next steps
   - Prioritize the top 2-3 actions that will have the highest impact on their competitiveness
   - Frame positively around growth and market positioning

---

**IMPORTANT GUIDELINES:**

✅ DO:
- Base all feedback on observable evidence from their documents
- Use industry-standard terminology and frameworks
- Provide specific, actionable recommendations with examples
- Consider the specific requirements of the role and company when identifying gaps
- Acknowledge genuine strengths with specific evidence
- Frame development areas constructively as growth opportunities
- Reference current market trends and industry expectations

❌ DO NOT:
- Make assumptions about personality, psychology, or character
- Provide vague advice like "work on communication" without actionable specifics
- Focus on soft skills without technical grounding
- Use discouraging or demotivating language
- Suggest improvements in areas not relevant to technical/professional development
- Reference psychological traits, emotional intelligence, or personality frameworks

---

Generate the feedback now, returning ONLY valid JSON matching the CandidateFeedback schema structure.
"""

    # -------------------------------
    # 5️⃣ Call LLM with structured output
    # -------------------------------

    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=CandidateFeedback.model_json_schema(),
        temperature=0.2  # Slightly higher than evaluation for more nuanced feedback
    )

    model_name = "gemini-2.5-flash"

    response = client.models.generate_content(
        model=model_name,
        contents=[prompt],
        config=config,
    )

    # Parse response
    try:
        parsed_response = response.parsed

        if isinstance(parsed_response, dict):
            result = CandidateFeedback(**parsed_response)
        elif isinstance(parsed_response, CandidateFeedback):
            result = parsed_response
        else:
            # Fallback parsing
            json_text = response.text.strip()
            if json_text.startswith('```json'):
                json_text = json_text.split('```json')[1].split('```')[0].strip()
            elif json_text.startswith('```'):
                json_text = json_text.split('```')[1].split('```')[0].strip()

            parsed_dict = json.loads(json_text)
            result = CandidateFeedback(**parsed_dict)

    except Exception as e:
        print(f"Error parsing LLM output: {e}")
        print(f"Response type: {type(response.parsed)}")
        print(f"Raw response text: {response.text}")
        raise

    return result


# -------------------------------
# 6️⃣ Feedback generation helpers
# -------------------------------


def generate_feedback_for_candidate(
    candidate_id: int,
    evaluations_file: Path = None,
    requirements_file: Path = None,
    output_file: Path = None,
    project_root: Path = None,
    feedback_dir: Path = None,
) -> CandidateFeedback:
    """Generate feedback for a single candidate."""
    if project_root is None:
        project_root = get_project_root()

    if evaluations_file is None:
        evaluations_file = project_root / "data" / "candidate_evaluations.json"
    if requirements_file is None:
        requirements_file = project_root / "data" / "job_requirements.json"

    if feedback_dir is None:
        feedback_dir = project_root / "data" / "feedback"
    feedback_dir.mkdir(parents=True, exist_ok=True)
    individual_file = feedback_dir / f"candidate_{candidate_id}_feedback.json"

    if output_file is None:
        output_file = project_root / "data" / "candidate_feedback.json"

    with open(evaluations_file, "r") as f:
        evaluations_data = json.load(f)

    with open(requirements_file, "r") as f:
        job_requirements = json.load(f)

    candidate_key = str(candidate_id)
    candidate_eval = evaluations_data.get("candidates", {}).get(candidate_key)
    if not candidate_eval:
        raise ValueError(f"Candidate {candidate_id} not found in evaluation file")

    print("=" * 80)
    print(f"Generating feedback for candidate {candidate_id}")
    print("=" * 80)

    feedback = generate_candidate_feedback(
        candidate_id=candidate_id,
        evaluation_data=candidate_eval,
        job_requirements=job_requirements,
        project_root=project_root,
    )

    # Load existing feedback file if present
    if output_file.exists():
        with open(output_file, "r") as f:
            feedback_data = json.load(f)
    else:
        feedback_data = {
            "metadata": {
                "generation_date": datetime.now().isoformat(),
                "total_candidates": len(evaluations_data.get("candidates", {})),
                "feedback_generated_for": 0,
                "job_role": job_requirements.get("company_name", "Unknown"),
            },
            "feedback": {},
        }

    feedback_data["feedback"][candidate_key] = feedback.model_dump()
    feedback_data["metadata"]["feedback_generated_for"] = len(feedback_data["feedback"])
    feedback_data["metadata"]["generation_date"] = datetime.now().isoformat()

    with open(output_file, "w") as f:
        json.dump(feedback_data, f, indent=2)

    with open(individual_file, "w") as f:
        json.dump(feedback.model_dump(), f, indent=2)

    print(f"Feedback saved to {individual_file}")
    return feedback


# -------------------------------
# 7️⃣ Utility function to format feedback as human-readable text
# -------------------------------

def format_feedback_as_text(feedback: CandidateFeedback, candidate_id: int = None) -> str:
    """
    Format CandidateFeedback object as human-readable text for email or display.

    Args:
        feedback: CandidateFeedback object
        candidate_id: Optional candidate ID to include in the header

    Returns:
        Formatted text string
    """
    header = f"CANDIDATE FEEDBACK REPORT"
    if candidate_id:
        header += f" - Candidate #{candidate_id}"

    lines = [
        "=" * 80,
        header,
        "=" * 80,
        "",
        "PROFILE SUMMARY",
        "-" * 80,
        feedback.profile_summary.overall_assessment,
        "",
        "Standout Qualities:",
        *[f"  • {quality}" for quality in feedback.profile_summary.standout_qualities],
        "",
        f"Career Stage: {feedback.profile_summary.career_stage_assessment}",
        f"Industry Alignment Score: {feedback.industry_alignment_score:.2f} / 1.0",
        "",
        "",
        "YOUR TECHNICAL STRENGTHS",
        "-" * 80,
    ]

    for i, strength in enumerate(feedback.technical_strengths, 1):
        lines.extend([
            f"{i}. {strength.skill_area} ({strength.proficiency_level})",
            f"   Evidence: {strength.evidence}",
            ""
        ])

    lines.extend([
        "",
        "AREAS FOR IMPROVEMENT",
        "-" * 80,
    ])

    for i, area in enumerate(feedback.improvement_areas, 1):
        lines.extend([
            f"{i}. {area.dimension}",
            f"   Current Gap: {area.current_gap}",
            f"   Why It Matters: {area.importance_context}",
            f"   Timeline: {area.estimated_timeline}",
            "",
            "   Actionable Recommendations:",
            *[f"      • {rec}" for rec in area.actionable_recommendations],
            ""
        ])

    lines.extend([
        "",
        "RECOMMENDED NEXT STEPS",
        "-" * 80,
        feedback.next_steps_summary,
        "",
        "=" * 80,
        ""
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate feedback for a single candidate")
    parser.add_argument("candidate_id", type=int, help="Candidate ID")
    parser.add_argument("--evaluations-file", default=None)
    parser.add_argument("--requirements-file", default=None)
    parser.add_argument("--output-summary", default=None)
    parser.add_argument("--feedback-dir", default=None)

    args = parser.parse_args()

    feedback = generate_feedback_for_candidate(
        candidate_id=args.candidate_id,
        evaluations_file=Path(args.evaluations_file) if args.evaluations_file else None,
        requirements_file=Path(args.requirements_file) if args.requirements_file else None,
        output_file=Path(args.output_summary) if args.output_summary else None,
        feedback_dir=Path(args.feedback_dir) if args.feedback_dir else None,
    )

    print("\n" + "=" * 80)
    print("FORMATTED FEEDBACK REPORT")
    print("=" * 80 + "\n")
    print(format_feedback_as_text(feedback, args.candidate_id))
