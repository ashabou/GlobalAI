# Interview Question Generation Module

## Overview

The Interview Question Generation module (`top_k_question_generator.py`) generates targeted interview questions for top-ranked candidates based on their evaluation scores, identified gaps, and job requirements. This module helps hiring teams conduct more effective interviews by focusing on areas of ambiguity or strength in each candidate's application.

## Features

- **Gap-Probing Questions**: Questions targeting areas where candidates scored low to validate whether these represent true skill gaps or insufficient evidence
- **Depth-Validation Questions**: Questions to confirm genuine expertise in areas where candidates scored high
- **Behavioral Questions**: STAR-method questions assessing soft skills, culture fit, and past behavior patterns
- **Technical Questions**: Domain-specific questions evaluating hard skills and technical knowledge
- **Role-Specific Questions**: Questions unique to the company and position

## Design Philosophy

### FastAPI-Ready Architecture

The module is designed with FastAPI integration in mind:

1. **Pydantic Models**: All data structures use Pydantic `BaseModel` for automatic validation and serialization
2. **Separation of Concerns**: Business logic is separated from the API layer for easy endpoint wrapping
3. **Type Safety**: Full type hints throughout the codebase
4. **JSON Schema**: Structured outputs compatible with OpenAPI specification
5. **Reusable Functions**: Core functions can be directly used in FastAPI route handlers

### Example FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from top_k_question_generator import (
    generate_questions_for_top_k_candidates,
    get_questions_for_candidate,
    CandidateQuestions,
    InterviewGuide
)

app = FastAPI()

@app.post("/api/v1/generate-questions", response_model=InterviewGuide)
async def generate_interview_questions(
    top_k: int = 3,
    evaluations_file: str = "data/candidate_evaluations.json",
    job_requirements_file: str = "data/job_requirements.json"
):
    """Generate interview questions for top-K candidates"""
    try:
        interview_guide = generate_questions_for_top_k_candidates(
            top_k=top_k,
            evaluations_file=evaluations_file,
            job_requirements_file=job_requirements_file
        )
        return interview_guide
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/questions/{candidate_id}", response_model=CandidateQuestions)
async def get_candidate_questions(candidate_id: int):
    """Retrieve questions for a specific candidate"""
    questions = get_questions_for_candidate(candidate_id)
    if not questions:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return questions
```

## Data Models

### Question

Individual interview question with metadata:

```python
class Question(BaseModel):
    question_text: str                    # The actual question
    question_type: Literal[...]           # Type of question
    target_skill: str                     # Skill being evaluated
    difficulty_level: Literal[...]        # easy/medium/hard
    rationale: str                        # Why this question is asked
    expected_signals: List[str]           # What to listen for
```

### CandidateQuestions

All questions for a specific candidate:

```python
class CandidateQuestions(BaseModel):
    candidate_id: int
    candidate_affinity_score: float
    gap_probing_questions: List[Question]
    depth_validation_questions: List[Question]
    behavioral_questions: List[Question]
    technical_questions: List[Question]
    role_specific_questions: List[Question]
    total_questions: int
```

### InterviewGuide

Complete interview guide for all top-K candidates:

```python
class InterviewGuide(BaseModel):
    job_title: str
    company: str
    top_k: int
    candidates: List[CandidateQuestions]
    common_questions: List[Question]
    generated_at: str
```

## Usage

### 1. Standalone Script

```bash
# Generate questions for top 3 candidates
python src/top_k_question_generator.py --top-k 3

# Generate questions for top 5 candidates with custom paths
python src/top_k_question_generator.py \
    --top-k 5 \
    --evaluations data/candidate_evaluations.json \
    --job-requirements data/job_requirements.json \
    --output data/interview_questions.json

# Display questions for a specific candidate
python src/top_k_question_generator.py --candidate-id 5
```

### 2. Via Runner Script

```bash
# Generate questions for top 3 candidates
python src/question_generation_runner.py --top-k 3

