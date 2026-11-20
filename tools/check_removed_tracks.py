#!/usr/bin/env python3
"""Design fixes 2026-11-20: the removed Proteus track pieces are exactly the decided ones.

User decision 2026-11-20 (STATUS.md "Design fixes 2026-11-20"): the dangling stub of finding 16 and
the zero-length / very short pieces of finding 20 are not built (p2k_config.py REMOVED_TRACKS).
gerber_to_tracks and gerber_roundtrip only require every REMOVED_TRACKS entry to match a Proteus
draw; this board-local check pins the decision independently of the config and of the
make_pcb.sh --check byte compare (removed when generation stopped, 2026-11-20; this check never
regenerated anything and works on the hand-edited board):

  - REMOVED_TRACKS lists exactly EXPECTED (no entry missing, none added),
  - every EXPECTED piece is a Conductor draw in the Proteus copper gerber of its layer,
  - the board has no track segment on those endpoints (either direction, 0.001 mm).

Usage: python3 tools/check_removed_tracks.py [board.kicad_pcb]
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
sys.dont_write_bytecode = True
os.chdir(ROOT)
from p2k import gerber, sexpr  # noqa: E402
from p2k import pcb as bc  # noqa: E402
from p2k.board import config  # noqa: E402

# (layer, x1, y1, x2, y2), IPC / Gerber frame (Y up), as the Proteus draws (STATUS.md findings 16, 20)
EXPECTED = {
    ("B.Cu", 88.9, -0.762, 88.9, -0.6985),              # finding 16: dangling stub, RLY4-13 track
    ("F.Cu", -61.087, -1.905, -61.087, -1.905),         # finding 20: zero length
    ("F.Cu", -61.722, -22.225, -61.722, -22.225),       # finding 20: zero length
    ("F.Cu", -139.7635, -16.5735, -139.7635, -16.4465),
    ("F.Cu", -130.81, -38.735, -130.8735, -38.7985),
    ("F.Cu", -60.96, -1.905, -61.087, -1.905),
    ("B.Cu", -18.87074, 24.13, -19.05, 24.13),
    ("B.Cu", -114.427, -18.415, -114.3, -18.415),
    ("B.Cu", -43.942, -6.858, -43.942, -6.985),
}
TOL = 0.001


def same(key, layer, x1, y1, x2, y2):
    lay, a1, b1, a2, b2 = key
    if lay != layer:
        return False
    return any(math.hypot(p[0] - x1, p[1] - y1) <= TOL and math.hypot(q[0] - x2, q[1] - y2) <= TOL
               for p, q in (((a1, b1), (a2, b2)), ((a2, b2), (a1, b1))))


def main():
    board = sys.argv[1] if len(sys.argv) > 1 else os.path.relpath(bc.board_file())
    bad = []
    listed = set(getattr(config(), "REMOVED_TRACKS", {}) or {})
    if listed != EXPECTED:
        bad.append(f"REMOVED_TRACKS != the decided pieces: missing {sorted(EXPECTED - listed)}, "
                   f"extra {sorted(listed - EXPECTED)}")
    draws = []
    for gname, layer, _user in config().COPPER:
        g = gerber.parse(bc.gerber_path(gname))
        draws += [(layer, d.x1, d.y1, d.x2, d.y2) for d in g.of(gerber.Draw) if d.ap.function == "Conductor"]
    for key in sorted(EXPECTED):
        n = sum(same(key, *d) for d in draws)
        if n != 1:
            bad.append(f"{key}: {n} Proteus Conductor draws (expected 1)")
    segs = 0
    for node in sexpr.find_all(sexpr.load(board), "segment"):
        segs += 1
        (sx, sy), (ex, ey) = sexpr.find(node, "start")[1:3], sexpr.find(node, "end")[1:3]
        layer = sexpr.find(node, "layer")[1]
        for key in EXPECTED:
            if same(key, layer, float(sx), -float(sy), float(ex), -float(ey)):   # KiCad (x, y) = (x, -y)
                bad.append(f"{board}: track {layer} ({sx}, {sy}) -> ({ex}, {ey}) is the removed piece {key}")
    print(f"check_removed_tracks: {len(EXPECTED)} decided pieces, {len(listed)} in REMOVED_TRACKS, "
          f"all Proteus draws, none of {segs} board tracks")
    for b in bad:
        print("check_removed_tracks: ERROR " + b)
    print("check_removed_tracks: " + ("FAILED" if bad else "OK"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
