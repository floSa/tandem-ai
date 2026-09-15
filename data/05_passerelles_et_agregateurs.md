> [!WARNING]
> Fiche antérieure à la mise en place du pipeline de sourçage. Les chiffres qu'elle
> contient n'ont pas de source vérifiable et sont en attente de re-vérification.
> Données validées : [`catalog/`](../catalog/).

# Référentiel Data : Passerelles Universelles & Agrégateurs Multi-Modèles (Août 2026)

## 1. OpenRouter (L'Agrégateur Universel de Référence)
* **Nom officiel :** OpenRouter
* **Éditeur :** OpenRouter, Inc.
* **Liens Officiels :**
  * Site web : [https://openrouter.ai](https://openrouter.ai)
  * Modèles & Tarifs en direct : [https://openrouter.ai/models](https://openrouter.ai/models)
  * Documentation : [https://openrouter.ai/docs](https://openrouter.ai/docs)
* **Nature Technique :** Passerelle API universelle fournissant un point d'accès unifié et standardisé (format OpenAI) à plus de 300 modèles de fondation issus de tous les laboratoires mondiaux.
* **Intégration & Rôle Pivot :**
  * Permet d'utiliser n'importe quel modèle (Anthropic Claude 5, OpenAI GPT-5.6, DeepSeek V4, Qwen 3, GLM-5, Mistral) dans n'importe quel harnais ou IDE (Cursor, Cline, Roo Code, Aider, Continue, Hermes Agent) avec **une seule clé API unique**.
  * Routage intelligent : bascule automatique vers un autre hébergeur en cas de panne de l'endpoint principal.
  * Gestion du prompt caching transparente pour réduire drastiquement les coûts d'input répétés.
* **Modèle Économique :**
  * Aucun abonnement mensuel obligatoire.
  * Paiement 100% à l'usage réel au million de tokens, aux tarifs exacts des fournisseurs (avec transparence totale sur les remises par lot ou les coûts de mise en cache).

---

## 2. Together AI / Fireworks AI / Groq / DeepInfra (Hébergeurs Spécialisés)
* **Together AI :** [https://together.ai](https://together.ai) — Spécialiste de l'hébergement rapide de modèles open-weights (DeepSeek, Qwen, Mistral, Llama) avec tarifs très compétitifs.
* **Fireworks AI :** [https://fireworks.ai](https://fireworks.ai) — Moteur d'inférence ultra-rapide optimisé pour les modèles de code et d'appels d'outils (*Function Calling*).
* **Groq :** [https://groq.com](https://groq.com) — Inférence temps réel sur puces LPU matérielles dédiées, idéal pour l'autocomplétion instantanée.
* **DeepInfra :** [https://deepinfra.com](https://deepinfra.com) — Hébergement de modèles open-weights à très bas coût à la seconde / au token.

---

## 3. Serveurs Locaux OpenAI-Compatibles (Auto-hébergement)
* **Ollama :** CLI ultra-simple (`ollama serve`) exposant une API locale sur le port `11434`.
* **LM Studio Local Server :** Interface graphique permettant de charger n'importe quel fichier GGUF et d'activer un serveur local sur le port `1234`.
* **vLLM / SGLang :** Moteurs d'inférence Python haute performance pour serveurs dédiés sous Linux/WSL2 avec GPU Nvidia, permettant de saturer les capacités de calcul locales avec un débit maximal de tokens/seconde.
