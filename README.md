# LLM speeds on AMD Strix Halo — every model I measured

One list of all language models tried on one machine, with their generation speed in
tokens per second. Consolidated from five separate measurement logs (see [Sources](#sources)).

**Machine:** AMD Ryzen AI MAX+ 395, Radeon 8060S iGPU (gfx1151, RDNA 3.5) + XDNA2 NPU,
128 GB LPDDR5X-8000 unified memory, Nobara Linux 44, kernel 7.1–7.2.
**Period:** August – 28 September 2026.

> **Read this first.** The numbers come from different harnesses and are **not** a ranking
> to the decimal. The *How* column says which one produced a figure; the legend is
> [below the table](#how-the-numbers-were-measured). Looking for a specific model? Use
> the browser search — models that were tried but produced **no number** are in
> [their own table](#tried-but-no-number).

## The list

One row per model, with the **best generation speed measured** and the configuration that
produced it. All variants (other engines, quantisations, with and without speculative
decoding) are in [Variants per model](#variants-per-model). Runs on the iGPU unless the
engine column says NPU or CPU.

| # | Model | Architecture | Quant, file size | Engine | Generation tok/s | Prompt tok/s | How |
|---:|---|---|---|---|---:|---:|---|
| 1 | qwen3:0.6b | 0.75B dense | 0.5 GB | Ollama | **236.6** | — | B |
| 2 | llama3.2:1b-instruct-q4_0 | 1B dense | Q4_0, 0.77 GB | Ollama | **202.3** | — | B |
| 3 | fableforge-ai/nexus-medical | small domain model | 3.1 GB | Ollama | **147.5** | — | B |
| 4 | fableforge-ai/nexus-science | small domain model | 3.1 GB | Ollama | **145.7** | — | B |
| 5 | llama3.2:1b | 1B dense | 1.3 GB | Ollama | **135.1** | — | B |
| 6 | qwen3:1.7b | 2B dense | 1.4 GB | Ollama | **128.5** | — | B |
| 7 | Qwen3.6-35B-A3B | 35B MoE, 3B active | UD-IQ4_XS, 17 GB | llama.cpp Vulkan + MTP | **≈ 97** | 1839 | D |
| 8 | Qwen3-30B-A3B-Instruct-2507 | 30B MoE, 3B active | IQ4_XS, 15.3 GiB | llama.cpp Vulkan | **94.3** | 2115 | D |
| 9 | llama3.2:3b | 3.2B dense | 2.0 GB | Ollama | **84.7** | — | B |
| 10 | gemma4:e2b | — | Q4_K_M, 7.2 GB | Ollama | **82.0** | — | A |
| 11 | granite4.2:3b | 3.7B dense | 2.3 GB | Ollama | **74.9** | — | B |
| 12 | qwen3-vl:30b | 30B | Q4_K_M, 19.6 GB | Ollama | **64.5** | — | A |
| 13 | Ornith-1.5-35B-A3B | 35B MoE, 3B active | Q4_K_M, 21.7 GB | Ollama | **60.0** | — | B |
| 14 | Gemma-4-E4B-it | 4B active | Q4_K_M, 5.6 GB | Lemonade (llama.cpp Vulkan) | **56.8** | 62–235 | A |
| 15 | gpt-oss-120b | 117B MoE, 4 of 128 experts | MXFP4, 63.4 GB | llama.cpp Vulkan | **53.7** | 1464 | C |
| 16 | qwen3-coder-next | 80B MoE, 3B active | 52 GB | Ollama | **51.1** | — | B |
| 17 | nex-agi Nex-N2.5-mini | 35B MoE | Q4_K_M, 21.3 GB | Ollama | **50.8** | — | B |
| 18 | qwen3-next | 80B MoE, 3B active | 50 GB | Ollama | **45.1** | — | B |
| 19 | Qwen3.8-Flash-Next | 125B MoE, 6B active | UD-IQ4_XS, 93.7 GB | llama.cpp Vulkan (PR #28243) + MTP | **41.3** | — | D |
| 20 | DeepSeek-Qwen3-8B | 8B | Q4_1, 4.9 GB | Lemonade (llama.cpp Vulkan) | **40.6** | — | A |
| 21 | granite4.2 | 8B dense | 5.3 GB | Ollama | **40.4** | — | B |
| 22 | qwen3-vl:8b-instruct | 8B | Q4_K_M, 6.1 GB | Ollama | **37.3** | — | A |
| 23 | Qwen3.8-27B | 27B dense | Q4_K_M, 16.8 GB | llama.cpp Vulkan + MTP | **30–36** | 479 | D |
| 24 | qwen3.5:9b | 9B | Q4_K_M, 6.6 GB | Ollama | **31.5** | — | A |
| 25 | DeepSeek-V4-Flash-0731 | 284B MoE, 13B active | UD-IQ2_XXS, 85 GiB | llama.cpp fork, Vulkan + DSpark draft n=3 | **28.9** | 262 | D |
| 26 | Qwen3.8-27B Heretic (DavidAU finetune) | 27B dense | MTP-Q4_K_M, 18.5 GB | llama.cpp fork, Vulkan + MTP | **28.3** | 242 | D |
| 27 | gemma4:12b | 12B dense | Q4_K_M, 7.4 GB | llama.cpp Vulkan | **25.6** | 741 | C |
| 28 | NousResearch Hermes-4-14B | 14B dense | Q4_K_M, 9.0 GB | llama.cpp Vulkan | **23.5** | 695 | C |
| 29 | gemma4:26b-a4b-it-bf16 | 26B MoE, 4B active | F16, 51.7 GB | Ollama | **21.1** | — | A |
| 30 | gpt-oss-20b-FLM | 20B MoE, ~3.6B active | 14 GB | FastFlowLM on the **NPU** | **19.3** | 22–26 | A |
| 31 | phi4-reasoning:plus | 14B dense | 11 GB | Ollama | **18.1** | — | B |
| 32 | Qwen3.5-122B-A10B | 122B MoE, 10B active | MXFP4, 65 GB | llama.cpp Vulkan | **14.3** | — | B |
| 33 | muse-glimmer | 30B dense | Q4_K_M, 16.7 GB | llama.cpp Vulkan | **12.4** | 357 | C |
| 34 | gemma4:31b | 31B dense | Q4_K_M, 19.9 GB | Ollama | **9.7** | — | A |
| 35 | llama3.1:70b | 70B dense | 43 GB | Ollama | **5.6** | — | B |
| 36 | nemotron | MoE | 43 GB | Ollama | **5.3** | — | B |
| 37 | DeepSeek-V4 REAP (pruned) | MoE | 79 GiB | colibri | **2.19** | — | E |
| 38 | GLM-5.2 | 744B MoE | int4, 400 GiB | colibri, experts streamed from NVMe | **1.29** (0.26–1.71) | — | E |

Generation speed is memory-bound on this machine: what counts is how many bytes are read
per token, not the parameter count in the name. Every model above 40 tok/s is either small
(8B or less) or a mixture-of-experts with few active parameters; dense models from 27B upwards stay below
15 tok/s unless speculative decoding (MTP, DSpark) helps.

## Tried, but no number

| Model | Size | What happened |
|---|---|---|
| **GLM-5.3-Flash** (`unsloth/GLM-5.3-Flash-GGUF`, UD-IQ1_S) | 93 GB | Downloaded 2026-09-21. The one `llama-bench` attempt **failed at load**: the architecture `glm5next` existed only in open llama.cpp PRs (#27752, #27754, #27773) at the time. **Never measured.** |
| Ling-2.6-flash (IQ4_NL) | 65 GB, 104B MoE | Ollama answered every request with HTTP 500; its architecture `bailing_hybrid` is not supported by the bundled llama.cpp. Never loaded. |
| qwen3.8:27b-mxfp8 | 32 GB | Ollama: "this model requires MLX support" — Apple only. |
| Qwen3-VL-235B-A22B-Instruct | ~133 GB at Q4_K_M | Larger than the machine's memory. Not downloaded. |
| MiniMax-M2-AWQ-4bit | ~115 GB, 230B MoE | Too large, and AWQ needs vLLM, which does not run usefully on gfx1151. Not downloaded. |
| Kimi K2 | ~600 GB at 4 bit, 1T MoE | Five times the machine's memory. Not downloaded. |

Figures for other models that appear in my notes (GLM-4.5-Air at 25.0 tok/s,
Qwen3-235B-A22B at 17.2 tok/s) are **third-party measurements** quoted for comparison. They
were not measured here and are therefore not in the list.

## Variants per model

### Qwen3.6-35B-A3B

| Engine | Configuration | Generation tok/s | Prompt tok/s | Date |
|---|---|---:|---:|---|
| llama.cpp Vulkan (lab build) | UD-IQ4_XS + MTP, family chat service | ≈ 97 | 1839 (2048 tokens) | 09-22 |
| llama.cpp Vulkan (strix fork) | UD-IQ4_XS + MTP | 89.8 | 1610 (2048 tokens, 09-21) | 09-18 |
| llama.cpp Vulkan | UD-IQ4_XS + MTP, draft length 0 / 1 / 2 / 3 / 4 | 61.7 / 77.8 / 81.9 / 80.2 / 78.6 | — | 09-18 |
| colibri fork, own GPU decode | int4 trunk, with MTP | 77.3 | — | 09-28 |
| colibri fork, own GPU decode | int4 trunk | 66.9 | — | 09-28 |
| llama.cpp Vulkan | UD-IQ4_XS, no MTP (`llama-bench` tg256) | 62.7 | 1461 (pp512) | 09-26 |
| Ollama | Q4_K_M, 23.9 GB (`qwen3.6:latest`) | 54.5 | — | 09-15 |
| Ollama | Q4_K_M, 23.9 GB (`qwen3.6-en`) | 54.0 | — | 09-15 |
| colibri, Vulkan expert tier (PR #1338) | int4, all experts on the GPU | 31.6 | — | 09-26 |
| colibri, CPU only | int4, 22 GB | 19.7 | — | 09-14 / 09-26 |
| FastFlowLM on the NPU | `qwen3.6-moe-35b-a3b-FLM` | 13.4 (first run), 10.2 (smoke test) | 6.9 | 09-15 |
| colibri, HIP expert tier | int4 | 12.35 | — | 09-14 |

### Qwen3.8-27B (dense)

| Engine | Configuration | Generation tok/s | Prompt tok/s | Date |
|---|---|---:|---:|---|
| llama.cpp Vulkan (lab build) | Q4_K_M + MTP, coder service under agent load | 30–36 | 479 (pp512), 357 (real 21.6 k request) | 09-22 |
| llama.cpp 10565 (strix fork) | Q4_K_M + MTP, 400 tokens | 27.9 | 244 | 09-16 |
| Ollama | `qwen3.8:27b` with MTP, candidate run | 25.3 | — | 09-16 |
| llama.cpp 10707 (strix fork 0.7.6) | Q4_K_M + MTP | 20.3 | 341 | 09-16 |
| Ollama 0.34.1 | Q4_K_M + MTP, 400 tokens | 19.5 | 288 | 09-16 |
| Ollama | `qwen3.8:latest`, 17.7 GB, smoke test | 18.2 | — | 09-15 |
| llama.cpp Vulkan | UD-IQ4_XS, no MTP | 14.13 | 391 | 09-28 |
| llama.cpp Vulkan | Q4_K_M, no MTP | 12.36 | 389 | 09-28 |
| llama.cpp Vulkan / HIP | Q4_K_M, `llama-bench` (August build) | 12.09 / 11.19 | 329 / 321 | 08 |
| Ollama | `qwen3.8:27b-q8_0`, 29 GB | 7.3 | — | 09-16 |
| colibri, CPU | int4 / int8 | 6.93 / 4.28 | — | 09-28 |
| llama.cpp, CPU (`-ngl 0 -t 16`) | Q4_K_M | 5.63 | — | 09-28 |

The Heretic finetune (row 26) measured 28.3 / 18.1 tok/s with MTP on llama.cpp 10565 / 10707,
18.6 on Ollama with MTP, and 10.9–11.2 without MTP.

### Qwen3.8-Flash-Next

| Engine | Configuration | Generation tok/s | Date |
|---|---|---:|---|
| llama.cpp Vulkan, PR #28243 | UD-IQ4_XS + MTP, draft length 2 | 41.3 | 09-28 |
| llama.cpp Vulkan, PR #28243 | UD-IQ4_XS + MTP, draft length 3 | 40.6 | 09-28 |
| llama.cpp Vulkan, PR #28243 | UD-IQ4_XS, no MTP | 26.85 | 09-28 |
| llama.cpp 10707 (strix fork 0.7.6) | UD-IQ4_XS, no MTP | 26.5 | 09-16 |
| colibri, CPU | FP8 checkpoint (185.6 GB), expert cache 256 / 128 per layer | 6.9–7.5 / 5.8–6.8 | 09-28 |

Occupies 90–94 GiB when loaded. It only runs alone.

### DeepSeek-V4-Flash-0731

| Engine | Configuration | Generation tok/s | Prompt tok/s | Date |
|---|---|---:|---:|---|
| llama.cpp fork (source build), Vulkan | UD-IQ2_XXS + DSpark draft n=3 | 28.91 | 261.7 | 09-20 |
| Lucebox `dflash_server`, HIP | their ROCMFP2 file (102.3 GB) + DSpark, **4** experts | 28.2 (peak 31.3) | ~403 | 09-20 |
| llama.cpp fork, Vulkan | UD-IQ2_XXS + DSpark n=2 | 27.46 | 253.5 | 09-20 |
| Lucebox `dflash_server`, HIP | their file + DSpark, 6 experts | 26.5 | ~367 | 09-20 |
| llama.cpp fork v0.6.4, Vulkan | UD-IQ3_XXS + DSpark n=3, `llama-cli` | 23.9–29.0 | — | 08 |
| llama.cpp fork, Vulkan | UD-IQ3_XXS + DSpark n=2 | 23.01 | 201.5 | 09-20 |
| Lucebox `dflash_server`, HIP | their file, no draft, 4 experts | 22.8 | ~411 | 09-20 |
| llama.cpp fork, Vulkan | UD-IQ2_XXS, no draft | 18.91 | 225.7 | 09-20 |
| llama.cpp fork v0.6.4, Vulkan | UD-IQ3_XXS, no draft, governor `performance` | 18.85 | 207.5 | 08 |
| llama.cpp fork, Vulkan | UD-IQ3_XXS, no draft | 18.40 | 206.5 | 09-20 |
| llama.cpp mainline b10488, Vulkan | UD-IQ3_XXS, no draft | 11.94 | 127.4 | 08 |
| llama.cpp mainline, Vulkan | UD-IQ3_XXS + DSpark draft | 7.7 | — | 08 |

Perplexity (wikitext): UD-IQ3_XXS 4.57, UD-IQ2_XXS 5.21. The smoke test of 09-15 recorded
24.6 tok/s with the draft model and 17.9 without. IQ2 plus draft model occupied 108 of 124 GB
and hung the amdgpu driver once; it is a measurement setup, not an operating mode.

### gpt-oss-120b (MXFP4)

| Engine | Configuration | Generation tok/s | Prompt tok/s | Date |
|---|---|---:|---:|---|
| llama.cpp master + PR #27952, Vulkan | `llama-bench` | 53.70 | 1151.9 (pp512), 1463.9 (pp2048) | 09-21 |
| llama.cpp lab build, Vulkan | service setting | 53.6 | 1459 (2048 tokens) | 09-22 |
| llama.cpp fork, Vulkan | `-fa 1 -b 2048 -ub 512` | 53.5 | 834.9 (pp512) | 09-20 |
| Lemonade (llama.cpp Vulkan) | smoke test | 49.3 | — | 09-15 |
| llama.cpp upstream, HIP (ROCm 7.1.1) | `llama-bench` | 47.6 | 939.7 (pp512), 1230.2 (pp2048) | 09-20 |
| llama.cpp fork, Vulkan | with EAGLE3 draft, length 1 / 2 / 3 / 4 | 43.7 / 38.9 / 32.4 / 27.7 | — | 09-20 |
| llama.cpp fork, Vulkan | at context depth 8192 / 32768 / ~87 000 | 49.1 / 40.6 / 29.1 | 748 / — / 622 | 09-20, 09-21 |

Generation sits at 85 % of the memory-bandwidth ceiling (62.9 tok/s). The EAGLE3 draft model
makes it slower.

### Qwen3-30B-A3B-Instruct-2507 (IQ4_XS)

| Engine | Configuration | Generation tok/s | Prompt tok/s | Date |
|---|---|---:|---:|---|
| llama.cpp lab build, Vulkan | service | 94.3 | 2115 (2048 tokens) | 09-22 |
| llama.cpp strix fork, Vulkan | service | 88.8 | 1830 (2048 tokens) | 09-21 |
| llama.cpp fork v0.6.4, Vulkan | governor `performance`, GPU `high` | 87.57 | 1550 (pp512) | 08 |
| llama.cpp mainline, Vulkan | `-fa 1 -mmp 0 -b 2048 -ub 512` | 85.53 | 1378 (pp512) | 08 |
| llama.cpp mainline, HIP | same flags | 72.71 | 1296 (pp512) | 08 |

### Dense models, HIP against Vulkan (`llama-bench`, August build)

| Model | File GB | Vulkan tg128 | HIP tg128 | Vulkan pp512 | HIP pp512 | Ollama (smoke test) |
|---|---:|---:|---:|---:|---:|---:|
| gemma4:12b (Q4_K_M) | 7.37 | 25.58 | 23.75 | 741.0 | 816.0 | 23.3 |
| Hermes-4-14B (Q4_K_M) | 9.00 | 23.45 | 21.51 | 694.5 | 696.6 | 22.5 |
| muse-glimmer 30B (Q4_K_M) | 16.74 | 12.40 | 11.38 | 356.6 | 367.0 | 11.6 |
| Qwen3.8-27B (Q4_K_M) | 16.80 | 12.09 | 11.19 | 329.4 | 320.6 | 18.2 |

Vulkan wins generation by 8–9 % on every dense model.

### NPU (FastFlowLM) against iGPU

| Model | Runs on | Generation tok/s | Prompt tok/s |
|---|---|---:|---:|
| Gemma-4-E4B-it (GGUF) | iGPU, llama.cpp Vulkan | 53.6–56.8 | 62–235 |
| gemma4-it-e4b-FLM | NPU | 10.1–12.4 | 15.9–26.9 |
| gpt-oss-20b-FLM | NPU | 16.2–19.3 | 21.8–26.3 |
| qwen3.6-moe-35b-a3b-FLM | NPU | 10.2–13.4 | 6.9 |

The same Gemma 4 E4B weights are about 5× slower on the NPU. The NPU is a second compute unit
that runs while the iGPU is busy, not an accelerator.

### GLM-5.2 (int4, 400 GiB) in colibri

| Date | Configuration | Generation tok/s |
|---|---|---:|
| 09-14 | first measurement, Vulkan tier with 320 experts | 0.26–0.33 |
| 09-15 | tuned, 4500 experts in the Vulkan tier | 1.29 |
| 09-18 | routing sweep: baseline / `TOPK=4` | 1.00 / 1.71 |

Realistic: 0.8–1.0 tok/s. `TOPK=4` reduces the expert routing and is not the same model.

## How the numbers were measured

| Code | Harness | Settings | Comparable with |
|---|---|---|---|
| **A** | Smoke test through Ollama and Lemonade, 2026-09-15 | six short German tasks, 400-token output cap, "tok/s warm", one run per model | other A rows |
| **B** | Candidate run, 2026-09-16 | same six tasks, 2000-token cap, thinking switched off | other B rows, roughly A |
| **C** | `llama-bench` | `-ngl 999 -p 512 -n 128`, 2–3 repetitions; prompt = pp512 unless stated | other C rows |
| **D** | `llama-server` or the running service | fixed prompts, median or mean; with speculative decoding where stated | same model only |
| **E** | colibri (`JustVugg/colibri`) | decode speed as reported by the engine | other E rows |

Caveats that apply to the whole list:

* **A and B are single runs.** They are good for orders of magnitude. Speed spot checks were
  reproducible (gpt-oss-120b 49.0 / 48.2 / 49.3 across three runs).
* **Speculative decoding (MTP, DSpark) depends on the text.** Code and prose give different
  acceptance rates; the figure is the mean or median over the stated prompts.
* **Nothing else may run during a measurement.** A parallel image generation halved Gemma's
  speed (56.8 → 24.7 tok/s) and the number looked plausible.
* **Software stack matters more than flags.** The same model went from 11.9 to 18.3 tok/s by
  changing the llama.cpp build; all flag and system tuning together brought under 3 %.
* **The list says nothing about quality.** About half the models in the smoke test scored
  6/6; the task results are in the source repositories.

## Sources

| Repository | What it holds |
|---|---|
| [strix-halo-deepseek-v4](https://github.com/huppiflupp/strix-halo-deepseek-v4) | DeepSeek-V4-Flash protocol, `BENCHMARKS.md`, `GPT-OSS-120B.md`, HIP against Vulkan |
| [strix-halo-npu-linux](https://github.com/huppiflupp/strix-halo-npu-linux) | `MODELS.md`: the 19-model smoke test, NPU against iGPU |
| [colibri fork](https://github.com/huppiflupp/colibri), branch `decode-gpu` | Qwen3.6 GPU decode in colibri |
| ai395-setup (private) | `bench/MODELLE.md`, candidate run, colibri and Qwen3.8 measurements |
| strix-halo-kernel-lab (private) | lab book, `docs/GAINS.md`, the GLM-5.3-Flash load failure (E039) |

Last consolidated: 2026-09-29.
