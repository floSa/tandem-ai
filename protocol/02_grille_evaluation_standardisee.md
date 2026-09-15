# Grille d'Évaluation Standardisée (« Fiche Identité »)

Cette grille d'évaluation sert de gabarit d'analyse pour toute solution ou fournisseur évalué dans le cadre de l'audit.

---

## 1. Gabarit pour les Outils & Harnais de Développement (IDE, Extension, Desktop, CLI)

* **Nom de l'outil :** `[Nom officiel et version active]`
* **Éditeur / Organisation :** `[Société ou Collectif open-source responsable]`
* **Liens Officiels :**
  * Site web officiel : `[URL]`
  * Documentation technique : `[URL]`
  * Dépôt GitHub / Open VSX : `[URL si applicable]`
  * Page des tarifs : `[URL]`
* **Catégorie Technique :** `[IDE Dérivé / Extension VS Code / Desktop GUI / Agent CLI]`
* **Intégration & Workflow Développeur :**
  * Mode d'intégration : `[Fork natif VS Code / Plugin marketplace / Terminal pur / App externe]`
  * Capacités agentiques : `[Autocomplétion / Chat contextuel / Agent autonome multi-fichiers / Exécution terminal]`
* **Gestion des Modèles :**
  * Modèles fournis par défaut : `[Modèles inclus dans l'offre]`
  * Support BYOK (*Bring Your Own Key*) : `[Oui / Non]`
  * Support OpenRouter / Passerelles : `[Oui / Non]`
  * Support Modèles Locaux (Ollama, LM Studio) : `[Oui / Non]`
* **Modèle Économique & Tarification :**
  * Version Gratuite : `[Quotas et fonctionnalités incluses]`
  * Formules d'Abonnement : `[Prix/mois, quotas de requêtes rapides, crédits]`
  * Coût en mode API / BYOK : `[Gratuit (coût API uniquement) ou surcoût par requête/token]`
* **Forces Principales :** `[Points différenciants majeurs]`
* **Limites & Points d'Attention :** `[Dépendance cloud, limitations d'autonomie, verrouillage propriétaire]`

---

## 2. Gabarit pour les Fournisseurs de Modèles (Labs IA)

* **Nom du Fournisseur :** `[Nom du Lab ou de l'Entreprise]`
* **Liens Officiels :**
  * Console Développeur / Plateforme API : `[URL]`
  * Documentation API : `[URL]`
  * Page Tarifs Officielle : `[URL]`
* **Présence Outils & Écosystème Développeur :**
  * Application Desktop officielle : `[Oui / Non — Détails et fonctionnalités]`
  * Extension / Harnais VS Code officiel : `[Oui / Non — Nom et lien]`
  * Agent CLI officiel : `[Oui / Non — Nom et lien]`
* **Abonnements SaaS Grand Public / Pro :**
  * Noms des forfaits : `[ex: Plus, Pro, Ultra, Team]`
  * Prix mensuel : `[Prix en $ / mois]`
  * Périmètre couvert : `[Interface web/desktop uniquement, ou accès API/IDE inclus]`
* **Tarification API au Million de Tokens (Août 2026) :**
  * Modèle Flagship / Raisonnement :
    * Nom du modèle : `[Model ID exact]`
    * Input (Cache Miss) : `[$ / 1M tokens]`
    * Input (Cache Hit / Cached) : `[$ / 1M tokens]`
    * Output : `[$ / 1M tokens]`
  * Modèle Flash / Économique :
    * Nom du modèle : `[Model ID exact]`
    * Input (Cache Miss) : `[$ / 1M tokens]`
    * Input (Cache Hit / Cached) : `[$ / 1M tokens]`
    * Output : `[$ / 1M tokens]`
  * Particularités tarifaires : `[Heures creuses, remises par lots, variations régionales]`
* **Interopérabilité dans les Harnais Tiers :**
  * Compatible endpoints OpenAI : `[Oui / Non]`
  * Présence sur OpenRouter : `[Oui / Non]`
  * Poids ouverts téléchargeables (Ollama / HuggingFace) : `[Oui / Non / Modèles spécifiques]`
