import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# Application credentials (secure in production)
USERNAME = os.getenv("APP_USERNAME", "admin")
PASSWORD = os.getenv("APP_PASSWORD", "admin123")

# Default Google Sheet settings
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "data")
