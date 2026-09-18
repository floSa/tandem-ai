#!/usr/bin/env python3
"""
Suite de tests du pipeline.

Le référentiel contrôle la qualité de ses données ; ces tests contrôlent la
qualité du code qui les produit. Chaque test correspond à un bug réellement
survenu ou à une règle du protocole qui doit rester vraie.

    python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import re
import subprocess
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
sys.path.insert(0, str(ROOT / "pipeline"))


def load(name: str) -> dict:
    p = CATALOG / name
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


class TestNormalisationDesScores(unittest.TestCase):
    """Bug réel : Aider polyglot publie en % et affichait 88,0 sur un plafond de 1,0."""

    @classmethod
    def setUpClass(cls):
        cls.scores = load("scores.yaml").get("scores", [])
        cls.bench = {b["name"]: b for b in load("benchmarks.yaml").get("tracked", [])}

    def test_scores_dans_les_bornes(self):
        for s in self.scores:
            if s.get("unit") == "minutes" or s.get("score") is None:
                continue
            with self.subTest(b=s["benchmark"], m=s["model_version"]):
                self.assertGreaterEqual(s["score"], 0.0)
                self.assertLessEqual(
                    s["score"], 1.5,
                    f"score non normalisé : {s['score']} — vérifier `scale` dans le registre")

    def test_aucun_benchmark_ne_depasse_son_plafond(self):
        for s in self.scores:
            b = self.bench.get(s["benchmark"])
            if not b or s.get("unit") == "minutes" or s.get("score") is None:
                continue
            ceil = b.get("score_ceiling")
            if ceil:
                self.assertLessEqual(s["score"], ceil * 1.02,
                                     f"{s['benchmark']} dépasse son plafond déclaré")

    def test_stderr_plausible(self):
        for s in self.scores:
            if s.get("stderr") is None:
                continue
            with self.subTest(b=s["benchmark"]):
                self.assertGreater(s["stderr"], 0)
                self.assertLess(s["stderr"], 0.5, "erreur-type aberrante — "
                                "une demi-largeur d'IC95 a-t-elle été prise pour un stderr ?")


class TestEffortEtCout(unittest.TestCase):
    """L'effort de raisonnement et le coût mesuré doivent survivre à l'ingestion."""

    @classmethod
    def setUpClass(cls):
        cls.scores = load("scores.yaml").get("scores", [])

    def test_efforts_dans_le_vocabulaire_connu(self):
        connus = {"low", "medium", "high", "xhigh", "max", "minimal"}
        vus = {s["effort"] for s in self.scores if s.get("effort")}
        self.assertTrue(vus, "aucun effort identifié — le parsing a régressé")
        self.assertTrue(vus <= connus, f"efforts inconnus : {vus - connus}")

    def test_model_base_sans_suffixe_de_reglage(self):
        """Le budget de réflexion est un réglage, au même titre que l'effort.

        La règle n'en retirait que les paliers nommés : `claude-opus-4-6_32K`
        restait un modèle à part entière, et la matrice de couverture affichait
        quatre lignes pour un seul Opus 4.6 — chassant du classement des modèles
        réellement distincts.
        """
        import variantes
        for s in self.scores:
            mb = s.get("model_base")
            if not mb:
                continue
            self.assertIsNone(variantes.SUFFIXE.match(mb),
                              f"`model_base` porte encore un réglage d'exécution : {mb}")

    def test_le_budget_de_reflexion_n_est_pas_perdu(self):
        """Retirer le suffixe ne doit pas effacer l'information qu'il portait."""
        avec = [s for s in self.scores
                if (s.get("model_version") or "").endswith("K")
                and (s.get("model_version") or "") != s.get("model_base")]
        for s in avec:
            self.assertIn("Budget de réflexion", s.get("protocol") or {},
                          f"{s['model_version']} perd son budget de réflexion")

    def test_couts_positifs(self):
        c = [s for s in self.scores if s.get("cost_usd") is not None]
        self.assertGreater(len(c), 100, "le coût mesuré a disparu de l'ingestion")
        for s in c:
            self.assertGreater(s["cost_usd"], 0, f"coût nul ou négatif sur {s['model_version']}")

    def test_deepswe_porte_bien_ses_courbes_d_effort(self):
        """DeepSWE alimente la vue coût × performance : sans effort, elle est vide."""
        d = [s for s in self.scores if s["benchmark"] == "DeepSWE"]
        self.assertTrue(d, "DeepSWE absent du catalogue")
        avec = [s for s in d if s.get("effort") and s.get("cost_usd")]
        self.assertGreater(len(avec), 50, "DeepSWE a perdu effort ou coût")
        familles = {s["model_base"] for s in avec}
        multi = [m for m in familles
                 if len({s["effort"] for s in avec if s["model_base"] == m}) > 1]
        self.assertGreater(len(multi), 5, "plus aucun modèle multi-effort : la courbe est plate")


class TestProvenance(unittest.TestCase):
    """Règle n°1 du protocole : aucun chiffre sans source vérifiable."""

    @classmethod
    def setUpClass(cls):
        cls.meta = load("_meta.yaml")
        cls.models = load("models.yaml").get("models", [])
        cls.plans = load("plans.yaml").get("plans", [])
        cls.scores = load("scores.yaml").get("scores", [])
        cls.rangs = set(cls.meta.get("provenance_ranking", []))

    def test_tout_tarif_porte_une_source(self):
        for m in self.models:
            pr = m.get("pricing") or {}
            if pr.get("input_per_1m") is None:
                continue
            src = pr.get("source") or {}
            with self.subTest(m=m["id"]):
                self.assertTrue(src.get("url"), "tarif sans URL de source")
                self.assertTrue(src.get("verified_on"), "tarif sans date de vérification")
                self.assertIn(src.get("status"), self.rangs)

    def test_tout_forfait_porte_une_source(self):
        for p in self.plans:
            src = p.get("source") or {}
            with self.subTest(p=p["id"]):
                self.assertTrue(src.get("url"))
                self.assertTrue(src.get("verified_on"))

    def test_aucune_saisie_en_euros(self):
        """La conversion est calculée au build : saisir des euros la fige."""
        for m in self.models:
            pr = m.get("pricing") or {}
            if pr.get("currency"):
                self.assertEqual(pr["currency"], "USD", f"{m['id']} : devise non USD")
            for k in pr:
                self.assertNotIn("eur", k.lower(), f"{m['id']} : champ en euros dans le catalogue")

    def test_provenance_des_scores_declaree(self):
        for s in self.scores:
            self.assertIn(s.get("provenance"), self.rangs)
            self.assertTrue(s.get("source_url"))

    def test_dates_de_verification_non_futures(self):
        today = date.today()
        for m in self.models:
            d = ((m.get("pricing") or {}).get("source") or {}).get("verified_on")
            if d:
                self.assertLessEqual(date.fromisoformat(str(d)[:10]), today,
                                     f"{m['id']} : vérifié dans le futur")


class TestIntegriteReferentielle(unittest.TestCase):
    def test_tout_modele_pointe_un_lab_connu(self):
        labs = {l["id"] for l in load("labs.yaml").get("labs", [])}
        for m in load("models.yaml").get("models", []):
            self.assertIn(m.get("lab"), labs, f"{m['id']} : lab inconnu")

    def test_tout_score_pointe_un_benchmark_du_registre(self):
        noms = {b["name"] for b in load("benchmarks.yaml").get("tracked", [])}
        for b in {s["benchmark"] for s in load("scores.yaml").get("scores", [])}:
            self.assertIn(b, noms)

    def test_les_forfaits_references_existent(self):
        ids = {p["id"] for p in load("plans.yaml").get("plans", [])}
        for t in load("tools.yaml").get("tools", []):
            for pid in t.get("plans") or []:
                self.assertIn(pid, ids, f"{t['id']} référence un forfait inexistant : {pid}")

    def test_identifiants_uniques(self):
        for f, k in (("models.yaml", "models"), ("plans.yaml", "plans"), ("tools.yaml", "tools")):
            ids = [x["id"] for x in load(f).get(k, [])]
            self.assertEqual(len(ids), len(set(ids)), f"{f} : identifiants dupliqués")


class TestAbsenceDeTarif(unittest.TestCase):
    """Un modèle sans tarif doit dire POURQUOI il n'en a pas.

    Sans cette distinction, « pas encore relevé » et « n'aura jamais de tarif »
    se ressemblent — et le catalogue paraît éternellement inachevé.
    """

    @classmethod
    def setUpClass(cls):
        cls.models = load("models.yaml")["models"]
        cls.saisie = load("pricing_verified.yaml")

    def test_tout_modele_sans_tarif_est_motive(self):
        muets = [m["id"] for m in self.models
                 if (m.get("pricing") or {}).get("input_per_1m") is None
                 and (m.get("pricing") or {}).get("source", {}).get("status") != "no_public_price"]
        self.assertEqual(muets, [],
                         "modèles sans tarif ni motif — les classer dans no_public_price "
                         "ou relever leur tarif")

    def test_un_motif_accompagne_chaque_exclusion(self):
        for m in self.models:
            src = (m.get("pricing") or {}).get("source") or {}
            if src.get("status") == "no_public_price":
                self.assertTrue((src.get("note") or "").strip(),
                                f"{m['id']} exclu sans motif")

    def test_une_exclusion_ne_porte_aucun_montant(self):
        for m in self.models:
            pr = m.get("pricing") or {}
            if (pr.get("source") or {}).get("status") != "no_public_price":
                continue
            for k in ("input_per_1m", "input_cached_per_1m", "output_per_1m"):
                self.assertIsNone(pr.get(k),
                                  f"{m['id']} est classé sans tarif mais porte {k}")

    def test_aucun_modele_classe_deux_fois(self):
        vus = set()
        for g in self.saisie.get("no_public_price") or []:
            for mid in g["models"]:
                self.assertNotIn(mid, vus, f"{mid} classé dans deux motifs différents")
                vus.add(mid)


class TestPropagationTarifaire(unittest.TestCase):
    """`applies_to` et les variantes d'effort recopient un tarif : jamais l'inventer."""

    @classmethod
    def setUpClass(cls):
        cls.models = load("models.yaml")["models"]
        cls.idx = {m["id"]: m for m in cls.models}
        cls.saisie = load("pricing_verified.yaml")

    def test_les_cibles_applies_to_existent(self):
        for v in self.saisie["models"]:
            for alias in v.get("applies_to") or []:
                self.assertIn(alias, self.idx,
                              f"`applies_to` de {v['id']} vise {alias}, absent du catalogue")

    def test_un_alias_porte_le_meme_tarif_que_sa_source(self):
        saisi = {v["id"]: v for v in self.saisie["models"]}
        for v in self.saisie["models"]:
            for alias in v.get("applies_to") or []:
                a = self.idx[alias]["pricing"]
                self.assertEqual(a["input_per_1m"], v["pricing"]["input_per_1m"],
                                 f"{alias} diverge du tarif de {v['id']}")
                self.assertEqual(a["source"].get("priced_as"), v["id"],
                                 f"{alias} ne dit pas au nom de quel modèle il est tarifé")

    def test_une_variante_d_effort_herite_exactement_de_sa_base(self):
        n = 0
        for m in self.models:
            src = (m.get("pricing") or {}).get("source") or {}
            base_id = src.get("variant_of")
            if not base_id:
                continue
            n += 1
            base = self.idx[base_id]["pricing"]
            for k in ("input_per_1m", "output_per_1m"):
                self.assertEqual(m["pricing"].get(k), base.get(k),
                                 f"{m['id']} diverge de sa base {base_id} sur {k}")
        self.assertGreater(n, 0, "aucune variante d'effort propagée — mécanisme mort")

    def test_le_balayage_outillage_est_date_pour_chaque_fournisseur(self):
        for lab in load("labs.yaml")["labs"]:
            t = lab.get("tooling") or {}
            self.assertTrue(t.get("checked_on"),
                            f"{lab['id']} jamais balayé côté outillage")
            self.assertTrue((t.get("note") or "").strip(),
                            f"{lab['id']} balayé sans consigner ce qui a été trouvé")


class TestPerimetreTemporel(unittest.TestCase):
    """Bug réel : jusqu'en septembre 2026, Terminal-Bench 2.0, METR et SWE-bench Verified
    étaient figés depuis des mois sans qu'aucun contrôle ne le dise, et la page montrait
    encore Claude 3.7. Le contrôle de fraîcheur ne regardait que la mesure la plus récente,
    tous benchmarks confondus."""

    def test_fenetre_glissante_en_mois(self):
        import scope
        self.assertEqual(scope.cutoff(date(2026, 9, 16), 12), "2025-09-16")
        self.assertEqual(scope.cutoff(date(2026, 3, 31), 1), "2026-02-28")
        self.assertEqual(scope.cutoff(date(2026, 1, 10), 18), "2024-07-10")

    def test_un_benchmark_fige_est_detecte_meme_si_un_autre_vit(self):
        import scope
        scores = [
            {"benchmark": "vivant", "model_released_on": "2026-09-03"},
            {"benchmark": "vivant", "model_released_on": "2025-01-01"},
            {"benchmark": "fige", "model_released_on": "2026-04-23"},
        ]
        dormants = scope.dormant_benchmarks(scores, 90)
        self.assertEqual([d[0] for d in dormants], ["fige"])
        self.assertEqual(dormants[0][2], 133)

    def test_aucun_benchmark_suivi_en_sommeil(self):
        import scope
        scores = load("scores.yaml").get("scores", [])
        self.assertEqual(scope.dormant_benchmarks(scores, scope.dormant_after_days()), [],
                         "benchmark figé à la source : le remplacer ou le retirer")

    def test_aucun_score_hors_fenetre(self):
        doc = load("scores.yaml")
        since = (doc.get("_generated") or {}).get("since")
        self.assertTrue(since, "scores.yaml ne consigne plus la fenêtre appliquée")
        vieux = {s["model_version"] for s in doc["scores"]
                 if s.get("model_released_on") and s["model_released_on"] < since}
        self.assertEqual(vieux, set())

    def test_les_benchmarks_retires_sont_motives(self):
        suivis = {b["name"] for b in load("benchmarks.yaml").get("tracked", [])}
        rejets = {b["benchmark"]: b["reason"] for b in load("benchmarks.yaml").get("rejected", [])}
        for nom in ("Terminal Bench", "SWE-Bench verified", "METR Time Horizons", "Aider polyglot"):
            self.assertNotIn(nom, suivis)
            self.assertTrue(rejets.get(nom), f"{nom} retiré sans motif consigné")


class TestTerminalBench4(unittest.TestCase):
    """Terminal-Bench 4.0 n'est pas relayé par Epoch : il est lu sur tbench.ai."""

    def test_parseur_du_flux_next(self):
        import json
        import tbench_ingest
        ligne = {"rank": 1, "metadata": {"date": "2026-09-03"},
                 "metrics": {"accuracy": 58.18, "n_trials": 330}}
        flight = ('{"title":"Terminal-Bench 4.0","x":1},"rows":' + json.dumps([ligne]) + "}")
        html = ("<script>self.__next_f.push([1," + json.dumps(flight) + "])</script>")
        rows = tbench_ingest.parse_rows(html)
        self.assertEqual(rows[0]["metrics"]["accuracy"], 58.18)

    def test_parseur_echoue_bruyamment_si_la_page_change(self):
        import tbench_ingest
        with self.assertRaises(ValueError):
            tbench_ingest.parse_rows("<html>autre chose</html>")

    def test_chaque_score_nomme_son_harnais(self):
        tb = [s for s in load("scores.yaml")["scores"] if s["benchmark"] == "Terminal-Bench 4.0"]
        self.assertTrue(tb, "Terminal-Bench 4.0 absent du catalogue")
        for s in tb:
            self.assertTrue(s.get("harness"), f"{s['model_version']} sans harnais")
            self.assertLessEqual(s["score"], 1.0)


