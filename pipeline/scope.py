#!/usr/bin/env python3
"""
Périmètre temporel du référentiel : ce qui est encore actuel, ce qui ne l'est plus.

Deux questions distinctes, partagées par l'ingestion, l'amorce, le validateur et le
plan de travail — d'où ce module unique plutôt que quatre seuils recopiés :

  • un MODÈLE est obsolète quand il a été publié avant la fenêtre glissante
    (`scope.model_window_months` dans catalog/_meta.yaml) ;
  • un BENCHMARK est en sommeil quand son modèle mesuré le plus récent accuse un
    retard de plus de `freshness.benchmark_dormant_after_days` sur le modèle le plus
    récent du catalogue. Le retard se compte par rapport au catalogue, pas à la date
    du jour : si aucun laboratoire ne publie pendant un trimestre, aucun benchmark
    n'est accusé à tort.
"""
from __future__ import annotations

import collections
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "catalog" / "_meta.yaml"


def meta() -> dict:
    return yaml.safe_load(META.read_text(encoding="utf-8")) or {}


def cutoff(today: date | None = None, months: int | None = None) -> str:
    """Date ISO avant laquelle un modèle est obsolète."""
    today = today or date.today()
    if months is None:
        months = (meta().get("scope") or {}).get("model_window_months", 12)
    y, m = divmod(today.year * 12 + today.month - 1 - months, 12)
    m += 1
    # 31 mars − 1 mois : on se rabat sur le dernier jour du mois cible.
    for d in (today.day, 30, 29, 28):
        try:
            return date(y, m, d).isoformat()
        except ValueError:
            continue
    raise AssertionError("inaccessible")


def dormant_after_days() -> int:
    return (meta().get("freshness") or {}).get("benchmark_dormant_after_days", 90)


def dormant_benchmarks(scores: list[dict], days: int) -> list[tuple[str, str, int]]:
    """Benchmarks en sommeil : (nom, dernier modèle mesuré, retard en jours)."""
    latest: dict[str, str] = collections.defaultdict(str)
    for s in scores:
        r = s.get("model_released_on")
        if r and r > latest[s["benchmark"]]:
            latest[s["benchmark"]] = r
    if not latest:
        return []
    front = date.fromisoformat(max(latest.values())[:10])
    out = []
    for b, r in latest.items():
        lag = (front - date.fromisoformat(r[:10])).days
        if lag > days:
            out.append((b, r, lag))
    return sorted(out, key=lambda x: -x[2])
