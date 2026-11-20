# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/tube_preamp_kicad to KiCad 10: Phase 2 (footprints;
model: Opus per playbook section 6). Phases 0-1 are done: 5 sheets, 163/163 parts, the KiCad
netlist equals the IPC netlist (98 nets, 0 wrong-net pins), ERC 0 errors / 0 warnings;
tools/check_all.sh passes (comparison through the board-local wrapper tools/compare.py).

Read, in this order: PLAN.md, STATUS.md (phase table, "Phase 0" pad / drill families and the
via / hole inventory, "Phase 1 preparation" pinout tables, "Phase 1 transcription", "Findings"
esp. 7, 8, "p2k candidates", "Decisions"), tools/p2k/CONVERSION_PLAYBOOK.md (sections 1, 3
"Phase 2", 5), tools/p2k/README.md (footprints, check_footprints; config keys
FOOTPRINT_PAD_SIZES, OFF_BOARD_PARTS, HOLE_FOOTPRINT), lib/part_map.csv (device / package
columns), reference/ipc356_pads.csv. Run tools/check_all.sh first and compare with STATUS.md
"Last check output" (ALL CHECKS PASSED). Examples (read only, never change those repos):
~/dev/tube_power_amp_kicad/tools/gen_footprints.py and its STATUS.md "Phase 2" (same 2010
Proteus export: single-pad terminals, 2 W resistors, electrolytics, plated mounting holes),
~/dev/tube_psu_kicad/tools/gen_footprints.py.

Do:
1. tools/gen_footprints.py (RULES, PROJECT; p2k.footprints.run) -> lib/footprint_map.csv and
   lib/tube_preamp.pretty: a footprint for each of the 163 parts by symbol + IPC pad pattern
   (pad count, span, pad size, drill). Families (STATUS.md Phase 0): Q1-Q9 TO92 (1.524 / 0.762),
   small R / C 1.778 / 0.762, C2 / C30 2.032 / 0.762, D1-D5 / D8 / D9 DO41 and the 2 W resistors
   2.286 / 1.016, RLY1-RLY5 G5V-2 and the film / electrolytic capacitors 2.54 / 1.143 (several
   lead spacings: 22N / 100N XICON, MMK 2.5*7.2, MMK J04, ORANGE DROP, CAP20, ELEC D16 R7.5,
   ELEC-RAD10, 22U 100V), 47 single-pad terminals 3.048 / 1.524, U1-U3 noval sockets
   4.318 / 1.727 (9-PIN BELTON NOVAL), 13 plated 3.0 mm mounting holes with 6.35 mm pads
   (board-only footprints), 14 vias (Phase 3). KiCad library footprints where the pads fit,
   derived / built project footprints otherwise. Default FOOTPRINT_PAD_SIZES = "kicad".
2. p2k check_footprints (and kipy -m p2k.check_footprints --pcbnew): every part fits the IPC
   pads within 0.05 mm; reports/footprint_fit.csv and footprint_pads.csv. Pin-order check of
   the unmoved KiCad base footprints: J112 TO92 (Proteus D = 1, S = 2, G = 3 against the JEDEC
   TO-92 pad order; both drain / source orientations are on the board, finding 8), G5V-2
   (Proteus 1-8 against Omron 1 / 4 / 6 / 8 / 9 / 11 / 13 / 16; mapping in STATUS.md), the noval
   socket (pin 1-9 order and rotation direction: top or bottom view, cf. the pilot's octal
   socket finding), DO41, the polarized capacitors (C28 / C33-C37: pin 2 = +; C2 / C30).
3. Re-run the five sheet scripts so that the Footprint fields are filled from the map
   (tools/sheets/sheet01.py ... sheet05.py; two runs byte-identical), then tools/check_all.sh.
4. Add the steps to tools/check_all.sh (gen_footprints --check, check_footprints) and
   negative-test them (a wrong footprint, a shifted pad, a swapped pin number -> fail; restore).

Done when: every part fits <= 0.05 mm, map and library up to date, check_all passes. Report
pinout oddities found by the fit and the pad size / drill differences KiCad vs Proteus.

Open user questions (do not decide them): which values are on the built board for R13, R22,
R27, R30, R34, R51 and Q4 (findings 1, 7, 11; schematic values are used); pad sizes only if
DRC forces them (Phase 3); if the noval socket only fits mirrored (bottom view), record it and
ask, as on the power amp's octal sockets.

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
temporary files in build/tmp; never run the KiCad AppImage with --version (use tools/p2k/bin/kipy
and tools/p2k/bin/kicad-cli). At the end: STATUS.md updated (results, last check output,
findings, p2k candidates, decisions), README.md status line, next_prompt.md replaced with the
Phase 3 (PCB) prompt, commit and push (git push origin main). If something needs a user
decision, stop, record it in STATUS.md, commit and push, and report it.
```
