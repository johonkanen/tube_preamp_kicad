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
