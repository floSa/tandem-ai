<!-- FICHIER GÉNÉRÉ par pipeline/build_guide.py — ne pas éditer.
     Corriger dans catalog/, puis régénérer. -->

# Fournisseurs de modèles

11 laboratoires suivis. Généré le 2026-09-15 depuis `catalog/`.

## Anthropic

- **Pays :** US
- **Tarifs :** [https://www.anthropic.com/pricing](https://www.anthropic.com/pricing)
- **Documentation :** [https://docs.claude.com/en/docs/about-claude/models](https://docs.claude.com/en/docs/about-claude/models)
- **Modèles au catalogue :** 35 · **tarifés :** 4

| Modèle | Entrée $ | Cache $ | Sortie $ | Contexte | Relevé le |
| :-- | --: | --: | --: | --: | :-- |
| Claude Haiku 4.5 | $1 | $0.1 | $5 | 200k | 2026-09-15 |
| Claude Sonnet 5 | $2 | $0.2 | $10 | 200k | 2026-09-15 |
| Claude Opus 5 | $5 | $0.5 | $25 | 200k | 2026-09-15 |
| Claude Fable 5.1 | $10 | $0.25 | $50 | 200k | 2026-09-15 |

**Meilleurs scores mesurés**

- `claude-opus-4-5-20251101` — Cybench 82.0% · GPQA diamond 80.7% · SWE-Bench verified 76.6%
- `claude-opus-4-7` — GPQA diamond 90.1% · SWE-Bench verified 83.5% · Terminal Bench 80.2%
- `claude-opus-4-6` — Cybench 93.0% · GPQA diamond 88.4% · Terminal Bench 79.8%
- `claude-sonnet-4-5-20250929` — GPQA diamond 73.7% · SWE-Bench verified 71.3% · Cybench 60.0%
- `claude-opus-4-8` — GPQA diamond 91.0% · ARC-AGI-2 72.1% · DeepSWE 59.0%
- `claude-sonnet-4-6` — GPQA diamond 83.3% · SWE-Bench verified 75.2% · ARC-AGI-2 60.4%

## OpenAI

- **Pays :** US
- **Tarifs :** [https://openai.com/api/pricing/](https://openai.com/api/pricing/)
- **Documentation :** [https://platform.openai.com/docs/models](https://platform.openai.com/docs/models)
- **Modèles au catalogue :** 44 · **tarifés :** 9

| Modèle | Entrée $ | Cache $ | Sortie $ | Contexte | Relevé le |
| :-- | --: | --: | --: | --: | :-- |
| GPT-5.6 Luna | $0.2 | $0.02 | $1.2 | — | 2026-09-15 |
| GPT-5.6 Terra | $2 | $0.2 | $12 | — | 2026-09-15 |
| o3 | $2 | $0.5 | $8 | — | 2026-09-15 |
| GPT-5.4 | $2.5 | $0.25 | $15 | — | 2026-09-15 |
| GPT-5.6 Sol | $4 | $0.4 | $20 | — | 2026-09-15 |
| GPT-5.5 | $5 | $0.5 | $30 | — | 2026-09-15 |
| GPT-6 Astra | $10 | $1 | $50 | — | 2026-09-15 |
| o3-pro | $20 | — | $80 | — | 2026-09-15 |
| GPT-5.5 Pro | $30 | — | $180 | — | 2026-09-15 |

**Meilleurs scores mesurés**

- `gpt-5-2025-08-07` — Aider polyglot 88.0% · GPQA diamond 86.2% · SWE-Bench verified 73.6%
- `gpt-5.4-2026-03-05` — GPQA diamond 93.3% · Terminal Bench 81.8% · SWE-Bench verified 76.9%
- `gpt-5.5` — GPQA diamond 90.7% · ARC-AGI-2 85.0% · Terminal Bench 84.7%
- `gpt-5.2-2025-12-11` — GPQA diamond 91.4% · METR Time Horizons 75.3% · SWE-Bench verified 73.8%
- `gpt-5.1-2025-11-13` — GPQA diamond 87.6% · SWE-Bench verified 68.0% · Terminal Bench 47.6%
- `gpt-5.6-sol` — GPQA diamond 93.5% · ARC-AGI-2 92.5% · DeepSWE 72.7%

## Google DeepMind

- **Pays :** US
- **Tarifs :** [https://ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)
- **Documentation :** [https://ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)
- **Modèles au catalogue :** 22 · **tarifés :** 4

| Modèle | Entrée $ | Cache $ | Sortie $ | Contexte | Relevé le |
| :-- | --: | --: | --: | --: | :-- |
| Gemini 3.5 Flash-Lite | $0.3 | $0.03 | $2.5 | — | 2026-09-15 |
| Gemini 3.8 Flash | $0.75 | $0.075 | $3.75 | — | 2026-09-15 |
| Gemini 3.5 Flash | $1.5 | $0.15 | $9 | — | 2026-09-15 |
| Gemini 3.1 Pro | $2 | $0.2 | $12 | 200k | 2026-09-15 |

**Meilleurs scores mesurés**

- `gemini-3-pro-preview` — GPQA diamond 92.6% · SWE-Bench verified 72.9% · METR Time Horizons 71.0%
- `gemini-3.1-pro-preview` — GPQA diamond 94.4% · Terminal Bench 80.2% · ARC-AGI-2 77.1%
- `gemini-2.5-pro` — GPQA diamond 85.3% · SWE-Bench verified 57.6% · SciCode 42.8%
- `gemini-2.5-pro-preview-06-05` — GPQA diamond 84.9% · Aider polyglot 79.1% · METR Time Horizons 55.4%
- `gemini-3-flash-preview` — GPQA diamond 89.4% · SWE-Bench verified 75.4% · Terminal Bench 64.3%
- `gemini-3.7-flash` — GPQA diamond 94.8% · ARC-AGI-2 84.6% · DeepSWE 65.5%

## DeepSeek

- **Pays :** CN
- **Tarifs :** [https://api-docs.deepseek.com/quick_start/pricing](https://api-docs.deepseek.com/quick_start/pricing)
- **Documentation :** [https://api-docs.deepseek.com](https://api-docs.deepseek.com)
- **Modèles au catalogue :** 14 · **tarifés :** 2

| Modèle | Entrée $ | Cache $ | Sortie $ | Contexte | Relevé le |
| :-- | --: | --: | --: | --: | :-- |
| DeepSeek Flash | $0.3 | $0.006 | $1.2 | 1000k | 2026-09-15 |
| DeepSeek V4-Pro | $1.32 | $0.044 | $3.96 | 1000k | 2026-09-15 |

**Meilleurs scores mesurés**

- `deepseek-v4-flash-0731` — GPQA diamond 91.0% · ARC-AGI-2 61.4% · SciCode 49.9%
- `deepseek-v4-pro` — GPQA diamond 90.9% · SWE-Bench verified 77.6% · SciCode 50.0%
- `deepseek-v4-pro-0813` — GPQA diamond 91.7% · ARC-AGI-2 61.3% · SciCode 49.2%
- `deepseek/deepseek-v3.2` — Terminal Bench 39.6% · APEX-Agents 7.0% · ARC-AGI-2 4.0%
- `DeepSeek-V3.2-Exp` — Aider polyglot 70.2% · The Agent Company 52.4%
- `DeepSeek-V3.2-Exp_thinking` — Aider polyglot 74.2% · SciCode 38.9%

## Alibaba

- **Pays :** CN
- **Tarifs :** [https://www.alibabacloud.com/help/en/model-studio/models](https://www.alibabacloud.com/help/en/model-studio/models)
- **Documentation :** [https://www.alibabacloud.com/help/en/model-studio](https://www.alibabacloud.com/help/en/model-studio)
- **Modèles au catalogue :** 32 · **tarifés :** 0

**Meilleurs scores mesurés**

- `qwen3.7-plus` — GPQA diamond 87.9% · SciCode 45.5% · FrontierCode 10.2%
- `qwen3.5-9B` — GPQA diamond 79.0% · SciCode 27.6% · Terminal Bench 9.2%
- `qwen3.6-35b-a3b` — GPQA diamond 84.9% · SciCode 35.8% · Terminal Bench 23.0%
- `qwen3.6-plus` — GPQA diamond 88.4% · SWE-Bench verified 57.9% · SciCode 40.7%
- `qwen3.7-max` — GPQA diamond 90.9% · SWE-Bench verified 77.3% · SciCode 48.8%
- `qwen3.8-max` — GPQA diamond 92.7% · DeepSWE 57.5% · SciCode 52.9%

## Mistral AI

- **Pays :** FR
- **Tarifs :** [https://mistral.ai/pricing](https://mistral.ai/pricing)
- **Documentation :** [https://docs.mistral.ai/getting-started/models/models_overview/](https://docs.mistral.ai/getting-started/models/models_overview/)
- **Modèles au catalogue :** 10 · **tarifés :** 0

**Meilleurs scores mesurés**

- `magistral-small-2506` — GPQA diamond 56.1% · ARC-AGI-2 0.0%
- `magistral-small-2509` — GPQA diamond 47.6% · SciCode 35.2%
- `mistral-medium-2604` — SciCode 39.6% · FrontierCode 8.0%
- `devstral-small-2512` — SciCode 28.8%
- `magistral-medium-2506` — ARC-AGI-2 0.0%
- `magistral-medium-2509` — SciCode 39.2%

## Moonshot

- **Pays :** CN
- **Tarifs :** [https://platform.moonshot.ai/docs/pricing](https://platform.moonshot.ai/docs/pricing)
- **Documentation :** [https://platform.moonshot.ai/docs](https://platform.moonshot.ai/docs)
- **Modèles au catalogue :** 9 · **tarifés :** 3

| Modèle | Entrée $ | Cache $ | Sortie $ | Contexte | Relevé le |
| :-- | --: | --: | --: | --: | :-- |
| Kimi K2.6 | $0.95 | $0.16 | $4 | 262k | 2026-09-15 |
| Kimi K2.7 Code | $0.95 | $0.19 | $4 | 262k | 2026-09-15 |
| Kimi K3 | $3 | $0.3 | $15 | 1048k | 2026-09-15 |

**Meilleurs scores mesurés**

- `kimi-k2.5` — SWE-Bench verified 73.8% · SciCode 49.0% · Terminal Bench 43.2%
- `kimi-k3` — GPQA diamond 93.1% · DeepSWE 68.5% · ARC-AGI-2 60.4%
- `kimi-k2.6` — GPQA diamond 90.8% · SWE-Bench verified 76.6% · SciCode 53.5%
- `kimi-k2.7-code` — GPQA diamond 87.9% · SciCode 47.4% · DeepSWE 30.5%
- `Kimi-K2-Instruct` — Aider polyglot 59.1% · Terminal Bench 27.8% · GSO-Bench 4.9%
- `kimi-k2-thinking` — METR Time Horizons 59.2% · Terminal Bench 35.7% · APEX-Agents 4.1%

## Z.ai (Zhipu AI)

- **Pays :** CN
- **Tarifs :** [https://docs.z.ai/guides/overview/pricing](https://docs.z.ai/guides/overview/pricing)
- **Documentation :** [https://docs.z.ai](https://docs.z.ai)
- **Modèles au catalogue :** 9 · **tarifés :** 3

| Modèle | Entrée $ | Cache $ | Sortie $ | Contexte | Relevé le |
| :-- | --: | --: | --: | --: | :-- |
| GLM-4.7-Flash | gratuit | gratuit | gratuit | — | 2026-09-15 |
| GLM-5.3-Flash | $0.15 | $0.03 | $0.5 | — | 2026-09-15 |
| GLM-5.3 | $1.4 | $0.26 | $4.4 | — | 2026-09-15 |

**Meilleurs scores mesurés**

- `glm-5.2` — GPQA diamond 91.9% · SWE-Bench verified 78.7% · SciCode 50.5%
- `glm-5` — GPQA diamond 87.8% · SWE-Bench verified 72.1% · Terminal Bench 52.4%
- `glm-4.7` — GPQA diamond 83.3% · SciCode 45.1% · Terminal Bench 33.4%
- `glm-5.1` — GPQA diamond 89.9% · SWE-Bench verified 74.2% · SciCode 43.8%
- `glm-5.3` — GPQA diamond 90.9% · DeepSWE 69.0% · SciCode 56.5%
- `glm-5.3-flash` — GPQA diamond 90.1% · DeepSWE 63.4% · SciCode 46.1%

## xAI

- **Pays :** US
- **Tarifs :** [https://docs.x.ai/docs/models](https://docs.x.ai/docs/models)
- **Documentation :** [https://docs.x.ai](https://docs.x.ai)
- **Modèles au catalogue :** 10 · **tarifés :** 0

**Meilleurs scores mesurés**

- `grok-4-0709` — GPQA diamond 87.0% · Aider polyglot 79.6% · METR Time Horizons 66.6%
- `grok-4.5` — GPQA diamond 93.4% · SciCode 54.0% · DeepSWE 53.8%
- `grok-4.6` — GPQA diamond 94.0% · DeepSWE 67.5% · ARC-AGI-2 67.1%
- `grok-4-1` — Cybench 39.0% · APEX-Agents 12.8%
- `grok-4-20` — ARC-AGI-2 65.1% · Terminal Bench 57.3%
- `grok-4-fast` — Cybench 30.0% · ARC-AGI-2 5.3%

## Meta AI

- **Pays :** US
- **Tarifs :** [https://llama.developer.meta.com/docs/pricing](https://llama.developer.meta.com/docs/pricing)
- **Documentation :** [https://llama.developer.meta.com/docs](https://llama.developer.meta.com/docs)
- **Modèles au catalogue :** 3 · **tarifés :** 0

**Meilleurs scores mesurés**

- `muse-spark` — GPQA diamond 89.8% · SciCode 51.5% · HLE 40.6%
- `muse-spark-1.1` — SciCode 58.2% · DeepSWE 53.3% · APEX-Agents 41.9%
- `muse-spark-1.2` — SciCode 56.4% · DeepSWE 54.9%

## MiniMax

- **Pays :** CN
- **Tarifs :** [https://platform.minimax.io/docs/price](https://platform.minimax.io/docs/price)
- **Documentation :** [https://platform.minimax.io/docs](https://platform.minimax.io/docs)
- **Modèles au catalogue :** 6 · **tarifés :** 0

**Meilleurs scores mesurés**

- `MiniMax-M3` — GPQA diamond 90.9% · SciCode 45.4% · FrontierCode 14.7%
- `MiniMax-M2.5` — Terminal Bench 42.7% · APEX-Agents 6.2% · ARC-AGI-2 4.9%
- `MiniMax-M2.7` — SciCode 47.0% · Terminal Bench 45.1%
- `MiniMax-M2` — Terminal Bench 30.0%
- `MiniMax-M2.1` — Terminal Bench 36.6%

