# Méthodologie d'Évaluation par Benchmarks

Ce document fixe **comment on lit un score** dans ce référentiel. Il est
indépendant de tout agent et doit pouvoir être appliqué par un tiers.

---

## 1. Le principe qui commande tout le reste

> **Un score n'est pas un attribut d'un modèle. C'est le résultat d'un triplet :
> (modèle × harnais × protocole), mesuré à une date donnée par un acteur donné.**

Ce n'est pas une précaution théorique, c'est mesurable dans nos propres données.
Un même modèle change de score de plusieurs points selon l'agent qui l'exécute ;
le catalogue contient **17 harnais distincts**, dont 4 sur Terminal-Bench 4.0. Le graphique « Effet du harnais » de `site/index.html` existe
précisément pour rendre cet écart visible.

Conséquence pratique : **« quel est le meilleur modèle ? » est une question mal
posée.** La question exploitable est « quel couple modèle + harnais, à quel coût,
pour quel type de tâche ? » — et c'est l'objet de ce référentiel.

---

## 2. Les quatre questions avant de citer un score

Un score ne se publie qu'après avoir répondu aux quatre :

1. **Qui a mesuré ?** Un run indépendant, un leaderboard officiel, ou le lab
   lui-même ? (voir la hiérarchie dans `04_sources_et_collecte.md`)
2. **Avec quel harnais ?** Sans cette information, le score n'est comparable
   à rien d'autre.
3. **Sous quel protocole ?** Effort de raisonnement, budget d'étapes, pass@k,
   outils autorisés. Ces paramètres déplacent les scores autant que le modèle.
4. **Quand ?** Un score de mars ne décrit pas le modèle de septembre.

Si une des quatre réponses manque, le score se publie **avec la mention du
manque**, jamais comme un chiffre nu.

---

## 3. L'incertitude n'est pas décorative

Les benchmarks sérieux publient une erreur-type (`stderr`). Deux modèles dont les
intervalles de confiance à 95 % se chevauchent sont **à égalité statistique** :
les classer l'un devant l'autre est une erreur de lecture, pas une nuance.

`pipeline/validate.py` applique ce test automatiquement et signale les cas où les
deux premiers d'un classement ne sont pas séparables. Au moment de l'écriture,
c'est le cas sur Terminal-Bench 4.0, DeepSWE et GPQA diamond entre les deux modèles de tête.

**Règle de rédaction : ne jamais titrer sur un vainqueur que le validateur
signale comme non séparé.**

Dans `site/index.html`, la bande bleue derrière le premier du classement
matérialise cette zone d'égalité.

---

## 4. Critères de sélection d'un benchmark

Un benchmark entre au registre (`catalog/benchmarks.yaml`) s'il satisfait :

| Critère | Test |
| :-- | :-- |
| **Pouvoir discriminant** | les meilleurs modèles n'y sont pas au plafond |
| **Résistance à la contamination** | problèmes postérieurs aux dates d'entraînement, ou jeu privé |
| **Pertinence** | mesure une capacité qui a un sens pour du développement |
| **Traçabilité** | protocole publié, résultats vérifiables |
| **Vitalité** | maintenu, avec des soumissions récentes |

Un benchmark est **écarté** dès qu'il est saturé, remplacé, ou qu'il mesure de la
mémorisation. Les rejets sont consignés **avec leur motif** dans la section
`rejected` de `catalog/benchmarks.yaml` : documenter un rejet évite de reposer la
question à chaque édition.

`validate.py` alerte automatiquement quand un benchmark suivi dépasse 92 % de son
plafond — signal qu'il faut lui chercher un remplaçant.

---

## 5. Ce que chaque famille mesure vraiment

| Famille | Ce que ça mesure | Ce que ça ne mesure pas |
| :-- | :-- | :-- |
| **Ingénierie logicielle** (CursorBench, DeepSWE, FrontierSWE, GSO) | réparer du code existant dans un vrai dépôt | concevoir une architecture |
| **Agentique CLI** (Terminal-Bench 4.0) | enchaîner des commandes et vérifier son travail | qualité du code produit |
| **Génération** (LiveCodeBench, FrontierCode, MirrorCode) | algorithmique sur problèmes récents | travail en base de code réelle |
| **Computer use** (OSWorld) | piloter une interface graphique | fiabilité en production |
| **Post-entraînement** (PostTrainBench) | conduire seul une boucle d'entraînement de modèle | qualité du code produit |
| **Valeur économique** (GDP.pdf, Remote Labor Index) | tâches professionnelles réelles jugées par des experts | coût total d'usage |
| **Raisonnement** (GPQA, HLE, ARC-AGI-2) | capacité générale hors code | aptitude au développement |

