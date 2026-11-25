#!/usr/bin/env python3
"""llama-server harness for the x9 runs of 2026-11-25: prompt speed (~4k tokens, median of 3), generation
(3 texts of 500 tokens), 20 first-token probes and the greedy texts for comparing builds.

x9-moecache-bench.py LABEL BINDIR [server arguments ...]   (model: environment variable M)
"""
import json, os, subprocess, sys, time, urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
M = os.environ.get("M", "/data/models/Qwen3.6-35B-A3B-mix-iq3gpu-q4cpu12-trunkIQ4XS.gguf")
PORT = 18090
label, bindir, extra = sys.argv[1], sys.argv[2], sys.argv[3:]

GEN = [
    "Write a long, detailed essay about how heat pumps work and where they make sense.",
    "Schreibe eine ausführliche Geschichte über eine Leuchtturmwärterin, die eine Flaschenpost findet.",
    "Write a Python module implementing an LRU cache, a binary heap and Dijkstra's algorithm, with docstrings and tests.",
]
PROBEN = [
    "The capital of Australia is", "Die Hauptstadt von Österreich ist", "def fibonacci(n):\n    if n < 2:\n        return",
    "Water boils at a temperature of", "Der Zweite Weltkrieg endete im Jahr", "The first element of the periodic table is",
    "SELECT name FROM users WHERE", "Once upon a time, there was a", "17 * 23 =", "The opposite of hot is",
    "import numpy as", "Mitochondria are often called the", "Im Winter ist es in Deutschland meist",
    "The author of Romeo and Juliet is", "To be or not to be, that is the", "git commit -m",
    "La capitale de la France est", "The speed of light is approximately", "#include <", "Photosynthesis converts light energy into",
]


def post(pfad, daten):
    r = urllib.request.Request(f"http://127.0.0.1:{PORT}{pfad}", json.dumps(daten).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=900) as a:
        return json.load(a)


def chat(text, n):
    return post("/v1/chat/completions", {"messages": [{"role": "user", "content": text}], "max_tokens": n,
                                          "temperature": 0, "seed": 1, "cache_prompt": False})


log = open(f"{HIER}/{label}.log", "w")
srv = subprocess.Popen([f"{bindir}/llama-server", "-m", M, "--jinja", "--host", "127.0.0.1", "--port", str(PORT),
                        "--alias", "mess", "--no-webui", *extra], stdout=log, stderr=subprocess.STDOUT)
erg = {"label": label, "bin": bindir, "args": extra, "modell": M}
try:
    for _ in range(300):
        if srv.poll() is not None:
            raise SystemExit(f"{label}: server exited while loading, see {HIER}/{label}.log")
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2)
            break
        except Exception:
            time.sleep(1)
    else:
        raise SystemExit(f"{label}: not ready")
    chat("Explain in detail how a combustion engine works.", 300)  # warm-up with a text of its own
    gpu = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True)
    erg["vram_mib"] = int(gpu.stdout.split()[0])
    lang = open("/data/tmp_runs/hwbench/p4k.txt").read()
    erg["prompt"] = []
    for i in range(3):
        t = post("/completion", {"prompt": f"[{i}] " + lang, "n_predict": 1, "temperature": 0, "cache_prompt": False})["timings"]
        erg["prompt"].append((t["prompt_n"], round(t["prompt_per_second"], 1)))
    erg["gen"], erg["texte"], erg["draft"] = [], [], []
    for g in GEN:
        a = chat(g, 500)
        t = a["timings"]
        erg["gen"].append((t["predicted_n"], round(t["predicted_per_second"], 2)))
        erg["draft"].append((t.get("draft_n", 0), t.get("draft_n_accepted", 0)))
        m = a["choices"][0]["message"]
        erg["texte"].append((m.get("reasoning_content") or "") + (m.get("content") or ""))
    erg["proben"] = [post("/completion", {"prompt": p, "n_predict": 1, "temperature": 0, "n_probs": 10, "cache_prompt": False})
                     .get("completion_probabilities") for p in PROBEN]
finally:
    srv.terminate()
    srv.wait(60)
json.dump(erg, open(f"{HIER}/{label}.json", "w"), ensure_ascii=False)
# overall speed = all tokens / all time
tok = sum(n for n, _ in erg["gen"]); sek = sum(n / v for n, v in erg["gen"])
dn = sum(d for d, _ in erg["draft"]); da = sum(a for _, a in erg["draft"])
pp = sorted(v for _, v in erg["prompt"])[1]
print(f"{label:18s} generation {tok / sek:6.1f} tok/s ({' / '.join(str(v) for _, v in erg['gen'])}) | prompt {erg['prompt'][0][0]} Tok {pp:7.1f} tok/s"
      f" | VRAM {erg['vram_mib']} MiB" + (f" | draft accepted {100 * da / dn:.0f} %" if dn else ""), flush=True)
