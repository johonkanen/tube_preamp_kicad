#!/usr/bin/env python3
"""Create the rev B KiCad project skeleton: kicad/tube_preamp_revb.kicad_pro, the root sheet with
one sheet symbol per sub-sheet, empty sub-sheets (the sheet scripts fill them), the sym-lib-table.
Re-running keeps existing sub-sheets (their contents belong to the sheet scripts)."""
import json
import os
import uuid

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = os.path.join(HERE, "kicad")
PROJECT = "tube_preamp_revb"
SHEETS = [("01_input", "01 Input, S1, channel gain networks"),
          ("02_gain_stages", "02 S2, S5, S3, switched voicing"),
          ("03_tone_output", "03 CF, Baxandalls, post gain, S4, output"),
          ("04_control", "04 Switch control"),
          ("05_supply", "05 B+ regulator, decoupling, heaters, connectors")]
NS = uuid.uuid5(uuid.NAMESPACE_URL, PROJECT)


def u(k):
    return str(uuid.uuid5(NS, k))


def title(t):
    return (f'\t(title_block\n\t\t(title "{t}")\n\t\t(company "Tube amplifier")\n\t\t(rev "rev B (design D) - first draft")\n'
            f'\t\t(comment 1 "From tube_amplifier_kicad sim/preamp_voicing (design D) and docs/preamp_board_plan.md")\n\t)\n')


def main():
    os.makedirs(K, exist_ok=True)
    root_uuid = u("root")
    s = (f'(kicad_sch\n\t(version 20260101)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n'
         f'\t(uuid "{root_uuid}")\n\t(paper "A3")\n' + title("Tube preamp rev B") + '\t(lib_symbols)\n')
    for i, (f, name) in enumerate(SHEETS):
        x, y = 25.4 + (i % 3) * 127.0, 38.1 + (i // 3) * 40.64
        s += (f'\t(sheet\n\t\t(at {x} {y})\n\t\t(size 101.6 20.32)\n\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n'
              f'\t\t(stroke\n\t\t\t(width 0.1524)\n\t\t\t(type solid)\n\t\t)\n\t\t(fill\n\t\t\t(color 0 0 0 0)\n\t\t)\n\t\t(uuid "{u("sheet" + f)}")\n'
              f'\t\t(property "Sheetname" "{name}"\n\t\t\t(at {x} {y - 0.7} 0)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.524 1.524)\n\t\t\t\t)\n\t\t\t\t(justify left bottom)\n\t\t\t)\n\t\t)\n'
              f'\t\t(property "Sheetfile" "{f}.kicad_sch"\n\t\t\t(at {x} {y + 20.92} 0)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left top)\n\t\t\t)\n\t\t)\n'
              f'\t\t(instances\n\t\t\t(project "{PROJECT}"\n\t\t\t\t(path "/{root_uuid}"\n\t\t\t\t\t(page "{i + 2}")\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')
    s += '\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n'
    open(os.path.join(K, f"{PROJECT}.kicad_sch"), "w").write(s)
    for f, name in SHEETS:
        p = os.path.join(K, f + ".kicad_sch")
        if not os.path.exists(p):
            open(p, "w").write(f'(kicad_sch\n\t(version 20260101)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n'
                               f'\t(uuid "{u("file" + f)}")\n\t(paper "A2")\n' + title("Tube preamp rev B - " + name[3:]) +
                               '\t(lib_symbols)\n\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n')
    pro = {"meta": {"filename": f"{PROJECT}.kicad_pro", "version": 3}, "schematic": {}, "board": {},
           "sheets": [[u("root"), "Root"]] + [[u("sheet" + f), n] for f, n in SHEETS]}
    json.dump(pro, open(os.path.join(K, f"{PROJECT}.kicad_pro"), "w"), indent=2)
    open(os.path.join(K, "sym-lib-table"), "w").write(
        f'(sym_lib_table\n\t(version 7)\n\t(lib (name "{PROJECT}")(type "KiCad")(uri "${{KIPRJMOD}}/../lib/{PROJECT}.kicad_sym")(options "")(descr "rev B symbols, from KiCad stock libraries (tools/make_lib.py)"))\n)\n')


if __name__ == "__main__":
    main()
