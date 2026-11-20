#!/usr/bin/env python3
"""Generate lib/tube_preamp.kicad_sym, the project symbol library (helpers: p2k.symgen).

Adapted from the power amp pilot (~/dev/tube_power_amp_kicad/tools/gen_symbols.py). Pin numbers
equal the Proteus/IPC pin ids (STATUS.md "Phase 1 preparation"). All part symbols are copied
from the KiCad 10 standard library (flattened, pins renumbered where needed). The Proteus pin
definitions in ROOT.DSN (read by hand, pilot p2k candidate 4):
  12AX7 (*PINOUT 9-PIN BELTON NOVAL)  A1=1 G1=2 K1=3 H1=4 H2=5 A2=6 G2=7 K2=8 HCT=9;
                                      pin 9 is N/C in the IPC (U1-U3)
  J112 (device $PINSHORT, TO92)       D=1 S=2 G=3   (= KiCad Q_NJFET_DSG; source / drain swap per part
                                      on the board, see STATUS.md: follow the IPC per refdes)
  G5V-2(HI) (*PINOUT G5V-2(HI))       AC1=1 COM1=2 NC1=3 DC1=4 DC2=5 COM2=6 NC2=7 AC2=8
                                      (AC = the make / normally open contact, DC = coil)
  1N4001                              A, K
  electrolytics                       C2 / C30: +, - ; C28 / C33-C37 (*PINOUT ELEC D16 R7.5): 1 = -, 2 = +
No power symbols: the IPC has no =POWER nets.

Run:  tools/gen_symbols.py           (needs the AppImage mount for the std libs)
      tools/gen_symbols.py --check   (fail if lib/tube_preamp.kicad_sym is not up to date)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2k"))  # proteus2kicad
from p2k.symgen import *  # noqa: E402,F401,F403
from p2k.symgen import run  # noqa: E402

def pin_types(sym, types):
    """Set the electrical type of pins {number: type}."""
    seen = set()
    for pin in walk(sym, "pin"):
        num = find(pin, "number")[1]
        if num in types:
            pin[1] = Sym(types[num])
            seen.add(num)
    assert seen == set(types), (sym[1], set(types) - seen)
    return sym


def swap_units(sym, a, b):
    """Swap the unit numbers a and b of the sub-symbols (NAME_<unit>_<style>)."""
    name = sym[1]
    for sub in find_all(sym, "symbol"):
        unit, style = sub[1][len(name) + 1:].split("_")
        if unit in (str(a), str(b)):
            sub[1] = f"{name}_{b if unit == str(a) else a}_{style}"
    return sym


def hide_pin_names(sym):
    """Pin names stay in the symbol (Proteus names, for the netlist / ERC texts) but are not drawn."""
    sym[:] = [c for c in sym if not (isinstance(c, list) and c and c[0] == "pin_names")]
    sym.insert(2, [Sym("pin_names"), [Sym("offset"), 0], [Sym("hide"), Sym("yes")]])
    return sym


def ecc83():
    # KiCad Valve:ECC83 (extends ECC81): unit 1 = triode 6/7/8, unit 2 = triode 1/2/3, unit 3 =
    # heater 4/5/9, envelope drawn for every unit. Units 1 and 2 are swapped here so that unit 1 (A)
    # is the Proteus element 1 (A1 G1 K1 = pins 1 2 3) and unit 2 (B) is element 2 (A2 G2 K2 =
    # 6 7 8); unit 3 (C) stays the heater. Names -> Proteus names. Pin types: anode / cathode /
    # heater passive (KiCad: output / bidirectional / power_in; the heater nets H4/H5 and the
    # cathode nets have only passive drivers and ERC would report power_in pins undriven, pilot
    # p2k candidate 9); grid stays input. Pin 9 (heater centre tap) is N/C in Proteus: passive
    # with a no-connect flag in the schematic (_common.tube() places it). Not type no_connect:
    # KiCad 10 keeps a no_connect pin in its own unconnected-(...) net even when a wire joins it
    # (ERC only warns no_connect_connected), so compare_netlists could not see such a mistake;
    # a passive pin on a wire joins the net and compare reports the N/C mismatch.
    sym = from_std("Valve", "ECC83", "12AX7", "U", desc="12AX7 / ECC83 double triode, noval; Proteus pin ids "
                   "A1=1 G1=2 K1=3 H1=4 H2=5 A2=6 G2=7 K2=8 HCT=9 (N/C: no-connect flag); unit A = pins 1-3, B = 6-8, C = heater",
                   pins={str(n): str(n) for n in range(1, 10)},
                   names={"1": "A1", "2": "G1", "3": "K1", "4": "H1", "5": "H2", "6": "A2", "7": "G2",
                          "8": "K2", "9": "HCT"})
    swap_units(sym, 1, 2)
    return pin_types(sym, {"1": PAS, "3": PAS, "6": PAS, "8": PAS, "4": PAS, "5": PAS, "9": PAS})


def build():
    syms = [
        from_std("Device", "R", "R", "R", "R"),
        from_std("Device", "C", "C", "C", "C"),
        from_std("Device", "C_Polarized", "C_Polarized", "C", "C", desc="Polarized capacitor, Proteus pins +/-",
                 pins={"1": "+", "2": "-"}, names={"+": "+", "-": "-"}),
        from_std("Device", "C_Polarized", "C_Polarized_12", "C", "C",
                 desc="Polarized capacitor, Proteus pins 1 = -, 2 = + (package ELEC D16 R7.5)",
                 pins={"1": "2", "2": "1"}, names={"2": "+", "1": "-"}),
        from_std("Device", "D", "D", "D", desc="Diode, Proteus pins A/K", pins={"1": "K", "2": "A"}),
        from_std("Device", "Q_NJFET_DSG", "J112", "Q", "J112",
                 desc="N-channel JFET J112, TO-92; Proteus ids 1=D 2=S 3=G"),
        hide_pin_names(from_std("Relay", "G5V-2_Split", "G5V-2", "RLY", "G5V-2(HI)",
                 desc="Omron G5V-2 DPDT relay; Proteus ids DC1=4 DC2=5 (coil, unit A), "
                      "COM1=2 NC1=3 AC1(NO)=1 (unit B), COM2=6 NC2=7 AC2(NO)=8 (unit C)",
                 pins={"1": "4", "16": "5", "4": "2", "6": "3", "8": "1", "13": "6", "11": "7", "9": "8"},
                 names={"4": "DC1", "5": "DC2", "2": "COM1", "3": "NC1", "1": "AC1", "6": "COM2",
                        "7": "NC2", "8": "AC2"})),
        ecc83(),
        from_std("Connector", "TestPoint", "PIN", "J", "TERMINAL",
                 desc="Proteus TERMINAL: one fly-lead pad (package PIN)"),
    ]
    return syms


if __name__ == "__main__":
    sys.exit(run(build))
