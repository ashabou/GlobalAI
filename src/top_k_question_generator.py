"""
Top-K Candidate Question Generator Module

This module generates targeted interview questions for top-ranked candidates
based on their evaluation scores, identified gaps, and job requirements.

The module is designed to be FastAPI-ready with Pydantic models for easy
API endpoint integration.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
import vertexai
from vertexai.generative_models import GenerativeModel


# ============================================================================
# PYDANTIC MODELS (FastAPI-ready)
# ============================================================================

class Question(BaseModel):
    """Base model for interview questions"""
    question_text: str = Field(..., description="The actual question to ask")
    question_type: Literal["gap_probing", "depth_validation", "behavioral", "technical", "role_specific"] = Field(
        ..., description="Type of question"
    )
    target_skill: str = Field(..., description="The skill/feature this question targets")
    difficulty_level: Literal["easy", "medium", "hard"] = Field(
        ..., description="Difficulty level of the question"
    )
    rationale: str = Field(..., description="Why this question is being asked for this candidate")
    expected_signals: List[str] = Field(
        ..., description="What the interviewer should listen for in the answer"
    )


class CandidateQuestions(BaseModel):
    """Questions generated for a specific candidate"""
    candidate_id: int
    candidate_affinity_score: float
    gap_probing_questions: List[Question] = Field(
        default_factory=list,
        description="Questions to probe areas where candidate scored low"
    )
    depth_validation_questions: List[Question] = Field(
        default_factory=list,
        description="Questions to validate areas where candidate scored high"
    )
    behavioral_questions: List[Question] = Field(
        default_factory=list,
        description="Behavioral questions based on role requirements"
    )
    technical_questions: List[Question] = Field(
        default_factory=list,
        description="Technical questions specific to job requirements"
    )
    role_specific_questions: List[Question] = Field(
        default_factory=list,
        description="Questions specific to the role and company"
    )
    total_questions: int = Field(0, description="Total number of questions generated")


class InterviewGuide(BaseModel):
    """Complete interview guide for top-K candidates"""
    job_title: str
    company: str
    top_k: int
    candidates: List[CandidateQuestions]
    common_questions: List[Question] = Field(
        default_factory=list,
        description="Questions applicable to all top candidates"
    )
    generated_at: str


# ============================================================================
# VERTEX AI CLIENT INITIALIZATION
# ============================================================================

def initialize_vertex_ai(
    project_id: str = "globalai-446020",
    location: str = "us-central1"
) -> GenerativeModel:
    """Initialize Vertex AI client"""
    vertexai.init(project=project_id, location=location)
    return GenerativeModel("gemini-2.0-flash-exp")


# ============================================================================
# QUESTION GENERATION FUNCTIONS
# ============================================================================

def generate_gap_probing_questions(
    candidate_id: int,
    low_scoring_features: List[Dict],
    job_requirements: Dict,
    model: GenerativeModel,
    num_questions: int = 3
) -> List[Question]:
    """
    Generate questions to probe areas where the candidate scored low.
    These questions help validate whether low scores represent true gaps
    or insufficient evidence in the application.
    """
    if not low_scoring_features:
        return []

    features_text = "\n".join([
        f"- {f['name']}: Score {f['score']:.2f} (Weight: {f['weight']:.2f})"
        for f in low_scoring_features
    ])

    prompt = f"""You are an expert interviewer designing questions for a job candidate.

Job Role: {job_requirements.get('company', 'Company')} - Position related to {job_requirements.get('job_description', '')[:200]}

The candidate (ID: {candidate_id}) scored LOW on these important features:
{features_text}

Generate {num_questions} targeted interview questions that:
1. Probe whether these low scores represent true skill gaps or just lack of evidence in their application
2. Give the candidate a chance to demonstrate competency they may not have shown in their CV/profile
3. Are specific, behavioral, and use the STAR method where appropriate
4. Are fair and not leading

For each question, provide:
- The question text (clear and specific)
- The target skill being evaluated
- Difficulty level (easy/medium/hard)
- Rationale for asking this question
- Expected signals (what a good answer would demonstrate)

