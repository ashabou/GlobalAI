#!/usr/bin/env python3
"""
Job Feature Weight Analyzer
Analyzes job descriptions and generates candidate evaluation weights.
Technical Mastery is always fixed at 1.0, others are dynamic based on job context.

Using Google Vertex AI with GCP credits.
"""

import os
import sys
import json
import re
from typing import Dict, List, Optional
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

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

# The 10 evaluation dimensions
FEATURES = [
    "Technical Mastery",
    "Discipline & Consistency",
    "Execution Reliability",
    "Cultural Agreeableness",
    "Creative Divergence",
    "Leadership Initiative",
    "Resilience & Grit",
    "Communication Clarity",
    "Team Elevation",
    "Growth Hunger"
]


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


def fetch_company_culture(company_name: str) -> str:
    """
    Fetch company culture information using LLM knowledge.
    
    Args:
        company_name: Name of the company
        
    Returns:
        Company culture information as a string
    """
    if not company_name or not company_name.strip():
        return ""
    
    prompt = f"""Based on your knowledge, provide a brief overview of the company culture and work environment for {company_name}.

Focus on:
- Work culture and values
- Team collaboration style
- Innovation and creativity emphasis
- Leadership expectations
- Work-life balance approach
- Communication style
- Growth and development opportunities

Return a concise paragraph (3-5 sentences) describing the company culture. If you don't have specific information about this company, provide general observations based on the company name and industry if possible, or return "No specific culture information available."
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )
        
        culture_info = response.text.strip()
        return culture_info
    except Exception as e:
        print(f"Warning: Could not fetch company culture information: {e}")
        return ""


def extract_tech_skills(job_description: str) -> List[str]:
    """
    Extract technical skills and technologies mentioned in job description.

    Args:
        job_description: Raw job description text

    Returns:
        List of technical skills/technologies
    """
    prompt = f"""Analyze the following job description and extract all technical skills (technologies, programming languages, frameworks, tools, and other technical competencies) 
    as well as soft skills relevant for performing well in this role.

    Return only a JSON array of strings. Do not include any additional text, explanation, or formatting.

    Example output:
    ["Adaptability", "Creativity", "Python", "Machine Learning", "TensorFlow", "AWS", "SQL"]

Job Description:
{job_description}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )

        # Parse JSON from response
        result = response.text.strip()
        if result.startswith('```json'):
            result = result.split('```json')[1].split('```')[0].strip()
        elif result.startswith('```'):
            result = result.split('```')[1].split('```')[0].strip()

        skills = json.loads(result)
        return skills if isinstance(skills, list) else []
    except Exception as e:
        print(f"Error extracting skills: {e}")
        return []


