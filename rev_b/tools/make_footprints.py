#!/usr/bin/env python3
"""Footprints for the rev B preamp.

- rev_b/lib/tube_preamp_revb.pretty: the footprints KiCad has no stock part for (Faston PCB tabs
  per tube_amplifier_kicad docs/interfaces.md 4.1: 2 legs on 5.00 mm, 1.4 mm drill) and the noval
  socket of rev A (copied from lib/tube_preamp.pretty: the same Belton PCB socket, PCD 21 mm).
- rev_b/lib/footprint_map.csv: refdes -> footprint, from the fp of every line in make_bom.py (the
  one list where a package is chosen). sch_builder writes it into the Footprint field when
  tools/sheets/draw_all.py draws the sheets.
- rev_b/kicad/fp-lib-table.

Checks (needs kicad-cli for the netlist): every schematic part has a footprint, and every symbol
pin number has a pad of that number in its footprint and the other way round.

Usage: python3 -I rev_b/tools/make_footprints.py [--check]
"""
import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RB = os.path.dirname(HERE)
REPO = os.path.dirname(RB)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "jlc"))
import make_bom  # noqa: E402  (ITEMS only; the JLC search runs under __main__)

PROJECT = "tube_preamp_revb"
PRETTY = os.path.join(RB, "lib", PROJECT + ".pretty")
KICAD_CLI = os.path.join(REPO, "tools", "p2k", "bin", "kicad-cli")
SCH = os.path.join(RB, "kicad", PROJECT + ".kicad_sch")


def stock_dir():
    m = open(f"/tmp/p2k_kicad_mount.{os.getuid()}").read().strip()
    return os.path.join(m, "share", "kicad", "footprints")


def line(x0, y0, x1, y1, layer, w):
    return (f'\t(fp_line (start {x0:.3f} {y0:.3f}) (end {x1:.3f} {y1:.3f})\n'
            f'\t\t(stroke (width {w}) (type solid)) (layer "{layer}"))\n')


def rect(x0, y0, x1, y1, layer, w):
    return (line(x0, y0, x1, y0, layer, w) + line(x1, y0, x1, y1, layer, w) +
            line(x1, y1, x0, y1, layer, w) + line(x0, y1, x0, y0, layer, w))


def text(kind, val, x, y, layer, hide=False):
    h = " (hide yes)" if hide else ""
    return (f'\t(property "{kind}" "{val}" (at {x:.3f} {y:.3f} 0) (layer "{layer}"){h}\n'
            f'\t\t(effects (font (size 1 1) (thickness 0.15))))\n')


def faston(width, n, pitch=0.0):
    """n blade tabs of the given width, one pad number per tab (both legs), tabs side by side
    along x at `pitch`. Legs on 5.00 mm along the blade (y), 1.4 mm drill, 2.8 mm pads. The
    courtyard leaves room for an insulated push-on receptacle (about 8 x 11 mm)."""
    name = f"Faston_Tab_{width}mm_x{n}" + (f"_P{pitch:.2f}mm" if n > 1 else "")
    s = (f'(footprint "{name}"\n\t(version 20241229)\n\t(generator "make_footprints")\n\t(layer "F.Cu")\n'
         f'\t(descr "PCB blade (Faston) tab {width} mm, 2 legs on 5.00 mm, 1.4 mm drill (interfaces.md 4.1); {n} tab(s)")\n'
         f'\t(tags "faston quick connect blade tab")\n')
    s += text("Reference", "REF**", 0, -7.2, "F.SilkS")
    s += text("Value", name, 0, 7.5, "F.Fab")
    s += '\t(attr through_hole)\n'
    for i in range(n):
        x = i * pitch
        s += rect(x - 0.4, -width / 2, x + 0.4, width / 2, "F.Fab", 0.1)
        s += rect(x - 4.1, -5.85, x + 4.1, 5.85, "F.SilkS", 0.12)
        s += rect(x - 4.25, -6.0, x + 4.25, 6.0, "F.CrtYd", 0.05)
        for y in (-2.5, 2.5):
            s += (f'\t(pad "{i + 1}" thru_hole circle (at {x:.3f} {y:.3f}) (size 2.8 2.8) (drill 1.4)\n'
                  f'\t\t(layers "*.Cu" "*.Mask"))\n')
    s += f'\t(fp_text user "{i + 1 if n == 1 else "1"}" (at -3.0 0 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))\n'
    s += ')\n'
    return name, s


