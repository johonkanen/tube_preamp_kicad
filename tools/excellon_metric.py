#!/usr/bin/env python3
"""Convert the June 2010 fab Excellon drill file (inch) to the metric form p2k.gerber_roundtrip reads.

  source/fab_2010/etunen - CADCAM Drill.TXT   M48 / INCH, tools TnnC<inch>, coordinates X+iiffff
                                              (2.4 inch, all digits written, explicit sign)
  -> reference/fab_2010_drill_metric.drl      M48 / METRIC, tools TnnC<mm, 4 decimals>, coordinates
                                              in 0.001 mm (4.3), same order, same tool numbers

Board-local: p2k.gerber_roundtrip.parse_excellon reads metric 4.3 files only and ignores the INCH
header line (it would read 1.3050 inch as 13.050 mm; STATUS.md "p2k candidates" 23). p2k_config.py
DRILL_EXCELLON points at the converted file. Positions are rounded to 0.001 mm (error <= 0.0005 mm,
the comparison tolerance is 0.05 mm); diameters keep 4 decimals (0.1181 inch = 2.9997 mm for the
3.0 mm holes, drill tolerance 0.005 mm).

Copied from the power amp pilot (~/dev/tube_power_amp_kicad/tools/excellon_metric.py); only the source
file name differs. This board's file: 7 tools, 364 holes (the October layout has 366: the two vias
added in October 2010 are missing, see tools/roundtrip.py).

Usage: python3 tools/excellon_metric.py [--check]
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source", "fab_2010", "etunen - CADCAM Drill.TXT")
DST = os.path.join(ROOT, "reference", "fab_2010_drill_metric.drl")


def convert():
    out, tools, hits, header, cur = [], {}, 0, True, None
    lines = [l.strip() for l in open(SRC, encoding="ascii")]
    if lines[:2] != ["M48", "INCH"]:
        raise SystemExit(f"excellon_metric: {SRC}: expected an M48 / INCH header, got {lines[:2]}")
    out += ["M48", "METRIC"]
    for line in lines[2:]:
        if not line:
            continue
        m = re.fullmatch(r"T(\d+)C(\d*\.\d+)", line)
        if m and header:
            tools[m[1]] = float(m[2]) * 25.4
            out.append(f"T{m[1]}C{tools[m[1]]:.4f}")
        elif line == "%" and header:
            header = False
            out.append("%")
        elif re.fullmatch(r"T(\d+)", line) and not header and line[1:] in tools:
            cur = line[1:]
            out.append(line)
        elif (m := re.fullmatch(r"X([+-]\d{6})Y([+-]\d{6})", line)) and cur:
            x, y = (round(int(v) * 2.54) for v in m.groups())    # 0.0001 inch -> um
            out.append(f"X{x:+07d}Y{y:+07d}")
            hits += 1
        elif line == "M30" and not header:
            out.append("M30")
        else:
            raise SystemExit(f"excellon_metric: {SRC}: unexpected line {line!r}")
    return "\n".join(out) + "\n", len(tools), hits


def main():
    text, ntools, hits = convert()
    rel = os.path.relpath(DST, ROOT)
    cur = open(DST).read() if os.path.exists(DST) else None
    if "--check" in sys.argv[1:]:
        if cur != text:
            print(f"excellon_metric: {rel} is not up to date (run tools/excellon_metric.py)")
            return 1
        print(f"excellon_metric: {rel} up to date ({ntools} tools, {hits} holes)")
        return 0
    with open(DST, "w") as f:
        f.write(text)
    print(f"excellon_metric: wrote {rel} ({ntools} tools, {hits} holes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
