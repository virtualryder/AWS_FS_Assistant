import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent
DOCS_PATH = str(BASE_DIR / "docs")

# PostgreSQL (Railway injects DATABASE_URL automatically)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = "claude-sonnet-4-6"
MAX_TOKENS = 16000   # sub-agent research phases; synthesis uses same budget

# Tavily (web search for discovery briefs)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ChromaDB collection name (legacy — pgvector is primary)
COLLECTION_NAME = "aws_finserv_docs"

# Embeddings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Chunking
CHUNK_SIZE = 800       # characters
CHUNK_OVERLAP = 100    # characters

# Retrieval — increased for financial services (more context = better compliance analysis)
TOP_K = 10

# Scraping
REQUEST_DELAY = 0.75   # seconds between requests
REQUEST_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
MIN_CONTENT_LENGTH = 300  # skip pages shorter than this

# Application branding
APP_NAME = "AWS Financial Services Assistant"
APP_SUBTITLE = "AWS Financial Services Assistant · Compliance-Validated Architecture Design"
