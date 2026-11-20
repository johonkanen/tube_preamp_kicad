"""proteus2kicad configuration of the etunen board (tools in tools/p2k, see its README).

Plain Python; every value here is specific to this board. Coordinates in mm, IPC frame (Y up).
Phase 0 (2026-11-20): sheets, IPC fix-ups, expected counts, layers, drills, outline.
"""

PROJECT = "tube_preamp"  # KiCad project / library name

# Sources (relative to the repo root). The CADCAM export with Gerber X2 attributes
# (October 2010 layout, the accepted baseline; source/fab_2010/ is the June 2010 fab set).
CADCAM = "source/cadcam"
IPC = "source/cadcam/etunen - CADCAM Netlist.IPC"

# --- Schematic skeleton (make_skeleton) ----------------------------------------------

# (Proteus page, sheet name, file). The 2010 PDF pages have no title block (as on the power
# amp board), so the names describe the page content (STATUS.md "Phase 0"); rename here
# before make_skeleton if wanted.
SHEETS = [
    (1, "Input stage", "01_input_stage.kicad_sch"),      # U1, GTR-IN, Q1/Q2, RLY1/RLY2, POTx-y
    (2, "Second stage", "02_second_stage.kicad_sch"),    # U2, RLY3, Q3-Q6, POT-GND
    (3, "EQ stage", "03_eq_stage.kicad_sch"),            # U3, RLY4/RLY5, Q7-Q9, PRES*, MV*, EQOUT
    (4, "Tone stacks", "04_tone_stacks.kicad_sch"),      # 3 tone stacks EQ1-EQ3, HI*/LO* pads
    (5, "Supply filter", "05_supply_filter.kicad_sch"),  # R62-R67, C28/C33-C37, A-D, SW1-SW3
]
SCH_TITLE = "Tube preamp"
SCH_COMPANY = "Tube amplifier"
SCH_REV = "rev A (as built)"
SCH_COMMENT = "Redrawn from Proteus etunen"
SCH_NOTE = ("Tube preamp (3x 12AX7) rev A - redrawn from Proteus etunen (2010, October layout).\n"
            "One sheet per Proteus PDF page. Net names follow the IPC-D-356A netlist "
            "(reference/pins_by_net.md).")

# --- IPC-D-356A fix-ups (ipc356) -----------------------------------------------------

# Truncated refdes (IPC 6-char field) -> full Proteus refdes, from the schematic PDF. Each
# truncated name is unique on this board, so no coordinates are needed. GTR-IN and
# POT1-1 ... POT3-2 are exactly 6 characters and complete (PDF).
TRUNCATED_REFDES = {
    "GTR-GN": "GTR-GND",     # sheet 1
    "POT-GN": "POT-GND",     # sheet 2
    "PREPOW": "PREPOWER",    # sheet 5
    "PRERET": "PRERETURN",   # sheet 5
}
# Expected net per restored refdes (checked by ipc356 --check). The tool looks these up by
# the *KiCad* refdes (after KICAD_REFDES), so the keys are the KiCad names.
TRUNCATED_NETS = {
    "GTR_GND": "PRE-GND",
    "POT_GND": "PRE-GND",
    "PREPOWER": "#00131",    # R67-2 (B+ input of the RC filter chain)
    "PRERETURN": "PRE-GND",
}

# Full Proteus refdes -> KiCad refdes (KiCad references: letter first, then letters, digits,
# '_'). Every script that compares against the IPC goes through this table (ipc356_pads.json
# carries it). Convention as tube_psu / the power amp: + -> P, - (sign) -> N, separators
# (space, '-', '.') -> '_', ' -> _PRIME. The single-letter pads A-D get a PAD_ prefix: "C"
# and "D" would read as unnumbered capacitor / diode references (A and B for consistency).
# No refdes on this board starts with a sign or contains '+', "'", '.' or a space.
KICAD_REFDES = {
    "GTR-IN": "GTR_IN",
    "GTR-GND": "GTR_GND",
    "POT-GND": "POT_GND",
    "POT1-1": "POT1_1",
    "POT1-2": "POT1_2",
    "POT2-1": "POT2_1",
    "POT2-2": "POT2_2",
    "POT3-1": "POT3_1",
    "POT3-2": "POT3_2",
    "A": "PAD_A",
    "B": "PAD_B",
    "C": "PAD_C",
    "D": "PAD_D",
}

