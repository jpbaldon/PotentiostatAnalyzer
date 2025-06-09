import time
import json
import random

start_time = time.time()
duration = 30.0  # seconds
interval = 0.1   # 100 ms

while True:
    elapsed = time.time() - start_time
    if elapsed >= duration:
        break

    data = {
        "time": round(elapsed, 2),
        "voltage": round(random.uniform(0, 5), 3),
        "current": round(random.uniform(-0.01, 0.01), 6),
        "resistance": round(random.uniform(1000, 10000), 2)
    }

    print(json.dumps(data), flush=True)
    time.sleep(interval)