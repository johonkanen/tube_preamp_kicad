#!/usr/bin/env python3
"""Sheet 4 - Tone stacks (PDF page 4): three identical passive tone stacks on the nets EQ1, EQ2,
EQ3 (from the relays RLY4 / RLY5 of sheet 3). The pots are off the board: HInO / HInW / HInX and
LOnO / LOnW / LOnX are their fly-lead pads. One helper (_common.tone_stack) draws a stack."""
from _common import *  # noqa: F401,F403

sh = sheet("04_tone_stacks.kicad_sch")

GND = 113                                 # row of the PRE-GND rail (PDF render, 10 px units)

g1 = tone_stack(sh, 1, 81, 11, "EQ1", "C18", "R35", "C16", "C17", "R36", "R37", "C19")
g2 = tone_stack(sh, 2, 25, 63, "EQ2", "C22", "R38", "C20", "C21", "R40", "R39", "C23", xc=12)
g3 = tone_stack(sh, 3, 147, 63, "EQ3", "C26", "R41", "C24", "C25", "R43", "R42", "C27")

# ground rail: the three ground nodes (R37 / C19, R39 / C23, R42 / C27) to PRE-GND
sh.glabel("PRE-GND", *P(16, GND), 180)
sh.wire(P(16, GND), P(147, GND), g3)
for gnode, x in ((g1, 81), (g2, 25)):
    sh.wire(gnode, P(x, GND))
    sh.junction(*P(x, GND))
for gnode in (g1, g2, g3):
    sh.junction(*gnode)

sh.save()
print("sheet04: written")
