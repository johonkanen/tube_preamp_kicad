#!/usr/bin/env python3
"""Last chain step: kipy finalize.py IN OUT

- Cut the ground pour on the OTHER layer under every high-impedance track and SMD pad (net class
  HIZ and GCB; tools/make_pcb.py), HIZ_POUR wide each side, with rule areas that forbid zone fill.
  The same-layer pour already keeps HIZ_POUR away by the "HIZ to pour" rule in the .kicad_dru.
  A few pF on a 1 MOhm node is audible and couples plates back into grids (user 2026-11-23).
- GNDA pours drop floating islands; every zone refilled.
"""
import fnmatch
import json
import os
import sys
import pcbnew

HIZ_POUR = 1.5
PRO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kicad", "tube_preamp_revb.kicad_pro")


def mm(v): return pcbnew.FromMM(v)


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    pats = [p["pattern"] for p in json.load(open(PRO))["net_settings"]["netclass_patterns"] if p["netclass"] == "HIZ"]
    pats += ["GCB", "*/GCB"]
    hiz = lambda n: any(fnmatch.fnmatchcase(n, p) for p in pats)
    other = {pcbnew.F_Cu: pcbnew.B_Cu, pcbnew.B_Cu: pcbnew.F_Cu}
    cut = {pcbnew.F_Cu: pcbnew.SHAPE_POLY_SET(), pcbnew.B_Cu: pcbnew.SHAPE_POLY_SET()}
    err = mm(0.05)
    n = 0
    for t in b.GetTracks():
        if t.GetClass() == "PCB_TRACK" and hiz(t.GetNetname()):
            t.TransformShapeToPolygon(cut[other[t.GetLayer()]], t.GetLayer(), mm(HIZ_POUR), err, pcbnew.ERROR_OUTSIDE)
            n += 1
    for f in b.GetFootprints():
        for p in f.Pads():
            if hiz(p.GetNetname()) and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD:
                lay = pcbnew.B_Cu if f.IsFlipped() else pcbnew.F_Cu
                p.TransformShapeToPolygon(cut[other[lay]], lay, mm(HIZ_POUR), err, pcbnew.ERROR_OUTSIDE)
    for lay, poly in cut.items():
        poly.Simplify()
        for i in range(poly.OutlineCount()):
            z = pcbnew.ZONE(b)
            z.SetIsRuleArea(True)
            z.SetDoNotAllowZoneFills(True)
            for fn in (z.SetDoNotAllowTracks, z.SetDoNotAllowVias, z.SetDoNotAllowPads, z.SetDoNotAllowFootprints):
                fn(False)
            z.SetLayer(lay)
            z.SetZoneName("HIZ pour cut")
            o = z.Outline()
            o.NewOutline()
            ol = poly.Outline(i)
            for k in range(ol.PointCount()):
                q = ol.CPoint(k)
                o.Append(q.x, q.y)
            b.Add(z)
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.GetNetname().split("/")[-1] == "GNDA":
            z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
    zones = b.Zones()
    pcbnew.ZONE_FILLER(b).Fill(zones)
    b.Save(sys.argv[2])
    print(f"HIZ pour cuts under {n} track segments; GNDA islands removed, zones refilled")


if __name__ == "__main__":
    main()
