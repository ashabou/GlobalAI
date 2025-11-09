#!/usr/bin/env python3
"""
Job Feature Extraction API
--------------------------
FastAPI service that:
  • scrapes a job description from a URL
  • uses an LLM to extract top N technical + N behavioral features
  • assigns importance weights
  • returns a structured JSON response

Run with:
    uvicorn job_api:app --reload
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
import fastapi as FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure Google Cloud Project
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

if not PROJECT_ID or PROJECT_ID == "your-project-id-here":
    raise ValueError("Please set GOOGLE_CLOUD_PROJECT in .env file with your actual GCP project ID")

# Initialize Vertex AI client
client = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location=LOCATION
)
app = FastAPI(title="Job Feature Extraction API")


# ---------------------------------------------------------------------------
# SCRAPER
# ---------------------------------------------------------------------------


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def scrape_job_description(url: str) -> str:
    """
    Scrape job description text from a URL.

    Args:
        url: URL of the job posting page

    Returns:
        Cleaned job description text

    Raises:
        ValueError: If URL is invalid or scraping fails
    """
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")

    try:
        # Fetch page with a proper user agent
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Try to find job description container (common selectors)
        job_selectors = [
            {'class': 'job-description'},
            {'class': 'description'},
            {'id': 'job-description'},
            {'class': 'posting-description'},
            {'class': 'job-details'},
            {'role': 'article'},
            {'class': 'content'},
        ]

        job_text = None

        # Try each selector
        for selector in job_selectors:
            container = soup.find('div', selector) or soup.find('section', selector)
            if container:
                job_text = container.get_text(separator='\n', strip=True)
                if len(job_text) > 100:  # Minimum viable description
                    break

        # Fallback: get main content or body
        if not job_text or len(job_text) < 100:
            main = soup.find('main') or soup.find('article') or soup.find('body')
            if main:
                job_text = main.get_text(separator='\n', strip=True)

        if not job_text:
            raise ValueError("Could not extract job description from page")

        # Clean up text
        lines = [line.strip() for line in job_text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)

        # Remove excessive whitespace
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

        return cleaned_text

    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}")
    except Exception as e:
        raise ValueError(f"Error scraping page: {e}")



# ---------------------------------------------------------------------------
# LLM-BASED FEATURE EXTRACTION
# ---------------------------------------------------------------------------

def extract_features_with_weights(job_description: str, company: str, n: int = 5) -> Dict:
    """Extract N technical + N behavioral features and assign weights using LLM."""
    prompt = f"""
    You are an expert recruiter and organizational psychologist.

    Analyze the following job description and the company context.

    Extract:
    - The top {n} *technical* skills or competencies (languages, frameworks, tools, domain knowledge).
    - The top {n} *behavioral or psychological* characteristics (soft skills, personality traits, mindset).

    Then assign an *importance weight* between 0.0 and 1.0 for each feature, representing how critical it is for success in this role.

    Return ONLY a valid JSON object with the following structure:

    {{
    "company": "{company}",
    "job_description": "<<FULL JOB TEXT>>",
    "features": ["Python", "Team Collaboration", ...],
    "weights": [1.0, 0.8, ...],
    "types": ["technical", "behavioral", ...]
    }}

    The arrays must be of the same length.
    Do not include any text, comments, or explanations outside the JSON object.

    Job Description:
    {job_description}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
        )
        text = re.sub(r"^```(json)?|```$", "", response.text.strip()).strip()
        result = json.loads(text)
        return result
    except Exception as e:
        raise RuntimeError(f"LLM error: {e}")


# ---------------------------------------------------------------------------
# GLOBAL FUNCTION FOR DIRECT USE
# ---------------------------------------------------------------------------

def analyze_job_from_url(
    url: str,
    company: str,
    n: int = 5,
    output_file: Optional[str] = None,
    project_root: Optional[Path] = None,
) -> Dict:
    """
    Analyze a job posting from a URL and return extracted features and weights.
    
    Args:
        url: URL of the job posting
        company: Company name
        n: Number of technical and behavioral features to extract (default: 5)
        
    Returns:
        Dictionary with the following structure:
        {
            "url": str,
            "company": str,
            "job_description": str,
            "features": List[str],
            "weights": List[float],
            "types": List[str],  # "technical" or "behavioral"
            "weights_dict": Dict[str, float]  # Convenience dict: feature -> weight
        }
    """
    job_description = scrape_job_description(url)
    result = extract_features_with_weights(job_description, company, n)
    
    # Add URL and original job description to result
    result["url"] = url
    result["job_description"] = job_description
    
    # Create a convenience dictionary mapping feature names to weights
    weights_dict = {
        feature: weight 
        for feature, weight in zip(result.get("features", []), result.get("weights", []))
    }
    result["weights_dict"] = weights_dict
    
    # Persist results if requested
    if output_file is None:
        output_file = "data/job_requirements.json"
    try:
        saved_path = save_job_analysis(result, output_file=output_file, project_root=project_root)
        result["saved_path"] = str(saved_path)
    except Exception as e:
        # Attach information but do not fail the analysis
        result["saved_path_error"] = str(e)

    return result


