# Style-transfer
My first repository on GitHub. This is a research done by a high school student on exploring how well each LLM does on transferring scientific essays to science popular articles.

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
