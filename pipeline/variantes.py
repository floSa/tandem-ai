#!/usr/bin/env python3
"""
Identité d'un modèle contre réglage de son exécution.

Les sources de benchmark nomment une configuration, pas un modèle : `gpt-6-astra`
mesuré à effort maximal s'y appelle `gpt-6-astra_max`, et Opus 4.6 avec 32 000
jetons de réflexion, `claude-opus-4-6_32K`. Ces suffixes décrivent un RÉGLAGE
D'EXÉCUTION — le modèle facturé, lui, est le même, au même tarif unitaire.

Distinguer les deux est la thèse du référentiel : un score appartient au triplet
(modèle × harnais × effort). Encore faut-il que la règle soit écrite une seule
fois. Elle a existé en deux versions divergentes — l'ingestion ne retirait que
les efforts nommés, la tarification retirait aussi les budgets de réflexion — et
la matrice de couverture affichait donc quatre lignes pour un seul Opus 4.6,
poussant hors du classement les modèles réellement distincts.
"""
from __future__ import annotations

import re

# Effort nommé, budget de réflexion (`_32K`), ou mode (`_thinking`).
SUFFIXE = re.compile(
    r"^(?P<base>.+)_(?P<variante>none|minimal|low|medium|high|xhigh|max|promax"
    r"|thinking|nonthinking|unknown|\d+K)$"
)

# Budget de réflexion : un nombre de jetons, pas un palier d'effort. Il ne peut
# donc pas rejoindre le vocabulaire `effort`, qui est ordonné.
BUDGET = re.compile(r"^\d+K$")


def base(identifiant: str | None) -> str | None:
    """Identifiant du modèle, débarrassé de son réglage d'exécution."""
    if not identifiant:
        return identifiant
    m = SUFFIXE.match(identifiant)
    return m.group("base") if m else identifiant


def variante(identifiant: str | None) -> str | None:
    """Le réglage porté par l'identifiant, ou None s'il n'en porte aucun."""
    if not identifiant:
        return None
    m = SUFFIXE.match(identifiant)
    return m.group("variante") if m else None


def budget(identifiant: str | None) -> str | None:
    """Budget de réflexion porté par l'identifiant (`32K`), le cas échéant."""
    v = variante(identifiant)
    return v if v and BUDGET.match(v) else None
