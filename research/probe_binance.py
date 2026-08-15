#!/usr/bin/env python3
"""Prove the Binance liquidation feed is real before building anything on it.

Connects to the all-market force-order stream and prints each liquidation as
the game would read it: a SELL means a long was force-sold (a bull dies), a
BUY means a short was force-covered (a bear dies).

    python3 probe.py           # run until Ctrl-C
    python3 probe.py 60        # run for 60 seconds
"""

import asyncio
import json
import sys
import time

import websockets

STREAM = "wss://fstream.binance.com/ws/!forceOrder@arr"


def render(order):
    """Turn one force-order payload into a line of game commentary."""
    symbol = order["s"]
    side = order["S"]                      # SELL = long liquidated, BUY = short liquidated
    price = float(order["ap"] or order["p"])
    qty = float(order["q"])
    usd = price * qty

    if side == "SELL":
        who, mark = "BULL", "v"
    else:
        who, mark = "BEAR", "^"

    stamp = time.strftime("%H:%M:%S", time.localtime(order["T"] / 1000))
    return "{}  {} {:<5} {:<12} ${:>12,.0f}  @ {:,.2f}".format(
        stamp, mark, who, symbol, usd, price
    )


async def main(duration=None):
    print("connecting to {} ...".format(STREAM))
    deadline = time.time() + duration if duration else None
    count = 0
    bulls = bears = 0
    volume = 0.0

    async with websockets.connect(STREAM, ping_interval=20) as ws:
        print("connected. waiting for liquidations "
              "(quiet markets can mean a long wait)\n")
        while True:
            if deadline and time.time() > deadline:
                break
            timeout = max(1.0, deadline - time.time()) if deadline else None
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
            except asyncio.TimeoutError:
                break

            msg = json.loads(raw)
            order = msg.get("o")
            if not order:
                continue

            count += 1
            price = float(order["ap"] or order["p"])
            volume += price * float(order["q"])
            if order["S"] == "SELL":
                bulls += 1
            else:
                bears += 1
            print(render(order))

    print("\n--- {} liquidations | {} bulls down, {} bears down | "
          "${:,.0f} total ---".format(count, bulls, bears, volume))


if __name__ == "__main__":
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else None
    try:
        asyncio.run(main(secs))
    except KeyboardInterrupt:
        print("\nstopped")
