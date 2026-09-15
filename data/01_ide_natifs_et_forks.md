# Référentiel Data : Les IDE Dérivés IA & Forks VS Code (Août 2026)

## 1. Cursor
* **Nom officiel :** Cursor
* **Éditeur :** Anysphere, Inc.
* **Liens Officiels :**
  * Site web : [https://cursor.com](https://cursor.com)
  * Documentation : [https://docs.cursor.com](https://docs.cursor.com)
  * Tarification : [https://cursor.com/pricing](https://cursor.com/pricing)
* **Nature Technique :** Fork complet et autonome de VS Code, synchronisé avec les extensions et configurations VS Code standard.
* **Intégration & Capacités :**
  * Mode Agent interactif (`Composer` / `Agent`), autocomplétion prédictive ultra-rapide (`Cursor Tab`), navigation de dépôt (`Codebase Indexing`).
  * Support du protocole MCP (*Model Context Protocol*) pour brancher des serveurs de contexte locaux ou distants.
* **Gestion des Modèles :**
  * Modèles internes : Cursor Small, Cursor Fast.
  * Modèles tiers accessibles : Claude Sonnet 5, Claude Opus 5, GPT-5.6 Sol/Terra, DeepSeek V4, Qwen 3.
  * Support BYOK : Oui (possibilité d'entrer ses propres clés API OpenAI, Anthropic, Google, ou endpoint personnalisé/OpenRouter).
* **Modèle Économique (Août 2026) :**
  * **Hobby (Gratuit) :** Autocomplétion de base limitée, crédits d'essai pour requêtes agent.
  * **Pro ($20/mois) :** Requêtes illimitées sur modèles Cursor de base, pool mensuel de requêtes rapides sur modèles Frontier tiers.
  * **Pro+ ($60/mois) :** Quota étendu pour développeurs intensifs.
  * **Ultra ($200/mois) :** Priorité absolue, accès illimité haute vitesse et support dédié.
  * **Teams ($40/utilisateur/mois) :** Facturation centralisée, gouvernance, mode Zero Data Retention.
  * *Note tarifaire :* Application du *Cursor Token Rate* ($0.25 / 1M tokens) sur l'usage de modèles tiers en entreprise au-delà du quota.

---

## 2. Windsurf / Devin Desktop
* **Nom officiel :** Windsurf (intégré à l'écosystème Devin Desktop)
* **Éditeur :** Cognition AI (ayant acquis Codeium / Windsurf)
* **Liens Officiels :**
  * Site web : [https://devin.ai](https://devin.ai) / [https://codeium.com/windsurf](https://codeium.com/windsurf)
  * Documentation : [https://docs.codeium.com/windsurf](https://docs.codeium.com/windsurf)
  * Tarification : [https://devin.ai/pricing](https://devin.ai/pricing)
* **Nature Technique :** Fork VS Code agentique conçu autour du moteur de flux de travail en cascade (*Cascade Flow*).
* **Intégration & Capacités :**
  * Moteur Cascade : combine la recherche sémantique profonde dans la codebase, la planification multi-étapes et l'exécution de commandes terminales supervisées.
  * Synchronisation fluide avec Devin Cloud pour déporter des tâches longues en arrière-plan.
* **Gestion des Modèles :**
  * Modèles par défaut : Claude Sonnet 5, GPT-5.6, Gemini 1.5/2.0 Pro, modèles internes Codeium.
  * Support BYOK : Oui via configuration avancée.
* **Modèle Économique (Août 2026) :**
  * **Free ($0) :** Quota quotidien d'invites Cascade et autocomplétion continue.
  * **Pro ($20/mois) :** Quotas standards pour modèles de pointe et intégration Devin Cloud.
  * **Max ($200/mois) :** Quotas maximaux pour équipes et développeurs à fort volume.
  * **Teams ($80 de base + $40/utilisateur/mois) :** Tableau de bord d'équipe, politiques de sécurité et rétention zéro.

---

## 3. Trae
* **Nom officiel :** Trae
* **Éditeur :** ByteDance
* **Liens Officiels :**
  * Site web : [https://trae.ai](https://trae.ai)
  * Documentation : [https://docs.trae.ai](https://docs.trae.ai)
  * Tarification : [https://trae.ai/pricing](https://trae.ai/pricing)
* **Nature Technique :** Fork natif de VS Code optimisé pour le développement agentique autonome, disponible sur macOS, Windows et Cloud IDE.
* **Intégration & Capacités :**
  * Mode **SOLO** : Agent entièrement autonome capable de concevoir, implémenter, tester et déployer une fonctionnalité de bout en bout à partir d'un prompt en langage naturel.
  * Support natif du protocole MCP (*Model Context Protocol*).
* **Gestion des Modèles :**
  * Intègre Claude Sonnet 5, GPT-5.6, DeepSeek V4 (Pro & Flash), et modèles internes ByteDance / Doubao.
* **Modèle Économique (Août 2026) :**
  * **Free ($0) :** 5 000 autocomplétions/mois, accès limité aux modèles de pointe.
  * **Lite ($3/mois) :** Accès léger aux modèles de pointe pour les développeurs occasionnels.
  * **Pro ($10/mois) :** Forfait de référence très agressif avec solde de crédits mensuel et essai gratuit de 7 jours.
  * **Pro+ ($30/mois) :** Pour usage intensif quotidien.
  * **Ultra ($100/mois) :** Accès illimité haute vitesse et priorité d'inférence.

---

## 4. Zed AI
* **Nom officiel :** Zed AI
* **Éditeur :** Zed Industries, Inc.
* **Liens Officiels :**
  * Site web : [https://zed.dev](https://zed.dev)
  * Documentation : [https://zed.dev/docs/assistant](https://zed.dev/docs/assistant)
  * Tarification : [https://zed.dev/pricing](https://zed.dev/pricing)
* **Nature Technique :** Éditeur de code ultra-rapide développé en Rust (non-VS Code), avec moteur GPU natif.
* **Intégration & Capacités :**
  * Fonctionnalité *Edit Predictions* (prédiction en temps réel du prochain bloc de code).
  * Assistant intégré avec support multi-fichiers et citations de contexte.
* **Gestion des Modèles :**
  * Support natif BYOK (OpenAI, Anthropic, Google, Ollama local, OpenRouter).
* **Modèle Économique (Août 2026) :**
  * **Personal (Gratuit) :** Éditeur complet + BYOK gratuit sans surcoût.
  * **Zed Pro ($10/mois) :** Modèles hébergés par Zed inclus, Edit Predictions illimitées et 5$ de crédits tokens inclus/mois.
  * **Zed Business :** Facturation d'équipe consolidée à l'usage réel.

---

## 5. Augment Code
* **Nom officiel :** Augment Code
* **Éditeur :** Augment Inc.
* **Liens Officiels :**
  * Site web : [https://augmentcode.com](https://augmentcode.com)
  * Tarification : [https://augmentcode.com/pricing](https://augmentcode.com/pricing)
* **Nature Technique :** Moteur d'indexation de codebase propriétaire pour les entreprises et équipes d'ingénierie.
* **Modèle Économique (Août 2026) :**
  * **Business Plan ($100/mois) :** Inclut jusqu'à 50 sièges (sans surcoût par siège), 100$ d'usage inclus (tokens LLM au prix public + calcul Cosmos à $0.19/h + frais de service de 40%).
  * **Enterprise :** Contrats sur mesure au-delà de 50 sièges.

---

## 6. Void IDE
* **Nom officiel :** Void IDE
* **Éditeur :** Projet Open-Source communautaire
* **Liens Officiels :**
  * Site web : [https://voideditor.com](https://voideditor.com)
  * Dépôt GitHub : [https://github.com/voideditor/void](https://github.com/voideditor/void)
* **Nature Technique :** Fork open-source de VS Code conçu pour une alternative 100% libre et locale à Cursor.
* **Statut (Août 2026) :** Projet en pause / maintenance communautaire (développement principal ralenti fin 2025). Entièrement gratuit (Bring Your Own Key uniquement).
