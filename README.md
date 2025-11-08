# Relieve AI – Live in a Movie (Dummy Project)

> **Step into the scene.**  
> Relieve AI transforms your life moments into cinematic experiences using generative AI.

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/relieve-ai.git
cd relieve-ai
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # on macOS/Linux
venv\Scripts\activate      # on Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your environment variables
Create a `.env` file in the root directory with your API keys:
```bash
OPENAI_API_KEY=your_openai_api_key
HF_API_TOKEN=your_huggingface_token
REPLICATE_API_TOKEN=your_replicate_token
```

### 5. Run the app
```bash
python app.py
```

or, if it’s a web app:

```bash
streamlit run app.py
```

Then open your browser at **http://localhost:8501**

---

## 1. Problem & Challenge

Modern users are surrounded by media, yet **creating cinematic experiences of one’s own life** remains inaccessible.  
Video editing, VFX tools, and storytelling require time and expertise.  
**Relieve AI** bridges this gap — turning everyday prompts, selfies, or text into **movie-like scenes** in seconds.

---

## 2. Target Audience

- **Content creators** who want fast, cinematic storytelling  
- **Casual users** who dream of seeing themselves as heroes in film-like scenes  
- **Studios & marketing teams** exploring AI-driven story generation

---

## 3. Solution & Core Features

Relieve AI combines multimodal AI models to **generate cinematic content** from user inputs.

- **Scene Builder:** Describe a scene in natural language (“me in a sci-fi city at night”)  
- **Character Personalization:** Upload your selfie → it adapts your likeness  
- **Cinematic Output:** Generates short video snippets or stylized image frames  
- **AI Director Mode:** Lets you refine mood, camera angles, or dialogue interactively  

---

## 4. Unique Selling Proposition (USP)

Unlike traditional content generation tools:
- **Runs end-to-end in minutes** — no manual editing or post-production  
- **Personalized, multimodal pipeline** (text + image → video)  
- **Cinematic intelligence:** prompts guided by film-style datasets for tone and composition  
- **Lightweight demo setup** for instant hackathon showcase  

---

## 5. Implementation & Technology

**Architecture overview**
- **Frontend:** Streamlit (quick, reactive demo UI)  
- **Backend:** Python + FastAPI for API orchestration  
- **Models:**
  - `GPT-4` or `Llama-3` for narrative generation  
  - `Stable Diffusion / Flux.1` for image generation  
  - `Pika Labs` or `RunwayML` for short video clips  
- **Storage:** Local temp cache for generated media  
- **Deployment:** Streamlit Cloud or local Docker container  

---

### requirements.txt (excerpt)
```text
python-dotenv
streamlit
openai
torch
transformers
diffusers
Pillow
requests
fastapi
uvicorn
replicate
```

---

## 6. Results & Impact

Within 24 hours, our team delivered:
- A **fully working demo** generating AI movie scenes from text + selfies  
- A **3-minute cinematic showcase** featuring real-time story generation  
- A solution that empowers creativity, democratizing cinematic storytelling  

**Impact:**  
Relieve AI reduces the barrier between imagination and visual expression — letting anyone *live inside their favorite movie*.

---

## 🎥 Demo Link

[Watch the Live Demo on YouTube](https://youtu.be/your-demo-link)  
or  
[Try the Web Demo](https://relieve-ai-demo.streamlit.app)

---

## Hackathon Info
- **Track:** Generative AI / Creativity  
- **Challenge:** *“Relieve AI – Live in a Movie”*  
- **Duration:** 24 hours  

---

## Team
- Kenza Amara – AI Research
- Zhou Gui – AI Research
- Vinicius Santos –  
- Aziz – 

---

## License
MIT License © 2025 Relieve AI Team
