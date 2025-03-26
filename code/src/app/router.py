import requests
from app.config_loader import CONFIG

HUGGINGFACE_API_KEY = CONFIG["HUGGINGFACE_API_KEY"]
ROUTING_TEAMS = CONFIG["routing_teams"]

def auto_route(request_type, email_text):
    """
    Determines the correct team based on request type and email content.
    """
    # Ensure request_type is a string
    if not isinstance(request_type, str):
        request_type = str(request_type)

    # Simple rule-based routing
    routing_rules = {
        "Loan Modification": "Loan Processing Team",
        "Fraud Report": "Fraud Investigation Team",
        "Document Request": "Document Review Team",
        "General Inquiry": "Customer Support",
        "Unknown": "Customer Support"  # Default fallback
    }
    
    # First try exact match
    if request_type in routing_rules:
        return routing_rules[request_type]
    
    # Then try case-insensitive partial match
    request_type_lower = request_type.lower()
    for key in routing_rules:
        if key.lower() in request_type_lower:
            return routing_rules[key]
    
    # Finally, try keyword matching in email text
    email_lower = email_text.lower()
    if "loan" in email_lower or "modification" in email_lower:
        return "Loan Processing Team"
    elif "fraud" in email_lower:
        return "Fraud Investigation Team"
    elif "document" in email_lower or "documents" in email_lower:
        return "Document Review Team"
    
    # Ultimate fallback
    return "Customer Support"