# Sources & Protocole de Collecte

Ce document est **indépendant de tout agent**. Il décrit où trouver la donnée et
sous quelles conditions elle entre au catalogue. Claude Code, Antigravity, Codex,
Cursor ou un humain doivent pouvoir l'appliquer à l'identique.

---

## 1. Règle fondamentale

> **Aucun chiffre n'entre au catalogue sans une source vérifiable, une date de
> vérification, et un niveau de provenance.**

Un chiffre sans source n'est pas une donnée : c'est une rumeur. Le validateur
(`pipeline/validate.py`) refuse la publication si cette règle est violée.

En cas de doute, la bonne action est **de laisser le champ vide et marqué
`unverified`**, jamais de recopier une valeur plausible. Un trou déclaré est
exploitable ; un chiffre inventé contamine tout le document.

---

## 2. Hiérarchie de provenance

Définie dans `catalog/_meta.yaml`, du plus fiable au moins fiable. Quand deux
sources se contredisent, **la plus haute dans cette liste gagne**, et la
contradiction est consignée dans le champ `note`.

| Niveau | Signification | Exemple |
| :-- | :-- | :-- |
| `independent_run` | Un tiers a **exécuté** le benchmark lui-même | Epoch AI, Vals AI |
| `official_pricing_page` | Page `/pricing` du fournisseur, consultée directement | anthropic.com/pricing |
| `independent_leaderboard` | Leaderboard officiel du benchmark | tbench.ai, swebench.com |
| `official_docs` | Documentation technique du fournisseur | docs.claude.com/models |
| `self_reported` | Chiffre publié par le lab **sur son propre modèle** | blog d'annonce, model card |
| `community` | Agrégateur tiers, article, comparatif | billets de blog, forums |
| `inferred` | Déduit ou estimé | jamais publiable sans mention |

**Le cas `self_reported` est le piège principal des benchmarks.** Un lab qui
publie le score de son propre modèle choisit son harnais, son budget de calcul
au test, et le moment de la mesure. Ces scores ne sont pas faux, mais ils ne sont
pas comparables à un run indépendant. Ils doivent être **étiquetés comme tels
dans toute publication**.

---

## 3. Sources de benchmarks

### 3.1 Epoch AI — source primaire du référentiel

| | |
| :-- | :-- |
| Page | https://epoch.ai/benchmarks |
| Donnée brute | https://epoch.ai/data/benchmark_data.zip |
| Client Python | `pip install epochai` (API Airtable, conserve les relations) |
| Authentification | **aucune** pour le ZIP |
| Licence | CC-BY 4.0 — attribution obligatoire |
| Ingestion | `python3 pipeline/epoch_ingest.py` |

Environ 80 benchmarks, ~1 000 modèles. **La convention de nommage encode la
provenance** : un fichier suffixé `_external.csv` est collecté auprès d'un tiers,
un fichier sans suffixe est un run exécuté par Epoch (provenance la plus haute,
avec logs publics consultables).

Colonnes structurantes à ne jamais perdre :

- `Agent` / `Harness` / `Scaffold` — le harnais qui exécutait le modèle
- `Reasoning effort`, `Step budget`, `Tool setting`, `Pass@k` — le protocole
- `stderr` / `Accuracy SE` — l'incertitude de mesure
- `Source` / `Source Link` — la provenance amont
- `Log viewer` — la preuve reproductible (runs internes uniquement)
- `scale` (dans `benchmark_metadata.csv`) — certains benchmarks publient en %,
  d'autres en fraction. **Toujours normaliser avant de comparer.**

### 3.2 Artificial Analysis — recoupement et tarifs

| | |
| :-- | :-- |
| API | `https://artificialanalysis.ai/api/v2` |
| Docs | https://artificialanalysis.ai/data-api/docs |
| Authentification | clé API en en-tête `x-api-key` |
| Palier gratuit | 100 requêtes / 24 h — `GET /language/models/free` |
| Licence | attribution visible obligatoire, redistribution à négocier |

