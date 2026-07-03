## **Contexte**

Dans ce TP final, vous devez construire une petite application IA capable de répondre à des questions à partir d’un document fourni.

Le document de travail est un texte en français : **discours de Barack Obama de 2013** . Ce texte est utilisé uniquement comme corpus documentaire pour tester votre application. Le TP ne porte pas sur une analyse politique du discours, mais sur la construction technique d’une chaîne RAG légère.

L’objectif est de produire une application simple, testable et documentée, en utilisant des outils open source et des services cloud gratuits ou accessibles gratuitement dans le cadre du TP.

À la fin du travail, un utilisateur doit pouvoir :

- charger ou sélectionner le document fourni
- indexer le contenu du document
- poser une question en langage naturel
- obtenir une réponse générée à partir du document
- visualiser les passages du document utilisés comme source

Le sujet est volontairement limité pour tenir dans une durée de 3h. Il ne s’agit pas de construire une application de production, mais une première application fonctionnelle illustrant les principes d’un RAG.

## **Rappel : qu’est-ce qu’un RAG ?**

Un modèle de langage répond généralement à partir de ses connaissances internes. Il peut produire une réponse fluide, mais il ne connaît pas forcément les documents spécifiques que l’on souhaite exploiter.

Le principe du **RAG** , pour _Retrieval-Augmented Generation_ , consiste à enrichir la réponse du modèle avec des passages extraits d’un document.

Le fonctionnement peut être résumé ainsi :

`Document source`\
↓\
`Découpage en passages courts`\
↓\
`Création des embeddings`\
↓\
`Stockage dans une base vectorielle`\
↓\
`Recherche des passages proches de la question`\
↓\
`Construction d’un prompt enrichi`\
↓\
`Réponse du LLM avec affichage des sources`

Dans ce TP, l’assistant ne doit pas se comporter comme un chatbot généraliste. Il doit répondre en s’appuyant sur les passages retrouvés dans le document.

Si l’information demandée n’est pas présente dans le document, l’application doit l’indiquer clairement.

## **Services et outils recommandés**

Vous êtes libres dans l’organisation de votre code. Il n’est pas demandé de respecter une arborescence imposée.

Les outils suivants sont recommandés pour réaliser le TP :

|**Besoin**|**Outil recommandé**|
|---|---|
|Environnement cloud de développement|GitHub Codespaces|
|Interface utilisateur|Streamlit|
|Backend API|FastAPI|
|Stockage du document brut|MinIO|
|Base vectorielle|ChromaDB|
|Orchestration RAG|LangChain|
|Modèle d’embeddings|`sentence-transformers/paraphrase-multili`|
|Automatisation CI|GitHub Actions|
|Versioning et remise|GitHub|

Vous pouvez utiliser une alternative si vous la justifiez clairement dans votre documentation.

Exemples :

- remplacer MinIO par un stockage local pour une version simplifiée
- utiliser un autre modèle léger disponible via Ollama
- construire une application Streamlit plus simple sans backend séparé
- utiliser une autre base vectorielle si son rôle est clairement expliqu

## **Travail demandé**

Vous devez construire une application capable d’exploiter le document fourni et de répondre à des questions à partir de ce document.

L’application doit couvrir les fonctionnalités suivantes.

## **1. Chargement du document**

L’utilisateur doit pouvoir charger ou sélectionner le fichier fourni depuis l’interface.

Le format recommandé est `.txt` . Le fichier txt du sujet est fourni en pièce jointe de ce sujet. Le support PDF est accepté en bonus, uniquement si le texte est correctement extractible. Attention à utiliser un PDF avec un petit volumes de pages vu la qualité minimaliste des modèles d’embedding et LLM choisis.

Le document peut être stocké dans MinIO ou dans un stockage équivalent. Si vous ne mettez pas en place MinIO, vous devez expliquer votre choix dans le README.

## **2. Indexation du document**

Votre application doit permettre d’indexer le document.

L’indexation consiste à :

- lire le contenu du document ;

- découper le texte en passages courts ;

- transformer chaque passage en embedding ;

- stocker les passages vectorisés dans une base vectorielle ;

- conserver des métadonnées simples : nom du fichier, numéro du passage, extrait du texte.

Paramétrage conseillé :

```plaintext
chunk_size:entre700et900caractères
chunk_overlap:entre100et150caractères
top_k:entre3et4passages
```

Ces valeurs peuvent être ajustées si vous expliquez votre choix.

## **3. Question utilisateur**

L’utilisateur doit pouvoir poser une question depuis l’interface. Exemples de questions possibles :

- Quelles priorités économiques sont évoquées dans le discours ?
- Que dit le texte sur l’éducation ?
- Quels passages parlent de l’énergie ou du climat ?
- Que propose le discours concernant le salaire minimum ?
- Quels éléments concernent la classe moyenne ?

## **4. Recherche documentaire**

Pour chaque question, votre application doit :

- transformer la question en embedding
- rechercher les passages les plus proches dans la base vectorielle
- récupérer les passages pertinents
- construire un contexte documentaire pour le LLM

## **5. Affichage des sources**

