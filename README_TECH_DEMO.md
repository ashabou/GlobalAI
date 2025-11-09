# GlobalAI - Tech Demo Strategy & Scripts

This folder contains everything you need to create both your **Product Demo** (60 sec) and **Tech Video** (60 sec) for the competition.

---

## 📁 Files in This Package

### Main Script Files
1. **`tech_video_script.md`** - Complete production script for the Tech Video
   - Shot-by-shot breakdown
   - Visual descriptions
   - Timing for each section
   - Audio/editing notes

2. **`voiceover_script.txt`** - Word-for-word voiceover script
   - Exactly what to say
   - Pronunciation guide
   - Timing marks
   - Emphasis notes

3. **`code_snippets_for_video.md`** - All code to show in the video
   - Exact line numbers
   - Files to open
   - Annotations to add
   - VS Code settings

4. **`architecture_diagram.md`** - Reference for creating visuals
   - ASCII diagram
   - Mermaid code
   - Color scheme
   - Tool recommendations

5. **`RECORDING_CHECKLIST.md`** - Step-by-step recording guide
   - Pre-recording setup
   - Shot sequence
   - Editing checklist
   - Export settings

---

## 🎯 Which File to Use When

### PHASE 1: Planning (Day 1)
**Read these files:**
- `tech_video_script.md` - Understand the overall structure
- `voiceover_script.txt` - Familiarize yourself with what you'll say
- `architecture_diagram.md` - Plan your visuals

**Actions:**
- [ ] Create architecture diagram (use Excalidraw/Figma)
- [ ] Design comparison graphics (With/Without Pydantic)
- [ ] Design cost comparison table
- [ ] Create final title card

---

### PHASE 2: Practice (Day 1-2)
**Read these files:**
- `voiceover_script.txt` - Practice reading out loud
- `code_snippets_for_video.md` - Open the files, find the right lines

**Actions:**
- [ ] Read voiceover 5+ times
- [ ] Time yourself (should be ~55-58 seconds)
- [ ] Navigate VS Code to each code snippet
- [ ] Adjust font size, theme, settings
- [ ] Do a practice screen recording

---

### PHASE 3: Recording Day (Day 2-3)
**Use this file:**
- `RECORDING_CHECKLIST.md` - Follow step by step

**Have open on second screen:**
- `voiceover_script.txt` - For reading during recording
- `tech_video_script.md` - For shot timing reference

**Actions:**
- [ ] Complete all pre-recording setup
- [ ] Record each shot following the checklist
- [ ] Review immediately after recording
- [ ] Re-record any problematic sections

---

### PHASE 4: Editing (Day 3)
**Reference files:**
- `tech_video_script.md` - For correct sequence and timing
- `code_snippets_for_video.md` - For annotation placement
- `RECORDING_CHECKLIST.md` - For editing checklist

**Actions:**
- [ ] Import all clips and graphics
- [ ] Cut and arrange shots
- [ ] Add text overlays and annotations
- [ ] Add background music (optional)
- [ ] Add captions/subtitles
- [ ] Export and review

---

## 🎬 Two Video Strategy

You need to create TWO 60-second videos:

### Video 1: Product Demo (What It Does)
**Goal**: Show the tool working - impress with functionality
**Structure**:
- 5-10 sec: Problem statement
- 45-50 sec: Screen recording of tool in action
- 5 sec: Impact/result

**Not included in this package** - See original conversation for Product Demo script

---

### Video 2: Tech Video (How We Built It)
**Goal**: Explain your engineering approach - impress with technical depth
**Structure**:
- 10-15 sec: Tech stack overview
- 15-20 sec: Implementation highlight (Pydantic schemas)
- 15-20 sec: Challenges & trade-offs
- 5 sec: Key lesson learned

**All files in this package are for the Tech Video**

---

## 🔑 Key Messages (Don't Forget These!)

### Core Innovation
> "We pass Pydantic schemas directly to Gemini's structured output API, forcing the model to return valid JSON matching our exact structure—no parsing errors, no validation issues, just perfect data every time."

### Three Challenges
1. **LLM Hallucinations** → Multi-layer fallback parsing
2. **Inconsistent HTML** → 7 fallback CSS selectors
3. **API Costs** → Flash models (10x cheaper, 3x faster)

### Closing Insight
> "Structured output is the future of LLM applications. It turns generative AI into reliable, production-grade software."

---

## ⏱️ Timeline Recommendation

### 2 Days Before Deadline
- **Day 1 Morning**: Create all graphics/diagrams (2-3 hours)
- **Day 1 Afternoon**: Practice voiceover, test recording setup (2 hours)
- **Day 1 Evening**: Do full practice run, time yourself (1 hour)

### 1 Day Before Deadline
- **Day 2 Morning**: Record all shots (2-3 hours with retakes)
- **Day 2 Afternoon**: Edit video, add graphics/annotations (3-4 hours)
- **Day 2 Evening**: Review, export, upload (1 hour)

