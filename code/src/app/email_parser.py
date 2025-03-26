import os

EMAILS_FOLDER = "emails/"

def get_latest_email():
    """Fetch the latest email file from the emails folder."""
    try:
        files = [f for f in os.listdir(EMAILS_FOLDER) if f.endswith(".txt")]
        if not files:
            return {"error": "No email files found in the folder."}

        # Sort files by creation time and get the latest one
        latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(EMAILS_FOLDER, x)))

        with open(os.path.join(EMAILS_FOLDER, latest_file), "r", encoding="utf-8") as f:
            content = f.readlines()

        # Extract subject from the first line and remove "Subject: " prefix
        subject = content[0].strip().replace("Subject: ", "") if content else "Unknown Subject"

        # Extract email body (everything after the first line)
        body = "\n".join(content[1:]).strip()

        return {"subject": subject, "body": body}

    except Exception as e:
        return {"error": f"Error reading email: {str(e)}"}
