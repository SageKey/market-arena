#!/usr/bin/env python3
"""Which feed gives us more to shoot at — Coinbase or Hyperliquid?

Runs both for the same window and counts trades per second. More events per
second means a busier battlefield, which is the whole point.
"""

import asyncio
import json
import sys
import time

import websockets

HL_WS = "wss://api.hyperliquid.xyz/ws"
HL_COINS = ["BTC", "ETH", "SOL", "HYPE", "DOGE", "XRP"]

CB_WS = "wss://ws-feed.exchange.coinbase.com"
CB_PAIRS = ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "XRP-USD", "LTC-USD"]


async def hyperliquid(seconds):
    n = 0
    try:
        async with websockets.connect(HL_WS, ping_interval=20) as ws:
            for c in HL_COINS:
                await ws.send(json.dumps({
                    "method": "subscribe",
                    "subscription": {"type": "trades", "coin": c}}))
            end = time.time() + seconds
            while time.time() < end:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=max(1, end - time.time()))
                except asyncio.TimeoutError:
                    break
                m = json.loads(raw)
                if m.get("channel") == "trades":
                    n += len(m.get("data", []))
    except Exception as e:
        print("hyperliquid error:", e)
    return n


async def coinbase(seconds):
    n = 0
    try:
        async with websockets.connect(CB_WS, ping_interval=20) as ws:
            await ws.send(json.dumps({
                "type": "subscribe",
                "product_ids": CB_PAIRS,
                "channels": ["matches"],
            }))
            end = time.time() + seconds
            sample = None
            while time.time() < end:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=max(1, end - time.time()))
                except asyncio.TimeoutError:
                    break
                m = json.loads(raw)
                t = m.get("type")
                if t in ("match", "last_match"):
                    n += 1
                    if sample is None:
                        sample = m
                        print("coinbase sample:", json.dumps(m)[:260])
                elif t == "error":
                    print("coinbase error:", m)
                    break
    except Exception as e:
        print("coinbase error:", e)
    return n


async def main(seconds):
    hl, cb = await asyncio.gather(hyperliquid(seconds), coinbase(seconds))
    print("\n{:<14} {:>7} trades  {:>6.1f}/sec".format("hyperliquid", hl, hl / seconds))
    print("{:<14} {:>7} trades  {:>6.1f}/sec".format("coinbase", cb, cb / seconds))
    if hl and cb:
        print("\ncoinbase is {:.1f}x hyperliquid".format(cb / hl))


if __name__ == "__main__":
    asyncio.run(main(float(sys.argv[1]) if len(sys.argv) > 1 else 45))
