from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import re
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

EMBEDDING_DIMENSION = 512


@dataclass(slots=True)
class Chunk:
    # Représentation minimale d'un passage indexable.
    chunk_id: str
    text: str
    source: str
    chunk_index: int


@dataclass(slots=True)
class AnswerResult:
    # Objet de sortie unique pour simplifier l'affichage dans Streamlit.
    answer: str
    sources: list[dict[str, Any]]
    used_fallback: bool


def read_text_file(path: Path) -> str:
    # Le corpus est un simple `.txt`, donc une lecture UTF-8 suffit.
    return path.read_text(encoding="utf-8").strip()


def read_pdf_file(path: Path) -> str:
    # Extraction texte simple pour les PDF textuels. Les PDF scannés ne sont
    # pas correctement pris en charge par cette approche.
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    return "\n".join(page for page in pages if page).strip()


def read_document(path: Path) -> str:
    # Point d'entrée unique pour lire un document selon son extension.
    if path.suffix.lower() == ".txt":
        return read_text_file(path)
    if path.suffix.lower() == ".pdf":
        return read_pdf_file(path)
    raise ValueError(f"Format non supporté : {path.suffix}")


def chunk_text(
    text: str,
    source_name: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> list[Chunk]:
    # On compacte les espaces pour obtenir des chunks plus propres et éviter
    # que la vectorisation dépende de retours à la ligne parasites.
    cleaned_text = " ".join(text.split())
    if not cleaned_text:
        return []
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks: list[Chunk] = []
    start = 0
    # Le pas réel entre deux chunks est réduit par l'overlap pour conserver
    # un peu de contexte d'un passage au suivant.
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
    # On injecte explicitement les métadonnées pour que la réponse reste
    # traçable et facile à vérifier pendant la démo.
    context_lines = []
    for chunk in chunks:
        context_lines.append(
            f"[Source: {chunk['source']} | Passage: {chunk['chunk_index']} | Score: {chunk['score']:.4f}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_lines)
    return (
        "Tu es un assistant documentaire. "
        "Réponds uniquement à partir du contexte fourni. "
        "Si l'information n'est pas présente dans le contexte, dis clairement "
        "\"Je ne trouve pas cette information dans le document fourni.\" "
        "Réponds en français de façon concise.\n\n"
        f"Question : {question}\n\n"
        f"Contexte :\n{context}\n\n"
        "Réponse :"
    )


def _tokenize(text: str) -> list[str]:
    # Découpage très simple en mots alphanumériques pour construire
    # des embeddings locaux sans dépendre d'un modèle externe.
    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)


def embed_text(text: str, dimension: int = EMBEDDING_DIMENSION) -> list[float]:
    # Embedding local basé sur du hashing de tokens. C'est moins riche qu'un
    # vrai modèle sémantique, mais stable, rapide et sans dépendance lourde.
    vector = [0.0] * dimension
    for token in _tokenize(text):
        digest = hashlib.md5(token.encode("utf-8")).hexdigest()
        index = int(digest, 16) % dimension
        vector[index] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def embed_texts(texts: list[str], dimension: int = EMBEDDING_DIMENSION) -> list[list[float]]:
    return [embed_text(text, dimension=dimension) for text in texts]


def _get_collection():
    # La collection est persistée sur disque pour éviter de réindexer à chaque
    # redémarrage de l'application.
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def index_document(path: Path) -> dict[str, Any]:
    # Pipeline d'indexation complet : lecture, découpage puis insertion dans Chroma.
    text = read_document(path)
    if not text:
        raise ValueError("Aucun texte exploitable n'a pu être extrait du document.")
    chunks = chunk_text(text=text, source_name=path.name)
    collection = _get_collection()

    # Si on réindexe le même document, on supprime d'abord ses anciens passages
    # pour garder une base cohérente.
    existing = collection.get(where={"source": path.name})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])

    documents = [chunk.text for chunk in chunks]
    collection.add(
        ids=[chunk.chunk_id for chunk in chunks],
        documents=documents,
        embeddings=embed_texts(documents),
        metadatas=[
            {
                "source": chunk.source,
                "chunk_index": chunk.chunk_index,
                "preview": chunk.text[:160],
            }
            for chunk in chunks
        ],
    )

    # Ce résumé est utilisé directement par l'interface pour confirmer l'action.
    return {
        "document": path.name,
        "chunk_count": len(chunks),
        "collection": COLLECTION_NAME,
    }


def retrieve_sources(question: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
    # Recherche vectorielle des passages les plus proches de la question.
    collection = _get_collection()
    results = collection.query(
        query_embeddings=[embed_text(question)],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        # Chroma retourne une distance. On la convertit en score lisible pour l'UI.
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
    # Appel HTTP direct pour éviter d'ajouter un client Ollama dédié.
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
        # On remonte une erreur métier simple, plus facile à gérer dans l'app.
        raise RuntimeError("Ollama is unavailable") from exc

    return body.get("response", "").strip()


def build_fallback_answer(question: str, chunks: list[dict[str, Any]]) -> str:
    # Mode dégradé utile en soutenance si le modèle local n'est pas lancé.
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
    # Étape 1 : récupération documentaire.
    sources = retrieve_sources(question=question, top_k=TOP_K)
    if not sources:
        return AnswerResult(
            answer="Je ne trouve pas cette information dans le document fourni.",
            sources=[],
            used_fallback=False,
        )

    # Étape 2 : construction du prompt enrichi envoyé au LLM.
    prompt = build_prompt(question=question, chunks=sources)

    try:
        # Étape 3 : génération de la réponse finale.
        answer = ask_ollama(prompt)
        if not answer:
            answer = "Je ne trouve pas cette information dans le document fourni."
        return AnswerResult(answer=answer, sources=sources, used_fallback=False)
    except RuntimeError:
        # Si le LLM local n'est pas disponible, l'application reste démontrable.
        return AnswerResult(
            answer=build_fallback_answer(question=question, chunks=sources),
            sources=sources,
            used_fallback=True,
        )
