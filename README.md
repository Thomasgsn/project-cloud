# Mini projet RAG Cloud

Application RAG légère construite pour répondre à des questions à partir du corpus fourni dans `EXAMEN/corpus_de_travail.txt` (discours de Barack Obama, 2013).

## Objectif

L'application permet de :

- charger un fichier `.txt` ou utiliser le corpus fourni ;
- indexer le document en passages courts ;
- vectoriser les passages avec un modèle d'embeddings multilingue ;
- rechercher les passages les plus proches d'une question ;
- générer une réponse en français ;
- afficher les sources utilisées.

Chaîne RAG utilisée :

`Document -> Découpage -> Embeddings -> Base vectorielle -> Recherche -> Prompt enrichi -> Réponse + sources`

## Choix techniques

- Interface : `Streamlit`
- Base vectorielle : `ChromaDB`
- Embeddings : `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- Génération : `Ollama` en local via HTTP
- Stockage du document : local (`data/documents/`)

MinIO n'a pas été mis en place pour garder une version simple, testable rapidement et compatible avec un environnement local ou Codespaces sans services supplémentaires. Le stockage local remplit ici le même rôle pour le TP.

## Structure

```text
app.py
src/
  config.py
  document_store.py
  rag_pipeline.py
tests/
.github/workflows/ci.yml
```

## Installation

Prérequis :

- Python 3.11+
- Ollama installé localement

Créer l'environnement puis installer les dépendances :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancer Ollama

Installer Ollama puis récupérer un modèle léger, par exemple :

```bash
ollama pull mistral:7b-instruct
ollama serve
```

Le projet appelle par défaut le modèle `mistral:7b-instruct` sur `http://localhost:11434`.

Si Ollama n'est pas disponible, l'application reste utilisable en mode dégradé : elle affiche les passages retrouvés les plus pertinents au lieu d'une réponse générée complète.

## Lancer l'application

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Puis ouvrir l'interface dans le navigateur.

## Utilisation

1. Charger un fichier `.txt` ou sélectionner `corpus_de_travail.txt`.
2. Cliquer sur `Indexer le document`.
3. Poser une question en langage naturel.
4. Lire la réponse et vérifier les passages sources affichés.

Exemples de questions :

- `Quelles priorités économiques sont évoquées dans le discours ?`
- `Que dit le texte sur l'éducation ?`
- `Quels passages parlent de l'énergie ou du climat ?`
- `Que propose le discours concernant la classe moyenne ?`

## Paramètres RAG

- `chunk_size = 850`
- `chunk_overlap = 120`
- `top_k = 4`

Ces valeurs respectent la plage conseillée dans le sujet et gardent des passages assez riches pour un corpus textuel continu.

## Tests

Lancer les tests :

```bash
pytest
```

La GitHub Action exécute aussi `pytest` à chaque `push` et `pull_request`.

## Limites connues

- Une seule collection Chroma est utilisée pour simplifier le projet.
- La qualité finale dépend du modèle Ollama installé localement.
- Le mode dégradé ne produit pas une vraie synthèse LLM.
- Le projet ne prend en charge que les fichiers `.txt`.
