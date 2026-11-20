#!/usr/bin/env python3
"""Sheet 2 - Second stage (PDF page 2): U2 (12AX7). RLY3 (coil SW1 against H4) routes PRE1 (from
sheet 1) through R16 to triode A (grid divider R16 / R17, R19 switched by Q3, grid stop R18) and
connects EQ (to sheet 3) to PRE2, the anode of triode B. Triode A: cathode R21 with C6 / R20
switched by Q4, anode R22 / C8 from C, C7 into the network C11 / C13 / R31, R24-R27, C12 to the
grid of triode B (R29 switched by Q6). Triode B: cathode R28 / C9 with C14 / R30 switched by Q5,
anode R23 from D (net PRE2, R50 to ground).

Differences from the PDF drawing (same nets): the KiCad 12AX7 is three units (triode A, triode B
mirrored, heater between the cathode networks), so everything right of the tube is further right;
the relay is KiCad's one-unit G5V-2 (Omron pin numbers) turned so that the coil is on top with its
diode above it, COM on the left, NC the upper and NO the lower contact; R50 runs straight down to the ground rail."""
from _common import *  # noqa: F401,F403

sh = sheet("02_second_stage.kicad_sch")

GND, GRID, KBUS = 115, 71, 81       # rows (PDF render, 10 px units): PRE-GND rail, grids, cathode buses


def V(ref, x, y, top):
    """Vertical two-pin part of the part map at P(x, y) with pin `top` at the top: (top, bottom)."""
    return vert2(sh, sym(ref), ref, *P(x, y), sh_value(ref), top=top)[1:]


def jfet(ref, x, y):
    """J112 with the gate on the right, source (pin 2) at the top at P(x, y), drain (pin 1) on the
    PRE-GND rail (Q3-Q6: rotation 180). Returns the gate point."""
    cx, cy = P(x + 2, y + 4)
    tx = round(cx + g(5), 4)
    q = sh.place(sym(ref), ref, cx, cy, 180, value=sh_value(ref),
                 ref_at=(tx, round(cy + g(3), 4), 0, None), value_at=(tx, round(cy + g(5), 4), 0, None))
    assert q.pin(2) == P(x, y), (ref, q.pins)
    rail(sh, q.pin(1), y=P(0, GND)[1])
    return q.pin(3)


ua, ub, uh = tube(sh, "U2", P(97, GRID), P(111, GRID), P(100, 91), mirror_b=True)

# --- RLY3 (Omron pins): pole 4 / 6 / 8 EQ -> PRE2 (NC), pole 13 / 11 / 9 PRE1 -> R16 (NC); both NO
# contacts joined (#00062) -----------------------------------------------------------------------------
k = relay(sh, "RLY3", P(22, 39))
glabel_left(sh, "EQ", k.pin(4), 4)
glabel_left(sh, "PRE1", k.pin(13), 4)
label_right(sh, "PRE2", k.pin(6), 5)
sh.wire(k.pin(8), P(32, 41), P(32, 49))
sh.wire(P(32, 49), k.pin(9))
coil_block(sh, k, "D3", "SW1")

# --- triode A ---------------------------------------------------------------------------------------
# grid: R16 (#00046) from RLY3 NC 11; node #00047 with R17 to ground, R19 / Q3 (#00049, J1), R18 (#00043)
t, b = V("R16", 43, 62, 1)
sh.wire(k.pin(11), P(43, 45), t)
sh.wire(b, P(43, GRID))
_, r18l, r18r = horiz2(sh, "R", "R18", *P(66, GRID), sh_value("R18"), left=2)
sh.wire(P(43, GRID), r18l)
sh.wire(r18r, ua.pin(2))
t, b = V("R17", 43, 86, 2)
sh.wire(P(43, GRID), t)
sh.junction(*P(43, GRID))
rail(sh, b, y=P(0, GND)[1])
t, b = V("R19", 53, 86, 1)
sh.wire(P(53, GRID), t)
sh.junction(*P(53, GRID))
sh.wire(b, P(53, 99))
q3g = jfet("Q3", 53, 99)
sh.wire(q3g, P(65, 103), P(65, 131))
sh.wire(P(65, 131), P(75, 131))
sh.glabel("J1", *P(75, 131), 0)
term(sh, "POT_GND", *P(53, 123), "down")
sh.wire(P(53, GND), P(53, 123))
# cathode (#00044): R21 to ground, C6 / R20 through Q4 (#00050, J1)
sh.wire(ua.pin(3), P(95, KBUS), P(69, KBUS))
t, c6b = V("C6", 69, 88, 2)
sh.wire(P(69, KBUS), t)
t, r20b = V("R20", 81, 88, 2)
sh.wire(P(81, KBUS), t)
sh.junction(*P(81, KBUS))
sh.wire(r20b, P(81, 93), P(69, 93))
sh.wire(c6b, P(69, 100))
sh.junction(*P(69, 93))
q4g = jfet("Q4", 69, 100)
sh.wire(q4g, P(84, 104), P(84, 121))
sh.wire(P(84, 121), P(88, 121))
sh.glabel("J1", *P(88, 121), 0)
t, b = V("R21", 89, 100, 2)
sh.wire(P(89, KBUS), t)
sh.junction(*P(89, KBUS))
rail(sh, b, y=P(0, GND)[1])
# anode (#00037): R22 and C8 from C, C7 to the network
t, b = V("R22", 97, 12, 2)
sh.wire(b, ua.pin(1))
sh.wire(t, P(97, 3))
sh.wire(P(79, 3), P(110, 3))
sh.glabel("C", *P(110, 3), 0)
sh.junction(*P(97, 3))
c8t, c8b = V("C8", 79, 11, 1)
sh.wire(c8t, P(79, 3))
sh.wire(c8b, P(79, 21), P(97, 21))
sh.junction(*P(97, 21))
c7l, c7r = hcap(sh, "C7", *P(124, 21), left=1)
sh.wire(P(97, 21), c7l)

