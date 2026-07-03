from pathlib import Path

from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload(monkeypatch, tmp_path):
    saved_path = tmp_path / "sample.txt"

    def fake_save_uploaded_document(name, content):
        saved_path.write_bytes(content)
        return saved_path

    monkeypatch.setattr("src.api.save_uploaded_document", fake_save_uploaded_document)

    response = client.post(
        "/upload",
        files={"file": ("sample.txt", b"hello world", "text/plain")},
    )

    assert response.status_code == 200
    assert response.json()["filename"] == "sample.txt"
    assert saved_path.read_text(encoding="utf-8") == "hello world"


def test_index(monkeypatch):
    monkeypatch.setattr(
        "src.api.list_available_documents",
        lambda: [Path("/tmp/document.txt")],
    )
    monkeypatch.setattr(
        "src.api.index_document",
        lambda path: {"document": path.name, "chunk_count": 2, "collection": "test"},
    )

    response = client.post("/index", json={"document_name": "document.txt"})

    assert response.status_code == 200
    assert response.json()["status"] == "indexed"
    assert response.json()["chunk_count"] == 2


def test_ask(monkeypatch):
    class DummyResult:
        answer = "Une reponse"
        sources = [{"source": "document.txt", "chunk_index": 0, "score": 0.9, "text": "texte"}]
        used_fallback = False

    monkeypatch.setattr("src.api.answer_question", lambda question: DummyResult())

    response = client.post("/ask", json={"question": "Que dit le texte ?"})

    assert response.status_code == 200
    assert response.json()["answer"] == "Une reponse"
