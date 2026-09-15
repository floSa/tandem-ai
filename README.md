# Observatoire des solutions de développement par IA

Référentiel ouvert sur l'offre du marché — **modèles de fondation** et **harnais
de développement** — évalués sur benchmarks, avec leurs coûts, leurs sources et
leurs dates de vérification.

La particularité tient en une phrase : **un score n'est pas un attribut d'un
modèle**, mais d'un triplet *(modèle × harnais × protocole)*. Sur Terminal-Bench,
le catalogue recense 52 harnais distincts, et l'écart entre le meilleur et le
moins bon dépasse souvent l'écart entre deux modèles. Ce référentiel est construit
pour rendre cet effet visible plutôt que pour le masquer derrière un classement.

État actuel : **11 fournisseurs · 194 modèles · 18 benchmarks · 1 263 mesures
dont 286 avec coût réellement mesuré · 25 grilles tarifaires et 21 forfaits
relevés sur sources officielles · 18 harnais dont 13 re-vérifiés.**

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
« Couverture » affiche les trous en pointillés plutôt que de les interpoler, et
le validateur distingue un modèle *pas encore mesuré* d'un modèle *dont le tarif
reste à relever*.

**4. Le coût se mesure, il ne se déduit pas.** Le prix au token ne permet pas de
comparer deux niveaux d'effort d'un même modèle : le tarif est identique, seule
la consommation change. Le référentiel exploite le coût réellement dépensé
pendant les runs — 286 mesures — pour croiser performance et dépense.

---

## Architecture

```
catalog/        SOURCE DE VÉRITÉ — le seul endroit édité à la main
  _meta.yaml      taux de change, TVA, seuils de fraîcheur, hiérarchie de provenance
  labs.yaml       fournisseurs + URL de tarification officielles
  models.yaml     modèles + tarifs + provenance
  tools.yaml      harnais (IDE, extensions, CLI, desktop, passerelles) + conformité
  plans.yaml      forfaits d'abonnement SaaS
  pricing_verified.yaml  tarifs API relevés à la main (seul endroit de saisie)
  benchmarks.yaml registre raisonné des benchmarks        ← généré
  scores.yaml     mesures (modèle × harnais × protocole)  ← généré

pipeline/       ingestion, validation, génération, recoupement
tests/          34 tests des invariants du protocole
content/        fragments narratifs du Guide (écrits à la main)
site/           page interactive                          ← généré
data/           fiches par catégorie                      ← généré
protocol/       méthodologie (fait autorité)
snapshots/      instantanés datés, base des changelogs
```

Le Guide Markdown et `site/index.html` sont **générés**. On ne les corrige pas à
la main : on corrige `catalog/` puis on régénère.

---

## Utilisation

```bash
pip install pyyaml
```

```bash
python3 pipeline/worklist.py                        # ← COMMENCER ICI : quoi vérifier maintenant
python3 pipeline/epoch_ingest.py --force-download   # rafraîchir les benchmarks
python3 pipeline/seed_catalog.py                    # détecter les nouveaux modèles
python3 pipeline/apply_pricing.py                   # injecter les tarifs relevés
python3 pipeline/validate.py                        # contrôle qualité (code 1 si erreur)
python3 pipeline/build_site.py                      # régénérer la page
python3 pipeline/apply_pricing.py                   # injecter les tarifs relevés
python3 pipeline/crosscheck_aa.py                   # recouper avec une seconde source
python3 pipeline/build_guide.py                     # régénérer le Guide et les fiches
python3 pipeline/changelog.py                       # diff avec l'édition précédente
python3 -m unittest discover -s tests               # tests du pipeline
```

Deux portes avant publication : les **tests du pipeline** (34 tests sur le code
qui produit la donnée) puis **`validate.py`** (la donnée elle-même). Tant que
l'une échoue, on ne publie pas. Les deux tournent en CI à chaque push et une fois
par mois, avec un contrôle que les sorties générées n'ont pas divergé du
catalogue.

`worklist.py` est le point d'entrée : il dit ce qui n'a jamais été vérifié, ce qui
a dépassé sa date de péremption, avec l'URL à ouvrir et les pièges d'accès connus
pour chaque fournisseur (redirections, 403, 404 déjà rencontrés).

Une mise à jour ne consiste pas seulement à remplir les cases vides : elle
re-contrôle aussi l'existant, et tout écart constaté alimente le changelog au lieu
d'être corrigé silencieusement.

Le protocole opératoire complet — quoi relever, dans quel ordre, quels pièges —
est dans [`protocol/06_protocole_operatoire.md`](./protocol/06_protocole_operatoire.md).
Avec Claude Code, le skill `audit-referentiel` l'applique directement :
« mets à jour le référentiel en suivant le protocole ». Les autres agents lisent
[`AGENTS.md`](./AGENTS.md).

---

## État de la vérification

| Couche | État |
| :-- | :-- |
| Benchmarks | ✅ 1 263 mesures sourcées (Epoch AI, CC-BY) |
| Identité des modèles | ✅ 194 modèles |
| Taux de change | ✅ taux de référence BCE du 15/09/2026 |
| Tarifs API | 🟡 25 relevés sur page officielle — Mistral, Alibaba, xAI, MiniMax, Meta restants |
| Forfaits d'abonnement | 🟡 21 relevés (Anthropic, GitHub, Cursor, Mistral, Zed, Trae) |
| Harnais | 🟡 13 re-vérifiés sur 18 |
| Conformité | 🟡 6 harnais sur 18 |
| Source de recoupement | ⚠️ Artificial Analysis implémenté, clé non configurée |

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
