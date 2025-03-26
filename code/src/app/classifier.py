import re
import json
import requests
from typing import Dict, Optional
from app.config_loader import CONFIG

HUGGINGFACE_API_KEY = CONFIG["HUGGINGFACE_API_KEY"]
CLASSIFICATION_MODEL = CONFIG["huggingface_classification_model"]

class DynamicClassifier:
    def __init__(self):
        self.cache = {}
        # Predefined categories for fallback
        self.categories = [
            "Loan Modification", "Payment Issue", "Fraud Report",
            "Document Request", "General Inquiry", "Account Closure"
        ]

    def classify(self, email_body: str) -> Dict[str, str]:
        """Classifies email content with robust error handling"""
        try:
            # First try quick pattern matching
            quick_result = self._quick_pattern_match(email_body)
            if quick_result:
                return quick_result
            
            # Then try proper zero-shot classification
            return self._zero_shot_classification(email_body)
            
        except Exception as e:
            print(f"Classification error: {str(e)}")
            return self._fallback_classification(email_body)

    def _quick_pattern_match(self, email_body: str) -> Optional[Dict[str, str]]:
        """Fast regex-based classification"""
        patterns = {
            "Loan Modification": r"modif(y|ication)\s*loan|adjust\s*repayment",
            "Payment Issue": r"payment\s*(dispute|missing|not\s*reflected)",
            "Fraud Report": r"unauthorized\s*transaction|account\s*compromised",
            "Document Request": r"send\s*doc|attach\s*form|submit\s*verification",
            "Account Closure": r"close\s*account|loan\s*closure"
        }
        
        for req_type, pattern in patterns.items():
            if re.search(pattern, email_body, re.IGNORECASE):
                return {
                    "request_type": req_type,
                    "sub_request_type": self._get_subtype(req_type, email_body)
                }
        return None

    def _get_subtype(self, main_type: str, text: str) -> str:
        """Determine subtype based on main category"""
        subtypes = {
            "Loan Modification": {
                "rate": r"interest\s*rate",
                "term": r"loan\s*term",
                "payment": r"payment\s*plan"
            },
            "Payment Issue": {
                "missing": r"payment\s*missing",
                "dispute": r"dispute|incorrect\s*amount",
                "late": r"late\s*payment"
            }
        }
        if main_type in subtypes:
            for subtype, pattern in subtypes[main_type].items():
                if re.search(pattern, text, re.IGNORECASE):
                    return subtype
        return "General"

    def _zero_shot_classification(self, email_body: str) -> Dict[str, str]:
        """Proper zero-shot classification API call"""
        url = f"https://api-inference.huggingface.co/models/{CLASSIFICATION_MODEL}"
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "inputs": email_body[:1024],  # Truncate to avoid token limits
            "parameters": {
                "candidate_labels": self.categories,
                "multi_label": False
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            return {
                "request_type": result["labels"][0],
                "sub_request_type": self._get_subtype(result["labels"][0], email_body)
            }
        else:
            raise Exception(f"API error {response.status_code}: {response.text}")

    def _fallback_classification(self, email_body: str) -> Dict[str, str]:
        """Final fallback when all else fails"""
        return {
            "request_type": "General Inquiry",
            "sub_request_type": "Other"
        }

# Singleton with error handling
try:
    classifier = DynamicClassifier()
except Exception as e:
    print(f"Classifier init failed: {str(e)}")
    classifier = None

def classify_email(email_body: str) -> Dict[str, str]:
    """Public interface"""
    if not classifier:
        return {"request_type": "Unclassified", "sub_request_type": "Other"}
    return classifier.classify(email_body)