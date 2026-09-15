# Instructions pour les agents

Ce dépôt est un **référentiel de données**, pas une application. Sa valeur tient
entièrement à la traçabilité de ses chiffres : un chiffre sans source est un
défaut, au même titre qu'un test qui échoue.

Ce fichier est le point d'entrée pour tout agent (Claude Code, Antigravity,
Codex, Cursor, Copilot…). La méthodologie de référence est dans `protocol/`.

## Architecture

```
catalog/     ← SOURCE DE VÉRITÉ. C'est le seul endroit qu'on édite à la main.
pipeline/    ← scripts d'ingestion, validation et génération
site/        ← GÉNÉRÉ. Page HTML interactive.
data/        ← fiches Markdown par catégorie
protocol/    ← la méthodologie (fait autorité)
snapshots/   ← instantanés datés, base des changelogs
sources/raw/ ← données brutes téléchargées (non versionné)
```

Le Guide Markdown et `site/index.html` sont **générés**. Les corriger à la main
est inutile : le build suivant les écrase. On corrige dans `catalog/`.

Dans `catalog/`, deux fichiers sont eux-mêmes générés et ne s'éditent pas :
`benchmarks.yaml` et `scores.yaml` (voir `pipeline/epoch_ingest.py`).

## Les deux règles

1. **Aucun chiffre sans `source.url` + `verified_on` + `status`.** En cas de
   doute, laisser vide et marqué `unverified`. Ne jamais combler un trou avec une
   valeur plausible : c'est la faute la plus grave possible ici.
2. **Un score de benchmark appartient au triplet (modèle × harnais × protocole)**,
   jamais au modèle seul. Publier un classement sans nommer le harnais est une
   erreur méthodologique.

## Commandes

```bash
python3 pipeline/epoch_ingest.py --force-download   # rafraîchit les benchmarks
python3 pipeline/seed_catalog.py                    # amorce modèles et labs
python3 pipeline/validate.py                        # contrôle qualité (code 1 si erreur)
python3 pipeline/build_site.py                      # régénère la page
python3 pipeline/changelog.py                       # diff vs édition précédente
```

`validate.py` est la porte de sortie : **tant qu'il échoue, on ne publie pas.**
Ses alertes indiquent ce que le document n'a pas le droit d'affirmer — notamment
les classements dont les deux premiers ne sont pas séparés statistiquement.

## Dépendances

Python 3.10+ et `pyyaml`. Rien d'autre. La page HTML n'a aucune dépendance
externe hors la police Google Fonts.

## Licences

Les données de benchmark viennent d'Epoch AI sous CC-BY 4.0 : l'attribution est
obligatoire dans toute republication. Voir `ATTRIBUTION.md`.
