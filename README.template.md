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
Quality check on 2026-10-02 against gpt-oss-120b, same coding task as the MiMo duel
(`bench/code-duell`: an expression evaluator with Python semantics, no `eval`/`ast`; 47 fixed
cases, 500 random expressions; 3 attempts each, at most 16,000 tokens). With
`reasoning_effort: high` neither model finished: all six attempts used the whole budget for
thinking and returned no code. With Mistral at `none` (its only other setting; temperature 0.3)
against gpt-oss at `medium`: Mistral 0 of 3 usable (one stopped mid-function, one had a syntax
error, one passed 30/47 fixed and 85/500 random cases); gpt-oss 3 of 3 working in 1–2 minutes
(46–47/47, 449–500/500). Both early stops were reported as a normal end, which might also
point at an overflow from the patch; not investigated. **Decision: model deleted on
2026-10-02.** It is slower than gpt-oss-120b (35 against ~50 tok/s), takes 92 instead of
63 GiB, needs a patched llama.cpp and did clearly worse on the coding task.

**Qwen3.5-122B-A10B (2026-10-02).** Pulled again (unsloth MTP GGUF, UD-Q4_K_XL, 78.6 GB)
because DGX Spark users call it the best quality model for one Spark, especially for tool
calls. Perplexity 3.64; 22.1 tok/s without MTP, 31 with MTP (22.7 poem, 33.2 explanation, 37.0
code), 523 tok/s prompt; 73–76 GiB in use, runs only alone. Coding task (`bench/code-duell`,
thinking on, 16,000 tokens): 1 of 3 near-perfect (46/47, 499/500), one 34/47 and 280/500, one
out of budget, 7–8 minutes each; gpt-oss-120b at `medium` solved 3 of 3 in 1–2 minutes.
Tool-call test (`bench/toolcall`: 12 cases with mock tools, two rounds, everything else
stopped first): Qwen3.5-122B, gpt-oss-120b and Qwen3.6-35B-A3B all 22/24. Both Qwen models
sent an e-mail to "Thomas" without an address instead of asking; gpt-oss asked, but fetched
only one of two cities in a single step. Tool-call correctness was perfect for all three
otherwise, so the test does not separate them. **Decision: model deleted on 2026-10-02.** No
advantage over gpt-oss-120b, which is faster (~50 against 31 tok/s) and smaller (63 against
76 GiB).

