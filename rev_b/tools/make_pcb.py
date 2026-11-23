#!/usr/bin/env python3
"""Start the rev B board: rev_b/kicad/tube_preamp_revb.kicad_pcb from the schematic netlist.

Run with KiCad's python:  tools/p2k/bin/kipy rev_b/tools/make_pcb.py   (from the repo root)

What it does (layout decisions: rev_b/README.md, "Layout"):
- outline, mounting holes and noval positions of the built `etunen` board (rev A
  kicad/tube_preamp.kicad_pcb, same frame: chassis x = board x + 198.73, chassis y = board y +
  42.35; the top edge y = -26.175 is the front);
- 2 copper layers, net classes and the HV clearance rules (kicad_pro + kicad_dru);
- every schematic part with its footprint, nets and schematic link (Update PCB from Schematic
  matches them by UUID);
- the parts whose position is an interface or mechanical decision placed: V1-V3 (solder side, as
  rev A), H101-H113, J504-J506, J401, J501, J502, J102, J101, J507, J503;
- every other part parked below the board, grouped by sheet, for placement;
- the placement zones and keep-outs drawn on User.Comments.

It writes a new board each time: run it only before the placement starts (it refuses to overwrite
a board that has tracks unless --force).
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
RB = os.path.dirname(HERE)
REPO = os.path.dirname(RB)
PROJECT = "tube_preamp_revb"
K = os.path.join(RB, "kicad")
PCB = os.path.join(K, PROJECT + ".kicad_pcb")
PRO = os.path.join(K, PROJECT + ".kicad_pro")
SCH = os.path.join(K, PROJECT + ".kicad_sch")
REVA = os.path.join(REPO, "kicad", "tube_preamp.kicad_pcb")
KICAD_CLI = os.path.join(REPO, "tools", "p2k", "bin", "kicad-cli")
STOCK = os.path.join(os.environ.get("KICAD_MOUNT") or open(f"/tmp/p2k_kicad_mount.{os.getuid()}").read().strip(),
                     "share", "kicad", "footprints")

# Board frame (rev A): x -195.357 .. 187.433, y -26.175 (front) .. 45.730 (rear).
X0, X1, Y0, Y1 = -195.357, 187.433, -26.175, 45.730
FRONT_STRIP = 15.0      # mm: no part taller than 5 mm (interfaces.md 12.2)
HEADER_SETBACK = 20.0   # mm: J504-J506 body front edge behind the front edge (interfaces.md 12.2)

# Net classes: by the DC voltage a net reaches (normal operation, start-up, a short).
# Names without the sheet path; each matches the global net and the sheet-local one ("*/NAME").
HV = ["BP_RAW", "CS", "ZT", "GF", "GP", "SRC", "QB", "BP", "BP_DRN", "DRN_A", "DRN_B", "FB_A", "FB_B",
      "RF_A", "RF_B", "BP1", "BP2", "BP3", "BP4", "BL2", "BL3"]
MV = ["P1", "P2", "P3", "P4", "P5", "Z1", "Z2", "BLEED_M", "VDIV_M"]
V90 = ["KCF", "GCB", "VB90"]          # the CF's cathode and grid bias, about 90 V: 0.6 mm (IPC B2 51-100 V)
HEATER = ["HTR1", "HTR2", "HREF"]

DRU = """(version 1)
# Rev B preamp clearance rules (tools/make_pcb.py; tube_amplifier_kicad review N57, IPC-2221B B2,
# uncoated): HV = nets that reach 300-430 V, MV = 100-300 V (plates, the zener string, the dividers),
# V90 = about 90 V (net class clearance 0.6 mm). Unconnected pads (a relay's open NC contact) are
# left out. Functional insulation only.
(rule "HV to LV"
  (condition "A.NetClass == 'HV' && B.NetClass != 'HV' && B.NetClass != 'MV' && B.NetClass != 'V90' && B.NetName != 'unconnected-*'")
  (constraint clearance (min 2.5mm)))
(rule "HV to MV or V90"
  (condition "A.NetClass == 'HV' && (B.NetClass == 'MV' || B.NetClass == 'V90')")
  (constraint clearance (min 1.25mm)))
(rule "MV to LV"
  (condition "A.NetClass == 'MV' && B.NetClass != 'HV' && B.NetClass != 'MV' && B.NetName != 'unconnected-*'")
  (constraint clearance (min 1.25mm)))
