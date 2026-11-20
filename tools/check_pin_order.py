#!/usr/bin/env python3
"""Pin-order check: the UNMOVED KiCad base footprints with the Proteus renumbering, fitted onto
the IPC pads (playbook Phase 2, step 2). A small residual confirms that the Proteus pin ids sit on
the pads the renumbering says; a residual of a pad pitch or more means the ids are on other pads.

Inline and two-pad parts always fit (a 180 deg turn reverses the pad order), so for them the
orientation of the body marker decides: the fitted KiCad graphics (band, flat side, tab, '+',
pin-1 pad) are drawn over the Proteus silk with --render (reports/pin_order/<refdes>.png) and
were compared by eye (STATUS.md "Phase 2 - pin order").

For the noval socket the KiCad footprint (Valve:Valve_Noval_P) is on a 2.54 mm grid, not on the
Proteus 21.00 mm pitch circle, so the residual is never small; the chirality test compares the
unmirrored fit (KiCad = standard noval numbering, clockwise seen from the pin side = solder side
of a top-mounted socket) with the mirrored one, and also fits an ideal standard noval (10
positions at 36 deg, gap between 9 and 1) on the Proteus pitch circle.

The G5V-2 pad pattern (2 columns x 4 rows) is mirror-symmetric, so two renumberings of the Omron
pads describe the same relay: the one used by tools/gen_footprints.py (Proteus 4/2/3/1 on the Omron
16/13/11/9 column, fits unmirrored) and the column-for-column reading of the Phase 1 symbol mapping
(Proteus 4/2/3/1 on Omron 1/4/6/8, fits only mirrored). Since the design fixes of 2026-11-20
(finding 14) the symbol carries Omron's terminal names (COIL16, COM13, NO9, ...): the Omron numbers
are read from the pin names of lib/tube_preamp.kicad_sym and must fit the IPC pads unmirrored, i.e.
name the same Omron terminals as the footprint renumbering (relay_symbol_map()).

Phase 5 (user decision 2026-11-20: the sockets are on the BOTTOM side): the project footprint
tube_preamp:Valve_Noval_Belton_PCD21.00mm has the standard noval numbering in its own view (fits
the ideal standard noval unmirrored, not mirrored), fits the IPC pads only mirrored (so
check_footprints places it on the bottom), reports/footprint_fit.csv has U1-U3 on the bottom and
every other part on top, and the board has U1-U3 on B.Cu and every other footprint on F.Cu
(bottom_side_noval(), as the pilot's bottom_side_octal()).

Adapted from the power amp pilot (~/dev/tube_power_amp_kicad/tools/check_pin_order.py, octal).

Usage: tools/p2k/bin/kipy tools/check_pin_order.py [--render]   (python3 works without --render;
       --render needs matplotlib, e.g. the system python3)
Exit 1 when a result differs from EXPECT (so a changed footprint or renumbering is noticed).
"""
import csv
import glob
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
os.chdir(ROOT)
from p2k import fpgeom, pcb, sexpr  # noqa: E402
from p2k.footprints import footprint_path  # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.dont_write_bytecode = True   # no stale tools/__pycache__/gen_footprints.pyc (same-second edits)
from gen_footprints import PROJECT  # noqa: E402  (the renumberings checked here are the generator's)

# refdes group -> (KiCad base footprint, Proteus renumbering of the base pads)
NOVALS = "U1 U2 U3"
NOVAL = "tube_preamp:Valve_Noval_Belton_PCD21.00mm"
RELAY_FP = PROJECT["Relay_DPDT_Omron_G5V-2_ProteusPins"]["renumber"]


def relay_symbol_map():
    """{Omron terminal: pin number} from the G5V-2 symbol of the generated library: each pin name is
    Omron's terminal name (COIL / COM / NC / NO + the Omron terminal number), the pin number the
    Proteus id (finding 14)."""
    import re
    lib = sexpr.load(os.path.join("lib", "tube_preamp.kicad_sym"))
    sym = next(s for s in sexpr.find_all(lib, "symbol") if s[1] == "G5V-2")
    out = {}
    for pin in sexpr.walk(sym, "pin"):
        name, num = sexpr.find(pin, "name")[1], sexpr.find(pin, "number")[1]
        m = re.fullmatch(r"(COIL|COM|NC|NO)(\d+)", name)
        assert m, f"G5V-2 pin {num}: name {name!r} is not an Omron terminal name"
        out[m.group(2)] = num
    assert len(out) == 8, out
    return out


