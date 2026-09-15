<!-- Version portable du skill Claude Code `audit-referentiel`.
     Applicable par n'importe quel agent ou par un humain. -->

# Protocole de mise à jour du référentiel

## Démarrer : toujours par le plan de travail

```bash
python3 pipeline/worklist.py
```

Ce plan est le point d'entrée. Il liste ce qui est à vérifier **maintenant**,
trié par impact, avec l'URL à ouvrir et les pièges d'accès connus pour chaque
fournisseur. Ne pas improviser un ordre : le suivre.

Si l'utilisateur veut une liste cochable à garder sous les yeux :
`python3 pipeline/worklist.py --markdown`

Annoncer le plan avant d'agir, puis traiter dans l'ordre **BLOQUANT →
IMPORTANT → À FAIRE**. La VEILLE se traite en fin d'édition.

## Les deux règles qui ne se négocient pas

1. **Aucun chiffre sans source vérifiable, date de relevé et niveau de
   provenance.** En cas de doute : laisser vide et marqué `unverified`. Un trou
   déclaré est exploitable ; un chiffre plausible mais non sourcé contamine tout
   le document. Cette règle a déjà servi : en septembre 2026, les tarifs Mistral
   n'ont pas été saisis faute de page officielle accessible — c'était la bonne
   décision.
2. **Un score de benchmark appartient au triplet (modèle × harnais × protocole)**,
   jamais au modèle seul. Ne jamais publier un classement sans dire sous quel
   harnais il a été obtenu.

Le catalogue `catalog/` est la seule source de vérité. Le Guide et
`site/index.html` sont **générés** : les corriger à la main est inutile, le build
suivant les écrase. Dans `catalog/`, `benchmarks.yaml` et `scores.yaml` sont eux
aussi générés (par `epoch_ingest.py`) — ne pas les éditer.

---

## Vérifier un tarif API

**Le point crucial, et le plus souvent oublié : il ne s'agit pas seulement de
remplir les cases vides, mais de re-contrôler ce qui est déjà là.** Un tarif
saisi il y a quatre mois a pu baisser, changer de structure, ou porter sur un
modèle déprécié. `worklist.py` distingue explicitement les deux cas.

Pour chaque lab du plan :

1. Ouvrir la `pricing_url`. **Lire le piège d'accès** affiché par le worklist
   (redirections, 403, 404 déjà rencontrés) avant de perdre du temps.
2. Relever en **USD par 1M de tokens** : entrée standard, entrée en cache,
   sortie. Relever aussi la fenêtre de contexte et l'identifiant d'API exact.
3. **Comparer à ce que le catalogue contient déjà.** Tout écart est une
   information à consigner, pas une simple correction silencieuse :
   - un prix qui bouge → le noter pour le changelog ;
   - un modèle qui disparaît de la page → passer son `status` à `deprecated`,
     ne pas le supprimer (une disparition est une information) ;
   - un palier qui n'existe plus → le consigner dans `verification.finding`.
4. Saisir dans **`catalog/pricing_verified.yaml`** — le seul endroit où l'on
   écrit un tarif.
5. Si l'URL réellement consultée diffère de celle de `labs.yaml` (redirection),
   mettre à jour `SOURCES` dans `pipeline/apply_pricing.py` **et** `GOTCHAS`
   dans `pipeline/worklist.py`, pour que l'édition suivante n'y repasse pas.

```bash
python3 pipeline/apply_pricing.py
```

Pièges à traiter explicitement plutôt qu'à écraser :

