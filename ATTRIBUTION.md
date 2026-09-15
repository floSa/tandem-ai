# Attribution des sources

Ce référentiel agrège des données produites par des tiers. Toute republication,
totale ou partielle, doit conserver les attributions ci-dessous.

## Epoch AI — Capabilities & Benchmarking

La totalité des scores de benchmark de `catalog/scores.yaml` et du registre
`catalog/benchmarks.yaml` provient de cette source.

> Epoch AI, *Capabilities & Benchmarking*. Publié en ligne sur epoch.ai.
> Consulté sur https://epoch.ai/benchmarks

Licence : [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/).
Libre d'usage, de distribution et de reproduction **sous réserve de crédit**.

Epoch agrège elle-même des résultats externes qui conservent leur licence
d'origine ; le champ `source_url` de chaque score renvoie à la source amont.

```bibtex
@misc{EpochLLMBenchmarkingHub2024,
  title  = {{Capabilities & Benchmarking}},
  author = {{Epoch AI}},
  year   = {2026},
  url    = {https://epoch.ai/benchmarks}
}
```

## Artificial Analysis

`pipeline/crosscheck_aa.py` interroge cette API pour **recouper** les tarifs du
catalogue. Il n'écrit rien : il signale les écarts, qui s'arbitrent selon la
hiérarchie de provenance.

Si des données issues de cette API venaient à être **affichées**, leurs conditions
imposent une **attribution visible** sur la page concernée. En l'état, le
référentiel ne les publie pas — il s'en sert uniquement comme contre-témoignage.

Source : [Artificial Analysis](https://artificialanalysis.ai) —
https://artificialanalysis.ai/data-api/docs

## Fournisseurs de modèles

Les tarifs proviennent des pages officielles de chaque fournisseur. L'URL exacte
et la date de relevé sont portées par chaque entrée du catalogue
(`pricing.source`). Les marques citées appartiennent à leurs détenteurs
respectifs.

## Contenu propre à ce dépôt

La méthodologie (`protocol/`), les scripts (`pipeline/`) et la curation éditoriale
des benchmarks sont publiés sous la licence indiquée dans `LICENSE`.