# No Proteus power nets (no "=POWER" names). The named nets keep their IPC spelling
# (PRE-GND, H4, H5, A-F, J1-J4, SW1-SW3, PRE1, PRE2, EQ, EQ1-EQ3); the PDF writes some in
# lower case (pre-gnd, sw1-sw3, h4, h5, j4): Proteus net names ignore case, KiCad's do not.
NET_ALIASES = {}

# Pin ids renamed after parsing the IPC file (p2k ipc356, so every tool sees them). {KiCad refdes:
# {Proteus pin id: KiCad pin id}}. RLY1-RLY5 (design change 2026-11-20, coordinating-session decision
# "PR relays", STATUS.md "Shared-tool migration 2026-11-20"): the Proteus package G5V-2(HI) numbers the
# pads 1-8; the Omron terminals on those pads (STATUS.md "Phase 2", finding 14) are Proteus 1 / 2 / 3 =
# NO 9 / COM 13 / NC 11 (pole 1), 4 / 5 = coil 16 / 1, 6 / 7 / 8 = COM 4 / NC 6 / NO 8 (pole 2). With
# the Omron numbers the symbol and footprint are KiCad's Relay:G5V-2 / Relay_THT:Relay_DPDT_Omron_G5V-2
# unchanged (as tube_pi_fxloop_kicad's SERIES_MIX, same map); the copper and every net stay as built.
IPC_PIN_IDS = {f"RLY{i}": {"1": "9", "2": "13", "3": "11", "4": "16", "5": "1", "6": "4", "7": "6", "8": "8"}
               for i in range(1, 6)}

# Blank-refdes records: 14 vias (0.508 mm drill, 1.27 mm pad), no free pads; the 13 records
# without a net are the plated 3.0 mm mounting holes (6.35 mm pad on both layers).
VIA_DRILLS = (0.508,)
FREE_PAD_DRILLS = ()
HOLE_DRILLS = (3.0,)
HOLES_PLATED = True

# Expected counts in the Proteus file (PLAN.md section 1).
EXPECTED_IPC = {
    "nets": 98,           # NNAME declarations (numbered 00001-00114 with gaps)
    "records": 366,       # 339 component pads (incl. 3 N/C) + 14 vias + 13 holes
    "refdes_raw": 164,    # 163 refdes fields + the blank one of the vias / holes
    "tht_records": 366,
    "smd_records": 0,
    "smd_top": 0,
    "smd_bottom": 0,
    "nc_pads": 3,         # pin 9 (heater centre tap) of U1-U3
    "vias": 14,
    "free_pads": 0,
    "holes": 13,
    "parts": 163,
}

# --- Gerbers (check_sources, later the PCB tools) ------------------------------------

# Proteus copper gerber name -> KiCad copper layer, User layer for the pour outlines
# (there are no pours on this board: no G36 regions, no %LPC%).
COPPER = [
    ("Top Copper", "F.Cu", "User.1"),
    ("Bottom Copper", "B.Cu", "User.2"),
]
DRILL_PLATED = "Drill TOP-BOT Plated"
DRILL_NONPLATED = None    # no NonPlated drill file: the mounting holes are plated
OUTLINE = "Mechanical 1"
OUTLINE_RECT = (-195.357, -45.73, 382.79, 71.905)  # x, y, width, height

# --- ERC (p2k erc; was tools/erc.sh) -------------------------------------------------------------

# ERC warnings that fail: a no-connect pin that is wired (for this conversion a netlist error; Phase 5,
# as the PI / FX loop board) and a Footprint field naming a missing library / footprint (e.g. without
# kicad/fp-lib-table). Other warnings are listed only; report reports/erc.rpt.
ERC_FATAL_WARNINGS = {"no_connect_connected", "footprint_link_issues"}

# --- Footprints (Phase 2, tools/gen_footprints.py, p2k check_footprints) ---------------

# Pad sizes: "kicad" (KiCad library pad sizes and drills, pad centres on the Proteus positions;
# the IPC-built footprints - noval socket, fly-lead terminal - have the Proteus pads). Changing
# it is a user decision (Phase 3 DRC). STATUS.md "Phase 2" lists the differences per refdes.
FOOTPRINT_PAD_SIZES = "kicad"
# Every part of lib/part_map.csv is on the board (no off-board parts).
OFF_BOARD_PARTS = {}
# tools/gen_footprints.py (footprints.run) writes / --checks kicad/fp-lib-table (default descr).
FP_LIB_TABLE = True

# --- Pin order (p2k check_pin_order; was tools/check_pin_order.py, STATUS.md "Phase 2" and
# "Shared-tool migration 2026-11-20") ---------------------------------------------------------