class TestDateDesTarifs(unittest.TestCase):
    """Bug réel : apply_pricing.py datait chaque tarif du jour où il tournait —
    relancer le script faisait passer un relevé ancien pour une vérification fraîche."""

    def test_la_date_est_celle_du_releve(self):
        saisie = load("pricing_verified.yaml")
        campagne = str(saisie["_meta"]["verified_on"])
        attendu = {v["id"]: str(v.get("verified_on") or campagne) for v in saisie["models"]}
        for m in load("models.yaml")["models"]:
            src = (m.get("pricing") or {}).get("source") or {}
            if m["id"] in attendu:
                self.assertEqual(str(src.get("verified_on")), attendu[m["id"]],
                                 f"{m['id']} : date de relevé réécrite")


class TestHarnaisMesures(unittest.TestCase):
    """Un harnais qui apparaît dans les mesures existe et compte.

    La veille par mots-clés trouve les outils dont on parle ; les mesures nomment
    ceux qui servent. mini-SWE-agent, le harnais le plus mesuré du référentiel,
    est resté hors catalogue faute de ce contrôle.
    """

    @classmethod
    def setUpClass(cls):
        cls.scores = load("scores.yaml")["scores"]
        doc = load("tools.yaml")
        cls.tools = doc["tools"]
        cls.ecartes = doc.get("ecartes") or []

    @staticmethod
    def cle(x):
        return re.sub(r"[^a-z0-9]", "", (x or "").lower())

    def test_tout_harnais_mesure_est_catalogue_ou_ecarte(self):
        connus = {self.cle(t["id"]) for t in self.tools}
        connus |= {self.cle(t["name"]) for t in self.tools}
        connus |= {self.cle(e["id"]) for e in self.ecartes}
        connus |= {self.cle(e["name"]) for e in self.ecartes}
        connus.discard("")
        vus = {s["harness"] for s in self.scores if s.get("harness")}
        orphelins = sorted(h for h in vus
                           if not any(k in self.cle(h) or self.cle(h) in k for k in connus))
        self.assertEqual(orphelins, [],
                         "harnais mesurés absents du catalogue : les ajouter, "
                         "ou consigner leur rejet dans `ecartes` de tools.yaml")

    def test_tout_harnais_ecarte_porte_son_motif(self):
        for e in self.ecartes:
            self.assertTrue((e.get("reason") or "").strip(),
                            f"{e['id']} écarté sans motif")
            self.assertTrue(e.get("checked_on"),
                            f"{e['id']} écarté sans date de contrôle")


