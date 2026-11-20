#!/usr/bin/env python3
"""Sheet 1 - Input stage (PDF page 1): U1 (12AX7). Triode A: guitar input (GTR-IN, R1 / R2),
cathode R11 / C2 with R3 switched in by the JFET Q1 (J1), anode R6 from A, C1 to the relays.
Triode B: grid from R13 / R14 (C5 from its own anode, R15 to PRE1) and RLY1; cathode R5 / C3 with
R12 / C4 switched by Q2 (J2); anode R7 from B. RLY1 / RLY2 (coils SW1 / SW2 against H4) select
the gain pots POT1-POT3 (off the board, fly-lead pads POTn-1 / POTn-2).

Differences from the PDF drawing (same nets): the KiCad 12AX7 is three units (triode A, triode B
mirrored, heater), so the tube is wider and the heater unit (h4 / h5 of the PDF) stands at the
lower right; the relay poles are KiCad's G5V-2 units turned so that COM is on the left, NC the
upper and NO the lower contact; the diodes stand beside the coils, and the
relay block is wider than in the PDF."""
from _common import *  # noqa: F401,F403

sh = sheet("01_input_stage.kicad_sch")

GND, GRID = 121, 75                 # rows of the PDF render (10 px units): PRE-GND rail, grids


def R(ref, x, y, top):
    """Vertical resistor / capacitor of the part map at P(x, y) with pin `top` at the top."""
    return vert2(sh, sym(ref), ref, *P(x, y), sh_value(ref), top=top)[1:]


def gnd(p):
    """Wire from p straight down to the PRE-GND rail, with a junction on the rail."""
    q = (p[0], P(0, GND)[1])
    sh.wire(p, q)
    sh.junction(*q)


ua, ub, uh = tube(sh, "U1", P(83, 75), P(97, 75), P(177, 88), mirror_b=True)

# --- triode A ---------------------------------------------------------------------------------------
# input: GTR-IN, R2 to ground, R1 grid stop (#00009, #00007)
term(sh, "GTR_IN", *P(27, GRID), "left")
_, r1l, r1r = horiz2(sh, "R", "R1", *P(68, GRID), sh_value("R1"), left=2)
sh.wire(P(27, GRID), r1l)
sh.wire(r1r, ua.pin(2))
t, b = R("R2", 41, 98, 2)
sh.wire(P(41, GRID), t)
sh.junction(*P(41, GRID))
gnd(b)
# cathode (#00008): C2, R11 to ground, R3 through Q1 (#00011, gate J1)
sh.wire(ua.pin(3), P(81, 87), P(53, 87))
t, b = R("C2", 53, 98, "+")
sh.wire(P(53, 87), t)
gnd(b)
t, b = R("R11", 63, 98, 1)
sh.wire(P(63, 87), t)
sh.junction(*P(63, 87))
gnd(b)
t, b = R("R3", 73, 98, 2)
sh.wire(P(73, 87), t)
sh.junction(*P(73, 87))
q1 = place_mirrored(sh, sym("Q1"), "Q1", *P(75, 113), axis="y", value=sh_value("Q1"),
                    ref_at=(P(66, 0)[0], P(0, 112)[1], 0, None), value_at=(P(66, 0)[0], P(0, 114)[1], 0, None))
sh.wire(b, q1.pin(1))
gnd(q1.pin(2))
sh.wire(q1.pin(3), P(88, 113))
sh.glabel("J1", *P(88, 113), 0)
# anode (#00001): R6 from A, C1 to RLY1 pole 2
t, b = R("R6", 83, 10, 1)
sh.wire(t, P(83, 3), P(104, 3))
sh.glabel("A", *P(104, 3), 0)
sh.wire(b, ua.pin(1))
c1l, c1r = hcap(sh, "C1", *P(106, 25), left=1)
sh.wire(P(83, 25), c1l)
sh.junction(*P(83, 25))

# --- triode B ---------------------------------------------------------------------------------------
# anode (#00000): R7 from B, C5 to the R14 / R15 node (#00031)
t, b = R("R7", 97, 18, 1)
sh.wire(t, P(97, 11), P(104, 11))
sh.glabel("B", *P(104, 11), 0)
sh.wire(b, ub.pin(6))
c5l, c5r = hcap(sh, "C5", *P(106, 37), left=1)
sh.wire(P(97, 37), c5l)
sh.junction(*P(97, 37))
# grid (#00005): R13 - R14 (#00030) - R15 up to PRE1, RLY1 COM 1, R4 to ground
r15t, r15b = R("R15", 123, 42, 1)
r14t, r14b = R("R14", 123, 56, 1)
r13t, r13b = R("R13", 123, 68, 1)
sh.wire(r15t, P(123, 32))
sh.glabel("PRE1", *P(123, 32), 90)
sh.wire(r15b, r14t)
sh.wire(c5r, P(119, 37), P(119, 49))
sh.wire(P(119, 49), P(123, 49))
sh.junction(*P(123, 49))
sh.wire(r14b, r13t)
sh.wire(r13b, P(123, GRID))
sh.wire(ub.pin(7), P(149, GRID))
sh.junction(*P(123, GRID))
sh.junction(*P(131, GRID))
t, b = R("R4", 149, 82, 2)
sh.wire(P(149, GRID), t)
gnd(b)
# cathode (#00006): R5, C3 to ground; R12 and C4 through Q2 (#00035, gate J2)
sh.wire(ub.pin(8), P(99, 87), P(133, 87))
t, b = R("R5", 103, 98, 1)
sh.wire(P(103, 87), t)
sh.junction(*P(103, 87))
gnd(b)
t, b = R("C3", 111, 99, 2)
sh.wire(P(111, 87), t)
sh.junction(*P(111, 87))
gnd(b)
t, r12b = R("R12", 123, 96, 2)
sh.wire(P(123, 87), t)
sh.junction(*P(123, 87))
t, c4b = R("C4", 133, 96, 1)
sh.wire(P(133, 87), t)
q2 = sh.place(sym("Q2"), "Q2", *P(125, 109), 180, value=sh_value("Q2"),
              ref_at=(P(116, 0)[0], P(0, 108)[1], 0, None), value_at=(P(116, 0)[0], P(0, 110)[1], 0, None))
