#!/usr/bin/env python3
"""Can we get real liquidations from a US-reachable exchange?

Binance is geo-blocked (451). Bybit is blocked (403). That leaves the perp
DEXes. dYdX types its fills, so a liquidation is labelled as one; this polls
its trade endpoint across the busiest markets and counts what shows up.
"""

import json
import sys
import time
import urllib.request
from collections import Counter

MARKETS = ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "AVAX-USD", "LINK-USD"]
BASE = "https://indexer.dydx.trade/v4/trades/perpetualMarket/{}?limit=1000"


def fetch(market):
    try:
        with urllib.request.urlopen(BASE.format(market), timeout=15) as r:
            return json.loads(r.read()).get("trades", [])
    except Exception as e:
        print("  {} failed: {}".format(market, e))
        return []


def main(rounds=3, gap=20):
    seen = set()
    types = Counter()
    liqs = []

    for i in range(rounds):
        for m in MARKETS:
            for t in fetch(m):
                key = t.get("id")
                if key in seen:
                    continue
                seen.add(key)
                ty = t.get("type", "?")
                types[ty] += 1
                if ty != "LIMIT":
                    liqs.append((m, t))
        print("round {}/{}: {} unique trades, types={}".format(
            i + 1, rounds, len(seen), dict(types)))
        if i < rounds - 1:
            time.sleep(gap)

    print("\ntype breakdown: {}".format(dict(types)))
    if liqs:
        print("\nnon-LIMIT samples:")
        for m, t in liqs[:6]:
            print("  {} {} side={} size={} price={}".format(
                m, t.get("type"), t.get("side"), t.get("size"), t.get("price")))
    else:
        print("\nno liquidation-typed fills in this sample")

    n_liq = sum(v for k, v in types.items() if k != "LIMIT")
    if seen:
        print("\nliquidation share: {}/{} = {:.2f}%".format(
            n_liq, len(seen), 100 * n_liq / len(seen)))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
