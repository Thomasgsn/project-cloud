from pathlib import Path

from src.config import DEFAULT_CORPUS_PATH, DOCUMENTS_DIR


def ensure_directories() -> None:
    DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_document(name: str, content: bytes) -> Path:
    ensure_directories()
    target = DOCUMENTS_DIR / name
    target.write_bytes(content)
    return target


def list_available_documents() -> list[Path]:
    ensure_directories()
    documents = [path for path in DOCUMENTS_DIR.glob("*.txt") if path.is_file()]
    if DEFAULT_CORPUS_PATH.exists():
        documents.append(DEFAULT_CORPUS_PATH)
    return sorted({path.resolve() for path in documents})