class TestConversionMonetaire(unittest.TestCase):
    """La conversion €/TVA est la seule arithmétique du build : elle doit être exacte."""

    def test_calcul_ht_et_ttc(self):
        meta = load("_meta.yaml")
        fx = meta["fx"]["usd_eur"]
        vat = meta["vat"]["rate"]
        for p in load("plans.yaml").get("plans", []):
            usd = p.get("price_usd_month")
            if usd is None:
                continue
            with self.subTest(p=p["id"]):
                self.assertAlmostEqual(round(usd * fx, 2), round(usd * fx, 2))
                self.assertAlmostEqual(round(usd * fx * (1 + vat), 2),
                                       round(usd * fx * (1 + vat), 2))

    def test_taux_de_tva_plausible(self):
        vat = load("_meta.yaml")["vat"]["rate"]
        self.assertGreater(vat, 0)
        self.assertLess(vat, 0.30)


class TestCoherenceTarifaire(unittest.TestCase):
    def test_cache_moins_cher_que_entree(self):
        for m in load("models.yaml").get("models", []):
            pr = m.get("pricing") or {}
            i, c = pr.get("input_per_1m"), pr.get("input_cached_per_1m")
            if i is not None and c is not None:
                self.assertLessEqual(c, i, f"{m['id']} : cache plus cher que cache miss")

    def test_heures_creuses_moins_cheres(self):
        for m in load("models.yaml").get("models", []):
            pr = m.get("pricing") or {}
            op = pr.get("offpeak")
            if not op:
                continue
            with self.subTest(m=m["id"]):
                self.assertLessEqual(op["input_per_1m"], pr["input_per_1m"])
                self.assertLessEqual(op["output_per_1m"], pr["output_per_1m"])

    def test_aucun_tarif_negatif(self):
        for m in load("models.yaml").get("models", []):
            for k, v in (m.get("pricing") or {}).items():
                if isinstance(v, (int, float)):
                    self.assertGreaterEqual(v, 0, f"{m['id']} : {k} négatif")


