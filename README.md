# Style-transfer
My first repository on GitHub. This is a research done by a high school student on exploring how well each LLM does on transferring scientific essays to science popular articles.

# ST-Bench: Scientific-to-Popular Style Transfer Benchmark

My first repository on GitHub. This is a research project by a high school
student exploring how well different LLMs perform at transferring scientific
essays into popular-science articles aimed at high school readers.

## Overview

This repository provides a rigorous evaluation of LLMs on **scientific-to-
popular style transfer** — rewriting scientific essays so that they are
understandable to a high school audience.

## Dataset

**`ST-Bench_all_domain.csv`**

Contains 150 scientific essays scraped from arXiv (HTML format), spanning
three domains — **Computer Science, Physics, and Mathematics** (50 essays
each) — along with the corresponding LLM-generated popular-science rewrites.
These domains were chosen to test a broad range of skills, from simplifying
complex mathematical formulas to explaining nuanced experimental results.

## Repository Structure

```
├── generated_prompts/     # Style-transfer generation code
│   ├── gpt_style_transfer.ipynb
│   ├── Llama_style_transfer.ipynb
│   ├── Mixtral_style_transfer.ipynb   # <!-- confirm: rename to Ministral? -->
│   └── transfer_prompt.py
├── LLM_judgesv1/           # Automated scoring
│   ├── gpt_as_judge.ipynb
│   ├── llama_as_judge.ipynb
│   ├── claude_as_judge.ipynb          # not yet run (no API access)
│   ├── G_Eval_gpt.ipynb
│   ├── G_Eval_claude.ipynb
│   ├── GEval_prompt.py
│   └── prompt.py
├── score_analysis/
│   └── cohen_kappa_score.ipynb
├── test_results/
│   └── results_<LLM>_all.csv
├── pipeline.py
├── unit_test_pipeline.py
└── ST-Bench_all_domain.csv
```

## Generator Models

Three models were used to generate the popular-science rewrites:

| Model | Provider | Notes |
|---|---|---|
| GPT-5.2 | OpenAI | Requires OpenAI API key |
| Llama-3.1-8B | Meta | Requires Hugging Face API key |
| Ministral-3-8B | Mistral | Requires Hugging Face API key |

Model outputs are saved to `results_<LLM>_all.csv` in `test_results/`.

### Environment

All experiments were run on **Google Colab**.

- `generated_prompts/` — requires an **A100 GPU** (source essays are long)
- `LLM_judgesv1/` — CPU only

## Evaluation

Rewrites are scored using two approaches:

- **Likert scale (1–5)** — discrete, scored by GPT-5.2
- **G-Eval (0.0–1.0)** — continuous, fine-grained

Both are based on the same three criteria (see prompts in `LLM_judgesv1/`),
combined into a final overall score. The Likert scoring additionally reports
each criterion individually:

| Criterion | Description |
|---|---|
| **Content Preservation (C)** | How well the response preserves the content of the original essay |
| **Style Transfer Intensity (ST)** | How well the response matches popular-science style, including removal or plain-language explanation of jargon |
| **Language Naturalness (N)** | How fluent and natural the response reads |

Code for using **Claude as judge** is also included, intended to reduce
self-bias when evaluating GPT's own outputs. This has not yet been run due
to lack of API access.

## Manual Rating

To validate the reliability of the automated LLM scoring, 9 articles per
model (3 each from Math, Physics, and CS) were manually rated.

## Results

| Model | Strengths | Weaknesses |
|---|---|---|
| GPT-5.2 | Extremely strong summarization; high information density per sentence | Often leaves jargon unexplained |
| Ministral-3-8B | Frequent, effective analogies; most understandable to a general reader | Tends to be verbose |
| Llama-3.1-8B | Adds more detail on methods/findings than Ministral | Longer than GPT; reads less like genuine popular science |

## Limitations & Reflection

As a non-expert in the source material, manual Content Preservation ratings
are likely less reliable than the LLM judges'. Style Transfer Intensity
ratings were based on how well the rater personally understood each
response, making them inherently subjective; Language Naturalness ratings
were based on how "human-written" a response felt, which is similarly
subjective.

Notably, manual scores for Ministral-3-8B diverged substantially from the
LLM judges' scores. In several cases, its rewrites took the rater from not
understanding the abstract at all to genuinely understanding the paper's
core contribution — arguably fulfilling the benchmark's goal of making
advanced science accessible to a high-school reader. The LLM judges, by
contrast, appeared to weight factual/detail accuracy more heavily. This
discrepancy highlights a deeper open question: what should matter most in
scientific-to-popular style transfer, and how can rigorous, quantitative
scoring capture the more intuitive, human sense of what makes a piece of
writing truly understandable?

## Acknowledgements

The use of Inspirit AI resources — the ChatGPT API and a Google Colab A100
machine — is acknowledged. Thanks to Mia Gancayco for her guidance and
support throughout this project.


## Generator models

To compare *model families* (not model generations), the three generators use
current-generation models from each family rather than mixing a frontier model
with legacy open-weight ones (audit issue H10):

| Family  | Model                                              | Generation       | Notes |
|---------|----------------------------------------------------|------------------|-------|
| OpenAI  | GPT (frontier API model)                           | late-2025/2026   | Set the exact model name in `gpt_style_transfer.ipynb`. |
| Meta    | `Llama-4-Scout-17B-16E-Instruct` (4-bit, Unsloth)  | Llama 4, Apr 2025| MoE (17B active / 109B total); ~55 GB in 4-bit, needs an A100 80GB / H100 — will **not** fit a free Colab T4. |
| Mistral | `mistralai/Ministral-3-8B-Instruct-2512`           | Ministral 3, Dec 2025 | Current generation of the same 8B-dense line as the original Ministral-8B; still runnable in 4-bit. |

Llama 4 is MoE-only (no small dense 8B), so restoring Meta-family generation
parity requires the larger Scout checkpoint and more GPU than the prior 8B model.
