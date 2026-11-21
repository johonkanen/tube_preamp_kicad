#!/usr/bin/env python3
"""Draw the five rev B sheets (first draft) from design D (tube_amplifier_kicad
sim/preamp_voicing/ours/chain_d.py + fit_design_D.json, docs/preamp_board_plan.md).

Netlist-first drawing: every part is placed on a grid and each connected pin gets a short wire
stub and a label (local label if the net stays on one sheet, global label if it crosses sheets,
a power symbol for GND / +5V / +15V / -15V). Two passes: the first collects the nets of every
sheet, the second draws. Readable enough for a first draft and exact for ERC and the netlist;
the layout gets tidied in a later pass.

Tube units (KiCad ECC83): unit 2 = pins 1/2/3, unit 1 = pins 6/7/8, unit 3 = heater 4/5/9.
  V1: unit 2 = S1, unit 1 = S2     V2: unit 2 = S5, unit 1 = S3     V3: unit 2 = CF, unit 1 = S4
The 1.6k grid resistors of the simulations are noise models, not parts: not drawn.
Run from anywhere: python3 rev_b/tools/sheets/draw_all.py
"""
import math
import os
import sys

RB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("P2K_BOARD", RB)
sys.path.insert(0, os.path.join(RB, "..", "tools", "p2k"))
from p2k.sch_builder import Sheet, lib  # noqa: E402
from p2k.sexpr import find, find_all  # noqa: E402

POWER = {"GNDA", "GNDD", "+5V", "+15V", "-15V"}
# Grounding (tube_amplifier_kicad docs/grounding.md §5a, user-confirmed 2026-11-21): "GND" in the
# sheet code means AGND (GNDA): signal and power star, entry at J501 pin 2, chassis bond at the
# CHASSIS pad J102 by the input. Sheet 04's logic sits on a DGND island (GNDD) joined to AGND by one
# soft tie (10R || 100n, R426 / C407 after numbering) next to J401. Switch references (JFET / MOSFET sources, gate caps,
# JFET-gate pull-downs) are AGND.
GRID = 2.54


def g(v):
    return round(round(v / 1.27) * 1.27, 2)


def at(c, r):
    """Grid cell (column c, row r) -> schematic mm."""
    return g(30.48 + c * 20.32), g(35.56 + r * 17.78)


class Drawer:
    def __init__(self, fname, mode, globals_=frozenset()):
        self.fname, self.mode, self.globals = fname, mode, globals_
        self.nets = set()
        self.sheet_no = int(fname[:2])
        self.count = {}
        self.refmap = {}
        self.sh = Sheet(os.path.join(RB, "kicad", fname)).clear() if mode == "draw" else None
        if self.sh is not None:
            self.sh.pwr = self.sheet_no * 100   # #PWR / #FLG numbers unique across sheets

    def auto_ref(self, ref, sym):
        """Unique reference per sheet: prefix letters + sheet number x 100 + a running number
        (V1-V3 and #FLG / #PWR keep their names; a multi-unit part keeps its first ref)."""
        if ref.startswith(("V", "#")):
            return ref
        multi = sym in ("DG411xY", "ECC83")
        if multi and ref in self.refmap:
            return self.refmap[ref]
        pre = "".join(ch for ch in ref if ch.isalpha() and not ch.isdigit())[:1] or "X"
        if ref.startswith("U") or ref.startswith("J"):
            pre = ref[0]
        self.count[pre] = self.count.get(pre, 0) + 1
        new = f"{pre}{self.sheet_no * 100 + self.count[pre]}"
        self.refmap[ref] = new
        return new

    def part(self, sym, ref, c, r, nets, value=None, rot=0, unit=1, stub=GRID):
        ref = self.auto_ref(ref, sym)
        nets = {k: ("GNDA" if v == "GND" else v) for k, v in nets.items()}
        for n in nets.values():
            if n and n != "NC":
                self.nets.add(n)
        if self.mode != "draw":
            return
        x, y = at(c, r)
        p = self.sh.place(sym, ref, x, y, rot=rot, unit=unit, value=value)
        dirs = {}
        for sub in find_all(lib()[sym], "symbol"):
            u = int(sub[1].rsplit("_", 2)[-2])
            if u not in (0, unit):
                continue
            for pn in find_all(sub, "pin"):
                dirs[str(find(pn, "number")[1])] = float(find(pn, "at")[3])
        for pin, net in nets.items():
            if not net:
                continue
            x0, y0 = p.pin(pin)
            if net == "NC":
                self.sh.no_connect(x0, y0)
                continue
            out = (dirs[str(pin)] + 180 + rot) % 360
            a = math.radians(out)
            x1, y1 = g(x0 + math.cos(a) * stub), g(y0 - math.sin(a) * stub)
            self.sh.wire((x0, y0), (x1, y1))
            lrot = int(round(out / 90.0)) * 90 % 360
            if net in POWER:
                self.sh.power(net, x1, y1, rot=0 if net != "GND" or lrot != 90 else 0)
            elif net in self.globals:
                self.sh.glabel(net, x1, y1, rot=lrot)
            else:
                self.sh.label(net, x1, y1, rot=lrot)

    def text(self, s, c, r, size=1.27):
        if self.mode == "draw":
            self.sh.text(s, *at(c, r), size=size)

    def save(self):
        if self.mode == "draw":
            self.sh.save()


