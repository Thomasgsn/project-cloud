# ✅ Checklist Projet RAG Lite
📁 1. Chargement du document
 L'utilisateur peut charger un fichier .txt
 (Bonus) Le PDF est également accepté
 Le document est stocké (MinIO ou stockage local)
 Si MinIO n'est pas utilisé, c'est expliqué dans le README
📚 2. Indexation
 Lecture du document
 Découpage en chunks
 chunk_size ≈ 700–900 caractères
 chunk_overlap ≈ 100–150 caractères
 Création des embeddings
 Stockage dans ChromaDB (ou équivalent)
 Les métadonnées sont enregistrées :
 Nom du document
 Numéro du chunk
 Extrait du texte
🤖 3. Question utilisateur
 Champ permettant de poser une question
 Le backend reçoit correctement la question
🔍 4. Recherche documentaire
 La question est transformée en embedding
 Recherche des passages les plus proches
 top_k = 3 ou 4
 Les passages retrouvés sont récupérés
🧠 5. Génération de réponse
 Le prompt contient :
 la question
 le contexte
 l'instruction de répondre uniquement avec le contexte
 Ollama fonctionne
 Le modèle (ex : qwen2.5:0.5b) répond correctement

 Si la réponse n'est pas dans le document, le modèle répond clairement :

"Je ne trouve pas cette information dans le document fourni."

📄 6. Affichage des sources
 La réponse est affichée
 Les passages utilisés sont affichés
 Le nom du document apparaît
 Le numéro du chunk est affiché
 (Bonus) Le score de similarité est affiché
🖥️ Interface
 Bouton pour charger un document
 Bouton pour lancer l'indexation
 Champ de question
 Bouton "Poser la question"
 Réponse affichée
 Sources affichées
⚙️ Backend (si FastAPI)
 GET /health
 POST /upload
 POST /index
 POST /ask

(Non obligatoire si tout est fait avec Streamlit.)

☁️ Déploiement
 L'application fonctionne sur GitHub Codespaces
 Le port est public
 Le professeur peut accéder à l'application
 Le lien de test est prêt
🧪 GitHub Actions
 Workflow GitHub Actions présent
 Installation des dépendances
 Lancement des tests
 Les tests passent

Tests possibles :

 test du découpage
 test du prompt
 test du endpoint /health
 test du format de réponse
📖 README

Le README explique :

 l'objectif du projet
 les outils utilisés
 comment lancer le projet
 comment installer/lancer Ollama
 comment indexer le document
 un exemple de question
 les limites du projet
 le fonctionnement d'un RAG

Schéma présent :

Document
↓
Découpage
↓
Embeddings
↓
Base vectorielle
↓
Recherche
↓
Prompt enrichi
↓
Réponse + Sources
📦 Livrables
 Repository GitHub
 Lien de test
 Capture d'écran de l'application
 README
 Capture GitHub Actions (pipeline vert)
 Exemple de question/réponse avec les sources
⭐ Bonus (facultatif)
 Support PDF
 Plusieurs documents
 Bouton "Réinitialiser l'index"
 Réglage du nombre de passages (top_k)
 Affichage du score de similarité
 Docker
 Plus de tests unitaires
 Comparaison de plusieurs modèles Ollama
🎯 Vérification finale

Avant de rendre le projet, vérifie que tu peux répondre oui à toutes ces questions :

 Le projet fonctionne du début à la fin sans erreur.
 Les réponses proviennent bien du document et non des connaissances du LLM.
 Les sources sont visibles.
 Si une information n'existe pas dans le document, l'application le dit clairement.
 Le professeur peut lancer ou tester le projet facilement grâce au README et au lien de déploiement.
