from pathlib import Path

import streamlit as st

from src.document_store import list_available_documents, save_uploaded_document
from src.rag_pipeline import AnswerResult, answer_question, index_document


st.set_page_config(page_title="RAG Obama 2013", layout="wide")
st.title("Mini application RAG sur le discours de Barack Obama (2013)")
st.caption("Chargement, indexation, question-réponse et affichage des sources.")


def render_sources(result: AnswerResult) -> None:
    st.subheader("Sources utilisées")
    for source in result.sources:
        with st.expander(
            f"{source['source']} | passage {source['chunk_index']} | score {source['score']:.3f}"
        ):
            st.write(source["text"])


with st.sidebar:
    st.header("Document")
    uploaded = st.file_uploader("Charger un fichier .txt", type=["txt"])
    if uploaded is not None:
        path = save_uploaded_document(uploaded.name, uploaded.getvalue())
        st.success(f"Document enregistré : {path.name}")

    documents = list_available_documents()
    if not documents:
        st.warning("Aucun document .txt disponible.")
        selected_document = None
    else:
        selected_document = st.selectbox(
            "Sélectionner un document à indexer",
            options=documents,
            format_func=lambda path: Path(path).name,
        )

    if st.button("Indexer le document", disabled=selected_document is None):
        try:
            summary = index_document(Path(selected_document))
        except Exception as exc:
            st.error(f"Échec de l'indexation : {exc}")
        else:
            st.success(
                f"Indexation terminée : {summary['chunk_count']} passages dans {summary['collection']}."
            )

st.subheader("Poser une question")
question = st.text_input(
    "Exemple : Que dit le discours sur l'éducation ou la classe moyenne ?"
)

if st.button("Obtenir une réponse", type="primary", disabled=not question.strip()):
    try:
        result = answer_question(question.strip())
    except Exception as exc:
        st.error(
            "La recherche ou la génération a échoué. "
            f"Vérifiez que le document a été indexé. Détail : {exc}"
        )
    else:
        st.subheader("Réponse")
        st.write(result.answer)
        if result.used_fallback:
            st.info("Réponse générée en mode dégradé : Ollama n'était pas disponible.")
        render_sources(result)