# ------------------------------------------------------------------ helpers for common parts
def R(d, ref, c, r, a, b, v, rot=90):
    d.part("R", ref, c, r, {1: a, 2: b}, value=v, rot=rot)


def C(d, ref, c, r, a, b, v, rot=90):
    d.part("C", ref, c, r, {1: a, 2: b}, value=v, rot=rot)


def CP(d, ref, c, r, plus, minus, v, rot=0):
    d.part("C_Polarized", ref, c, r, {1: plus, 2: minus}, value=v, rot=rot)


def jfet(d, ref, c, r, drain, gate_drv, tag):
    """NJFET shunt (MMBFJ113) with its RC-slowed gate: 100k from the driver, 10 nF to ground."""
    d.part("MMBFJ113", ref, c, r, {1: drain, 2: "GND", 3: f"G_{tag}"}, value="MMBFJ113")
    R(d, f"R{ref[1:]}A", c - 1, r, gate_drv, f"G_{tag}", "100k", rot=0)
    C(d, f"C{ref[1:]}A", c - 1, r + 1, f"G_{tag}", "GND", "10n", rot=270)


def mosfet_net(d, ref, c, r, k, ctl, tag, series_r=None):
    """AC cathode network: [R +] 22 µF from the cathode to a 2N7002 low-side switch, 1M bleed
    across the switch, gate RC 100k / 10 nF from the control line (CH-5 rules 1-2)."""
    top = k
    if series_r:
        R(d, f"R{ref[1:]}S", c, r - 1, k, f"N_{tag}", series_r)
        top = f"N_{tag}"
    CP(d, f"C{ref[1:]}", c, r, top, f"M_{tag}", "22u/25V")
    d.part("2N7002", ref, c, r + 1, {1: f"GM_{tag}", 2: "GND", 3: f"M_{tag}"}, value="2N7002")
    R(d, f"R{ref[1:]}B", c + 1, r + 1, f"M_{tag}", "GND", "1M")
    R(d, f"R{ref[1:]}G", c - 1, r + 1, ctl, f"GM_{tag}", "100k", rot=0)
    C(d, f"C{ref[1:]}G", c - 1, r + 2, f"GM_{tag}", "GND", "10n", rot=270)


def relay(d, ref, c, r, drive, poles):
    """G6K-2 (SMD, 5 V coil): coil pin 1 to +5V, pin 8 to the ULN2003 sink. poles: dict pin->net
    (pole 1: COM 3, contacts 2 / 4; pole 2: COM 6, contacts 7 / 5). NC / NO assignment of
    2 / 4 and 7 / 5 to check against the Omron datasheet."""
    nets = {1: "+5V", 8: drive}
    for p in (2, 3, 4, 5, 6, 7):
        nets[p] = poles.get(p, "NC")
    d.part("G6K-2", ref, c, r, nets, value="G6K-2F-Y 5VDC")