**Un score ne s'agrège qu'avec des scores de même unité.** Le champ `unit` du
catalogue protège de cette erreur (METR Time Horizons, retiré en septembre 2026,
s'exprimait en minutes).

---

## 6. Interdits de composition

- **Pas de score composite maison.** Additionner des benchmarks aux protocoles
  différents produit un chiffre qui ne veut rien dire. Si un composite est
  nécessaire, citer un index existant et versionné (ECI d'Epoch, Intelligence
  Index d'Artificial Analysis) **en nommant sa version**.
- **Pas d'interpolation.** Un modèle non mesuré sur un benchmark reste vide. La
  vue « Couverture » affiche délibérément les trous en pointillés.
- **Pas de comparaison inter-benchmarks.** 70 % sur SWE-bench et 70 % sur GPQA ne
  décrivent pas la même difficulté.
- **Pas de mélange de versions d'index.** Un Intelligence Index v4.2 et un v4.3
  ne se comparent pas.

---

## 7. Ce qu'aucun benchmark ne dit

À rappeler dans toute publication destinée à une décision d'achat :

- la **latence** et le débit en conditions réelles ;
- le **coût réel** d'une tâche complète (un modèle plus cher au token peut revenir
  moins cher s'il réussit en un essai) ;
- la **qualité du code produit** au-delà du test qui passe (lisibilité, dette) ;
- l'**ergonomie du harnais**, qui pèse souvent plus que 3 points de benchmark ;
- la **conformité** : rétention des données, résidence, engagements contractuels.

Un référentiel honnête dit aussi ce qu'il ne mesure pas.

---

## 8. Coût mesuré contre prix catalogue

Deux grandeurs portent le mot « coût » et **ne se substituent jamais l'une à
l'autre** :

| | Ce que c'est | Où c'est |
| :-- | :-- | :-- |
| **Prix catalogue** | $ par million de tokens, affiché par le fournisseur | `catalog/models.yaml` |
| **Coût mesuré** | $ réellement dépensés pour accomplir une tâche du benchmark | `catalog/scores.yaml`, champ `cost_usd` |

Le prix catalogue ne permet pas de comparer deux niveaux d'effort d'un même
modèle : le tarif au token est identique, seule la consommation change. Seul le
coût mesuré rend la comparaison possible — c'est pourquoi la vue
« Coût × performance » n'accepte que les benchmarks qui le publient.

Benchmarks fournissant un coût mesuré : **DeepSWE** (le plus complet — jusqu'à 5
niveaux d'effort par modèle, sous un harnais unique, donc comparaison contrôlée),
**CursorBench**, **FrontierSWE**, **Terminal-Bench 4.0** (coût du run rapporté à un
essai), **ARC-AGI-2**, **OSWorld 2.0**.

### L'effort de raisonnement est une variable de décision

Les suffixes `_low`, `_medium`, `_high`, `_xhigh`, `_max` ne sont pas des
variantes de modèle : c'est le **budget de raisonnement** accordé au même modèle.
Son effet dépasse souvent l'écart entre deux modèles concurrents, et il se paie.

Ce que la donnée de septembre 2026 établit :

- l'effort peut transformer un modèle de bout en bout — un même modèle passe de
  1,5 % à 67,2 % de `low` à `max`, pour un coût multiplié par plus de 40 ;
- **le rendement s'effondre au sommet** : le palier `max` coûte fréquemment le
  double du `xhigh` pour un gain nul, et parfois négatif (un modèle perd 0,2
  point en passant de `xhigh` à `max`) ;
- un modèle plus modeste à effort élevé bat souvent un modèle plus prestigieux à
  effort faible, à coût égal.

**Règle de publication : ne jamais citer un score sans son niveau d'effort.**
« Ce modèle fait 73 % » est une affirmation incomplète tant que le budget de
raisonnement et le coût par tâche ne sont pas donnés.

### Lecture de la vue

L'axe des coûts est **inversé** : moins cher vers la droite. Le coin
**haut-droite** est donc la zone strictement préférable — meilleur et moins cher.
Le front de Pareto relie les points qu'aucun autre ne domine sur les deux axes à
la fois ; tout ce qui est en dessous est dominé, c'est-à-dire qu'il existe une
option à la fois meilleure et moins chère.
