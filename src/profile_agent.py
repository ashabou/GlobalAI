import os
import json
from dotenv import load_dotenv
from langchain_core.prompts.prompt import PromptTemplate
from langchain_community.chat_models import ChatGooglePalm
from langchain_community.document_loaders import PyPDFLoader
from pydantic import BaseModel
from typing import List

# -------------------------------
# 1️⃣ Pydantic models for output
# -------------------------------

class FeatureScore(BaseModel):
    name: str
    weight: float
    score: float

class CandidateEvaluation(BaseModel):
    feature_scores: List[FeatureScore]
    affinity_score: float

# -------------------------------
# 2️⃣ Load environment variables
# -------------------------------

load_dotenv()  # loads .env from current working directory
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# -------------------------------
# 3️⃣ Evaluation function
# -------------------------------

def evaluate_candidate(ID: int, requirements: dict) -> CandidateEvaluation:
    folder = f"data/candidate_{ID}/"
    cv_path = os.path.join(folder, f"cv_{ID}.pdf")
    linkedin_path = os.path.join(folder, f"linkedin_post_{ID}.json")

    # --- Load CV ---
    loader = PyPDFLoader(cv_path)
    pages = loader.load()
    cv_text = "\n".join([p.page_content for p in pages])

    # --- Load LinkedIn JSON ---
    with open(linkedin_path, "r") as f:
        linkedin_data = json.load(f)
    linkedin_text = json.dumps(linkedin_data, indent=2)

    # --- Combine both sources ---
    combined_text = f"=== CV ===\n{cv_text}\n\n=== LinkedIn Data ===\n{linkedin_text}"

    # --- Define prompt ---
    prompt = PromptTemplate(
        input_variables=["candidate_text", "requirements"],
        template=(
            "You are an expert technical recruiter.\n"
            "Analyze the following candidate information:\n\n"
            "{candidate_text}\n\n"
            "The company is looking for these features (with weights):\n{requirements}\n\n"
            "For each feature, assign a score between 0 and 1 representing how well the candidate matches it.\n"
            "Then compute the weighted average (affinity_score).\n\n"
            "Return a valid JSON object exactly like this:\n"
            "{{\n"
            "  \"feature_scores\": [\n"
            "     {{\"name\": ..., \"weight\": ..., \"score\": ...}}, ...\n"
            "  ],\n"
            "  \"affinity_score\": ...\n"
            "}}"
        )
    )

    # --- Initialize Google PaLM ---
    llm = ChatGooglePalm(model="chat-bison-001", temperature=0)

    # --- Format prompt ---
    input_text = prompt.format(candidate_text=combined_text, requirements=json.dumps(requirements))

    # --- Call the LLM ---
    response_text = llm.predict_messages([{"role": "user", "content": input_text}])

    # --- Parse with Pydantic ---
    try:
        result = CandidateEvaluation.parse_raw(response_text)
    except Exception as e:
        print("Error parsing LLM output:", e)
        print("Raw output:", response_text)
        raise

    return result

# -------------------------------
# 4️⃣ Example usage
# -------------------------------

if __name__ == "__main__":
    requirements = {
        "features": [
            {"name": "Machine Learning", "weight": 0.4},
            {"name": "Python programming", "weight": 0.3},
            {"name": "Communication skills", "weight": 0.2},
            {"name": "Leadership", "weight": 0.1}
        ]
    }

    result = evaluate_candidate(1, requirements)
    print(result.json(indent=2))
