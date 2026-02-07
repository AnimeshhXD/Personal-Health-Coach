"""
LLM Client for ScaleDown AI Integration

This module handles real API calls to ScaleDown AI for generating
personalized health recommendations while maintaining fallback safety.
"""

import logging
from typing import Optional
import requests
import hashlib
import base64
import json
import re
from config.settings import SCALEDOWN_API_KEY, SCALEDOWN_BASE_URL

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_api_key_valid() -> bool:
    """
    Validate if the API key is properly configured.

    Returns:
        True if API key appears valid, False otherwise
    """
    logger.info(f"Checking API key validity: '{SCALEDOWN_API_KEY}'")

    if not SCALEDOWN_API_KEY:
        logger.warning("No API key configured")
        return False

    # Check for exact match with common placeholder patterns
    placeholder_keys = [
        "your_api_key_here",
        "set_your_api_key",
        "example_key",
        "test_key",
        "demo_key",
        "sk-your-api-key-here"
    ]

    api_key_clean = SCALEDOWN_API_KEY.strip().lower()
    logger.info(f"Cleaned API key: '{api_key_clean}'")

    if api_key_clean in [pk.lower() for pk in placeholder_keys]:
        logger.warning("Placeholder API key detected")
        return False

    # Check for common placeholder patterns within the key
    if any(pattern.lower() in api_key_clean for pattern in ["your_api_key", "set_your", "example_key", "test_key", "demo_key"]):
        logger.warning("Invalid API key pattern detected")
        return False

    # Basic format validation (ScaleDown keys typically have specific format)
    if len(SCALEDOWN_API_KEY) < 20:
        logger.warning("API key too short")
        return False

    # Check if it looks like a real API key (alphanumeric with some special chars)
    import re
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', SCALEDOWN_API_KEY):
        logger.warning("API key format invalid")
        return False

    logger.info("API key appears valid")
    return True


def generate_llm_recommendation(prompt: str) -> str:
    """
    Generate health recommendations using ScaleDown AI API.

    Args:
        prompt: The structured prompt containing health twin summary and budget mode

    Returns:
        Generated recommendation text from ScaleDown AI

    Raises:
        Exception: If API call fails, allowing graceful fallback to deterministic logic
    """
    # Validate API key before making request
    if not is_api_key_valid():
        error_msg = "Invalid API key configuration"
        logger.error(error_msg)
        raise Exception(error_msg)

    try:
        # Construct API endpoint
        url = f"{SCALEDOWN_BASE_URL}/compress/raw/"

        # Prepare headers
        headers = {
            "x-api-key": SCALEDOWN_API_KEY,
            "Content-Type": "application/json"
        }

        # Prepare payload
        payload = {
            "context": "Generate personalized health recommendations based on health data",
            "prompt": prompt,
            "model": "gpt-4o",
            "scaledown": {
                "rate": "auto"
            }
        }

        # Make HTTPS POST request
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=30)

        # Log HTTP status code
        logger.info(f"HTTP Status Code: {response.status_code}")

        if response.status_code != 200:
            raise Exception(f"API returned status code {response.status_code}: {response.text}")

        # Parse response
        data = response.json()

        # Extract the compressed prompt (which contains the AI-generated recommendations)
        llm_output = data.get('results', {}).get('compressed_prompt', '')

        if not llm_output:
            raise Exception("No LLM output found in API response")

        # Parse the LLM output to extract clean recommendations
        recommendations = _extract_recommendations_from_response(llm_output)

        # Log first 60 characters of output for verification
        logger.info(f"LLM Output Preview: {recommendations[:60]}...")

        return recommendations

    except Exception as e:
        error_msg = f"Error calling ScaleDown API: {str(e)}"
        logger.error(error_msg)
        raise Exception(error_msg)


def _extract_recommendations_from_response(response_text: str) -> str:
    """
    Extract clean, human-readable recommendations from AI response.

    Args:
        response_text: Raw AI response text

    Returns:
        Clean recommendation string formatted as numbered list
    """
    # Remove the context/prompt from the beginning if present
    response_text = response_text.strip()

    # Look for the actual recommendations section
    # Find content after common markers
    markers = ["RECOMMENDATIONS:", "Recommendations:", "Here are", "Based on", "1.", "- "]
    start_pos = len(response_text)

    for marker in markers:
        pos = response_text.find(marker)
        if pos != -1 and pos < start_pos:
            start_pos = pos

    if start_pos < len(response_text):
        response_text = response_text[start_pos:]

    # Split into lines and clean up
    lines = [line.strip() for line in response_text.split('\n') if line.strip()]

    # Extract recommendations (look for numbered items or bullet points)
    recommendations = []
    for line in lines:
        # Skip lines that are just the context or headers
        if any(skip in line.lower() for skip in ["health twin", "budget mode", "detailed health", "recommendation requirements"]):
            continue

        # Remove numbering/bullets and clean up
        clean_line = re.sub(r'^(\d+\.|\-|\•|\*)\s*', '', line.strip())
        if clean_line and len(clean_line) > 10 and not clean_line.startswith(('Generate', 'Based on', 'Provide')):  # Filter out very short lines and prompt remnants
            recommendations.append(clean_line)

    # Format as numbered list
    if recommendations:
        formatted = '\n'.join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations))
        return formatted
    else:
        # Fallback if no clear recommendations found - try to extract meaningful sentences
        sentences = [s.strip() for s in response_text.split('.') if s.strip() and len(s.strip()) > 20]
        if sentences:
            return "1. " + sentences[0] + "."
        else:
            return "1. " + response_text.strip().split('.')[0] + "."
