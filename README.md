# Style-transfer
My first repository on GitHub. This is a research done by a high school student on exploring how well each LLM does on transferring scientific essays to science popular articles.

## Overview

This repository provides an evaluation of LLMs on **scientific-to-
popular style transfer** — rewriting scientific essays so that they are
understandable to a high school students.

## Dataset

**`ST-Bench_all_domain.csv`**

Contains 150 CC-BY licensed scientific essays scraped from arXiv (HTML format), spanning
three domains: **Computer Science, Physics, and Mathematics** (50 essays
each). These domains were chosen to test a broad range of skills, from simplifying
complex mathematical formulas to explaining nuanced experimental results. The dates of the articles 
are between 2026/2/24 to 2026/2/26 in the ArXiv ‘recent’ section to mitigate 
data contamination. Additionally, users can apply our codes to scrape the latest arXiv entries and continuously 
expand the benchmark, ensuring the benchmark remains challenging
for future models. 

## Repository Structure

```
├── generated_prompts/     # Style-transfer generation code
│   ├── gpt_style_transfer.ipynb
│   ├── Llama_style_transfer.ipynb
│   ├── Mixtral_style_transfer.ipynb
│   └── transfer_prompt.py
├── LLM_judgesv1/           # Automated scoring
│   ├── gpt_as_judge.ipynb
│   ├── llama_as_judge.ipynb
│   ├── claude_as_judge.ipynb        # not yet run (no API access)
│   ├── G_Eval_gpt.ipynb
│   ├── G_Eval_claude.ipynb
│   ├── GEval_prompt.py
│   └── prompt.py
├── test_results/
│   └── results_<LLM>_all.csv
│   └── results_gpt_rate_<LLM>.csv
│   └── results_gpt_geval_rate_<LLM>.csv
│   └── manual_rating.csv
├── pipeline.py
├── unit_test_pipeline.py
└── ST-Bench_all_domain.csv
```

## Generator Models

To compare *model families* (not model generations), the three generators
use current-generation models from each family rather than mixing a
frontier model with legacy open-weight ones.

| Family | Model | Generation | Notes |
|--------|-------|------------|-------|
| OpenAI | GPT-5.2 (frontier API model) | late-2025/2026 | Requires OpenAI API key. |
| Meta | `Llama-3.1-8B-Instruct` | Llama 3.1, Jul 2024 | Requires Hugging Face API key. Llama 4 can not be used in a Google Colab environment due to memory constraints.(4-bit, Unsloth) |
| Mistral | `mistralai/Ministral-3-8B-Instruct-2512` | Ministral 3, Dec 2025 | Current generation of the same 8B-dense line as the original Ministral-8B; still runnable in 4-bit. Requires Hugging Face API key. |

Model outputs are saved to `results_<LLM>_all.csv` in `test_results/`.

### Environment

All experiments were run on **Google Colab**.

- `generated_prompts/` — requires an **A100 GPU** (source essays are long)
- `LLM_judgesv1/` — CPU only

## Evaluation

Rewrites are scored using two approaches:

- **Likert scale (1–5)** 
- **G-Eval (0.0–1.0)** 

Both are based on the same three criteria (see prompts in `LLM_judges/`),
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

### Results

| Model | Strengths | Weaknesses |
|---|---|---|
| GPT-5.2 | Extremely strong at concise and accurate summarization; high information density | Often leaves jargon unexplained |
| Ministral-3-8B | Effective and interesting analogies; most understandable to a general reader | A bit verbose and excess the word limit|
| Llama-3.1-8B | Adds more detail on methods/findings | Excess the word limit; reads less like genuine popular science |

### Limitations & Reflection

As a non-expert in the scientific fields, manual Content Preservation ratings
are likely less reliable than the LLM judges'. Style Transfer Intensity
ratings were based on how well I personally understood each
response, making them inherently subjective. Language Naturalness ratings
were based on how "human-written" a response felt, which is also
subjective.

Notably, manual scores for Ministral-3-8B diverged substantially from the
LLM judges' scores. In several cases, its rewrites made me understand  the paper's
core contribution even if I previously didn't understand what the abstract was talking about.
This fulfilled the benchmark's primary goal of making advanced science accessible to a high-school reader. 
By comparison, I think the LLM judges appeared to weigh factual accuracy more heavily and thus caused the
discrepany. This invoked me of an open question: what should matter most in
scientific-to-popular style transfer? How can rigorous, quantitative
scoring capture the more intuitive, human sense of what makes a piece of
knowledge truly understandable? Therefore, future work will lie in the exploration of more rigorous metrics to evaluate LLMs' responses, and the expansion of the essay range into different languages.

## Acknowledgements

The use of Inspirit AI resources including the ChatGPT API and a Google Colab A100
machine is acknowledged. Thanks to Mia Gancayco for her guidance and
support throughout this project.
