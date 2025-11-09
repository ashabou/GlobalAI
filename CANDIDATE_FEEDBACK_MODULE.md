# Candidate Feedback Generator Module

## Overview

The **Candidate Feedback Generator** is an AI-powered module that provides comprehensive, actionable feedback to rejected candidates in the recruitment pipeline. It analyzes candidate profiles against job requirements and generates personalized, evidence-based feedback focused on technical skills, professional competencies, and career development.

## Key Features

### 🎯 Structured Feedback Components

1. **Profile Summary**
   - Overall assessment of candidate's strengths
   - Standout qualities and achievements
   - Career stage and readiness evaluation

2. **Technical Strengths Analysis**
   - Top 3-5 technical competencies identified
   - Evidence-based assessment from CV, LinkedIn, and other documents
   - Proficiency level classification (Foundational, Intermediate, Advanced, Expert)

3. **Improvement Areas**
   - 3-4 prioritized development areas based on industry requirements
   - Gap analysis: current profile vs. market expectations
   - Context: why each area matters for target roles
   - **Actionable Recommendations**: 3-5 specific steps per area
   - Realistic timelines (Short/Medium/Long-term)

4. **Industry Alignment Score**
   - 0.0-1.0 score indicating overall industry readiness
   - Benchmarked against current market standards

5. **Next Steps Summary**
   - Concise action plan for career development
   - Prioritized recommendations for maximum impact

---

## Architecture

### Technology Stack

- **LLM Provider**: Google Vertex AI (Gemini 2.5 Flash)
- **Structured Output**: Pydantic models with JSON schema validation
- **Document Processing**: Multi-format support (PDF, JSON, Text)
- **Temperature**: 0.2 (balanced determinism and nuance)

### Module Structure

```
src/candidate_feedback_generator.py
├── 1️⃣ Pydantic Models
│   ├── TechnicalStrength
│   ├── ImprovementArea
│   ├── ProfileSummary
│   └── CandidateFeedback
├── 2️⃣ Client Initialization (Vertex AI)
├── 3️⃣ Core Feedback Generation
│   └── generate_candidate_feedback()
├── 4️⃣ Expert-Level Prompt Engineering
├── 5️⃣ Batch Processing
│   └── generate_feedback_for_rejected_candidates()
└── 6️⃣ Formatting Utilities
    └── format_feedback_as_text()
```

---

## Data Models

### TechnicalStrength

```python
{
    "skill_area": str,              # Technical skill or competency
    "evidence": str,                # Specific evidence from profile
    "proficiency_level": str        # Foundational | Intermediate | Advanced | Expert
}
```

### ImprovementArea

```python
{
    "dimension": str,                      # Evaluation dimension or skill area
    "current_gap": str,                    # Gap vs. industry requirements
    "importance_context": str,             # Why it matters for target roles
    "actionable_recommendations": [str],   # 3-5 specific action steps
    "estimated_timeline": str              # Short/Medium/Long-term
}
```

### ProfileSummary

```python
{
    "overall_assessment": str,        # 2-3 sentence profile summary
    "standout_qualities": [str],      # 2-3 distinguishing qualities
    "career_stage_assessment": str    # Current career stage/readiness
}
```

### CandidateFeedback

```python
{
    "candidate_id": int,
    "profile_summary": ProfileSummary,
    "technical_strengths": [TechnicalStrength],
    "improvement_areas": [ImprovementArea],
    "industry_alignment_score": float,     # 0.0 - 1.0
    "next_steps_summary": str
}
```

---

## Prompt Engineering

### Expert Role Definition

The module uses an **expert consultant persona** with 15+ years of experience in:
- Technical competency assessment
- Skill gap identification
- Career development coaching
- Industry benchmarking
- Evidence-based feedback delivery

### Feedback Principles

✅ **DO:**
- Base all feedback on observable evidence
- Use industry-standard terminology
- Provide specific, actionable recommendations
- Consider role and company requirements
- Acknowledge genuine strengths
- Frame development areas as growth opportunities

❌ **DO NOT:**
- Make psychological or personality-based assessments
- Provide vague advice without actionable specifics
- Focus on soft skills without technical grounding
- Use discouraging language
- Reference emotional intelligence or personality frameworks

### Prioritization Logic

Improvement areas are prioritized based on:
1. **Feature weights** from job analysis (higher weight = higher priority)
2. **Score gaps** (bigger gaps = higher priority)
3. **Market impact** (skills significantly affecting competitiveness)

---

## Usage

### Basic Usage: Single Candidate Feedback

