# 🚀 Projet : Audit & Référentiel des Solutions de Développement par IA (Août 2026)

## 📌 Présentation du Projet
Ce projet constitue un observatoire et un référentiel méthodologique complet sur l'ensemble des solutions de développement assisté par Intelligence Artificielle (IDE dérivés, extensions VS Code, applications desktop, agents CLI, passerelles universelles et modèles de fondation) à date d'**Août 2026**.

Le projet est conçu pour être **pérenne, modulaire et actualisable tous les 6 mois** sans réinventer la méthodologie d'audit.

---

## 📂 Arborescence du Projet

```text
Audit_Harness_2026/
├── README.md                                    # Présentation générale et guide de navigation
├── Guide_Complet_Solutions_Dev_IA_2026.md      # Le livrable maître complet avec tableaux détaillés (1 ligne / modèle & 1 ligne / forfait)
│
├── protocol/                                   # Méthodologie et processus de ré-audit semestriel
│   ├── 01_methodologie_audit.md                # Taxonomie en 4 couches et principes de veille
│   ├── 02_grille_evaluation_standardisee.md    # Gabarit d'analyse pour nouveaux outils / modèles
│   └── 03_protocole_mise_a_jour_semestrielle.md# Procédure de mise à jour à 6 mois (Fév. 2027)
│
└── data/                                       # Fiches de données détaillées par catégorie
    ├── 01_ide_natifs_et_forks.md               # Cursor, Windsurf/Devin, Trae, Zed, Augment, Void
    ├── 02_extensions_harnais_vscode.md         # GitHub Copilot (AI Credits), Cline, Roo Code, Continue, Qoder, CodeGeeX
    ├── 03_applications_desktop_et_local.md     # LM Studio Bionic, Claude Desktop, ChatGPT Desktop, Kimi
    ├── 04_agents_cli_et_frameworks.md          # Claude Code, Aider, Hermes Agent, OpenClaw, OpenHands
    ├── 05_passerelles_et_agregateurs.md        # OpenRouter, Together AI, Ollama, LM Studio Server
    └── 06_fournisseurs_modeles_et_grilles_api.md# Tarifs API détaillés en € au 1M tokens (Claude 5.0, GPT-5.6, DeepSeek V4, Qwen 3.8, Mistral, Kimi, GLM)
```

---

## 🧭 Guide Rapide de Consultation

1. **Pour une vision d'ensemble immédiate et comparative :**
   * Consultez directement le document maître : [`Guide_Complet_Solutions_Dev_IA_2026.md`](./Guide_Complet_Solutions_Dev_IA_2026.md).
   * **Tableaux formatés :** 1 ligne par modèle pour l'API (triés par prix d'entrée), et 1 ligne par forfait SaaS (avec prix HT et TTC en Euros, et liens officiels vers chaque page tarifaire).
2. **Pour analyser un outil spécifique ou ses liens officiels :**
   * Consultez le dossier [`data/`](./data/) classé par catégorie technique.
3. **Pour ré-exécuter l'audit dans 6 mois :**
   * Suivez les étapes décrites dans [`protocol/03_protocole_mise_a_jour_semestrielle.md`](./protocol/03_protocole_mise_a_jour_semestrielle.md).

---

## 🛠️ Rappel des 4 Couches d'Analyse
* **Couche 1 (Harnais) :** L'interface développeur (IDE Fork, Extension VS Code, Desktop GUI, Agent CLI).
* **Couche 2 (Passerelle) :** Le connecteur / routeur (OpenRouter, Together AI, Ollama, LM Studio Localhost).
* **Couche 3 (Modèle) :** Le laboratoire d'IA (Anthropic Claude 5.0, OpenAI GPT-5.6 / o3, DeepSeek V4, Qwen 3.8, Mistral, Moonshot Kimi K3, Zhipu GLM-5.3).
* **Couche 4 (Modèle Éco) :** Forfait SaaS captif ($3–$200/mois) vs BYOK API au token (€/1M tokens) vs Local GPU (0 €).
