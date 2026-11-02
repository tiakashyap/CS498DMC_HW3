import json
import statistics
import sys
import time
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
N = 500

def run(endpoint):
    times = []
    for i in range(N):
        body = json.dumps({"Make": "LATENCYTEST", "Model": endpoint, "seq": i}).encode()
        req = urllib.request.Request(
            BASE + endpoint, data=body, headers={"Content-Type": "application/json"}, method="POST"
        )
        start = time.perf_counter()
        with urllib.request.urlopen(req) as resp:
            resp.read()
        times.append((time.perf_counter() - start) * 1000) 
    return times

for ep in ("/insert-fast", "/insert-safe"):
    run_n = urllib.request.Request(
        BASE + ep, data=b'{"Make":"WARMUP"}', headers={"Content-Type": "application/json"}, method="POST"
    )
    urllib.request.urlopen(run_n).read()

results = {}
for ep in ("/insert-fast", "/insert-safe"):
    t = run(ep)
    results[ep] = t
    print(f"{ep}: n={len(t)}  avg={statistics.mean(t):.2f} ms  "
          f"median={statistics.median(t):.2f} ms  min={min(t):.2f}  max={max(t):.2f}")

fast, safe = statistics.mean(results["/insert-fast"]), statistics.mean(results["/insert-safe"])
print(f"\n/insert-safe is {safe / fast:.2f}x slower than /insert-fast on average ({safe - fast:.2f} ms difference)")