- **tarification dynamique** (DeepSeek : heures pleines/creuses) → champ `offpeak` ;
- **paliers de contexte** (Google : ≤200k vs >200k) → champ `tier_note` ;
- **promotions datées** (Google jusqu'au 31/12/2026) → `promo_until` + `promo_note` ;
- **variations régionales** (Alibaba) → préciser la région dans `note` ;
- **tarifs batch** : à distinguer du temps réel, jamais à confondre.

Ne jamais saisir d'euros : la conversion est calculée au build depuis
`catalog/_meta.yaml`. Si le taux de change est signalé non vérifié, le traiter —
c'est un BLOQUANT parce que toutes les valeurs en euros en héritent.

---

## Vérifier un forfait d'abonnement

Même discipline, dans `catalog/plans.yaml`. Relever le prix affiché **HT en USD**
et laisser le build calculer le HT en euros (pro, autoliquidation) et le TTC
(particulier, TVA 20 %).

Points à relever systématiquement :

- les paliers **et** ce qu'ils incluent réellement (quotas, crédits en dollars) ;
- le prix avec engagement annuel s'il diffère ;
- la facturation par siège et le minimum de sièges ;
- si l'agent CLI du fournisseur est inclus ou non — c'est souvent le
  discriminant réel entre deux forfaits.

Rattacher le forfait au harnais correspondant via le champ `plans` de
`catalog/tools.yaml`.

---

## Vérifier un harnais

Pour chaque outil listé par le worklist, contrôler **dans cet ordre** :

1. **Le projet vit-il encore ?** Actif, en maintenance, archivé, racheté,
   renommé. Pour un projet open-source : date du dernier commit.
2. **Les URL répondent-elles ?** Site, docs, dépôt, page tarifaire.
3. **Le modèle économique a-t-il changé de nature ?** Passage d'un forfait à des
   crédits, suppression d'un palier, arrêt d'une offre grand public.
4. **Les capacités ont-elles bougé ?** BYOK, modèles locaux, MCP, agent autonome.

Puis remplir le bloc `verification` de la fiche :

```yaml
verification:
  status: official_pricing_page     # ou official_docs, community…
  verified_on: 2026-09-15
  finding: "Les paliers Pro+ et Ultra ne figurent plus sur la page."
```

`finding` est important : c'est ce qui remonte dans la page publiée et signale au
lecteur ce qui a changé. Un outil disparu passe en `status: retired` avec sa
date — on ne le supprime pas.

---

## Rafraîchir les benchmarks

```bash
python3 pipeline/epoch_ingest.py --force-download
python3 pipeline/seed_catalog.py
```

Epoch AI republie régulièrement ; `--force-download` ignore le cache local.
`seed_catalog.py` ajoute les modèles nouvellement mesurés — sans jamais inventer :
un modèle n'entre que s'il apparaît dans une source de benchmark.

Pour ajouter ou retirer un benchmark du suivi, éditer `CURATION` dans
`pipeline/epoch_ingest.py`, jamais `catalog/benchmarks.yaml`. Tout rejet se
documente avec son motif dans `REJECTED`.

Traiter les alertes de saturation : au-delà de 92 % du plafond, un benchmark a
épuisé son pouvoir discriminant et doit être remplacé.

Si un benchmark remonte 0 mesure, c'est un mapping de colonne cassé en amont —
vérifier `COLUMN_MAP` : chaque benchmark nomme sa colonne de score différemment,
et certains publient en pourcentage quand d'autres publient en fraction.

---

## Clôturer une édition

Dans cet ordre, sans en sauter :

```bash
python3 pipeline/validate.py        # doit sortir en 0
python3 pipeline/changelog.py       # ce qui a changé depuis l'instantané
python3 pipeline/build_site.py      # régénère la page
python3 pipeline/changelog.py --snapshot   # fige la nouvelle référence
```

Puis mettre à jour `audit.edition` et `audit.next_review_due` dans
`catalog/_meta.yaml`, et commiter avec le changelog en corps de message.

**`validate.py` est la porte de sortie : tant qu'il échoue, on ne publie pas.**
Ses alertes ne sont pas du bruit, elles disent ce que le document n'a pas le
droit d'affirmer. En particulier, quand il signale que les deux premiers d'un
classement ne sont pas séparés statistiquement, **ne pas titrer sur un vainqueur**.

Ne figer l'instantané qu'**après** publication : c'est lui qui sert de base de
comparaison à l'édition suivante.

---

## Rendre compte à l'utilisateur

À la fin d'une passe, dire :

- ce qui a été **re-vérifié** et ce qui a **changé** (pas seulement ce qui a été
  ajouté) ;
- ce qui reste **non vérifié**, et pourquoi — un trou assumé est un résultat ;
- ce que le validateur **interdit d'affirmer**.

Ne pas présenter comme « à jour » un document dont une partie n'a pas été
contrôlée. Le tableau d'état du README doit refléter la réalité après chaque
passe.

---

## Erreurs déjà commises, à ne pas refaire

- **Conclure qu'une donnée est fausse parce qu'elle est absente d'une source.**
  Les jeux de benchmark ont du retard sur les annonces commerciales : un modèle
  peut être vendu sans être encore mesuré. Vérifier sur la page du fournisseur
  avant de qualifier quoi que ce soit d'erroné.
- Éditer un fichier généré (Guide, `site/`, `benchmarks.yaml`, `scores.yaml`).
- Saisir un prix en euros dans le catalogue.
- Comparer des scores obtenus sous des harnais différents sans le dire.
- Écraser un tarif sans noter qu'il a changé : le changelog perd l'information.