# ------------------------------------------------------------------ sheet 01
CH = (("CL", "clean"), ("CR", "crunch"), ("LD", "lead"))


def sheet01(d):
    d.text("01 Input, S1 and the channel gain networks (design D). Each channel has its own coupling cap, "
           "pad, gain pot (on its pot ribbon) and bright cap, JFET-selected into S2's grid (GX2).", 0, -1.0, 2)
    d.part("Conn_01x02", "J101", 0, 1, {1: "IN_TIP", 2: "GND"}, value="INPUT")
    R(d, "R101", 1, 2, "IN_TIP", "GND", "1M")
    d.part("Conn_01x01", "J102", 0, 3.5, {1: "GND"}, value="CHASSIS (bolted tag; the only bond)")
    R(d, "R102", 2, 1, "IN_TIP", "G1", "68k", rot=0)
    d.part("ECC83", "V1", 4, 1, {1: "P1", 2: "G1", 3: "K1"}, value="12AX7", unit=2)
    R(d, "R103", 4, 0, "BP1", "P1", "100k")
    R(d, "R104", 4, 3, "K1", "GND", "2.7k")
    mosfet_net(d, "Q101", 6, 3, "K1", "CTL_S1A", "S1A", series_r="1.5k")     # clean
    mosfet_net(d, "Q102", 9, 3, "K1", "CTL_S1B", "S1B")                     # crunch, lead
    vals = {"CL": ("22n", None, "470p"), "CR": ("2.2n", None, "470p"), "LD": ("4.7n", None, None)}   # lead pad and bright cap dropped by the refit (2026-11-20)
    for i, (t, name) in enumerate(CH):
        c0, r0 = 12, 1 + i * 4
        cc, pad, br = vals[t]
        d.text(f"{name}: gain pot on J5{i + 4} (pot ribbon)", c0, r0 - 0.6)
        C(d, f"C1{i}1", c0, r0, "P1", f"N1_{t}" if pad else f"POT_G_{t}_TOP", cc, rot=0)
        if pad:
            R(d, f"R1{i}1", c0 + 1, r0, f"N1_{t}", f"POT_G_{t}_TOP", pad, rot=0)
        if br:
            C(d, f"C1{i}2", c0 + 2, r0 + 1, f"POT_G_{t}_TOP", f"POT_G_{t}_W", br)
        R(d, f"R1{i}2", c0 + 3, r0, f"POT_G_{t}_W", f"XI_{t}", "100k", rot=0)
        jfet(d, f"Q1{i}3", c0 + 5, r0 + 1, f"XI_{t}", f"JDRV_I{t}", f"I{t}")
        R(d, f"R1{i}3", c0 + 6, r0, f"XI_{t}", "GX2", "100k", rot=0)