# The UNMOVED KiCad base footprints with the Proteus renumbering fitted onto the IPC pads: a small
# residual on the expected side confirms that the Proteus pin ids sit on the pads the renumbering
# says. Two-pad and inline parts fit both ways round: `polarity` (the IPC pin id on the marked base
# pad 1: square pad + '+' silk of CP_Radial, band of DO-41, stated from the Proteus pinouts) and the
# renders (--render, reports/pin_order/) decide. The noval socket: KiCad's Valve_Noval_P is on a
# 2.54 mm grid (never a small residual), so the chirality is shown by the mirrored fit and by an
# ideal standard noval on the Proteus 21.00 mm pitch circle (10 positions at 36 deg, gap between 9
# and 1); since Phase 5 the sockets are on the bottom side (the project footprint has the standard
# numbering in its own view and fits the IPC pads only mirrored).
_NOVAL_IDEAL = dict(n=9, pcd=21.0, step=36, start=-54, pad=4.318, drill=1.727)
_NOVALS = "U1 U2 U3"
_RELAYS = "RLY1 RLY2 RLY3 RLY4 RLY5"
_G5V2_PHASE1 = {o: IPC_PIN_IDS["RLY1"][p] for o, p in {"1": "4", "4": "2", "6": "3", "8": "1", "16": "5",
                                                      "13": "6", "11": "7", "9": "8"}.items()}
PIN_ORDER = [
    dict(spec="TO-92_Inline_P2.03mm", refs="Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9", mirror=False, res=0.51,
         note="TO-92_Inline_Wide is P2.54, Proteus P2.032"),
    dict(spec="D_DO-41_SOD81_P10.16mm_Horizontal_AK", refs="D1 D2 D3 D4 D5 D8 D9", mirror=False, res=0.01,
         polarity="K"),                                    # 1N4001: A / K
    dict(spec="CP_Radial_D6.3mm_P2.54mm_PM", refs="C2", mirror=False, res=0.03, polarity="+",
         note="P2.50 vs P2.54"),                           # ELEC-RAD10: pins + / -
    dict(spec="CP_Radial_D6.3mm_P2.50mm_PM", refs="C30", mirror=False, res=0.01, polarity="+"),   # 22U 100V
    dict(spec="CP_Radial_D16.0mm_P7.50mm_Pin2Plus", refs="C28 C33 C34 C35 C36 C37", mirror=False, res=0.01,
         polarity="2"),                                    # ELEC D16 R7.5: + = 2, - = 1
    # G5V-2: the IPC pin ids of RLY1-RLY5 are the Omron pins (IPC_PIN_IDS), so the unmoved KiCad G5V-2
    # must fit unmirrored. The pad pattern (2 columns x 4 rows) is mirror-symmetric: the Phase 1
    # symbol mapping (Proteus 4 / 2 / 3 / 1 on Omron 1 / 4 / 6 / 8 and 5 / 6 / 7 / 8 on 16 / 13 / 11 / 9),
    # expressed in today's Omron ids, must fit only mirrored, which also proves that IPC_PIN_IDS is the
    # physical and not the mirrored mapping (as tube_pi_fxloop_kicad's SERIES_MIX).
    dict(refs=_RELAYS, footprint="Relay_THT:Relay_DPDT_Omron_G5V-2", mirror=False, res=0.01,
         note="Omron ids (IPC_PIN_IDS) on the unmoved KiCad G5V-2"),
    dict(name=_RELAYS + " (Phase 1 mapping)", refs=_RELAYS, footprint="Relay_THT:Relay_DPDT_Omron_G5V-2",
         renumber=_G5V2_PHASE1, mirror=True, res=0.01, render=False,
         note="the Phase 1 symbol mapping fits only mirrored"),
    # noval: only the MIRRORED KiCad noval matches the Proteus numbering
    dict(footprint="Valve:Valve_Noval_P", refs=_NOVALS, mirror=True, res=3.1),
    dict(name=_NOVALS + " (ideal)", ideal=_NOVAL_IDEAL, refs=_NOVALS, mirror=True, res=0.02, other=0.02,
         note="ideal standard noval, PCD 21.00 mm"),
    dict(name="noval footprint vs ideal", footprint="tube_preamp:Valve_Noval_Belton_PCD21.00mm",
         on_ideal=_NOVAL_IDEAL, mirror=False, res=0.02, other=0.02,
         note="standard noval numbering in the footprint's own view"),
    dict(name=_NOVALS + " (project)", footprint="tube_preamp:Valve_Noval_Belton_PCD21.00mm", refs=_NOVALS,
         mirror=True, res=0.02, other=0.02, note="fits only mirrored = bottom side"),
]
# reports/footprint_fit.csv and the board: exactly these parts on the bottom side (Phase 5)
PIN_ORDER_BOTTOM = {"U1", "U2", "U3"}
# Derived project footprints: how far their pads may sit from the renumbered base pads (footprint
# frame, mm); a wrong renumbering moves pads by a pitch while the graphics (band, '+', pin-1 mark)
# stay.
PIN_ORDER_MAX_MOVE = {
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
}

