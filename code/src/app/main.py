from fastapi import FastAPI
from app.email_parser import get_latest_email
from app.classifier import classify_email
from app.extractor import extract_dynamic_attributes
from app.duplicate_checker import is_duplicate_email

# Initialize FastAPI app first
app = FastAPI()

@app.get("/process_latest_email")
async def process_latest_email():
    """
    Processes the latest email and returns classification and extracted attributes
    """
    email_data = get_latest_email()
    
    if "error" in email_data:
        return email_data

    # Handle subject extraction properly
    subject_lines = email_data["subject"].split('\n')
    subject = subject_lines[0].replace("Subject: ", "") if subject_lines else "No Subject"
    body = email_data["body"]

    if is_duplicate_email(body):
        return {"error": f"Duplicate email detected: {subject}"}

    extracted_attributes = extract_dynamic_attributes(body)
    classification = classify_email(body)

    return {
        "classification": classification,
        "extracted_attributes": extracted_attributes
    }

# For debugging - can be removed in production
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)