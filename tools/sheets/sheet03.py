#!/usr/bin/env python3
"""Sheet 3 - EQ stage (PDF page 3): U3 (12AX7). Triode A is a cathode follower (anode on E, grid
from EQ through C10, biased by R33 / R48 / C30 through R49; cathode R32, C15 out). RLY4 / RLY5
send the follower output to one of the tone stacks EQ1-EQ3 (sheet 4) and pick the matching
master-volume return MV1-MV3 for the grid of triode B (R46). Triode B: cathode R44, anode R51 /
R34 from F, output EQOUT, C29 to PRES; Q7-Q9 (J3, J2, J4) ground the pads PRES1-PRES3. RLY4's
coil is fed from SW2 or SW3 through D5 / D4 (#00081), RLY5's from SW3. The heater pads H4 / H5.

Differences from the PDF drawing (same nets): the KiCad 12AX7 is three units (triode A, triode B
mirrored, heater); the heater unit with the pads H4 / H5 stands at the upper right. The relay
poles are KiCad's G5V-2 units turned so that COM is on the left, NC the upper and NO the lower
contact; the relay block and the JFETs are further right than in the PDF."""
from _common import *  # noqa: F401,F403

sh = sheet("03_eq_stage.kicad_sch")

GND, GRID = 127, 43                 # rows (PDF render, 10 px units): PRE-GND rail, grids


def V(ref, x, y, top, **kw):
    """Vertical two-pin part of the part map at P(x, y) with pin `top` at the top: (top, bottom)."""
    return vert2(sh, sym(ref), ref, *P(x, y), sh_value(ref), top=top, **kw)[1:]


def gnd(p):
    """Wire from p straight down to the PRE-GND rail, with a junction on the rail."""
    q = (p[0], P(0, GND)[1])
    sh.wire(p, q)
    sh.junction(*q)


ua, ub, uh = tube(sh, "U3", P(57, GRID), P(71, GRID), P(165, 22), mirror_b=True)

# --- triode A (cathode follower) ----------------------------------------------------------------------
# grid (#00075): EQ through C10, R49 from the bias node (#00102: R33 from E, R48 and C30 to ground)
c10l, c10r = hcap(sh, "C10", *P(19, GRID), left=1)
glabel_left(sh, "EQ", c10l, 8)
sh.wire(c10r, ua.pin(2))
t, b = V("R49", 27, 76, 2)
sh.wire(P(27, GRID), t)
sh.junction(*P(27, GRID))
c30t, c30b = V("C30", 27, 104, "+")
sh.wire(b, c30t)
gnd(c30b)
r33t, r33b = V("R33", 37, 62, 2)
r48t, r48b = V("R48", 37, 102, 2)
sh.wire(r33b, r48t)
sh.wire(P(27, 87), P(37, 87))
sh.junction(*P(27, 87))
sh.junction(*P(37, 87))
gnd(r48b)
# anode = E, R33 pin 2
sh.wire(ua.pin(1), P(57, 22))
sh.glabel("E", *P(57, 22), 90)
sh.wire(r33t, P(37, 31), P(57, 31))
sh.junction(*P(57, 31))
# cathode (#00076): R32 to ground, C15 to RLY4 COM 2 (#00082, R45 to ground)
t, b = V("R32", 45, 116, 2)
sh.wire(ua.pin(3), P(55, 53), P(45, 53))
sh.wire(P(45, 53), t)
gnd(b)
c15l, c15r = hcap(sh, "C15", *P(55, 73), left=1)
sh.wire(P(45, 73), c15l)
sh.junction(*P(45, 73))
t, b = V("R45", 67, 102, 2)
sh.wire(P(67, 73), t)
sh.junction(*P(67, 73))
gnd(b)

# --- triode B ---------------------------------------------------------------------------------------
# cathode (#00074): R44 to ground
t, b = V("R44", 81, 100, 1)
sh.wire(ub.pin(8), P(73, 53), P(81, 53))
sh.wire(P(81, 53), t)
gnd(b)
# anode (#00068): R51 to the output node (#00092: R34 from F, EQOUT, C29 to PRES #00095)
r51t, r51b = V("R51", 71, 28, 2)
sh.wire(r51b, ub.pin(6))
r34t, r34b = V("R34", 71, 12, 2)
sh.wire(r34b, r51t)
sh.wire(r34t, P(71, 3), P(108, 3))
sh.glabel("F", *P(108, 3), 0)
term(sh, "EQOUT", *P(108, 21), "right")
sh.wire(P(71, 21), P(108, 21))
sh.junction(*P(71, 21))
c29t, c29b = V("C29", 93, 81, 1)
sh.wire(P(93, 21), c29t)
sh.junction(*P(93, 21))
term(sh, "PRES", *P(99, 87), "right")
sh.wire(c29b, P(93, 87), P(99, 87))
# grid (#00073): R46 to ground, RLY4 COM 1
t, b = V("R46", 135, 96, 2)
sh.wire(ub.pin(7), P(153, GRID))
sh.wire(P(135, GRID), t)
sh.junction(*P(135, GRID))
gnd(b)

