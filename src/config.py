import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- LLM Configuration ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# --- Models Configuration ---
LLM_MODEL = "llama-3.3-70b-versatile"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

# --- Vector DB Configuration ---
VECTOR_DB_DIR = "./data/chroma_db"
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 200

# --- Corpus URLs (Groww Mutual Fund Schemes) ---
SCHEME_URLS = [
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
]
