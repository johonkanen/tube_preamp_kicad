#!/usr/bin/env python3
"""Generate lib/part_map.csv: refdes -> PDF page, symbol, value, Proteus device and package.

Adapted from the power amp pilot (~/dev/tube_power_amp_kicad/tools/make_part_map.py).
Sources (STATUS.md "Phase 1 preparation"):
  refdes   reference/ipc356_pads.json (`refdes` = KiCad name, `refdes_proteus` = Proteus name).
           No off-board parts on this board: every part drawn in the PDF has IPC pads (OFF_BOARD
           stays empty; the refdes-like PDF words without pads are net labels EQ1-EQ3, J1-J4,
           PRE1, PRE2 and value text J112 / "MMK J04 1µ").
  value    schematic value from ROOT.DSN in source/etunen.pdsprj (= the PDF)
  device, package   layout record in ROOT.LYT
  sheet    PDF page whose text layer has the refdes; PAGE_OVERRIDES for the ambiguous ones
  lib_id   SYMBOL_BY_DEVICE (Proteus device -> lib/tube_preamp.kicad_sym symbol)

Board-local workarounds (STATUS.md "p2k candidates"):
  - SINGLE_LETTER_PARTS: the terminals A-D. p2k.pdsprj.dsn_values raises on single-letter refdes
    (they match unrelated one-letter strings in ROOT.DSN), so pdsprj is called without them and
    their value / device / package come from here (ROOT.LYT records read by hand:
    "A" TERMINAL TERMINAL PIN J1, ... "D" ... J4; ROOT.DSN COMPONENT VALUE TERMINAL).
  - LATIN1_PARTS: values (and for C28/C33-C37 the whole layout record) with a Latin-1 µ (0xB5),
    which p2k.pdsprj drops (pilot p2k candidate 1). Values from the PDF text layer; device /
    package of C28/C33-C37 from the ROOT.LYT bytes ("C28" "22\\xb5F 450V" "22\\xb5F 450V"
    "ELEC D16 R7.5" PRE-GND A). The script fails if pdsprj starts reading one of them.

  tools/make_part_map.py           write lib/part_map.csv
  tools/make_part_map.py --check   fail if lib/part_map.csv is not up to date
"""
import csv
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2k"))  # proteus2kicad
from p2k import board, pdftext, pdsprj  # noqa: E402

PRJ = board.path("source", "etunen.pdsprj")
PDF = board.path("source", "schematic_pdf", "etunen.PDF")
OUT = board.path("lib", "part_map.csv")
LIB = board.config().PROJECT

C, CP, R = "C", "C_Polarized", "R"
SYMBOL_BY_DEVICE = {
    # film / ceramic capacitors
    "22N XICON": C, "100N XICON": C, "MMK J01": C, "MMK J04 5MM": C, "CERAMIC56P": C,
    "1N ORANGE DROP": C, "2N2 ORANGE DROP": C, "3N3 ORANGE DROP": C, "4N7 ORANGE DROP": C,
    # electrolytics: C2 / C30 have Proteus pins +/-, C28 / C33-C37 pins 1 (-) / 2 (+)
    "HITEMP10U50V": CP, "MINELECT10U50V": CP, "22µF 450V": "C_Polarized_12",
    "MINRES100K": R, "METALFILM1K": R,
    "1N4001": "D",
    "J112": "J112",
    "G5V-2(HI)": "G5V-2",
    "12AX7": "12AX7",
    "TERMINAL": "PIN",
}

# Parts drawn in the PDF without a layout part / IPC pads. None on this board (checked: every
# refdes-like PDF word is an IPC refdes, a net label or value text; 47 TERMINAL words = the 47
# terminals of the IPC).
OFF_BOARD = {}

# p2k candidate 2: single-letter refdes that p2k.pdsprj cannot read (Proteus refdes -> record).
SINGLE_LETTER_PARTS = {k: {"value": "TERMINAL", "device": "TERMINAL", "package": "PIN"} for k in "ABCD"}

# pilot p2k candidate 1: Latin-1 µ values. value: from the PDF; device / package: None = take the
# ROOT.LYT record that pdsprj reads.
_E22 = {"value": "22µF 450V", "device": "22µF 450V", "package": "ELEC D16 R7.5"}
LATIN1_PARTS = {
    "C4": {"value": "MMK J04 1µ", "device": None, "package": None},    # lyt value cut to "MMK J04 1"
    "C14": {"value": "1µ mmk", "device": None, "package": None},
    "C30": {"value": "22µ", "device": None, "package": None},
    "C28": _E22, "C33": _E22, "C34": _E22, "C35": _E22, "C36": _E22, "C37": _E22,
}

# Refdes whose PDF text-layer hits are ambiguous (resolved on the page renders):
PAGE_OVERRIDES = {
    "A": 5, "B": 5, "C": 5, "D": 5,  # the terminals (pads on J1-J4); A-D on pages 1/2 are labels of the B+ nets A-D
    "H4": 3, "H5": 3,                # the terminals (page 3, at U3); H4 / H5 on pages 1-3 are also net labels
}

