from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
CHROMA_DIR = DATA_DIR / "chroma"
DEFAULT_CORPUS_PATH = BASE_DIR / "EXAMEN" / "corpus_de_travail.txt"

CHUNK_SIZE = 850
CHUNK_OVERLAP = 120
TOP_K = 4
COLLECTION_NAME = "obama-2013-fr"
OLLAMA_MODEL = "mistral:7b-instruct"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