sh.wire(r12b, q2.pin(2))
sh.wire(c4b, P(133, 103), P(123, 103))
sh.junction(*P(123, 103))
gnd(q2.pin(1))
sh.wire(q2.pin(3), P(156, 109))
sh.glabel("J2", *P(156, 109), 0)

# --- C1 output (#00017): R47 to ground, RLY1 COM 2 ---------------------------------------------------
t, b = R("R47", 113, 64, 2)
sh.wire(P(113, 25), t)
sh.junction(*P(113, 25))
sh.wire(b, P(113, 91), P(93, 91))
gnd(P(93, 91))

# --- relays -----------------------------------------------------------------------------------------
# pole units turned 270: COM on the left, NC upper right, NO lower right
k1c, k1p1, k1p2 = relay(sh, "RLY1", P(149, 46), P(148, 33), P(148, 25), rot1=270, rot2=270)
k2c, k2p1, k2p2 = relay(sh, "RLY2", P(191, 46), P(190, 31), P(190, 23), rot1=270, rot2=270)
sh.wire(c1r, k1p2.pin(6))                               # #00017
sh.wire(P(131, GRID), P(131, 33), k1p1.pin(2))          # #00005
sh.wire(k1p2.pin(7), k2p2.pin(6))                       # #00018
sh.wire(k1p1.pin(3), k2p1.pin(2))                       # #00014
# RLY1 NO 2 -> POT1-1 (#00019); NO 1 -> R8 -> POT1-2 (#00020, #00027)
term(sh, "POT1_1", *P(160, 11), "up")
sh.wire(k1p2.pin(8), P(160, 27), P(160, 11))
t, b = R("R8", 167, 44, 1)
sh.wire(k1p1.pin(1), P(167, 35), t)
term(sh, "POT1_2", *P(167, 55), "down")
sh.wire(b, P(167, 55))
# RLY2 NC 2 -> POT3-1 (#00024), NO 2 -> POT2-1 (#00025)
term(sh, "POT3_1", *P(201, 11), "up")
sh.wire(k2p2.pin(7), P(201, 21), P(201, 11))
term(sh, "POT2_1", *P(213, 11), "up")
sh.wire(k2p2.pin(8), P(213, 25), P(213, 11))
# RLY2 NC 1 -> R9 -> POT3-2 (#00021, #00028), NO 1 -> R10 -> POT2-2 (#00026, #00029)
t, b = R("R9", 210, 44, 1)
sh.wire(k2p1.pin(3), P(210, 29), t)
term(sh, "POT3_2", *P(210, 55), "down")
sh.wire(b, P(210, 55))
t, b = R("R10", 222, 44, 1)
sh.wire(k2p1.pin(1), P(222, 33), t)
term(sh, "POT2_2", *P(222, 55), "down")
sh.wire(b, P(222, 55))
# coils: pin 5 = SW1 / SW2 with the diode cathode, pin 4 = H4 with the anode
coil_block(sh, k1c, "D1", "SW1")
coil_block(sh, k2c, "D2", "SW2")

# --- heater (unit C): pin 4 = H4, pin 5 = H5 ---------------------------------------------------------
for pin, net in ((4, "H4"), (5, "H5")):
    p = uh.pin(pin)
    sh.wire(p, down(p, 4))
    sh.glabel(net, *down(p, 4), 270)

# --- ground rail ------------------------------------------------------------------------------------
term(sh, "GTR_GND", *P(27, GND), "left")
sh.wire(P(27, GND), P(158, GND))
sh.glabel("PRE-GND", *P(158, GND), 0)

sh.text("PDF labels pre-gnd, sw1, sw2, h4, h5 = nets PRE-GND, SW1, SW2, H4, H5 (Proteus net names are "
        "case-insensitive).", *P(27, 130))
sh.text("PDF terminal names: GTR-IN = GTR_IN, GTR-GND = GTR_GND, POTn-m = POTn_m. U1 pin 9 has no net "
        "(as in Proteus).", *P(27, 133))
sh.save()
print("sheet01: written")
