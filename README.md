# Observatoire des solutions de développement par IA

Référentiel ouvert sur l'offre du marché — **modèles de fondation** et **harnais
de développement** — évalués sur benchmarks, avec leurs coûts, leurs sources et
leurs dates de vérification.

La particularité tient en une phrase : **un score n'est pas un attribut d'un
modèle**, mais d'un triplet *(modèle × harnais × protocole)*. Sur Terminal-Bench,
le catalogue recense 52 harnais distincts, et l'écart entre le meilleur et le
moins bon dépasse souvent l'écart entre deux modèles. Ce référentiel est construit
pour rendre cet effet visible plutôt que pour le masquer derrière un classement.

État actuel : **11 fournisseurs · 194 modèles · 18 benchmarks · 1 263 mesures ·
25 grilles tarifaires et 13 forfaits relevés sur sources officielles · 18 harnais.**

---

## Consulter

| | |
| :-- | :-- |
| **Vue interactive** | [`site/index.html`](./site/index.html) — classements avec intervalles de confiance, effet du harnais, progression, couverture, prix × performance |
| **Méthodologie** | [`protocol/`](./protocol/) |
| **Données** | [`catalog/`](./catalog/) |

---

## Principes

**1. Aucun chiffre sans source vérifiable, date de relevé et niveau de provenance.**
En cas de doute, le champ reste vide et marqué `unverified`. Un trou déclaré est
exploitable ; un chiffre plausible mais inventé contamine tout le document.

**2. L'incertitude fait partie de la donnée.** Deux modèles dont les intervalles
de confiance à 95 % se chevauchent sont à égalité. Le validateur refuse les
classements qui l'ignorent — c'est aujourd'hui le cas des deux premiers de
SWE-bench Verified.

**3. Ce que le référentiel ne mesure pas est dit explicitement.** La vue
« Couverture » affiche les trous en pointillés plutôt que de les interpoler.

---

## Architecture

```
catalog/        SOURCE DE VÉRITÉ — le seul endroit édité à la main
  _meta.yaml      taux de change, TVA, seuils de fraîcheur, hiérarchie de provenance
  labs.yaml       fournisseurs + URL de tarification officielles
  models.yaml     modèles + tarifs + provenance
  tools.yaml      harnais (IDE, extensions, CLI, desktop, passerelles)
  plans.yaml      forfaits d'abonnement SaaS
  pricing_verified.yaml  tarifs API relevés à la main (seul endroit de saisie)
  benchmarks.yaml registre raisonné des benchmarks        ← généré
  scores.yaml     mesures (modèle × harnais × protocole)  ← généré

pipeline/       ingestion, validation, génération
site/           page interactive                          ← généré
protocol/       méthodologie (fait autorité)
snapshots/      instantanés datés, base des changelogs
data/           fiches Markdown par catégorie
```

Le Guide Markdown et `site/index.html` sont **générés**. On ne les corrige pas à
la main : on corrige `catalog/` puis on régénère.

---

## Utilisation

```bash
pip install pyyaml
```

```bash
python3 pipeline/epoch_ingest.py --force-download   # rafraîchir les benchmarks
python3 pipeline/seed_catalog.py                    # détecter les nouveaux modèles
python3 pipeline/apply_pricing.py                   # injecter les tarifs relevés
python3 pipeline/validate.py                        # contrôle qualité (code 1 si erreur)
python3 pipeline/build_site.py                      # régénérer la page
python3 pipeline/changelog.py                       # diff avec l'édition précédente
```

`validate.py` est la porte de sortie : tant qu'il échoue, on ne publie pas. Il
tourne aussi en CI à chaque push et une fois par mois, pour détecter les données
qui ont dépassé leur date de péremption.

Avec Claude Code, le skill `audit-referentiel` enchaîne ces étapes :
« mets à jour le référentiel », « y a-t-il de nouveaux harnais », « vérifie les prix ».
Les autres agents lisent [`AGENTS.md`](./AGENTS.md).

---

## État de la vérification

| Couche | État |
| :-- | :-- |
| Benchmarks | ✅ 1 263 mesures sourcées (Epoch AI, CC-BY) |
| Identité des modèles | ✅ 194 modèles |
| Tarifs API | 🟡 25 relevés sur page officielle (Anthropic, OpenAI, Google, DeepSeek, Moonshot, Z.ai) — Mistral, Alibaba, xAI restants |
| Forfaits d'abonnement | 🟡 13 relevés (Anthropic, GitHub, Cursor, Mistral) |
| Harnais | 🟡 4 re-vérifiés sur 18 |
| Taux de change | ⚠️ non vérifié |

Le [Guide 2026](./Guide_Complet_Solutions_Dev_IA_2026.md) et les fiches
[`data/`](./data/) sont antérieurs à ce pipeline. La confrontation aux pages
officielles donne un bilan nuancé : les noms de modèles sont réels et plusieurs
grilles tarifaires (Anthropic, Moonshot, Codestral) sont exactes, mais les prix
de mise en cache sont fréquemment faux et certains tarifs ont été attribués à la
mauvaise génération de modèle. Le détail figure en tête du Guide.

---

## Sources & licences

Données de benchmark : [Epoch AI — *Capabilities & Benchmarking*](https://epoch.ai/benchmarks),
sous [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Code sous MIT, contenu sous CC BY 4.0. Attributions complètes :
[`ATTRIBUTION.md`](./ATTRIBUTION.md).
