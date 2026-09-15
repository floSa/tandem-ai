> [!NOTE]
> Fiche antérieure au pipeline de sourçage : ses chiffres n'ont pas de source
> attachée et n'ont pas tous été re-vérifiés. Certains restent exacts, d'autres
> non — la distinction est faite dans [`catalog/`](../catalog/), qui fait foi.

# Référentiel Data : Fournisseurs de Modèles (Labs IA) & Grilles Tarifaires API Détaillées (Août 2026)

*Note de conversion : Les tarifs sont indiqués en Euros (€) au taux de référence standard (1 $ USD ≈ 0,92 € EUR). Les équivalents en dollars sont précisés entre parenthèses.*

---

## 1. Anthropic (Gamme Claude 5.0)
* **Console API :** [https://console.anthropic.com](https://console.anthropic.com)
* **Page Tarifs :** [https://anthropic.com/pricing](https://anthropic.com/pricing)
* **Présence Outils Développeur :**
  * Application Desktop : **Claude Desktop** (compatible serveurs MCP).
  * Agent CLI officiel : **Claude Code CLI** (`@anthropic-ai/claude-code`).
  * Extension VS Code native : Non (utilisé via Cline, Roo Code, Claude Code).
* **Forfaits SaaS (Grand Public / Pro) :**
  * **Claude Free :** 0,00 € / mois (accès web/desktop limité).
  * **Claude Pro :** 18,40 € HT (~22,00 € TTC) / mois ($20) — Inclut Claude Desktop (MCP) et **Claude Code CLI**.
  * **Claude Max 5x :** 92,00 € HT (~110,40 € TTC) / mois ($100) — 5x le quota de requêtes de Pro.
  * **Claude Max 20x :** 184,00 € HT (~220,80 € TTC) / mois ($200) — 20x le quota de requêtes de Pro.
* **Grille Tarifaire API (par 1M de tokens) :**
  * **Claude Opus 5.0 (Flagship Raisonnement & Architecture Complexe - 200k/1M contexte) :**
    * Entrée Standard : **4,60 €** ($5.00)
    * Entrée avec Prompt Caching : **0,46 €** ($0.50)
    * Sortie (Génération) : **23,00 €** ($25.00)
  * **Claude Sonnet 5.0 (Référence Mondiale Ingénierie Logicielle & Code - 200k/1M contexte) :**
    * Entrée Standard : **1,84 €** ($2.00)
    * Entrée avec Prompt Caching : **0,184 €** ($0.20)
    * Sortie (Génération) : **9,20 €** ($10.00)
  * **Claude Haiku 4.5 (Modèle Flash / Économique - 200k contexte) :**
    * Entrée Standard : **0,92 €** ($1.00)
    * Entrée avec Prompt Caching : **0,092 €** ($0.10)
    * Sortie (Génération) : **4,60 €** ($5.00)

---

## 2. OpenAI (Gamme GPT-5.6 & Raisonnement o3)
* **Console API :** [https://platform.openai.com](https://platform.openai.com)
* **Page Tarifs :** [https://openai.com/api/pricing](https://openai.com/api/pricing)
* **Présence Outils Développeur :**
  * Application Desktop : **ChatGPT Desktop** (avec *Work with Apps* connecté à VS Code / Xcode / Terminal).
  * Outils CLI / Canvas : Intégrés dans l'environnement de bureau et web.
* **Forfaits SaaS (Grand Public / Pro) :**
  * **ChatGPT Free :** 0,00 € / mois (modèle GPT-5.6 Luna).
  * **ChatGPT Go :** 7,36 € HT (~8,80 € TTC) / mois ($8).
  * **ChatGPT Plus :** 18,40 € HT (~22,00 € TTC) / mois ($20) — Espace Canvas, Deep Research, quotas Sol/Terra.
  * **ChatGPT Pro :** 92,00 € à 184,00 € HT (~110,40 € à 220,80 € TTC) / mois ($100–$200) — Puissance o3 maximale.
  * **ChatGPT Business :** 18,40 € HT / utilisateur / mois ($20/u) — Minimum 2 utilisateurs, rétention zéro.
* **Grille Tarifaire API (par 1M de tokens) :**
  * **GPT-5.6 Sol (Flagship Haute Capacité Multimodal - 256k/1M contexte) :**
    * Entrée Standard : **4,60 €** ($5.00)
    * Entrée avec Prompt Caching : **0,46 €** ($0.50)
    * Sortie (Génération) : **27,60 €** ($30.00)
  * **o3 / o3-pro (Modèle Raisonnement Pur & Logique Algorithmique) :**
    * o3 : Entrée : **1,84 €** ($2.00) | Sortie : **7,36 €** ($8.00)
    * o3-pro : Entrée : **18,40 €** ($20.00) | Sortie : **73,60 €** ($80.00)
  * **GPT-5.6 Terra (Équilibré Développeur - 256k contexte) :**
    * Entrée Standard : **2,30 €** ($2.50)
    * Entrée avec Prompt Caching : **0,23 €** ($0.25)
    * Sortie (Génération) : **13,80 €** ($15.00)
  * **GPT-5.6 Luna (Modèle Flash / Économique - 128k contexte) :**
    * Entrée Standard : **0,92 €** ($1.00)
    * Entrée avec Prompt Caching : **0,092 €** ($0.10)
    * Sortie (Génération) : **5,52 €** ($6.00)

---

## 3. DeepSeek (Gamme Unifiée DeepSeek V4 & V4-Pro)
* **Plateforme API :** [https://platform.deepseek.com](https://platform.deepseek.com)
* **Documentation :** [https://api-docs.deepseek.com](https://api-docs.deepseek.com)
* **Présence Outils Développeur :**
  * Application Desktop : Non (utilisé via LM Studio, Jan ou clients communautaires).
  * Extension VS Code : Non (utilisé via Cline, Roo Code, Continue ou Aider).
* **Forfaits SaaS :** Aucun (modèle 100% à l'usage API ou open-weights gratuits en local).
* **Grille Tarifaire API Dynamique (par 1M de tokens) :**
  * *Heures de Pointe (Peak) :* 01:00–04:00 & 06:00–10:00 UTC (Lun-Ven).
  * *Heures Creuses (Off-Peak) :* Reste de la semaine et weekends (**50% de réduction automatique**).
  * **DeepSeek V4-Pro (Flagship avec Mode Raisonnement Intégré - 1M Contexte) :**
    * Entrée Standard (Off-Peak) : **0,61 €** ($0.66) | (Peak) : **1,21 €** ($1.32)
    * Entrée avec Cache (Off-Peak) : **0,15 €** ($0.16) | (Peak) : **0,30 €** ($0.33)
    * Sortie (Off-Peak) : **1,82 €** ($1.98) | (Peak) : **3,64 €** ($3.96)
  * **DeepSeek V4-Flash (Modèle Flash Ultra-Économique - 1M Contexte) :**
    * Entrée Standard (Off-Peak) : **0,20 €** ($0.22) | (Peak) : **0,40 €** ($0.44)
    * Entrée avec Cache (Off-Peak) : **0,046 €** ($0.05) | (Peak) : **0,10 €** ($0.11)
    * Sortie (Off-Peak) : **0,61 €** ($0.66) | (Peak) : **1,21 €** ($1.32)

---

## 4. Qwen / Alibaba Cloud (Gamme Qwen 3.8 & 3.7)
* **Portail Model Studio :** [https://www.alibabacloud.com/product/model-studio](https://www.alibabacloud.com/product/model-studio)
* **Documentation Tarifs :** [https://www.alibabacloud.com/help/en/model-studio](https://www.alibabacloud.com/help/en/model-studio)
* **Présence Outils Développeur :**
  * Application Desktop : **QoderWork**.
  * Extension VS Code : **Qoder / Tongyi Lingma**.
* **Forfaits SaaS / Forfaits Développeur :**
  * **Qwen Coding Plan :** ~46,00 € HT (~55,20 € TTC) / mois ($50) — Quota mensuel fixe pour modèles Qwen3.8-Max et Qwen3.7-Plus dans les IDEs.
* **Grille Tarifaire API (par 1M de tokens - Région Internationale Singapour) :**
  * **Qwen3.8-Max (Flagship MoE Multimodal 2.4T - 1M Contexte) :**
    * Entrée Standard : **1,84 €** ($2.00)
    * Entrée avec Prompt Caching : **0,184 €** ($0.20)
    * Sortie (Génération) : **5,52 €** ($6.00)
  * **Qwen3.7-Plus (Modèle Équilibré Dev & Code - 128k Contexte) :**
    * Entrée Standard : **0,32 €** ($0.35)
    * Entrée avec Cache : **0,046 €** ($0.05)
    * Sortie : **1,15 €** ($1.25)
  * **Qwen3.8-Flash-Next / Qwen3.7-Flash (Modèle Flash Ultra-Rapide - 1M Contexte) :**
    * Entrée Standard : **0,046 €** ($0.05)
    * Entrée avec Cache : **0,009 €** ($0.01)
    * Sortie : **0,184 €** ($0.20)

---

## 5. Mistral AI (Gamme Codestral & Mistral Large)
* **Console API :** [https://console.mistral.ai](https://console.mistral.ai)
* **Plateforme Vibe :** [https://vibe.mistral.ai](https://vibe.mistral.ai)
* **Présence Outils Développeur :**
  * Application Desktop : PWA installable **Mistral Vibe** (ex-Le Chat).
  * Extension VS Code : Extension officielle **Mistral Vibe** et intégration **Continue.dev**.
* **Forfaits SaaS :**
  * **Mistral Le Chat Pro (Vibe Pro) :** 15,00 € à 18,40 € HT / mois ($16–$20) — Canvas, génération d'agents.
* **Grille Tarifaire API (par 1M de tokens) :**
  * **Codestral (Modèle Spécialisé Code & Dépôts Complets - 256k Contexte) :**
    * Entrée Standard : **0,276 €** ($0.30)
    * Entrée avec Cache : **0,028 €** ($0.03)
    * Sortie : **0,828 €** ($0.90)
  * **Mistral Large 2 (Flagship Raisonnement Général - 128k Contexte) :**
    * Entrée Standard : **1,84 €** ($2.00)
    * Entrée avec Cache : **0,184 €** ($0.20)
    * Sortie : **5,52 €** ($6.00)
  * **Mistral Small (Modèle Flash Économique - 128k Contexte) :**
    * Entrée Standard : **0,092 €** ($0.10)
    * Entrée avec Cache : **0,009 €** ($0.01)
    * Sortie : **0,276 €** ($0.30)

---

## 6. Moonshot AI (Gamme Kimi K3 & K2.7 Code)
* **Plateforme API :** [https://platform.moonshot.cn](https://platform.moonshot.cn)
* **Portail Kimi :** [https://kimi.moonshot.cn](https://kimi.moonshot.cn)
* **Présence Outils Développeur :**
  * Application Desktop : **Kimi Work**.
  * Agent CLI officiel : **Kimi Code CLI** (binaire autonome ACP).
  * Extension VS Code : **Kimi Code Extension**.
* **Forfaits SaaS Grand Public & Pro :**
  * **Adagio (Free) :** 0,00 € / mois.
  * **Moderato :** 17,48 € HT / mois ($19) — K2.6, crédits d'entrée Kimi Code.
  * **Allegretto :** 35,88 € HT / mois ($39) — Quotas renforcés.
  * **Allegro :** 91,08 € HT / mois ($99) — Essaims d'agents professionnels.
  * **Vivace :** 183,08 € HT / mois ($199) — Capacité maximale 300 agents.
* **Grille Tarifaire API (par 1M de tokens) :**
  * **Kimi K3 (Flagship 2.8T Multimodal - 1M Contexte) :**
    * Entrée Standard : **2,76 €** ($3.00)
    * Entrée avec Cache Hit : **0,276 €** ($0.30)
    * Sortie : **13,80 €** ($15.00)
  * **Kimi K2.7 Code (Modèle Dédié Développement Logiciel - 256k Contexte) :**
    * Entrée Standard : **0,874 €** ($0.95)
    * Entrée avec Cache Hit : **0,175 €** ($0.19)
    * Sortie : **3,68 €** ($4.00)
  * **Kimi K2.5 (Modèle MoE Économique - 256k Contexte) :**
    * Entrée Standard : **0,552 €** ($0.60)
    * Entrée avec Cache Hit : **0,092 €** ($0.10)
    * Sortie : **2,76 €** ($3.00)

---

## 7. Zhipu AI / GLM (Gamme GLM-5.3 & GLM-5.2)
* **Plateforme Internationale :** [https://z.ai](https://z.ai) | **Chine :** [https://bigmodel.cn](https://bigmodel.cn)
* **Extension CodeGeeX :** [https://codegeex.cn](https://codegeex.cn)
* **Présence Outils Développeur :**
  * Extension VS Code : **CodeGeeX**.
* **Forfaits SaaS (GLM Coding Plan) :**
  * **Coding Plan Lite :** 16,56 € HT / mois ($18) — Crédits hebdomadaires pour GLM-5.3/5.2.
  * **Coding Plan Pro :** 73,60 € HT / mois ($80) — Usage intensif pour IDEs.
  * **Coding Plan Max :** 154,56 € HT / mois ($168) — Quota maximal.
* **Grille Tarifaire API (par 1M de tokens) :**
  * **GLM-5.3 / GLM-5.2 (Flagship Raisonnement & Code - 128k Contexte) :**
    * Entrée Standard : **1,288 €** ($1.40) *(ou 0,35 € – 0,50 € via OpenRouter/Together)*
    * Entrée avec Cache : **0,129 €** ($0.14)
    * Sortie : **4,048 €** ($4.40)
  * **GLM-5.3-Flash / GLM-4.7-Flash (Modèle Flash Ultra-Rapide - 128k Contexte) :**
    * Entrée Standard : **0,00 € (Gratuit)**
    * Sortie : **0,00 € (Gratuit)** avec limites de requêtes par minute.
