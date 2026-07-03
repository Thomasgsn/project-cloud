from src.rag_pipeline import build_fallback_answer, build_prompt, chunk_text


def test_chunk_text_creates_overlapping_chunks():
    text = "a" * 2000
    chunks = chunk_text(text, source_name="sample.txt", chunk_size=800, chunk_overlap=100)

    assert len(chunks) == 3
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1
    assert chunks[0].source == "sample.txt"


def test_build_prompt_mentions_sources_and_question():
    prompt = build_prompt(
        question="Que dit le texte sur l'éducation ?",
        chunks=[
            {
                "source": "corpus.txt",
                "chunk_index": 2,
                "score": 0.88,
                "text": "Le discours mentionne les écoles et les universités.",
            }
        ],
    )

    assert "Que dit le texte sur l'éducation" in prompt
    assert "corpus.txt" in prompt
    assert "Passage: 2" in prompt


def test_build_fallback_answer_returns_extracts():
    answer = build_fallback_answer(
        "Que dit le texte sur le climat ?",
        [
            {
                "source": "corpus.txt",
                "chunk_index": 5,
                "score": 0.81,
                "text": "Le changement climatique est présenté comme une menace.",
            }
        ],
    )

    assert "Ollama n'est pas disponible" in answer
    assert "Passage 5" in answer