Intérêt particulier : le palier gratuit expose **à la fois** les scores et les
tarifs (`price_1m_input_tokens`, `price_1m_output_tokens`,
`price_1m_cache_hit_tokens`). C'est la seule source qui croise les deux.
Attention : l'Intelligence Index est **versionné** (v4.3 au moment de l'écriture) —
comparer deux éditions d'index différentes n'a pas de sens.

Clé à placer dans `.env` (jamais commitée — voir `.gitignore`).

### 3.3 Leaderboards officiels — à consulter en cas de doute

| Benchmark | Leaderboard |
| :-- | :-- |
| SWE-bench (Verified / Pro / Multimodal) | https://swebench.com |
| Terminal-Bench | https://www.tbench.ai/leaderboard |
| LiveCodeBench | https://livecodebench.github.io/leaderboard.html |
| Aider Polyglot | https://aider.chat/docs/leaderboards/ |
| ARC-AGI | https://arcprize.org/leaderboard |
| LMArena (préférence humaine) | https://lmarena.ai/leaderboard |
| METR (horizons temporels) | https://metr.org |
| Vals AI (évaluations indépendantes) | https://vals.ai |

---

## 4. Sources tarifaires

**Les tarifs ne s'obtiennent QUE sur la page `/pricing` officielle du
fournisseur.** Aucun comparatif tiers, aucun article, aucune mémoire de modèle de
langage ne fait foi. Les URL de départ sont dans `catalog/labs.yaml`
(champ `pricing_url`).

La saisie se fait dans `catalog/pricing_verified.yaml`, jamais directement dans
`models.yaml` : ce dernier est reconstruit par `pipeline/apply_pricing.py`.

Procédure par modèle :

1. Ouvrir la `pricing_url` du lab.
2. Relever, **en USD** : entrée standard, entrée en cache, sortie, par 1M tokens.
3. Relever aussi la fenêtre de contexte et l'identifiant d'API exact (`api_model_id`).
4. Renseigner `catalog/models.yaml` :

```yaml
pricing:
  currency: USD            # jamais EUR — la conversion est calculée au build
  input_per_1m: 3.00
  input_cached_per_1m: 0.30
  output_per_1m: 15.00
  source:
    url: https://www.anthropic.com/pricing
    verified_on: 2026-09-15
    status: official_pricing_page
    note: "Tarif standard hors batch."
```

**Aucune valeur en euros ne se saisit à la main.** Le taux de change et la TVA
vivent dans `catalog/_meta.yaml` et la conversion est recalculée à chaque build :
c'est ce qui garantit que tout le document reste cohérent quand le taux bouge.

Points d'attention récurrents :

- distinguer l'abonnement grand public (ChatGPT Plus) de la consommation API ;
- relever les tarifs **dynamiques** (DeepSeek applique des heures creuses) ;
- vérifier la région de facturation (les tarifs Alibaba diffèrent selon la zone) ;
- noter les tarifs batch / asynchrones séparément du tarif temps réel.

### Quand la page ne porte pas le modèle mesuré

Les identifiants mesurés par les benchmarks ne sont presque jamais ceux qui figurent
sur une page tarifaire. Trois cas, trois traitements — et un interdit.

| Ce qu'on observe | Traitement | Champ |
| :-- | :-- | :-- |
| L'identifiant est un **instantané daté** du modèle tarifé (`gpt-5-2025-08-07` pour `gpt-5`) | Recopier le tarif à l'identique | `applies_to` |
| L'identifiant porte un **suffixe de réglage** (`_none`, `_32K`, `_high`) | Ne rien saisir : `apply_pricing.py` propage le tarif de la base. Un réglage d'exécution ne change pas le tarif unitaire, seulement la consommation | automatique |
| Le modèle **n'a pas de tarif éditeur** : poids ouverts, génération retirée de la grille, alias de revendeur (`openai/…`, `zai-org/…`), pré-version jamais commercialisée | Le classer avec son motif | `no_public_price` |