```python
from candidate_feedback_generator import generate_candidate_feedback

# Load evaluation and job data
evaluation_data = {
    "candidate_id": 2,
    "feature_scores": [...],
    "affinity_score": 0.85
}

job_requirements = {
    "tech_skills": ["Python", "Machine Learning", ...],
    "weights": {...},
    "company_name": "TechCorp",
    "company_culture": "..."
}

# Generate feedback
feedback = generate_candidate_feedback(
    candidate_id=2,
    evaluation_data=evaluation_data,
    job_requirements=job_requirements
)

print(feedback.profile_summary.overall_assessment)
for area in feedback.improvement_areas:
    print(f"- {area.dimension}: {area.current_gap}")
    for rec in area.actionable_recommendations:
        print(f"  • {rec}")
```

### Batch Processing: All Rejected Candidates

```python
from candidate_feedback_generator import generate_feedback_for_rejected_candidates

# Generate feedback for all candidates except top 1
feedback_results = generate_feedback_for_rejected_candidates(
    top_n=1,  # Number of top candidates to exclude
    evaluations_file=Path("data/candidate_evaluations.json"),
    requirements_file=Path("data/job_requirements.json"),
    output_file=Path("data/candidate_feedback.json")
)

# Results saved to data/candidate_feedback.json
```

### Command-Line Execution

```bash
# Run with defaults (keep top 1, process all others)
python src/candidate_feedback_generator.py

# Output files:
# - data/candidate_feedback.json (structured JSON)
# - Console: Formatted text reports
```

### Human-Readable Formatting

```python
from candidate_feedback_generator import format_feedback_as_text

formatted_text = format_feedback_as_text(feedback, candidate_id=2)
print(formatted_text)

# Output suitable for:
# - Email templates
# - PDF reports
# - Applicant tracking systems
# - Candidate communication portals
```

---

## Output Format

### JSON Output Structure

```json
{
  "metadata": {
    "generation_date": "2025-11-09T...",
    "total_candidates": 4,
    "top_selected": 1,
    "feedback_generated_for": 3,
    "job_role": "Lululemon"
  },
  "feedback": {
    "2": {
      "candidate_id": 2,
      "profile_summary": {...},
      "technical_strengths": [...],
      "improvement_areas": [...],
      "industry_alignment_score": 0.75,
      "next_steps_summary": "..."
    }
  }
}
```

### Human-Readable Text Output

```
================================================================================
CANDIDATE FEEDBACK REPORT - Candidate #2
================================================================================

PROFILE SUMMARY
--------------------------------------------------------------------------------
[2-3 sentence overall assessment]

Standout Qualities:
  • [Quality 1]
  • [Quality 2]
  • [Quality 3]

Career Stage: [Assessment]
Industry Alignment Score: 0.75 / 1.0


YOUR TECHNICAL STRENGTHS
--------------------------------------------------------------------------------
1. [Skill Area] (Advanced)
   Evidence: [Specific evidence from documents]

2. [Skill Area] (Intermediate)
   Evidence: [Specific evidence from documents]

...


AREAS FOR IMPROVEMENT
--------------------------------------------------------------------------------
1. [Dimension Name]
   Current Gap: [Specific gap identified]
   Why It Matters: [Importance context]
   Timeline: Medium-term (3-6 months)

   Actionable Recommendations:
      • [Specific action 1]
      • [Specific action 2]
      • [Specific action 3]
      • [Specific action 4]
      • [Specific action 5]

...


RECOMMENDED NEXT STEPS
--------------------------------------------------------------------------------
[Concise 2-3 sentence summary of top priorities]

================================================================================
```

---

## Integration with Recruitment Pipeline

### Pipeline Flow

```
Job Analysis (Agent A)
    ↓
Candidate Evaluation (Agent B)
    ↓
Ranking & Selection
    ↓
Feedback Generation (This Module) ← For rejected candidates
    ↓
Candidate Communication
```

### Required Input Files

1. **`data/candidate_evaluations.json`** (from Agent B)
   - Contains all candidate scores and affinity ratings

2. **`data/job_requirements.json`** (from Agent A)
   - Technical skills, feature weights, company culture

3. **`data/candidate_X/`** (candidate documents)
   - CVs (PDF), LinkedIn profiles (JSON), portfolios (text/JSON)

### Output Files

- **`data/candidate_feedback.json`** - Structured feedback data
- **Console Output** - Human-readable formatted reports

---

## Configuration

### Environment Variables

Required in `.env` file:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

### Adjustable Parameters

**In `generate_feedback_for_rejected_candidates()`:**