### Deadline Day
- **Buffer time for emergencies**
- Final review and submission
- DO NOT START EDITING ON DEADLINE DAY!

---

## 🎨 Assets You Need to Create

Before recording, create these graphics:

### 1. Architecture Diagram
Shows: Job URL → Scraper → LLM → Pydantic Schema → Valid JSON → Rankings
**Time on screen**: 0:00-0:15
**Tool**: Excalidraw (recommended) or draw.io

### 2. Code Comparison Table
```
Without Pydantic Schema     |  With Pydantic Schema
❌ Inconsistent text        |  ✅ Valid JSON every time
❌ Manual parsing           |  ✅ Auto-validated
```
**Time on screen**: 0:25-0:30
**Tool**: Canva, Figma, or PowerPoint

### 3. Cost Comparison Table
```
              Gemini Pro    Gemini Flash
Cost          $3.50         $0.35 (10x cheaper)
Speed         900ms         300ms (3x faster)
Accuracy      98%           95%
```
**Time on screen**: 0:49-0:55
**Tool**: Excel, Google Sheets, or Figma

### 4. Final Title Card
```
🔑 KEY INSIGHT
Schema-driven LLMs = AI you can trust in production
GlobalAI - AI-Powered Recruitment
```
**Time on screen**: 0:58-1:00
**Tool**: Canva, Figma, or PowerPoint

---

## 💡 Pro Tips

### DO:
✅ Make code font size 18pt+ (must be readable on mobile)
✅ Use high-contrast VS Code theme (GitHub Dark)
✅ Pause on key code sections (let judges read it)
✅ Speak clearly and slightly slower than normal
✅ Test playback on mobile device before submitting

### DON'T:
❌ Rush through the technical explanation
❌ Use small font sizes (code must be readable)
❌ Include too many code sections (focus on 3-4 key snippets)
❌ Forget to add captions (accessibility + clarity)
❌ Start editing on deadline day

---

## 🆘 Troubleshooting

### "I'm running out of time!"
→ Use simplified version: Screen recording + voiceover only (no fancy graphics)
→ Use Loom (easier than OBS, auto-captions)
→ Cut Challenge 3 if needed (save 7 seconds)

### "Code isn't readable on video"
→ Increase font size to 20-24pt
→ Use Zen Mode in VS Code (hides sidebar)
→ Record in 4K instead of 1080p

### "Timing is off (over 60 seconds)"
→ Speed up video to 1.05x or 1.1x in editor
→ Cut pauses between sentences
→ Shorten Challenge 2 or 3 sections

### "Audio quality is poor"
→ Record in quiet room
→ Use headphones mic or external mic
→ Add noise reduction in Audacity (free tool)
→ Speak closer to microphone

---

## 🎓 What Judges Are Looking For

### Technical Judges Want to See:
- **Sophistication**: Pydantic structured output (most teams don't know this!)
- **Production thinking**: Error handling, fallback strategies
- **Trade-offs**: You chose Flash over Pro (cost awareness)
- **Real engineering**: Multi-format parsing, robust scraping

### What Makes Your Video Stand Out:
- You're not just using an LLM - you're CONTROLLING it with schemas
- You thought through real-world challenges (costs, reliability, scraping)
- You built production-grade error handling
- You can explain WHY you made specific technical choices

---

## ✅ Final Checklist Before Submission

- [ ] Video is exactly 60 seconds or less
- [ ] All code is readable (test on mobile)
- [ ] Audio is clear throughout
- [ ] Captions are accurate
- [ ] File format is MP4 (H.264)
- [ ] Resolution is 1080p minimum
- [ ] Pydantic innovation is clearly explained
- [ ] All 3 challenges are mentioned
- [ ] Closing insight is impactful
- [ ] Saved backup copy to cloud

---

## 🎯 Success Criteria

**Your video is successful if a judge watching it thinks:**

1. "They actually understand production LLM development"
2. "That Pydantic schema approach is clever - I should try that"
3. "They solved real engineering problems, not just hackathon problems"
4. "This is production-ready, not just a prototype"
5. "I want to see this demo in person"

---

## 📞 Need Help?

If you get stuck:
- **Video editing**: YouTube "DaVinci Resolve tutorials" (free, professional)
- **Screen recording**: OBS Studio Discord community
- **Voiceover**: Practice with free teleprompter apps
- **Graphics**: Canva templates (search "comparison table")

---

## 🚀 You've Got This!

Remember:
- Your technical approach (Pydantic schemas) is genuinely sophisticated
- You've solved real production problems
- The video doesn't need to be Hollywood-quality - judges want CLARITY
- Focus on explaining your innovation clearly
- Have confidence in your engineering choices

**Follow the checklist, stick to the script, and you'll create a compelling tech video that stands out.**

Good luck! 🎬

---

_Last updated: 2025-11-09_
_For questions or issues with these scripts, review the detailed files above._
