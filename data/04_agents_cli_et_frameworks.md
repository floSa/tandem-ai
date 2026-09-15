> [!NOTE]
> Fiche antérieure au pipeline de sourçage : ses chiffres n'ont pas de source
> attachée et n'ont pas tous été re-vérifiés. Certains restent exacts, d'autres
> non — la distinction est faite dans [`catalog/`](../catalog/), qui fait foi.

# Référentiel Data : Agents CLI & Frameworks Autonomes (Août 2026)

## 1. Claude Code CLI
* **Nom officiel :** Claude Code
* **Éditeur :** Anthropic, PBC
* **Liens Officiels :**
  * Documentation officielle : [https://docs.anthropic.com/en/docs/claude-code](https://docs.anthropic.com/en/docs/claude-code)
  * Installation : Via npm (`npm install -g @anthropic-ai/claude-code`)
* **Nature Technique :** Outil CLI agentique officiel conçu pour opérer directement au cœur du terminal dans n'importe quel dépôt Git.
* **Intégration & Capacités :**
  * Interaction en ligne de commande via la commande `claude`.
  * Agent autonome capable d'indexer la codebase, d'éditer des fichiers multi-arborescences, d'exécuter des tests, de lancer des builds et de créer des commits Git formatés.
* **Modèle Économique :**
  * Inclus sans surcoût pour les abonnés **Claude Pro ($20/mois)**, **Claude Max ($100–$200/mois)** ou facturé à l'usage réel via une clé API Anthropic (Claude Sonnet 5 / Opus 5).

---

## 2. Aider
* **Nom officiel :** Aider
* **Éditeur :** Paul Gauthier (Open-Source)
* **Liens Officiels :**
  * Site web : [https://aider.chat](https://aider.chat)
  * Dépôt GitHub : [https://github.com/paul-gauthier/aider](https://github.com/paul-gauthier/aider)
* **Nature Technique :** Agent de programmation par paire (*Pair Programming*) en ligne de commande dans le terminal.
* **Intégration & Capacités :**
  * Fonctionne avec Git : chaque modification approuvée génère automatiquement un commit Git propre avec un message conventionnel pertinent.
  * Moteur de mapping de dépôt ultra-compact utilisant `tree-sitter` pour envoyer uniquement la carte syntaxique pertinente au LLM (économise massivement les tokens d'entrée).
* **Gestion des Modèles :**
  * Compatible avec tous les LLMs majeurs via API : Claude Sonnet 5, DeepSeek V4, GPT-5.6, Qwen 3, OpenRouter, et modèles locaux via Ollama.
* **Modèle Économique :**
  * **100% Gratuit et Open-Source.**

---

## 3. Hermes Agent
* **Nom officiel :** Hermes Agent
* **Éditeur :** Nous Research
* **Liens Officiels :**
  * Site web : [https://hermes-agent.org](https://hermes-agent.org)
  * Dépôt GitHub : [https://github.com/NousResearch/Hermes-Agent](https://github.com/NousResearch/Hermes-Agent)
* **Nature Technique :** Framework agentique persistant et auto-améliorant, déployable sur serveur, VPS ou machine locale.
* **Intégration & Capacités :**
  * **Mémoire continue & Synthèse de compétences :** Mémorise les préférences architecturales du développeur et génère de nouvelles compétences réutilisables à partir des erreurs passées.
  * **Architecture multi-rôles :** Pipeline d'agents coordonnés (Architect, Engineer, Reviewer).
  * Plus de 40 outils intégrés (automatisation web, exécution shell, vision, Codex CLI).
* **Modèle Économique :**
  * **Open-Source.** Compatible avec OpenRouter pour router les requêtes vers les modèles de son choix.

---

## 4. OpenClaw
* **Nom officiel :** OpenClaw
* **Éditeur :** Collectif OpenClaw
* **Liens Officiels :**
  * Site web : [https://openclaw.ai](https://openclaw.ai)
* **Nature Technique :** Orchestrateur agentique orienté exécution de tâches et automatisation terminal / messageries.
* **Intégration & Capacités :**
  * Boucle agentique en 7 étapes permettant de piloter des tâches de CI/CD et de déploiement via la commande `openclaw agent exec`.
  * Contrôle distant possible via canaux sécurisés (messageries, passerelles mobiles).
* **Modèle Économique :**
  * **Open-Source.**

---

## 5. Kimi Code CLI
* **Nom officiel :** Kimi Code CLI
* **Éditeur :** Moonshot AI
* **Liens Officiels :**
  * Plateforme Développeur : [https://platform.moonshot.cn](https://platform.moonshot.cn)
* **Nature Technique :** Agent de développement autonome distribué sous forme de binaire unique (autonome, sans dépendance Node.js).
* **Intégration & Capacités :**
  * Optimisé pour les sessions de développement longues avec planification autonome, édition de fichiers et exécution shell.
  * Support du protocole ACP (*Agent Client Protocol*) pour s'interfacer avec différents éditeurs.
* **Modèle Économique :**
  * Utilisation via les crédits d'abonnement Kimi ou par clé API Moonshot (modèles K2.7 Code / K3).

---

## 6. OpenHands (ex-OpenDevin)
* **Nom officiel :** OpenHands
* **Éditeur :** All-Hands-AI (Open-Source)
* **Liens Officiels :**
  * Site web : [https://all-hands.dev](https://all-hands.dev)
  * Dépôt GitHub : [https://github.com/All-Hands-AI/OpenHands](https://github.com/All-Hands-AI/OpenHands)
* **Nature Technique :** Plateforme logicielle open-source reproduisant un agent de génie logiciel autonome complet (environnement sandbox Docker, terminal, navigateur web et éditeur de code).
* **Modèle Économique :**
  * **Logiciel libre (Open-Source) auto-hébergé** (BYOK / OpenRouter).
  * Offre Cloud managée payante pour les entreprises.
