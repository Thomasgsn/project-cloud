import os
from pathlib import Path


# Point d'entrée central pour éviter de disperser les chemins et paramètres
# dans plusieurs fichiers.
BASE_DIR = Path(__file__).resolve().parent.parent
# Dossier de données persistantes générées par l'application.
DATA_DIR = BASE_DIR / "data"
# Documents `.txt` déposés par l'utilisateur depuis l'interface.
DOCUMENTS_DIR = DATA_DIR / "documents"
# Base Chroma persistée localement sur disque.
CHROMA_DIR = DATA_DIR / "chroma"
# Corpus fourni par le sujet, disponible par défaut sans upload.
DEFAULT_CORPUS_PATH = BASE_DIR / "corpus_de_travail.txt"

# Paramètres RAG recommandés dans l'énoncé.
CHUNK_SIZE = 850
CHUNK_OVERLAP = 120
TOP_K = 4
# Nom unique de la collection vectorielle utilisée dans Chroma.
COLLECTION_NAME = "obama-fr"
# Modèle appelé via Ollama pour générer la réponse finale.
OLLAMA_MODEL = "qwen2.5:0.5b"
# Endpoint HTTP d'Ollama, configurable pour fonctionner en local ou dans Docker.
OLLAMA_API_URL = os.getenv(
    "OLLAMA_API_URL",
    "http://localhost:11434/api/generate",
)
