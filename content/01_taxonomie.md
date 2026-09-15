## 1. Architecture conceptuelle : la taxonomie en quatre couches

Évaluer une solution de développement assisté par IA suppose de découpler quatre
choses que le marketing mélange volontiers : l'interface, le transport, le modèle
et la facturation. Un même modèle donne des résultats différents selon le harnais
qui l'exécute, et un même harnais change de prix du tout au tout selon le régime
de facturation choisi.

```
┌────────────────────────────────────────────────────────────────────────┐
│ COUCHE 1 — LE HARNAIS D'EXÉCUTION                                      │
│ IDE dérivés · extensions VS Code · applications desktop · agents CLI   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │  REST · API OpenAI · MCP · ACP
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 2 — LA PASSERELLE                                               │
│ agrégateurs cloud · serveurs locaux compatibles OpenAI · accès direct  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 3 — LE FOURNISSEUR DE MODÈLE                                    │
│ laboratoires propriétaires · laboratoires à poids ouverts              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│ COUCHE 4 — LE MODÈLE ÉCONOMIQUE                                        │
│ forfait SaaS · facturation au token (BYOK) · auto-hébergement          │
└────────────────────────────────────────────────────────────────────────┘
```

La couche 1 n'est pas neutre. Sur Terminal-Bench, le référentiel recense des
dizaines de harnais différents pour les mêmes modèles, et l'écart qu'ils
produisent dépasse souvent l'écart entre deux modèles concurrents. C'est la
raison d'être de ce document : un score ne se lit jamais sans son harnais.