**Service builds against upstream (2026-10-02).** The four service models, each with its frozen
lab build and switches against upstream 254b17730 of the same day (llama-bench, `-fa 1`, the
service's `-ub`, everything else stopped):

| model | prompt 2048, lab → upstream | generation, lab → upstream | perplexity, lab / upstream |
|---|---|---|---|
| Qwen3.6-35B-A3B (hybrid) | 1841 → 1324 (−28 %) | 63.0 → 63.1 | 6.3064 / 6.3064 |
| Qwen3.8-27B coder (hybrid2) | 450 → 335 (−26 %) | 12.3 → 12.3 | 6.2792 / 6.2810 |
| gpt-oss-120b (gptoss) | 1399 → 1407 | 53.7 → 53.8 | 1096 / 1112 |
| Qwen3-30B-A3B (gptoss) | 1642 → 1262 (−23 %) | 94.9 → 93.4 | 6.6888 / 6.6770 |

With MTP on the server (three greedy prompts): Qwen3.6 53/93/103 tok/s (lab) against 58/88/97
(upstream), the coder 15/25/30 in both. Upstream has not caught up with the lab's prompt
kernels (the concat tiling of E040, the packed matmul); generation is the same. The services
stay on their frozen builds. gpt-oss-120b's perplexity on raw wikitext is about 1100 in both
builds, so it is not a build difference; why it is that high on plain text was not checked
(the model does solve the coding task, see the Mistral note).

**colibri Qwen3.6 with the tiled Vulkan GEMMs (2026-10-02).** colibri #1834 (tiled GEMM with
cooperative matrix) and #1837 (prefill projections per block of rows), measured end to end
with the `Kreuzzelg/qwen36-35b-a3b-colibri-i4-gs64` container, a 583-token prompt and all
experts in RAM, Performance mode (120 W). Vulkan prefill doubles, 22.9 → 48.5 tok/s, and so reaches the CPU's 48.9 but
not beyond it: the device GEMMs take only 0.73 s of the ~12 s, the rest is routed-expert work
on the CPU. Generation is 29.6 tok/s on the CPU and 20.4 with Vulkan, the same before and
after. For comparison, llama.cpp runs the same model at 1841 tok/s prompt and 63 tok/s
generation (97 with MTP). On the operation level the new kernel is 12.6x faster at M=256
(see the colibri discussion #1590).

**gpt-oss-120b.** Generation sits at 85 % of the memory-bandwidth ceiling (62.9 tok/s). The
EAGLE3 draft model makes it slower.

**GLM-5.2.** Realistic speed is 0.8–1.0 tok/s. `TOPK=4` reduces the expert routing and is
not the same model.

**NPU.** The same Gemma 4 E4B weights are about 5× slower on the NPU than on the iGPU. The
NPU is a second compute unit that runs while the iGPU is busy, not an accelerator.

## The same model on other machines

Not Strix Halo, and therefore **not in the list or in `models.csv`**: Qwen3.6-35B-A3B on the
two other machines that serve it under the same alias, measured on 2026-10-02 for comparison.
The question was whether an old workstation with an 11 GB card can take part as a third
backend. It can.

| Machine | Quant, file size | llama.cpp, configuration | Generation tok/s | Prompt tok/s |
|---|---|---|---:|---:|
| **245k**: Core Ultra 5 245K, RTX 5080 16 GB | UD-IQ3_XXS, 13.1 GB | 4fea119, CUDA, everything in VRAM, MTP | **275** | 4189 |
| Strix Halo (this list, other harness) | UD-IQ4_XS, 17 GB | lab build, Vulkan, MTP, `-ub 2048` | ≈ 97 (63 without MTP) | 1841 |
| **x9**: Xeon E5-2697 v2, 64 GB DDR3-1333, RTX 2080 Ti 11 GB | UD-IQ3_XXS, 13.1 GB | bed0a85, CUDA, `--fit on --fit-target 384`, MTP, `-ub 2048` (the service) | **46.8** | 1105 |
| x9 | UD-IQ3_XXS, 13.1 GB | same, `-ub 512` | 49.2 | 497 |
| x9 | UD-IQ3_XXS, 13.1 GB | `--fit on` (1024 MiB margin), MTP, `-ub 512` | 50.0 | 453 |
| x9 | UD-IQ3_XXS, 13.1 GB | `--fit on`, no MTP, `-ub 512` | 45.2 | 516 |
| x9 | UD-IQ3_XXS, 13.1 GB | `--fit on` (1024 MiB margin), MTP, `-ub 2048`, over the LAN | 39.5 | 1019 |
| x9 | UD-IQ3_XXS, 13.1 GB | `--fit-target 384`, MTP, `-ub 512`, 24 threads instead of 12 | 35.0 | 489 |
| x9 | Q4_K_M, 19 GB | `--fit on`, separate MTP head (`-md`), `-ub 512` | 48.4 | 234 |
| x9 | UD-IQ4_XS, 17 GB | `--fit on`, MTP, `-ub 512` | 39.8 | 304 |

Harness: `llama-server`, `/v1/chat/completions`, temperature 0, prompt cache off, 32,768-token
context, one warm-up request, then **one run each**: 500 new tokens for a coding prompt
(generation) and a 7,362-token prompt of C++ source (prompt speed). The Strix Halo row is
taken from the list above (2,048-token prompt) and was not measured again that day. Script and
raw results: [`other-machines/`](other-machines/).

What the x9 runs show:

* **The model does not fit into 11 GB, and it hardly matters.** `--fit` puts about 10 GB on
  the card (10.3 of 11 GB in use) and leaves the remaining expert weights in RAM.
  With 3B active parameters the CPU share stays small, even on a 2013 Xeon without AVX2 and
  with DDR3. The estimate before measuring was 8–15 tok/s.
* **`-ub 2048` doubles prompt speed** (497 → 1105 tok/s) and costs a few percent of generation.
  With the larger batch the default `--fit` margin of 1024 MiB pushes too much onto the CPU
  (39.5 tok/s); `--fit-target 384` restores it (46.5–46.8).
* **12 threads, not 24.** Hyper-threads make generation slower (35 against 49 tok/s).
* **MTP gains only about 10 %** here (45.2 → 50.0), against roughly 50 % on Strix Halo.
* **Larger quants mainly cost prompt speed**: more of the model sits in RAM, and prompt
  processing drops to 234–304 tok/s, while generation stays at 40–48 tok/s.

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