# Display questions for candidate #5
python src/question_generation_runner.py --display-candidate 5
```

### 3. Via Main Pipeline

```bash
# Run full pipeline including question generation
python main.py <job_url> --company "Lululemon" --top-k 3

# Run full pipeline but skip question generation
python main.py <job_url> --company "Lululemon" --skip-questions
```

### 4. Programmatic Usage

```python
from top_k_question_generator import generate_questions_for_top_k_candidates

# Generate questions
interview_guide = generate_questions_for_top_k_candidates(
    top_k=3,
    evaluations_file="data/candidate_evaluations.json",
    job_requirements_file="data/job_requirements.json",
    output_file="data/interview_questions.json"
)

# Access results
for candidate in interview_guide.candidates:
    print(f"Candidate {candidate.candidate_id}")
    print(f"Total questions: {candidate.total_questions}")

    for question in candidate.gap_probing_questions:
        print(f"  - {question.question_text}")
```

## Question Generation Strategy

### 1. Gap-Probing Questions (3 per candidate)

**Purpose**: Validate low scores - are they true gaps or just lack of evidence?

**Strategy**:
- Focus on features where score < 0.4 AND weight >= 0.5
- Prioritize high-weight features first
- Give candidates a chance to demonstrate hidden competencies
- Use behavioral/STAR format to probe real experiences

**Example**:
```
Feature: "Product Knowledge (Lululemon)" - Score 0.0, Weight 1.0

Question: "While your profile doesn't explicitly mention Lululemon products,
can you describe a time when you had to quickly learn about a new product line
or brand in order to effectively sell or promote it? What was your approach,
and what were the results?"
```

### 2. Depth-Validation Questions (2 per candidate)

**Purpose**: Confirm high scores represent genuine expertise, not surface knowledge

**Strategy**:
- Focus on features where score >= 0.7 AND weight >= 0.5
- Ask challenging, nuanced questions
- Explore real-world application and problem-solving
- Differentiate experts from competent practitioners

**Example**:
```
Feature: "Leadership" - Score 0.9, Weight 0.9

Question: "You've demonstrated strong leadership in your profile. Describe
a situation where you had to lead a team through a significant change or
challenge. How did you handle resistance, and what would you do differently
in retrospect?"
```

### 3. Behavioral Questions (2 per candidate)

**Purpose**: Assess soft skills, culture fit, and work style

**Strategy**:
- Based on job features (Leadership, Collaboration, Communication, etc.)
- Use STAR method (Situation, Task, Action, Result)
- Open-ended to allow meaningful storytelling
- Relevant to specific role and company context

### 4. Technical Questions (2 per candidate)

**Purpose**: Evaluate domain-specific knowledge and hard skills

**Strategy**:
- Based on job requirements and technical features
- Practical and job-relevant (not abstract trivia)
- Appropriate for role seniority level
- Allow for follow-up discussion

### 5. Role-Specific Questions (1-2 per candidate)

**Purpose**: Assess company knowledge, motivation, and role fit

**Strategy**:
- Unique to the specific company and position
- Test understanding of industry/products/market
- Gauge genuine interest and preparation
- Explore role-specific challenges

## Output Format

The module generates a JSON file with the following structure:

```json
{
  "job_title": "Assistant Store Manager - Lululemon",
  "company": "Lululemon",
  "top_k": 3,
  "generated_at": "2025-01-09T12:34:56",
  "candidates": [
    {
      "candidate_id": 5,
      "candidate_affinity_score": 0.64,
      "gap_probing_questions": [
        {
          "question_text": "...",
          "question_type": "gap_probing",
          "target_skill": "Product Knowledge (Lululemon)",
          "difficulty_level": "medium",
          "rationale": "...",
          "expected_signals": ["...", "...", "..."]
        }
      ],
      "depth_validation_questions": [...],
      "behavioral_questions": [...],
      "technical_questions": [...],
      "role_specific_questions": [...],
      "total_questions": 10
    }
  ],
  "common_questions": []
}
```

## Integration with Existing Pipeline

The module integrates as **Agent D** in the main pipeline:

```
Agent A: Job Requirements Analysis
    ↓
    Outputs: data/job_requirements.json