# K201 / K204: the G6K-2F-Y's coil pad 1 (+5 V) is 2.4 mm from contact pad 2 (B+ ~300-330 V); the
# relay's own coil-contact rating covers it (-Y: 3.2 mm inside the part). Accepted exception.
(rule "K201 K204 coil to contact"
  (condition "A.NetClass == 'HV' && B.NetClass != 'HV' && B.NetName != 'unconnected-*' && ((A.memberOfFootprint('K201') && B.memberOfFootprint('K201')) || (A.memberOfFootprint('K204') && B.memberOfFootprint('K204')))")
  (constraint clearance (min 2.3mm)))
# C501 (2.2 uF 450 V, 8 mm, 3.5 mm lead pitch): 1.9 mm between its own pads, GF (up to 390 V) to GND.
# The part's lead pitch sets it; accepted exception for its own pads only.
(rule "C501 own pads"
  (condition "A.memberOfFootprint('C501') && B.memberOfFootprint('C501')")
  (constraint clearance (min 1.8mm)))
# The front panel's pot pins end about 2.2 mm in front of the board's front edge (main session
# 2026-11-22), and the chassis is all round: HV copper 2.5 mm, MV 1.25 mm from every board edge.
(rule "HV to board edge"
  (condition "A.NetClass == 'HV'")
  (constraint edge_clearance (min 2.5mm)))
(rule "MV to board edge"
  (condition "A.NetClass == 'MV'")
  (constraint edge_clearance (min 1.25mm)))
