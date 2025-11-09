import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

# New import for genai types
from google import genai
from google.genai import types 
import PyPDF2

# -------------------------------
# 1️⃣ Pydantic models for output
# -------------------------------

class FeatureScore(BaseModel):
    name: str = Field(description="The name of the feature being scored.")
    weight: float = Field(description="The weight assigned to this feature.")
    score: float = Field(description="The score (0.0 to 1.0) for how well the candidate matches this feature.")

class CandidateEvaluation(BaseModel):
    feature_scores: List[FeatureScore] = Field(description="A list of scores for each required feature.")
    affinity_score: float = Field(description="The weighted average of the feature scores.")

# -------------------------------
# 2️⃣ Load environment variables and Initialize Client
# -------------------------------

# Load environment variables
load_dotenv()

# Configure Google Cloud Project
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# Initialize Vertex AI client (or use genai.Client() for the Gemini API)
# Using 'genai.Client()' without arguments will look for GOOGLE_API_KEY, 
# but since you are using GOOGLE_CLOUD_PROJECT/LOCATION, the Vertex AI client is appropriate.
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)

def evaluate_candidate(ID: int, requirements: dict) -> CandidateEvaluation:
    folder = f"data/candidate_{ID}/"
    cv_path = os.path.join(folder, f"cv_{ID}.pdf")
    linkedin_path = os.path.join(folder, f"linkedin_post_{ID}.json")

    # --- Load CV text ---
    cv_text = ""
    if os.path.exists(cv_path):
        with open(cv_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                cv_text += page.extract_text() + "\n"
    else:
        cv_text = "CV file not found."

    # --- Load LinkedIn JSON ---
    linkedin_text = ""
    if os.path.exists(linkedin_path):
        with open(linkedin_path, "r") as f:
            linkedin_data = json.load(f)
        linkedin_text = json.dumps(linkedin_data, indent=2)
    else:
        linkedin_text = "LinkedIn data file not found."

    # --- Combine both sources ---
    combined_text = f"=== CV ===\n{cv_text}\n\n=== LinkedIn Data ===\n{linkedin_text}"


    # --- Define prompt (simplified) ---
    prompt = (
        "You are an expert technical recruiter. "
        "Analyze the following candidate information and provided requirements. "
        "For each feature in the requirements, assign a score between 0.0 and 1.0 representing how well the candidate matches it. "
        "Finally, compute the weighted average of the scores for the 'affinity_score'."
        f"\n\nCandidate Information:\n{combined_text}"
        f"\n\nRequirements:\n{json.dumps(requirements, indent=2)}"
    )

    # --- Call the LLM with structured output config ---
    
    # Define the generation configuration for JSON output based on the Pydantic model
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_json_schema=CandidateEvaluation.model_json_schema(), # Use the Pydantic model schema
        # Optional: Set a low temperature for more deterministic scoring
        temperature=0.0
    )

    # Use a Gemini model appropriate for Vertex AI
    model_name = "gemini-2.5-flash" 

    response = client.models.generate_content(
        model=model_name,
        contents=[prompt],
        config=config,
    )
    
    # --- Parse with Pydantic (handled automatically by client, available in .parsed) ---
    try:
        # The genai client automatically parses the JSON response into the Pydantic model
        result: CandidateEvaluation = response.parsed
    except Exception as e:
        print("Error parsing LLM output, raw response text:", response.text)
        raise

    return result

if __name__ == "__main__":
    requirements = {
        "features": [
            {"name": "Machine Learning", "weight": 0.4},
            {"name": "Python programming", "weight": 0.3},
            {"name": "Communication skills", "weight": 0.2},
            {"name": "Leadership", "weight": 0.1}
        ]
    }

    print("Executing LLM call with Candidate ID 1...")
    try:
        # This calls the function that should return a CandidateEvaluation object
        result = evaluate_candidate(1, requirements) 
        
        print("✅ Successfully generated and parsed Pydantic object:")
        # This is the correct Pydantic V2 method call
        print(result) 
        
    except Exception as e:
        print(f"❌ An error occurred during evaluation or output printing.")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