Return ONLY a valid JSON array of objects with this structure:
[
  {{
    "question_text": "string",
    "target_skill": "string",
    "difficulty_level": "easy|medium|hard",
    "rationale": "string",
    "expected_signals": ["signal1", "signal2", "signal3"]
  }}
]"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }
    )

    try:
        questions_data = json.loads(response.text)
        return [
            Question(
                question_text=q["question_text"],
                question_type="gap_probing",
                target_skill=q["target_skill"],
                difficulty_level=q["difficulty_level"],
                rationale=q["rationale"],
                expected_signals=q["expected_signals"]
            )
            for q in questions_data[:num_questions]
        ]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing gap probing questions for candidate {candidate_id}: {e}")
        return []


def generate_depth_validation_questions(
    candidate_id: int,
    high_scoring_features: List[Dict],
    job_requirements: Dict,
    model: GenerativeModel,
    num_questions: int = 2
) -> List[Question]:
    """
    Generate questions to validate areas where the candidate scored high.
    These questions confirm genuine expertise vs. surface-level knowledge.
    """
    if not high_scoring_features:
        return []

    features_text = "\n".join([
        f"- {f['name']}: Score {f['score']:.2f} (Weight: {f['weight']:.2f})"
        for f in high_scoring_features
    ])

    prompt = f"""You are an expert interviewer designing questions for a job candidate.

Job Role: {job_requirements.get('company', 'Company')} - Position related to {job_requirements.get('job_description', '')[:200]}

The candidate (ID: {candidate_id}) scored HIGH on these features:
{features_text}

Generate {num_questions} in-depth questions that:
1. Validate the depth of their expertise (not just surface-level knowledge)
2. Explore real-world application of these skills
3. Identify how they've handled challenges in these areas
4. Are challenging enough to differentiate true experts from competent practitioners

For each question, provide:
- The question text (clear and specific)
- The target skill being evaluated
- Difficulty level (medium/hard - these should be challenging)
- Rationale for asking this question
- Expected signals (what a strong answer would demonstrate)

Return ONLY a valid JSON array of objects with this structure:
[
  {{
    "question_text": "string",
    "target_skill": "string",
    "difficulty_level": "medium|hard",
    "rationale": "string",
    "expected_signals": ["signal1", "signal2", "signal3"]
  }}
]"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }
    )

    try:
        questions_data = json.loads(response.text)
        return [
            Question(
                question_text=q["question_text"],
                question_type="depth_validation",
                target_skill=q["target_skill"],
                difficulty_level=q["difficulty_level"],
                rationale=q["rationale"],
                expected_signals=q["expected_signals"]
            )
            for q in questions_data[:num_questions]
        ]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing depth validation questions for candidate {candidate_id}: {e}")
        return []


def generate_behavioral_questions(
    candidate_id: int,
    job_requirements: Dict,
    candidate_score: float,
    model: GenerativeModel,
    num_questions: int = 2
) -> List[Question]:
    """
    Generate behavioral questions based on job requirements.
    These assess soft skills, culture fit, and past behavior patterns.
    """
    features = job_requirements.get('features', [])

    prompt = f"""You are an expert interviewer designing behavioral questions for a job candidate.

Job Role: {job_requirements.get('company', 'Company')}
Job Requirements (Key Features): {', '.join(features[:10])}

The candidate (ID: {candidate_id}) has an overall affinity score of {candidate_score:.2f}.

Generate {num_questions} behavioral interview questions that:
1. Assess soft skills like leadership, communication, adaptability, collaboration
2. Use the STAR method (Situation, Task, Action, Result)
3. Are relevant to the specific role and company
4. Help evaluate culture fit and work style
5. Are open-ended and allow the candidate to share meaningful experiences

For each question, provide:
- The question text (clear and specific)
- The target skill being evaluated
- Difficulty level (easy/medium/hard)
- Rationale for asking this question
- Expected signals (what a good answer would demonstrate)

Return ONLY a valid JSON array of objects with this structure:
[
  {{
    "question_text": "string",
    "target_skill": "string",
    "difficulty_level": "easy|medium|hard",
    "rationale": "string",
    "expected_signals": ["signal1", "signal2", "signal3"]
  }}
]"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.4,
            "response_mime_type": "application/json"
        }
    )

    try:
        questions_data = json.loads(response.text)
        return [
            Question(
                question_text=q["question_text"],
                question_type="behavioral",
                target_skill=q["target_skill"],
                difficulty_level=q["difficulty_level"],
                rationale=q["rationale"],
                expected_signals=q["expected_signals"]
            )
            for q in questions_data[:num_questions]
        ]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing behavioral questions for candidate {candidate_id}: {e}")
        return []