# ------------------------------------------------------------------ sheet 02
def sheet02(d):
    d.text("02 S2, S5, S3 and the switched voicing (design D): one DC cathode resistor per stage, AC networks on "
           "2N7002s; relays only for the S2 -> S3 coupling cap (K203), the S5 routing (K202) and the lead's treble "
           "bleeds (K201, K204).", 0, -1.0, 2)
    R(d, "R201", 0, 2, "GX2", "GND", "1M")
    d.part("ECC83", "V1", 2, 1, {6: "P2", 7: "GX2", 8: "K2"}, value="12AX7", unit=1)
    R(d, "R202", 2, 0, "BP2", "P2", "100k")
    R(d, "R203", 2, 3, "K2", "GND", "10k")
    mosfet_net(d, "Q201", 4, 3, "K2", "CTL_S2A", "S2A")                     # clean, crunch
    # lead's fitted 4.7k + 22 uF, fitted as a switched network: drawn permanent (no switch, no 17th
    # control line). Clean / crunch then see 22 uF || (4.7k + 22 uF), same as 22 uF in band.
    R(d, "R204", 2, 5, "K2", "N_S2L", "4.7k")
    CP(d, "C202", 2, 6.5, "N_S2L", "GND", "22u/25V")
    C(d, "C203", 6, 0, "P2", "BL2", "1n/630V", rot=0)
    R(d, "R206", 7, 1, "BL2", "BP2", "10M")
    relay(d, "K201", 7, 3, "RLY_BL2_N", {3: "BL2", 4: "BP2"})              # lead: S2 treble bleed
    C(d, "C204", 9, 1, "P2", "C2A", "2.2n/630V", rot=0)
    C(d, "C205", 9, 2, "P2", "C2B", "22n/630V", rot=0)
    R(d, "R207", 10, 3, "C2A", "GND", "10M")
    R(d, "R208", 11, 3, "C2B", "GND", "10M")
    relay(d, "K203", 11, 5, "RLY_C2_N", {3: "N2", 2: "C2A", 4: "C2B"})    # crunch: 22 nF
    R(d, "R209", 12, 2, "N2", "GND", "10M")
    R(d, "R210", 13, 1, "N2", "GX2B", "470k", rot=0)
    C(d, "C206", 13, 2, "N2", "GX2B", "470p", rot=0)
    R(d, "R211", 14, 3, "GX2B", "GND", "470k")
    # S5 routing: pole 1 switches S5's input, pole 2 picks bypass (NC) or S5 out (NO) into S3
    relay(d, "K202", 16, 5, "RLY_S5_N", {3: "GX2B", 4: "CI5", 6: "CX", 7: "GX2B", 5: "Q5"})
    C(d, "C207", 16, 1, "CI5", "GI5", "100n", rot=0)
    R(d, "R212", 15, 2, "CI5", "GND", "10M")
    R(d, "R213", 17, 2, "GI5", "GND", "1M")
    d.part("ECC83", "V2", 18, 1, {1: "P5", 2: "GI5", 3: "K5"}, value="12AX7", unit=2)
    R(d, "R214", 18, 0, "BP3", "P5", "100k")
    R(d, "R215", 18, 3, "K5", "GND", "1.5k")
    C(d, "C208", 19, 3, "K5", "GND", "680n")
    C(d, "C209", 20, 1, "P5", "N5", "22n/630V", rot=0)
    R(d, "R216", 21, 1, "N5", "Q5", "470k", rot=0)
    R(d, "R217", 21, 3, "Q5", "GND", "1M")
    C(d, "C210", 18, 6, "CX", "GX3", "100n", rot=0)
    R(d, "R218", 17, 7, "CX", "GND", "10M")
    R(d, "R219", 19, 7, "GX3", "GND", "680k")
    d.part("ECC83", "V2", 21, 6, {6: "P3", 7: "GX3", 8: "K3"}, value="12AX7", unit=1)
    R(d, "R220", 21, 5, "BP3", "P3", "100k")
    R(d, "R221", 21, 8, "K3", "GND", "4.7k")
    mosfet_net(d, "Q202", 23, 8, "K3", "CTL_S3A", "S3A", series_r="1.5k")   # crunch
    mosfet_net(d, "Q203", 26, 8, "K3", "CTL_S3B", "S3B")                    # lead
    C(d, "C215", 23, 5, "P3", "BL3", "1n/630V", rot=0)
    R(d, "R227", 24, 6, "BL3", "BP3", "10M")
    relay(d, "K204", 25, 4, "RLY_BL3_N", {3: "BL3", 4: "BP3"})             # lead: S3 treble bleed


# ------------------------------------------------------------------ sheet 03
STACK = {"CL": ("560p", "5.6n", "470p", "3.3n"), "CR": ("2.2n", "22n", "120p", "820p"), "LD": ("560p", "5.6n", "470p", "3.3n")}


