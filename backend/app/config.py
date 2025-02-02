import os
from dotenv import load_dotenv

load_dotenv()

os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "1"

API_KEY = os.getenv("API_KEY")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")

PDF_STORAGE_DIR = "./data/pdfs"
