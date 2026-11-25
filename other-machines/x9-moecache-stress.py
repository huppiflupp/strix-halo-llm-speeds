#!/usr/bin/env python3
"""Stress test: prompts up to near the end of the context, mixed requests, follow-ups that reuse the prompt cache.
Needs wiki.test.raw (wikitext-2) next to the script.

x9-moecache-stress.py LABEL BINDIR CTX [server arguments ...]   (seconds: environment variable DAUER)
"""
import json, os, subprocess, sys, threading, time, urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
M = os.environ.get("M", "/data/models/Qwen3.6-35B-A3B-mix-iq3gpu-q4cpu12-trunkIQ4XS.gguf")
PORT = 18090
label, bindir, ctx, extra = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4:]


def post(pfad, daten):
    r = urllib.request.Request(f"http://127.0.0.1:{PORT}{pfad}", json.dumps(daten).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=900) as a:
        return json.load(a)


spitze, ende = [0], threading.Event()


def vram():
    while not ende.is_set():
        a = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"], capture_output=True, text=True)
        spitze[0] = max(spitze[0], int(a.stdout.split()[0]))
        ende.wait(0.5)


log = open(f"{HIER}/{label}.log", "w")
srv = subprocess.Popen([f"{bindir}/llama-server", "-m", M, "-c", str(ctx), "--jinja", "--host", "127.0.0.1", "--port", str(PORT),
                        "--no-webui", *extra], stdout=log, stderr=subprocess.STDOUT)
try:
    for _ in range(300):
        if srv.poll() is not None:
            raise SystemExit(f"{label}: server exited while loading")
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2)
            break
        except Exception:
            time.sleep(1)
    threading.Thread(target=vram, daemon=True).start()
    text = open(f"{HIER}/wiki.test.raw").read()
    toks = post("/tokenize", {"content": text[:400000]})["tokens"]
    start, runden, t0 = 0, 0, time.time()
    tok = sek = 0.0
    while time.time() - t0 < float(os.environ.get("DAUER", "240")):
        laenge = [ctx - 1200, 300, ctx // 2, 2500, 40][runden % 5]
        teil = toks[start:start + laenge]
        start = (start + laenge) % (len(toks) - ctx)
        a = post("/completion", {"prompt": teil, "n_predict": 1000 if runden % 5 in (0, 3) else 300, "temperature": [0, 0.8][runden % 2]})
        t = a["timings"]
        tok += t["predicted_n"]; sek += t["predicted_ms"] / 1000
        # follow-up: continue prompt + answer (cache reuse as in a conversation)
        weiter = post("/tokenize", {"content": a["content"]})["tokens"]
        n = min(100, ctx - len(teil) - len(weiter) - 10)
        if n > 0:
            post("/completion", {"prompt": teil + weiter, "n_predict": n, "temperature": 0.7})
        runden += 1
    gespraech = post("/v1/chat/completions", {"messages": [{"role": "user", "content": "Erkläre in fünf Sätzen, warum der Himmel blau ist."}],
                                              "max_tokens": 3000, "temperature": 0})["choices"][0]["message"].get("content", "")
    print(f"{label}: {runden} rounds without error in {time.time() - t0:.0f} s | generation {tok / sek:.1f} tok/s | VRAM peak {spitze[0]} MiB | alive: {srv.poll() is None}")
    print(gespraech.strip()[:700])
finally:
    ende.set()
    srv.terminate()
    srv.wait(60)