"""


def stock(lib):
    return os.path.normpath(os.path.join(STOCK, lib + ".pretty"))


def netlist():
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "n.xml")
        subprocess.run([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", out, SCH],
                       check=True, capture_output=True)
        return ET.parse(out)


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def seg(board, x0, y0, x1, y1, layer, w=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pt(x0, y0))
    s.SetEnd(pt(x1, y1))
    s.SetLayer(layer)
    s.SetWidth(mm(w))
    board.Add(s)


def box(board, x0, y0, x1, y1, layer, w=0.1):
    for a, b, c, d in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
        seg(board, a, b, c, d, layer, w)


def note(board, s, x, y, size=1.5, layer=pcbnew.Cmts_User):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(s)
    t.SetPosition(pt(x, y))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(mm(size), mm(size)))
    t.SetTextThickness(mm(size * 0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
    board.Add(t)


def keepout_circle(board, x, y, r):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.B_Cu)
    z.SetLayerSet(ls)
    o = z.Outline()
    o.NewOutline()
    import math
    for i in range(32):
        a = 2 * math.pi * i / 32
        o.Append(mm(x + r * math.cos(a)), mm(y + r * math.sin(a)))
    board.Add(z)


def keepout_rect(board, x0, y0, x1, y1):
    """Rule area on both copper layers: no tracks, vias, pads, zone fill or footprints."""
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    for f in (z.SetDoNotAllowTracks, z.SetDoNotAllowVias, z.SetDoNotAllowZoneFills, z.SetDoNotAllowPads,
              z.SetDoNotAllowFootprints):
        f(True)
    ls = pcbnew.LSET()
    ls.AddLayer(pcbnew.F_Cu)
    ls.AddLayer(pcbnew.B_Cu)
    z.SetLayerSet(ls)
    o = z.Outline()
    o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(mm(x), mm(y))
    board.Add(z)


def project_settings():
    pro = json.load(open(PRO))
    pro.setdefault("board", {})
    classes = [
        {"name": "Default", "clearance": 0.2, "track_width": 0.3, "via_diameter": 0.8, "via_drill": 0.4,
         "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647},
        {"name": "HV", "clearance": 0.3, "track_width": 0.5, "via_diameter": 1.0, "via_drill": 0.5,
         "pcb_color": "rgba(194, 0, 0, 1.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 0},
        {"name": "MV", "clearance": 0.3, "track_width": 0.4, "via_diameter": 0.9, "via_drill": 0.45,
         "pcb_color": "rgba(194, 118, 0, 1.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 1},
        {"name": "V90", "clearance": 0.6, "track_width": 0.3, "via_diameter": 0.8, "via_drill": 0.4,
         "pcb_color": "rgba(150, 150, 0, 1.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 3},
        {"name": "HEATER", "clearance": 0.6, "track_width": 1.2, "via_diameter": 1.2, "via_drill": 0.6,
         "pcb_color": "rgba(0, 120, 194, 1.000)", "schematic_color": "rgba(0, 0, 0, 0.000)", "priority": 2},
    ]
    pats = [{"netclass": c, "pattern": p} for c, names in (("HV", HV), ("MV", MV), ("V90", V90), ("HEATER", HEATER))
            for n in names for p in (n, "*/" + n)]
    pro["net_settings"] = {"classes": classes, "meta": {"version": 4}, "net_colors": None,
                           "netclass_assignments": None, "netclass_patterns": pats}
    json.dump(pro, open(PRO, "w"), indent=2)
    open(os.path.join(K, PROJECT + ".kicad_dru"), "w").write(DRU)


def load_fp(lib_id):
    lib, name = lib_id.split(":")
    path = os.path.join(RB, "lib", PROJECT + ".pretty") if lib == PROJECT else stock(lib)
    f = pcbnew.FootprintLoad(path, name)
    if f is None:
        raise SystemExit(f"footprint {lib_id} not found in {path}")
    f.SetFPID(pcbnew.LIB_ID(lib, name))
    return f


def crtyd(f):
    c = f.GetCourtyard(pcbnew.F_CrtYd if not f.IsFlipped() else pcbnew.B_CrtYd)
    b = c.BBox() if c.OutlineCount() else f.GetBoundingBox(False)
    return [pcbnew.ToMM(v) for v in (b.GetLeft(), b.GetTop(), b.GetRight(), b.GetBottom())]


def place_box(f, rot, cx=None, top=None, left=None, right=None, cy=None, bottom=None):
    """Rotate, then move so the courtyard box meets the given edges / centres."""
    f.SetOrientationDegrees(rot)
    l, t, r, b = crtyd(f)
    dx = (cx - (l + r) / 2) if cx is not None else (left - l) if left is not None else (right - r) if right is not None else 0
    dy = (cy - (t + b) / 2) if cy is not None else (top - t) if top is not None else (bottom - b) if bottom is not None else 0
    p = f.GetPosition()
    f.SetPosition(pcbnew.VECTOR2I(p.x + mm(dx), p.y + mm(dy)))


def main():
    if os.path.exists(PCB) and "--force" not in sys.argv:
        b = pcbnew.LoadBoard(PCB)
        if len(b.GetTracks()):
            raise SystemExit(f"{PCB} has tracks: not overwritten (use --force)")
    project_settings()
    reva = pcbnew.LoadBoard(REVA)
    rev_a = {f.GetReference(): f for f in reva.GetFootprints()}
    board = pcbnew.NewBoard(PCB)
    board.SetCopperLayerCount(2)
    ds = board.GetDesignSettings()
    ds.SetBoardThickness(mm(1.6))
    ds.m_TrackMinWidth = mm(0.2)
    ds.m_MinClearance = mm(0.2)
    ds.m_ViasMinSize = mm(0.6)
    ds.m_MinThroughDrill = mm(0.3)
    ds.m_CopperEdgeClearance = mm(0.5)
    box(board, X0, Y0, X1, Y1, pcbnew.Edge_Cuts, 0.1)

    t = netlist()
    nets = {}
    for n in t.iter("net"):
        name = n.get("name")
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        for nd in n.iter("node"):
            nets[(nd.get("ref"), nd.get("pin"))] = ni

    parked = {}
    fps = {}
    for c in t.iter("comp"):
        ref = c.get("ref")
        f = load_fp(c.findtext("footprint"))
        f.SetReference(ref)
        f.SetValue(c.findtext("value"))
        sym = {fld.get("name"): fld.text or "" for fld in c.iter("field")}   # the parity check compares them
        for fd in f.GetFields():
            if fd.GetName() in ("Datasheet", "Description"):
                fd.SetText(sym.get(fd.GetName(), ""))
        sp = c.find("sheetpath")
        f.SetPath(pcbnew.KIID_PATH(sp.get("tstamps") + c.findtext("tstamps")))
        f.SetSheetname(sp.get("names"))
        f.SetSheetfile((c.find("property[@name='Sheetfile']").get("value")))
        for p in f.Pads():
            ni = nets.get((ref, p.GetNumber()))
            if ni is not None:
                p.SetNet(ni)
        board.Add(f)
        fps[ref] = f
        parked.setdefault(sp.get("names"), []).append(f)

    # --- fixed parts -------------------------------------------------------------------------
    fixed = set()
    for v, a in (("V1", "U1"), ("V2", "U2"), ("V3", "U3")):     # rev A U1-U3: solder side, 180 deg
        f, ra = fps[v], rev_a[a]
        f.SetPosition(ra.GetPosition())
        f.Flip(ra.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        f.SetOrientation(ra.GetOrientation())
        fixed.add(v)
    for ref, ra in rev_a.items():                               # mounting holes H101-H113
        if re.fullmatch(r"H1\d\d", ref):
            h = load_fp("MountingHole:MountingHole_3.2mm_M3")
            h.SetReference(ref)
            h.SetValue("M3 (3.2 NPTH)")
            h.SetPosition(ra.GetPosition())
            h.SetBoardOnly(True)
            board.Add(h)
            p = ra.GetPosition()
            keepout_circle(board, pcbnew.ToMM(p.x), pcbnew.ToMM(p.y), 4.0)
    hdr_top = Y0 + HEADER_SETBACK
    for ref, cx in (("J504", -112.0), ("J505", -62.0), ("J506", 25.0)):
        place_box(fps[ref], 90, cx=cx, top=hdr_top)
        fixed.add(ref)
    place_box(fps["J401"], 0, right=X1 - 1.5, top=Y0 + 11.0)     # behind H102's keep-out
    place_box(fps["J501"], 0, right=X1 - 10.0, bottom=Y1 - 1.0)
    place_box(fps["J502"], 0, cx=98.0, bottom=Y1 - 1.0)
    place_box(fps["J503"], 90, cx=116.0, bottom=Y1 - 2.0)
    place_box(fps["J507"], 0, cx=132.0, bottom=Y1 - 1.0)
    place_box(fps["J101"], 90, left=X0 + 2.0, cy=0.0)
    place_box(fps["J102"], 0, left=X0 + 2.0, cy=16.0)
    fixed |= {"J401", "J501", "J502", "J503", "J507", "J101", "J102"}

    # --- parked parts: below the board, one block per sheet ---------------------------------
    y = Y1 + 12.0
    for sheet in sorted(parked):
        items = sorted((f for f in parked[sheet] if f.GetReference() not in fixed),
                       key=lambda f: (str(f.GetFPID().GetLibItemName()), f.GetReference()))
        if not items:
            continue
        note(board, f"Sheet {sheet.strip('/')}: to place", X0, y - 4.0, 2.0)
        x, rowh = X0, 0.0
        for f in items:
            f.SetOrientationDegrees(0)
            l, t_, r, b = crtyd(f)
            w, h = r - l, b - t_
            if x + w > X1:
                x, y = X0, y + rowh + 4.0
                rowh = 0.0
            place_box(f, 0, left=x, top=y)
            x += w + 4.0
            rowh = max(rowh, h)
        y += rowh + 12.0

    # --- zones and keep-outs on User.Comments -------------------------------------------------
    C = pcbnew.Cmts_User
    box(board, X0, Y0, X1, Y0 + FRONT_STRIP, C, 0.2)
    note(board, "Front strip 15 mm: SMD passives / SOT-23 only, nothing taller than 5 mm (interfaces.md 12.2)",
         -120.0, Y0 + 2.5, 1.2)
    note(board, f"J504-J506: body front edge {HEADER_SETBACK:.0f} mm behind the front edge; clean, crunch, lead",
         -120.0, Y0 + 5.0, 1.2)
    # Front panel pot pins (upper row, treble / presence) reach to about 2 mm from the front edge over
    # chassis x 180-390 (front panel fourth pass): nothing within 4 mm of the edge there, so the edge
    # can also be pulled back 2 mm later if the chassis measurement says so (main session 2026-11-23).
    # It stops at chassis x 377.7, before H102's courtyard (the last pins, presence at x 371, end at about 376).
    keepout_rect(board, 180.0 - 198.73, Y0, 179.0, Y0 + 4.0)
    note(board, "Keep-out 4 mm: pot pins (chassis x 180-390)", 60.0, Y0 + 7.5, 1.0)
    # Between the front strip and each pot header the front panel's ribbon bends up into the header
    # (front panel board, third pass): parts there at most 20 mm (J504 / J505) / 38 mm (J506) tall.
    for ref, hmax in (("J504", 20), ("J505", 20), ("J506", 38)):
        l, t_, r, b_ = crtyd(fps[ref])
        box(board, l, Y0 + FRONT_STRIP, r, t_, C, 0.15)
        note(board, f"<= {hmax} mm (ribbon bend)", l + 1.0, Y0 + FRONT_STRIP + 2.5, 1.0)
    zones = [
        ("Regulator (430 V, HV rules):\nQ502 drain pour >= 6 cm2 per side, F and B, stitched;\n"
         "Q503 on F in a cut-out over the B-side drain copper;\nR522-R524 off the pour", 120.0, 4.0, 172.0, 30.0),
        ("Control (DGND island):\nU401-U405 by J401;\nAGND tie R426 / C407\nnext to J401 only", 140.0, -10.5, 172.0, 2.0),
    ]
    for s, x0, y0, x1, y1 in zones:
        box(board, x0, y0, x1, y1, C, 0.15)
        note(board, s, x0 + 1.0, y0 + 2.0, 1.0)
    pcbnew.SaveBoard(PCB, board)
    print(f"{PCB}: {len(fps)} parts ({len(fixed)} placed), {len(nets)} pin-net links")


if __name__ == "__main__":
    main()
