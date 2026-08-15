#!/usr/bin/env python3
"""Does Hyperliquid expose liquidations on its public WebSocket?

Subscribes to trades across the busiest coins and reports the raw shape of
what arrives, so we can see whether liquidations are flagged.

    python3 hl_probe.py 60
"""

import asyncio
import json
import sys
from collections import Counter

import websockets

WS = "wss://api.hyperliquid.xyz/ws"
COINS = ["BTC", "ETH", "SOL", "HYPE"]


async def main(seconds):
    keys_seen = Counter()
    shown = 0
    total = 0

    async with websockets.connect(WS, ping_interval=20) as ws:
        for coin in COINS:
            await ws.send(json.dumps({
                "method": "subscribe",
                "subscription": {"type": "trades", "coin": coin},
            }))
        print("subscribed to trades: {}\n".format(", ".join(COINS)))

        loop = asyncio.get_event_loop()
        end = loop.time() + seconds
        while loop.time() < end:
            try:
                raw = await asyncio.wait_for(
                    ws.recv(), timeout=max(1.0, end - loop.time()))
            except asyncio.TimeoutError:
                break

            msg = json.loads(raw)
            if msg.get("channel") != "trades":
                if shown < 3:
                    print("non-trade frame: {}".format(raw[:200]))
                    shown += 1
                continue

            for t in msg.get("data", []):
                total += 1
                for k in t:
                    keys_seen[k] += 1
                if total <= 6:
                    print("trade: {}".format(json.dumps(t)))

    print("\n{} trades seen".format(total))
    print("fields present: {}".format(dict(keys_seen)))


if __name__ == "__main__":
    asyncio.run(main(float(sys.argv[1]) if len(sys.argv) > 1 else 45))