# --- PCB (Phase 3, build_pcb) ----------------------------------------------------------

# The 13 IPC 'hole' records: plated 3.0 mm holes with a 6.35 mm pad on both layers, no net.
HOLE_FOOTPRINT = "tube_preamp:MountingHole_3.0mm_PTH_Pad6.35mm"
HOLE_VALUE = "MountingHole_3.0mm"
# The holes are H101-H113 (build_pcb's hole n = H(100 + n), top row first, left to right; STATUS.md
# "Phase 3" maps them to README's mechanical table): the schematic has the heater terminals H4 / H5,
# so H1-H13 would collide (was tools/rename_holes.py, p2k candidate 18).
HOLE_START = 101
# Board thickness: 1.6 mm, the 2010 standard; the 2010 fab READ-ME (source/fab_2010) gives no
# stack-up. The 2026 export's READ-ME lists Proteus 8's default 2-layer stack (2 x 0.036 Cu +
# 1.483 FR4 = 1.555 mm, + 2 x 0.01 resist), written when the design was re-saved, not the 2010 order.
PCB_THICKNESS = 1.6
# Design rules from the Proteus copper as built (STATUS.md "Phase 3", `kipy -m p2k.measure_gaps`), mm.
PCB_RULES = dict(
    min_track=0.5,        # thinnest conductor draw 0.508 (20 mil)
    min_via=1.2,          # the 14 Proteus vias: 1.27 mm pad
    min_annular=0.3,      # via (1.27 - 0.508) / 2 = 0.381; smallest KiCad pad ring 0.35 (G5V-2 1.4/0.7, TO-92 1.5/0.8)
    min_drill=0.5,        # smallest drill 0.508 (vias); components >= 0.7 (KiCad G5V-2)
    clearance=0.38,       # smallest different-net gap 0.381 (15 mil: pad-track, track-via); track-track 0.390, pad-pad 0.468
    hole_clearance=0.25,  # drill to other-net copper: >= 0.381 gap + annular ring
    hole_to_hole=1.0,     # smallest drill-to-drill 1.270 (Proteus, TO-92), 1.232 with the KiCad TO-92 0.8 drills
    edge_clearance=0.5,   # copper to outline >= 0.521 (terminal H4)
    track=0.508,          # Default netclass
    via=1.27,             # Default netclass = the Proteus via 1.27 / 0.508
    via_drill=0.508,
)
# DRC error types that remain by design (p2k drc; STATUS.md "Phase 3", remaining DRC items).
# NOT accepted: clearance (the TO-92 pad 1 is round on Q1-Q9, user decision; 0 clearance errors).
DRC_ACCEPTED = {
    "courtyards_overlap": "KiCad courtyards vs the Proteus placement (36 pairs, parts exactly at the "
                          "Proteus positions): film caps and resistors packed closer than the KiCad "
                          "courtyards, Q7-Q9, terminals at film caps (the noval sockets U1-U3 are on "
                          "the bottom side since Phase 5)",
    "pth_inside_courtyard": "the same Proteus placement: 16 pads (R / C pads in neighbouring film-cap / "
                            "resistor courtyards; mounting holes H103-H105 and R1, C4, R18, C9, R30 in "
                            "the B-side noval socket courtyards: a THT pad is on both sides)",
}

# --- Recorded copper deviations (p2k.pcb: gerber_to_tracks, gerber_roundtrip) ---------

