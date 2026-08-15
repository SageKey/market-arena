#!/usr/bin/env python3
"""Diagnostic: is the feed silent, or am I parsing it wrong?

Opens both the raw and combined stream endpoints and dumps whatever arrives,
unparsed. Also pulls a REST snapshot to confirm the market is actually moving.
"""

import asyncio
import json
import sys
import urllib.request

import websockets

ENDPOINTS = {
    "raw": "wss://fstream.binance.com/ws/!forceOrder@arr",
    "combined": "wss://fstream.binance.com/stream?streams=!forceOrder@arr",
}


def market_is_alive():
    """REST sanity check — if this moves, the market is open and trading."""
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr?symbol=BTCUSDT"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            d = json.loads(r.read())
        print("REST ok: BTCUSDT last={} 24h_change={}% trades={}".format(
            d["lastPrice"], d["priceChangePercent"], d["count"]))
        return True
    except Exception as e:
        print("REST failed: {}".format(e))
        return False


async def listen(name, url, seconds):
    got = 0
    try:
        async with websockets.connect(url, ping_interval=20) as ws:
            print("[{}] connected".format(name))
            loop = asyncio.get_event_loop()
            end = loop.time() + seconds
            while loop.time() < end:
                try:
                    raw = await asyncio.wait_for(
                        ws.recv(), timeout=max(1.0, end - loop.time()))
                except asyncio.TimeoutError:
                    break
                got += 1
                if got <= 5:
                    print("[{}] frame {}: {}".format(name, got, raw[:400]))
    except Exception as e:
        print("[{}] error: {}".format(name, type(e).__name__, ))
        print("[{}] {}".format(name, e))
    print("[{}] total frames in {}s: {}".format(name, seconds, got))
    return got


async def main(seconds):
    results = await asyncio.gather(
        *(listen(n, u, seconds) for n, u in ENDPOINTS.items())
    )
    print("\nsummary: {}".format(dict(zip(ENDPOINTS, results))))


if __name__ == "__main__":
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 90
    market_is_alive()
    asyncio.run(main(secs))
