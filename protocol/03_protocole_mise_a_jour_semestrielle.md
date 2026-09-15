# Protocole de Mise à Jour Semestrielle de l'Audit

## 1. Objectif
Ce document décrit la procédure étape par étape pour réexécuter l'audit complet tous les 6 mois (par exemple en février 2027), afin de mettre à jour le référentiel sans avoir à réinventer la structure d'analyse.

---

## 2. Checklist de Ré-Exécution Semestrielle

### Étape 1 : Veille & Découverte des Nouveaux Acteurs
Exécuter des requêtes web ciblées en anglais pour détecter les nouveaux outils émergents et les pivots d'entreprises :
* `"AI code editor" "VS Code fork" [Année]`
* `"autonomous coding agent" terminal OR CLI [Année]`
* `"VS Code AI extension" marketplace [Année]`
* `"open source coding harness" LLM [Année]`

### Étape 2 : Vérification des Statuts et Dépréciations
Pour chaque outil existant dans le dossier `data/` :
1. Vérifier si le projet est toujours actif, racheté, renommé ou archivé.
2. Mettre à jour les URL officielles, liens de dépôts et marques commerciales.
3. Noter les éventuels changements d'architecture (ex: passage à des sous-agents, adoption massive de MCP).

### Étape 3 : Audit des Grilles Tarifaires et Modèles de Production
Pour chaque fournisseur de modèles :
1. Consulter la page `/pricing` officielle anglophone du fournisseur.
2. Noter la disparition des anciens alias de modèles et l'arrivée des nouvelles générations (ex: passage à une nouvelle génération de modèles).
3. Relever les coûts exacts au 1M tokens :
   * Input (Standard)
   * Input (Cache Hit)
   * Output
   * Tarification dynamique (Peak / Off-Peak si applicable).
4. Relever les nouveaux paliers d'abonnements SaaS (ex: quotas de crédits IA, changements de seuils pour les requêtes rapides).

### Étape 4 : Mise à Jour des Fiches Individuelles dans `data/`
1. Modifier directement les fichiers markdown dans `data/01_ide_natifs_et_forks.md`, `data/02_extensions_harnais_vscode.md`, etc.
2. Ajouter de nouveaux fichiers si une nouvelle catégorie émerge.

### Étape 5 : Régénération du Rapport Global
1. Reporter les nouvelles données dans `Guide_Complet_Solutions_Dev_IA_2026.md` (ou version n+1).
2. Actualiser les tableaux comparatifs de coûts et les matrices de recommandation matérielle.
