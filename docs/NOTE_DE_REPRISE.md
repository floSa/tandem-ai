# Note de reprise

Ce qui reste à faire, consigné pour la prochaine session. À relire avant de lancer
`python3 pipeline/worklist.py`.

## Dernière passe — 16/09/2026

Mise à jour des benchmarks et retrait de l'obsolète :

- **Fenêtre glissante de 12 mois** (`scope.model_window_months`) : les modèles publiés
  avant le 16/09/2025 sont sortis des scores, du catalogue et de
  `pricing_verified.yaml` (Claude 3.7/4/4.1, GPT-4.1, o3, GPT-5, Gemini 2.5, Kimi K2,
  Grok 4…).
- **Sept benchmarks figés à la source retirés**, motif consigné dans `REJECTED` :
  Terminal-Bench 2.0, SWE-bench Verified, METR Time Horizons, Aider polyglot, Cybench,
  GDPval, The Agent Company.
- **Remplaçants ajoutés** : Terminal-Bench 4.0 (lu sur tbench.ai), CursorBench,
  FrontierSWE, PostTrainBench, GDP.pdf.
- **Contrôle de vitalité par benchmark** dans `validate.py` et `worklist.py` : c'est
  son absence qui a laissé passer la situation.
- **Correctif** : `apply_pricing.py` re-datait chaque tarif au jour de son exécution.

## À faire

### Tarifs — prochaine session

Les tarifs n'ont **pas** été re-vérifiés lors de cette passe : ils datent toujours du
relevé du 15/09/2026. Seules les entrées de modèles obsolètes ont été retirées.

### Passerelles et serveurs locaux — à compléter

Catégorie « serveurs locaux » (`catalog/tools.yaml`, catégorie `local_server`) : elle ne
couvre aujourd'hui qu'Ollama et LM Studio. À ajouter, avec relevé sur la documentation
officielle de chacun :

- **vLLM** : serveur d'inférence haute performance, API compatible OpenAI ;
- **llama.cpp en conteneur** (`llama-server`, images Docker officielles) ;
- **services de déploiement direct d'un modèle**, type Hugging Face Inference
  Endpoints : on choisit un modèle du Hub et le service le sert derrière une API. À
  situer entre « serveur local » et « passerelle » : ce n'est ni un routeur multi-labs,
  ni un serveur qu'on héberge soi-même.

### Benchmarks — points de vigilance

- **GSO-Bench** : dernier modèle mesuré fin juin 2026, 65 j de retard. Il passera en
  sommeil vers octobre s'il n'est pas relancé.
- **GPQA diamond et ARC-AGI-2** approchent de la saturation (96 % et 95 %) : leur
  chercher des remplaçants.
- **Terminal-Bench 4.0** est lu dans le flux Next.js de tbench.ai, faute d'API. Si le
  site change, `tbench_ingest.py` échoue bruyamment : adapter le parseur. Un libellé de
  modèle inconnu d'Epoch est écarté et signalé — compléter `ALIASES`.
- **METR** : surveiller la sortie d'une suite v2. La v1.1 est saturée.
- **HLE** : encore vivant, mais seul Fable 5.1 y a été mesuré depuis juin 2026.
- **Instantané** : ne pas oublier `python3 pipeline/changelog.py --snapshot` après
  publication de cette édition.
