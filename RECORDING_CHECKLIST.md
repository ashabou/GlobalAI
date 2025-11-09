# 🎬 TECH VIDEO RECORDING CHECKLIST

Use this on recording day. Check off each item as you go.

---

## PRE-RECORDING SETUP (30 min before)

### Environment Setup
- [ ] Close all unnecessary applications
- [ ] Turn on "Do Not Disturb" mode (no notifications)
- [ ] Charge laptop to 100% (or plug in power)
- [ ] Close all browser tabs except necessary tools
- [ ] Clear desktop of clutter
- [ ] Silence phone and other devices

### VS Code Setup
- [ ] Open GlobalAI project folder
- [ ] Set editor font size to 18pt minimum
- [ ] Disable minimap (`"editor.minimap.enabled": false`)
- [ ] Disable breadcrumbs (`"breadcrumbs.enabled": false`)
- [ ] Choose high-contrast theme (GitHub Dark recommended)
- [ ] Close all tabs except the 3 files you'll show:
  - `src/candidate_feedback_generator.py`
  - `src/candidate_profile_evaluator.py`
  - `src/job_requirements_analyzer.py`

### Assets Prepared
- [ ] Architecture diagram created (Excalidraw/Figma/draw.io)
- [ ] Code comparison graphic ready
- [ ] Cost comparison table ready
- [ ] Final title card designed
- [ ] Background music downloaded (optional)

### Recording Software Setup
- [ ] OBS Studio / Loom / QuickTime open and configured
- [ ] Recording resolution set to 1080p minimum
- [ ] Frame rate set to 30fps or 60fps
- [ ] Audio input tested (clear, no background noise)
- [ ] Test recording made and reviewed (check if code is readable!)

### Voice Preparation
- [ ] Water nearby (stay hydrated)
- [ ] Read voiceover script 3 times (practice timing)
- [ ] Time yourself (should be 55-58 seconds, leaving buffer)
- [ ] Warm up voice (read out loud for 2-3 minutes)

---

## RECORDING SEQUENCE

### SHOT 1: Opening [0:00-0:08]
- [ ] Start recording
- [ ] Show VS Code project structure (2 sec)
- [ ] Transition to architecture diagram (6 sec)
- [ ] Voiceover: "GlobalAI uses Google's Gemini..."
- [ ] Verify timing with stopwatch

### SHOT 2: Innovation Highlight [0:08-0:15]
- [ ] Keep architecture diagram on screen
- [ ] Animate or highlight Pydantic path
- [ ] Voiceover: "But the real innovation..."
- [ ] Check timing (should be at 15 seconds mark)

### SHOT 3A: Problem Statement [0:15-0:20]
- [ ] Switch to VS Code
- [ ] Open `candidate_feedback_generator.py`
- [ ] Scroll to line 38 (ImprovementArea class)
- [ ] Zoom to 200%
- [ ] Voiceover: "The hardest problem..."

### SHOT 3B: Solution [0:20-0:35]
- [ ] Scroll down to line 315 (config setup)
- [ ] Highlight lines 315-319
- [ ] Show code comparison graphic (side-by-side)
- [ ] Voiceover: "We solved this by passing Pydantic schemas..."
- [ ] Hold on code for 5 seconds (let judges read it)

### SHOT 4A: Challenge 1 [0:35-0:42]
- [ ] Switch to `candidate_profile_evaluator.py`
- [ ] Scroll to line 301 (fallback parsing)
- [ ] Show try/except structure
- [ ] Voiceover: "First, LLMs can still hallucinate..."

### SHOT 4B: Challenge 2 [0:42-0:49]
- [ ] Switch to `job_requirements_analyzer.py`
- [ ] Scroll to line 114 (CSS selectors)
- [ ] Highlight the job_selectors array
- [ ] Voiceover: "Second, every job board has different HTML..."

### SHOT 4C: Challenge 3 [0:49-0:55]
- [ ] Show cost comparison table graphic
- [ ] Highlight "10x cheaper, 3x faster"
- [ ] Voiceover: "Third, Vertex AI costs add up..."

### SHOT 5: Closing [0:55-1:00]
- [ ] Show terminal with successful run (or your face)
- [ ] Transition to final title card
- [ ] Voiceover: "Biggest lesson? Structured output..."
- [ ] Hold on title card for 2 seconds
- [ ] STOP RECORDING

---

## IMMEDIATE POST-RECORDING

### Quick Review
- [ ] Watch entire recording
- [ ] Check timing (should be 58-60 seconds)
- [ ] Verify all code is readable
- [ ] Check audio quality (clear, no distortion)
- [ ] Note any issues for re-recording

### Decision Point
- [ ] Satisfactory? → Proceed to editing
- [ ] Issues found? → Re-record problematic sections

---

## EDITING CHECKLIST

### Import & Organize
- [ ] Import all video clips into editor
- [ ] Import graphics (diagrams, tables, title card)
- [ ] Import background music (if using)
- [ ] Organize in timeline chronologically

### Video Edits
- [ ] Trim any dead space at beginning/end
- [ ] Cut out any mistakes or long pauses
- [ ] Add smooth transitions between shots (fade, slide)
- [ ] Ensure total duration is 58-60 seconds

### Add Graphics
- [ ] Overlay architecture diagram [0:00-0:15]
- [ ] Add tech stack text overlay [0:05-0:08]
- [ ] Insert code comparison graphic [0:25-0:30]
- [ ] Add cost comparison table [0:49-0:55]
- [ ] Place final title card [0:58-1:00]

