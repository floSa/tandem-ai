---
name: audit-referentiel
description: >-
  Met à jour le référentiel des solutions de développement par IA (modèles,
  harnais, tarifs, benchmarks). À utiliser dès que l'utilisateur veut rafraîchir
  l'audit, chercher de nouveaux modèles ou harnais, vérifier des tarifs, ingérer
  des benchmarks, régénérer le Guide ou la page HTML, ou produire le changelog
  d'une édition. Triggers : "mets à jour le référentiel", "y a-t-il de nouveaux
  harnais", "vérifie les prix", "rafraîchis les benchmarks", "publie l'édition".
---

# Mise à jour du référentiel Dev IA

## Ce qu'il faut comprendre avant d'agir

Le catalogue YAML dans `catalog/` est **la seule source de vérité**. Le Guide
Markdown et la page HTML en sont des sorties générées. **Ne jamais corriger un
chiffre dans le Guide** : il serait écrasé au build suivant. On corrige dans
`catalog/`, puis on régénère.

La méthodologie complète est dans `protocol/` et **fait autorité sur ce fichier** :

- `protocol/04_sources_et_collecte.md` — où trouver la donnée, hiérarchie de provenance
- `protocol/05_methodologie_benchmarks.md` — comment lire et publier un score

Les deux règles qui ne se négocient pas :

1. **Aucun chiffre sans source vérifiable + date de vérification.** En cas de
   doute : laisser vide et marqué `unverified`. Un trou déclaré vaut mieux qu'un
   chiffre inventé.
2. **Un score n'appartient pas à un modèle** mais au triplet
   (modèle × harnais × protocole). Ne jamais publier un classement sans dire sous
   quel harnais il a été obtenu.

## Boucle de travail

Quelle que soit la demande, terminer par :

```bash
python3 pipeline/validate.py && python3 pipeline/build_site.py
```

`validate.py` sort en code 1 s'il détecte une erreur bloquante. **Ne pas publier
tant qu'il échoue.** Ses alertes ne sont pas du bruit : elles disent ce que le
document n'a pas le droit d'affirmer.

---

## Modes

L'utilisateur arrive généralement avec une de ces demandes.

### « Y a-t-il de nouveaux modèles ? »

```bash
python3 pipeline/epoch_ingest.py --force-download   # re-télécharge la donnée amont
python3 pipeline/seed_catalog.py                    # ajoute les modèles nouvellement mesurés
python3 pipeline/validate.py
```

Puis rapporter : modèles apparus, labs concernés, et lesquels n'ont pas encore de
tarif. Un modèle n'entre au catalogue que s'il est mesuré quelque part — ne pas
l'ajouter à la main sur la foi d'une annonce.

### « Y a-t-il de nouveaux harnais ? »

Veille manuelle, requêtes en anglais (voir `protocol/04` §5). Pour chaque
candidat sérieux, remplir la grille de `protocol/02_grille_evaluation_standardisee.md`
et l'ajouter à `catalog/tools.yaml`.

Vérifier **aussi** les outils déjà catalogués : projet archivé, racheté, renommé,
URL morte, changement de modèle économique. Un outil mort doit passer en
`status: retired` avec sa date, pas disparaître — la disparition est une
information.

### « Vérifie / mets à jour les prix »

C'est le mode le plus exigeant, et il ne peut pas être automatisé : les tarifs ne
s'obtiennent que sur les pages `/pricing` officielles.

Pour chaque lab de `catalog/labs.yaml`, ouvrir `pricing_url`, relever en **USD**
l'entrée standard, l'entrée en cache et la sortie par 1M tokens, puis remplir
`catalog/models.yaml` avec le bloc `source` complet (url, `verified_on`,
`status: official_pricing_page`).

- Ne jamais saisir d'euros : la conversion est calculée au build depuis
  `catalog/_meta.yaml`.
- Penser à re-vérifier le taux de change lui-même et à passer `fx.status` à
  `verified` — sinon toutes les valeurs en euros restent marquées douteuses.
- Signaler les tarifs dynamiques (heures creuses), les variantes régionales et
  les tarifs batch dans `note`.

### « Rafraîchis les benchmarks »

```bash
python3 pipeline/epoch_ingest.py --force-download
python3 pipeline/validate.py
```

Pour ajouter ou retirer un benchmark du suivi, éditer le dictionnaire `CURATION`
dans `pipeline/epoch_ingest.py` — **pas** `catalog/benchmarks.yaml`, qui est
généré. Tout rejet se documente avec son motif dans `REJECTED`.

Traiter les alertes de saturation : un benchmark au-dessus de 92 % de son plafond
a perdu son pouvoir discriminant et doit être remplacé.

### « Mets tout à jour » (édition complète)

Dans l'ordre :

1. `python3 pipeline/epoch_ingest.py --force-download`
2. `python3 pipeline/seed_catalog.py`
3. veille harnais (manuelle) → `catalog/tools.yaml`
4. vérification tarifaire (manuelle) → `catalog/models.yaml`
5. `python3 pipeline/validate.py` — corriger jusqu'au vert
6. `python3 pipeline/changelog.py` — diff contre l'édition précédente
7. `python3 pipeline/build_site.py`
8. mettre à jour `audit.edition` dans `catalog/_meta.yaml`
9. commit avec le changelog en corps de message

### « Fais-moi un graphique de tel type »

Les vues existantes de `site/index.html` : classement (avec IC95), effet du
harnais, progression temporelle, couverture, prix × performance.

Pour une vue nouvelle, ajouter une fonction dans `DRAW` de
`pipeline/build_site.py` et un bouton dans `#kind`. Respecter la palette validée
déjà en place (variables `--s1`…`--s8`) et la contrainte de 3 séries maximum sur
les nuages de points.

---

## Erreurs à ne pas commettre

- Éditer le Guide ou `site/index.html` à la main → écrasé au build.
- Éditer `catalog/benchmarks.yaml` ou `catalog/scores.yaml` → générés.
- Saisir un prix en euros dans le catalogue.
- Publier un classement en ignorant une alerte de non-séparation statistique.
- Comparer des scores obtenus sous des harnais différents sans le dire.
- Ajouter un modèle qu'aucune source ne mesure.
