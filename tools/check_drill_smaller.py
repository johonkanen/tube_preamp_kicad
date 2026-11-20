#!/usr/bin/env python3
"""Phase 5: the KiCad drills smaller than the Proteus drill are exactly the 80 decided holes.

p2k ipc356_diff and p2k gerber_roundtrip accept a smaller KiCad drill by the *pair* of diameters in
p2k_config.py DRILL_SMALLER ((Proteus mm, KiCad mm)), not by pad: any other pad with the same pair
(e.g. a 0.762 mm Proteus hole on a footprint whose drill became 0.75 mm) would be accepted silently
and only change a count in their output (STATUS.md "p2k candidates"). This board-local check closes
that: it reads the Proteus IPC-D-356A file with its own small parser (no p2k code), finds the board
pad or via at every record position (0.05 mm) and requires

  - every record to have a plated board hole at its position,
  - the pads whose board drill is smaller than the Proteus drill (0.005 mm) to be exactly EXPECTED
    (user decision 2026-11-20: RLY1-RLY5 40 holes, C1/C5/C7/C10 8, the 14 Orange Drops 28,
    C4/C14 4 = 80),
  - every pair in DRILL_SMALLER to be used by EXPECTED, and no other pair.

Ported in Phase 5 from tube_pi_fxloop_kicad/tools/check_drill_smaller.py (same code, this board's
EXPECTED).

Usage: tools/p2k/bin/kipy tools/check_drill_smaller.py [board.kicad_pcb]
"""
import math
import os
import re
import sys

import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True
sys.path.insert(0, ROOT)
import p2k_config as cfg  # noqa: E402

# (Proteus drill, KiCad drill) -> pads, as decided (STATUS.md "Decisions", 2026-11-20)
ORANGE_DROPS = "C8 C11 C12 C13 C16 C17 C19 C20 C21 C23 C24 C25 C27 C29".split()
EXPECTED = {
    (1.143, 0.7): {(f"RLY{r}", str(n)) for r in range(1, 6) for n in range(1, 9)},
    (1.143, 1.0): {(c, p) for c in ("C1", "C5", "C7", "C10") for p in ("1", "2")},
    (1.143, 1.1): {(c, p) for c in ORANGE_DROPS for p in ("1", "2")},
    (0.762, 0.75): {(c, p) for c in ("C4", "C14") for p in ("1", "2")},
}
POS_TOL, DRILL_TOL = 0.05, 0.005


def ipc_records(path):
    """(x, y, drill mm, plated) of every 317 record (SI units: 0.001 mm), IPC frame (Y up)."""
    out = []
    for line in open(path, encoding="latin-1"):
        if not line.startswith("317"):
            continue
        m = re.search(r"D(\d{4})([PU])A\d\dX([+-]\d+)Y([+-]\d+)X\d+", line)
        if not m:
            raise SystemExit(f"check_drill_smaller: cannot read the IPC record {line.rstrip()!r}")
        out.append((int(m[3]) / 1000, int(m[4]) / 1000, int(m[1]) / 1000, m[2] == "P"))
    return out


def main():
    board_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "kicad", f"{cfg.PROJECT}.kicad_pcb")
    board = pcbnew.LoadBoard(board_path)
    mm = pcbnew.ToMM
    holes = []    # (x, y, drill, plated, name)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetDrillSize().x > 0:
                p = pad.GetPosition()
                holes.append((mm(p.x), -mm(p.y), mm(pad.GetDrillSize().x),
                              pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH, (fp.GetReference(), pad.GetNumber())))
    for t in board.GetTracks():
        if t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            holes.append((mm(p.x), -mm(p.y), mm(t.GetDrill()), True, ("via", f"{mm(p.x):.3f},{-mm(p.y):.3f}")))
    recs = ipc_records(os.path.join(ROOT, cfg.IPC))
    errors, smaller, used = [], {}, set()
    for x, y, d, plated in recs:
        near = [h for h in holes if math.hypot(h[0] - x, h[1] - y) <= POS_TOL]
        if len(near) != 1:
            errors.append(f"IPC record at ({x}, {y}): {len(near)} board holes within {POS_TOL} mm")
            continue
        h = near[0]
        used.add(h[4])
        if h[3] != plated:
            errors.append(f"{h[4][0]}-{h[4][1]}: plated {plated} in Proteus, {h[3]} on the board")
        if h[2] < d - DRILL_TOL:
            smaller[h[4]] = (d, round(h[2], 4))
    for h in holes:
        if h[4] not in used:
            errors.append(f"board hole {h[4][0]}-{h[4][1]} at ({h[0]:.3f}, {h[1]:.3f}): no IPC record")
    want = {pad: pair for pair, pads in EXPECTED.items() for pad in pads}
    for pad in sorted(set(smaller) - set(want)):
        errors.append(f"{pad[0]}-{pad[1]}: board drill {smaller[pad][1]} < Proteus {smaller[pad][0]}, not a decided hole")
    for pad in sorted(set(want) - set(smaller)):
        errors.append(f"{pad[0]}-{pad[1]}: expected a board drill smaller than Proteus {want[pad]}, it is not")
    for pad in sorted(set(want) & set(smaller)):
        if any(abs(a - b) > DRILL_TOL for a, b in zip(want[pad], smaller[pad])):
            errors.append(f"{pad[0]}-{pad[1]}: drills Proteus / board {smaller[pad]}, decided {want[pad]}")
    conf = set(getattr(cfg, "DRILL_SMALLER", {}))
    if conf != set(EXPECTED):
        errors.append(f"p2k_config.DRILL_SMALLER pairs {sorted(conf)} != the decided pairs {sorted(EXPECTED)}")
    for e in errors:
        print("check_drill_smaller:", e)
    counts = ", ".join(f"{len(pads)}x {a}->{b}" for (a, b), pads in sorted(EXPECTED.items()))
    print(f"check_drill_smaller: {len(recs)} IPC records, {len(holes)} board holes; smaller board drills: "
          f"{len(smaller)} (decided {sum(len(v) for v in EXPECTED.values())}: {counts})")
    print("check_drill_smaller: " + ("OK" if not errors else f"FAILED ({len(errors)} errors)"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
