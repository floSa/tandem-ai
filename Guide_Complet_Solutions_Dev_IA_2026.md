# Guide de référence des solutions de développement par IA

**Édition Septembre 2026** · document généré le 2026-09-15 depuis `catalog/` · prochaine révision prévue le 2027-03-15

> [!NOTE]
> Ce document est **généré**. Toute correction se fait dans `catalog/`, puis `python3 pipeline/build_guide.py`.
> Une modification faite ici sera écrasée à la prochaine génération.

## État de vérification

| Couche | Couverture |
| :-- | :-- |
| Mesures de benchmark | 1 275 sur 18 benchmarks |
| Modèles au catalogue | 194 |
| Tarifs API relevés sur page officielle | 25 / 194 |
| Forfaits d'abonnement relevés | 13 |
| Harnais re-vérifiés | 4 / 18 |
| Taux de change USD→EUR | 0.92 — **non vérifié** |

> [!WARNING]
> Le taux de change n'est pas vérifié : **toutes les valeurs en euros de ce document en héritent**. Les montants en dollars, eux, sont relevés sur les pages officielles.

---

## 1. Architecture conceptuelle : la taxonomie en quatre couches

Évaluer une solution de développement assisté par IA suppose de découpler quatre
choses que le marketing mélange volontiers : l'interface, le transport, le modèle
et la facturation. Un même modèle donne des résultats différents selon le harnais
qui l'exécute, et un même harnais change de prix du tout au tout selon le régime
de facturation choisi.

```
┌────────────────────────────────────────────────────────────────────────┐
│ COUCHE 1 — LE HARNAIS D'EXÉCUTION                                      │
│ IDE dérivés · extensions VS Code · applications desktop · agents CLI   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │  REST · API OpenAI · MCP · ACP
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 2 — LA PASSERELLE                                               │
│ agrégateurs cloud · serveurs locaux compatibles OpenAI · accès direct  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 3 — LE FOURNISSEUR DE MODÈLE                                    │
│ laboratoires propriétaires · laboratoires à poids ouverts              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 4 — LE MODÈLE ÉCONOMIQUE                                        │
│ forfait SaaS · facturation au token (BYOK) · auto-hébergement          │
└────────────────────────────────────────────────────────────────────────┘
```

La couche 1 n'est pas neutre. Sur Terminal-Bench, le référentiel recense des
dizaines de harnais différents pour les mêmes modèles, et l'écart qu'ils
produisent dépasse souvent l'écart entre deux modèles concurrents. C'est la
raison d'être de ce document : un score ne se lit jamais sans son harnais.

---

## 2. Facturation depuis la France

Deux régimes coexistent, et ils ne produisent pas le même débit pour le même
prix affiché.

**Plateformes facturant en dollars via Stripe.** Un particulier français se voit
appliquer la TVA de 20 % au paiement : un forfait affiché à 20 $ donne lieu à un
débit de 24 $. Un professionnel qui renseigne son numéro de TVA
intracommunautaire bascule en autoliquidation : la facture est émise à 0 % de TVA
et le montant débité est strictement le montant hors taxes.

**Plateformes affichant un prix en euros TTC.** Le prix européen intègre déjà la
TVA. Le professionnel ne bénéficie alors d'aucune autoliquidation sur ce canal.

Les colonnes « € HT » et « € TTC » des tableaux qui suivent sont **calculées**,
jamais saisies : elles dérivent d'un taux de change unique et d'un taux de TVA
uniques, déclarés dans `catalog/_meta.yaml`. Quand le taux bouge, tout le
document suit.

Un point de vigilance qui coûte cher en pratique : **ne pas confondre un
abonnement de chat grand public avec une consommation d'API**. Les deux
s'expriment en dollars par mois mais ne financent pas la même chose, et seul le
second passe à l'échelle d'une équipe.

---

## 3. Panorama des harnais

La colonne *vérifié* indique si la fiche a été re-contrôlée à cette édition. Une fiche non re-contrôlée est signalée comme telle plutôt que présentée comme à jour.

### 3.1 IDE dérivés

