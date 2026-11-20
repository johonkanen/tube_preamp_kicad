#!/usr/bin/env python3
"""Build lib/tube_preamp_revb.kicad_sym from KiCad's standard symbol libraries: the symbols the
rev B sheets use, flattened (KiCad's derived 'extends' symbols resolved, since a schematic's
lib_symbols needs them whole)."""
import copy
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "..", "tools", "p2k"))
from p2k.sexpr import Sym, find, find_all, load, save  # noqa: E402

KICAD = os.environ.get("KICAD_SYMBOLS", "/mnt/c/Program Files/KiCad/10.0/share/kicad/symbols")
WANT = [
    ("Device", "R"), ("Device", "C"), ("Device", "C_Polarized"), ("Device", "D"), ("Device", "D_Zener"),
    ("Device", "Q_NMOS"), ("Device", "Q_NMOS_Depletion"), ("Device", "Q_NPN"),
    ("Valve", "ECC83"), ("Transistor_FET", "MMBFJ113"), ("Transistor_FET", "2N7002"),
    ("Relay", "G6K-2"), ("Interface_Expansion", "MCP23S17x-x-SS"), ("Transistor_Array", "ULN2003"),
    ("Analog_Switch", "DG411xY"), ("74xGxx", "74LVC1G08"),
    ("Connector_Generic", "Conn_02x07_Odd_Even"), ("Connector_Generic", "Conn_02x13_Odd_Even"),
    ("Connector_Generic", "Conn_01x02"), ("Connector_Generic", "Conn_01x03"),
    ("power", "GND"), ("power", "+5V"), ("power", "+15V"), ("power", "-15V"), ("power", "PWR_FLAG"),
]
_cache = {}


def library(name):
    if name not in _cache:
        _cache[name] = {s[1]: s for s in find_all(load(os.path.join(KICAD, name + ".kicad_sym")), "symbol")}
    return _cache[name]


def flat(libname, name):
    s = copy.deepcopy(library(libname)[name])
    ext = find(s, "extends")
    if not ext:
        return s
    base = flat(libname, ext[1])
    out = copy.deepcopy(base)
    out[1] = name
    for sub in find_all(out, "symbol"):
        sub[1] = sub[1].replace(ext[1] + "_", name + "_", 1)
    props = {p[1]: p for p in find_all(s, "property")}
    for i, c in enumerate(out):
        if isinstance(c, list) and c and c[0] == "property" and c[1] in props:
            out[i] = props.pop(c[1])
    for p in props.values():
        out.insert(2, p)
    return out


def main():
    lib = [Sym("kicad_symbol_lib"), [Sym("version"), 20251024], [Sym("generator"), "make_lib"],
           [Sym("generator_version"), "10.0"]]
    for libname, name in WANT:
        lib.append(flat(libname, name))
    save(os.path.join(HERE, "lib", "tube_preamp_revb.kicad_sym"), lib)
    for libname, name in WANT:
        s = flat(libname, name)
        pins = []
        for sub in find_all(s, "symbol"):
            for p in find_all(sub, "pin"):
                num, nm = find(p, "number"), find(p, "name")
                pins.append(f"{num[1]}={nm[1]}" if num and nm else "?")
        print(f"{name}: " + " ".join(pins))


if __name__ == "__main__":
    main()
