import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Application credentials (secure these in production)
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "admin123")

# Default Google Sheet settings
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "data")
# If provided (non‑empty), the app will automatically load data from this Google Sheet.
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK", "https://docs.google.com/spreadsheets/d/1voF3obTyEOxwoFumDkMv897BaT5vnbCBujfRFyZ52NI/edit?usp=sharing").strip()
