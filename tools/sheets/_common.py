"""Helpers for the per-sheet transcription scripts (tools/sheets/sheetNN.py).

Adapted from the power amp pilot (~/dev/tube_power_amp_kicad/tools/sheets/_common.py): part map
lookups, term(), P(), place_mirrored(); plus tube() / relay() that place every unit of the
multi-unit symbols (STATUS.md "Transcription rules").

The generic helpers come from p2k.sheetkit (grid g(), sheet(), left/right/up/down,
glabel_*/label_*, power_at, bus_group, flagged_power, vert2, horiz2, terminal); board helpers
below. Each sheet script starts with
    from _common import *  # noqa: F401,F403
"""
import csv
import os
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(TOOLS, "p2k"))  # proteus2kicad
from p2k.sch_builder import Sheet  # noqa: E402,F401
from p2k.sheetkit import *  # noqa: E402,F401,F403
from p2k.sheetkit import _two_pin_rot  # noqa: E402

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
    """Proteus TERMINAL part as sheetkit.terminal does it (connection point (x, y), circle
    pointing in `direction`, texts horizontal), but with the symbol and value of the part map
    (PIN, value TERMINAL). sheetkit.terminal always places value "PIN" and justifies the texts of
    left / right terminals over the circle (pilot p2k candidates 3, 7)."""
    rot = {"up": 0, "left": 90, "down": 180, "right": 270}[direction]
    kw = {}
    if direction == "right":     # KiCad mirrors justification for rot 270
        kw = dict(ref_at=(x + 5.08, y - 1.27, 90, "left"), value_at=(x + 5.08, y + 1.27, 90, "left"))
    elif direction == "left":
        kw = dict(ref_at=(x - 5.08, y - 1.27, 270, "right"), value_at=(x - 5.08, y + 1.27, 270, "right"))
    return sh.place(sym(ref), ref, x, y, rot, value=sh_value(ref), **kw)


# --- PDF coordinates ---------------------------------------------------------------------------------
# The Proteus PDF pages rendered at 200 dpi (build/tmp/pdf/hi-N.png) have 0.127 mm pixels, so
# 10 px = one 1.27 mm grid unit. P(px/10, py/10) puts a point of the render on the A3 KiCad sheet
# (same scale, shifted by OX/OY grid units), which keeps the layout close to the PDF.
OX, OY = 40, 30


def P(x, y):
    """Sheet point (mm, on the 1.27 mm grid) of PDF render position (x, y) in units of 10 px."""
    return (g(x + OX), g(y + OY))


# --- mirrored symbols --------------------------------------------------------------------------------
def place_mirrored(sh, name, ref, x, y, axis="x", **kw):
    """sh.place() at rotation 0 with the symbol mirrored: axis 'x' = about the X axis (top and
    bottom swapped), 'y' = about the Y axis (left and right swapped). p2k.sch_builder.Sheet.place has
    no mirror option (p2k candidate), so the node it wrote gets a (mirror ...) entry here and the
    returned pin points are mirrored about the symbol origin. Pass ref_at / value_at for the texts
    (KiCad keeps field positions absolute)."""
    from p2k.sexpr import Sym, find
    p = sh.place(name, ref, x, y, 0, **kw)
    unit = kw.get("unit", 1)
    for node in sh.tree:
        if (isinstance(node, list) and node and str(node[0]) == "symbol" and find(node, "unit")[1] == unit
                and any(c[1:3] == ["Reference", ref] for c in node if isinstance(c, list) and str(c[0]) == "property")):
            node.insert(next(i for i, c in enumerate(node) if isinstance(c, list) and str(c[0]) == "at") + 1,
                        [Sym("mirror"), Sym(axis)])
            break
    else:
        raise KeyError(ref)
    for num, (px, py) in list(p.pins.items()):
        p.pins[num] = (px, round(2 * y - py, 4)) if axis == "x" else (round(2 * x - px, 4), py)
    return p


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
        ub = place_mirrored(sh, sym(ref), ref, *b, axis="y", unit=2, value=val, **texts(*b, 1, 0))
    else:
        ub = sh.place(sym(ref), ref, *b, rot_b, unit=2, value=val, **texts(*b, 1, rot_b))
    uh = sh.place(sym(ref), ref, *heater, rot_h, unit=3, value=val)
    sh.no_connect(*uh.pin("9"))
    return ua, ub, uh


