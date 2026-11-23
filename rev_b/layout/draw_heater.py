#!/usr/bin/env python3
"""Draw the heater pair (HTR1 / HTR2) on the rev B board: kipy draw_heater.py IN OUT

6.3 V AC heaters (12AX7: pins 4+5 to HTR1, pin 9 to HTR2; 0.3 A each, 0.9 A in all). As rev A, the
pair runs along the front edge, the edge opposite the B+ row, as a broadside pair: HTR1 on F
directly over HTR2 on B (1.2 mm, 1.6 mm of FR-4 between), so the loop they enclose is the board
thickness. It runs at y -21.0, behind the 4 mm pot-pin keep-out (y < -22.175) and in front of the
H104 / H105 hole keep-outs (y > -19.82), from V1 to x 88 just east of V3, then rearward
to J502. The rearward leg runs on B, the two conductors side by side 2.2 mm apart, so other
tracks cross it on F (a broadside pair is a wall on a two-layer board); nothing is placed in front
of the front run. At each socket HTR1 (F) takes short stubs to pins 4 and 5; HTR2 (B) leaves the pair
between pins 4 and 5 (0.8 mm, 0.69 mm to each) and runs through the socket centre to pin 9, about
10 mm from the grid pins (2, 7). No vias. make_groups.py keeps the path free of parts.
"""
import sys
import pcbnew

Y_F, X_E = -21.0, 87.5          # front run; rearward leg (HTR1 x, HTR2 at x + 2.2)
W, WS = 1.2, 0.8
J502_X1, J502_X2, J502_Y = 91.62, 104.32, (36.18, 41.18)
Y_SPLIT = 30.0                  # where the pair splits for the two tabs


def mm(v): return pcbnew.FromMM(v)


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    fp = {f.GetReference(): f for f in b.GetFootprints()}
    net = {n: fp["J502"].FindPadByNumber(p).GetNet() for n, p in (("HTR1", "1"), ("HTR2", "2"))}

    def trk(n, pts, layer, w=W):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(mm(x0), mm(y0))); t.SetEnd(pcbnew.VECTOR2I(mm(x1), mm(y1)))
            t.SetWidth(mm(w)); t.SetLayer(layer); t.SetNet(net[n]); t.SetLocked(True); b.Add(t)

    def via(n, x, y):
        v = pcbnew.PCB_VIA(b)
        v.SetPosition(pcbnew.VECTOR2I(mm(x), mm(y))); v.SetWidth(mm(1.2)); v.SetDrill(mm(0.6))
        v.SetNet(net[n]); v.SetLocked(True); b.Add(v)

    socks = [{pd.GetNumber(): (pcbnew.ToMM(pd.GetPosition().x), pcbnew.ToMM(pd.GetPosition().y)) for pd in fp[v].Pads()}
             for v in ("V1", "V2", "V3")]
    x_w = socks[0]["4"][0]
    xc_w = (socks[0]["4"][0] + socks[0]["5"][0]) / 2
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    # front run, broadside (nothing lies in front of it, so nothing has to cross it)
    trk("HTR1", [(X_E - 2.5, Y_F), (x_w, Y_F)], F)
    trk("HTR2", [(X_E + 2.2, Y_F), (xc_w, Y_F)], B)
    # rearward leg: both on B side by side (crossable on F); HTR1 drops to B by one via behind the run
    trk("HTR1", [(X_E - 2.5, Y_F), (X_E, Y_F + 2.5)], F)
    via("HTR1", X_E, Y_F + 2.5)
    trk("HTR1", [(X_E, Y_F + 2.5), (X_E, 33.0), (J502_X1, 33.0), (J502_X1, J502_Y[0])], B)
    trk("HTR2", [(X_E + 2.2, Y_F), (X_E + 2.2, 27.0), (J502_X2, 27.0), (J502_X2, J502_Y[0])], B)
    trk("HTR1", [(J502_X1, J502_Y[0]), (J502_X1, J502_Y[1])], B)
    trk("HTR2", [(J502_X2, J502_Y[0]), (J502_X2, J502_Y[1])], B)
    for s in socks:
        (x4, y4), (x5, _), (x9, y9) = s["4"], s["5"], s["9"]
        trk("HTR1", [(x4, Y_F), (x4, y4)], F)
        trk("HTR1", [(x5, Y_F), (x5, y4)], F)
        xc = (x4 + x5) / 2
        trk("HTR2", [(xc, Y_F), (xc, y4 + 3.0), (x9, y9 - 4.0), (x9, y9)], B, WS)
    b.Save(sys.argv[2])
    print("heater pair drawn (front edge, broadside)")


if __name__ == "__main__":
    main()
