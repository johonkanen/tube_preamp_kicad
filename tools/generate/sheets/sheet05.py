#!/usr/bin/env python3
"""Sheet 5 - Supply filter (PDF page 5): the B+ RC filter chain PREPOWER -> R67 -> F -> R66 -> E ->
R65 -> D -> R64 -> C -> R63 -> B -> R62 -> A with one 22 uF / 450 V electrolytic per node to PRE-GND
(PRERETURN), and the fly-lead pads A-D (KiCad refdes PAD_A-PAD_D, on the JFET gate nets J1-J4) and
SW1-SW3 (relay coil switch nets)."""
from _common import *  # noqa: F401,F403

sh = sheet("05_supply_filter.kicad_sch")

RAIL, GND = 45, 71                       # rows of the PDF render (10 px units)
NODES = (("A", 39, "C28", "R62"), ("B", 55, "C33", "R63"), ("C", 73, "C34", "R64"),
         ("D", 91, "C35", "R65"), ("E", 109, "C36", "R66"), ("F", 127, "C37", "R67"))

prev = None
for net, x, cap, res in NODES:
    sh.wire(P(x, 34), P(x, RAIL))
    sh.glabel(net, *P(x, 34), 90)
    _, top, bot = vert2(sh, sym(cap), cap, *P(x, 61), sh_value(cap), top=2)   # pin 2 = +
    sh.wire(P(x, RAIL), top)
    sh.wire(bot, P(x, GND))
    _, rl, rr = horiz2(sh, sym(res), res, *P(x + 7, RAIL), sh_value(res), left=1)
    sh.wire(P(x, RAIL), rl)
    if prev:
        sh.wire(prev, P(x, RAIL))
    sh.junction(*P(x, RAIL))
    sh.junction(*P(x, GND))
    prev = rr

# PREPOWER (#00131, R67 pin 2) and the ground rail PRE-GND with PRERETURN
term(sh, "PREPOWER", *P(149, RAIL), "right")
sh.wire(prev, P(149, RAIL))
term(sh, "PRERETURN", *P(149, GND), "right")
sh.wire(P(28, GND), P(149, GND))
sh.glabel("PRE-GND", *P(28, GND), 180)

# fly-lead pads: Proteus terminals A-D are on J1-J4 (not on the B+ nodes A-D above)
for ref, net, x, y in (("PAD_A", "J1", 107, 87), ("PAD_B", "J2", 107, 101), ("PAD_C", "J3", 107, 115),
                       ("PAD_D", "J4", 107, 129), ("SW1", "SW1", 149, 87), ("SW2", "SW2", 149, 101),
                       ("SW3", "SW3", 149, 115)):
    term(sh, ref, *P(x, y), "right")
    sh.wire(P(x - 15, y), P(x, y))
    sh.glabel(net, *P(x - 15, y), 180)

sh.text("PAD_A-PAD_D are the Proteus terminals A-D: they are on the JFET gate nets J1-J4, "
        "not on the B+ filter nodes A-D.", *P(28, 137))
sh.save()
print("sheet05: written")