def build_library():
    os.makedirs(PRETTY, exist_ok=True)
    for args in ((4.8, 2, 15.0), (6.3, 2, 12.7), (6.3, 1)):
        name, s = faston(*args)
        open(os.path.join(PRETTY, name + ".kicad_mod"), "w").write(s)
    # The noval socket of rev A, with a round courtyard and outline (r 13.47 / 13.0 mm, the rectangle's
    # half width): the
    # socket is round, and the rectangle clipped the standoff holes beside it (H103-H105), which
    # carry the built board.
    v = open(os.path.join(REPO, "lib", "tube_preamp.pretty", "Valve_Noval_Belton_PCD21.00mm.kicad_mod")).read()
    v, n = re.subn(r'\t\(fp_poly\n\t\t\(pts\n[^\n]*\n\t\t\)\n\t\t\(stroke\n\t\t\t\(width 0\.05\)\n\t\t\t\(type solid\)\n'
                   r'\t\t\)\n\t\t\(fill no\)\n\t\t\(layer "F\.CrtYd"\)\n\t\)\n',
                   '\t(fp_circle (center 0 0) (end 13.47 0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"))\n', v)
    assert n == 1, "socket courtyard not found"
    v, n = re.subn(r'\t\(fp_line\n\t\t\(start [^)]*\)\n\t\t\(end [^)]*\)\n\t\t\(stroke\n\t\t\t\(width 0\.12\)\n'
                   r'\t\t\t\(type solid\)\n\t\t\)\n\t\t\(layer "F\.SilkS"\)\n\t\)\n', '', v)
    assert n == 4, "socket silk rectangle not found"
    v = v.replace('\t(fp_circle (center 0 0) (end 13.47 0)',
                  '\t(fp_circle (center 0 0) (end 13.0 0) (stroke (width 0.12) (type solid)) (fill no) (layer "F.SilkS"))\n'
                  '\t(fp_circle (center 0 0) (end 13.47 0)', 1)
    open(os.path.join(PRETTY, "Valve_Noval_Belton_PCD21.00mm.kicad_mod"), "w").write(v)
    open(os.path.join(RB, "kicad", "fp-lib-table"), "w").write(
        f'(fp_lib_table\n\t(version 7)\n\t(lib (name "{PROJECT}")(type "KiCad")(uri "${{KIPRJMOD}}/../lib/{PROJECT}.pretty")'
        f'(options "")(descr "rev B project footprints (tools/make_footprints.py)"))\n)\n')


def footprint_map():
    fp = {}
    for it in make_bom.ITEMS:
        for r in it["refs"]:
            if r in fp:
                raise SystemExit(f"{r} is on two BOM lines")
            fp[r] = it["fp"]
    with open(os.path.join(RB, "lib", "footprint_map.csv"), "w", newline="") as f:
        f.write("# Generated by tools/make_footprints.py from tools/make_bom.py; do not edit.\n")
        w = csv.writer(f)
        w.writerow(["refdes", "footprint"])
        for r in sorted(fp, key=lambda s: (re.sub(r"\d", "", s), int(re.sub(r"\D", "", s) or 0))):
            w.writerow([r, fp[r]])
    return fp


def pads(lib_id):
    lib, name = lib_id.split(":")
    d = PRETTY if lib == PROJECT else os.path.join(stock_dir(), lib + ".pretty")
    txt = open(os.path.join(d, name + ".kicad_mod")).read()
    return {p for p in re.findall(r'\(pad "([^"]*)"', txt) if p}


def check(fp):
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "n.xml")
        subprocess.run([KICAD_CLI, "sch", "export", "netlist", "--format", "kicadxml", "-o", out, SCH],
                       check=True, capture_output=True)
        t = ET.parse(out)
    libpins = {}
    for lp in t.iter("libpart"):
        libpins[lp.get("part")] = {p.get("num") for p in lp.iter("pin")}
    bad = 0
    refs = set()
    for c in t.iter("comp"):
        ref = c.get("ref")
        refs.add(ref)
        f = c.findtext("footprint") or ""
        if f != fp.get(ref):
            print(f"{ref}: schematic footprint '{f}', map '{fp.get(ref)}' (rerun draw_all.py)")
            bad += 1
            continue
        pins = libpins[c.find("libsource").get("part")]
        p = pads(f)
        if pins != p:
            print(f"{ref}: symbol pins {sorted(pins)} vs pads {sorted(p)} of {f}")
            bad += 1
    extra = set(fp) - refs
    if extra:
        print("on the BOM but not in the schematic:", ", ".join(sorted(extra)))
        bad += 1
    print(f"{len(refs)} parts, {len(set(fp.values()))} footprints, {bad} problems")
    return bad


def main():
    build_library()
    fp = footprint_map()
    if "--check" in sys.argv:
        return 1 if check(fp) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
