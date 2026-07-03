PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest
STREAMLIT := .venv/bin/streamlit
DOCKER := docker
COMPOSE := docker compose
OLLAMA_API_URL ?= http://host.docker.internal:11434/api/generate

.PHONY: help venv install run run-local ui-local api-local \
	compose-up compose-down compose-build compose-logs \
	fastapi-up streamlit-up minio-up \
	test check ollama-pull ollama-serve clean

help: ## Affiche la liste des commandes
	@awk 'BEGIN {FS = ": ## "}; /^[a-zA-Z0-9_-]+: ## / {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Cree l'environnement virtuel Python dans .venv
	python3 -m venv .venv

install: ## Installe toutes les dependances Python dans .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r fastapi_requirements.txt
	$(PIP) install -r streamlit_requirements.txt

run: compose-up ## Alias principal pour lancer la stack Docker Compose

run-local: ui-local ## Alias pour lancer l'interface Streamlit en local

ui-local: ## Lance l'interface Streamlit en local sur le port 8501
	$(STREAMLIT) run app.py --server.port 8501 --server.address 0.0.0.0

api-local: ## Lance l'API FastAPI en local sur le port 8000
	$(PYTHON) -m uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload

compose-build: ## Construit les images Docker Compose
	$(COMPOSE) build

compose-up: ## Construit et lance toute la stack Docker Compose
	$(COMPOSE) up --build

compose-down: ## Arrete la stack Docker Compose
	$(COMPOSE) down

compose-logs: ## Affiche les logs de la stack Docker Compose
	$(COMPOSE) logs -f

fastapi-up: ## Lance uniquement le service FastAPI via Docker Compose
	$(COMPOSE) up --build fastapi

streamlit-up: ## Lance uniquement le service Streamlit via Docker Compose
	$(COMPOSE) up --build streamlit

minio-up: ## Lance uniquement le service MinIO via Docker Compose
	$(COMPOSE) up --build minio

test: ## Lance les tests unitaires
	$(PYTEST)

check: ## Verifie la syntaxe Python puis lance les tests
	$(PYTHON) -m compileall app.py src tests
	$(PYTEST)

ollama-pull: ## Telecharge le modele configure dans src/config.py
	ollama pull qwen2.5:0.5b

ollama-serve: ## Demarre le serveur Ollama en local
	ollama serve

clean: ## Supprime les caches Python generes localement
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
