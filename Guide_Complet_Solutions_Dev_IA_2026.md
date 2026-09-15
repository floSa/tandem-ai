> [!WARNING]
> **Document en cours de re-vérification — ne pas utiliser pour une décision d'achat.**
>
> La mise en place du pipeline de sourçage (septembre 2026) a établi que plusieurs
> affirmations de ce document ne résistent pas à la vérification sur sources
> primaires : des modèles qui n'apparaissent dans aucune source de benchmark
> (`GPT-5.6 Sol/Terra/Luna`, `Kimi K3`, `Qwen3.8-Max`, `GLM-5.3`, `Claude 5.0`),
> et des grilles tarifaires sans source vérifiable.
>
> Les données réellement vérifiées vivent désormais dans [`catalog/`](./catalog/)
> et se consultent via [`site/index.html`](./site/index.html).
> Ce Guide sera régénéré depuis le catalogue une fois les tarifs relevés sur les
> pages officielles. Voir [`protocol/04_sources_et_collecte.md`](./protocol/04_sources_et_collecte.md).

---

# Guide de Référence & Audit Exhaustif des Solutions de Développement par IA (Août 2026)
## Panorama des Harnais, IDEs Dérivés, Applications Desktop, Agents CLI, Passerelles & Grilles Tarifaires Réelles en France

---

