#!/usr/bin/env python3
"""Feedback-path check: kipy coupling_check.py BOARD [MM]

Lists where a plate / output net (aggressor) runs within MM (default 2.0) of a grid / input /
high-impedance net (victim) on the same layer, as parallel length and closest gap per net pair.
A later stage's plate next to an earlier stage's grid is a feedback loop; the report says which.
"""
import fnmatch
import json
import math
import os
import sys
import pcbnew

PRO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kicad", "tube_preamp_revb.kicad_pro")
# stage order along the signal path (lower = earlier); plates and outputs as aggressors
AGG = {"P1": 1, "P2": 2, "C2A": 2, "C2B": 2, "P5": 3, "P3": 4, "GCB": 4, "KCF": 5, "SIN": 5, "P4": 6, "AT": 6, "OUT": 7}
VIC_STAGE = {"IN_TIP": 0, "G1": 0, "GX2": 1, "XI_": 1, "POT_G_": 1, "N1_CR": 1, "GX2B": 2, "N2": 2, "CI5": 2,
             "GI5": 2, "N5": 3, "Q5": 3, "CX": 3, "GX3": 3, "GCB": 4, "POT_BS": 5, "POT_TR": 5, "POT_P": 5,
             "XP_": 5, "GX4": 5}


def short(n): return n.split("/")[-1]


def stage(n):
    for k, v in VIC_STAGE.items():
        if n == k or (k.endswith("_") and n.startswith(k)) or n.startswith(k + "_"):
            return v
    return None


def seg_dist(a0, a1, b0, b1):
    def pd(p, s0, s1):
        dx, dy = s1[0] - s0[0], s1[1] - s0[1]
        L = dx * dx + dy * dy
        t = 0 if L == 0 else max(0, min(1, ((p[0] - s0[0]) * dx + (p[1] - s0[1]) * dy) / L))
        return math.hypot(p[0] - s0[0] - t * dx, p[1] - s0[1] - t * dy)
    return min(pd(a0, b0, b1), pd(a1, b0, b1), pd(b0, a0, a1), pd(b1, a0, a1))


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    lim = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
    pats = [p["pattern"] for p in json.load(open(PRO))["net_settings"]["netclass_patterns"] if p["netclass"] == "HIZ"]
    segs = []
    for t in b.GetTracks():
        if t.GetClass() != "PCB_TRACK":
            continue
        n = short(t.GetNetname())
        w = pcbnew.ToMM(t.GetWidth()) / 2
        s = (pcbnew.ToMM(t.GetStart().x), pcbnew.ToMM(t.GetStart().y))
        e = (pcbnew.ToMM(t.GetEnd().x), pcbnew.ToMM(t.GetEnd().y))
        segs.append((n, t.GetLayer(), s, e, w, pcbnew.ToMM(t.GetLength())))
    agg = [x for x in segs if x[0] in AGG]
    vic = [x for x in segs if stage(x[0]) is not None and x[0] not in AGG or x[0] == "GCB"]
    res = {}
    for a in agg:
        for v in vic:
            if a[0] == v[0] or a[1] != v[1]:
                continue
            g = seg_dist(a[2], a[3], v[2], v[3]) - a[4] - v[4]
            if g < lim:
                k = (a[0], v[0])
                L, G = res.get(k, (0.0, 99.0))
                res[k] = (L + min(a[5], v[5]), min(G, g))
    print(f"aggressor -> victim within {lim} mm on one layer (parallel length ~ overlap of the shorter segments)")
    for (an, vn), (L, G) in sorted(res.items(), key=lambda kv: -kv[1][0]):
        fb = "FEEDBACK (later plate -> earlier grid)" if AGG[an] > (stage(vn) or 0) else ""
        print(f"  {an:5s} -> {vn:14s} {L:6.1f} mm, closest {G:4.2f} mm  {fb}")


if __name__ == "__main__":
    main()
