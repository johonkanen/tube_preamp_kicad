#!/usr/bin/env python3
"""Q502 drain pours (BP_DRN, F and B) with Q503's cut-out on F: kipy draw_pours.py IN OUT

README Layout: Q502's tab on at least 6 cm2 per side, stitched; Q503 on F in a cut-out of that
pour, over the B-side drain copper (thermal coupling without an electrical connection).
"""
import sys
import pcbnew

POUR = (127.0, 12.5, 152.0, 37.0)
CUT = 3.6          # half size of Q503's cut-out on F (mm)


def mm(v): return pcbnew.FromMM(v)


def zone(b, net, layer, rect, hole=None, prio=10):
    z = pcbnew.ZONE(b)
    z.SetLayer(layer); z.SetNet(net); z.SetAssignedPriority(prio)
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
    z.SetMinThickness(mm(0.3)); z.SetLocalClearance(mm(0.3))
    o = z.Outline(); o.NewOutline()
    x0, y0, x1, y1 = rect
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(mm(x), mm(y))
    if hole:
        o.NewHole()
        hx0, hy0, hx1, hy1 = hole
        for x, y in ((hx0, hy0), (hx0, hy1), (hx1, hy1), (hx1, hy0)):
            o.Append(mm(x), mm(y), 0, 0)
    b.Add(z)
    return z


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    fp = {f.GetReference(): f for f in b.GetFootprints()}
    net = fp["Q502"].FindPadByNumber("2").GetNet()
    q = fp["Q503"].GetPosition()
    qx, qy = pcbnew.ToMM(q.x), pcbnew.ToMM(q.y)
    zone(b, net, pcbnew.F_Cu, POUR, (qx - CUT, qy - CUT, qx + CUT, qy + CUT))
    zone(b, net, pcbnew.B_Cu, POUR)
    # stitching vias on a 3 mm grid, clear of Q503's cut-out and of every pad
    x0, y0, x1, y1 = POUR
    pads = [p for f in b.GetFootprints() for p in f.Pads()]
    n = 0
    y = y0 + 2.0
    while y < y1 - 1.5:
        x = x0 + 2.0
        while x < x1 - 1.5:
            ok = not (abs(x - qx) < CUT + 1.0 and abs(y - qy) < CUT + 1.0)
            for p in pads:
                if not ok:
                    break
                bb = p.GetBoundingBox()
                ok = not (pcbnew.ToMM(bb.GetLeft()) - 1.0 < x < pcbnew.ToMM(bb.GetRight()) + 1.0 and
                          pcbnew.ToMM(bb.GetTop()) - 1.0 < y < pcbnew.ToMM(bb.GetBottom()) + 1.0)
            if ok:
                v = pcbnew.PCB_VIA(b)
                v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); v.SetWidth(mm(1.0)); v.SetDrill(mm(0.5))
                v.SetNet(net); v.SetLocked(True); b.Add(v); n += 1
            x += 3.0
        y += 3.0
    zones = b.Zones()
    pcbnew.ZONE_FILLER(b).Fill(zones)
    b.Save(sys.argv[2])
    print(f"BP_DRN pours F/B, {n} stitching vias")


if __name__ == "__main__":
    main()