**L'interdit :** ne jamais mettre dans `applies_to` un modèle simplement « proche ». Une
génération voisine n'est pas le même produit — sur la grille Anthropic de septembre 2026,
Opus 4.1 est à 15/75 quand Opus 4.6 est à 5/25. Dans le doute, ne rien saisir.

Cette classification n'est pas un confort de présentation : sans elle, un modèle à poids
ouverts reste indéfiniment inscrit au plan de travail comme « tarif à relever », et le
reste-à-faire affiché est faux.

---

## 5. Veille des nouveaux entrants

### Modèles

Un modèle entre au catalogue **s'il apparaît dans au moins une source de
benchmark vérifiable**. On n'ajoute pas un modèle sur la foi d'une annonce.
`pipeline/seed_catalog.py` applique cette règle automatiquement.

### Harnais et outils

**Balayage fournisseur par fournisseur — obligatoire, et à faire en premier.**

La veille par mots-clés ne suffit pas : elle trouve les outils dont on parle, pas ceux
qui existent. En septembre 2026, elle avait manqué **Qwen Studio**, **Qwen Code** et
**Kimi Work**, et laissé supprimer à tort **ChatGPT Desktop** — quatre outils de
laboratoires pourtant déjà au catalogue.

Pour **chaque lab** de `catalog/labs.yaml`, poser les quatre mêmes questions :

| Question | Où chercher |
| :-- | :-- |
| Une application desktop officielle ? | page produit du lab, section « download » |
| Un agent CLI officiel ? | dépôt GitHub de l'organisation du lab |
| Une extension IDE officielle ? | marketplace VS Code, plugins JetBrains |
| Un forfait couvrant ces outils ? | page `/pricing` déjà consultée pour les tarifs |

**Une réponse négative se consigne au même titre qu'une découverte**, dans le bloc
`tooling` de `catalog/labs.yaml` : date du balayage, et ce qui a été trouvé — y compris
« rien ».

```yaml
tooling:
  checked_on: '2026-09-15'
  note: >-
    AUCUN harnais officiel. Les agents en circulation sont communautaires ;
    la doc d'intégration du lab ne référence que des outils tiers.
```

`pipeline/worklist.py` réclame un balayage tant que `checked_on` est absent, et se tait
dès qu'il est renseigné. Un fournisseur sans harnais devient alors un constat daté, pas
un trou qu'on redécouvre à chaque édition.

**Ce que le balayage de septembre 2026 avait manqué**, faute d'avoir été fait : Google
Antigravity et son CLI — alors que Gemini CLI, encore catalogué par les sources
secondaires, avait cessé de servir les requêtes grand public le 18/06/2026 — ainsi que
Grok Build (xAI), Mistral Vibe et Muse Code (Meta). Quatre laboratoires majeurs, aucun
harnais au catalogue.

Requêtes complémentaires, en anglais, pour les nouveaux entrants :

```
"AI code editor" OR "VS Code fork" 2026
"autonomous coding agent" CLI terminal 2026
"coding agent" harness open source 2026
site:github.com "coding agent" stars:>2000 pushed:>2026-01-01
```

Pour chaque candidat, remplir la grille de
[`02_grille_evaluation_standardisee.md`](./02_grille_evaluation_standardisee.md).

Pour chaque outil **déjà au catalogue**, vérifier à chaque édition :

1. le projet est-il toujours actif, racheté, renommé, archivé ?
2. les URL officielles répondent-elles encore ?
3. le modèle économique a-t-il changé de nature (forfait → crédits, etc.) ?
4. la date de dernier commit du dépôt, si open-source.

---

## 6. Conservation des traces

Toute donnée brute téléchargée va dans `sources/raw/` (non versionné). À chaque
édition publiée, `pipeline/changelog.py` fige un instantané du catalogue dans
`snapshots/`, qui sert de base de comparaison à l'édition suivante.

C'est ce qui permet de répondre à « qu'est-ce qui a changé depuis février ? »
sans relire le document.