| Outil | Éditeur | Capacités | Forfaits | Vérifié |
| :-- | :-- | :-- | :-- | :-- |
| [Cursor](https://cursor.com) | Anysphere, Inc. | BYOK, modèles locaux, MCP | Hobby, Individual, Teams | 2026-09-15 |
| [Trae](https://trae.ai) | ByteDance | MCP | — | non |
| [Void IDE](https://voideditor.com) *(maintenance)* | Communauté open-source | BYOK, modèles locaux | — | non |
| [Windsurf / Devin](https://devin.ai) | Cognition AI | BYOK, MCP | — | non |
| [Zed](https://zed.dev) | Zed Industries, Inc. | BYOK, modèles locaux | — | non |

> **Cursor —** Les paliers Pro+ (60 $) et Ultra (200 $) de l'édition précédente ne figurent plus.

### 3.2 Extensions VS Code

| Outil | Éditeur | Capacités | Forfaits | Vérifié |
| :-- | :-- | :-- | :-- | :-- |
| Cline | Collectif open-source | BYOK, modèles locaux, MCP, gratuit | — | non |
| [Continue](https://continue.dev) | Continue Dev, Inc. | BYOK, modèles locaux, gratuit | — | non |
| [GitHub Copilot](https://github.com/features/copilot) | GitHub / Microsoft | — | Free, Pro, Pro+, Max | 2026-09-15 |
| Roo Code | Collectif open-source | BYOK, modèles locaux, MCP, gratuit | — | non |

> **GitHub Copilot —** Modèle de crédits confirmé : 15 $ (Pro), 70 $ (Pro+), 200 $ (Max). Complétions illimitées sur tout forfait payant.

### 3.3 Applications desktop

| Outil | Éditeur | Capacités | Forfaits | Vérifié |
| :-- | :-- | :-- | :-- | :-- |
| [ChatGPT Desktop](https://openai.com/chatgpt/desktop) | OpenAI, LLC | — | — | non |
| [Claude Desktop](https://claude.ai/download) | Anthropic, PBC | MCP | Free, Pro, Max | 2026-09-15 |
| [LM Studio](https://lmstudio.ai) | Element Labs, Inc. | modèles locaux, gratuit | — | non |

### 3.4 Agents CLI

| Outil | Éditeur | Capacités | Forfaits | Vérifié |
| :-- | :-- | :-- | :-- | :-- |
| [Aider](https://aider.chat) | Paul Gauthier (open-source) | BYOK, modèles locaux, gratuit | — | non |
| [Claude Code](https://docs.claude.com/en/docs/claude-code) | Anthropic, PBC | MCP | Pro, Max | 2026-09-15 |
| [Kimi Code CLI](https://platform.kimi.ai) | Moonshot AI | — | — | non |
| [OpenHands](https://all-hands.dev) | All-Hands-AI | BYOK, gratuit | — | non |

> **Claude Code —** Confirmé inclus dans Pro ; explicitement exclu du forfait Free.

### 3.5 Passerelles

| Outil | Éditeur | Capacités | Forfaits | Vérifié |
| :-- | :-- | :-- | :-- | :-- |
| [Ollama](https://ollama.com) | Ollama | modèles locaux, gratuit | — | non |
| [OpenRouter](https://openrouter.ai) | OpenRouter, Inc. | — | — | non |

---

## 4. Forfaits d'abonnement

Montants calculés au taux de 0.92 $/€ et à une TVA de 20%. La colonne **€ HT** est ce que débite un professionnel en autoliquidation ; la colonne **€ TTC** ce que débite un particulier.

| Éditeur | Produit | Forfait | Affiché | € HT (pro) | € TTC | Inclus | Source |
| :-- | :-- | :-- | --: | --: | --: | :-- | :-- |
| Anthropic | Claude | **Free** | gratuit | 0,00 € | 0,00 € | Chat web, iOS, Android et desktop. Claude Code non inclus. | [page](https://claude.com/pricing) |
| Anthropic | Claude | **Pro** | $20 | 18,40 € | 22,08 € | Usage étendu, accès Opus, projets étendus, Claude for Microsoft 365. Inclut Claude Code. | [page](https://claude.com/pricing) |
| Anthropic | Claude | **Max** | $100 | 92,00 € | 110,40 € | 5x ou 20x l'usage de Pro, limites de sortie supérieures, accès prioritaire. | [page](https://claude.com/pricing) |
| Anysphere | Cursor | **Hobby** | gratuit | 0,00 € | 0,00 € | Requêtes Agent limitées, accès Composer. | [page](https://cursor.com/pricing) |
| Anysphere | Cursor | **Individual** | $20 | 18,40 € | 22,08 € | Limites étendues sur Agent, modèles frontier, MCP, skills, hooks, agents cloud. | [page](https://cursor.com/pricing) |
| Anysphere | Cursor | **Teams** | $40/u | 36,80 € | 44,16 € | Facturation centralisée, marketplace interne, SSO SAML/OIDC, mode privé. | [page](https://cursor.com/pricing) |
| GitHub | GitHub Copilot | **Free** | gratuit | 0,00 € | 0,00 € | 2 000 complétions/mois, 24+ modèles dont Haiku 4.5 et GPT-5 mini. | [page](https://github.com/features/copilot/plans) |
| GitHub | GitHub Copilot | **Pro** | $10 | 9,20 € | 11,04 € | Complétion et next-edit illimitées, 15 $ de crédits mensuels. | [page](https://github.com/features/copilot/plans) |
| GitHub | GitHub Copilot | **Pro+** | $39 | 35,88 € | 43,06 € | 70 $ de crédits mensuels, 4x+ l'usage de Pro. | [page](https://github.com/features/copilot/plans) |
| GitHub | GitHub Copilot | **Max** | $100 | 92,00 € | 110,40 € | 200 $ de crédits mensuels, 2,9x+ l'usage de Pro+. | [page](https://github.com/features/copilot/plans) |
| Mistral AI | Mistral Vibe | **Free** | gratuit | 0,00 € | 0,00 € | Messages et recherches limités, 10 $/mois de crédits API. | [page](https://mistral.ai/pricing) |
| Mistral AI | Mistral Vibe | **Pro** | $14.99 | 13,79 € | 16,55 € | Capacité de code étendue, 15 $/mois de crédits API. 5,99 $ pour les étudiants vérifiés. | [page](https://mistral.ai/pricing) |
| Mistral AI | Mistral Vibe | **Team** | $24.99/u | 22,99 € | 27,59 € | Minimum 50 $/mois, 30 Go de stockage par utilisateur, vérification de domaine. | [page](https://mistral.ai/pricing) |

---

## 5. Tarifs API au million de tokens

Une ligne par modèle, triée par coût d'entrée croissant. Seuls figurent les modèles dont le tarif a été relevé sur la page officielle du fournisseur : un modèle absent de ce tableau n'est pas un modèle sans tarif, c'est un tarif non encore vérifié.

| Fournisseur | Modèle | Rôle | Contexte | Entrée $ | Cache $ | Sortie $ | Entrée € HT | Sortie € HT | Relevé le |
| :-- | :-- | :-- | --: | --: | --: | --: | --: | --: | :-- |
| Z.ai (Zhipu AI) | **GLM-4.7-Flash** | Gratuit avec limites de débit | — | gratuit | gratuit | gratuit | 0,00 € | 0,00 € | 2026-09-15 |
| Z.ai (Zhipu AI) | **GLM-5.3-Flash** | Flash économique | — | $0.15 | $0.03 | $0.5 | 0,14 € | 0,46 € | 2026-09-15 |
| OpenAI | **GPT-5.6 Luna** | Flash / économique | — | $0.2 | $0.02 | $1.2 | 0,18 € | 1,10 € | 2026-09-15 |
| DeepSeek | **DeepSeek Flash** | Flash ultra-économique | 1000k | $0.3 | $0.006 | $1.2 | 0,28 € | 1,10 € | 2026-09-15 |
| Google DeepMind | **Gemini 3.5 Flash-Lite** | Ultra-économique | — | $0.3 | $0.03 | $2.5 | 0,28 € | 2,30 € | 2026-09-15 |
| Google DeepMind | **Gemini 3.8 Flash** | Flash génération courante | — | $0.75 | $0.075 | $3.75 | 0,69 € | 3,45 € | 2026-09-15 |
| Moonshot | **Kimi K2.6** | — | 262k | $0.95 | $0.16 | $4 | 0,87 € | 3,68 € | 2026-09-15 |
| Moonshot | **Kimi K2.7 Code** | Dédié développement logiciel | 262k | $0.95 | $0.19 | $4 | 0,87 € | 3,68 € | 2026-09-15 |
| Anthropic | **Claude Haiku 4.5** | Flash / économique | 200k | $1 | $0.1 | $5 | 0,92 € | 4,60 € | 2026-09-15 |
| DeepSeek | **DeepSeek V4-Pro** | Flagship raisonnement | 1000k | $1.32 | $0.044 | $3.96 | 1,21 € | 3,64 € | 2026-09-15 |
| Z.ai (Zhipu AI) | **GLM-5.3** | Flagship raisonnement et code | — | $1.4 | $0.26 | $4.4 | 1,29 € | 4,05 € | 2026-09-15 |
| Google DeepMind | **Gemini 3.5 Flash** | — | — | $1.5 | $0.15 | $9 | 1,38 € | 8,28 € | 2026-09-15 |
| Anthropic | **Claude Sonnet 5** | Référence ingénierie logicielle | 200k | $2 | $0.2 | $10 | 1,84 € | 9,20 € | 2026-09-15 |
| Google DeepMind | **Gemini 3.1 Pro** | Flagship raisonnement | 200k | $2 | $0.2 | $12 | 1,84 € | 11,04 € | 2026-09-15 |
| OpenAI | **GPT-5.6 Terra** | Équilibré développeur | — | $2 | $0.2 | $12 | 1,84 € | 11,04 € | 2026-09-15 |
| OpenAI | **o3** | Raisonnement algorithmique | — | $2 | $0.5 | $8 | 1,84 € | 7,36 € | 2026-09-15 |
| OpenAI | **GPT-5.4** | — | — | $2.5 | $0.25 | $15 | 2,30 € | 13,80 € | 2026-09-15 |
| Moonshot | **Kimi K3** | Flagship multimodal | 1048k | $3 | $0.3 | $15 | 2,76 € | 13,80 € | 2026-09-15 |
| OpenAI | **GPT-5.6 Sol** | Haute capacité multimodal | — | $4 | $0.4 | $20 | 3,68 € | 18,40 € | 2026-09-15 |
| Anthropic | **Claude Opus 5** | Flagship architecture et cas complexes | 200k | $5 | $0.5 | $25 | 4,60 € | 23,00 € | 2026-09-15 |
| OpenAI | **GPT-5.5** | — | — | $5 | $0.5 | $30 | 4,60 € | 27,60 € | 2026-09-15 |
| Anthropic | **Claude Fable 5.1** | Flagship raisonnement étendu | 200k | $10 | $0.25 | $50 | 9,20 € | 46,00 € | 2026-09-15 |
| OpenAI | **GPT-6 Astra** | Flagship nouvelle génération | — | $10 | $1 | $50 | 9,20 € | 46,00 € | 2026-09-15 |
| OpenAI | **o3-pro** | Raisonnement extrême | — | $20 | — | $80 | 18,40 € | 73,60 € | 2026-09-15 |
| OpenAI | **GPT-5.5 Pro** | — | — | $30 | — | $180 | 27,60 € | 165,60 € | 2026-09-15 |

**Particularités tarifaires**

- **DeepSeek Flash** — heures creuses : $0.15 en entrée, $0.6 en sortie (01:00-04:00 et 06:00-10:00, lundi-vendredi).
- **DeepSeek V4-Pro** — heures creuses : $0.66 en entrée, $1.98 en sortie (01:00-04:00 et 06:00-10:00, lundi-vendredi).
- **Gemini 3.1 Pro** — Tarif ≤200k tokens. Au-delà : 4,00 / 0,40 / 18,00.
- **Gemini 3.8 Flash** — Tarif promotionnel. Au-delà : 1,50 / 0,15 / 7,50. (jusqu'au 2026-12-31).

---

## 6. Performance mesurée

18 benchmarks suivis, 14 écartés (saturés, obsolètes ou mesurant de la mémorisation). Chaque rejet est documenté avec son motif dans `catalog/benchmarks.yaml`.

### 6.1 État de l'art par benchmark

| Benchmark | Ce qu'il mesure | Meilleur score | Modèle | Harnais |
| :-- | :-- | --: | :-- | :-- |
| **Aider polyglot** | Édition de code existant dans plusieurs langages, au format diff. | 88.0% | `gpt-5-2025-08-07_high` | — |
| **GPQA diamond** | Questions scientifiques de niveau doctorat, hors de portée d'une recherche | 95.8% | `gpt-6-astra_max` | — |
| **HLE** | Humanity's Last Exam : questions expertes volontairement très difficiles. | 46.5% | `claude-fable-5-1_xhigh` | — |
| **METR Time Horizons** | Durée de tâche humaine qu'un modèle accomplit avec 50% de réussite. Exprim | 0.85 min | `claude-mythos-preview-early` | — |
| **SWE-Bench verified** | Résolution de vraies issues GitHub Python, patch validé par les tests du d | 83.5% | `claude-opus-4-7_max` | — |
| **Terminal Bench** | Tâches multi-étapes en ligne de commande : navigation, exécution, vérifica | 84.7% | `gpt-5.5_unknown` | NexAU-AHE |
| **APEX-Agents** | Capacités agentiques sur tâches expertes. | 47.4% | `claude-fable-5-1_unknown` | — |
| **ARC-AGI-2** | Raisonnement abstrait sur grilles, résistant à la mémorisation. | 95.0% | `gpt-6-astra_max` | — |
| **Cybench** | Résolution de défis de cybersécurité type CTF. | 93.0% | `claude-opus-4-6_unknown` | — |
| **DeepSWE** | Ingénierie logicielle sur tâches longues. | 74.1% | `gpt-6-astra_xhigh` | mini-swe-agent |
| **FrontierCode** | Génération de code sur problèmes récents, conçu contre la contamination. | 53.5% | `claude-fable-5_unknown` | claude-code |
| **GDPval** | Tâches professionnelles réelles évaluées par des experts du métier. | 49.7% | `gpt-5.2-2025-12-11_none` | — |
| **GSO-Bench** | Optimisation de code sous contrainte de performance mesurée. | 47.1% | `claude-opus-4-8_unknown` | OpenHands |
| **MirrorCode** | Benchmark de code récent, résistant à la contamination. | 73.3% | `claude-fable-5-1_high` | — |
| **OSWorld 2.0** | Pilotage d'un vrai bureau graphique (fenêtres, applications). | 31.4% | `claude-opus-5_max` | — |
| **Remote Labor Index** | Capacité à accomplir des missions freelance réellement rémunérées. | 16.1% | `claude-fable-5` | — |
| **SciCode** | Implémentation de code scientifique à partir d'énoncés de recherche. | 62.0% | `claude-fable-5-1_max` | — |
| **The Agent Company** | Tâches de travail réalistes en entreprise simulée (navigation, outils, col | 52.4% | `DeepSeek-V3.2-Exp` | — |

> [!IMPORTANT]
> **Égalités statistiques.** Sur les benchmarks suivants, les deux premiers ne sont pas séparés au seuil de 95 % : les classer l'un devant l'autre est une erreur de lecture.
>
> - **Terminal Bench** — `gpt-5.5_unknown` et `gpt-5.5_unknown` (écart 0.016, intervalle 0.058)
> - **GPQA diamond** — `gpt-6-astra_max` et `gemini-3.8-flash_high` (écart 0.004, intervalle 0.038)
> - **SWE-Bench verified** — `claude-opus-4-7_max` et `gpt-5.5-pre-release_xhigh` (écart 0.029, intervalle 0.048)
> - **DeepSWE** — `gpt-6-astra_xhigh` et `gemini-3.8-flash_high` (écart 0.003, intervalle 0.032)

### 6.2 Coût mesuré et effort de raisonnement

Les suffixes `low` à `max` ne désignent pas des modèles différents mais le **budget de raisonnement** accordé au même modèle. Son effet dépasse souvent l'écart entre deux modèles concurrents, et il se paie. Le coût ci-dessous est celui **réellement mesuré pendant le run**, pas un prix au token.

Benchmark de référence sur cet axe : **DeepSWE**, mesuré sous un harnais unique (`mini-swe-agent`) — l'écart observé s'impute donc au modèle et à son effort, pas au harnais.

| Modèle | Effort le plus bas | Effort le plus haut | Gain | Surcoût |
| :-- | :-- | :-- | --: | --: |
| `gpt-6-astra` | low — 67.0% à $2.19 | max — 73.2% à $12.37 | +6.2 pts | ×5.7 |
| `gemini-3.8-flash` | medium — 71.0% à $1.97 | high — 73.8% à $2.36 | +2.8 pts | ×1.2 |
| `claude-opus-5` | low — 58.1% à $1.66 | max — 73.7% à $11.84 | +15.5 pts | ×7.1 |
| `gpt-5.6-sol` | low — 45.4% à $1.07 | max — 72.7% à $8.39 | +27.3 pts | ×7.8 |
| `claude-fable-5` | low — 59.6% à $3.76 | max — 69.7% à $21.63 | +10.1 pts | ×5.8 |
| `gpt-5.6-terra` | low — 24.1% à $0.43 | max — 69.6% à $4.95 | +45.6 pts | ×11.6 |
| `grok-4.6` | low — 41.6% à $1.04 | xhigh — 66.7% à $5.50 | +25.1 pts | ×5.3 |
| `gpt-5.6-luna` | low — 1.6% à $0.07 | max — 67.2% à $3.03 | +65.6 pts | ×41.8 |
| `gpt-5.5` | low — 27.0% à $1.20 | xhigh — 67.0% à $7.23 | +40.1 pts | ×6.0 |
| `gemini-3.7-flash` | low — 53.8% à $1.83 | high — 65.3% à $2.18 | +11.5 pts | ×1.2 |
| `claude-opus-4-8` | low — 40.8% à $2.29 | max — 59.0% à $13.22 | +18.2 pts | ×5.8 |
| `claude-sonnet-5` | low — 30.5% à $2.19 | max — 53.8% à $26.40 | +23.3 pts | ×12.1 |
| `glm-5.2` | high — 36.3% à $2.84 | max — 43.8% à $3.92 | +7.5 pts | ×1.4 |
| `gemini-3.5-flash` | medium — 37.4% à $7.34 | high — 36.1% à $3.45 | -1.3 pts | ×0.5 |

Un gain faible pour un surcoût élevé signale que l'effort supplémentaire ne s'achète plus. Certains modèles **régressent** au palier maximal.

---

## Ce que ce document n'affirme pas

Un référentiel honnête énonce ses limites avant ses conclusions.

- **Aucun classement de « meilleur modèle ».** La question est mal posée : un
  score appartient au triplet *(modèle × harnais × effort de raisonnement)*.
- **Aucun score composite maison.** Agréger des benchmarks aux protocoles
  différents produit un nombre sans signification.
- **Aucune interpolation.** Un modèle non mesuré sur un benchmark reste vide.
- **Le coût par tâche de benchmark n'est pas le coût d'une journée de
  développement.** Il en donne un ordre de grandeur comparatif, rien de plus.
- **Rien sur la latence perçue, l'ergonomie du harnais ni la qualité durable du
  code produit** — trois facteurs qui pèsent souvent plus que quelques points de
  benchmark.

---

## Sources et licences

Données de benchmark : [Epoch AI — *Capabilities & Benchmarking*](https://epoch.ai/benchmarks), sous licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Tarifs relevés sur les pages officielles des fournisseurs, dont l'URL et la date de consultation figurent dans `catalog/`. Attributions complètes : [`ATTRIBUTION.md`](./ATTRIBUTION.md).

