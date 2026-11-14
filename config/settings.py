import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

# App metadata
APP_TITLE = "AI Web Signal Hunter"
APP_TAGLINE = "Discover Hidden Opportunities Across the Web"
APP_VERSION = "1.0.0"

# AI Provider configurations
DEFAULT_AI_PROVIDER = os.getenv("DEFAULT_AI_PROVIDER", "groq").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Crawler settings
MAX_PAGES_DEFAULT = int(os.getenv("MAX_PAGES_DEFAULT", "25"))
CRAWL_TIMEOUT_SECONDS = int(os.getenv("CRAWL_TIMEOUT_SECONDS", "12"))
CRAWL_DELAY_SECONDS = float(os.getenv("CRAWL_DELAY_SECONDS", "0.8"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "AI-Web-Signal-Hunter/1.0 (+https://github.com/internship/ai-web-signal-hunter; research bot)"
)

# Opportunity score weights (normalized 0 to 1)
WEIGHT_RELEVANCE = 0.30
WEIGHT_URGENCY = 0.25
WEIGHT_CONFIDENCE = 0.20
WEIGHT_FREQUENCY = 0.15
WEIGHT_RECENCY = 0.10

# Database path
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_PATH = DATA_DIR / "signals.db"

# Valid signal categories as specified in the assignment
VALID_CATEGORIES = [
    "Pain Points",
    "Demand Signals",
    "Feature Requests",
    "Pricing Concerns",
    "Competitor Activity",
    "Irrelevant Content",
]

# Actionable categories (excluding Irrelevant Content)
USEFUL_CATEGORIES = [c for c in VALID_CATEGORIES if c != "Irrelevant Content"]
