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
| same, 64k, prompt adds "ask no questions, do not stop before the DSN exists" | llama.cpp CUDA, RTX 5080 | 3 min 34 s | 56 | No script. The project note copied into the directory named the main repository, the model listed it (it holds another model's output) and tried to read a file there; `opencode` rejected the path and the run ended. Not a question this time, and an error in my setup, not in the model. |
| same, third run after fixing the note and forbidding the main repository | llama.cpp CUDA, RTX 5080 | 1 min 2 s | 11 | No script. One context compaction at step 9, then a closing *"Want me to probe the MODULE/PAD constructors now … or is there something else you'd like to adjust first?"*, although the prompt said not to ask. |
| same, 64k, **with a wrapper** that answers *"Yes, continue. Ask no questions."* each time the model stops | llama.cpp CUDA, RTX 5080 | 7 min 55 s (three `opencode` calls: it stopped after 40 steps, then twice more) | 40 + 76 + 19 | **Produced all three files**: script, DSN, report; running the script again gives an identical DSN; nothing written outside `bench/testplatinen/`. But it is not the requested circuit: 13 placements (a 32-pad QFN with every pad on GND, 6 resistors, 2 capacitors, 4 pin headers), 3 nets, 20 × 15 mm outline; components are built from code and appear as `::1`…`::12` in the DSN, pad numbers read `@1`…; the report says two tracks of 0.04 mm while the script's own statistics print three. Usable as routing input, not as a phase shifter. |

## What it shows

* **Only the largest model finished unaided**, and it was neither the fastest at generating
  nor the quickest overall: Flash-Next decodes at 32–54 tok/s here, gpt-oss at 52–54 (rows in
  `models.csv`; I did not time it inside this run), the 5080 runs at 170–260 (`other-machines/`). It needed few steps (33) and left six small probe scripts
  (`tmp/probe_api*.py`) from before the generator; I did not read them, so how it found the
  right API calls is not documented here.
* **Speed and finishing are different things.** gpt-oss was the fastest to "finish" and
  produced nothing usable; the Qwen3.6 runs on the 5080 took under three minutes each and
  stopped before writing the script.
* **The local Qwen3.6 ends its run with a question, even when told not to.** In
  non-interactive mode a closing question or status report ends the run. Four runs ended that
  way or on a blocked read; the one that had the instruction "ask no questions" in its prompt
  still ended with a question after a context compaction. `opencode`'s own text after a
  compaction says "Continue if you have next steps, **or stop and ask for clarification** if
  you are unsure how to proceed", which invites exactly that. The context fills to 45–57k of
  64k, mostly with long `dir()` listings of the `pcbnew` API (the three documents the prompt
  names are only about 19k tokens). A compaction does not always end the run: one run went on
  for 29 more steps. A sentence in the prompt was not enough for this model. A wrapper that
  simply answers "yes, continue" got the same model to write all three files in under eight
  minutes, so the stopping is more a harness problem than a lack of ability, but the result
  is mixed (last row): complete files, wrong circuit, a report that does not fully match.
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
