> [!NOTE]
> Fiche antérieure au pipeline de sourçage : ses chiffres n'ont pas de source
> attachée et n'ont pas tous été re-vérifiés. Certains restent exacts, d'autres
> non — la distinction est faite dans [`catalog/`](../catalog/), qui fait foi.

# Référentiel Data : Extensions & Harnais pour VS Code Standard (Août 2026)

## 1. GitHub Copilot & Copilot Workspace
* **Nom officiel :** GitHub Copilot
* **Éditeur :** GitHub / Microsoft
* **Liens Officiels :**
  * Site web : [https://github.com/features/copilot](https://github.com/features/copilot)
  * Tarification : [https://github.com/pricing](https://github.com/pricing)
* **Nature Technique :** Extension officielle intégrée pour Visual Studio Code, Visual Studio, JetBrains et Neovim.
* **Intégration & Capacités :**
  * Autocomplétion de code en ligne (Ghost text / Next-edit suggestions).
  * Chat contextuel dans la barre latérale, mode `@workspace` pour interroger l'ensemble du projet.
  * Environnement **Copilot Workspace** pour planifier et générer des PRs complètes à partir d'issues GitHub.
* **Modèle Économique (Mise à jour majeure au 1er juin 2026) :**
  * Transition vers le système de facturation **GitHub AI Credits** à la consommation de tokens.
  * **Completions gratuites :** Les suggestions en ligne et l'autocomplétion ne consomment aucun crédit IA sur tous les forfaits payants.
  * **Copilot Free ($0/mois) :** Quota limité de complétions et accès restreint au chat.
  * **Copilot Pro ($10/mois) :** Allocation mensuelle de base de GitHub AI Credits pour les développeurs individuels.
  * **Copilot Pro+ ($39/mois) :** Quota élevé de crédits pour les flux agentiques avancés.
  * **Copilot Max ($100/mois) :** Pour les utilisateurs intensifs nécessitant le volume maximal de crédits.
  * **Copilot Business ($19/utilisateur/mois) :** Mutualisation des crédits d'équipe, politiques de sécurité d'entreprise (dépassement à $0.01 par AI Credit).
  * **Copilot Enterprise ($39/utilisateur/mois) :** Indexation de bases de code privées d'organisation, modèles fins et sécurité renforcée.

---

## 2. Cline (ex-Claude Dev)
* **Nom officiel :** Cline
* **Éditeur :** Collectif Open-Source (créé initialement par Saoud Rizwan)
* **Liens Officiels :**
  * Dépôt GitHub : [https://github.com/cline/cline](https://github.com/cline/cline)
  * VS Code Marketplace : [https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
* **Nature Technique :** Extension agentique autonome open-source pour VS Code.
* **Intégration & Capacités :**
  * Agent autonome capable de créer/modifier des fichiers, d'exécuter des commandes dans le terminal intégré, d'analyser les erreurs de compilation et de tester son propre code de manière itérative.
  * Demande d'approbation humaine granulaire pour chaque action sensible (écriture disque, exécution shell).
  * Support complet du protocole MCP (*Model Context Protocol*).
* **Gestion des Modèles :**
  * 100% BYOK (*Bring Your Own Key*) : Anthropic (Claude Sonnet 5), OpenAI (GPT-5.6), OpenRouter (pour accéder à DeepSeek V4, Qwen 3, GLM-5), Ollama / LM Studio (modèles locaux).
* **Modèle Économique :**
  * **100% Gratuit et Open-Source.**
  * Aucun abonnement mensuel : l'utilisateur ne paye que sa consommation réelle de tokens auprès de son fournisseur API (ou 0$ s'il utilise un modèle local).

---

## 3. Roo Code
* **Nom officiel :** Roo Code
* **Éditeur :** Collectif Open-Source RooVetGit
* **Liens Officiels :**
  * Dépôt GitHub : [https://github.com/RooVetGit/Roo-Code](https://github.com/RooVetGit/Roo-Code)
  * VS Code Marketplace : [https://marketplace.visualstudio.com/items?itemName=RooVeterinaryInc.roo-cline](https://marketplace.visualstudio.com/items?itemName=RooVeterinaryInc.roo-cline)
* **Nature Technique :** Fork avancé et spécialisé de Cline, orienté multi-rôles.
* **Intégration & Capacités :**
  * Système de **Modes Spécialisés** configurables :
    * `Code` : Implémentation logicielle et refactoring.
    * `Architect` : Conception haut niveau et réflexion technique sans modification immédiate de fichiers.
    * `Ask` : Questions / Réponses sur la codebase sans toucher au code.
    * `Debug` : Analyse d'erreurs et de logs.
    * `Custom Modes` : Création de sous-agents sur mesure avec prompts systèmes et outils spécifiques.
* **Modèle Économique :**
  * **100% Gratuit et Open-Source** (BYOK pur via OpenRouter, Anthropic, OpenAI, ou serveurs locaux).

---

## 4. Continue.dev
* **Nom officiel :** Continue
* **Éditeur :** Continue Dev, Inc. (Open-Source)
* **Liens Officiels :**
  * Site web : [https://continue.dev](https://continue.dev)
  * Documentation : [https://docs.continue.dev](https://docs.continue.dev)
  * Dépôt GitHub : [https://github.com/continuedev/continue](https://github.com/continuedev/continue)
* **Nature Technique :** Extension open-source modulaire pour VS Code et JetBrains IDEs.
* **Intégration & Capacités :**
  * Spécialisé dans l'autocomplétion par tabulation (*Tab Autocomplete*) et le chat contextuel.
  * Permet de séparer le modèle d'autocomplétion rapide (ex: Codestral ou modèle local 3B/7B) du modèle de chat/raisonnement (ex: Claude Sonnet 5 ou DeepSeek V4).
* **Modèle Économique :**
  * **Gratuit & Open-Source** pour les développeurs individuels (BYOK / Ollama).
  * **Continue for Teams :** Offre entreprise avec hub de configuration centralisé et règles de gouvernance.

---

## 5. Qoder / Tongyi Lingma
* **Nom officiel :** Qoder CN (anciennement Tongyi Lingma)
* **Éditeur :** Alibaba Cloud
* **Liens Officiels :**
  * Site web : [https://alibabacloud.com](https://alibabacloud.com)
  * VS Code Marketplace : Extension "Qoder" / "Tongyi Lingma"
* **Nature Technique :** Extension IDE officielle pour VS Code et JetBrains, optimisée pour l'écosystème Qwen / Alibaba Cloud.
* **Modèle Économique (Août 2026) :**
  * Modèle d'essai pour nouveaux utilisateurs.
  * Forfait mensuel **Coding Plan** (~$50/mois) pour les développeurs utilisant intensivement les modèles Qwen3.7-Plus / Qwen3.8-Max via la passerelle Alibaba Cloud Model Studio.

---

## 6. CodeGeeX
* **Nom officiel :** CodeGeeX
* **Éditeur :** Zhipu AI (Z.ai)
* **Liens Officiels :**
  * Site web : [https://codegeex.cn](https://codegeex.cn)
  * VS Code Marketplace : Extension "CodeGeeX"
* **Nature Technique :** Extension multilingue d'assistance au code pour VS Code et JetBrains.
* **Intégration & Capacités :**
  * Modes "Stealth" (suggestions discrètes en arrière-plan) et "Interactive" (sélection de candidats).
  * Traduction automatique de code inter-langages (ex: Python vers C++ ou Rust).
* **Modèle Économique :**
  * **Gratuit pour usage individuel** avec les modèles GLM-4.7-Flash / CodeGeeX intégrés.
  * Formules **GLM Coding Plan** ($10–$80/mois) pour débloquer les modèles de pointe GLM-5.2 et GLM-5.3.

---

## 7. Autres Acteurs Spécialisés & Statuts 2026
* **Tabnine :** Orienté exclusivement entreprises ($39–$59/utilisateur/mois) avec hébergement sur cloud privé ou sur site (*On-premise*).
* **Sourcegraph Cody :** Forfaits Free et Pro grand public arrêtés depuis juillet 2025 ; offre repositionnée uniquement sur les grands comptes (*Cody Enterprise*).
* **Amazon Q Developer :** Fin des nouvelles inscriptions depuis mai 2026, arrêt définitif du service programmé pour avril 2027.
