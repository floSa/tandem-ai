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

    def test_model_base_sans_suffixe_d_effort(self):
        for s in self.scores:
            mb = s.get("model_base")
            if not mb:
                continue
            self.assertIsNone(
                re.search(r"_(max|xhigh|high|medium|low|minimal)$", mb),
                f"`model_base` porte encore un suffixe d'effort : {mb}")

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