Agent B: Candidate Evaluation
    ↓
    Outputs: data/candidate_evaluations.json

Agent C: Feedback Generation (for rejected candidates)
    ↓
    Outputs: data/feedback/*

Agent D: Interview Question Generation (for top-K candidates) ← NEW
    ↓
    Outputs: data/interview_questions.json
```

## Configuration

### Thresholds

Default thresholds can be modified in `analyze_candidate_scores()`:

- **Low Score Threshold**: 0.4 (features scoring below this are considered gaps)
- **High Score Threshold**: 0.7 (features scoring above this are considered strengths)
- **Minimum Weight**: 0.5 (only consider features with weight >= 0.5)

### Question Counts

Default question counts per candidate:

- Gap-Probing: 3 questions
- Depth-Validation: 2 questions
- Behavioral: 2 questions
- Technical: 2 questions
- Role-Specific: 1 question

Total: ~10 questions per candidate

### LLM Settings

- **Model**: Gemini 2.0 Flash (via Vertex AI)
- **Temperature**: 0.3-0.4 (balanced between consistency and creativity)
- **Output Format**: Structured JSON with schema validation

## Error Handling

The module includes robust error handling:

1. **Missing Files**: Clear error messages with suggestions
2. **JSON Parsing Errors**: Graceful fallback with logging
3. **LLM Response Errors**: Catches malformed responses
4. **Validation Errors**: Pydantic models validate all data

## Future Enhancements

### Potential Features

1. **Common Questions**: Generate questions applicable to all top candidates
2. **Follow-up Questions**: AI-generated follow-ups based on expected answers
3. **Question Scoring**: Rubrics for evaluating candidate responses
4. **Interview Scripts**: Complete interview guides with timing and transitions
5. **Multi-language Support**: Generate questions in different languages
6. **Question Bank**: Reusable question templates by role type
7. **Candidate Comparison**: Side-by-side question comparison for multiple candidates

### API Enhancements (Future FastAPI Features)

```python
# Suggested future endpoints:

@app.post("/api/v1/questions/regenerate/{candidate_id}")
async def regenerate_questions_for_candidate(candidate_id: int):
    """Regenerate questions for a specific candidate"""
    pass

@app.get("/api/v1/questions/export/{candidate_id}")
async def export_questions_as_pdf(candidate_id: int):
    """Export questions as PDF interview guide"""
    pass

@app.post("/api/v1/questions/customize")
async def customize_question_generation(
    low_score_threshold: float = 0.4,
    high_score_threshold: float = 0.7,
    num_gap_questions: int = 3
):
    """Generate questions with custom parameters"""
    pass
```

## Dependencies

- **vertexai**: Google Cloud Vertex AI SDK
- **pydantic**: Data validation and serialization
- **pathlib**: Path manipulation
- **json**: JSON parsing and serialization
- **typing**: Type hints

## Testing

### Manual Testing

```bash
# 1. Ensure required files exist
ls data/candidate_evaluations.json
ls data/job_requirements.json

# 2. Generate questions
python src/question_generation_runner.py --top-k 3

# 3. Verify output
cat data/interview_questions.json

# 4. Display questions for a candidate
python src/question_generation_runner.py --display-candidate 5
```

### Unit Testing (Future)

```python
import pytest
from top_k_question_generator import analyze_candidate_scores

def test_analyze_candidate_scores():
    candidate_eval = {
        "candidate_id": 1,
        "feature_scores": [
            {"name": "Leadership", "score": 0.9, "weight": 0.9},
            {"name": "Product Knowledge", "score": 0.0, "weight": 1.0}
        ]
    }

    low, high = analyze_candidate_scores(candidate_eval)

    assert len(low) == 1
    assert len(high) == 1
    assert low[0]["name"] == "Product Knowledge"
    assert high[0]["name"] == "Leadership"
```

## License

This module is part of the GlobalAI candidate evaluation system.

## Support

For issues or questions, please refer to the main project documentation or contact the development team.
