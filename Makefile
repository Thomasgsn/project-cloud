PYTHON := .venv/bin/python
PIP := .venv/bin/pip
PYTEST := .venv/bin/pytest
STREAMLIT := .venv/bin/streamlit

.PHONY: help venv install run test check ollama-pull ollama-serve clean

help: ## Affiche la liste des commandes
	@awk 'BEGIN {FS = ": ## "}; /^[a-zA-Z0-9_-]+: ## / {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Cree l'environnement virtuel Python dans .venv
	python3 -m venv .venv

install: ## Installe toutes les dependances Python dans .venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: ## Lance l'interface Streamlit sur le port 8501
	$(STREAMLIT) run app.py --server.port 8501 --server.address 0.0.0.0

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
