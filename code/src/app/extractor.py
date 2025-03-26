import requests
import json
import re
from typing import Dict, Any
from app.config_loader import CONFIG

HUGGINGFACE_API_KEY = CONFIG["HUGGINGFACE_API_KEY"]
MODEL_NAME = CONFIG["huggingface_model"]

def extract_dynamic_attributes(email_body: str) -> Dict[str, Any]:
    """
    Robust extraction with improved JSON parsing from AI responses
    """
    url = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Extract ALL key information from this email in JSON format ONLY. Follow this structure:
    {{
      "transaction": {{
        "type": "<fraud|payment|etc>",
        "amount": "$X.XX",
        "date": "Month Day, Year",
        "account_name": "string",
        "account_number": "string"
      }},
      "actions": ["list", "of", "requested", "actions"],
      "contact": {{
        "name": "string",
        "email": "string",
        "phone": "string"
      }},
      "urgency": "low/medium/high"
    }}

    Email:
    {email_body[:3000]}  # Truncate to avoid token limits
    """

    try:
        response = requests.post(
            url,
            headers=headers,
            json={"inputs": prompt, "parameters": {"return_full_text": False}},
            timeout=30
        )

        if response.status_code == 200:
            return _parse_ai_response(response.json())
        return {"error": f"API error: {response.status_code}"}

    except Exception as e:
        return {"error": f"Extraction failed: {str(e)}"}

def _parse_ai_response(ai_response) -> Dict[str, Any]:
    """Robust parsing of AI response with multiple fallback methods"""
    try:
        # Handle different response formats
        if isinstance(ai_response, list):
            text = ai_response[0]["generated_text"]
        else:
            text = ai_response.get("generated_text", "")
        
        # Method 1: Try direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Method 2: Extract JSON from markdown code blocks
        code_block = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
        if code_block:
            return json.loads(code_block.group(1))
        
        # Method 3: Extract innermost JSON
        json_match = re.search(r'\{[^{}]*\}', text)
        if json_match:
            return json.loads(json_match.group(0))
        
        # Final fallback: Manual extraction
        return _manual_extraction(text)
    
    except Exception as e:
        return {"error": f"Response parsing failed: {str(e)}"}

def _manual_extraction(text: str) -> Dict[str, Any]:
    """Fallback manual extraction when JSON parsing fails"""
    result = {}
    
    # Extract common patterns
    if amount := re.search(r'\$[\d,]+\.?\d{0,2}', text):
        result.setdefault("transaction", {})["amount"] = amount.group(0)
    if date := re.search(r'[A-Za-z]+\s\d{1,2},?\s\d{4}', text):
        result.setdefault("transaction", {})["date"] = date.group(0)
    
    return result if result else {"error": "No extractable data found"}