def analyze_job(job_description: str, company: str, n: int = 5) -> Dict:
    """
    Analyze a job description from text and return extracted features and weights.
    
    Args:
        job_description: Job description text
        company: Company name
        n: Number of technical and behavioral features to extract (default: 5)
        
    Returns:
        Dictionary with the same structure as analyze_job_from_url
    """
    result = extract_features_with_weights(job_description, company, n)
    result["url"] = "text_input"
    result["job_description"] = job_description
    
    # Create a convenience dictionary mapping feature names to weights
    weights_dict = {
        feature: weight 
        for feature, weight in zip(result.get("features", []), result.get("weights", []))
    }
    result["weights_dict"] = weights_dict
    
    return result


# ---------------------------------------------------------------------------
# FILE I/O HELPERS
# ---------------------------------------------------------------------------


def save_job_analysis(result: Dict, output_file: str = "data/job_requirements.json", 
                      project_root: Optional[Path] = None) -> Path:
    """
    Save job analysis results to a JSON file.
    
    Args:
        result: Job analysis result dictionary
        output_file: Path to output file (relative to project root)
        project_root: Optional project root path (defaults to auto-detected)
        
    Returns:
        Path to the saved file
    """
    if project_root is None:
        project_root = get_project_root()
    output_path = project_root / output_file
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(result, f, indent=2)
    
    return output_path


def load_job_analysis(input_file: str = "data/job_requirements.json",
                      project_root: Optional[Path] = None) -> Dict:
    """
    Load job analysis results from a JSON file.
    
    Args:
        input_file: Path to input file (relative to project root)
        project_root: Optional project root path (defaults to auto-detected)
        
    Returns:
        Job analysis result dictionary with weights_dict ensured
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if project_root is None:
        project_root = get_project_root()
    input_path = project_root / input_file
    
    if not input_path.exists():
        raise FileNotFoundError(
            f"Job analysis file not found: {input_path}\n"
            f"Please run job analysis first to generate the file."
        )
    
    with open(input_path, 'r') as f:
        result = json.load(f)
    
    # Ensure weights_dict exists for backward compatibility
    if "weights_dict" not in result:
        if "features" in result and "weights" in result:
            result["weights_dict"] = {
                feature: weight 
                for feature, weight in zip(result.get("features", []), result.get("weights", []))
            }
        elif "weights" in result and isinstance(result["weights"], dict):
            result["weights_dict"] = result["weights"]
        else:
            result["weights_dict"] = {}
    
    return result


def display_results(result: Dict):
    """Display analysis results in a formatted way."""
    print()
    print("=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print()
    
    if "url" in result and result["url"] != "text_input":
        print(f"Source URL: {result['url']}")
        print()
    
    if "company" in result:
        print(f"Company: {result['company']}")
        print()
    
    features = result.get("features", [])
    weights = result.get("weights", [])
    types = result.get("types", [])
    
    if features and weights and types:
        print("Extracted Features:")
        print("-" * 60)
        
        # Group by type
        technical_features = [
            (f, w) for f, w, t in zip(features, weights, types) if t == "technical"
        ]
        behavioral_features = [
            (f, w) for f, w, t in zip(features, weights, types) if t == "behavioral"
        ]
        
        if technical_features:
            print("Technical Features:")
            for feature, weight in technical_features:
                bar = "█" * int(weight * 20)
                print(f"  • {feature:.<30} {weight:.2f} {bar}")
            print()
        
        if behavioral_features:
            print("Behavioral Features:")
            for feature, weight in behavioral_features:
                bar = "█" * int(weight * 20)
                print(f"  • {feature:.<30} {weight:.2f} {bar}")
            print()
    else:
        print("No features extracted.")
        print()
    
    print("=" * 60)
    print()


# ---------------------------------------------------------------------------
# FASTAPI ENDPOINT
# ---------------------------------------------------------------------------

class JobRequest(BaseModel):
    url: str
    company: str
    n: Optional[int] = 5


@app.post("/analyze_job")
def analyze_job_endpoint(req: JobRequest):
    """
    POST endpoint that receives:
      {
        "url": "https://...",
        "company": "CompanyName",
        "n": 5
      }
    and returns extracted features and weights.
    """
    try:
        return analyze_job_from_url(req.url, req.company, req.n)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {e}")


# ---------------------------------------------------------------------------
# RUN LOCAL (optional)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    #import uvicorn
    #uvicorn.run(app, host="0.0.0.0", port=8000)
    url = "https://careers.lululemon.com/en_US/careers/JobDetail/Guest-Experience-Lead-Crossgates-Mall/55003"
    company = "Lululemon"
    n = 5
    result = analyze_job_from_url(url, company, n)
    display_results(result)

