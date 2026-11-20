"""Helpers for the per-sheet transcription scripts (tools/sheets/sheetNN.py).

Adapted from the power amp pilot (~/dev/tube_power_amp_kicad/tools/sheets/_common.py): part map
lookups, term(), P(); plus tube() (all three units of a 12AX7, STATUS.md "Transcription rules") and
relay() / coil_block() (the one-unit G5V-2 with its coil diode).

The generic helpers come from p2k.sheetkit (grid g(), sheet(), left/right/up/down,
glabel_*/label_*, power_at, bus_group, flagged_power, vert2, horiz2, terminal); board helpers
below. Each sheet script starts with
    from _common import *  # noqa: F401,F403
"""
import csv
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # tools/generate/sheets/ -> tools
sys.path.insert(0, os.path.join(TOOLS, "p2k"))  # proteus2kicad
from p2k.sch_builder import Sheet  # noqa: E402,F401
from p2k.sheetkit import *  # noqa: E402,F401,F403

_PART_MAP = None


def part(ref):
    """Row of lib/part_map.csv for a KiCad refdes (keys refdes, sheet, lib_id, value, ...)."""
    global _PART_MAP
    if _PART_MAP is None:
        with open(os.path.join(os.path.dirname(TOOLS), "lib", "part_map.csv"), newline="", encoding="utf-8") as f:
            _PART_MAP = {r["refdes"]: r for r in csv.DictReader(l for l in f if not l.startswith("#"))}
    return _PART_MAP[ref]


def sh_value(ref):
    """Value of a refdes from lib/part_map.csv."""
    return part(ref)["value"]


def sym(ref):
    """Symbol name (lib_id without the library nickname) of a refdes from lib/part_map.csv."""
    return part(ref)["lib_id"].partition(":")[2]


def term(sh, ref, x, y, direction="up"):
    """Proteus TERMINAL part: sheetkit.terminal with the symbol and value of the part map (PIN,
    value TERMINAL) and the texts beside the circle, away from the wire (justify="away")."""
    return terminal(sh, ref, x, y, direction, symbol=sym(ref), value=sh_value(ref), justify="away")


# --- PDF coordinates ---------------------------------------------------------------------------------
# The Proteus PDF pages rendered at 200 dpi (build/tmp/pdf/hi-N.png) have 0.127 mm pixels, so
# 10 px = one 1.27 mm grid unit. P(px/10, py/10) puts a point of the render on the A3 KiCad sheet
# (same scale, shifted by OX/OY grid units), which keeps the layout close to the PDF.
OX, OY = 40, 30


def P(x, y):
    """Sheet point (mm, on the 1.27 mm grid) of PDF render position (x, y) in units of 10 px."""
    return (g(x + OX), g(y + OY))


# --- multi-unit symbols ------------------------------------------------------------------------------
_FIELD_ANGLE = {0: 0, 90: 270, 180: 0, 270: 90}    # field angle that reads horizontally on a rotated symbol


def tube(sh, ref, a, b, heater, rot_a=0, rot_b=0, rot_h=0, mirror_b=False):
    """All three units of a 12AX7 (U1-U3): unit 1 = triode A (A1 G1 K1 = pins 1 2 3) at `a`, unit 2 =
    triode B (A2 G2 K2 = 6 7 8) at `b`, unit 3 = heater (H1 H2 = 4 5) at `heater`; pin 9 (HCT, N/C
    in Proteus) gets a no-connect flag here. mirror_b: triode B mirrored about the Y axis (grid and
    cathode on the right, as the right half of the Proteus dual-triode symbol; rot_b must be 0).
    Returns (unit1, unit2, unit3) Placed objects (.pin(n))."""
    val = sh_value(ref)
    def texts(x, y, side, rot):          # reference and value beside the top of the envelope
        tx = round(x + side * g(6), 4)
        fa = _FIELD_ANGLE[rot % 360]
        return dict(ref_at=(tx, round(y - g(8), 4), fa, None), value_at=(tx, round(y - g(6.5), 4), fa, None))

    ua = sh.place(sym(ref), ref, *a, rot_a, unit=1, value=val, **texts(*a, -1, rot_a))
    if mirror_b:
        ub = sh.place(sym(ref), ref, *b, 0, unit=2, value=val, mirror="y", **texts(*b, 1, 0))
    else:
        ub = sh.place(sym(ref), ref, *b, rot_b, unit=2, value=val, **texts(*b, 1, rot_b))
    uh = sh.place(sym(ref), ref, *heater, rot_h, unit=3, value=val)
    sh.no_connect(*uh.pin("9"))
    return ua, ub, uh


def relay(sh, ref, centre):
    """A G5V-2 relay (RLY1-RLY5, KiCad's one-unit Relay:G5V-2 with the Omron pin numbers, IPC_PIN_IDS)
    turned 270: coil on top (pin 16 = Proteus 4 on the left, pin 1 = Proteus 5 on the right, 8 grid
    units above `centre`), then the Omron pole 1 (COM 4 at `centre` on the left, NC 6 upper right, NO 8
    lower right; Proteus pole 2 = 6 / 7 / 8) and, 8 grid units lower, the Omron pole 2 (COM 13, NC 11,
    NO 9; Proteus pole 1 = 2 / 3 / 1). The contacts sit where the pole units of the former split symbol
    were. Reference and value centred below the symbol. Returns the Placed object (.pin(n), Omron n)."""
    x, y = centre
    fa = _FIELD_ANGLE[270]
    return sh.place(sym(ref), ref, x, y, 270, value=sh_value(ref),
                    ref_at=(x, round(y + g(13), 4), fa, None), value_at=(x, round(y + g(14.5), 4), fa, None))


