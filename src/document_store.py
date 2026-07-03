from pathlib import Path

from src.config import DOCUMENTS_DIR


def ensure_directories() -> None:
    # On crée le dossier de dépôt au démarrage pour éviter les erreurs
    # au premier upload.
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_document(name: str, content: bytes) -> Path:
    # Le fichier est enregistré localement pour rester simple et testable
    # sans dépendre d'un service externe type MinIO.
    ensure_directories()
    target = DOCUMENTS_DIR / name
    target.write_bytes(content)
    return target


def list_available_documents() -> list[Path]:
    # L'interface ne propose que les documents réellement déposés dans
    # `data/documents`.
    ensure_directories()
    documents = [
        path
        for extension in ("*.txt", "*.pdf")
        for path in DOCUMENTS_DIR.glob(extension)
        if path.is_file()
    ]
    # Le set évite d'afficher deux fois un même fichier si un doublon existe.
    return sorted({path.resolve() for path in documents})