def generate_feature_weights(job_description: str, tech_skills: List[str], 
                              company_culture: str = "") -> Dict[str, float]:
    """
    Generate weights for all 10 candidate evaluation features.
    Technical Mastery is fixed at 1.0, others are 0.0-1.0 based on job requirements.

    Args:
        job_description: Raw job description text
        tech_skills: List of extracted technical skills
        company_culture: Optional company culture information

    Returns:
        Dictionary mapping feature names to weights (0.0-1.0)
    """
    # Features to weight (excluding Technical Mastery which is fixed)
    features_to_weight = [f for f in FEATURES if f != "Technical Mastery"]

    # Build prompt with optional culture information
    culture_section = ""
    if company_culture and company_culture.strip():
        culture_section = f"""

Company Culture Information:
{company_culture}

Use this culture information to inform your weight assignments. For example:
- If the company values innovation and creativity, increase "Creative Divergence" weight
- If the company emphasizes teamwork, increase "Team Elevation" and "Cultural Agreeableness" weights
- If the company values leadership and initiative, increase "Leadership Initiative" weight
- If the company has a fast-paced, resilient culture, increase "Resilience & Grit" weight
"""

    prompt = f"""You are an expert recruiter analyzing job requirements. Based on this job description,
assign importance weights (0.0 to 1.0) for the following candidate evaluation criteria.

Technical skills identified: {', '.join(tech_skills) if tech_skills else "None specified"}
{culture_section}
Evaluation criteria to weight:
{chr(10).join(f'- {f}' for f in features_to_weight)}

Guidelines:
- 1.0 = Critical for this role
- 0.7-0.9 = Very important
- 0.4-0.6 = Moderately important
- 0.1-0.3 = Nice to have
- 0.0 = Not relevant

Consider:
- Seniority level (junior vs senior)
- Role type (IC vs manager, individual vs team-focused)
- Company stage (startup vs enterprise)
- Technical complexity
- Company culture and values (if provided above)

Return ONLY a JSON object with feature names as keys and weights as values.
Example: {{"Discipline & Consistency": 0.8, "Execution Reliability": 0.9, ...}}

Job Description:
{job_description}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt
        )

        # Parse JSON from response
        result = response.text.strip()
        if result.startswith('```json'):
            result = result.split('```json')[1].split('```')[0].strip()
        elif result.startswith('```'):
            result = result.split('```')[1].split('```')[0].strip()

        weights = json.loads(result)

        # Add fixed Technical Mastery weight
        weights["Technical Mastery"] = 1.0

        # Validate all features are present
        for feature in FEATURES:
            if feature not in weights:
                weights[feature] = 0.5  # Default fallback

        return weights
    except Exception as e:
        print(f"Error generating weights: {e}")
        # Fallback: return default weights
        return {feature: 1.0 if feature == "Technical Mastery" else 0.5
                for feature in FEATURES}


def analyze_job(job_description: str, company_name: Optional[str] = None) -> Dict:
    """
    Complete analysis pipeline: extract skills and generate feature weights.

    Args:
        job_description: Raw job description text
        company_name: Optional company name for culture analysis

    Returns:
        Dictionary with tech_skills, weights, and company culture info
    """
    print("Extracting technical skills...")
    tech_skills = extract_tech_skills(job_description)

    print(f"Found {len(tech_skills)} technical skills")
    
    # Fetch company culture if company name is provided
    company_culture = ""
    if company_name:
        print(f"Fetching company culture information for: {company_name}")
        company_culture = fetch_company_culture(company_name)
        if company_culture:
            print("✓ Company culture information retrieved")
        else:
            print("⚠ No company culture information available")
        print()
    
    print("Generating feature weights...")
    weights = generate_feature_weights(job_description, tech_skills, company_culture)

    result = {
        "tech_skills": tech_skills,
        "weights": weights
    }
    
    if company_name:
        result["company_name"] = company_name
    if company_culture:
        result["company_culture"] = company_culture
    
    return result


def analyze_job_from_url(url: str, company_name: Optional[str] = None) -> Dict:
    """
    Analyze job posting directly from URL.

    Args:
        url: URL of the job posting
        company_name: Optional company name for culture analysis

    Returns:
        Dictionary with url, job_description, tech_skills, weights, and company culture
    """
    print(f"Scraping job description from: {url}")
    print()

    job_description = scrape_job_description(url)

    print(f"✓ Extracted {len(job_description)} characters")
    print()

    print("Extracting technical skills...")
    tech_skills = extract_tech_skills(job_description)

    print(f"✓ Found {len(tech_skills)} technical skills")
    print()

    # Fetch company culture if company name is provided
    company_culture = ""
    if company_name:
        print(f"Fetching company culture information for: {company_name}")
        company_culture = fetch_company_culture(company_name)
        if company_culture:
            print("✓ Company culture information retrieved")
        else:
            print("⚠ No company culture information available")
        print()

    print("Generating feature weights...")
    weights = generate_feature_weights(job_description, tech_skills, company_culture)

    print("✓ Analysis complete")
    print()

    result = {
        "url": url,
        "job_description": job_description,
        "tech_skills": tech_skills,
        "weights": weights
    }
    
    if company_name:
        result["company_name"] = company_name
    if company_culture:
        result["company_culture"] = company_culture
    
    return result


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
        Job analysis result dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
    """
    if project_root is None:
        project_root = get_project_root()
    input_path = project_root / input_file
    
    if not input_path.exists():
            raise FileNotFoundError(
            f"Job analysis file not found: {input_path}\n"
            f"Please run job_requirements_analyzer.py first to generate the analysis."
        )
    
    with open(input_path, 'r') as f:
        return json.load(f)


