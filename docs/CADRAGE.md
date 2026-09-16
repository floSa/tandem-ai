# Cadrage — Tandem

Le POURQUOI. Le COMMENT est dans [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 1. Pitch

**Tandem** — un référentiel ouvert de l'offre de développement assisté par IA, modèles
de fondation et harnais d'exécution, construit pour résister à la vérification. Le nom
porte la thèse : les deux n'avancent qu'attelés, et c'est le couple qui se mesure.

1. **Mesurer** la performance des modèles sur des benchmarks réputés, en conservant le
   harnais, le protocole, l'incertitude et le coût réel de chaque mesure.
2. **Tarifer** l'accès à ces modèles : prix API au million de tokens et forfaits
   d'abonnement, relevés sur les pages officielles et convertis en euros HT et TTC.
3. **Rejouer** l'audit à intervalle régulier sans réinventer la méthode, avec un plan
   de travail qui dit ce qui est à re-vérifier et un validateur qui refuse de publier
   ce qui n'est pas défendable.

---

## 2. Objectifs et périmètre

**Dans le périmètre**

- Modèles de fondation des principaux laboratoires, tarifs API et forfaits SaaS.
- Harnais de développement : IDE dérivés, extensions, applications desktop, agents CLI,
  passerelles.
- Benchmarks de code, agentiques et de raisonnement, avec leur coût mesuré.
- Facturation vue depuis la France : autoliquidation professionnelle contre TVA
  particulier.

**Hors périmètre, volontairement**

- **Tout classement de « meilleur modèle ».** La question est mal posée : un score
  appartient au triplet *(modèle × harnais × effort)*.
- **Tout score composite maison.** Agréger des benchmarks aux protocoles différents
  produit un nombre sans signification.
- Latence perçue, ergonomie du harnais, qualité durable du code produit — trois facteurs
  qui pèsent souvent plus que quelques points de benchmark, et qu'aucune mesure
  disponible ne capture.
- Coût d'une journée de développement réelle. Le coût par tâche de benchmark n'en est
  qu'un proxy comparatif.

---

## 3. Contraintes

| Contrainte | Détail |
|---|---|
| Dépendances | Python 3.12 et PyYAML uniquement. Tout le reste en bibliothèque standard |
| Fonctionnement hors ligne | Aucune clé d'API requise pour le fonctionnement nominal |
| Publication | Dépôt public. Code sous MIT ([LICENSE](../LICENSE)), contenu sous CC BY 4.0 ([LICENSE-CONTENT](../LICENSE-CONTENT)) par compatibilité avec les sources |
| Portabilité | La méthodologie doit être applicable par un agent autre que Claude Code, ou par un humain |
| Sorties | Le Guide et la page doivent être lisibles sans outil : Markdown et HTML autonome |

---

## 4. Hypothèses

- **Une mesure sans son protocole n'est pas comparable.** Le harnais, le budget de
  raisonnement et le nombre de tentatives déplacent les scores autant que le modèle.
  Empiriquement vérifié : le catalogue recense **17 harnais distincts** ; sur Terminal-Bench 4.0,
  le même modèle n'est pas mesuré dans le même harnais selon son éditeur.
  *Ce qui la remettrait en cause* : une normalisation du marché sur un harnais de
  référence unique.

- **Un chiffre sans source est une rumeur.** En cas de doute, le champ reste vide et
  marqué `unverified` plutôt que rempli d'une valeur plausible. Un trou déclaré est
  exploitable ; un chiffre inventé contamine tout le document.
  *Appliqué en septembre 2026* : les tarifs Mistral n'ont pas été saisis, la page
  tarifaire officielle n'ayant pas été localisée.

- **Les jeux de benchmark ont du retard sur les annonces commerciales.** Un modèle peut
  être vendu plusieurs mois avant d'être mesuré par un tiers indépendant. Ce décalage
  s'affiche, il ne se comble pas.
  *Cette hypothèse vient d'une erreur réelle* : l'absence d'un modèle des données Epoch
  avait été prise pour la preuve qu'il n'existait pas, alors qu'il figurait bien au
  catalogue officiel du fournisseur.

- **Le prix au token ne mesure pas le coût.** À effort différent, le tarif au token est
  identique et seule la consommation change. Comparer deux niveaux d'effort exige un
  coût réellement mesuré.

- **Un outil qui disparaît est une information.** Un projet archivé passe en `retired`
  avec sa date, il n'est pas retiré du catalogue.

---

## 5. Stack technique

| Brique | Choix | Licence |
|---|---|---|
| Langage | Python 3.12 | PSF |
| Sérialisation | PyYAML 6.0.1 | MIT |
| Tests | `unittest` (bibliothèque standard) | PSF |
| Intégration continue | GitHub Actions | — |
| Visualisation | SVG et JavaScript écrits à la main, sans dépendance | — |
| Données de benchmark | Epoch AI — *Capabilities & Benchmarking* | CC BY 4.0 |
| Recoupement optionnel | Artificial Analysis Data API v2 | Attribution requise |

---

## 6. Décisions

**Décisions figées**

- **Catalogue YAML** plutôt que base de données, parce qu'un diff Git sur du YAML se
  relit et que le dépôt est fait pour être publié.
- **Sorties générées** plutôt que rédigées, parce que la duplication entre les fiches et
  le Guide produisait une divergence à chaque édition.
- **Tarifs saisis en USD uniquement**, la conversion en euros étant recalculée au build
  depuis un taux unique — sinon un changement de taux oblige à reprendre tout le document.
- **Le recoupement signale, il n'écrit pas**, parce qu'arbitrer entre deux sources
  contradictoires demande un jugement fondé sur la hiérarchie de provenance.
- **Deux portes avant publication** : les tests du pipeline, puis le validateur de la
  donnée. Tant que l'une échoue, on ne publie pas.
- **Une absence de donnée doit dire pourquoi elle est absente.** Un modèle sans tarif est
  soit un relevé à faire, soit un modèle qui n'aura jamais de tarif éditeur — et rien ne
  distingue les deux si le catalogue se contente d'une case vide. La distinction est donc
  portée par la donnée (`no_public_price` et son motif), pas laissée à l'interprétation.
  Sans elle, le reste-à-faire affiché est faux, et il le reste indéfiniment.
- **Un fournisseur se balaye entièrement, pas par mots-clés.** Chercher « CLI » ou
  « coding agent » laisse passer les harnais dont le nom ne contient ni l'un ni l'autre.
  Le balayage est donc fournisseur par fournisseur, et sa date est consignée — y compris
  quand il ne trouve rien.

**À trancher**

- **Hébergement de la page.** GitHub Pages depuis `site/` serait le plus simple, mais
  impose de versionner un fichier de 457 Ko à chaque édition. Recommandation par défaut :
  GitHub Pages, la lisibilité du diff important peu sur un fichier généré.
- **Périmètre des benchmarks non liés au code.** GPQA, HLE et ARC-AGI-2 sont suivis mais
  ne mesurent pas une capacité de développement ; les trois approchent la saturation.
  Recommandation par défaut : les conserver une édition, puis les écarter s'ils
  n'ajoutent rien.
- **Conformité.** Les champs existent mais ne sont relevés que pour 6 harnais sur 30.
  Les compléter exige de lire des DPA et des pages de confiance, pas des pages
  tarifaires : c'est le seul chantier du référentiel qui ne se ramène pas à un relevé
  chiffré, et le seul qui reste largement ouvert.

---

## 7. Roadmap

0. **Socle** — catalogue YAML, ingestion des benchmarks, validateur. *Fait.*
1. **Tarification** — relevé sur sources primaires, conversion euro. *Fait : 109 modèles
   tarifés, 51 classés sans tarif éditeur avec leur motif, 0 en attente de relevé.*
2. **Coût mesuré** — exploitation des coûts de run et de l'effort de raisonnement. *Fait.*
3. **Harnais** — balayage fournisseur par fournisseur, statuts et forfaits. *Fait : 11
   fournisseurs balayés, 30 fiches contrôlées. Seule la grille Windsurf / Devin manque.*
4. **Recoupement** — seconde source pour confronter les tarifs. *Implémenté, clé non configurée.*
5. **Conformité** — rétention, résidence, engagements contractuels. *6 harnais sur 30.*
6. **Publication** — hébergement de la page et première édition publique. *Fait.*

---

## 8. Stratégie de tests

Deux niveaux, complémentaires et tous deux bloquants en CI.

**Tests du pipeline** — 51 tests dans [tests/test_pipeline.py](../tests/test_pipeline.py),
qui vérifient le code produisant la donnée : normalisation des scores, survie de l'effort
et du coût à l'ingestion, intégrité référentielle, interdiction de saisie en euros,
cohérence tarifaire, démarrage effectif de chaque script, non-divergence des sorties
générées. Chaque test correspond à un bug réellement survenu ou à une règle du protocole.

**Validation de la donnée** — [pipeline/validate.py](../pipeline/validate.py), qui
vérifie le contenu du catalogue selon les six familles décrites dans
[ARCHITECTURE.md](ARCHITECTURE.md#5-les-six-familles-de-contrôle).

Ce que les tests ne prouvent pas : **l'exactitude d'un tarif relevé à la main**. Aucun
test ne peut dire qu'une valeur saisie correspond à la page officielle — seule la date
de vérification et l'URL consignée permettent de le recontrôler.

---

## 9. Références

- [Epoch AI — Capabilities & Benchmarking](https://epoch.ai/benchmarks) — source des
  mesures, sous CC BY 4.0.
- [Artificial Analysis Data API](https://artificialanalysis.ai/data-api/docs) — source
  de recoupement.
- Leaderboards officiels consultés en cas de doute : [SWE-bench](https://swebench.com) (figé, retiré du suivi),
  [Terminal-Bench](https://www.tbench.ai/leaderboard),
  [Aider Polyglot](https://aider.chat/docs/leaderboards/),
  [ARC Prize](https://arcprize.org/leaderboard).
- Méthodologie interne : [protocol/04_sources_et_collecte.md](../protocol/04_sources_et_collecte.md),
  [protocol/05_methodologie_benchmarks.md](../protocol/05_methodologie_benchmarks.md),
  [protocol/06_protocole_operatoire.md](../protocol/06_protocole_operatoire.md).