- `top_n`: Number of top candidates to exclude (default: 1)
- `evaluations_file`: Path to evaluations JSON
- `requirements_file`: Path to job requirements JSON
- `output_file`: Path for feedback output

**In `generate_candidate_feedback()`:**

- `temperature`: 0.2 (can adjust for more/less determinism)
- `model_name`: "gemini-2.5-flash" (can use other Gemini models)

---

## Best Practices

### 1. Feedback Timing
- Generate feedback after final hiring decisions
- Ensure top N candidates are confirmed before batch processing

### 2. Customization
- Adjust `top_n` based on hiring pipeline (e.g., top 3 for roles with multiple positions)
- Modify feature weights to emphasize role-specific competencies

### 3. Quality Assurance
- Review generated feedback for alignment with company values
- Validate recommendations against industry standards
- Ensure actionable advice is specific and achievable

### 4. Privacy & Compliance
- Redact sensitive information before distribution
- Ensure feedback complies with employment law (no protected class references)
- Focus strictly on professional competencies (no psychological assessments)

### 5. Communication Integration
- Format feedback for your ATS or email system
- Personalize subject lines and introductions
- Include contact information for follow-up questions

---

## Example: Actionable Recommendations

### Good Examples (Specific & Actionable)

✅ "Complete the 'Machine Learning Specialization' on Coursera (offered by Stanford) to strengthen foundational ML knowledge"

✅ "Build a portfolio project using Python and scikit-learn that demonstrates end-to-end ML pipeline (data preprocessing, model training, evaluation). Host on GitHub with comprehensive README"

✅ "Join the 'Python Developers' community on LinkedIn and engage with 2-3 posts per week to build industry connections"

✅ "Achieve AWS Certified Machine Learning - Specialty certification within 6 months to demonstrate cloud ML proficiency"

### Bad Examples (Vague or Non-Actionable)

❌ "Improve your communication skills"
❌ "Learn more about machine learning"
❌ "Work on being more confident"
❌ "Try to be more creative"

---

## Troubleshooting

### Error: "No documents found for candidate X"
- **Solution**: Ensure `data/candidate_X/` directory exists with at least one document (PDF, JSON, or text)

### Error: "GOOGLE_CLOUD_PROJECT not found"
- **Solution**: Add required environment variables to `.env` file

### Error: "Failed to parse LLM output"
- **Solution**: Check model availability and quota limits
- **Fallback**: Module includes JSON parsing fallback logic

### Warning: Empty feedback results
- **Solution**: Verify evaluation data has correct structure
- **Check**: Ensure `top_n` < total candidates evaluated

---

## Performance Metrics

### Processing Time
- **Single Candidate**: ~10-20 seconds (depending on document size and model latency)
- **Batch (3 candidates)**: ~30-60 seconds
- **Batch (10 candidates)**: ~2-3 minutes

### Token Usage
- **Average per candidate**: 5,000-8,000 tokens (input + output)
- **Large profiles (>10 documents)**: 10,000-15,000 tokens

### Cost Estimation (Gemini 2.5 Flash via Vertex AI)
- **Per candidate**: ~$0.01-0.03 USD
- **Batch (100 candidates)**: ~$1-3 USD

---

## Future Enhancements

### Planned Features

1. **Multi-language Support**
   - Generate feedback in candidate's preferred language
   - Translate technical recommendations

2. **Skill Gap Visualization**
   - Generate charts showing strength/weakness distribution
   - Career roadmap visualizations

3. **Learning Resource Integration**
   - Direct links to courses, certifications, and resources
   - Personalized learning pathways

4. **Follow-up Tracking**
   - Track candidate progress on recommendations
   - Re-evaluation after development period

5. **A/B Testing Framework**
   - Test different feedback formats
   - Measure candidate engagement and satisfaction

---

## Contributing

When extending this module:

1. **Maintain consistency** with existing Pydantic models
2. **Follow the prompting style** (evidence-based, actionable, technical)
3. **Add test cases** for new features
4. **Document changes** in this README
5. **Preserve focus** on professional development (no psychological feedback)

---

## License & Attribution

Part of the GlobalAI recruitment pipeline project.

**Developed by**: GlobalAI Team
**Last Updated**: November 2025
**Version**: 1.0.0

---

## Support

For questions or issues:
1. Check the troubleshooting section above
2. Review existing evaluation and job requirement files
3. Verify environment configuration
4. Contact the development team for assistance

---

**Remember**: The goal is to provide constructive, actionable feedback that helps candidates grow professionally and improve their competitiveness in the market. Focus on empowering candidates with specific steps they can take to enhance their skills and career prospects.
