# Projet Cloud - Présentation

## 1. Contexte et problématique du sujet

- Construire une mini application IA capable de répondre à des questions à partir d’un document donné.
- Le corpus utilisé est le discours d’investiture de Barack Obama.
- Objectif technique: mettre en place une chaîne RAG simple, testable et démontrable.
- Problème à résoudre: répondre uniquement à partir du document, avec des sources visibles.

---

## 2. Architecture technique

- Interface utilisateur: `Streamlit`
- Stockage local des documents: dossier `data/documents/`
- Indexation vectorielle: `ChromaDB`
- Embeddings: embedding local léger par hashing de tokens
- Génération des réponses: `Ollama`
  
### Interactions

`Upload / sélection du document`
→ `lecture du texte`
→ `découpage en chunks`
→ `vectorisation`
→ `stockage dans Chroma`
→ `question utilisateur`
→ `recherche des passages proches`
→ `prompt enrichi`
→ `réponse + sources`

---

## 3. Implémentation

- `app.py`
  - gère l’interface Streamlit
  - permet l’upload `.txt` et `.pdf`
  - lance l’indexation et l’interrogation

- `src/document_store.py`
  - enregistre les documents localement
  - liste les documents disponibles dans `data/documents/`

- `src/rag_pipeline.py`
  - lit les fichiers `.txt` et `.pdf`
  - découpe le texte en passages
  - génère les embeddings locaux
  - indexe dans Chroma
  - recherche les passages pertinents
  - construit le prompt pour Ollama

- `Makefile`
  - simplifie les commandes de démo et de correction

- `README.md`
  - explique le projet, le lancement et les limites

---

## 4. Tests et résultats

### Tests mis en place

- test du découpage en chunks
- test de la construction du prompt
- test du mode dégradé
- vérification de compilation Python

### Résultats observables

- une réponse est produite à partir des passages retrouvés
- les sources sont affichées dans l’interface
- le mode dégradé permet de montrer le projet même sans Ollama
- le support PDF fonctionne pour les PDF textuels simples

---

## 5. Conclusion

- Le projet répond à la problématique du TP avec une architecture RAG légère.
- La solution reste simple à lancer, à comprendre et à corriger.
- Les limites connues sont assumées:
  - qualité dépendante du texte source
  - PDF scannés non pris en charge sans OCR
  - génération dépendante d’Ollama

### Ouverture possible

- ajouter un backend FastAPI
- ajouter un meilleur embedding sémantique
- ajouter OCR pour les PDF scannés
- exposer l’application sur un environnement cloud complet