RELAY_SYM = relay_symbol_map()
CHECKS = [
    ("Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9", "Package_TO_SOT_THT:TO-92_Inline_Wide",
     PROJECT["TO-92_Inline_P2.03mm"].get("renumber", {})),
    ("D1 D2 D3 D4 D5 D8 D9", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
     PROJECT["D_DO-41_SOD81_P10.16mm_Horizontal_AK"]["renumber"]),
    ("C2", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", PROJECT["CP_Radial_D6.3mm_P2.54mm_PM"]["renumber"]),
    ("C30", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", PROJECT["CP_Radial_D6.3mm_P2.50mm_PM"]["renumber"]),
    ("C28 C33 C34 C35 C36 C37", "Capacitor_THT:CP_Radial_D16.0mm_P7.50mm",
     PROJECT["CP_Radial_D16.0mm_P7.50mm_Pin2Plus"]["renumber"]),
    ("RLY1 RLY2 RLY3 RLY4 RLY5", "Relay_THT:Relay_DPDT_Omron_G5V-2", RELAY_FP),
    ("RLY1 RLY2 RLY3 RLY4 RLY5 (symbol map)", "Relay_THT:Relay_DPDT_Omron_G5V-2", RELAY_SYM),
    (NOVALS, "Valve:Valve_Noval_P", {}),
]
# expected best fit per group: (mirror, residual upper bound mm)
EXPECT = {
    "Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9": (False, 0.51),   # TO-92_Inline_Wide is P2.54, Proteus P2.032
    "D1 D2 D3 D4 D5 D8 D9": (False, 0.01),
    "C2": (False, 0.03),                            # P2.50 vs P2.54
    "C30": (False, 0.01),
    "C28 C33 C34 C35 C36 C37": (False, 0.01),
    "RLY1 RLY2 RLY3 RLY4 RLY5": (False, 0.01),
    "RLY1 RLY2 RLY3 RLY4 RLY5 (symbol map)": (False, 0.01),   # Omron pin names (finding 14); Phase 1: mirrored
    NOVALS: (True, 3.1),           # only the MIRRORED KiCad noval matches the Proteus numbering
}
# Derived project footprints (gen_footprints PROJECT with a base): how far their pads may sit from
# the renumbered base pads (footprint frame, mm). p2k.footprints.derive moves the pads onto the IPC
# positions, so a wrong renumbering would move pads by a pitch while the graphics (band, '+',
# pin-1 mark) stay: this catches it, also for the two-pad parts the fit above cannot tell apart.
MOVE_LIMIT = {
    "R_Axial_DIN0414_L11.9mm_D4.5mm_P19.05mm_Horizontal": 0.64,   # P20.32 -> P19.05
    "C_Rect_L13.0mm_W6.0mm_P9.70mm": 0.16,                        # P10.00 -> P9.70
    "C_Rect_L16.5mm_W7.0mm_P9.70mm": 2.66,                        # P15.00 -> P9.70
    "C_Rect_L24.0mm_W7.0mm_P20.00mm": 1.26,                       # P22.50 -> P20.00
    "C_Disc_D7.5mm_W2.5mm_P5.08mm": 0.05,                         # P5.00 -> P5.08
    "CP_Radial_D6.3mm_P2.54mm_PM": 0.03,                          # P2.50 -> P2.54
    "CP_Radial_D6.3mm_P2.50mm_PM": 0.001,
    "CP_Radial_D16.0mm_P7.50mm_Pin2Plus": 0.001,
    "D_DO-41_SOD81_P10.16mm_Horizontal_AK": 0.001,
    "TO-92_Inline_P2.03mm": 0.51,                                 # P2.54 -> P2.032
    "Relay_DPDT_Omron_G5V-2_ProteusPins": 0.001,
}

# Polarity, stated independently of the generator (Proteus pinouts, STATUS.md "Phase 1
# preparation"): the IPC pin id that must sit on the marked KiCad base pad 1 (square pad + '+' silk
# of CP_Radial, band of DO-41). Two-pad parts fit both ways round, so this is what catches a wrong
# renumbering in gen_footprints.py.
POLARITY = {
    "CP_Radial_D6.3mm_P2.54mm_PM": "+",           # C2 (ELEC-RAD10: pins + / -)
    "CP_Radial_D6.3mm_P2.50mm_PM": "+",           # C30 (22U 100V: pins + / -)
    "CP_Radial_D16.0mm_P7.50mm_Pin2Plus": "2",    # C28, C33-C37 (ELEC D16 R7.5: + = 2, - = 1)
    "D_DO-41_SOD81_P10.16mm_Horizontal_AK": "K",  # D1-D5, D8, D9 (1N4001: A / K)
}

# render (--render) these groups' parts with the fitted KiCad graphics
RENDER = {"Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9", "D1 D2 D3 D4 D5 D8 D9", "C2", "C30", "C28 C33 C34 C35 C36 C37",
          "RLY1 RLY2 RLY3 RLY4 RLY5", NOVALS}


def base_pads(fpid, ren):
    pads = fpgeom.load_footprint(footprint_path(fpid))
    out = []
    for p in pads:
        if p["num"] == "":
            continue   # Valve_Octal centre hole
        q = dict(p)
        q["num"] = ren.get(p["num"], p["num"])
        out.append(q)
    return out


def ideal_noval(r=10.5):
    """Standard noval numbering in KiCad's top view (Y up): 10 positions at 36 deg, counter-clockwise
    from pad 1 (i.e. clockwise seen from the pin / solder side), the empty position between 9 and 1
    at -90 deg."""
    return [{"num": str(k + 1), "x": r * math.cos(math.radians(-54 + 36 * k)),
             "y": r * math.sin(math.radians(-54 + 36 * k)), "w": 4.318, "h": 4.318, "rot": 0.0, "drill": 1.727,
             "kind": "thru_hole", "shape": "circle"} for k in range(9)]


def graphics(fpid):
    """F.SilkS / F.Fab polylines of a footprint (footprint frame, Y up)."""
    node = sexpr.load(footprint_path(fpid))
    lines = []

    def xy(n):
        return float(n[1]), -float(n[2])
    for g in node:
        if not isinstance(g, list) or not g or str(g[0]) not in ("fp_line", "fp_rect", "fp_circle", "fp_arc", "fp_poly"):
            continue
        layer = sexpr.find(g, "layer")
        if layer is None or layer[1] not in ("F.SilkS", "F.Fab"):
            continue
        kind = str(g[0])
        if kind == "fp_line":
            lines.append([xy(sexpr.find(g, "start")), xy(sexpr.find(g, "end"))])
        elif kind == "fp_rect":
            (x0, y0), (x1, y1) = xy(sexpr.find(g, "start")), xy(sexpr.find(g, "end"))
            lines.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)])
        elif kind == "fp_circle":
            (cx, cy), (ex, ey) = xy(sexpr.find(g, "center")), xy(sexpr.find(g, "end"))
            r = math.hypot(ex - cx, ey - cy)
            lines.append([(cx + r * math.cos(t / 20 * math.pi), cy + r * math.sin(t / 20 * math.pi)) for t in range(41)])
        elif kind == "fp_arc":
            a, m, b = xy(sexpr.find(g, "start")), xy(sexpr.find(g, "mid")), xy(sexpr.find(g, "end"))
            lines.append(_arc(a, m, b))
        else:
            pts = [xy(p) for p in sexpr.find(g, "pts")[1:]]
            lines.append(pts + pts[:1])
    return lines


