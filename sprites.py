#!/usr/bin/env python3
"""Design + validate the pixel sprites before they go near the canvas.

v1 came out as blobs: the head merged into the body and the ears vanished.
Two fixes here — a transparent neck gap so the head reads as a separate mass,
and ears/horns that rise out of clear empty space.

Prints two views per sprite: the shaded version, and the pure silhouette. If
the silhouette alone isn't recognisable, the sprite has failed regardless of
how nice the shading is.

Legend
  .  transparent   1 body   2 outline   3 highlight   4 eye   5 weapon
"""

W = 11

SPRITES = {
"wolf": [
    ".2.......2.",
    ".22.....22.",
    ".232...232.",
    ".2321.2232.",
    ".23111132..",
    ".2411111 2.",
    ".23111114 2",
    "..2311132..",
    "...22122...",   # neck
    "..2311132..",
    ".231111132.",
    "231111111 5",   # weapon arm
    ".23111132..",
    ".2311132...",
    ".231.132...",
    ".23...32...",
    ".22...22...",
    "222...222..",
],
"vampire": [
    "...22222...",
    "..2333332..",
    "..2343432..",
    "..2333332..",
    "...23332...",
    "....212....",   # neck
    "..2311132..",
    ".2231111322",
    "231111111 2",
    "23111111 55",   # weapon arm
    "231111111 2",
    ".2311111 2.",
    "..23111 2..",
    "..231132...",
    "..231.32...",
    "..23..32...",
    "..22..22...",
    ".222..222..",
],
"bull": [
    "3.........3",
    "23.......32",
    ".23.....32.",
    "..2333332..",
    "..2341432..",
    "..2333332..",
    "...23332...",
    "....212....",   # neck
    "..2311132..",
    ".231111132.",
    "23111111 55",   # weapon arm
    ".231111132.",
    "..23111 2..",
    "..231132...",
    "..231.32...",
    "..23..32...",
    "..22..22...",
    ".222..222..",
],
"bear": [
    "..22...22..",
    ".2332.2332.",
    ".2332.2332.",
    "..2333332..",
    "..2341432..",
    "..2333332..",
    "...23432...",
    "....212....",   # neck
    "..2311132..",
    ".231111132.",
    "23111111 55",   # weapon arm
    ".231111132.",
    "..23111 2..",
    "..231132...",
    "..231.32...",
    "..23..32...",
    "..22..22...",
    ".222..222..",
],
}

SHADE = {".": " ", " ": " ", "1": "█", "2": "▓", "3": "▒", "4": "●", "5": "═"}


def show(name, rows):
    widths = {len(r) for r in rows}
    good = widths == {W}
    print("\n{}  {}x{}  {}".format(
        name.upper(), sorted(widths), len(rows), "OK" if good else "!! RAGGED"))
    if not good:
        for i, r in enumerate(rows):
            if len(r) != W:
                print("   row {:>2} is {} wide: {!r}".format(i, len(r), r))

    pad = len(rows[0])
    print("  shaded" + " " * (pad - 4) + "silhouette")
    for r in rows:
        shaded = "".join(SHADE.get(c, "?") for c in r)
        solid = "".join(" " if c in ". " else "█" for c in r)
        print("  |" + shaded + "|   |" + solid + "|")
    return good


def main():
    ok = all(show(n, r) for n, r in SPRITES.items())
    print("\n" + ("all sprites valid" if ok else "FIX THE RAGGED ROWS"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
