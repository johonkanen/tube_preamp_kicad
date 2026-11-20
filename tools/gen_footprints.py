#!/usr/bin/env python3
"""Footprint assignment and the project footprint library of the preamp (stdlib only).

Writes (through the shared generator tools/p2k/p2k/footprints.py)
  lib/footprint_map.csv        refdes -> footprint for all 163 parts of lib/part_map.csv
  lib/tube_preamp.pretty/      project footprints: derived from KiCad library footprints (pads
                               renumbered to the Proteus ids, pad centres moved onto the Proteus
                               positions) or built from the IPC-D-356A pads where KiCad has nothing
  kicad/fp-lib-table           registers the project library (board-local: footprints.run does
                               not write it; STATUS.md "p2k candidates")

Usage: python3 tools/gen_footprints.py [--check]      (needs the KiCad AppImage mount)

This file holds what is decided for this board: RULES (symbol + IPC pad pattern -> footprint)
and PROJECT (the project footprint specs); the rule syntax and the spec keys are documented in
tools/p2k/p2k/footprints.py. Pad numbers always equal the IPC pin ids. Adapted from the power amp
pilot (~/dev/tube_power_amp_kicad/tools/gen_footprints.py: same 2010 Proteus library; the fly-lead
terminal, DO-41, TO-92 P2.03, 2 W resistor, 22n Xicon and mounting-hole specs are the pilot's).

Pad sizes: p2k_config.py FOOTPRINT_PAD_SIZES = "kicad" (KiCad library pads and drills; the
footprints built from the IPC pads - noval socket, fly-lead terminal - have the Proteus pads).
tools/p2k check_footprints verifies every footprint against the IPC pads (residual < 0.05 mm per
pad) and reports the pad size / drill differences.
"""
import glob
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))  # proteus2kicad
from p2k import footprints, gerber, sexpr  # noqa: E402

P = "tube_preamp:"
PIN1_DOT = (-0.45, 1.35, 0.2)   # TO-92 pin-1 dot: x, y (KiCad footprint frame, Y down), radius mm

# (symbol, conditions, footprint, note). Conditions: n = pad count, tht, span (mm, +-0.02),
# pad = (w, h) of the IPC pads, drill, package / device (lib/part_map.csv columns), refdes.
# One rule per Proteus package (2010 package name in the note).
RULES = [
    # --- resistors
    ("R", dict(package="RES40", span=10.16, pad=(1.778, 1.778), drill=0.762),
     "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal", "RES40: 1/4 W axial, P10.16"),
    ("R", dict(package="2W METAL FILM RESISTOR", span=19.05, pad=(2.286, 2.286), drill=1.016),
     P + "R_Axial_DIN0414_L11.9mm_D4.5mm_P19.05mm_Horizontal", "2W METAL FILM RESISTOR: 2 W axial, P19.05"),
    # --- film / ceramic capacitors
    ("C", dict(package="22N XICON", span=9.70, pad=(2.54, 2.54), drill=1.143),
     P + "C_Rect_L13.0mm_W6.0mm_P9.70mm", "22N XICON: film box 13 x 6 mm, P9.70"),
    ("C", dict(package="1N ORANGE DROP", span=9.70, pad=(2.54, 2.54), drill=1.143),
     P + "C_Rect_L16.5mm_W7.0mm_P9.70mm", "1N ORANGE DROP: film box (Proteus silk 15.1 x 6.7 mm), P9.70"),
    ("C", dict(package="2N2 ORANGE DROP", span=9.70, pad=(2.54, 2.54), drill=1.143),
     P + "C_Rect_L16.5mm_W7.0mm_P9.70mm", "2N2 ORANGE DROP: film box (Proteus silk 15.1 x 6.7 mm), P9.70"),
    ("C", dict(package="3N3 ORANGE DROP", span=9.70, pad=(2.54, 2.54), drill=1.143),
     P + "C_Rect_L16.5mm_W7.0mm_P9.70mm", "3N3 ORANGE DROP: film box (Proteus silk 15.1 x 6.7 mm), P9.70"),
    ("C", dict(package="4N7 ORANGE DROP", span=9.70, pad=(2.54, 2.54), drill=1.143),
     P + "C_Rect_L16.5mm_W7.0mm_P9.70mm", "4N7 ORANGE DROP: film box (Proteus silk 15.1 x 6.7 mm), P9.70"),
    ("C", dict(package="100N XICON", span=20.0, pad=(2.54, 2.54), drill=1.143),
     P + "C_Rect_L24.0mm_W7.0mm_P20.00mm", "100N XICON: film box (Proteus silk 23.1 x 6.0 mm), P20.00"),
    ("C", dict(package="MMK 2.5*7.2", span=5.0, pad=(1.778, 1.778), drill=0.762),
     "Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2", "MMK 2.5*7.2: film box 7.2 x 2.5 mm, P5.00"),
    ("C", dict(package="MMK J04", span=5.0, pad=(1.778, 1.778), drill=0.762),
     "Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm", "MMK J04: film box 7.2 x 5.0 mm, P5.00"),
    ("C", dict(package="CAP20", span=5.08, pad=(1.778, 1.778), drill=0.762),
     P + "C_Disc_D7.5mm_W2.5mm_P5.08mm", "CAP20: ceramic disc, P5.08"),
    # --- electrolytics
    ("C_Polarized", dict(package="ELEC-RAD10", span=2.54, pad=(2.032, 2.032), drill=0.762),
     P + "CP_Radial_D6.3mm_P2.54mm_PM", "ELEC-RAD10: 6.3 mm radial electrolytic, P2.54, pads +/-"),
    ("C_Polarized", dict(package="22U 100V", span=2.5, pad=(2.032, 2.032), drill=0.762),
     P + "CP_Radial_D6.3mm_P2.50mm_PM", "22U 100V: 6.3 mm radial electrolytic, P2.50, pads +/-"),
    ("C_Polarized_12", dict(package="ELEC D16 R7.5", span=7.5, pad=(2.54, 2.54), drill=1.143),
     P + "CP_Radial_D16.0mm_P7.50mm_Pin2Plus", "ELEC D16 R7.5: 16 mm radial electrolytic, P7.50, pad 2 = +"),
    # --- diodes
    ("D", dict(package="DO41", span=10.16), P + "D_DO-41_SOD81_P10.16mm_Horizontal_AK", "DO41: pads A/K"),
    # --- JFETs
    ("J112", dict(package="TO92", span=4.064, pad=(1.524, 1.524), drill=0.762), P + "TO-92_Inline_P2.03mm",
     "TO92: inline, 1=D 2=S 3=G (J112), P2.032"),
    # --- relays
    ("G5V-2", dict(package="G5V-2(HI)", n=8, pad=(2.54, 2.54), drill=1.143),
     P + "Relay_DPDT_Omron_G5V-2_ProteusPins", "G5V-2(HI): Omron G5V-2, pads = Proteus pin ids"),
    # --- tubes
    ("12AX7", dict(package="9-PIN BELTON NOVAL", n=9, pad=(4.318, 4.318), drill=1.727),
     P + "Valve_Noval_Belton_PCD21.00mm", "9-PIN BELTON NOVAL: noval socket, Proteus pads and pin ids"),
    # --- terminals (fly leads)
    ("PIN", dict(package="PIN", n=1, pad=(3.048, 3.048), drill=1.524),
     P + "FlyLead_Pad_D3.048mm_Drill1.524mm", "PIN: fly-lead terminal pad"),
]