def relay(sh, ref, coil, pole1, pole2, rot_coil=0, rot1=0, rot2=0, coil_text=-12):
    """All three units of a G5V-2 relay (RLY1-RLY5): unit 1 = coil (Proteus DC1 = 4 on Omron COIL16,
    DC2 = 5 on Omron COIL1; unrotated: pin 5 at the top) at `coil`, unit 2 = Proteus pole 1 (COM1 = 2,
    NC1 = 3, AC1/NO = 1 on Omron COM13 / NC11 / NO9) at `pole1`, unit 3 = Proteus pole 2 (COM2 = 6,
    NC2 = 7, AC2/NO = 8 on Omron COM4 / NC6 / NO8) at `pole2` (finding 14). Texts (centred, horizontal): beside the coil (coil_text grid units from
    its centre) and above each pole. Returns (coil, pole1, pole2) Placed objects."""
    out = []
    for u, (x, y), rot in ((1, coil, rot_coil), (2, pole1, rot1), (3, pole2, rot2)):
        fa = _FIELD_ANGLE[rot % 360]
        if u == 1:
            tx, ty1, ty2 = round(x + g(coil_text), 4), round(y - g(1), 4), round(y + g(1), 4)
        else:
            tx, ty1, ty2 = round(x - g(2), 4), round(y - g(4.5), 4), round(y - g(3), 4)
        out.append(sh.place(sym(ref), ref, x, y, rot, unit=u, value=sh_value(ref),
                            ref_at=(tx, ty1, fa, None), value_at=(tx, ty2, fa, None)))
    return tuple(out)


# --- relay coil with its diode -------------------------------------------------------------------------
def coil_block(sh, coil, dref, sw, xd=7, xsw=-6, ylab=6, sw_label=True):
    """Diode `dref` across a relay coil (unit 1 placed with relay(), pin 5 at the top) and the
    labels below it: cathode on coil pin 5 (the switch net `sw`, taken xsw grid units to the side
    and down), anode on coil pin 4 = H4 (finding 4: the anode is on H4). xd = column of the diode
    relative to the coil. sw_label=False: no label on the pin 5 node (RLY4: net #00081).
    Returns (pin 5 node, pin 4 node)."""
    top, bot = coil.pin("5"), coil.pin("4")
    assert top[1] < bot[1] and top[0] == bot[0], "coil pin 5 must be at the top"
    xdm = round(top[0] + g(xd), 4)
    _, dt, db = vert2(sh, sym(dref), dref, xdm, round((top[1] + bot[1]) / 2, 4), sh_value(dref), top="K")
    sh.wire(top, (xdm, top[1]), dt)
    sh.wire(bot, (xdm, bot[1]), db)
    yl = round(bot[1] + g(ylab), 4)
    sh.wire(bot, (bot[0], yl))
    sh.glabel("H4", bot[0], yl, 270)
    sh.junction(*bot)
    if sw_label:
        xs = round(top[0] + g(xsw), 4)
        sh.wire(top, (xs, top[1]), (xs, yl))
        sh.glabel(sw, xs, yl, 270)
        sh.junction(*top)
    return top, bot


# --- horizontal capacitors ---------------------------------------------------------------------------
def hcap(sh, ref, x, y, left=1):
    """Horizontal capacitor (symbol / value from the part map) with pin `left` on the left; the
    reference goes above and the value below the plates (the default text placement of
    sch_builder for horizontal two-pin parts is made for resistors and overlaps the plates).
    Returns (left_point, right_point)."""
    rot = _two_pin_rot(sym(ref), left, "left")
    fa = {0: 0, 90: 270, 180: 0, 270: 90}[rot]
    p = sh.place(sym(ref), ref, x, y, rot, value=sh_value(ref),
                 ref_at=(x, round(y - 3.81, 4), fa, None), value_at=(x, round(y + 3.81, 4), fa, None))
    a, b = sorted(p.pins.values())
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