### Add Annotations
- [ ] Arrow pointing to "Force JSON format" (line 316)
- [ ] Arrow pointing to "Pass our schema" (line 317)
- [ ] Highlight key code sections with yellow background
- [ ] Add "✅" checkmarks on success points
- [ ] Add callout: "⭐ The Magic" near Pydantic config

### Add Text Overlays
- [ ] "Challenge 1: LLM Hallucinations" [0:35]
- [ ] "Challenge 2: Inconsistent HTML" [0:42]
- [ ] "Challenge 3: API Costs" [0:49]
- [ ] "Schema-driven LLMs" [0:58]

### Audio
- [ ] Verify voiceover is clear throughout
- [ ] Add background music (if using) at -20dB
- [ ] Fade music in/out smoothly
- [ ] Check for audio peaks (no distortion)
- [ ] Balance voice and music levels

### Captions/Subtitles
- [ ] Generate auto-captions (YouTube, Rev.com, or manual)
- [ ] Review and fix any errors
- [ ] Format: White text, black background, centered
- [ ] Ensure readable font size
- [ ] Export as SRT file or burn into video

### Color Correction (Optional)
- [ ] Adjust brightness/contrast for clarity
- [ ] Ensure code is high contrast
- [ ] Match color grading across all shots

---

## EXPORT SETTINGS

### Video Export
- [ ] Format: MP4 (H.264 codec)
- [ ] Resolution: 1920x1080 (1080p) or 3840x2160 (4K)
- [ ] Frame rate: 30fps or 60fps (match recording)
- [ ] Bitrate: 8-10 Mbps (high quality)

### Audio Export
- [ ] Codec: AAC
- [ ] Sample rate: 48kHz
- [ ] Bitrate: 192kbps or higher

### File Size
- [ ] Target: Under 500MB (most platforms)
- [ ] If too large: Reduce bitrate slightly

---

## FINAL QUALITY CHECK

### Technical Review
- [ ] Play full video start to finish
- [ ] Check timing (exactly 60 seconds or less)
- [ ] Verify all code is readable on mobile device
- [ ] Confirm audio is clear (test with headphones)
- [ ] Check for typos in text overlays
- [ ] Verify all transitions are smooth

### Content Review
- [ ] Does it clearly explain the tech stack?
- [ ] Is the Pydantic innovation highlighted?
- [ ] Are all 3 challenges explained?
- [ ] Is the closing message impactful?
- [ ] Would a judge understand this without prior knowledge?

### Platform Check
- [ ] Test playback on laptop
- [ ] Test playback on mobile phone
- [ ] Verify captions work properly
- [ ] Check thumbnail clarity (if separate)

---

## SUBMISSION

- [ ] Rename file: `GlobalAI_Tech_Video_60sec.mp4`
- [ ] Upload to submission platform
- [ ] Upload separate captions file (if required)
- [ ] Verify upload completed successfully
- [ ] Test playback on submission platform
- [ ] Save backup copy to cloud (Google Drive, Dropbox)

---

## BACKUP PLAN (If Something Goes Wrong)

### If recording fails:
- [ ] Have backup recording app ready (e.g., QuickTime if OBS fails)
- [ ] Save raw recordings in multiple locations
- [ ] Test equipment 1 day before deadline

### If editing takes too long:
- [ ] Simplified version: Just screen recording + voiceover (no graphics)
- [ ] Use Loom (auto-captions, no editing needed)
- [ ] Focus on SHOWING code over polish

### If timing is off:
- [ ] Speed up video slightly (1.1x speed in editor)
- [ ] Cut pauses between sentences
- [ ] Simplify Challenge 3 section (save 5 seconds)

---

## TIME BUDGET

Realistic timeline for production:

| Task | Time Needed |
|------|-------------|
| Setup & practice | 30 min |
| Recording (with retakes) | 1-2 hours |
| Editing | 2-3 hours |
| Review & export | 30 min |
| **TOTAL** | **4-6 hours** |

**Start at least 2 days before deadline!**

---

## QUICK REFERENCE: Key Messages

If you forget everything else, remember these 3 points:

1. **Innovation**: "Pydantic schemas force LLMs to return valid JSON"
2. **Challenges**: "Fallback parsing, CSS selectors, cost optimization"
3. **Lesson**: "Structured output is the future of production LLM apps"

---

## CONFIDENCE BOOSTERS

Before you start recording, remember:

✅ Your Pydantic approach is genuinely sophisticated
✅ Most teams DON'T use structured output
✅ You solved real production challenges
✅ Judges will appreciate the technical depth
✅ You've built something production-ready

**You've got this! 🚀**

---

## POST-SUBMISSION

After you submit:

- [ ] Celebrate! 🎉
- [ ] Save all project files for portfolio
- [ ] Consider posting on LinkedIn/Twitter
- [ ] Prepare for demo questions from judges
- [ ] Relax and wait for results

---

## EMERGENCY CONTACTS (Just in case)

- Video editing help: YouTube tutorials, DaVinci Resolve forums
- Audio issues: Audacity (free audio editor)
- Screen recording issues: OBS Discord, Reddit r/obs
- Last-minute questions: Stack Overflow, AI Discord communities

---

Good luck! Follow this checklist and you'll have a polished, professional tech video that impresses the judges. 🎬
