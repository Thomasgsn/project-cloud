from __future__ import annotations

from pathlib import Path

from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from src.document_store import list_available_documents, save_uploaded_document
from src.rag_pipeline import answer_question, index_document


app = FastAPI(title="Mini RAG API", version="1.0.0")


class IndexRequest(BaseModel):
    document_name: str | None = None


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


def _resolve_document(document_name: str | None) -> Path:
    documents = list_available_documents()
    if not documents:
        raise HTTPException(
            status_code=400,
            detail="Aucun document disponible dans data/documents. Uploadez d'abord un fichier.",
        )

    if document_name is None:
        if len(documents) == 1:
            return documents[0]
        raise HTTPException(
            status_code=400,
            detail="Plusieurs documents sont disponibles. Precisez document_name.",
        )

    matching = [path for path in documents if path.name == document_name]
    if not matching:
        raise HTTPException(
            status_code=404,
            detail=f"Document introuvable: {document_name}",
        )
    return matching[0]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict[str, str | int]:
    filename = Path(file.filename or "").name
    if not filename:
        raise HTTPException(status_code=400, detail="Nom de fichier manquant.")

    if Path(filename).suffix.lower() not in {".txt", ".pdf"}:
        raise HTTPException(status_code=400, detail="Formats acceptes: .txt ou .pdf")

    content = await file.read()
    saved_path = save_uploaded_document(filename, content)
    return {
        "filename": saved_path.name,
        "path": str(saved_path),
        "size": len(content),
    }


@app.post("/index")
def index(payload: IndexRequest = Body(default_factory=IndexRequest)) -> dict[str, str | int]:
    document_path = _resolve_document(payload.document_name)
    summary = index_document(document_path)
    return {
        "status": "indexed",
        "document": summary["document"],
        "chunk_count": summary["chunk_count"],
        "collection": summary["collection"],
    }


@app.post("/ask")
def ask(payload: AskRequest) -> dict[str, object]:
    result = answer_question(payload.question)
    return {
        "question": payload.question,
        "answer": result.answer,
        "sources": result.sources,
        "used_fallback": result.used_fallback,
    }