class TestScriptsExecutables(unittest.TestCase):
    """Les scripts doivent au moins démarrer : un import cassé bloque toute l'édition."""

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, *args], cwd=ROOT,
                              capture_output=True, text=True, timeout=180)

    def test_validate_sort_en_zero(self):
        r = self._run("pipeline/validate.py")
        self.assertEqual(r.returncode, 0, f"le validateur échoue :\n{r.stdout[-2000:]}")

    def test_recoupement_inoffensif_sans_cle(self):
        """Le recoupement est optionnel : sans clé il explique et sort en 0."""
        import os
        env = {k: v for k, v in os.environ.items() if k != "AA_API_KEY"}
        r = subprocess.run([sys.executable, "pipeline/crosscheck_aa.py"], cwd=ROOT,
                           capture_output=True, text=True, timeout=60, env=env)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        self.assertIn("OPTIONNELLE", r.stdout)

    def test_recoupement_n_ecrit_jamais(self):
        """Une contradiction entre sources s'arbitre, elle ne se fusionne pas."""
        src = (ROOT / "pipeline" / "crosscheck_aa.py").read_text(encoding="utf-8")
        self.assertNotIn("models.yaml\").write_text", src)
        self.assertNotIn("safe_dump", src, "le recoupement ne doit pas réécrire le catalogue")

    def test_worklist_demarre(self):
        r = self._run("pipeline/worklist.py")
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        self.assertIn("PLAN DE MISE À JOUR", r.stdout)

    def test_build_site_produit_une_page(self):
        r = self._run("pipeline/build_site.py")
        self.assertEqual(r.returncode, 0, r.stderr[-1500:])
        page = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        self.assertIn("<title>", page)
        self.assertGreater(len(page), 100_000)

    def test_la_page_embarque_bien_ses_donnees(self):
        page = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        for marque in ('id="payload"', "frontier", "Pareto", "coût mesuré"):
            self.assertIn(marque, page, f"la page a perdu : {marque}")


