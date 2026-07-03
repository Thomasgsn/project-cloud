from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
from urllib import error, request

from src.config import (
    CHROMA_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    OLLAMA_API_URL,
    OLLAMA_MODEL,
    TOP_K,
)


@dataclass(slots=True)
class Chunk:
    chunk_id: str
    text: str
    source: str
    chunk_index: int


@dataclass(slots=True)
class AnswerResult:
    answer: str
    sources: list[dict[str, Any]]
    used_fallback: bool


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def chunk_text(
    text: str,
    source_name: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[Chunk] = []
    start = 0
    step = chunk_size - chunk_overlap
    chunk_index = 0

    while start < len(cleaned_text):
        end = min(start + chunk_size, len(cleaned_text))
        content = cleaned_text[start:end].strip()
        if content:
            chunks.append(
                Chunk(
                    chunk_id=f"{source_name}-{chunk_index}",
                    text=content,
                    source=source_name,
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1
        if end >= len(cleaned_text):
            break
        start += step

    return chunks


def build_prompt(question: str, chunks: list[dict[str, Any]]) -> str:
    context_lines = []
    for chunk in chunks:
        context_lines.append(
            f"[Source: {chunk['source']} | Passage: {chunk['chunk_index']} | Score: {chunk['score']:.4f}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_lines)
    return (
        "Tu es un assistant RAG. "
        "Réponds uniquement à partir du contexte fourni. "
        "Si l'information n'est pas présente dans le document, dis clairement "
        "\"Je ne trouve pas cette information dans le document fourni.\" "
        "Réponds en français de façon concise.\n\n"
        f"Question : {question}\n\n"
        f"Contexte :\n{context}\n\n"
        "Réponse :"
    )


def _get_embedding_function():
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    return SentenceTransformerEmbeddingFunction(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )


def _get_collection():
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=_get_embedding_function(),
        metadata={"hnsw:space": "cosine"},
    )


def index_document(path: Path) -> dict[str, Any]:
    text = read_text_file(path)
    chunks = chunk_text(text=text, source_name=path.name)
    collection = _get_collection()

    existing = collection.get(where={"source": path.name})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    collection.add(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=[chunk.text for chunk in chunks],
        metadatas=[
            {
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
                "preview": chunk.text[:160],
            }
            for chunk in chunks
        ],
    )

    return {
        "document": path.name,
        "chunk_count": len(chunks),
        "collection": COLLECTION_NAME,
    }


def retrieve_sources(question: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
    collection = _get_collection()
    results = collection.query(
        query_texts=[question],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        score = 1 - float(distance)
        retrieved.append(
            {
                "text": document,
                "source": metadata["source"],
                "chunk_index": metadata["chunk_index"],
                "preview": metadata["preview"],
                "score": score,
            }
        )
    return retrieved


def ask_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = request.Request(
        OLLAMA_API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=90) as response:
            body = json.loads(response.read().decode("utf-8"))
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError("Ollama is unavailable") from exc

    return body.get("response", "").strip()


def build_fallback_answer(question: str, chunks: list[dict[str, Any]]) -> str:
    if not chunks:
        return "Je ne trouve pas cette information dans le document fourni."

    intro = (
        "Ollama n'est pas disponible, voici les passages les plus pertinents "
        "retrouvés pour répondre à la question."
    )
    extracts = "\n".join(
        f"- Passage {chunk['chunk_index']} ({chunk['source']}) : {chunk['text']}"
        for chunk in chunks[:2]
    )
    return f"{intro}\nQuestion : {question}\n{extracts}"


def answer_question(question: str) -> AnswerResult:
    sources = retrieve_sources(question=question, top_k=TOP_K)
    if not sources:
        return AnswerResult(
            answer="Je ne trouve pas cette information dans le document fourni.",
            sources=[],
            used_fallback=False,
        )

    prompt = build_prompt(question=question, chunks=sources)

    try:
        answer = ask_ollama(prompt)
        if not answer:
            answer = "Je ne trouve pas cette information dans le document fourni."
        return AnswerResult(answer=answer, sources=sources, used_fallback=False)
    except RuntimeError:
        return AnswerResult(
            answer=build_fallback_answer(question=question, chunks=sources),
            sources=sources,
            used_fallback=True,
        )