def generate_technical_questions(
    candidate_id: int,
    job_requirements: Dict,
    model: GenerativeModel,
    num_questions: int = 2
) -> List[Question]:
    """
    Generate technical questions based on job requirements.
    These assess hard skills and domain-specific knowledge.
    """
    features = job_requirements.get('features', [])
    job_desc = job_requirements.get('job_description', '')

    prompt = f"""You are an expert interviewer designing technical questions for a job candidate.

Job Role: {job_requirements.get('company', 'Company')}
Job Description: {job_desc[:300]}...
Technical Requirements: {', '.join(features[:10])}

Generate {num_questions} technical interview questions that:
1. Assess domain-specific knowledge and hard skills
2. Are practical and job-relevant (not abstract trivia)
3. Allow candidates to demonstrate problem-solving approaches
4. Can reveal depth of understanding through follow-up discussion
5. Are appropriate for the seniority level implied by the role

For each question, provide:
- The question text (clear and specific)
- The target skill being evaluated
- Difficulty level (easy/medium/hard)
- Rationale for asking this question
- Expected signals (what a good answer would demonstrate)

Return ONLY a valid JSON array of objects with this structure:
[
  {{
    "question_text": "string",
    "target_skill": "string",
    "difficulty_level": "easy|medium|hard",
    "rationale": "string",
    "expected_signals": ["signal1", "signal2", "signal3"]
  }}
]"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.3,
            "response_mime_type": "application/json"
        }
    )

    try:
        questions_data = json.loads(response.text)
        return [
            Question(
                question_text=q["question_text"],
                question_type="technical",
                target_skill=q["target_skill"],
                difficulty_level=q["difficulty_level"],
                rationale=q["rationale"],
                expected_signals=q["expected_signals"]
            )
            for q in questions_data[:num_questions]
        ]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing technical questions for candidate {candidate_id}: {e}")
        return []


def generate_role_specific_questions(
    candidate_id: int,
    job_requirements: Dict,
    model: GenerativeModel,
    num_questions: int = 2
) -> List[Question]:
    """
    Generate role-specific questions tailored to the company and position.
    These questions are unique to the specific job opening.
    """
    company = job_requirements.get('company', 'the company')
    job_desc = job_requirements.get('job_description', '')

    prompt = f"""You are an expert interviewer designing role-specific questions for a job candidate.

Company: {company}
Job Description: {job_desc[:400]}...

Generate {num_questions} role-specific questions that:
1. Are unique to this specific company and position
2. Assess understanding of the company's industry, products, or market
3. Explore motivation and genuine interest in this specific role
4. Address challenges or scenarios specific to this position
5. Help determine if the candidate has done their homework about the company

For each question, provide:
- The question text (clear and specific)
- The target skill/attribute being evaluated
- Difficulty level (easy/medium/hard)
- Rationale for asking this question
- Expected signals (what a good answer would demonstrate)