def display_results(result: Dict):
    """Display analysis results in a formatted way"""
    print()
    print("=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print()

    if "url" in result and result["url"] != "example":
        print(f"Source URL: {result['url']}")
        print()
    
    if "company_name" in result:
        print(f"Company: {result['company_name']}")
        if "company_culture" in result and result["company_culture"]:
            print(f"Company Culture: {result['company_culture'][:200]}...")
        print()

    print("Technical Skills Identified:")
    print("-" * 60)
    for skill in result["tech_skills"]:
        print(f"  • {skill}")
    print()

    print("Feature Weights (Technical Mastery = 1.0 baseline):")
    print("-" * 60)
    for feature in FEATURES:
        weight = result["weights"].get(feature, 0.5)
        bar = "█" * int(weight * 20)
        print(f"  {feature:.<30} {weight:.2f} {bar}")
    print()


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Job Feature Weight Analyzer - Analyzes job postings and generates candidate evaluation weights"
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL of the job posting to analyze"
    )
    parser.add_argument(
        "--company",
        type=str,
        help="Company name for culture analysis"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Job Feature Weight Analyzer")
    print("=" * 60)
    print()

    # Check if URL provided as command line argument
    if args.url:
        # Validate that the argument is actually a URL
        parsed = urlparse(args.url)
        if parsed.scheme in ('http', 'https') and parsed.netloc:
            # Valid URL provided
            print(f"Mode: URL Analysis")
            if args.company:
                print(f"Company: {args.company}")
            print()

            try:
                result = analyze_job_from_url(args.url, company_name=args.company)
            except ValueError as e:
                print(f"Error: {e}")
                print()
                print("Please provide a valid job posting URL")
                sys.exit(1)
        else:
            # Not a valid URL, show error
            print(f"Error: Invalid URL format: {args.url}")
            print()
            print("Please provide a valid URL starting with http:// or https://")
            print()
            print("Usage:")
            print("  python job_requirements_analyzer.py <job_posting_url> [--company COMPANY_NAME]")
            print()
            print("Example:")
            print("  python job_requirements_analyzer.py https://example.com/jobs/senior-engineer --company Google")
            sys.exit(1)
    else:
        # Use example job description for testing
        print("Mode: Example Analysis (no URL provided)")
        if args.company:
            print(f"Company: {args.company}")
        print()

        example_job = """
Senior Machine Learning Engineer

We are seeking a Senior ML Engineer to join our AI research team.

Requirements:
- 5+ years of experience in machine learning and deep learning
- Expert in Python, PyTorch, and TensorFlow
- Experience with distributed training and MLOps
- Strong research background with publications preferred
- Excellent communication skills for cross-functional collaboration
- Self-motivated and able to work independently
- Experience mentoring junior engineers

Responsibilities:
- Design and implement ML models for production
- Collaborate with research team on novel algorithms
- Optimize model performance and scalability
- Lead technical discussions and code reviews
        """

        print("Using example job description:")
        print("-" * 60)
        print(example_job.strip()[:200] + "...")
        print("-" * 60)
        print()

        result = analyze_job(example_job, company_name=args.company)
        result["url"] = "example"

    # Display results
    display_results(result)

    # Export JSON
    output_path = save_job_analysis(result)
    print(f"Full results saved to: {output_path}")
    print()
    print("=" * 60)
    print("Usage:")
    print("  python job_requirements_analyzer.py                    # Use example")
    print("  python job_requirements_analyzer.py <job_posting_url>  # Analyze URL")
    print("  python job_requirements_analyzer.py <job_posting_url> --company COMPANY_NAME  # With company culture")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
