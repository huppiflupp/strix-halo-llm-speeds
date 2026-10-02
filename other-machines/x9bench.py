#!/usr/bin/env python3
"""Measure one llama-server configuration: generation and prompt speed in tokens per second.

Starts the server, waits for /health, sends one warm-up request, then one coding prompt
(500 new tokens) and one long prompt (~7,400 tokens of source code), and prints one JSON line
with the server's own timings. Paths are those of the machine "x9"; adjust BIN and the model
directory for another host.

    x9bench.py NAME MODEL.gguf [further llama-server arguments ...]
"""
import json, subprocess, sys, time, urllib.request, os

BIN = "/data/llama/llama.cpp/build/bin/llama-server"
PORT = 18190
BASE = f"http://127.0.0.1:{PORT}"
name, model, extra = sys.argv[1], sys.argv[2], sys.argv[3:]

log = open(f"/data/llama/bench/{name}.log", "w")
cmd = [BIN, "-m", f"/data/models/{model}", "-fa", "on", "--jinja", "-np", "1", "--no-webui",
       "-t", "12", "--host", "127.0.0.1", "--port", str(PORT)] + extra
srv = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)

def post(path, body, timeout=900):
    req = urllib.request.Request(BASE + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())

res = {"name": name, "args": " ".join(extra)}
try:
    t0 = time.time()
    while True:
        if srv.poll() is not None:
            raise RuntimeError("server exited, see log")
        try:
            if urllib.request.urlopen(BASE + "/health", timeout=2).status == 200:
                break
        except Exception:
            pass
        if time.time() - t0 > 600:
            raise RuntimeError("timeout while loading")
        time.sleep(1)
    res["load_s"] = round(time.time() - t0)

    def chat(prompt, n):
        r = post("/v1/chat/completions", {"messages": [{"role": "user", "content": prompt}],
                 "max_tokens": n, "temperature": 0, "cache_prompt": False})
        return r["timings"]

    chat("Sag kurz hallo.", 16)  # warm-up
    gen = "Schreibe ein vollständiges Python-Modul mit einer Klasse LRUCache (get, put, Kapazitätsgrenze, Typannotationen, Docstrings) und dazu pytest-Tests."
    t = chat(gen, 500)
    res["gen_tok_s"] = round(t["predicted_per_second"], 1)
    res["gen_n"] = t["predicted_n"]
    # long prompt: source code as context (7362 tokens for this model)
    src = open("/data/llama/llama.cpp/common/sampling.cpp").read()[:28000]
    t = chat("Fasse zusammen, was dieser Code tut:\n\n" + src, 200)
    res["prompt_tok_s"] = round(t["prompt_per_second"], 1)
    res["prompt_n"] = t["prompt_n"]
    res["gen_tok_s_after_long_prompt"] = round(t["predicted_per_second"], 1)
    smi = subprocess.run(["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True).stdout.strip()
    res["vram_mib"] = int(smi)
    rss = int(open(f"/proc/{srv.pid}/statm").read().split()[1]) * os.sysconf("SC_PAGE_SIZE") // 2**20
    res["rss_mib"] = rss
except Exception as e:
    res["error"] = str(e)
finally:
    srv.terminate()
    try:
        srv.wait(30)
    except Exception:
        srv.kill()
print(json.dumps(res, ensure_ascii=False))