def noval_body():
    """The noval socket outline of the Proteus Top Assembly layer (a 26.4 x 25.4 mm rectangle
    around the socket): the closed 4-segment loop around U1's pads, board coordinates."""
    path = glob.glob(os.path.join(ROOT, "source", "cadcam", "*Top Assembly.GBR"))[0]
    draws = gerber.parse(path).of(gerber.Draw)
    cx, cy = -156.100, 6.168   # U1: centre of the 21.00 mm pitch circle (reference/ipc356_pads.csv)
    pts = []
    for d in draws:
        if math.hypot(d.x2 - d.x1, d.y2 - d.y1) > 20 and \
                all(math.hypot(x - cx, y - cy) < 19 for x, y in ((d.x1, d.y1), (d.x2, d.y2))):
            pts.append((round(d.x1, 3), round(d.y1, 3)))
    if len(pts) != 4 or any(abs(abs(x - cx) - 13.22) > 0.01 or abs(abs(y - cy) - 12.70) > 0.01 for x, y in pts):
        raise SystemExit(f"gen_footprints: U1 assembly outline not found as expected: {pts}")
    return sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


# Project footprints (spec keys: see p2k.footprints). `ipc` = refdes whose IPC pads give the
# pad centres. All parts are THT and on the top side (Proteus Top Assembly).
PROJECT = {
    "R_Axial_DIN0414_L11.9mm_D4.5mm_P19.05mm_Horizontal": dict(
        base="Resistor_THT:R_Axial_DIN0414_L11.9mm_D4.5mm_P20.32mm_Horizontal", ipc="R6",
        descr="2 W axial metal film resistor DIN0414, Proteus pads 19.05 mm apart"),
    # 22n Xicon film: Proteus silk 12.8 x 6.0 mm, pads 9.70 mm apart (as the power amp)
    "C_Rect_L13.0mm_W6.0mm_P9.70mm": dict(
        base="Capacitor_THT:C_Rect_L13.0mm_W6.0mm_P10.00mm_FKS3_FKP3_MKS4", ipc="C1",
        descr="Film capacitor box 13 x 6 mm (22n Xicon), Proteus pads 9.70 mm apart"),
    # Orange Drop film: Proteus silk 15.1 x 6.7 mm, pads 9.70 mm apart; KiCad's nearest box is
    # 16.5 x 7.0 mm (P15.00), pads moved inwards
    "C_Rect_L16.5mm_W7.0mm_P9.70mm": dict(
        base="Capacitor_THT:C_Rect_L16.5mm_W7.0mm_P15.00mm_MKT", ipc="C8",
        descr="Film capacitor box 16.5 x 7 mm (Orange Drop), Proteus pads 9.70 mm apart"),
    # 100n Xicon film: Proteus silk 23.1 x 6.0 mm, pads 20.00 mm apart; KiCad box 24 x 7 mm (P22.50)
    "C_Rect_L24.0mm_W7.0mm_P20.00mm": dict(
        base="Capacitor_THT:C_Rect_L24.0mm_W7.0mm_P22.50mm_MKT", ipc="C15",
        descr="Film capacitor box 24 x 7 mm (100n Xicon), Proteus pads 20.00 mm apart"),
    # 250p ceramic (Proteus CAP20: ellipse about 8 x 2.7 mm), pads 5.08 mm apart
    "C_Disc_D7.5mm_W2.5mm_P5.08mm": dict(
        base="Capacitor_THT:C_Disc_D7.5mm_W2.5mm_P5.00mm", ipc="C18",
        descr="Ceramic disc capacitor D7.5 W2.5, Proteus pads 5.08 mm apart"),
    # electrolytics: KiCad pad 1 (square, '+' silk) = Proteus pin '+' (C2, C30) / pin 2 (C28, C33-C37)
    "CP_Radial_D6.3mm_P2.54mm_PM": dict(
        base="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", renumber={"1": "+", "2": "-"}, ipc="C2",
        descr="6.3 mm radial electrolytic, pads + (KiCad pad 1) / -, Proteus pads 2.54 mm apart"),
    "CP_Radial_D6.3mm_P2.50mm_PM": dict(
        base="Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", renumber={"1": "+", "2": "-"}, ipc="C30",
        descr="6.3 mm radial electrolytic P2.50, pads + (KiCad pad 1) / -"),
    "CP_Radial_D16.0mm_P7.50mm_Pin2Plus": dict(
        base="Capacitor_THT:CP_Radial_D16.0mm_P7.50mm", renumber={"1": "2", "2": "1"}, ipc="C28",
        descr="16 mm radial electrolytic P7.50, pad 2 = + (KiCad pad 1), pad 1 = - (Proteus ELEC D16 R7.5)"),
    # DO-41: KiCad pad 1 = cathode (band)
    "D_DO-41_SOD81_P10.16mm_Horizontal_AK": dict(
        base="Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", renumber={"1": "K", "2": "A"}, ipc="D1",
        descr="DO-41 diode P10.16, pads K (KiCad pad 1, band) / A"),
    # TO-92 at the Proteus 2.032 mm (80 mil) pitch: KiCad has 1.27 (Inline) and 2.54 (Inline_Wide).
    # J112 (TO-92): 1 = D, 2 = S, 3 = G = the KiCad pad numbers, no renumbering.
    # pad_shapes (board-local key, see derive_with_pad_shapes): pad 1 ROUND at the KiCad size 1.5 mm
    # instead of KiCad's square pin-1 pad (user decision 2026-11-20, option (a): the square corner
    # was 0.122 mm from the source track of Q4 / Q6; round 0.433). Pin 1 is then marked by the
    # pin1_dot (board-local key): KiCad's TO-92 outline is left-right symmetric, so the square pad
    # was the only pin-1 mark; a filled dot on F.SilkS / F.Fab left of pad 1 on the flat side
    # replaces it (same key value and position as tube_pi_fxloop_kicad, STATUS.md "Phase 3").
    "TO-92_Inline_P2.03mm": dict(
        base="Package_TO_SOT_THT:TO-92_Inline_Wide", ipc="Q1", pad_shapes={"1": "circle"},
        pin1_dot=PIN1_DOT,
        descr="TO-92 inline, pads 1-3 2.032 mm apart (Proteus TO92), round pad 1, pin-1 dot"),
    # Omron G5V-2: Proteus G5V-2(HI) pin ids on the Omron pads. The Proteus coil pin 4 / pole-1
    # column (4, 2, 3, 1) sits on the Omron 16 / 13 / 11 / 9 column (STATUS.md "Phase 2": the pattern
    # and the relay are mirror-symmetric, so this is the renumbering that fits without a mirror).
    "Relay_DPDT_Omron_G5V-2_ProteusPins": dict(
        base="Relay_THT:Relay_DPDT_Omron_G5V-2",
        renumber={"16": "4", "13": "2", "11": "3", "9": "1", "1": "5", "4": "6", "6": "7", "8": "8"},
        ipc="RLY1",
        descr="Omron G5V-2 DPDT relay, pads = Proteus G5V-2(HI) ids: 4/5 coil, 2/3/1 COM/NC/NO pole 1, "
              "6/7/8 COM/NC/NO pole 2"),
    # Noval socket built from the IPC pads: KiCad's Valve_Noval_P is on a 2.54 mm grid, Proteus has
    # a 21.00 mm pitch circle (10 positions at 36 deg, 1-9 with the gap between 9 and 1). Pad ids as
    # Proteus (see STATUS.md "Phase 2": numbering vs the noval standard).
    "Valve_Noval_Belton_PCD21.00mm": dict(
        ipc="U1", body_poly=noval_body(),
        descr="Noval tube socket (Proteus 9-PIN BELTON NOVAL): 9 pads 4.318 mm / drill 1.727 on a "
              "21.00 mm pitch circle, pad 9 without a net, body = the Proteus assembly outline"),
    "FlyLead_Pad_D3.048mm_Drill1.524mm": dict(
        ipc="GTR_IN", descr="Fly-lead terminal (Proteus PIN): one 3.048 mm pad, drill 1.524"),
    # Board-only (no symbol; placed by p2k.build_pcb at the 13 IPC 'hole' records)
    "MountingHole_3.0mm_PTH_Pad6.35mm": dict(
        board_only=True, pad=(6.35, 3.0), plated=True,
        descr="Plated 3.0 mm mounting hole with a 6.35 mm pad on both layers, no net"),
}

