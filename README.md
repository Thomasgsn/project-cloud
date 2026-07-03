# Mini projet RAG Cloud

Application RAG légère construite pour répondre à des questions à partir du corpus fourni : `corpus_de_travail.txt` (discours de Barack Obama).

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
- `make run` : construit et lance l'application via Docker ;
- `make run-local` : lance l'interface Streamlit en local ;
- `make docker-build` : construit l'image Docker ;
- `make docker-run` : lance le conteneur Docker ;
- `make test` : lance les tests ;
- `make check` : compile le code Python puis lance les tests ;
- `make ollama-pull` : télécharge le modèle Ollama configuré ;
- `make ollama-serve` : démarre Ollama.

## Lancer l'application

```bash
make run
```

Puis ouvrir l'interface dans le navigateur.

Si Docker n'est pas disponible, utiliser :

```bash
make run-local
```

Si vous lancez le projet dans Codespaces et que l'adresse d'Ollama diffère, vous pouvez surcharger l'URL au moment du lancement:

```bash
make docker-run OLLAMA_API_URL=http://host.docker.internal:11434/api/generate
```

## Utilisation

1. Charger un fichier `.txt` ou `.pdf`, ou sélectionner `corpus_de_travail.txt`.
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
make test
```

La GitHub Action exécute aussi `pytest` à chaque `push` et `pull_request`.

## Limites connues

- Une seule collection Chroma est utilisée pour simplifier le projet.
- L'embedding local est moins sémantique qu'un vrai modèle transformer.
- La qualité finale dépend du modèle Ollama installé localement.
- Le mode dégradé ne produit pas une vraie synthèse LLM.
- L'extraction PDF dépend de la qualité du texte présent dans le fichier.
