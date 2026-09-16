# Attribution des sources

Ce référentiel agrège des données produites par des tiers. Toute republication,
totale ou partielle, doit conserver les attributions ci-dessous.

## Epoch AI — Capabilities & Benchmarking

Les scores de benchmark de `catalog/scores.yaml` et le registre
`catalog/benchmarks.yaml` proviennent de cette source, à l'exception de
Terminal-Bench 4.0 (section suivante).

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

## Terminal-Bench 4.0 — tbench.ai

Epoch AI ne relaie que Terminal-Bench 2.0. Les scores de Terminal-Bench 4.0 sont lus
sur le leaderboard officiel par `pipeline/tbench_ingest.py`.

> Terminal-Bench, *Terminal-Bench 4.0 leaderboard*. Consulté sur
> https://www.tbench.ai/leaderboard/terminal-bench/4.0

Le leaderboard ne publie pas de licence explicite pour ses données : elles sont
citées avec leur source, score par score (`source_url`), et ne sont pas
redistribuées sous forme brute (`sources/raw/` n'est pas versionné).

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

Deux régimes coexistent, dans deux fichiers distincts :

| Périmètre | Licence | Fichier |
| :-- | :-- | :-- |
| Code du pipeline et tests | MIT | [`LICENSE`](LICENSE) |
| Méthodologie, documentation, curation, Guide | CC BY 4.0 | [`LICENSE-CONTENT`](LICENSE-CONTENT) |

Le contenu est sous CC BY 4.0 par compatibilité avec les données d'Epoch AI dont il
dérive : retenir la même licence préserve la chaîne d'attribution en aval.
