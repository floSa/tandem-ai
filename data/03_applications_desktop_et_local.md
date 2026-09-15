> [!WARNING]
> Fiche antérieure à la mise en place du pipeline de sourçage. Les chiffres qu'elle
> contient n'ont pas de source vérifiable et sont en attente de re-vérification.
> Données validées : [`catalog/`](../catalog/).

# Référentiel Data : Applications Desktop Autonomes & Moteurs Locaux (Août 2026)

## 1. LM Studio Bionic vs LM Studio Classique
* **Nom officiel :** LM Studio Bionic (Agent autonome) & LM Studio (Runner local)
* **Éditeur :** Element Labs, Inc.
* **Liens Officiels :**
  * Site web : [https://lmstudio.ai](https://lmstudio.ai)
  * Documentation : [https://lmstudio.ai/docs](https://lmstudio.ai/docs)
* **Nature Technique :**
  * **LM Studio Classique :** Serveur local et interface de téléchargement de modèles GGUF/Hugging Face. Intègre un serveur HTTP local compatible avec l'API OpenAI (`http://localhost:1234/v1`).
  * **LM Studio Bionic :** Nouvelle application autonome dédiée aux workflows agentiques (développement, inspection de codebases, diffs de code en direct, transcription vocale locale via Voxtral de Mistral).
* **Intégration & Capacités :**
  * Permet d'exécuter des modèles locaux (DeepSeek, Qwen, Mistral) sur le GPU de l'utilisateur (CUDA/RTX) et d'y connecter des harnais comme VS Code (Cline, Continue) via son serveur local.
  * Technologie *LM Link* pour orchestrer le calcul sur plusieurs machines d'un même réseau local.
* **Modèle Économique :**
  * **Gratuit pour usage personnel.**

---

## 2. Claude Desktop
* **Nom officiel :** Claude Desktop
* **Éditeur :** Anthropic, PBC
* **Liens Officiels :**
  * Téléchargement : [https://claude.ai/download](https://claude.ai/download)
  * Documentation MCP : [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
* **Nature Technique :** Application native pour Windows et macOS servant d'interface graphique à Claude, enrichie par le protocole MCP.
* **Intégration & Capacités :**
  * Support natif des **serveurs MCP (Model Context Protocol)** : permet à Claude Desktop de lire des bases de données locales, d'interagir avec Git, de manipuler des fichiers sur le disque et d'exécuter des outils configurés dans un fichier `claude_desktop_config.json`.
  * Capacités *Computer Use* pour interagir visuellement avec les fenêtres et applications de bureau.
* **Modèle Économique :**
  * Utilisable avec un compte gratuit, ou débloqué à pleine puissance via l'abonnement **Claude Pro ($20/mois)**, **Max 5x ($100/mois)** ou **Max 20x ($200/mois)**.

---

## 3. ChatGPT Desktop (avec *Work with Apps*)
* **Nom officiel :** ChatGPT Desktop Application
* **Éditeur :** OpenAI, LLC
* **Liens Officiels :**
  * Téléchargement : [https://openai.com/chatgpt/desktop](https://openai.com/chatgpt/desktop)
  * Documentation : [https://help.openai.com](https://help.openai.com)
* **Nature Technique :** Application native pour macOS et Windows.
* **Intégration & Capacités :**
  * Fonctionnalité **Work with Apps** : permet à ChatGPT Desktop de lire directement le code et le contexte de travail ouvert dans Visual Studio Code, Xcode, Terminal et iTerm2 sans copier-coller manuel.
  * Espace de travail interactif **Canvas** pour modifier du code ou des documents côte à côte avec le chat.
* **Modèle Économique :**
  * Version gratuite (accès au modèle GPT-5.6 Luna), ou forfaits **ChatGPT Plus ($20/mois)** et **ChatGPT Pro ($100–$200/mois)** pour les modèles Sol/Terra et les agents avancés.

---

## 4. Kimi Work (Moonshot AI)
* **Nom officiel :** Kimi Work
* **Éditeur :** Moonshot AI
* **Liens Officiels :**
  * Site web : [https://kimi.moonshot.cn](https://kimi.moonshot.cn)
* **Nature Technique :** Application desktop officielle disponible sur Windows et macOS pour les travailleurs du savoir et développeurs.
* **Intégration & Capacités :**
  * Modes "Work" et "Chat" avec accès aux fichiers locaux, planification de tâches en arrière-plan et automatisation bureautique.
* **Modèle Économique :**
  * Forfaits d'abonnement Kimi : **Moderato ($19/mois)**, **Allegretto ($39/mois)**, **Allegro ($99/mois)**.

---

## 5. Moteurs & Runners Locaux Complémentaires
* **Ollama :** Moteur en ligne de commande ultra-léger servant une API locale standardisée (`http://localhost:11434/v1`). 100% gratuit et open-source.
* **Jan :** Alternative open-source à LM Studio, 100% hors-ligne, permettant de chatter et de servir des modèles locaux compatibles OpenAI API.
* **AnythingLLM :** Application desktop tout-en-un spécialisée dans le RAG local (indexation de dépôts de code et documents complets pour recherche sémantique).
