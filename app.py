from pathlib import Path

import streamlit as st

from src.config import DEFAULT_CORPUS_PATH
from src.document_store import list_available_documents, save_uploaded_document
from src.rag_pipeline import AnswerResult, answer_question, index_document


# Configuration générale de la page Streamlit.
st.set_page_config(page_title="RAG Obama 2013", layout="wide")
st.title("Mini application RAG sur le discours de Barack Obama (2013)")
st.caption("Chargement, indexation, question-réponse et affichage des sources.")


def render_sources(result: AnswerResult) -> None:
    # Chaque source est affichée dans un bloc repliable pour garder l'interface lisible.
    st.subheader("Sources utilisées")
    for source in result.sources:
        with st.expander(
            f"{source['source']} | passage {source['chunk_index']} | score {source['score']:.3f}"
        ):
            st.write(source["text"])


with st.sidebar:
    # La barre latérale regroupe toute la partie préparation du corpus.
    st.header("Document")
    uploaded = st.file_uploader("Charger un fichier .txt ou .pdf", type=["txt", "pdf"])
    if uploaded is not None:
        path = save_uploaded_document(uploaded.name, uploaded.getvalue())
        st.success(f"Document enregistré : {path.name}")

    # L'utilisateur peut importer un document ou copier manuellement le corpus
    # du sujet dans `data/documents`.
    st.caption(f"Corpus fourni disponible ici : {DEFAULT_CORPUS_PATH}")
    documents = list_available_documents()
    if not documents:
        st.warning("Aucun document .txt ou .pdf disponible.")
        selected_document = None
    else:
        selected_document = st.selectbox(
            "Sélectionner un document à indexer",
            options=documents,
            format_func=lambda path: Path(path).name,
        )

    if st.button("Indexer le document", disabled=selected_document is None):
        try:
            # L'indexation crée ou met à jour la collection vectorielle locale.
            summary = index_document(Path(selected_document))
        except Exception as exc:
            st.error(f"Échec de l'indexation : {exc}")
        else:
            st.success(
                f"Indexation terminée : {summary['chunk_count']} passages dans {summary['collection']}."
            )

# Partie principale : question utilisateur puis restitution de la réponse.
st.subheader("Poser une question")
question = st.text_input(
    "Exemple : Que dit le discours sur l'éducation ou la classe moyenne ?"
)

if st.button("Obtenir une réponse", type="primary", disabled=not question.strip()):
    try:
        # Toute la logique RAG est encapsulée côté backend Python.
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
            # Message explicite pour signaler qu'on affiche un résultat sans LLM.
            st.info("Réponse générée en mode dégradé : Ollama n'était pas disponible.")
        render_sources(result)