## Sommaire
1. [Architecture Conceptuelle & Taxonomie en 4 Couches](#1-architecture-conceptuelle--taxonomie-en-4-couches)
2. [Règles de Facturation en France : Devises, Stripe & Impact Réel de la TVA (20%)](#2-règles-de-facturation-en-france--devises-stripe--impact-réel-de-la-tva-20)
3. [Panorama Comparatif des Harnais et Environnements de Développement](#3-panorama-comparatif-des-harnais-et-environnements-de-développement)
   * 3.1 [Les IDE Dérivés IA (Forks VS Code & Éditeurs Dédiés)](#31-les-ide-dérivés-ia-forks-vs-code--éditeurs-dédiés)
   * 3.2 [Les Extensions Agentes VS Code Standard (BYOK & Multi-Modèles)](#32-les-extensions-agentes-vs-code-standard-byok--multi-modèles)
   * 3.3 [Les Applications Desktop Autonomes (GUI & Agents Locaux)](#33-les-applications-desktop-autonomes-gui--agents-locaux)
   * 3.4 [Les Agents CLI & Frameworks d'Automatisation Terminal](#34-les-agents-cli--frameworks-dautomatisation-terminal)
   * 3.5 [Les Passerelles Universelles & Agrégateurs Multi-Modèles](#35-les-passerelles-universelles--agrégateurs-multi-modèles)
4. [Panorama Détaillé des Fournisseurs de Modèles (Labs IA)](#4-panorama-détaillé-des-fournisseurs-de-modèles-labs-ia)
5. [Tableaux Comparatifs Économiques Détaillés & Sourcés](#5-tableaux-comparatifs-économiques-détaillés--sourcés)
   * 5.1 [Tableau Comparatif des Forfaits SaaS : Montants Débités Réels en France (Particulier TTC vs Pro HT)](#51-tableau-comparatif-des-forfaits-saas--montants-débités-réels-en-france-particulier-ttc-vs-pro-ht)
   * 5.2 [Tableau Comparatif des Prix API au 1M de Tokens (1 Ligne par Modèle)](#52-tableau-comparatif-des-prix-api-au-1m-de-tokens-1-ligne-par-modèle)
   * 5.3 [Simulations Budgétaires Réelles en France](#53-simulations-budgétaires-réelles-en-france)
6. [Guide Pratique d'Interopérabilité & Matrice de Décision](#6-guide-pratique-dinteropérabilité--matrice-de-décision)

---

## 1. Architecture Conceptuelle & Taxonomie en 4 Couches

Pour évaluer objectivement les solutions d'assistance au code, il est nécessaire de découpler la couche d'interaction humaine du modèle d'intelligence artificielle et du modèle de facturation.

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│ COUCHE 1 : LE HARNAIS D'EXÉCUTION (L'Interface Développeur)                      │
│ • IDE Dérivés : Cursor, Windsurf (Devin Desktop), Trae, Zed AI                   │
│ • Extensions VS Code : GitHub Copilot, Cline, Roo Code, Continue, Qoder, CodeGeeX│
│ • Applications Desktop : LM Studio Bionic, Claude Desktop (MCP), ChatGPT Desktop │
│ • Agents CLI : Claude Code, Aider, Hermes Agent, OpenClaw, Kimi Code CLI         │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │ (Protocoles : REST, OpenAI API, MCP, SSE)
┌────────────────────────────────────────▼─────────────────────────────────────────┐
│ COUCHE 2 : LA PASSERELLE / ROUTEUR D'ACCÈS                                       │
│ • Agrégateurs Cloud Universels : OpenRouter, Together AI, Fireworks AI, Groq     │
│ • Serveurs Locaux OpenAI-Compatibles : Ollama, LM Studio Server, vLLM, SGLang    │
│ • Connexion Directe Provider : SDK officiel du laboratoire (Anthropic, OpenAI)   │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼─────────────────────────────────────────┐
│ COUCHE 3 : LE FOURNISSEUR DE MODÈLE (Le Laboratoire d'IA / Les Poids)            │
│ • Laboratoires Occidentaux : Anthropic (Claude 5), OpenAI (GPT-5.6, o3), Mistral │
│ • Laboratoires Asiatiques : DeepSeek (V4), Qwen (Qwen 3.8), Moonshot (Kimi K3),  │
│   Zhipu AI (GLM-5.3)                                                             │
└────────────────────────────────────────┬─────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────▼─────────────────────────────────────────┐
│ COUCHE 4 : LE MODÈLE ÉCONOMIQUE & LA FACTURATION EN FRANCE                       │
│ • Forfait SaaS Fixe en Euros TTC (ex: ChatGPT Plus à 23 € TTC/mois)              │
│ • Forfait SaaS facturé en USD via Stripe + TVA française de 20% ($20 -> $24 TTC) │
│ • Consommation API au token via passerelle (OpenRouter / Clé directe + TVA)      │
│ • Auto-Hébergé / Gratuit : Modèles Open-Weights exécutés sur votre propre GPU    │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Règles de Facturation en France : Devises, Stripe & Impact Réel de la TVA (20%)

Lors de l'achat d'un abonnement ou de crédits API depuis la France, deux régimes de facturation coexistent :

1. **Les plateformes à prix fixe en Euros (€) avec TVA intégrée :**
   * **OpenAI (ChatGPT) :** Fixe son prix européen directement à **23,00 € TTC / mois** pour le forfait Plus (au lieu de 20 $), intégrant nativement la TVA française de 20%.
   * **Mistral AI :** Entreprise française basée à Paris. Les factures sont assujetties à la TVA française classique de 20%.
2. **Les plateformes américaines facturant en Dollars US ($) via Stripe :**
   * **Anthropic (Claude Pro), Cursor, Windsurf, Trae, GitHub, OpenRouter :**
     * **Pour un Particulier en France :** La plateforme applique automatiquement la **TVA française de 20%** lors du paiement Stripe. Un forfait affiché à 20,00 $ USD donne lieu à un débit de **24,00 $ USD** (soit environ **21,50 € à 22,80 € prélevés sur votre compte bancaire**, selon le taux de change et les frais de transaction internationale de votre banque).
     * **Pour un Professionnel / Entreprise :** Si vous renseignez votre **numéro de TVA intracommunautaire (FRxx...)**, la facture est émise en **autoliquidation de TVA (0% de TVA débitée)**. Le montant prélevé est strictement le montant hors taxes (ex: 20,00 $ USD ≈ **18,40 € HT**).

---

## 3. Panorama Comparatif des Harnais et Environnements de Développement

### 3.1 Les IDE Dérivés IA (Forks VS Code & Éditeurs Dédiés)

#### 🔹 Cursor
* **Éditeur :** Anysphere, Inc. (San Francisco, USA)
* **Liens Officiels :** [Site Cursor](https://cursor.com) | [Documentation](https://docs.cursor.com) | [Tarifs Cursor](https://cursor.com/pricing)
* **Nature Technique :** Fork complet et autonome de Visual Studio Code.
* **Fonctionnalités Clés :**
  - Autocomplétion multi-lignes prédictive (*Cursor Tab*).
  - Mode Agentique *Composer* (édition multi-fichiers simultanée, exécution terminale et auto-correction).
  - Indexation vectorielle sémantique du dépôt local et support natif de MCP (*Model Context Protocol*).
* **Modèles Supportés :** Claude Sonnet 5.0, Claude Opus 5.0, GPT-5.6 Sol/Terra, DeepSeek V4, et modèles internes.
* **Facturation France :** Facturation en USD via Stripe avec ajout de la TVA française (20%) pour les particuliers ($20 + 20% = $24,00 USD débités).

#### 🔹 Windsurf / Devin Desktop
* **Éditeur :** Cognition AI (ayant intégré Codeium / Windsurf).
* **Liens Officiels :** [Site Devin AI](https://devin.ai) | [Portail Windsurf](https://codeium.com/windsurf) | [Tarifs Devin](https://devin.ai/pricing)
* **Nature Technique :** Fork VS Code articulé autour du moteur de flux en cascade (*Cascade Flow*).
* **Fonctionnalités Clés :**
  - Moteur Cascade : combine la recherche sémantique profonde, l'ordonnancement de tâches et l'exécution terminale contrôlée.
  - Connexion avec *Devin Cloud* pour déporter des tâches d'ingénierie longues en tâche de fond.
* **Modèles Supportés :** Claude Sonnet 5.0, GPT-5.6, Gemini 2.0 Pro et modèles Codeium.

#### 🔹 Trae
* **Éditeur :** ByteDance.
* **Liens Officiels :** [Site Trae](https://trae.ai) | [Documentation](https://docs.trae.ai) | [Tarifs Trae](https://trae.ai/pricing)
* **Nature Technique :** Fork VS Code optimisé pour le travail agentique autonome (macOS, Windows, Cloud IDE).
* **Fonctionnalités Clés :**
  - Mode **SOLO** : Agent entièrement autonome capable de concevoir, coder, tester et déployer une application complète à partir d'un prompt naturel.
  - Tarification très compétitive : Forfait Pro à $10/mois (~11,00 € TTC en France).
* **Modèles Supportés :** Claude Sonnet 5.0, GPT-5.6, DeepSeek V4 Pro/Flash et modèles Doubao.

#### 🔹 Zed AI
* **Éditeur :** Zed Industries, Inc.
* **Liens Officiels :** [Site Zed](https://zed.dev) | [Docs Assistant](https://zed.dev/docs/assistant) | [Tarifs Zed](https://zed.dev/pricing)
* **Nature Technique :** Éditeur natif haute performance écrit en Rust, rendu GPU pur.
* **Fonctionnalités Clés :** *Edit Predictions* instantanées et intégration native BYOK sans aucun surcoût.

---

### 3.2 Les Extensions Agentes VS Code Standard (BYOK & Multi-Modèles)

#### 🔹 GitHub Copilot & Copilot Workspace
* **Éditeur :** GitHub / Microsoft.
* **Liens Officiels :** [GitHub Copilot](https://github.com/features/copilot) | [Grille Tarifaire GitHub](https://github.com/pricing)
* **Système de Facturation (Depuis le 1er juin 2026) :**
  - Passage au modèle basé sur les **GitHub AI Credits** à la consommation de tokens.
  - **Autocomplétion gratuite :** Les suggestions en ligne et l'autocomplétion par tabulation ne consomment aucun crédit IA sur tous les plans payants.
  - Facturation en France : $10 USD + TVA 20% = **$12,00 USD TTC / mois** (environ 11,00 € TTC) pour le forfait Pro.

#### 🔹 Cline (ex-Claude Dev)
* **Éditeur :** Collectif Open-Source.
* **Liens Officiels :** [Dépôt GitHub Cline](https://github.com/cline/cline) | [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=saoudrizwan.claude-dev)
* **Nature Technique :** Extension agentique autonome open-source pour VS Code.
* **Fonctionnalités Clés :**
  - Agent autonome complet : lit la codebase, crée/modifie des fichiers, exécute les commandes dans le terminal intégré et teste son code de manière itérative.
  - Approbation humaine requise pour chaque action sensible.
  - 100% Gratuit et Open-Source (fonctionne exclusivement en BYOK via Anthropic, OpenAI, OpenRouter ou Ollama local).

#### 🔹 Roo Code
* **Éditeur :** Collectif Open-Source RooVetGit.
* **Liens Officiels :** [Dépôt GitHub Roo Code](https://github.com/RooVetGit/Roo-Code) | [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=RooVeterinaryInc.roo-cline)
* **Nature Technique :** Fork avancé de Cline avec modes spécialisés (`Code`, `Architect`, `Ask`, `Debug`, `Custom Modes`).
* **Modèle Économique :** **100% Gratuit et Open-Source** (BYOK pur).

#### 🔹 Continue.dev
* **Éditeur :** Continue Dev, Inc.
* **Liens Officiels :** [Site Continue](https://continue.dev) | [Dépôt GitHub](https://github.com/continuedev/continue)
* **Nature Technique :** Extension modulaire permettant de séparer le modèle d'autocomplétion rapide (ex: Codestral ou modèle local en VRAM) du modèle de chat/raisonnement (ex: Claude Sonnet 5.0 ou DeepSeek V4-Pro).
* **Modèle Économique :** **Gratuit & Open-Source** pour développeurs individuels.

#### 🔹 Qoder / Tongyi Lingma
* **Éditeur :** Alibaba Cloud.
* **Liens Officiels :** [Alibaba Model Studio](https://www.alibabacloud.com/product/model-studio)
* **Nature Technique :** Extension officielle pour VS Code et JetBrains optimisée pour la gamme Qwen (Coding Plan à ~$50/mois ou API Model Studio).

#### 🔹 CodeGeeX
* **Éditeur :** Zhipu AI (Z.ai).
* **Liens Officiels :** [Site CodeGeeX](https://codegeex.cn) | [Z.ai](https://z.ai)
* **Nature Technique :** Extension multilingue pour VS Code (gratuite avec GLM-4.7-Flash / GLM-5.3-Flash, ou forfaits GLM Coding Plan pour GLM-5.3).

---

### 3.3 Les Applications Desktop Autonomes (GUI & Agents Locaux)

#### 🔹 LM Studio Bionic vs LM Studio Classique
* **Éditeur :** Element Labs, Inc.
* **Liens Officiels :** [Site LM Studio](https://lmstudio.ai) | [Documentation](https://lmstudio.ai/docs)
* **Nature Technique :**
  - **LM Studio Classique :** Serveur d'inférence local fournissant une API OpenAI locale sur `http://localhost:1234/v1`.
  - **LM Studio Bionic :** Application agentique autonome dédiée au développement, à l'inspection de dépôts, aux diffs de code et à la dictée vocale locale (via Voxtral de Mistral).
* **Modèle Économique :** **Gratuit pour usage personnel**.

#### 🔹 Claude Desktop (avec MCP)
* **Éditeur :** Anthropic, PBC.
* **Liens Officiels :** [Téléchargement Claude Desktop](https://claude.ai/download) | [Protocole MCP](https://modelcontextprotocol.io)
* **Nature Technique :** Application native Windows / macOS connectable aux outils locaux via MCP (*Model Context Protocol*) et dotée de capacités *Computer Use*.
* **Modèle Économique :** Gratuit de base, ou débloqué via Claude Pro ($20 + 20% TVA = **$24,00 USD TTC / mois** en France).

#### 🔹 ChatGPT Desktop (avec *Work with Apps*)
* **Éditeur :** OpenAI, LLC.
* **Liens Officiels :** [ChatGPT Desktop](https://openai.com/chatgpt/desktop)
* **Nature Technique :** Application native capturant directement le code et le contexte ouvert dans VS Code, Xcode ou le Terminal.
* **Modèle Économique :** Gratuit (Luna), ou abonnement **ChatGPT Plus fixé à 23,00 € TTC / mois en France**.

#### 🔹 Kimi Work
* **Éditeur :** Moonshot AI.
* **Liens Officiels :** [Kimi](https://kimi.moonshot.cn)
* **Nature Technique :** Application bureautique Windows / macOS avec exécution de tâches et automatisation locale.

---

### 3.4 Les Agents CLI & Frameworks d'Automatisation Terminal

#### 🔹 Claude Code CLI
* **Éditeur :** Anthropic, PBC.
* **Liens Officiels :** [Documentation Claude Code](https://docs.anthropic.com/en/docs/claude-code)
* **Installation :** `npm install -g @anthropic-ai/claude-code`
* **Nature Technique :** Outil CLI agentique opérant directement dans le terminal au sein du dépôt Git local.
* **Modèle Économique :** Inclus sans surcoût dans l'abonnement **Claude Pro ($24 TTC / mois)** ou facturé à l'usage exact via clé API Anthropic (Claude Sonnet 5.0 / Opus 5.0).

#### 🔹 Aider
* **Éditeur :** Paul Gauthier (Open-Source).
* **Liens Officiels :** [Site Aider](https://aider.chat) | [GitHub Aider](https://github.com/paul-gauthier/aider)
* **Nature Technique :** Agent de pair-programming en ligne de commande avec commits Git automatiques et compression de carte syntaxique Tree-sitter.
* **Modèle Économique :** **100% Gratuit et Open-Source**.

#### 🔹 Hermes Agent
* **Éditeur :** Nous Research.
* **Liens Officiels :** [Site Hermes Agent](https://hermes-agent.org) | [GitHub](https://github.com/NousResearch/Hermes-Agent)
* **Nature Technique :** Framework agentique persistant avec mémoire continue et pipeline multi-agents (Architect, Engineer, Reviewer).
* **Modèle Économique :** **Open-Source** (BYOK via OpenRouter).

#### 🔹 OpenClaw & OpenHands
* **OpenClaw :** [Site OpenClaw](https://openclaw.ai) — Orchestrateur de tâches terminal / messageries.
* **OpenHands (ex-OpenDevin) :** [Site OpenHands](https://all-hands.dev) | [GitHub](https://github.com/All-Hands-AI/OpenHands) — Plateforme complète de génie logiciel autonome dans des conteneurs Docker.

---

### 3.5 Les Passerelles Universelles & Agrégateurs Multi-Modèles

#### 🔹 OpenRouter (L'Agrégateur Universel de Référence)
* **Éditeur :** OpenRouter, Inc.
* **Liens Officiels :** [Site OpenRouter](https://openrouter.ai) | [Catalogue des Modèles & Tarifs](https://openrouter.ai/models) | [Documentation](https://openrouter.ai/docs)
* **Rôle Stratégique :** Fournit **une clé API unique** au format standardisé OpenAI pour accéder à plus de **300 modèles** de tous les laboratoires mondiaux (Claude 5.0, GPT-5.6, DeepSeek V4, Qwen 3.8, GLM-5.3) sans abonnement captif et avec support transparent du *Prompt Caching*.
* **Facturation en France :** Recharges de crédits en dollars via Stripe avec application de la TVA française (20%) pour les particuliers ($10 de crédits = $12 débités).

---

## 4. Panorama Détaillé des Fournisseurs de Modèles (Labs IA)

| Fournisseur | App Desktop Officielle | Extension / Harnais VS Code | Agent CLI Officiel | Forfaits Pro Développeur | Modèles Phares (Août 2026) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Anthropic** | **Claude Desktop** (MCP) | Non (via Cline/Roo Code) | **Claude Code CLI** | Claude Pro ($20 HT / $24 TTC) | Claude Opus 5.0, Claude Sonnet 5.0, Haiku 4.5 |
| **OpenAI** | **ChatGPT Desktop** | Non (via *Work with Apps*) | Outils CLI intégrés | ChatGPT Plus (23 € TTC), Pro (103 € TTC) | GPT-5.6 Sol, GPT-5.6 Terra, GPT-5.6 Luna, o3 |
| **DeepSeek** | Non (GUI communautaires) | Non (via Cline, Roo, Aider) | Non (CLI communautaires) | Aucun (100% API & Poids ouverts) | DeepSeek V4-Pro, DeepSeek V4-Flash |
| **Qwen (Alibaba)** | QoderWork | **Qoder / Tongyi Lingma** | Non | Coding Plan (~$50 HT / $60 TTC) | Qwen3.8-Max, Qwen3.7-Plus, Qwen3.8-Flash-Next |
| **Mistral AI** | **Mistral Vibe** (PWA) | **Mistral Vibe / Continue** | Non | Le Chat Pro (~18 € TTC / mois) | Codestral, Mistral Large 2, Mistral Small |
| **Moonshot (Kimi)** | **Kimi Work** | **Kimi Code Extension** | **Kimi Code CLI** | Moderato ($19 HT / $22.80 TTC) | Kimi K3, Kimi K2.7 Code, Kimi K2.5 |
| **Zhipu AI (GLM)** | Non | **CodeGeeX** | Non | GLM Coding Plan ($18 à $168 HT) | GLM-5.3, GLM-5.2, GLM-5.3-Flash |

---

## 5. Tableaux Comparatifs Économiques Détaillés & Sourcés

### 5.1 Tableau Comparatif des Forfaits SaaS : Montants Débités Réels en France (Particulier TTC vs Pro HT)

*Ce tableau détaille le coût exact facturé en France selon votre statut : Particulier (TTC avec TVA 20%) ou Professionnel avec N° TVA intracommunautaire (HT en autoliquidation).*

| Fournisseur / Outil | Nom du Forfait | Prix Affiché (Devise Origine) | Montant Débité Particulier en France (TTC) | Montant Débité Pro France (HT Autoliquidation) | Quotas & Crédits Inclus | Modèles Inclus | Source / Lien Officiel |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :--- |
| **ChatGPT (OpenAI)** | **Go** | 8,00 € TTC | **8,00 € TTC** | ~6,67 € HT | Requêtes illimitées modèle Luna + fichiers | GPT-5.6 Luna | [OpenAI Pricing](https://openai.com/chatgpt/pricing) |
| **ChatGPT (OpenAI)** | **Plus** | 23,00 € TTC | **23,00 € TTC** | ~19,17 € HT | *Work with Apps* Desktop, Canvas, Deep Research | GPT-5.6 Sol / Terra / Luna, o3 | [OpenAI Pricing](https://openai.com/chatgpt/pricing) |
| **ChatGPT (OpenAI)** | **Pro** | 103,00 € TTC | **103,00 € TTC** | ~85,83 € HT | Puissance maximale o3, quotas étendus | GPT-5.6 Sol, o3-pro | [OpenAI Pricing](https://openai.com/chatgpt/pricing) |
| **ChatGPT (OpenAI)** | **Business** | 20,00 $ /u HT | **24,00 $ /u TTC** (~22 €) | **20,00 $ /u HT** (~18,40 €) | Min. 2 sièges, console admin, rétention zéro | Tous modèles GPT-5.6 & o3 | [OpenAI Pricing](https://openai.com/chatgpt/pricing) |
| **Claude (Anthropic)** | **Pro** | 20,00 $ HT | **24,00 $ TTC** (~22,00 €) | **20,00 $ HT** (~18,40 €) | **Claude Code CLI inclus** + Claude Desktop MCP | Claude Sonnet 5.0, Claude Opus 5.0 | [Anthropic Pricing](https://anthropic.com/pricing) |
| **Claude (Anthropic)** | **Max 5x** | 100,00 $ HT | **120,00 $ TTC** (~110,00 €) | **100,00 $ HT** (~92,00 €) | 5x le quota de requêtes Claude Code & Desktop | Claude Sonnet 5.0, Claude Opus 5.0 | [Anthropic Pricing](https://anthropic.com/pricing) |
| **Claude (Anthropic)** | **Max 20x** | 200,00 $ HT | **240,00 $ TTC** (~220,00 €) | **200,00 $ HT** (~184,00 €) | 20x le quota de requêtes pour usage intensif | Claude Opus 5.0, Claude Sonnet 5.0 | [Anthropic Pricing](https://anthropic.com/pricing) |
| **GitHub Copilot** | **Free** | 0,00 $ | **0,00 €** | **0,00 €** | Complétions limitées et chat standard | Modèles de base GitHub | [GitHub Pricing](https://github.com/pricing) |
| **GitHub Copilot** | **Pro** | 10,00 $ HT | **12,00 $ TTC** (~11,00 €) | **10,00 $ HT** (~9,20 €) | **Autocomplétion gratuite** + allocation AI Credits | GPT-5.6, Claude Sonnet 5.0 | [GitHub Pricing](https://github.com/pricing) |
| **GitHub Copilot** | **Pro+** | 39,00 $ HT | **46,80 $ TTC** (~43,00 €) | **39,00 $ HT** (~35,90 €) | Crédits IA renforcés pour agents autonomes | GPT-5.6, Claude Sonnet 5.0, Workspace | [GitHub Pricing](https://github.com/pricing) |
| **GitHub Copilot** | **Max** | 100,00 $ HT | **120,00 $ TTC** (~110,00 €) | **100,00 $ HT** (~92,00 €) | Volume maximal de GitHub AI Credits | Tous modèles prioritaires | [GitHub Pricing](https://github.com/pricing) |
| **GitHub Copilot** | **Business** | 19,00 $ /u HT | **22,80 $ /u TTC** (~21 €) | **19,00 $ /u HT** (~17,50 €) | Crédits mutualisés par équipe ($0.01/crédit sup.) | Tous modèles avec gouvernance d'entreprise | [GitHub Pricing](https://github.com/pricing) |
| **GitHub Copilot** | **Enterprise** | 39,00 $ /u HT | **46,80 $ /u TTC** (~43 €) | **39,00 $ /u HT** (~35,90 €) | Indexation de repos privés et modèles dédiés | Modèles personnalisés d'organisation | [GitHub Pricing](https://github.com/pricing) |
| **Trae (ByteDance)** | **Free** | 0,00 $ | **0,00 €** | **0,00 €** | 5 000 autocomplétions/mois + essais Frontier | Modèles Doubao, Claude Sonnet 5.0 (limité) | [Trae Pricing](https://trae.ai/pricing) |
| **Trae (ByteDance)** | **Lite** | 3,00 $ HT | **3,60 $ TTC** (~3,30 €) | **3,00 $ HT** (~2,76 €) | Quota de requêtes rapides légères | Claude Sonnet 5.0, GPT-5.6 | [Trae Pricing](https://trae.ai/pricing) |
| **Trae (ByteDance)** | **Pro** | 10,00 $ HT | **12,00 $ TTC** (~11,00 €) | **10,00 $ HT** (~9,20 €) | Agent autonome SOLO illimité + solde mensuel | Claude Sonnet 5.0, GPT-5.6, DeepSeek V4 | [Trae Pricing](https://trae.ai/pricing) |
| **Trae (ByteDance)** | **Pro+** | 30,00 $ HT | **36,00 $ TTC** (~33,00 €) | **30,00 $ HT** (~27,60 €) | Quota de crédits pour développeurs quotidiens | Claude Sonnet 5.0, GPT-5.6, DeepSeek V4 Pro | [Trae Pricing](https://trae.ai/pricing) |
| **Trae (ByteDance)** | **Ultra** | 100,00 $ HT | **120,00 $ TTC** (~110,00 €) | **100,00 $ HT** (~92,00 €) | Accès illimité sans file d'attente | Ensemble des modèles sans restriction | [Trae Pricing](https://trae.ai/pricing) |
| **Cursor** | **Hobby** | 0,00 $ | **0,00 €** | **0,00 €** | Autocomplétion de base + essai agent | Modèles internes Cursor | [Cursor Pricing](https://cursor.com/pricing) |
| **Cursor** | **Pro** | 20,00 $ HT | **24,00 $ TTC** (~22,00 €) | **20,00 $ HT** (~18,40 €) | Modèles Cursor illimités + pool rapide Frontier | Claude Sonnet 5.0, GPT-5.6, DeepSeek V4 | [Cursor Pricing](https://cursor.com/pricing) |
| **Cursor** | **Pro+** | 60,00 $ HT | **72,00 $ TTC** (~66,00 €) | **60,00 $ HT** (~55,20 €) | Quota de requêtes rapides 3x supérieur | Claude Sonnet 5.0, GPT-5.6, Opus 5.0 | [Cursor Pricing](https://cursor.com/pricing) |
| **Cursor** | **Ultra** | 200,00 $ HT | **240,00 $ TTC** (~220,00 €) | **200,00 $ HT** (~184,00 €) | Priorité absolue et quota maximal | Tous modèles tiers avec latence minimale | [Cursor Pricing](https://cursor.com/pricing) |
| **Cursor** | **Teams** | 40,00 $ /u HT | **48,00 $ /u TTC** (~44 €) | **40,00 $ /u HT** (~36,80 €) | Facturation centralisée + Zero Data Retention | Tous modèles + audit de sécurité | [Cursor Pricing](https://cursor.com/pricing) |
| **Windsurf / Devin** | **Free** | 0,00 $ | **0,00 €** | **0,00 €** | Quota quotidien de requêtes Cascade | Modèles Codeium standard | [Devin Pricing](https://devin.ai/pricing) |
| **Windsurf / Devin** | **Pro** | 20,00 $ HT | **24,00 $ TTC** (~22,00 €) | **20,00 $ HT** (~18,40 €) | Quotas Cascade standard + accès Devin Cloud | Claude Sonnet 5.0, GPT-5.6, Gemini 2.0 Pro | [Devin Pricing](https://devin.ai/pricing) |
| **Windsurf / Devin** | **Max** | 200,00 $ HT | **240,00 $ TTC** (~220,00 €) | **200,00 $ HT** (~184,00 €) | Quota massif pour flux de travail continus | Tous modèles + priorité Devin Cloud | [Devin Pricing](https://devin.ai/pricing) |
| **Zed AI** | **Zed Pro** | 10,00 $ HT | **12,00 $ TTC** (~11,00 €) | **10,00 $ HT** (~9,20 €) | Modèles hébergés inclus + $5 de crédits API | Claude Sonnet 5.0, GPT-5.6 | [Zed Pricing](https://zed.dev/pricing) |
| **Mistral AI** | **Le Chat Pro** | ~15,00 € HT | **~18,00 € TTC** | **~15,00 € HT** | Canvas illimité, génération d'agents | Codestral, Mistral Large 2 | [Mistral Vibe](https://vibe.mistral.ai) |
| **Moonshot (Kimi)** | **Moderato** | 19,00 $ HT | **22,80 $ TTC** (~21,00 €) | **19,00 $ HT** (~17,50 €) | Kimi Work Desktop + crédits Kimi Code | Kimi K2.6, Kimi K2.7 Code | [Kimi Portal](https://kimi.moonshot.cn) |
| **Moonshot (Kimi)** | **Allegretto** | 39,00 $ HT | **46,80 $ TTC** (~43,00 €) | **39,00 $ HT** (~35,90 €) | Quotas renforcés Kimi Code et productivité | Kimi K2.7 Code, Kimi K3 | [Kimi Portal](https://kimi.moonshot.cn) |
| **Moonshot (Kimi)** | **Allegro** | 99,00 $ HT | **118,80 $ TTC** (~109,00 €) | **99,00 $ HT** (~91,00 €) | Accès aux essaims d'agents professionnels | Kimi K3, Essaims d'agents | [Kimi Portal](https://kimi.moonshot.cn) |
| **Qwen (Alibaba)** | **Coding Plan** | 50,00 $ HT | **60,00 $ TTC** (~55,00 €) | **50,00 $ HT** (~46,00 €) | Forfait mensuel fixe pour IDEs et agents | Qwen3.8-Max, Qwen3.7-Plus | [Alibaba Model Studio](https://www.alibabacloud.com/product/model-studio) |
| **GLM (Zhipu AI)** | **Coding Lite** | 18,00 $ HT | **21,60 $ TTC** (~19,90 €) | **18,00 $ HT** (~16,56 €) | Crédits hebdomadaires pour l'extension CodeGeeX | GLM-5.2, GLM-5.3 | [Z.ai Platform](https://z.ai) |
| **GLM (Zhipu AI)** | **Coding Pro** | 80,00 $ HT | **96,00 $ TTC** (~88,30 €) | **80,00 $ HT** (~73,60 €) | Quota mensuel étendu pour développement actif | GLM-5.3, GLM-5.2 | [Z.ai Platform](https://z.ai) |
| **GLM (Zhipu AI)** | **Coding Max** | 168,00 $ HT | **201,60 $ TTC** (~185,50 €) | **168,00 $ HT** (~154,56 €) | Quota maximal pour équipes et agents | GLM-5.3, GLM-5.2 | [Z.ai Platform](https://z.ai) |

---

### 5.2 Tableau Comparatif des Prix API au 1M de Tokens (1 Ligne par Modèle)

*Les tarifs officiels sont triés par ordre croissant du coût d'entrée standard en dollars US ($), avec le coût équivalent en Euros HT (1 $ ≈ 0,92 €) et le coût TTC indicatif en France (TVA 20% appliquée lors des recharges de compte Stripe).*

| Fournisseur | Modèle Officiel | Rôle / Spécialité | Contexte | Entrée Standard (USD / 1M) | Entrée HT / TTC en France (€ / 1M) | Entrée avec Cache (€ HT / 1M) | Sortie (€ HT / TTC / 1M) | Source / Lien Officiel |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Zhipu AI (GLM)** | **GLM-5.3-Flash / 4.7-Flash** | Flash / Gratuit | 128k | **$0.00** | **0,00 €** / 0,00 € | **0,00 €** | **0,00 €** / 0,00 € | [Z.ai Platform](https://z.ai) |
| **Qwen (Alibaba)** | **Qwen3.8-Flash-Next** | Flash Ultra-Rapide | 1M | **$0.05** | **0,046 €** / 0,055 € | **0,009 €** | **0,184 €** / 0,221 € | [Alibaba Model Studio](https://www.alibabacloud.com/product/model-studio) |
| **Mistral AI** | **Mistral Small** | Flash / Économique | 128k | **$0.10** | **0,092 €** / 0,110 € | **0,009 €** | **0,276 €** / 0,331 € | [Mistral Platform](https://console.mistral.ai) |
| **DeepSeek** | **DeepSeek V4-Flash (Off-Peak)** | Flash / Économique | 1M | **$0.22** | **0,202 €** / 0,243 € | **0,046 €** | **0,607 €** / 0,729 € | [DeepSeek Docs](https://api-docs.deepseek.com) |
| **Mistral AI** | **Codestral** | Spécialisé Code 256k | 256k | **$0.30** | **0,276 €** / 0,331 € | **0,028 €** | **0,828 €** / 0,994 € | [Mistral Platform](https://console.mistral.ai) |
| **Qwen (Alibaba)** | **Qwen3.7-Plus** | Équilibré Dev & Code | 128k | **$0.35** | **0,322 €** / 0,386 € | **0,046 €** | **1,150 €** / 1,380 € | [Alibaba Model Studio](https://www.alibabacloud.com/product/model-studio) |
| **DeepSeek** | **DeepSeek V4-Flash (Peak)** | Flash (Heures de pointe) | 1M | **$0.44** | **0,405 €** / 0,486 € | **0,101 €** | **1,214 €** / 1,457 € | [DeepSeek Docs](https://api-docs.deepseek.com) |
| **Moonshot (Kimi)** | **Kimi K2.5** | MoE Économique | 256k | **$0.60** | **0,552 €** / 0,662 € | **0,092 €** | **2,760 €** / 3,312 € | [Moonshot Platform](https://platform.moonshot.cn) |
| **DeepSeek** | **DeepSeek V4-Pro (Off-Peak)** | Flagship Raisonnement | 1M | **$0.66** | **0,607 €** / 0,729 € | **0,147 €** | **1,822 €** / 2,186 € | [DeepSeek Docs](https://api-docs.deepseek.com) |
| **Moonshot (Kimi)** | **Kimi K2.7 Code** | Spécialisé Code & Dev | 256k | **$0.95** | **0,874 €** / 1,049 € | **0,175 €** | **3,680 €** / 4,416 € | [Moonshot Platform](https://platform.moonshot.cn) |
| **Anthropic** | **Claude Haiku 4.5** | Flash / Économique | 200k | **$1.00** | **0,920 €** / 1,104 € | **0,092 €** | **4,600 €** / 5,520 € | [Anthropic Pricing](https://anthropic.com/pricing) |
| **OpenAI** | **GPT-5.6 Luna** | Flash / Économique | 128k | **$1.00** | **0,920 €** / 1,104 € | **0,092 €** | **5,520 €** / 6,624 € | [OpenAI Pricing](https://openai.com/api/pricing) |
| **DeepSeek** | **DeepSeek V4-Pro (Peak)** | Flagship (Heures de pointe) | 1M | **$1.32** | **1,214 €** / 1,457 € | **0,304 €** | **3,643 €** / 4,372 € | [DeepSeek Docs](https://api-docs.deepseek.com) |
| **Zhipu AI (GLM)** | **GLM-5.3 / GLM-5.2** | Flagship Raisonnement | 128k | **$1.40** | **1,288 €** / 1,546 € | **0,129 €** | **4,048 €** / 4,858 € | [Z.ai Platform](https://z.ai) |
| **Anthropic** | **Claude Sonnet 5.0** | **Référence Mondiale Code** | 200k | **$2.00** | **1,840 €** / 2,208 € | **0,184 €** | **9,200 €** / 11,040 € | [Anthropic Pricing](https://anthropic.com/pricing) |
| **Qwen (Alibaba)** | **Qwen3.8-Max** | **Flagship MoE Multimodal 2.4T** | 1M | **$2.00** | **1,840 €** / 2,208 € | **0,184 €** | **5,520 €** / 6,624 € | [Alibaba Model Studio](https://www.alibabacloud.com/product/model-studio) |
| **Mistral AI** | **Mistral Large 2** | Flagship Raisonnement | 128k | **$2.00** | **1,840 €** / 2,208 € | **0,184 €** | **5,520 €** / 6,624 € | [Mistral Platform](https://console.mistral.ai) |
| **OpenAI** | **o3 (Reasoning)** | Raisonnement Algorithmique | 200k | **$2.00** | **1,840 €** / 2,208 € | **0,184 €** | **7,360 €** / 8,832 € | [OpenAI Pricing](https://openai.com/api/pricing) |
| **OpenAI** | **GPT-5.6 Terra** | Équilibré Développeur | 256k | **$2.50** | **2,300 €** / 2,760 € | **0,230 €** | **13,800 €** / 16,560 € | [OpenAI Pricing](https://openai.com/api/pricing) |
| **Moonshot (Kimi)** | **Kimi K3** | Flagship 2.8T Multimodal | 1M | **$3.00** | **2,760 €** / 3,312 € | **0,276 €** | **13,800 €** / 16,560 € | [Moonshot Platform](https://platform.moonshot.cn) |
| **Anthropic** | **Claude Opus 5.0** | **Flagship Ultra-Complexe** | 200k | **$5.00** | **4,600 €** / 5,520 € | **0,460 €** | **23,000 €** / 27,600 € | [Anthropic Pricing](https://anthropic.com/pricing) |
| **OpenAI** | **GPT-5.6 Sol** | **Flagship Haute Capacité** | 256k | **$5.00** | **4,600 €** / 5,520 € | **0,460 €** | **27,600 €** / 33,120 € | [OpenAI Pricing](https://openai.com/api/pricing) |
| **OpenAI** | **o3-pro (Reasoning Max)** | Raisonnement Extrême | 200k | **$20.00** | **18,400 €** / 22,080 € | **1,840 €** | **73,600 €** / 88,320 € | [OpenAI Pricing](https://openai.com/api/pricing) |

---

### 5.3 Simulations Budgétaires Réelles en France

#### 📊 Profil Développeur Solo Modéré (~3 Millions Tokens Entrée + 300k Tokens Sortie / mois)
* **Via Abonnement Forfaitaire :**
  * Trae Pro : **~11,00 € TTC / mois** ($12 TTC débités).
  * GitHub Copilot Pro : **~11,00 € TTC / mois** ($12 TTC débités).
  * ChatGPT Plus : **23,00 € TTC / mois** (prix fixe France).
  * Claude Pro / Cursor Pro : **~22,00 € TTC / mois** ($24 TTC débités).
* **Via Harnais Libre (Cline / Roo Code) + Crédits OpenRouter TTC :**
  * Avec **DeepSeek V4-Flash** : **~0,95 € TTC / mois**.
  * Avec **DeepSeek V4-Pro** : **~2,85 € TTC / mois**.
  * Avec **Qwen3.7-Plus** : **~1,55 € TTC / mois**.
  * Avec **Claude Sonnet 5.0** (avec cache) : **~4,65 € TTC / mois**.
  * Avec **Claude Opus 5.0** : **~11,60 € TTC / mois**.

---

## 6. Guide Pratique d'Interopérabilité & Matrice de Décision

### 6.1 Recette Universelle : Brancher n'importe quel modèle dans n'importe quel harnais

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ CONFIGURATION PAS-À-PAS (Cursor / Cline / Roo Code / Aider / Continue)                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 1. Créer un compte sur OpenRouter (https://openrouter.ai) et recharger 10$ par Stripe │
│ 2. Dans votre extension VS Code (ex: Cline / Roo Code) :                               │
│    • Provider : Sélectionner "OpenRouter"                                              │
│    • API Key : Coller votre clé OpenRouter                                             │
│    • Model ID : Sélectionner le modèle exact :                                         │
│      - `anthropic/claude-sonnet-5` (Référence absolue en code)                         │
│      - `anthropic/claude-opus-5` (Architecture et cas hautement complexes)             │
│      - `deepseek/deepseek-v4-pro` (Raisonnement avancé à tarif ultra-compétitif)       │
│      - `qwen/qwen-3.8-max` (MoE multimodal géant pour les gros projets)               │
│      - `zhipu/glm-5.3` (Modèle GLM de pointe)                                          │
│ 3. Pour un modèle local (exécuté sur votre PC avec LM Studio ou Ollama) :              │
│    • Provider : "OpenAI Compatible"                                                    │
│    • Base URL : `http://localhost:1234/v1` (LM Studio) ou `http://localhost:11434/v1` │
│    • API Key : `local`                                                                 │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 6.2 Matrice de Décision selon la Configuration Matérielle & le Profil

#### 🖥️ Profil 1 : Développeur sur PC Fixe avec GPU Dédié (Nvidia RTX 4060 Ti 16 Go VRAM)
* **Architecture Recommandée :** Hybride Local / Cloud.
* **Harnais :** **Continue.dev** (autocomplétion) + **Cline / Roo Code** (agentique).
* **Moteur Local :** **LM Studio Server** ou **Ollama** avec un modèle *Qwen 2.5/3 Coder 7B/14B* chargé à 100% en VRAM (latence zéro, 0 € de coût récurrent).
* **Moteur Cloud :** OpenRouter appelant **DeepSeek V4-Pro** ou **Claude Sonnet 5.0** pour les refactorings d'envergure.
* **Coût Réel :** **< 3 € à 8 € TTC / mois**.

#### 💻 Profil 2 : Développeur sur PC Portable Nomade (CPU / APU sans CUDA)
* **Architecture Recommandée :** 100% Cloud optimisé.
* **Harnais :** **Trae Pro (~11,00 € TTC / mois)** pour une solution tout-en-un clé en main, OU **VS Code standard + Cline + OpenRouter**.
* **Modèles Clés :** **DeepSeek V4-Flash** (tâches courantes) et **Claude Sonnet 5.0 / Qwen 3.8-Max** (architecture).
* **Coût Réel :** **5 € à 15 € TTC / mois**.

#### 🏢 Profil 3 : Développeur en Entreprise & Grands Comptes
* **Architecture Recommandée :** Conformité, Sécurité et Rétention Zéro.
* **Harnais :** **GitHub Copilot Enterprise (~43 € TTC / 35,90 € HT par siège)** ou **Cursor Teams (~44 € TTC / 36,80 € HT par siège)**.
* **Bénéfices :** Facturation unique, conformité RGPD/SOC2, étanchéité stricte des données de code propriétaire.