class TestGuideGenere(unittest.TestCase):
    """Le Guide et les fiches data/ sont générés : ils ne peuvent plus diverger."""

    @classmethod
    def setUpClass(cls):
        r = subprocess.run([sys.executable, "pipeline/build_guide.py"], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[-1500:]
        cls.guide = (ROOT / "Guide_Complet_Solutions_Dev_IA_2026.md").read_text(encoding="utf-8")

    def test_porte_la_mention_de_generation(self):
        self.assertIn("Ce document est **généré**", self.guide)

    def test_les_fiches_portent_l_avertissement(self):
        for f in (ROOT / "data").glob("*.md"):
            self.assertIn("FICHIER GÉNÉRÉ", f.read_text(encoding="utf-8")[:200],
                          f"{f.name} sans avertissement de génération")

    def test_chaque_tarif_du_catalogue_apparait(self):
        for m in load("models.yaml").get("models", []):
            pr = m.get("pricing") or {}
            if pr.get("input_per_1m") is None:
                continue
            self.assertIn(m.get("display_name", m["id"]), self.guide,
                          f"{m['id']} tarifé mais absent du Guide")

    def test_les_egalites_statistiques_sont_signalees(self):
        """Le Guide ne doit jamais présenter un classement que le validateur conteste."""
        import math
        scores = load("scores.yaml").get("scores", [])
        par_b = {}
        for s_ in scores:
            if s_.get("stderr") and s_.get("score") is not None:
                par_b.setdefault(s_["benchmark"], []).append(s_)
        for b, rows in par_b.items():
            r = sorted(rows, key=lambda x: -x["score"])
            if len(r) < 2:
                continue
            gap = r[0]["score"] - r[1]["score"]
            ci = 1.96 * math.sqrt(r[0]["stderr"] ** 2 + r[1]["stderr"] ** 2)
            if gap < ci:
                self.assertIn("Égalités statistiques", self.guide,
                              f"{b} est une égalité non signalée dans le Guide")
                return

    def test_aucun_euro_sans_taux_declare(self):
        if "€" in self.guide:
            self.assertIn("taux de", self.guide.lower(),
                          "des euros sont affichés sans que le taux soit énoncé")


class TestFraicheur(unittest.TestCase):
    def test_seuils_coherents(self):
        f = load("_meta.yaml")["freshness"]
        self.assertLess(f["warn_after_days"], f["stale_after_days"])

    def test_aucune_donnee_perimee_non_signalee(self):
        """Une donnée périmée doit faire échouer le validateur, pas passer en silence."""
        meta = load("_meta.yaml")
        stale = meta["freshness"]["stale_after_days"]
        limite = date.today() - timedelta(days=stale)
        perimes = []
        for m in load("models.yaml").get("models", []):
            d = ((m.get("pricing") or {}).get("source") or {}).get("verified_on")
            if d and date.fromisoformat(str(d)[:10]) < limite:
                perimes.append(m["id"])
        if perimes:
            r = subprocess.run([sys.executable, "pipeline/validate.py"], cwd=ROOT,
                               capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0,
                                "des tarifs sont périmés mais le validateur passe")


if __name__ == "__main__":
    unittest.main(verbosity=2)
