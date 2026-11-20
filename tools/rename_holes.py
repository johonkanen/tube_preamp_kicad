#!/usr/bin/env python3
"""Board step 1b of tools/make_pcb.sh: rename the mounting holes H1-H13 to H101-H113.

p2k.build_pcb names the board-only hole footprints H1, H2, ... (hard-coded). This board has two
schematic terminals called H4 and H5 (the heater fly-lead pads, on nets H4 / H5), so holes H4 / H5
would share their reference: p2k.pcb.ipc_to_kicad_nets keys pads by (reference, pad number) and
reports "IPC net H4 spans KiCad nets ['', 'H4']", and the DRC parity would see duplicate
references. The holes keep their build_pcb order and an H prefix (Phase 4 ipc356_diff recognises
plated board-only holes by the reference pattern H<n>): build_pcb's hole n becomes H(100 + n).
(build_pcb numbers top row first, left to right; README's mechanical table uses another order,
STATUS.md "Phase 3" gives the mapping.) STATUS.md p2k candidate 18.

Run with tools/p2k/bin/kipy right after p2k.build_pcb (board file from P2K_PCB like the p2k steps).
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "p2k"))
import pcbnew  # noqa: E402
from p2k import pcb  # noqa: E402

OFFSET = 100


def main():
    pcbnew.KIID.SeedGenerator(3101)  # reproducible UUIDs (no items are created; seeded anyway)
    c = pcb.cfg()
    board = pcbnew.LoadBoard(pcb.board_file())
    holes = [fp for fp in board.Footprints()
             if fp.GetFPIDAsString() == c.HOLE_FOOTPRINT and re.fullmatch(r"H\d+", fp.GetReference())]
    for fp in holes:
        fp.SetReference(f"H{OFFSET + int(fp.GetReference()[1:])}")
    refs = [fp.GetReference() for fp in board.Footprints()]
    dup = sorted({r for r in refs if refs.count(r) > 1})
    pcbnew.SaveBoard(pcb.board_file(), board)
    print(f"rename_holes: {len(holes)} mounting holes renamed H1.. -> H{OFFSET + 1}..")
    if dup:
        print(f"rename_holes: duplicate references remain: {' '.join(dup)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
