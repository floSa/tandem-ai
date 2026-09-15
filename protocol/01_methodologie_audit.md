# Protocole Méthodologique d'Audit des Solutions de Dev IA (Août 2026)

## 1. Contexte & Objectif
Ce protocole établit une méthode de veille, de classification et d'évaluation comparative des outils d'assistance au développement par Intelligence Artificielle (IDE, extensions, applications desktop, agents CLI, passerelles et modèles de fondation).

L'objectif est d'éliminer toute ambiguïté conceptuelle en séparant distinctement le client d'interface, la passerelle de transport, le modèle sous-jacent et le modèle économique.

---

## 2. Les 4 Couches Structurelles Fondamentales

```
┌────────────────────────────────────────────────────────────────────────┐
│ COUCHE 1 : LE HARNAIS D'EXÉCUTION (Interface Développeur)              │
│ - IDE Dérivés IA (Forks VS Code / Éditeurs natifs)                    │
│ - Extensions Agentes VS Code / JetBrains                              │
│ - Applications Desktop Autonomes (GUI & Espaces de travail)            │
│ - Agents CLI & Frameworks Terminal Autonomes                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (Protocole : REST, OpenAI API, MCP)
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 2 : LA PASSERELLE / ROUTEUR D'ACCÈS                            │
│ - Agrégateurs Cloud Multi-Fournisseurs (OpenRouter, Together AI)       │
│ - Serveurs Locaux OpenAI-Compatibles (Ollama, LM Studio Server, vLLM)  │
│ - Connexion Directe Provider (Clé API officielle du Lab)               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 3 : LE FOURNISSEUR DE MODÈLE (Le Laboratoire IA)               │
│ - Laboratoires Propriétaires (Anthropic, OpenAI, Moonshot AI)          │
│ - Laboratoires Mixtes / Open-Weights (DeepSeek, Qwen/Alibaba, Mistral) │
│ - Spécialistes Open-Source / Recherche (Nous Research, Zhipu AI)       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 4 : LE MODÈLE ÉCONOMIQUE                                        │
│ - Abonnement Forfaitaire SaaS (Quotas de requêtes rapides / crédits)   │
│ - Facturation à l'Usage / BYOK (Prix au 1M tokens : Input/Output/Cache)│
│ - Gratuité / Auto-hébergement (Modèles Open-Weights sur GPU local)     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Démarche de Recherche & Collecte de Données

Pour garantir la fraîcheur et la fiabilité des informations :
1. **Recherches en Anglais :** Les requêtes doivent cibler la documentation technique anglophone, les dépôts GitHub officiels et les pages `/pricing` officielles.
2. **Double Vérification des Modèles de Production :** Toujours vérifier les derniers identifiants de modèles (`model_id`) et les dépréciations d'anciens alias.
3. **Décomposition Précise des Tarifs API :**
   * Coût Input standard (*Cache Miss*).
   * Coût Input avec mise en cache (*Prompt Caching / Cache Hit*).
   * Coût Output (génération).
   * Variations horaires éventuelles (*Peak / Off-Peak hours*).
4. **Distinction entre Abonnements Grand Public et Crédits Développeurs :** Ne pas confondre un abonnement de chat grand public (ex: ChatGPT Plus à 20$/mois) avec une consommation API par token pour un agent de code.
