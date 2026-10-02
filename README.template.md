# LLM speeds on AMD Strix Halo — every model I measured

**Sortable version: <https://huppiflupp.github.io/strix-halo-llm-speeds/>** — click a column
header, search, filter by device. GitHub cannot sort tables in a README.

One list of all language models tried on one machine, with their generation speed in
tokens per second. {{SUMMARY}}

**Machine:** AMD Ryzen AI MAX+ 395, Radeon 8060S iGPU (gfx1151, RDNA 3.5) + XDNA2 NPU,
128 GB LPDDR5X-8000 unified memory, Nobara Linux 44, kernel 7.1–7.2.
**Period:** August – 29 September 2026.

> **Read this first.** The numbers come from different harnesses and are **not** a ranking
> to the decimal. The *How* column says which one produced a figure; the legend is
> [below](#how-the-numbers-were-measured). Models that were tried but produced **no number**
> are in [their own table](#tried-but-no-number).

## The list

One row per model, with its **fastest configuration** (mean over the prompts of that run).
Differences of one or two percent between runs are noise, so the list keeps the figure from
the running service where there is one. Every other measurement of the same model is in
[All measurements per model](#all-measurements-per-model).

{{LIST}}

Generation speed is memory-bound on this machine: what counts is how many bytes are read
per token, not the parameter count in the name. Every model above 40 tok/s is either small
(8B or less) or a mixture-of-experts with few active parameters; dense models from 27B
upwards stay below 15 tok/s unless speculative decoding (MTP, DSpark) helps.

## Tried, but no number

{{NO_NUMBER}}

Figures for other models that appear in my notes (GLM-4.5-Air at 25.0 tok/s,
Qwen3-235B-A22B at 17.2 tok/s) are **third-party measurements** quoted for comparison. They
were not measured here and are therefore not in the list.

## All measurements per model

Models with more than one measurement, fastest first. Click a name to open its table.

{{VARIANTS}}

## Notes on single models

**GLM-5.3-Flash.** Needs `-fa off` (PR #27754; the MLA latent is cast to F16). Wikitext
perplexity 4.49 (4 chunks of 2048, GPU). Occupies 89 GiB loaded, 95 GiB with MTP, so it only
runs alone; the larger quants (UD-Q2_K_XL 109 GB, UD-IQ3_XXS 120 GB) exceed what this machine
can hold. MTP acceptance 54–80 %. For comparison, unsloth reports 86.5 tok/s with MTP on one
B200. The first load attempt on 2026-09-21 failed because the architecture was not yet in
the build.

**Qwen3.6-35B-A3B and Qwen3-30B-A3B, measurements of 2026-09-29.** Perplexity check
(wikitext-2, 4 × 2048): for Qwen3.6 the lab build, master and master + #29182 all give 6.3139
at `-ub 512`; master 6.3124 and master + #25666 6.3154 at `-ub 4`. Qwen3-30B: 6.6888 (lab) and
6.6770 (master, master + #29182), 6.6844 / 6.6861 at `-ub 4` with / without the new MMVQ path.
None of the new paths computes wrongly.

**Qwen3.8-Flash-Next.** Occupies 90–94 GiB when loaded and only runs alone. With the full 262,144-token context and MTP it still fits alone: 78.2 GiB GTT plus 27.1 GiB host RAM,
about 10 GiB left (probe 2026-09-29); a second 262k slot does not fit. Greedy output
with MTP differs from greedy output without it (from token 15–53 on). Checked on 2026-09-29
token by token: at every divergence the MTP token is the target model's close second choice,
and the target model alone picks that same token at 23 of 38 positions once the last three
tokens run as one batch, as in MTP verification. The divergence is batch-dependent rounding
in Vulkan, not an MTP defect.

**DeepSeek-V4-Flash.** Perplexity (wikitext): UD-IQ3_XXS 4.57, UD-IQ2_XXS 5.21. IQ2 plus draft
model occupied 108 of 124 GB and hung the amdgpu driver once; it is a measurement setup, not
an operating mode. The Lucebox rows with 4 of 6 experts reduce the expert routing and are
not the same model.

**Mistral-Small-4-119B (2026-10-02).** Stock llama.cpp generates only 0.82 tok/s on Vulkan,
whatever the settings. The cause is one line: for `mistral4`, `build_moe_ffn` marks the
`ffn_down_exps` MUL_MAT_ID as F32 precision ("src1 can exceed F16 range"), and the Vulkan
backend's `supports_op` refuses MUL_MAT_ID at F32 precision. The op falls back to the CPU in
all 36 layers, and the scheduler copies about 0.9 GB of expert weights per layer and token
(perf: 33 % memmove, the rest OpenMP barriers). The GPU itself needs only ~34 ms per token.
Still the same in upstream 254b17730 of 2026-10-02; Metal got its own fix in #29029.
Letting Vulkan take the op anyway (env-gated one-line patch) gives 35.3 tok/s and 409 tok/s
prompt, perplexity 4.3256 against 4.3248 on the CPU path (wikitext-2, 4 chunks), so no
visible overflow on that text. Mistral's own EAGLE draft is EAGLE-1 with two MLA layers in
FP8, vLLM only; llama.cpp supports EAGLE-3 with Llama layers only. Ministral-3-3B as a draft
model shares the vocabulary except tokens 36/37 (`[MODEL_SETTINGS]`), needs a relaxed vocab
check and makes it slower (21–27 tok/s). `ngram-mod` helps on code (59.5 tok/s) and hurts on
free text (30.7). 92 GiB in use, runs only alone.

**gpt-oss-120b.** Generation sits at 85 % of the memory-bandwidth ceiling (62.9 tok/s). The
EAGLE3 draft model makes it slower.

**GLM-5.2.** Realistic speed is 0.8–1.0 tok/s. `TOPK=4` reduces the expert routing and is
not the same model.

**NPU.** The same Gemma 4 E4B weights are about 5× slower on the NPU than on the iGPU. The
NPU is a second compute unit that runs while the iGPU is busy, not an accelerator.

## How the numbers were measured

| Code | Harness | Settings | Comparable with |
|---|---|---|---|
| **A** | Smoke test through Ollama and Lemonade, 2026-09-15 | six short German tasks, 400-token output cap, "tok/s warm", one run per model | other A rows |
| **B** | Candidate run, 2026-09-16 | same six tasks, 2000-token cap, thinking switched off | other B rows, roughly A |
| **C** | `llama-bench` | `-ngl 999 -p 512 -n 128` unless the configuration says otherwise, 2–3 repetitions | other C rows |
| **D** | `llama-server`, `vllm serve` or the running service | fixed prompts, median or mean; with speculative decoding where stated | same model only |
| **E** | colibri (`JustVugg/colibri`) | decode speed as reported by the engine | other E rows |

Caveats that apply to the whole list:

* **A and B are single runs.** They are good for orders of magnitude. Speed spot checks were
  reproducible (gpt-oss-120b 49.0 / 48.2 / 49.3 across three runs).
* **Speculative decoding (MTP, DSpark, EAGLE3) depends on the text.** Code and prose give
  different acceptance rates; the figure is the mean or median over the stated prompts.
* **Prompt speed depends on prompt length and micro-batch.** Compare it only within one model.
* **August HIP (ROCm) figures come from a build that computed wrong results** on gfx1151
  (perplexity 663 instead of 5.6). The corrected build of 2026-09-14 runs at the same speed,
  so the figures stand as speed measurements and nothing more.
* **Nothing else may run during a measurement.** A parallel image generation halved Gemma's
  speed (56.8 → 24.7 tok/s) and the number looked plausible.
* **Software stack matters more than flags.** The same model went from 11.9 to 18.3 tok/s by
  changing the llama.cpp build; all flag and system tuning together brought under 3 %.
* **The list says nothing about quality.** About half the models in the smoke test scored
  6/6; the task results are in the source repositories.

## Adding a measurement

`models.csv` is the only place where numbers are entered. The tables in this README and
`index.html` are generated from it:

```bash
python3 build.py        # rewrites README.md and index.html
```

| Column | Meaning |
|---|---|
| `gen_tok_s`, `prompt_tok_s` | numbers, used for sorting; leave `gen_tok_s` empty for a model that produced no number |
| `gen_text`, `prompt_text` | optional display text where the measurement is a range, for example `30–36` |
| `how` | harness code A–E from the table above |
| `best` | `1` for the row that represents the model in the main list, exactly one per model |

Edit `README.template.md` for the prose and `template.html` for the page, not the generated
files.

## Sources

| Repository | What it holds |
|---|---|
| [strix-halo-deepseek-v4](https://github.com/huppiflupp/strix-halo-deepseek-v4) | DeepSeek-V4-Flash protocol, `BENCHMARKS.md`, `GPT-OSS-120B.md`, HIP against Vulkan |
| [strix-halo-npu-linux](https://github.com/huppiflupp/strix-halo-npu-linux) | `MODELS.md`: the 19-model smoke test, NPU against iGPU |
| [colibri fork](https://github.com/huppiflupp/colibri), branch `decode-gpu` | Qwen3.6 GPU decode in colibri |
| ai395-setup (private) | candidate run, colibri and Qwen3.8 measurements |
| strix-halo-kernel-lab (private) | lab book, the gains of the lab builds, the first GLM-5.3-Flash load attempt |

Last consolidated: {{BUILT}}.
