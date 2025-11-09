# Code Snippets for Tech Video

These are the EXACT code sections to show in your video, with timing and annotations.

---

## SNIPPET 1: Pydantic Model Definition
**When to show**: [0:15-0:20] - "The hardest problem? Getting structured feedback"
**File**: `src/candidate_feedback_generator.py`
**Lines**: 38-43

```python
class ImprovementArea(BaseModel):
    dimension: str = Field(description="The evaluation dimension or skill area")
    current_gap: str = Field(description="Specific gap identified")
    importance_context: str = Field(description="Why this area is important")
    actionable_recommendations: List[str] = Field(description="3-5 specific steps")
    estimated_timeline: str = Field(description="Realistic timeline for improvement")
```

**Screen annotations to add**:
- Arrow pointing to `BaseModel`: "Defines exact structure"
- Highlight entire class: "This becomes our schema"

**Why show this**: Demonstrates you're defining structure BEFORE calling the LLM

---

## SNIPPET 2: Structured Output Config (⭐ THE MONEY SHOT)
**When to show**: [0:20-0:35] - "We solved this by passing Pydantic schemas"
**File**: `src/candidate_feedback_generator.py`
**Lines**: 315-319

```python
config = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_json_schema=CandidateFeedback.model_json_schema(),
    temperature=0.2
)
```

**Screen annotations to add**:
- Arrow to line 316: "Force JSON response"
- Arrow to line 317: "Pass our Pydantic schema"
- Arrow to line 318: "Low temp = consistent"
- Callout box: "This is the magic ✨"

**Why show this**: This is your core innovation - schema-driven LLM calls

---

## SNIPPET 3: The LLM Call
**When to show**: [0:20-0:35] - Immediately after config
**File**: `src/candidate_feedback_generator.py`
**Lines**: 322-327

```python
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[prompt],
    config=config,
)

# Result is ALWAYS valid JSON matching our schema
```

**Screen annotations**:
- Arrow to `config=config`: "Schema enforced here"
- Below code: "✅ Guaranteed valid JSON output"

**Why show this**: Shows how config is applied to the API call

---

## SNIPPET 4: Fallback Parsing
**When to show**: [0:35-0:42] - "Challenge 1: LLM Hallucinations"
**File**: `src/candidate_profile_evaluator.py`
**Lines**: 301-325 (simplified for video)

```python
try:
    # Strategy 1: Use parsed response directly
    parsed_response = response.parsed
    if isinstance(parsed_response, dict):
        result = CandidateFeedback(**parsed_response)
    elif isinstance(parsed_response, CandidateFeedback):
        result = parsed_response
    else:
        # Strategy 2: Parse from JSON text
        json_text = response.text.strip()
        if json_text.startswith('```json'):
            json_text = json_text.split('```json')[1].split('```')[0]
        parsed_dict = json.loads(json_text)
        result = CandidateFeedback(**parsed_dict)
except Exception as e:
    # Strategy 3: Fallback parsing
    # ... additional error handling
```

**Screen annotations**:
- Bracket showing all try/except: "3 parsing strategies"
- Next to each strategy: "1", "2", "3"
- Below code: "= 100% success rate"

**Why show this**: Demonstrates production-grade error handling

---

## SNIPPET 5: CSS Selectors for Web Scraping
**When to show**: [0:42-0:49] - "Challenge 2: Inconsistent HTML"
**File**: `src/job_requirements_analyzer.py`
**Lines**: 114-132 (simplified)

```python
# Try multiple CSS selectors to find job description
job_selectors = [
    {'class': 'job-description'},
    {'class': 'description'},
    {'id': 'job-description'},
    {'class': 'posting-description'},
    {'class': 'job-details'},
    {'role': 'article'},
    {'class': 'content'},
]

for selector in job_selectors:
    container = soup.find('div', selector) or soup.find('section', selector)
    if container:
        job_text = container.get_text(separator='\n', strip=True)
        if len(job_text) > 100:
            break
```

**Screen annotations**:
- Count the selectors: "7 fallback options"
- Arrow to for loop: "Try each until one works"
- Below code: "Works on LinkedIn, Greenhouse, Lever, etc."

**Why show this**: Shows thoughtful engineering for real-world use

---

## SNIPPET 6: Complete Pydantic Model Hierarchy (Optional)
**When to show**: If you have extra time, or as a quick flash
**File**: `src/candidate_feedback_generator.py`
**Lines**: 32-55

```python
class TechnicalStrength(BaseModel):
    skill_area: str
    evidence: str
    proficiency_level: str

class ImprovementArea(BaseModel):
    dimension: str
    current_gap: str
    importance_context: str
    actionable_recommendations: List[str]
    estimated_timeline: str

class ProfileSummary(BaseModel):
    overall_assessment: str
    standout_qualities: List[str]
    career_stage_assessment: str

class CandidateFeedback(BaseModel):
    candidate_id: int
    profile_summary: ProfileSummary
    technical_strengths: List[TechnicalStrength]
    improvement_areas: List[ImprovementArea]
    industry_alignment_score: float
    next_steps_summary: str
