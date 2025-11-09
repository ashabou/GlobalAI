#!/usr/bin/env python3
"""
Profile Agent Module
Evaluates individual candidates against job requirements using LLM.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

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

def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def load_pdf_text(file_path: Path) -> str:
    """
    Extract text from a PDF file.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text from the PDF
    """
    try:
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF {file_path.name}: {str(e)}"


def load_json_text(file_path: Path) -> str:
    """
    Load and format JSON file as text.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Formatted JSON text
    """
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return f"Error reading JSON {file_path.name}: {str(e)}"


def load_text_file(file_path: Path) -> str:
    """
    Load text from a text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File contents as string
    """
    try:
        with open(file_path, "r", encoding='utf-8') as f:
            content = f.read()
        return content.strip()
    except Exception as e:
        return f"Error reading text file {file_path.name}: {str(e)}"


def scan_candidate_documents(candidate_dir: Path) -> Dict[str, List]:
    """
    Scan candidate directory for all documents and load their content.
    
    Args:
        candidate_dir: Path to the candidate directory
        
    Returns:
        Dictionary mapping document types to their content lists.
        Keys: 'pdfs', 'jsons', 'texts', 'all_content'
        Each list contains dicts with 'filename' and 'content' keys.
    """
    documents = {
        'pdfs': [],
        'jsons': [],
        'texts': [],
        'all_content': []
    }
    
    if not candidate_dir.exists():
        return documents
    
    # Scan for all files in the directory
    for file_path in candidate_dir.iterdir():
        if not file_path.is_file():
            continue
            
        file_name = file_path.name.lower()
        
        # Process PDF files
        if file_path.suffix.lower() == '.pdf':
            content = load_pdf_text(file_path)
            documents['pdfs'].append({
                'filename': file_path.name,
                'content': content
            })
            documents['all_content'].append({
                'filename': file_path.name,
                'type': 'PDF',
                'content': content
            })
        
        # Process JSON files
        elif file_path.suffix.lower() == '.json':
            content = load_json_text(file_path)
            documents['jsons'].append({
                'filename': file_path.name,
                'content': content
            })
            documents['all_content'].append({
                'filename': file_path.name,
                'type': 'JSON',
                'content': content
            })
        
        # Process text files
        elif file_path.suffix.lower() in ['.txt', '.md', '.rtf']:
            content = load_text_file(file_path)
            documents['texts'].append({
                'filename': file_path.name,
                'content': content
            })
            documents['all_content'].append({
                'filename': file_path.name,
                'type': 'TEXT',
                'content': content
            })
    
    return documents


def format_candidate_information(documents: Dict[str, str]) -> str:
    """
    Format all candidate documents into a single text string for the LLM.
    
    Args:
        documents: Dictionary of scanned documents
        
    Returns:
        Formatted text containing all candidate information
    """
    if not documents['all_content']:
        return "No candidate documents found in the directory."
    
    formatted_sections = []
    
    # Add PDFs section
    if documents['pdfs']:
        formatted_sections.append("=== PDF Documents (CVs, Resumes, etc.) ===")
        for pdf in documents['pdfs']:
            formatted_sections.append(f"\n--- {pdf['filename']} ---\n{pdf['content']}")
        formatted_sections.append("")
    
    # Add JSONs section
    if documents['jsons']:
        formatted_sections.append("=== JSON Documents (LinkedIn, Portfolio, etc.) ===")
        for json_file in documents['jsons']:
            formatted_sections.append(f"\n--- {json_file['filename']} ---\n{json_file['content']}")
        formatted_sections.append("")
    
    # Add text files section
    if documents['texts']:
        formatted_sections.append("=== Text Documents ===")
        for text_file in documents['texts']:
            formatted_sections.append(f"\n--- {text_file['filename']} ---\n{text_file['content']}")
        formatted_sections.append("")
    
    return "\n".join(formatted_sections)


def evaluate_candidate(ID: int, requirements: dict, project_root: Path = None) -> CandidateEvaluation:
    """
    Evaluate a single candidate against job requirements.
    Analyzes all available documents in the candidate's folder.
    
    Args:
        ID: Candidate ID
        requirements: Dictionary containing requirements with features and weights
        project_root: Optional project root path (defaults to auto-detected)
        
    Returns:
        CandidateEvaluation object with feature scores and affinity score
        
    Raises:
        ValueError: If no documents are found in the candidate directory
    """
    if project_root is None:
        project_root = get_project_root()
    
    candidate_dir = project_root / "data" / f"candidate_{ID}"
    
    # Scan for all documents in the candidate directory
    documents = scan_candidate_documents(candidate_dir)
    
    # Check if any documents were found
    if not documents['all_content']:
        raise ValueError(
            f"No documents found in candidate directory: {candidate_dir}\n"
            f"Please ensure the directory contains at least one document (PDF, JSON, or text file)."
        )
    
    # Format all documents into a single text string
    combined_text = format_candidate_information(documents)
    
    # Create document summary for the prompt
    doc_summary = []
    if documents['pdfs']:
        doc_summary.append(f"{len(documents['pdfs'])} PDF document(s)")
    if documents['jsons']:
        doc_summary.append(f"{len(documents['jsons'])} JSON document(s)")
    if documents['texts']:
        doc_summary.append(f"{len(documents['texts'])} text document(s)")
    document_summary = ", ".join(doc_summary)


    # --- Define prompt ---
    prompt = (
        "You are an expert technical recruiter. "
        "Analyze the following candidate information from all available documents and evaluate against the provided requirements. "
        f"The candidate information is compiled from {document_summary} found in their directory. "
        "For each feature in the requirements, assign a score between 0.0 and 1.0 representing how well the candidate matches it. "
        "Consider all available information from CVs, resumes, LinkedIn profiles, portfolios, or any other documents provided. "
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
        # The genai client may return a dict or a Pydantic model
        parsed_response = response.parsed
        
        # Convert to Pydantic model if it's a dict
        if isinstance(parsed_response, dict):
            # Convert dict to Pydantic model
            result = CandidateEvaluation(**parsed_response)
        elif isinstance(parsed_response, CandidateEvaluation):
            # Already a Pydantic model
            result = parsed_response
        else:
            # Try to parse from JSON text if parsed is not working
            try:
                json_text = response.text.strip()
                # Remove markdown code blocks if present
                if json_text.startswith('```json'):
                    json_text = json_text.split('```json')[1].split('```')[0].strip()
                elif json_text.startswith('```'):
                    json_text = json_text.split('```')[1].split('```')[0].strip()
                
                parsed_dict = json.loads(json_text)
                result = CandidateEvaluation(**parsed_dict)
            except Exception as json_error:
                print(f"Error parsing JSON from response text: {json_error}")
                print(f"Raw response text: {response.text}")
                raise
                
    except Exception as e:
        print(f"Error parsing LLM output: {e}")
        print(f"Response type: {type(response.parsed)}")
        print(f"Raw response text: {response.text}")
        # Try fallback: parse from text
        try:
            json_text = response.text.strip()
            if json_text.startswith('```json'):
                json_text = json_text.split('```json')[1].split('```')[0].strip()
            elif json_text.startswith('```'):
                json_text = json_text.split('```')[1].split('```')[0].strip()
            parsed_dict = json.loads(json_text)
            result = CandidateEvaluation(**parsed_dict)
        except Exception as fallback_error:
            print(f"Fallback parsing also failed: {fallback_error}")
            raise e

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
