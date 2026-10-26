#!/usr/bin/env python3
"""Generate a synthetic OHLC CSV for testing pnf.py (random walk, no real data)."""

import csv
import random
from datetime import date, timedelta

def main(n_days: int = 250, seed: int = 7, out: str = "sample_ohlc.csv"):
    rng = random.Random(seed)
    price = 20000.0
    start = date(2024, 1, 1)
    rows = []
    for i in range(n_days):
        drift = rng.gauss(0, price * 0.012)
        open_p = price
        close_p = max(1000.0, price + drift)
        high = max(open_p, close_p) * (1 + abs(rng.gauss(0, 0.004)))
        low = min(open_p, close_p) * (1 - abs(rng.gauss(0, 0.004)))
        rows.append({
            "date": (start + timedelta(days=i)).isoformat(),
            "open": round(open_p, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close_p, 2),
        })
        price = close_p
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "open", "high", "low", "close"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {n_days} synthetic rows -> {out}")

if __name__ == "__main__":
    main()
