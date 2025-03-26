import os
import json

CONFIG_FILE = "config/config.json"

def load_config():
    """Load the configuration file dynamically."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

CONFIG = load_config()

# ✅ Ensure essential keys exist
if "huggingface_classification_model" not in CONFIG:
    CONFIG["huggingface_classification_model"] = "facebook/bart-large-mnli"  # Default model

if "HUGGINGFACE_API_KEY" not in CONFIG:
    CONFIG["HUGGINGFACE_API_KEY"] = os.getenv("HUGGINGFACE_API_KEY", "")
