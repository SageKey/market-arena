# Arena

Two pixel armies fight a war driven by live cryptocurrency markets.

Price momentum decides who is winning. Individual trades fire the shots. When the
market rises the bulls take ground; when it falls the bears push them back. Nothing is
simulated — every shot on screen is a real trade that just happened on a real exchange.

**One HTML file. No backend, no build step, no API key, no dependencies.** The browser
talks to two exchanges directly.

---

## How it works

Four layers, each doing a job it is actually suited for.

**The day's move → where the front line sits.**
BTC's change over 24 hours positions the battle. A down day means the bears have already
pushed into bull territory, and the bulls spend the session fighting uphill. Ground stays
won — resetting the armies on a timer would make one side abruptly forget it had been
winning all afternoon, which reads as a glitch rather than a war.

**Three-minute momentum → the swing.**
Recent price action shoves the line up to ±26% around that day position, through
`tanh(drift / 0.012)`. The `tanh` matters: without it a sharp move pins the field at one end
and the battle stops being a battle.

**Trades → gunfire.**
Every trade sends soldiers firing, with the trade's notional deciding how many pull the
trigger at once. Roughly 17 trades per second across both feeds, so the field is never still.

**Sprites → a representative company.**
The counters are the real army; the sprites on screen stand in for them. Volley size and
reinforcement rate scale with how many are actually deployed, so a smaller screen does not
end up with an empty field.

### The chart

BTC price over 24 hours, against **cumulative volume delta** — buy notional minus sell
notional, accumulated for the session.

Trade *counts* are close to meaningless here. 349 buys against 140 sells looks like
overwhelming demand, but price can sit flat through it: retail buys are many and small,
institutional sells are few and large. Measured in dollars, pressure and price agree.

The shaded region marks where live order flow begins — candles give a day of prices, but
they cannot tell you the day's order flow, so CVD only exists from page load onward.

---

## Why not liquidations

The obvious idea is to drive the battle with liquidations — a liquidation is the only event
where a position is genuinely *destroyed*, which is a much better fit for "a kill" than a
trade is. A trade is an exchange; both parties wanted it.

It does not survive contact with the data:

| Exchange | Liquidation feed | Result |
|---|---|---|
| Binance | `!forceOrder@arr` | **Geo-blocked from the US.** REST returns HTTP 451; the WebSocket connects and then silently delivers nothing at all. |
| Bybit | v5 public | Blocked, HTTP 403 |
| dYdX | typed fills | Reachable, but **0 liquidations in 6,000 sampled trades** |
| Hyperliquid | — | No liquidation flag on the trades feed |

Liquidations happen during volatility. On a calm day there are almost none, so a
liquidation-driven screen is blank most of the time — a great mechanic for the day BTC drops
8%, and a dead one every other day. Price is continuous, genuinely asymmetric, and instantly
legible to anyone watching.

The scripts in [`research/`](research/) are the evidence for the table above.

---

## Data sources

Both feeds run at once, normalised through a single entry point.

| Source | Endpoint | Purpose |
|---|---|---|
| Coinbase | `wss://ws-feed.exchange.coinbase.com` — `matches` | Live tape, ~10 trades/sec |
| Hyperliquid | `wss://api.hyperliquid.xyz/ws` — `trades` | Live tape, ~6.6 trades/sec |
| Coinbase | `/products/BTC-USD/candles?granularity=300` | 24h of history on load |

The candles call returns ~29 hours at five-minute granularity, so the chart is useful the
moment the page opens instead of after ten minutes of collecting.

> **Gotcha worth knowing:** Coinbase's `side` field reports the **maker's** side, so the
> aggressor is the opposite — a maker `"sell"` means the taker *bought*. Reading it the
> obvious way inverts the entire battle.

Binance is the usual choice for this kind of thing and is unusable from the US. That is
worth knowing before you build on it.

---

## Themes

Factions are data, not code. The engine only knows "side A" and "side B".

```
?theme=market   Bulls vs Bears        (default)
?theme=gothic   Werewolves vs Vampires
?theme=frost    Frost vs Ember
```

Adding a faction means adding an entry to `THEMES` and, if you want a new silhouette, a
grid to `ART`. No engine changes.

---

## Sprites

11×18 pixel grids stored as text, baked once into offscreen canvases at load. Per-pixel
`fillRect` across ~56 sprites every frame will not hold 60fps; `drawImage` will.

`sprites.py` is the design tool. It renders each sprite twice — shaded, and as a pure
silhouette — and refuses ragged rows:

```bash
python3 sprites.py
```

The silhouette view is the point. The first version of these sprites looked fine as a grid
of characters and rendered as unreadable blobs, because the head merged into the body. A
transparent neck gap fixed it. If the silhouette alone is not recognisable, the shading will
not save it.

---

## Running locally

No build step. Any static server will do:

```bash
python3 -m http.server 8787
```

Then open <http://localhost:8787/index.html?theme=gothic>.

Opening the file directly over `file://` also works, but a server is closer to how it is
deployed.

---

## Layout

```
index.html      the whole application
sprites.py      sprite design + silhouette validation
research/       exchange feed probes — the evidence behind the design decisions
iterations/     earlier versions, kept because the path is part of the work
```

`iterations/` traces the build: abstract projectiles, then stick figures, then a version
driven by aggressor flow that sat stubbornly at 50/50 — because every trade has both a buyer
and a seller, so "buyers versus sellers" is even by definition. That flaw is what moved the
mechanic to price.

---

## License

MIT