FIELDS = ["refdes", "sheet", "lib_id", "value", "device", "package", "proteus_refdes", "off_board"]


def build():
    ipc = json.load(open(board.path("reference", "ipc356_pads.json")))
    kicad = {}
    for p in ipc["pads"]:
        if p["kind"] == "pad":
            kicad[p["refdes_proteus"]] = p["refdes"]
    for ref in OFF_BOARD:
        assert ref not in kicad, f"OFF_BOARD part {ref} has IPC pads"
        kicad[ref] = OFF_BOARD[ref][0]
    refs = set(kicad)
    readable = refs - set(SINGLE_LETTER_PARTS)
    values = pdsprj.dsn_values(PRJ, readable)
    parts = pdsprj.lyt_parts(PRJ, readable)
    pages = pdftext.refdes_pages(pdftext.pdf_words(PDF), refs)
    errors = []
    rows = []
    for ref in sorted(set(SINGLE_LETTER_PARTS) - refs):
        errors.append(f"SINGLE_LETTER_PARTS: {ref} is not a refdes")
    for ref in sorted(refs):
        page = PAGE_OVERRIDES.get(ref)
        if page is None:
            if len(pages[ref]) != 1:
                errors.append(f"{ref}: PDF pages {pages[ref]} (add to PAGE_OVERRIDES)")
                continue
            page = pages[ref][0]
        elif page not in pages[ref]:
            errors.append(f"{ref}: PAGE_OVERRIDES page {page} not among the PDF hits {pages[ref]}")
        if ref in SINGLE_LETTER_PARTS:
            fix = SINGLE_LETTER_PARTS[ref]
            value, dev, pkg = fix["value"], fix["device"], fix["package"]
        elif ref in LATIN1_PARTS:
            fix = LATIN1_PARTS[ref]
            if values.get(ref) is not None:
                errors.append(f"{ref}: pdsprj now reads the value {values[ref]!r}: drop LATIN1_PARTS")
            if fix["device"] is None:
                value, dev, pkg = fix["value"], parts[ref]["device"], parts[ref]["package"]
            else:
                if ref in parts:
                    errors.append(f"{ref}: pdsprj now reads the layout record {parts[ref]}: drop LATIN1_PARTS")
                value, dev, pkg = fix["value"], fix["device"], fix["package"]
        elif ref in OFF_BOARD:
            if ref in parts:
                errors.append(f"{ref}: OFF_BOARD part has a layout record")
            value, dev, pkg = values.get(ref), OFF_BOARD[ref][2], ""
        else:
            value, dev, pkg = values.get(ref), parts[ref]["device"], parts[ref]["package"]
        if not value:
            errors.append(f"{ref}: no schematic value")
            continue
        if ref in OFF_BOARD:
            sym = OFF_BOARD[ref][1]
        elif dev in SYMBOL_BY_DEVICE:
            sym = SYMBOL_BY_DEVICE[dev]
        else:
            errors.append(f"{ref}: no symbol for Proteus device {dev!r}")
            continue
        rows.append({"refdes": kicad[ref], "sheet": page, "lib_id": f"{LIB}:{sym}", "value": value,
                     "device": dev, "package": pkg, "proteus_refdes": ref if ref != kicad[ref] else "",
                     "off_board": "yes" if ref in OFF_BOARD else ""})
    for ref in sorted(set(PAGE_OVERRIDES) - refs):
        errors.append(f"PAGE_OVERRIDES: {ref} is not a refdes")
    if errors:
        sys.exit("make_part_map:\n  " + "\n  ".join(errors))
    key = lambda r: (r["sheet"], [(0, int(t), "") if t.isdigit() else (1, 0, t)
                                  for t in re.findall(r"\d+|\D+", r["refdes"])])
    rows.sort(key=key)
    buf = io.StringIO()
    buf.write("# Generated by tools/make_part_map.py - do not edit. sheet = Proteus PDF page;"
              " value = schematic value (ROOT.DSN; the µ values and A-D by override); device/package ="
              " Proteus layout record; Q4 value NADA as in the schematic (STATUS.md finding 1)\n")
    w = csv.DictWriter(buf, fieldnames=FIELDS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue(), rows


def main():
    text, rows = build()
    rel = os.path.relpath(OUT, board.root())
    per = {}
    for r in rows:
        per[r["sheet"]] = per.get(r["sheet"], 0) + 1
    summary = f"{len(rows)} parts ({sum(not r['off_board'] for r in rows)} on the board); per sheet " + \
        " ".join(f"{s}:{n}" for s, n in sorted(per.items()))
    if "--check" in sys.argv:
        if not os.path.exists(OUT) or open(OUT, encoding="utf-8").read() != text:
            print(f"make_part_map: {rel} is out of date, run tools/make_part_map.py")
            return 1
        print(f"make_part_map: {rel} up to date, {summary}")
        return 0
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(text)
    print(f"wrote {rel}: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
