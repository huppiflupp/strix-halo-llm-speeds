# One coding-agent task, five models, two machines (2026-11-04)

The speed list says nothing about whether a model can finish real work. This is one small
agent task given to local models through `opencode run` (non-interactive), measured the same
day. **Every row is a single run**, so it is a picture, not a ranking.

## The task

Taken from a private PCB-autorouter project. The agent starts in a fresh git worktree and gets
the same German prompt every time:

1. Read the project notes and two documents.
2. Write `bench/testplatinen/gen_phasenschieber.py`: a script that builds a small **two-layer
   SMD board** (an RC phase shifter) with KiCad's `pcbnew` Python API and exports it as a
   **Specctra DSN**. KiCad 10.0.8 runs as a Flatpak (`flatpak run --command=python3
   org.kicad.KiCad script.py`).
3. Run it and show that the DSN contains nets, components and layers.
4. Write a short report with the exact commands.

Rules in the prompt: write only below `bench/testplatinen/`, do not touch `src/`, do not
switch branches or push, and give up after three failed attempts at the same step.

**The prompts were not identical.** The first Qwen3.8-27B session did not say where scratch
files may go, and its run ended when it tried to read a file in `/tmp`: `opencode` rejects
paths outside the project when it runs without a terminal. For its continuation, and from the
start for every other row below, the prompt added "put scratch files below the project, never
in `/tmp`". The Qwen3.8-27B prompt also named a few unfinished files of an earlier attempt
that existed in its directory; the other directories had none, so that sentence was left out.

Judged by me afterwards, not by the model: DSN counted component placements, nets and pins
per net, and the generator was run again to see whether the same DSN came out.

## Results

| Model | Engine, machine | Wall time | Steps | Outcome |
|---|---|---|---:|---|
| **Qwen3.8 Flash-Next** UD-Q4_K_XL, MTP, temperature 0, thinking on | Gufo 0.22.0, Strix Halo | **10 min 14 s** | 33 | **Complete.** DSN with 6 placements (2 connectors, 2 resistors, 2 capacitors, real KiCad footprints), 4 nets with 2 / 3 / 3 / 4 pins that match the circuit, 2 copper layers, 20 × 14 mm outline; report written; running the generator again gave an identical DSN. |
| Qwen3.8-27B UD-Q4_K_XL, DFlash2 | Gufo 0.20.0, Strix Halo | about 20 min to a usable DSN, stopped by me after about 1 h 55 min | 14 + 47 (two sessions) | Usable DSN (5 components, 4 nets, 20 × 15 mm), built by creating the pads from code. No report. The first session ended on the `/tmp` rule above. |
| gpt-oss-120b MXFP4 | llama.cpp Vulkan, Strix Halo | 4 min 50 s | 36 | **Empty DSN**: 0 placements, 0 nets, a dummy ±1 mm outline. The Flatpak could not find the footprint libraries, and it stopped there. The report says so honestly; the chat summary sounds more successful. Also wrote `test.kicad_*` into the project root, against the rules. |
| Mistral Small 4 119B UD-Q4_K_M | llama.cpp Vulkan, Strix Halo | about 20 min to step 33, then no progress; aborted after 33 min in total | 33 | A generator script, no output. After step 33 every request returned HTTP 500: the model's Jinja chat template raises *"After the optional system message, conversation roles must alternate user and assistant roles"* when the client sends two user messages in a row, which `opencode` does after compacting its context. A client or template problem, not a verdict on the model. |
| Qwen3.6-35B-A3B UD-IQ3_XXS, MTP, temperature 0 | llama.cpp CUDA, RTX 5080 (32k context) | 40 s | 6 | A request of 44,374 tokens exceeded the 32,768-token window of the server. |
| same, 64k context | llama.cpp CUDA, RTX 5080 | 2 min 39 s | 61 | No script. Explored the `pcbnew` API, then ended with a status summary (which names KiCad 7.0.x, the Flatpak is 10.0.8). |
| same, 64k context, second run | llama.cpp CUDA, RTX 5080 | 2 min 43 s | 36 | No script. Ended with *"Ready to write the script. Want me to proceed?"*. |

## What it shows

* **Only the largest model finished unaided**, and it was neither the fastest at generating
  nor the quickest overall: Flash-Next decodes at 32–54 tok/s here, gpt-oss at 52–54 (rows in
  `models.csv`; I did not time it inside this run), the 5080 runs at 170–260 (`other-machines/`). It needed few steps (33) and left six small probe scripts
  (`tmp/probe_api*.py`) from before the generator; I did not read them, so how it found the
  right API calls is not documented here.
* **Speed and finishing are different things.** gpt-oss was the fastest to "finish" and
  produced nothing usable; the Qwen3.6 runs on the 5080 took under three minutes each and
  stopped before writing the script.
* **The local Qwen3.6 stops to ask.** In non-interactive mode a closing question or status
  report ends the run. With a 64k window the context was not the cause the second time (it
  sat at 45–47k tokens). A sentence in the prompt such as "do not ask, do not stop before the
  DSN exists" is the first thing to try, and was **not** tried here, to keep the prompt equal.
* **Chat templates matter for agents.** A strict role-alternation check in the template
  (Mistral Small 4, Devstral Small 2) makes `opencode` fail after the first context
  compaction. Starting `llama-server` with a relaxed `--chat-template-file` is the fix; not
  applied here.
* **Temperature 0 was only set for Flash-Next and the 5080 runs.** The other runs used
  `opencode`'s default sampling for the model, so the comparison is not controlled. For Gufo,
  temperature 0 raised code generation from 38 to 53 tok/s (see `models.csv`).

## Not run

* **Devstral Small 2 24B** (Q4_K_M) on the 16 GB card: 56 tok/s at 32k context, but the task
  needs about 45k, the KV cache then no longer fits next to the weights, and its chat template
  has the same strict role check as Mistral Small 4. Deleted afterwards.