def _arc(a, m, b):
    ax, ay = a
    bx, by = m
    cx, cy = b
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return [a, m, b]
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    r = math.hypot(ax - ux, ay - uy)
    t0, tm, t1 = (math.atan2(p[1] - uy, p[0] - ux) for p in (a, m, b))

    def ccw(s, e):
        return (e - s) % (2 * math.pi)
    if ccw(t0, tm) <= ccw(t0, t1):
        span = ccw(t0, t1)
    else:
        span = -ccw(t1, t0)
    return [(ux + r * math.cos(t0 + span * k / 24), uy + r * math.sin(t0 + span * k / 24)) for k in range(25)]


def to_board(fr, x, y):
    a = math.radians(fr["angle"])
    x = -x if fr["mirror"] else x
    return fr["tx"] + math.cos(a) * x - math.sin(a) * y, fr["ty"] + math.sin(a) * x + math.cos(a) * y


def render(ref, fpid, fr, ipc_pads, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle
    from p2k import gerber
    silk = gerber.parse(glob.glob("source/cadcam/*Top Silk Screen.GBR")[0]).of(gerber.Draw)
    xs = [p["x_mm"] for p in ipc_pads]
    ys = [p["y_mm"] for p in ipc_pads]
    m = 16 if len(ipc_pads) >= 8 and ipc_pads[0]["pad_w"] > 4 else 10
    box = (min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m)
    fig, ax = plt.subplots(figsize=(6, 6))
    for d in silk:
        if box[0] <= d.x1 <= box[1] and box[2] <= d.y1 <= box[3]:
            ax.plot([d.x1, d.x2], [d.y1, d.y2], color="k", lw=1.0)
    for p in ipc_pads:
        ax.add_patch(Circle((p["x_mm"], p["y_mm"]), p["pad_w"] / 2, color="orange", alpha=0.6))
        ax.text(p["x_mm"], p["y_mm"], p["pin"], ha="center", va="center", fontsize=9, color="b")
    for line in graphics(fpid):
        pts = [to_board(fr, x, y) for x, y in line]
        ax.plot([p[0] for p in pts], [p[1] for p in pts], color="r", lw=0.8)
    for num, f, q, _ in fr["pads"]:
        bx, by = to_board(fr, f["x"], f["y"])
        ax.add_patch(Circle((bx, by), 0.35, color="r"))
        if f is fr["pads"][0][1] or num in ("1", "K", "+"):
            ax.text(bx + 0.6, by + 0.6, f"KiCad {num}", fontsize=7, color="r")
    ax.set_title(f"{ref}: black = Proteus silk, orange = IPC pads (pin ids)\n"
                 f"red = unmoved {fpid.split(':')[1]} fitted ({'mirrored, ' if fr['mirror'] else ''}"
                 f"{fr['angle']:g} deg, res {fr['max_res']:.3f} mm)", fontsize=7)
    ax.set_aspect("equal")
    ax.set_xlim(box[0], box[1])
    ax.set_ylim(box[2], box[3])
    fig.savefig(out, dpi=120, bbox_inches="tight")
    plt.close(fig)


def bottom_side_noval(ipc):
    """Phase 5: the noval footprint is the standard noval and U1-U3 are on the bottom side."""
    bad = []
    refs = NOVALS.split()
    fp = fpgeom.load_footprint(footprint_path(NOVAL))
    target = [dict(p, pin=p["num"], x_mm=p["x"], y_mm=p["y"], pad_w=p["w"]) for p in ideal_noval()]   # as IPC pads
    ideal = {m: fpgeom.fit(fp, target, m)["max_res"] for m in (False, True)}
    on_ipc = {m: max(fpgeom.fit(fp, ipc[r], m)["max_res"] for r in refs) for m in (False, True)}
    name = NOVAL.split(":")[1]
    print(f"{'(footprint)':38s} {name + ' vs ideal noval':44s} {ideal[False]:7.3f}{'':11s} "
          f"{ideal[True]:7.3f}{'':11s}  {'unmirrored' if ideal[False] < ideal[True] else 'mirrored'}")
    print(f"{NOVALS:38s} {name + ' (project)':44s} {on_ipc[False]:7.3f}{'':11s} "
          f"{on_ipc[True]:7.3f}{'':11s}  {'mirrored = bottom side' if on_ipc[True] < on_ipc[False] else 'unmirrored'}")
    if not (ideal[False] < 0.02 < ideal[True]):
        bad.append(f"{name}: expected the standard noval numbering in the footprint's own view")
    if not (on_ipc[True] < 0.02 < on_ipc[False]):
        bad.append(f"{name}: expected to fit the IPC pads only mirrored (bottom side)")
    with open("reports/footprint_fit.csv") as f:
        rows = list(csv.DictReader(l for l in f if not l.startswith("# ")))
    wrong = [r["refdes"] for r in rows if (r["side"] == "bottom") != (r["refdes"] in refs)]
    if wrong:
        bad.append(f"reports/footprint_fit.csv: wrong side for {wrong} (bottom = exactly {refs})")
    layers = {}
    board = os.path.relpath(pcb.board_file())   # kicad/tube_preamp.kicad_pcb (P2K_PCB overrides)
    for node in sexpr.find_all(sexpr.load(board), "footprint"):
        ref = next((p[2] for p in sexpr.find_all(node, "property") if p[1] == "Reference"), "")
        layers[ref] = sexpr.find(node, "layer")[1]
    wrong = sorted(r for r, l in layers.items() if l != ("B.Cu" if r in refs else "F.Cu"))
    if wrong or not set(refs) <= set(layers):
        bad.append(f"{board}: wrong layer for {wrong or refs} (B.Cu = exactly {refs})")
    else:
        print(f"{'':38s} footprint_fit.csv and board: U1-U3 bottom (B.Cu), the other {len(layers) - 3} footprints top")
    return bad


def main():
    do_render = "--render" in sys.argv[1:]
    ipc = fpgeom.ipc_pads_by_refdes()
    bad = []
    print(f"{'parts':38s} {'KiCad base (unmoved)':44s} {'unmirrored':>18s} {'mirrored':>18s}  best")
    for refs, fpid, ren in CHECKS:
        fp = base_pads(fpid, ren)
        worst = {False: (0.0, None), True: (0.0, None)}
        for ref in refs.split(" (")[0].split():
            for mir in (False, True):
                r = fpgeom.fit(fp, ipc[ref], mir)
                if r["missing"] or r["extra"] or r["count_diff"]:
                    bad.append(f"{ref}: pad numbers differ from {fpid}: {r['missing']} {r['extra']} {r['count_diff']}")
                if worst[mir][1] is None or r["max_res"] > worst[mir][0]:
                    worst[mir] = (r["max_res"], r)
            if do_render and refs in RENDER:
                os.makedirs("reports/pin_order", exist_ok=True)
                best = min((fpgeom.fit(fp, ipc[ref], m) for m in (False, True)), key=lambda r: r["max_res"])
                render(ref, fpid, best, ipc[ref], f"reports/pin_order/{ref}.png")
        u, m = worst[False], worst[True]
        best = u[0] <= m[0]
        best_mir = not best
        cell = lambda w: f"{w[0]:7.3f} @{w[1]['angle']:5g}"  # noqa: E731
        print(f"{refs:38s} {fpid:44s} {cell(u):>18s} {cell(m):>18s}  {'mirrored' if best_mir else 'unmirrored'}")
        want_mir, lim = EXPECT[refs]
        res = m[0] if best_mir else u[0]
        if best_mir != want_mir or res > lim:
            bad.append(f"{refs}: best fit {'mirrored' if best_mir else 'unmirrored'} {res:.3f} mm, expected "
                       f"{'mirrored' if want_mir else 'unmirrored'} <= {lim}")
    # derived project footprints: pads where the renumbered base has them
    from p2k.board import config
    proj = config().PROJECT
    for name, spec in sorted(PROJECT.items()):
        if not spec.get("base"):
            continue
        basep = {p["num"]: p for p in base_pads(spec["base"], spec.get("renumber", {}))}
        mine = {p["num"]: p for p in fpgeom.load_footprint(footprint_path(f"{proj}:{name}")) if p["num"] != ""}
        if set(basep) != set(mine):
            bad.append(f"{name}: pad numbers {sorted(mine)} != renumbered base {sorted(basep)}")
            continue
        move = max(math.hypot(mine[n]["x"] - basep[n]["x"], mine[n]["y"] - basep[n]["y"]) for n in mine)
        lim = MOVE_LIMIT.get(name)
        print(f"{'derived':38s} {name:52s} pads moved {move:6.3f} mm (limit {lim})")
        if lim is None or move > lim:
            bad.append(f"{name}: pads moved {move:.3f} mm from the renumbered base {spec['base']} (limit {lim})")
    for name, want in sorted(POLARITY.items()):
        got = PROJECT[name].get("renumber", {}).get("1", "1")
        print(f"{'polarity':38s} {name:52s} KiCad pad 1 (marked) = {got!r} (expected {want!r})")
        if got != want:
            bad.append(f"{name}: the marked KiCad pad 1 is pin {got!r}, expected {want!r}")
    # ideal standard noval on the Proteus pitch circle
    nov = {}
    for mir in (False, True):
        nov[mir] = max(fpgeom.fit(ideal_noval(), ipc[r], mir)["max_res"] for r in NOVALS.split())
    print(f"{NOVALS:38s} {'ideal standard noval, PCD 21.00 mm':44s} {nov[False]:7.3f}{'':11s} "
          f"{nov[True]:7.3f}{'':11s}  {'mirrored' if nov[True] < nov[False] else 'unmirrored'}")
    if not (nov[True] < 0.02 < nov[False]):
        bad.append("ideal noval: expected only the mirrored standard noval to fit")
    bad += bottom_side_noval(ipc)
    for b in bad:
        print("check_pin_order: ERROR " + b)
    print("check_pin_order: " + ("FAILED" if bad else "OK (results as recorded in STATUS.md)"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