def sheet03(d):
    d.text("03 Self-biased CF, three Baxandalls (each channel's own pots on its ribbon; TS-5 values with the fitted "
           "cap scaling), JFET-selected post-gain outputs into S4, attenuator and output mute (design D).", 0, -1.0, 2)
    C(d, "C301", 0, 1, "P3", "GCB", "22n/630V", rot=0)
    R(d, "R301", 1, 0, "VB90", "GCB", "1M")
    d.part("ECC83", "V3", 3, 1, {1: "BP4", 2: "GCB", 3: "KCF"}, value="12AX7", unit=2)
    R(d, "R302", 3, 3, "KCF", "GND", "47k")
    C(d, "C302", 4, 1, "KCF", "SIN", "470n/250V", rot=0)
    for i, (t, name) in enumerate(CH):
        c0, r0 = 6, 0.5 + i * 4.5
        c1, c2, c3, c4 = STACK[t]
        d.text(f"{name} Baxandall: bass / treble / post pots on J5{i + 4}", c0, r0 - 0.6)
        R(d, f"R3{i}1", c0, r0, "SIN", f"POT_BS_{t}_TOP", "100k", rot=0)
        C(d, f"C3{i}1", c0 + 1, r0 + 1, f"POT_BS_{t}_TOP", f"POT_BS_{t}_W", c1)
        C(d, f"C3{i}2", c0 + 2, r0 + 1, f"POT_BS_{t}_W", f"POT_BS_{t}_BOT", c2)
        R(d, f"R3{i}2", c0 + 2, r0 + 3, f"POT_BS_{t}_BOT", "GND", "22k")
        R(d, f"R3{i}3", c0 + 3, r0, f"POT_BS_{t}_W", f"POT_TR_{t}_W", "100k", rot=0)
        C(d, f"C3{i}3", c0 + 4, r0, "SIN", f"POT_TR_{t}_TOP", c3, rot=0)
        C(d, f"C3{i}4", c0 + 5, r0 + 1, f"POT_TR_{t}_BOT", f"TR_{t}", c4)
        R(d, f"R3{i}4", c0 + 5, r0 + 3, f"TR_{t}", "GND", "22k")
        R(d, f"R3{i}5", c0 + 7, r0, f"POT_P_{t}_W", f"XP_{t}", "100k", rot=0)
        jfet(d, f"Q3{i}6", c0 + 9, r0 + 1, f"XP_{t}", f"JDRV_P{t}", f"P{t}")
        R(d, f"R3{i}6", c0 + 10, r0, f"XP_{t}", "GX4", "100k", rot=0)
    R(d, "R340", 18, 2, "GX4", "GND", "1M")
    d.part("ECC83", "V3", 20, 1, {6: "P4", 7: "GX4", 8: "K4"}, value="12AX7", unit=1)
    R(d, "R341", 20, 0, "BP4", "P4", "100k")
    R(d, "R342", 20, 3, "K4", "GND", "1.5k")
    CP(d, "C340", 21, 3, "K4", "GND", "22u/25V")
    C(d, "C341", 22, 1, "P4", "AT", "22n/630V", rot=0)
    R(d, "R343", 23, 1, "AT", "OUT", "330k", rot=0)
    R(d, "R344", 24, 2, "OUT", "GND", "220k")
    jfet(d, "Q345", 26, 2, "OUT", "JDRV_MUTE", "MUTE")