FP_LIB_TABLE = """(fp_lib_table
\t(version 7)
\t(lib (name "tube_preamp")(type "KiCad")(uri "${KIPRJMOD}/../lib/tube_preamp.pretty")(options "")(descr "Project footprints, pad numbers = IPC pin ids (tools/gen_footprints.py)"))
)
"""


_derive = footprints.derive


def derive_with_pad_shapes(name, spec, ipc):
    """p2k.footprints.derive plus two board-local spec keys (STATUS.md "p2k candidates" 22):
    `pad_shapes` ({pad number: shape}; the shared derive() has no pad-shape override; only the shape
    changes, size / drill / position stay as derive() made them) and `pin1_dot` ((x, y, r): a filled
    dot on F.SilkS and F.Fab, placed before pad 1). Guard: a pad made round must be exactly one
    `rect` pad in the base (the KiCad square pin-1 pad), so a library change is noticed."""
    node = _derive(name, spec, ipc)
    shapes = dict(spec.get("pad_shapes", {}))
    for num, shape in shapes.items():
        pads = [p for p in sexpr.find_all(node, "pad") if str(p[1]) == num]
        if len(pads) != 1 or str(pads[0][3]) != "rect":
            raise SystemExit(f"gen_footprints: {name}: expected one rect pad {num} in the base, got "
                             f"{[str(p[3]) for p in pads]}")
        size = sexpr.find(pads[0], "size")
        if shape == "circle" and float(size[1]) != float(size[2]):
            raise SystemExit(f"gen_footprints: {name} pad {num}: circle needs a square size, not {size[1:]}")
        pads[0][3] = sexpr.Sym(shape)
    if spec.get("pin1_dot"):
        x, y, r = spec["pin1_dot"]
        pad1 = [p for p in sexpr.find_all(node, "pad") if str(p[1]) == "1"][0]
        i = node.index(pad1)
        node[i:i] = [_dot(x, y, r, "F.SilkS", 0.12), _dot(x, y, r, "F.Fab", 0.1)]
    return node


def _dot(x, y, r, layer, width):
    Sym = sexpr.Sym
    return [Sym("fp_circle"), [Sym("center"), x, y], [Sym("end"), round(x + r, 4), y],
            [Sym("stroke"), [Sym("width"), width], [Sym("type"), Sym("solid")]], [Sym("fill"), Sym("yes")],
            [Sym("layer"), layer]]


footprints.derive = derive_with_pad_shapes   # build_library() calls the module-level derive


def fp_lib_table(check):
    path = os.path.join(ROOT, "kicad", "fp-lib-table")
    cur = open(path).read() if os.path.exists(path) else None
    if cur == FP_LIB_TABLE:
        return True
    if check:
        print("gen_footprints: out of date: kicad/fp-lib-table")
        return False
    with open(path, "w") as f:
        f.write(FP_LIB_TABLE)
    print("gen_footprints: wrote kicad/fp-lib-table")
    return True


if __name__ == "__main__":
    ok = fp_lib_table("--check" in sys.argv[1:])
    try:
        footprints.run(RULES, PROJECT)
    except SystemExit as e:
        sys.exit(e.code if ok else 1)