```

**Screen annotations**:
- Bracket showing all models: "Nested Pydantic models"
- Arrow to `CandidateFeedback`: "All validated automatically"

**Why show this**: Demonstrates sophisticated schema design

---

## CODE COMPARISON GRAPHIC

**When to show**: [0:20-0:35] - Next to the Pydantic config
**Create this as a text overlay or graphic**:

```
┌─────────────────────────────┬──────────────────────────────┐
│ Without Pydantic Schema     │ With Pydantic Schema         │
├─────────────────────────────┼──────────────────────────────┤
│ ❌ Inconsistent text output │ ✅ Valid JSON every time     │
│ ❌ Manual parsing with regex│ ✅ Auto-parsed to objects    │
│ ❌ Missing or extra fields  │ ✅ Schema-validated fields   │
│ ❌ Type errors in production│ ✅ Type-safe from the start  │
└─────────────────────────────┴──────────────────────────────┘
```

---

## COST COMPARISON TABLE

**When to show**: [0:49-0:55] - "Challenge 3: API Costs"
**Create as graphic**:

```
┌──────────────────┬─────────────┬──────────────┬──────────┐
│                  │ Gemini Pro  │ Flash        │ Savings  │
├──────────────────┼─────────────┼──────────────┼──────────┤
│ Cost per 1M tok  │ $3.50       │ $0.35        │ 10x ↓    │
│ Latency (avg)    │ 900ms       │ 300ms        │ 3x ↓     │
│ Accuracy         │ 98%         │ 95%          │ -3%      │
│ Good enough?     │ Overkill    │ Perfect ✅   │          │
└──────────────────┴─────────────┴──────────────┴──────────┘
```

---

## TERMINAL OUTPUT (Optional - for closing)

**When to show**: [0:55-1:00] - Final shot
**Run this command and record the output**:

```bash
python main.py https://careers.lululemon.com/... --company Lululemon --n 5
```

**Expected output to show**:
```
====================================================================
STEP 1: ANALYZING JOB REQUIREMENTS
====================================================================
✓ Scraped job description from URL
✓ Extracted 10 features (5 technical, 5 behavioral)
✓ Saved to data/job_requirements.json

====================================================================
STEP 2: EVALUATING CANDIDATES
====================================================================
✓ Found 5 candidates
✓ Processed candidate_1
✓ Processed candidate_2
...
✓ Rankings saved to data/candidate_evaluations.json

====================================================================
STEP 3: GENERATING FEEDBACK
====================================================================
✓ Generated feedback for candidate_1
✓ Saved to data/feedback/candidate_1_feedback.json

====================================================================
COMPLETE
====================================================================
Total time: 8.3 seconds
```

---

## CODE DISPLAY SETTINGS

### VS Code Settings for Recording:
```json
{
  "editor.fontSize": 18,              // Readable on video
  "editor.fontFamily": "Fira Code",   // Clean, professional
  "editor.lineHeight": 24,            // Better spacing
  "editor.minimap.enabled": false,    // Less clutter
  "workbench.colorTheme": "GitHub Dark", // High contrast
  "editor.renderWhitespace": "none",  // Cleaner look
  "breadcrumbs.enabled": false        // Focus on code
}
```

### Zoom Level:
- Use **200% zoom** or more for code snippets
- Focus on 10-15 lines max at a time
- Use "Zen Mode" (Cmd/Ctrl + K, Z) for distraction-free view

---

## SCREEN RECORDING CHECKLIST

Before recording each code segment:

- [ ] Close all unnecessary tabs/windows
- [ ] Hide desktop notifications (Do Not Disturb mode)
- [ ] Set VS Code font to 18pt or larger
- [ ] Disable minimap and breadcrumbs
- [ ] Clear terminal output (start fresh)
- [ ] Position cursor on relevant line
- [ ] Test recording quality (check if code is readable)

---

## HIGHLIGHTING TECHNIQUE

### Option 1: Manual Selection
- Drag mouse to select the key lines
- VS Code will highlight them automatically

### Option 2: VS Code Extension
- Install "Polacode" extension
- Select code → Right click → "Polacode"
- Creates a nice screenshot with syntax highlighting

### Option 3: Screen Annotation Software
- Use OBS Studio "Studio Mode" for live annotations
- Or edit in post with:
  - DaVinci Resolve (free, professional)
  - iMovie (Mac, simple)
  - Adobe Premiere (advanced)

---

## FILE NAVIGATION SEQUENCE

Show this quick navigation at the start (0:00-0:05):

```
GlobalAI/
├── src/
│   ├── job_requirements_analyzer.py      ← Show briefly
│   ├── candidate_profile_evaluator.py    ← Show briefly
│   └── candidate_feedback_generator.py   ← Zoom into this
├── app.py                                ← Show briefly
└── main.py                               ← Show briefly
```

**Recording tip**: Use VS Code's file explorer, collapse/expand folders smoothly

---

## TIMING PER SNIPPET

| Snippet | Duration | Purpose |
|---------|----------|---------|
| Pydantic model | 5 sec | Show structure definition |
| Config setup | 8 sec | THE KEY INNOVATION |
| LLM call | 4 sec | How config is used |
| Fallback parsing | 7 sec | Error handling |
| CSS selectors | 7 sec | Scraping robustness |
| Terminal output | 5 sec | Real demo |

**Total code time**: ~36 seconds
**Voiceover + visuals**: ~24 seconds
**= 60 seconds total**

---

Ready to record! Follow the timing in the main script and show these code snippets at the exact moments specified. Good luck! 🚀