# --- relay coil with its diode -------------------------------------------------------------------------
def coil_block(sh, k, dref, sw, sw_label=True):
    """Diode `dref` across the coil of relay `k` (placed with relay()), drawn above it: the coil pins
    (16 left, 1 right) go up 6 grid units to the diode row (clear of the body), cathode on pin 1 (the switch net `sw`,
    global label pointing up) and anode on pin 16 = H4 (finding 4: the anode is on H4; global label
    pointing up). sw_label=False: no label on the pin 1 node (RLY4: net #00081).
    Returns (pin 1 node, pin 16 node) on the diode row."""
    right, left = k.pin("1"), k.pin("16")
    assert right[1] == left[1] and left[0] < right[0], "relay coil must be horizontal, pin 16 on the left"
    yd = round(left[1] - g(6), 4)
    xm = round((left[0] + right[0]) / 2, 4)
    _, da, dk = horiz2(sh, sym(dref), dref, xm, yd, sh_value(dref), left="A", text="above")
    nl, nr = (left[0], yd), (right[0], yd)
    sh.wire(left, nl, da)
    sh.wire(right, nr, dk)
    for node, net, show in ((nl, "H4", True), (nr, sw, sw_label)):
        if show:
            top = (node[0], round(yd - g(2), 4))
            sh.wire(node, top)
            sh.glabel(net, *top, 90)
            sh.junction(*node)
    return nr, nl


# --- horizontal capacitors ---------------------------------------------------------------------------
def hcap(sh, ref, x, y, left=1):
    """Horizontal capacitor (symbol / value from the part map) with pin `left` on the left; the
    reference 3.81 mm above and the value 3.81 mm below the plates (text_gap; the default text
    placement for horizontal two-pin parts is made for resistors and overlaps the plates).
    Returns (left_point, right_point)."""
    _, a, b = horiz2(sh, sym(ref), ref, x, y, sh_value(ref), left=left, text_gap=3.81)
    return a, b


# --- sheet 4: one tone stack ---------------------------------------------------------------------------
def tone_stack(sh, n, x0, y0, eq, c_hi, r_top, c_lo1, c_lo2, r_mid, r_bot, c_gnd, xc=16, xeq=-8, xw=-18):
    """One of the three identical tone stacks of sheet 4. (x0, y0) = PDF render position (10 px
    units) of the EQn input node above r_top. eq = net of the input (global label); c_hi (250p) to
    HInO; r_top (220k) down to LOnX / c_lo1 (1N); c_lo1 and c_lo2 (4N7) join at LOnW and r_mid (220K) to
    HInW; LOnO / c_lo2 / r_bot (4k7) to the ground node; c_gnd (2N2) from the ground node to HInX.
    xc = column of c_hi / c_gnd, xeq / xw = columns of the EQn label and the LOnW terminal (offsets
    from x0). Returns the ground node point (bottom of r_bot)."""
    def Q(dx, dy):
        return P(x0 + dx, y0 + dy)

    def cap(ref, dx, dy):
        return hcap(sh, ref, *Q(dx, dy), left=1)

    # EQn input, c_hi to HInO
    sh.glabel(eq, *Q(xeq, 0), 180)
    l, r = cap(c_hi, xc, 0)
    sh.wire(Q(xeq, 0), l)
    sh.wire(r, Q(40, 0))
    term(sh, f"HI{n}O", *Q(40, 0), "right")
    sh.junction(*Q(0, 0))
    # r_top to the LOnX node, c_lo1
    _, t, b = vert2(sh, sym(r_top), r_top, *Q(0, 7), sh_value(r_top), top=2)
    sh.wire(Q(0, 0), t)
    sh.wire(b, Q(0, 14))
    term(sh, f"LO{n}X", *Q(-8, 14), "left")
    l, r = cap(c_lo1, 12, 14)
    sh.wire(Q(-8, 14), l)
    sh.junction(*Q(0, 14))
    sh.wire(r, Q(22, 14), Q(22, 26))
    # LOnW node, r_mid to HInW
    term(sh, f"LO{n}W", *Q(xw, 20), "left")
    _, l, r2 = horiz2(sh, sym(r_mid), r_mid, *Q(29, 20), sh_value(r_mid), left=1)
    sh.wire(Q(xw, 20), l)
    sh.junction(*Q(22, 20))
    sh.wire(r2, Q(40, 20))
    term(sh, f"HI{n}W", *Q(40, 20), "right")
    # LOnO node, c_lo2, r_bot
    term(sh, f"LO{n}O", *Q(-8, 26), "left")
    l, r = cap(c_lo2, 12, 26)
    sh.wire(Q(-8, 26), l)
    sh.wire(r, Q(22, 26))
    sh.junction(*Q(0, 26))
    _, t, b = vert2(sh, sym(r_bot), r_bot, *Q(0, 33), sh_value(r_bot), top=1)
    sh.wire(Q(0, 26), t)
    sh.wire(b, Q(0, 40))
    # ground node, c_gnd to HInX
    l, r = cap(c_gnd, xc, 40)
    sh.wire(Q(0, 40), l)
    sh.wire(r, Q(40, 40))
    term(sh, f"HI{n}X", *Q(40, 40), "right")
    return Q(0, 40)