# --- PRES1-PRES3 pads grounded by Q7-Q9 (#00098 / J3, #00096 / J2, #00097 / J4) ------------------------
for q, pad, net, x in (("Q7", "PRES1", "J3", 89), ("Q8", "PRES2", "J2", 105), ("Q9", "PRES3", "J4", 121)):
    cx, cy = P(x + 2, 117)
    tx = round(cx + g(4.5), 4)
    f = place_mirrored(sh, sym(q), q, cx, cy, axis="y", value=sh_value(q),
                       ref_at=(tx, round(cy + g(3), 4), 0, None), value_at=(tx, round(cy + g(5), 4), 0, None))
    term(sh, pad, *P(x, 100), "up")
    sh.wire(P(x, 100), f.pin(1))
    gnd(f.pin(2))
    sh.wire(f.pin(3), P(x + 11, 117), P(x + 11, 133))
    sh.wire(P(x + 11, 133), P(x + 15, 133))
    sh.glabel(net, *P(x + 15, 133), 0)

# --- relays -----------------------------------------------------------------------------------------
# pole units turned 270: COM on the left, NC upper right, NO lower right
k4c, k4p1, k4p2 = relay(sh, "RLY4", P(169, 97), P(163, 81), P(163, 73), rot1=270, rot2=270,
                        coil_text=-10)
k5c, k5p1, k5p2 = relay(sh, "RLY5", P(209, 111), P(203, 93), P(203, 83), rot1=270, rot2=270)
sh.wire(c15r, k4p2.pin(6))                              # #00082
sh.wire(P(153, GRID), P(153, 81), k4p1.pin(2))          # #00073
glabel_right(sh, "EQ1", k4p2.pin(7), 6)
sh.wire(k4p2.pin(8), P(191, 75), P(191, 83))            # #00084
sh.wire(P(191, 83), k5p2.pin(6))
sh.wire(k4p1.pin(1), P(187, 83), P(187, 93))            # #00085
sh.wire(P(187, 93), k5p1.pin(2))
term(sh, "MV1", *P(189, 101), "down")                   # #00079
sh.wire(k4p1.pin(3), P(189, 79), P(189, 101))
glabel_right(sh, "EQ2", k5p2.pin(7), 6)
glabel_right(sh, "EQ3", k5p2.pin(8), 6)
term(sh, "MV2", *P(223, 91), "right")                   # #00086
sh.wire(k5p1.pin(3), P(223, 91))
term(sh, "MV3", *P(223, 101), "right")                  # #00090
sh.wire(k5p1.pin(1), P(217, 95), P(217, 101))
sh.wire(P(217, 101), P(223, 101))
# RLY4 coil: pin 5 = #00081, fed from SW3 (D4) or SW2 (D5); D8 across the coil
n81, _ = coil_block(sh, k4c, "D8", None, sw_label=False)
sh.wire(n81, P(143, 91))
sh.junction(*n81)
for d, net, x in (("D4", "SW3", 143), ("D5", "SW2", 151)):
    t, b = V(d, x, 110, "K", text="left" if d == "D4" else None)
    sh.wire(P(x, 91), t)
    sh.wire(b, P(x, 119))
    sh.glabel(net, *P(x, 119), 270)
sh.junction(*P(151, 91))
# RLY5 coil: pin 5 = SW3, D9 across the coil
coil_block(sh, k5c, "D9", "SW3")

# --- heater (unit C): pin 4 = H4, pin 5 = H5, and the heater pads H4 / H5 -------------------------------
for pin, net, xt, d in ((4, "H4", 150, "left"), (5, "H5", 180, "right")):
    p = uh.pin(pin)
    sh.wire(p, down(p, 8))
    sh.glabel(net, *down(p, 8), 270)
    term(sh, net, *P(xt, 35), d)
    sh.wire(down(p, 4), P(xt, 35))
    sh.junction(*down(p, 4))

# --- ground rail, MV0 -------------------------------------------------------------------------------
sh.wire(P(16, GND), P(135, GND))
sh.glabel("PRE-GND", *P(16, GND), 180)
term(sh, "MV0", *P(73, 135), "right")
sh.wire(P(67, GND), P(67, 135), P(73, 135))

sh.text("PDF labels sw2, sw3 = nets SW2, SW3 (Proteus net names are case-insensitive). The pads H4 / H5 "
        "are on the nets H4 / H5.", *P(8, 142))
sh.text("U3 pin 9 has no net (as in Proteus).", *P(8, 145))
sh.save()
print("sheet03: written")
