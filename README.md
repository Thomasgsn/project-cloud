# Mini projet RAG Cloud

## Run Local

Lancer l'API localement:

```bash
make api-local
```

Lancer l'interface Streamlit localement:

```bash
make ui-local
```

Dans les deux cas, Ollama doit déjà tourner sur la machine hôte:

```bash
make ollama-serve
```

Puis ouvrir:

- `http://localhost:8000/docs` pour l'API
- `http://localhost:8501` pour l'interface Streamlit

## Run Codespaces

Lancer l'API dans Docker:

```bash
make run
```

Puis ouvrir l'API exposée sur le port `8000`.

Si Ollama tourne sur l'hôte Codespaces, on peut surcharger l'URL:

```bash
make docker-run OLLAMA_API_URL=http://host.docker.internal:11434/api/generate
```

Si vous voulez l'interface Streamlit dans Codespaces, utilisez:

```bash
make ui-local
```

<https://gamma.app/docs/Projet-Cloud-Chaine-RAG-cyuo9samzcomsjz>

## Objectif

L'application permet de :

- charger un fichier `.txt` ou `.pdf`
- indexer le document en passages courts
- vectoriser les passages avec un embedding local léger
- rechercher les passages les plus proches d'une question
- générer une réponse en français
- afficher les sources utilisées

Chaîne RAG utilisée :

`Document -> Découpage -> Embeddings -> Base vectorielle -> Recherche -> Prompt enrichi -> Réponse + sources`

## Choix techniques

- Interface : `Streamlit`
- Backend : `FastAPI`
- Base vectorielle : `ChromaDB`
- Embeddings : hashing local léger sans modèle externe
- Génération : `Ollama` en local via HTTP
- Stockage du document : local (`data/documents/`)
- Conteneurisation : `Docker`

MinIO n'a pas été mis en place pour garder une version simple, testable rapidement et compatible avec un environnement local ou Codespaces sans services supplémentaires. Le stockage local remplit ici le même rôle pour le TP.

Le corpus du sujet n'est plus proposé automatiquement dans l'interface si `data/documents/` est vide. Il faut soit uploader un fichier, soit copier le corpus fourni dans `data/documents/`.

Le support PDF est inclus pour les PDF textuels simples. Les PDF scannés ou mal structurés peuvent produire une extraction incomplète.

## Installation

Prérequis :

- Python 3.11+
- Ollama installé localement
- Docker installé localement pour le lancement containerisé

Créer l'environnement puis installer les dépendances :

```bash
make venv
make install
```

Si vous avez déjà installé les dépendances et voyez une erreur du type `A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x`, il faut réinstaller avec la version figée de NumPy :

```bash
rm -rf .venv
make venv
make install
```

## Lancer Ollama

Si Ollama n'est pas installé

```bash
curl -fsSL https://ollama.com/install.sh | sh
````

Récupérer le modèle :

```bash
make ollama-pull
```

Lacner le modèle :

```bash
make ollama-serve
```

Le projet appelle par défaut le modèle `qwen2.5:0.5b` sur `http://localhost:11434`.

Si Ollama n'est pas disponible, l'application reste utilisable en mode dégradé : elle affiche les passages retrouvés les plus pertinents au lieu d'une réponse générée complète.

En mode Docker, l'application passe par `host.docker.internal` pour joindre Ollama lancé sur la machine hôte.

## Commandes utiles

Le projet contient un `Makefile` pensé pour la correction et la présentation :

```bash
make help
```

Commandes principales :

- `make venv` : crée l'environnement virtuel ;
- `make install` : installe les dépendances ;
- `make run` : construit et lance l'API FastAPI via Docker ;
- `make api-local` : lance l'API en local sur le port 8000 ;
- `make ui-local` : lance l'interface Streamlit en local ;
- `make docker-build` : construit l'image Docker de l'API ;
- `make docker-run` : lance l'API dans un conteneur Docker ;
- `make test` : lance les tests ;
- `make check` : compile le code Python puis lance les tests ;
- `make ollama-pull` : télécharge le modèle Ollama configuré ;
- `make ollama-serve` : démarre Ollama.

## Lancer l'application

Pour l'API:

```bash
make run
```

Puis ouvrir la documentation interactive sur `http://localhost:8000/docs`.

Pour l'interface Streamlit:

```bash
make ui-local
```

Puis ouvrir l'interface dans le navigateur.

Si vous lancez le projet dans Codespaces et que l'adresse d'Ollama diffère, vous pouvez surcharger l'URL au moment du lancement:

```bash
make docker-run OLLAMA_API_URL=http://host.docker.internal:11434/api/generate
```

## Utilisation

1. Charger un fichier `.txt` ou `.pdf`, ou sélectionner `corpus_de_travail.txt`.
2. Cliquer sur `Indexer le document`.
3. Poser une question en langage naturel.
4. Lire la réponse et vérifier les passages sources affichés.

### Endpoints FastAPI

- `GET /health`
- `POST /upload`
- `POST /index`
- `POST /ask`

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
make test
```

La GitHub Action exécute aussi `pytest` à chaque `push` et `pull_request`.

## Limites connues

- Une seule collection Chroma est utilisée pour simplifier le projet.
- L'embedding local est moins sémantique qu'un vrai modèle transformer.
- La qualité finale dépend du modèle Ollama installé localement.
- Le mode dégradé ne produit pas une vraie synthèse LLM.
- L'extraction PDF dépend de la qualité du texte présent dans le fichier.
