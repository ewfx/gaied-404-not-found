import os
import hashlib

PROCESSED_EMAILS_FILE = "emails/processed_emails.txt"

def hash_email_content(email_content):
    """Generate a unique hash for the email body to check for duplicates."""
    return hashlib.sha256(email_content.encode()).hexdigest()

def is_duplicate_email(email_body):
    """Check if the email has already been processed."""
    email_hash = hash_email_content(email_body)

    # Ensure processed_emails.txt exists
    if not os.path.exists(PROCESSED_EMAILS_FILE):
        with open(PROCESSED_EMAILS_FILE, "w") as f:
            f.write("")

    # Read processed email hashes
    with open(PROCESSED_EMAILS_FILE, "r") as f:
        processed_hashes = f.read().splitlines()

    if email_hash in processed_hashes:
        return True  # Duplicate email detected

    # Store hash (without modifying API output)
    with open(PROCESSED_EMAILS_FILE, "a") as f:
        f.write(email_hash + "\n")

    return False