# --- network between the triodes ----------------------------------------------------------------------
# #00053: C7, C11, R24; #00054: R24, R25, C12; #00055: R25, R26, C13; #00064: C11, C13, R31
r24t, r24b = V("R24", 183, 28, 1)
r25t, r25b = V("R25", 183, 44, 1)
r26t, r26b = V("R26", 183, 62, 1)
sh.wire(c7r, P(183, 21), r24t)
sh.wire(r24b, r25t)
sh.wire(r25b, r26t)
c11t, c11b = V("C11", 159, 33, 2)
sh.wire(P(159, 21), c11t)
sh.junction(*P(159, 21))
c13l, c13r = hcap(sh, "C13", *P(166, 53), left=2)
sh.wire(c11b, P(159, 53), c13l)
sh.wire(c13r, P(183, 53))
sh.junction(*P(183, 53))
_, t, b = vert2(sh, "R", "R31", *P(175, 88), sh_value("R31"), top=1, text="left")
sh.wire(P(159, 43), P(175, 43), t)
sh.junction(*P(159, 43))
rail(sh, b, y=P(0, GND)[1])
c12t, c12b = V("C12", 193, 53, 2)
sh.wire(P(183, 37), P(193, 37), c12t)
sh.junction(*P(183, 37))

# --- triode B ---------------------------------------------------------------------------------------
# grid (#00041): R26, R27 to ground, C12, R29 through Q6 (#00056, J4)
sh.wire(ub.pin(7), P(193, GRID))
sh.wire(r26b, P(183, GRID))
sh.junction(*P(183, GRID))
t, b = V("R27", 183, 78, 2)
sh.wire(P(183, GRID), t)
rail(sh, b, y=P(0, GND)[1])
sh.wire(c12b, P(193, GRID))
t, b = V("R29", 193, 78, 1)
sh.wire(P(193, GRID), t)
sh.junction(*P(193, GRID))
sh.wire(b, P(193, 100))
q6g = jfet("Q6", 193, 100)
sh.wire(q6g, P(210, 104))
sh.glabel("J4", *P(210, 104), 0)
# cathode (#00042): C9, R28 to ground, C14 / R30 through Q5 (#00057, J1)
t, b = V("C9", 113, 104, 2)
sh.wire(ub.pin(8), t)
rail(sh, b, y=P(0, GND)[1])
sh.wire(P(113, KBUS), P(147, KBUS))
sh.junction(*P(113, KBUS))
t, b = V("R28", 123, 100, 2)
sh.wire(P(123, KBUS), t)
sh.junction(*P(123, KBUS))
rail(sh, b, y=P(0, GND)[1])
t, c14b = V("C14", 137, 88, 2)
sh.wire(P(137, KBUS), t)
sh.junction(*P(137, KBUS))
t, r30b = V("R30", 147, 88, 2)
sh.wire(P(147, KBUS), t)
sh.wire(r30b, P(147, 95), P(137, 95))
sh.wire(c14b, P(137, 100))
sh.junction(*P(137, 95))
q5g = jfet("Q5", 137, 100)
sh.wire(q5g, P(153, 104), P(153, 123))
sh.wire(P(153, 123), P(160, 123))
sh.glabel("J1", *P(160, 123), 0)
# anode = PRE2: R23 from D, R50 to ground, RLY3 NC 6 (label)
t, b = V("R23", 111, 38, 2)
sh.wire(t, P(111, 29), P(116, 29))
sh.glabel("D", *P(116, 29), 0)
sh.wire(b, ub.pin(6))
sh.wire(P(111, 49), P(136, 49))
sh.junction(*P(111, 49))
sh.label("PRE2", *P(136, 49), 0)
t, b = V("R50", 131, 62, 1)
sh.wire(P(131, 49), t)
sh.junction(*P(131, 49))
rail(sh, b, y=P(0, GND)[1])

# --- heater (unit C): pin 4 = H4, pin 5 = H5 ---------------------------------------------------------
for pin, net in ((4, "H4"), (5, "H5")):
    p = uh.pin(pin)
    sh.wire(p, down(p, 3))
    sh.glabel(net, *down(p, 3), 270)

# --- ground rail ------------------------------------------------------------------------------------
sh.wire(P(34, GND), P(193, GND))
sh.glabel("PRE-GND", *P(34, GND), 180)

sh.text("PDF labels sw1, j4 = nets SW1, J4 (Proteus net names are case-insensitive). PRE2 is a net of "
        "this sheet only (local labels).", *P(10, 138))
sh.text("PDF terminal name POT-GND = POT_GND. Q4's value is NADA in the Proteus schematic (the part on "
        "the board is a J112). U2 pin 9 has no net (as in Proteus).", *P(10, 141))
sh.save()
print("sheet02: written")
