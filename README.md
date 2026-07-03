# Mini projet RAG Cloud

Application RAG simple avec :

- une interface `Streamlit`
- une API `FastAPI`
- une base vectorielle locale `ChromaDB`
- un service `MinIO` présent dans la stack Docker Compose
- une génération optionnelle via `Ollama`

## Lancement avec Docker Compose

Le dépôt est actuellement structuré autour de [`docker-compose.yaml`](./docker-compose.yaml).

Lancer toute la stack :

```bash
docker compose up --build
```

ou via le raccourci :

```bash
make run
```

Services démarrés :

- `streamlit` sur <http://localhost:8501>
- `fastapi` sur <http://localhost:8000>
- `minio` API sur <http://localhost:9000>
- `minio` console sur <http://localhost:9001>

Pour arrêter la stack :

```bash
docker compose down
```

ou :

```bash
make compose-down
```

Pour relancer seulement un service :

```bash
docker compose up --build fastapi
docker compose up --build streamlit
docker compose up --build minio
```

Raccourcis `make` équivalents :

- `make fastapi-up`
- `make streamlit-up`
- `make minio-up`
- `make compose-logs`

## Ce que fait réellement la stack

- `fastapi` expose les endpoints RAG.
- `streamlit` fournit l'interface de démo.
- `minio` fait partie de la stack Compose, mais le pipeline Python actuel stocke encore ses fichiers localement dans `data/` et n'utilise pas MinIO pour l'indexation.

## Ollama

`Ollama` n'est pas lancé par `docker compose`.

Le code tente d'appeler par défaut :

```text
http://localhost:11434/api/generate
```

Depuis les conteneurs, cette URL ne pointe pas vers la machine hôte. Si `Ollama` n'est pas accessible, l'application reste utilisable en mode dégradé :

- l'indexation fonctionne
- la recherche de passages fonctionne
- la réponse finale est remplacée par les extraits les plus pertinents

## Utilisation

1. Ouvrir `http://localhost:8501`.
2. Charger un fichier `.txt` ou `.pdf`.
3. Cliquer sur `Indexer le document`.
4. Poser une question.
5. Consulter la réponse et les sources affichées.

Pour tester l'API directement, ouvrir :

- `http://localhost:8000/docs`

Endpoints disponibles :

- `GET /health`
- `POST /upload`
- `POST /index`
- `POST /ask`

## Objectif

L'application permet de :

- charger un document `.txt` ou `.pdf`
- découper le document en passages
- vectoriser les passages avec un embedding local léger
- retrouver les passages les plus proches d'une question
- générer une réponse en français si `Ollama` est disponible
- afficher les sources utilisées

Chaîne RAG utilisée :

`Document -> Decoupage -> Embeddings -> Base vectorielle -> Recherche -> Prompt enrichi -> Reponse + sources`

## Choix techniques

- Interface : `Streamlit`
- Backend : `FastAPI`
- Base vectorielle : `ChromaDB`
- Embeddings : hashing local léger
- Génération : `Ollama` via HTTP
- Stockage applicatif actuel : local dans `data/`
- Orchestration des services : `Docker Compose`

## Paramètres RAG

- `chunk_size = 850`
- `chunk_overlap = 120`
- `top_k = 4`

## Tests

Les tests sont dans [`tests/`](./tests).

Exécution locale :

```bash
make test
```

## Commandes utiles

Le [`Makefile`](./Makefile) fournit aussi :

- `make venv`
- `make install`
- `make api-local`
- `make ui-local`
- `make run`
- `make compose-down`
- `make compose-logs`
- `make ollama-pull`
- `make ollama-serve`

## Références

- Corpus d'exemple : [corpus_de_travail.txt](./corpus_de_travail.txt)