- L’application doit afficher
- la réponse générée
- les passages utilisés comme sources
- le nom du document
- le numéro du passage ou un identifiant équivalent
- éventuellement le score de similarité

Cela permet de vérifier que la réponse provient réellement du document.

## **Interface et backend**

Vous devez exposer une application utilisable depuis un navigateur.

L’interface doit au minimum permettre :

- le chargement ou la sélection du document
- le lancement de l’indexation
- la saisie d’une question
- l’affichage de la réponse
- l’affichage des sources

Si vous utilisez FastAPI, vous pouvez par exemple prévoir les endpoints suivants :

```plaintext
GET/health
POST/upload
POST/index
POST/ask
```

Ces endpoints ne sont pas obligatoires si vous réalisez une version simplifiée avec Streamlit uniquement. En revanche, votre code doit rester compréhensible, testable et documenté.

## **Déploiement et lien de test**

Votre application doit être testable par le professeur.

La solution recommandée est d’utiliser GitHub Codespaces et de rendre public le port utilisé par Streamlit.

Exemple de lancement Streamlit :

```plaintext
streamlitrunapp.py–server.port8501–server.address0.0.0.0
```

Si votre projet utilise un backend FastAPI séparé :

```plaintext
uvicornmain:app–host0.0.0.0–port8000–reload
```

Dans Codespaces, vous devez vérifier que le port de l’application est bien accessible depuis le navigateur.

Le lien de test de l’application devra être transmis au professeur.

## **GitHub Actions**

Votre repository doit contenir une automatisation simple avec GitHub Actions.

Il n’est pas demandé de mettre en place un pipeline de production. L’objectif est de montrer que vous savez intégrer une première étape de CI dans un projet cloud/IA. Votre workflow peut par exemple :

- installer les dépendances Python
- exécuter quelques tests simples
- vérifier qu’une fonction clé ne casse pas
- tester un endpoint de santé si vous utilisez FastAP
- Exemples de tests utiles
- test de découpage d’un texte en chunks
- test de construction du prompt
- test de disponibilité d’un endpoint `/health`
- test simple sur le format de réponse retournée

## **Documentation attendue**

Votre repository doit contenir un fichier `README.md` clair. Le README doit expliquer :

- l’objectif du projet
- les outils utilisés
- la manière de lancer l’application
- la manière d’installer ou lancer Ollama
- la manière d’indexer le document
- un exemple de question
- les limites connues de l’application

Vous devez également ajouter une courte description du fonctionnement RAG. Exemple minimal :

`Document -> Découpage -> Embeddings -> Base vectorielle -> Recherche -> Prompt enrichi -> Réponse + sources`

## **Livrables à transmettre**

À la fin du TP, chaque groupe doit transmettre :

   1. le lien du repository GitHub
   2. le lien de test de l’application IA
   3. une capture d’écran de l’application
   4. le README du projet
   5. une preuve que GitHub Actions s’exécute
   6. un exemple de question/réponse avec les sources affichées

Le professeur doit pouvoir comprendre, lancer ou tester le projet à partir des éléments fournis.

## **Critères d’évaluation**

L’évaluation portera principalement sur :

- le fonctionnement général de l’application
- la bonne compréhension du principe RAG
- la qualité du découpage documentaire
- l’utilisation d’une base vectorielle
- la capacité à générer une réponse fondée sur les passages retrouvés
- l’affichage clair des sources
- la lisibilité du code
- la qualité du README
- l’usage pertinent des services cloud gratuits
- la présence d’une automatisation simple avec GitHub Actions

Le design visuel de l’application n’est pas prioritaire. Une interface simple mais fonctionnelle vaut mieux qu’une interface travaillée mais instable.

## **Bonus possibles**

Les bonus sont facultatifs. Ils ne doivent être réalisés que si le socle principal fonctionne déjà.

Exemples de bonus :

- prise en charge d’un PDF non scanné
- gestion de plusieurs documents
- bouton permettant de réinitialiser l’index vectoriel
- réglage du nombre de passages récupérés
- affichage du score de similarité
- meilleure mise en forme des sources
- dockerisation plus complète
- tests unitaires plus nombreux
- comparaison entre deux modèles Ollama légers

## **Limites acceptées**

Cette application est volontairement une version légère. Les limites suivantes sont acceptées :

- temps de réponse parfois long
- qualité imparfaite du petit modèle
- corpus limité à un seul document
- absence d’authentification
- absence de monitoring avancé
- absence de déploiement production
- interface simple

En revanche, le principe suivant doit être respecté :

L’assistant doit répondre à partir du document. S’il ne trouve pas l’information dans le document, il doit le dire clairement.

## **Résultat attendu**

Le résultat attendu est une mini-application IA complète et testable. Vous devez être capables d’expliquer :

- le rôle du document source
- le principe du découpage en passages
- le rôle des embeddings
- le rôle de la base vectorielle
- le rôle du LLM
- le chemin parcouru par une question utilisateur
- la manière dont les sources sont affichées

Le but du TP n’est pas d’obtenir le meilleur modèle possible. Le but est de comprendre comment assembler une première application RAG, la rendre testable dans un environnement cloud gratuit, documenter les choix techniques et transmettre un code réutilisable.