Return ONLY a valid JSON array of objects with this structure:
[
  {{
    "question_text": "string",
    "target_skill": "string",
    "difficulty_level": "easy|medium|hard",
    "rationale": "string",
    "expected_signals": ["signal1", "signal2", "signal3"]
  }}
]"""

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.4,
            "response_mime_type": "application/json"
        }
    )

    try:
        questions_data = json.loads(response.text)
        return [
            Question(
                question_text=q["question_text"],
                question_type="role_specific",
                target_skill=q["target_skill"],
                difficulty_level=q["difficulty_level"],
                rationale=q["rationale"],
                expected_signals=q["expected_signals"]
            )
            for q in questions_data[:num_questions]
        ]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing role-specific questions for candidate {candidate_id}: {e}")
        return []


# ============================================================================
# CANDIDATE ANALYSIS
# ============================================================================

def analyze_candidate_scores(
    candidate_evaluation: Dict,
    low_score_threshold: float = 0.4,
    high_score_threshold: float = 0.7
) -> tuple[List[Dict], List[Dict]]:
    """
    Analyze candidate's feature scores to identify gaps and strengths.

    Returns:
        Tuple of (low_scoring_features, high_scoring_features)
    """
    feature_scores = candidate_evaluation.get('feature_scores', [])

    low_scoring = [
        fs for fs in feature_scores
        if fs['score'] < low_score_threshold and fs['weight'] >= 0.5
    ]

    high_scoring = [
        fs for fs in feature_scores
        if fs['score'] >= high_score_threshold and fs['weight'] >= 0.5
    ]

    # Sort by weight (most important first)
    low_scoring.sort(key=lambda x: x['weight'], reverse=True)
    high_scoring.sort(key=lambda x: x['weight'], reverse=True)

    return low_scoring, high_scoring


# ============================================================================
# MAIN GENERATION FUNCTION
# ============================================================================

def generate_questions_for_top_k_candidates(
    top_k: int = 3,
    evaluations_file: str = "data/candidate_evaluations.json",
    job_requirements_file: str = "data/job_requirements.json",
    output_file: str = "data/interview_questions.json",
    project_id: str = "globalai-446020",
    location: str = "us-central1"
) -> InterviewGuide:
    """
    Generate interview questions for the top-K ranked candidates.

    This is the main function that can be easily wrapped in a FastAPI endpoint.

    Args:
        top_k: Number of top candidates to generate questions for
        evaluations_file: Path to candidate evaluations JSON
        job_requirements_file: Path to job requirements JSON
        output_file: Path to save the interview guide
        project_id: Google Cloud project ID
        location: Google Cloud location

    Returns:
        InterviewGuide object containing all generated questions
    """
    from datetime import datetime

    # Load data
    with open(evaluations_file, 'r') as f:
        evaluations_data = json.load(f)

    with open(job_requirements_file, 'r') as f:
        job_requirements = json.load(f)

    # Extract candidate list from the data structure
    # Handle both list format and dict format
    if isinstance(evaluations_data, list):
        evaluations = evaluations_data
    elif isinstance(evaluations_data, dict) and 'candidates' in evaluations_data:
        # Convert dict to list
        candidates_dict = evaluations_data['candidates']
        evaluations = list(candidates_dict.values()) if isinstance(candidates_dict, dict) else candidates_dict
    else:
        evaluations = evaluations_data

    # Sort candidates by affinity score and get top-K
    sorted_candidates = sorted(
        evaluations,
        key=lambda x: x['affinity_score'],
        reverse=True
    )[:top_k]

    print(f"\n{'='*60}")
    print(f"GENERATING INTERVIEW QUESTIONS FOR TOP {top_k} CANDIDATES")
    print(f"{'='*60}\n")

    # Initialize Vertex AI
    model = initialize_vertex_ai(project_id, location)

    # Generate questions for each candidate
    candidate_questions_list = []

    for idx, candidate_eval in enumerate(sorted_candidates, 1):
        candidate_id = candidate_eval['candidate_id']
        affinity_score = candidate_eval['affinity_score']

        print(f"Candidate {candidate_id} (Rank #{idx}, Score: {affinity_score:.2f})")
        print(f"{'-'*60}")

        # Analyze scores
        low_scoring, high_scoring = analyze_candidate_scores(candidate_eval)

        print(f"  Low-scoring areas: {len(low_scoring)}")
        print(f"  High-scoring areas: {len(high_scoring)}")

        # Generate different types of questions
        gap_questions = generate_gap_probing_questions(
            candidate_id, low_scoring, job_requirements, model, num_questions=3
        )
        print(f"  ✓ Generated {len(gap_questions)} gap-probing questions")

        depth_questions = generate_depth_validation_questions(
            candidate_id, high_scoring, job_requirements, model, num_questions=2
        )
        print(f"  ✓ Generated {len(depth_questions)} depth-validation questions")

        behavioral_questions = generate_behavioral_questions(
            candidate_id, job_requirements, affinity_score, model, num_questions=2
        )
        print(f"  ✓ Generated {len(behavioral_questions)} behavioral questions")

        technical_questions = generate_technical_questions(
            candidate_id, job_requirements, model, num_questions=2
        )
        print(f"  ✓ Generated {len(technical_questions)} technical questions")

        role_questions = generate_role_specific_questions(
            candidate_id, job_requirements, model, num_questions=1
        )
        print(f"  ✓ Generated {len(role_questions)} role-specific questions")

        total = (len(gap_questions) + len(depth_questions) +
                len(behavioral_questions) + len(technical_questions) +
                len(role_questions))

        candidate_questions = CandidateQuestions(
            candidate_id=candidate_id,
            candidate_affinity_score=affinity_score,
            gap_probing_questions=gap_questions,
            depth_validation_questions=depth_questions,
            behavioral_questions=behavioral_questions,
            technical_questions=technical_questions,
            role_specific_questions=role_questions,
            total_questions=total
        )

        candidate_questions_list.append(candidate_questions)
        print(f"  Total questions: {total}\n")

    # Create interview guide
    interview_guide = InterviewGuide(
        job_title=job_requirements.get('job_description', '')[:100],
        company=job_requirements.get('company', 'Company'),
        top_k=top_k,
        candidates=candidate_questions_list,
        common_questions=[],  # Could add common questions for all candidates
        generated_at=datetime.now().isoformat()
    )

    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(interview_guide.model_dump(), f, indent=2)

    print(f"{'='*60}")
    print(f"Interview guide saved to: {output_file}")
    print(f"Total candidates: {len(candidate_questions_list)}")
    print(f"Total questions: {sum(cq.total_questions for cq in candidate_questions_list)}")
    print(f"{'='*60}\n")

    return interview_guide


# ============================================================================
# UTILITY FUNCTIONS (FastAPI-ready)
# ============================================================================

def get_questions_for_candidate(
    candidate_id: int,
    interview_guide_file: str = "data/interview_questions.json"
) -> Optional[CandidateQuestions]:
    """
    Retrieve questions for a specific candidate from the interview guide.
    This function can be directly used in a FastAPI endpoint.
    """
    with open(interview_guide_file, 'r') as f:
        guide_data = json.load(f)

    for candidate_data in guide_data.get('candidates', []):
        if candidate_data['candidate_id'] == candidate_id:
            return CandidateQuestions(**candidate_data)

    return None


def format_questions_as_text(candidate_questions: CandidateQuestions) -> str:
    """
    Format questions as human-readable text for display or export.
    """
    output = []
    output.append(f"\n{'='*70}")
    output.append(f"INTERVIEW QUESTIONS - CANDIDATE {candidate_questions.candidate_id}")
    output.append(f"Affinity Score: {candidate_questions.candidate_affinity_score:.2f}")
    output.append(f"{'='*70}\n")

    sections = [
        ("GAP-PROBING QUESTIONS", candidate_questions.gap_probing_questions),
        ("DEPTH-VALIDATION QUESTIONS", candidate_questions.depth_validation_questions),
        ("BEHAVIORAL QUESTIONS", candidate_questions.behavioral_questions),
        ("TECHNICAL QUESTIONS", candidate_questions.technical_questions),
        ("ROLE-SPECIFIC QUESTIONS", candidate_questions.role_specific_questions)
    ]

    for section_title, questions in sections:
        if questions:
            output.append(f"\n{section_title}")
            output.append("-" * 70)
            for i, q in enumerate(questions, 1):
                output.append(f"\n{i}. {q.question_text}")
                output.append(f"   Target Skill: {q.target_skill}")
                output.append(f"   Difficulty: {q.difficulty_level.upper()}")
                output.append(f"   Rationale: {q.rationale}")
                output.append(f"   Expected Signals:")
                for signal in q.expected_signals:
                    output.append(f"     • {signal}")
            output.append("")

    return "\n".join(output)


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate interview questions for top-K candidates"
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=3,
        help="Number of top candidates to generate questions for (default: 3)"
    )
    parser.add_argument(
        "--evaluations",
        type=str,
        default="data/candidate_evaluations.json",
        help="Path to candidate evaluations JSON file"
    )
    parser.add_argument(
        "--job-requirements",
        type=str,
        default="data/job_requirements.json",
        help="Path to job requirements JSON file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/interview_questions.json",
        help="Output file path for interview guide"
    )
    parser.add_argument(
        "--candidate-id",
        type=int,
        help="Display questions for a specific candidate (requires existing interview guide)"
    )

    args = parser.parse_args()

    if args.candidate_id:
        # Display questions for specific candidate
        candidate_questions = get_questions_for_candidate(args.candidate_id, args.output)
        if candidate_questions:
            print(format_questions_as_text(candidate_questions))
        else:
            print(f"No questions found for candidate {args.candidate_id}")
    else:
        # Generate questions for top-K candidates
        interview_guide = generate_questions_for_top_k_candidates(
            top_k=args.top_k,
            evaluations_file=args.evaluations,
            job_requirements_file=args.job_requirements,
            output_file=args.output
        )