# Proteus Conductor draws not built (user decision 2026-11-20, "Design fixes 2026-11-20" in
# STATUS.md; reverses Phase 5 decision 3): the dangling stub of finding 16 and the zero-length /
# very short track pieces of finding 20. Each lies on its own net's copper (a joint of the 2010
# routing), so removing it changes no connection (assign_nets / check_board / DRC parity unchanged).
# Key (layer, x1, y1, x2, y2) in the IPC / Gerber frame (Y up), exactly as the Proteus draw; every
# entry must match a draw (gerber_to_tracks fails otherwise).
REMOVED_TRACKS = {
    ("B.Cu", 88.9, -0.762, 88.9, -0.6985):
        "finding 16: 0.0635 mm dangling stub inside the RLY4-13 track bend (Net-(U3B-G2); Proteus pin 2, Net-(RLY4B-COM13) before the relay design change), DRC track_dangling",
    ("F.Cu", -61.087, -1.905, -61.087, -1.905): "finding 20: zero-length draw on the RLY3 NC track (Net-(R16-Pad1))",
    ("F.Cu", -61.722, -22.225, -61.722, -22.225): "finding 20: zero-length draw on H4",
    ("F.Cu", -139.7635, -16.5735, -139.7635, -16.4465): "finding 20: 0.127 mm piece on PRE-GND",
    ("F.Cu", -130.81, -38.735, -130.8735, -38.7985): "finding 20: 0.090 mm piece on PRE-GND",
    ("F.Cu", -60.96, -1.905, -61.087, -1.905): "finding 20: 0.127 mm piece on the RLY3 NC track (Net-(R16-Pad1))",
    ("B.Cu", -18.87074, 24.13, -19.05, 24.13): "finding 20: 0.179 mm piece on H5",
    ("B.Cu", -114.427, -18.415, -114.3, -18.415): "finding 20: 0.127 mm piece on H4",
    ("B.Cu", -43.942, -6.858, -43.942, -6.985): "finding 20: 0.127 mm piece on PRE-GND",
}

# --- Phase 4 checks (p2k.ipc356_diff, p2k.gerber_roundtrip) ---------------------------

# KiCad footprint drills smaller than the Proteus drill, kept by the user (2026-11-20;
# STATUS.md "Decisions"). Matched within 0.005 mm; reported, not failed.
# With the pad sets (reason, refdes) both tools require the smaller drills of each pair to be
# exactly those parts' pads (80 holes: RLY1-RLY5 40, C1/C5/C7/C10 8, the 14 Orange Drops 28, C4/C14
# 4; was tools/check_drill_smaller.py, p2k candidate 26).
DRILL_SMALLER = {
    (1.143, 0.7): ("RLY1-RLY5: KiCad G5V-2 0.7 mm drills kept (Proteus 1.143 = 45 mil); user decision 2026-11-20",
                   {"RLY1", "RLY2", "RLY3", "RLY4", "RLY5"}),
    (1.143, 1.0): ("C1/C5/C7/C10: KiCad C_Rect 1.0 mm drills kept (Proteus 1.143); user decision 2026-11-20",
                   {"C1", "C5", "C7", "C10"}),
    (1.143, 1.1): ("Orange Drops C8, C11-C13, C16, C17, C19-C21, C23-C25, C27, C29: KiCad C_Rect 1.1 mm drills kept (Proteus 1.143); user decision 2026-11-20",
                   {"C8", "C11", "C12", "C13", "C16", "C17", "C19", "C20", "C21", "C23", "C24", "C25", "C27", "C29"}),
    (0.762, 0.75): ("C4/C14: KiCad C_Rect 0.75 mm drills kept (Proteus 0.762 = 30 mil); user decision 2026-11-20",
                    {"C4", "C14"}),
}
# The June 2010 fab Excellon drill file (source/fab_2010/etunen - CADCAM Drill.TXT: inch, 364 hits,
# same frame as the X2 export): gerber_roundtrip compares it with the Proteus plated drill gerber,
# read in its own unit (inch; R1: was converted to metric by tools/excellon_metric.py).
DRILL_EXCELLON = "source/fab_2010/etunen - CADCAM Drill.TXT"
# It lacks exactly the 2 vias added in October 2010 (STATUS.md "Phase 0": Q6-3 moved from net J1 to
# J4, and the PRE-GND reroute); each entry must match exactly one "not in the Excellon file" mismatch.
# The labels keep the report words of the former tools/roundtrip.py (p2k candidate 3).
EXCELLON_MISSING = {
    (33.02, -31.115, 0.508): "via on J4: Q6-3 top track -> bottom track to Q9-3 (October edit)",
    (-29.337, -42.545, 0.508): "via on PRE-GND: joins the bottom track end to the top PRE-GND track (October reroute)",
}
EXCELLON_MISSING_LABELS = dict(file="2010 Excellon file", items="expected October vias", source="tools/roundtrip.py")