# ------------------------------------------------------------------ sheet 04
def sheet04(d):
    d.text("04 Switch control: MCP23S17 (SPI) -> 2x DG412 (JFET gates 0 / -15 V, normally open: reset or no -15 V "
           "= JFETs on = muted), 2N7002 gates direct (5 V), ULN2003 relay sinks. Unmute = GPA6 AND MUTE_ALL_N "
           "(pulled low: ribbon unplugged = muted).", 0, -1.0, 2)
    # INTERFACE CONTRACT: J401 pinout is in tube_amplifier_kicad docs/interfaces.md ("preamp rev B
    # draft (2026-11-20)"); other boards follow it. Propose changes via the main-branch session first.
    d.part("Conn_02x07_Odd_Even", "J401", 0, 2, {1: "+5V", 2: "GNDD", 3: "+15V", 4: "GNDD", 5: "-15V", 6: "GNDD",
                                                  7: "SPI_SCK", 8: "GNDD", 9: "SPI_MOSI", 10: "SPI_MISO",
                                                  11: "SPI_CS_N", 12: "MUTE_ALL_N", 13: "RESET_N", 14: "GNDD"},
           value="CONTROL (ribbon)")
    for i, n in enumerate(("+5V", "+15V", "-15V", "GNDD")):
        d.part("PWR_FLAG", f"#FLG40{i}", 2, 4 + i * 0.6, {1: n}, value="PWR_FLAG")
    R(d, "R401", 3, 1, "RESET_N", "+5V", "10k")
    R(d, "R402", 3, 3, "MUTE_ALL_N", "GNDD", "100k")
    gp = {21: "EX_ICL", 22: "EX_ICR", 23: "EX_ILD", 24: "EX_PCL", 25: "EX_PCR", 26: "EX_PLD", 27: "EX_UNMUTE",
          28: "EX_RLY_BL3", 1: "CTL_S1A", 2: "CTL_S1B", 3: "CTL_S2A", 4: "CTL_S3A", 5: "CTL_S3B",
          6: "EX_RLY_BL2", 7: "EX_RLY_S5", 8: "EX_RLY_C2"}
    nets = dict(gp)
    nets.update({9: "+5V", 10: "GNDD", 11: "SPI_CS_N", 12: "SPI_SCK", 13: "SPI_MOSI", 14: "SPI_MISO",
                 15: "GNDD", 16: "GNDD", 17: "GNDD", 18: "RESET_N", 19: "NC", 20: "NC"})
    d.part("MCP23S17x-x-SS", "U401", 6, 3, nets, value="MCP23S17-E/SS")
    C(d, "C401", 6, 0, "+5V", "GNDD", "100n", rot=0)
    for k, (pin, n) in enumerate(sorted(gp.items(), key=lambda x: x[1])):
        R(d, f"R41{k:02d}"[:5] if k < 10 else f"R4{20 + k}", 9 + (k % 8) * 1.6, 8 + (k // 8) * 1.4, n, "GNDD", "100k")
    d.part("74LVC1G08", "U404", 9, 5, {1: "EX_UNMUTE", 2: "MUTE_ALL_N", 3: "GNDD", 4: "SW_UNMUTE", 5: "+5V"},
           value="74LVC1G08")
    sw = [("EX_ICL", "JDRV_ICL"), ("EX_ICR", "JDRV_ICR"), ("EX_ILD", "JDRV_ILD"), ("EX_PCL", "JDRV_PCL"),
          ("EX_PCR", "JDRV_PCR"), ("EX_PLD", "JDRV_PLD"), ("SW_UNMUTE", "JDRV_MUTE"), ("GNDD", "NC")]
    pins = [(1, 2, 3), (8, 7, 6), (9, 10, 11), (16, 15, 14)]   # (IN, D, S) per KiCad unit 1-4 (switches 1, 4, 3, 2)
    for j in range(2):
        ref = f"U40{2 + j}"
        for u in range(4):
            inp, dpin, spin = pins[u]
            ex, drv = sw[j * 4 + u]
            d.part("DG411xY", ref, 13 + u * 2.2, 2 + j * 4, {inp: ex, dpin: drv, spin: "-15V" if drv != "NC" else "NC"},
                   value="DG412DY", unit=u + 1)
        d.part("DG411xY", ref, 22, 2 + j * 4, {4: "-15V", 5: "GNDD", 12: "+5V", 13: "+15V"}, value="DG412DY", unit=5)
        C(d, f"C40{2 + j}", 23.5, 1 + j * 4, "+15V", "GNDD", "100n")
        C(d, f"C40{4 + j}", 24.5, 1 + j * 4, "-15V", "GNDD", "100n")
    for k, (_, drv) in enumerate(sw[:7]):
        R(d, f"R43{k}", 13 + k * 1.3, 10.5, drv, "GNDA", "100k")      # 0 V = JFET on (muting); AGND: the JFET's reference
    d.part("ULN2003", "U406", 15, 13, {1: "EX_RLY_BL2", 2: "EX_RLY_S5", 3: "EX_RLY_C2", 4: "EX_RLY_BL3",
                                       5: "GNDD", 6: "GNDD", 7: "GNDD", 8: "GNDD", 9: "+5V", 16: "RLY_BL2_N",
                                       15: "RLY_S5_N", 14: "RLY_C2_N", 13: "RLY_BL3_N", 12: "NC", 11: "NC", 10: "NC"},
           value="ULN2003A")
    C(d, "C407", 17, 12, "+5V", "GNDD", "100n")
    d.text("DGND -> AGND soft tie (the only DGND-AGND link, next to J401; grounding.md §5a)", 3, 12.3)
    R(d, "R440", 3, 13, "GNDD", "GNDA", "10")
    C(d, "C440", 4.5, 13, "GNDD", "GNDA", "100n")


# ------------------------------------------------------------------ sheet 05
def sheet05(d):
    d.text("05 B+ regulator (docs/preamp_regulator.md: CCS-fed zener reference, Rf-Cf filter / soft start, HV "
           "MOSFET follower, foldback limit), RC decoupling to the stage supplies (values provisional), CF grid "
           "bias, heaters with the reference jumper (D12), pot ribbons, output.", 0, -1.0, 2)
    # INTERFACE CONTRACT: J501-J507 pinouts (tabs, pot ribbons, output) are in tube_amplifier_kicad
    # docs/interfaces.md ("preamp rev B draft (2026-11-20)"). Propose changes via the main session first.
    d.part("Conn_01x02", "J501", 0, 1, {1: "BP_RAW", 2: "GND"}, value="B+ RAW 430V (tab)")   # pin 2: the AGND entry
    d.part("PWR_FLAG", "#FLG503", 1, 2.5, {1: "GND"}, value="PWR_FLAG")
    d.part("Q_NMOS_Depletion", "Q501", 2, 1, {"D": "BP_RAW", "G": "ZT", "S": "CS"}, value="LND150")
    R(d, "R501", 3, 2, "CS", "ZT", "330")
    for i in range(3):
        d.part("D_Zener", f"D50{i + 1}", 3, 3 + i, {1: "ZT" if i == 0 else f"Z{i}", 2: f"Z{i + 1}" if i < 2 else "GND"},
               value="130V 1W", rot=90)
    R(d, "R502", 5, 2, "ZT", "GF", "1M", rot=0)
    CP(d, "C501", 6, 3, "GF", "GND", "2.2u/450V")
    R(d, "R503", 7, 2, "GF", "GP", "10k", rot=0)
    d.part("Q_NMOS", "Q502", 9, 2, {"D": "BP_RAW", "G": "GP", "S": "SRC"}, value="STP4N80K5")
    d.part("D_Zener", "D504", 9, 4, {1: "GP", 2: "SRC"}, value="15V", rot=90)
    d.part("D", "D505", 7, 0, {1: "BP_RAW", 2: "GF"}, value="1N4007")
    R(d, "R504", 10, 3, "SRC", "BP", "20", rot=0)
    d.part("Q_NPN", "Q503", 11, 5, {"B": "QB", "C": "GP", "E": "BP"}, value="MMBTA42")
    R(d, "R505", 10, 6, "SRC", "QB", "1k", rot=0)
    R(d, "R506", 12, 6, "QB", "BP", "10k", rot=0)
    R(d, "R507", 11, 7, "BP_RAW", "QB", "820k", rot=0)
    CP(d, "C502", 13, 3, "BP", "GND", "47u/450V")
    C(d, "C503", 14, 3, "BP", "GND", "100n/630V")
    R(d, "R508", 15, 3, "BP", "BLEED_M", "220k")    # 2 x 2512 in series (330 V over 200 V parts); lower half at the end
    chain = [("BP", "BP4", "3.3k"), ("BP4", "BP3", "6.8k"), ("BP3", "BP2", "10k"), ("BP2", "BP1", "10k")]
    for i, (a, b, rv) in enumerate(chain):
        R(d, f"R51{i}", 17 + i * 2, 1, a, b, rv, rot=0)
        CP(d, f"C51{i}", 18 + i * 2, 2, b, "GND", "22u/450V")
    R(d, "R520", 17, 4, "BP4", "VDIV_M", "330k")    # 2 x 2512 in series (230 V; 660k: VB90 = 0.29 x BP4); lower half at the end
    R(d, "R521", 17, 6, "VB90", "GND", "270k")
    CP(d, "C520", 18, 6, "VB90", "GND", "10u/250V")
    d.part("Conn_01x02", "J502", 0, 9, {1: "HTR1", 2: "HTR2"}, value="HEATER 6.3V (tab)")
    d.part("PWR_FLAG", "#FLG501", 1, 10, {1: "HTR1"}, value="PWR_FLAG")
    d.part("PWR_FLAG", "#FLG502", 1.6, 10, {1: "HTR2"}, value="PWR_FLAG")
    for i, v in enumerate(("V1", "V2", "V3")):
        d.part("ECC83", v, 3 + i * 2, 9, {4: "HTR1", 5: "HTR1", 9: "HTR2"}, value="12AX7", unit=3)
    R(d, "R530", 10, 9, "HTR1", "HREF", "100")
    R(d, "R531", 11, 9, "HTR2", "HREF", "100")
    d.part("Conn_01x03", "J503", 13, 9, {1: "GND", 2: "HREF", 3: "VB90"}, value="HEATER REF (jumper, D12)")
    for i, (t, name) in enumerate(CH):
        nets = {k: "GND" for k in range(1, 27, 2)}
        sig = [f"POT_G_{t}_TOP", f"POT_G_{t}_W", f"POT_BS_{t}_TOP", f"POT_BS_{t}_W", f"POT_BS_{t}_BOT",
               f"POT_TR_{t}_TOP", f"POT_TR_{t}_W", f"POT_TR_{t}_BOT", f"POT_P_{t}_W"]
        for k in range(13):
            nets[2 + 2 * k] = sig[k] if k < len(sig) else "GND"
        d.part("Conn_02x13_Odd_Even", f"J5{i + 4}", 16 + i * 4, 10, nets, value=f"POTS {name.upper()} (ribbon)")
    d.part("Conn_01x03", "J507", 0, 13, {1: "OUT", 2: "GND", 3: "SHLD_OUT"}, value="OUT to FX send / PI")
    R(d, "R540", 2, 14, "SHLD_OUT", "GND", "10")      # shield soft tie here, solid at the PI + FX end
    C(d, "C540", 3, 14, "SHLD_OUT", "GND", "100n")
    d.text("Post-gain pot top = treble pot wiper (POT_TR_x_W): joined on the pot board. Pot bottoms of gain / post = GND pins.", 15, 15.5)
    # Drawn last so the earlier refs keep their numbers: lower halves of the split HV resistors (R518, R519).
    R(d, "R550", 15, 5, "BLEED_M", "GND", "220k")
    R(d, "R551", 17, 5, "VDIV_M", "VB90", "330k")


SHEETS = [("01_input.kicad_sch", sheet01), ("02_gain_stages.kicad_sch", sheet02),
          ("03_tone_output.kicad_sch", sheet03), ("04_control.kicad_sch", sheet04),
          ("05_supply.kicad_sch", sheet05)]


def main():
    seen = {}
    for f, fn in SHEETS:
        d = Drawer(f, "collect")
        fn(d)
        for n in d.nets:
            seen.setdefault(n, set()).add(f)
    glob = frozenset(n for n, fs in seen.items() if len(fs) > 1 and n not in POWER)
    for f, fn in SHEETS:
        d = Drawer(f, "draw", glob)
        fn(d)
        d.save()
    single = sorted(n for n, fs in seen.items() if len(fs) == 1)
    print(f"nets: {len(seen)}, global: {len(glob)}")


if __name__ == "__main__":
    main()
