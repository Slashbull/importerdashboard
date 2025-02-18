import os

# When running on Streamlit Cloud, st.secrets is automatically available.
# Locally, you can still use a .env file if you wish.
# For local testing, you might set a fallback using os.getenv.

# Application credentials
USERNAME = os.getenv("APP_USERNAME", "") or (st.secrets["app"]["username"] if "app" in st.secrets else "admin")
PASSWORD = os.getenv("APP_PASSWORD", "") or (st.secrets["app"]["password"] if "app" in st.secrets else "admin123")

# Google Sheets Configuration
DEFAULT_SHEET_NAME = os.getenv("DEFAULT_SHEET_NAME", "") or (st.secrets["google_sheets"]["default_sheet_name"] if "google_sheets" in st.secrets else "data")
GOOGLE_SHEET_LINK = os.getenv("GOOGLE_SHEET_LINK", "").strip() or (st.secrets["google_sheets"]["google_sheet_link"] if "google_sheets" in st.secrets else "")

# Logging and caching settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "") or (st.secrets["logging"]["log_level"] if "logging" in st.secrets else "INFO")
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", 0) or (st.secrets["logging"]["cache_max_entries"] if "logging" in st.secrets else 50))
