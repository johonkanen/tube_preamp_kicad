# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/tube_preamp_kicad to KiCad 10: Phase 1
transcription of the 5 schematic sheets (model: Fable per playbook section 6). The preparation
is done (part map 163 parts, symbols, skeleton, check_all passes with 0/163 parts drawn).

Read, in this order: PLAN.md, STATUS.md ("Phase 1 preparation" with the pinout tables and its
**Transcription rules**, "Findings", "p2k candidates"), tools/p2k/CONVERSION_PLAYBOOK.md
(sections 1, 3 "Phase 1", 5), tools/p2k/README.md (sheetkit, compare_netlists, render_sheet),
tools/sheets/_common.py (part/sh_value/sym, term, P, place_mirrored, tube, relay),
lib/part_map.csv, reference/pin_nets_by_component.md and reference/pins_by_net.md. Run
tools/check_all.sh first and compare with STATUS.md "Last check output". Example sheet scripts
(read only, never change those repos): ~/dev/tube_power_amp_kicad/tools/sheets/sheet01-03.py and
its _common.py (same 2010 Proteus export, Phase 1 done), ~/dev/tube_psu_kicad/tools/sheets/.

Render the PDF pages first (pdftoppm -r 200 -png source/schematic_pdf/etunen.PDF
build/tmp/pdf/hi; zoom with -r 600 -x/-y/-W/-H where it is dense) and read them.

Transcribe one sheet at a time, in this order: 5 Supply filter (21 parts), 4 Tone stacks (39),
1 Input stage (36), 2 Second stage (33), 3 EQ stage (34). One script per sheet,
tools/sheets/sheetNN.py (NN = PDF page), rebuilding kicad/NN_*.kicad_sch from scratch, layout
close to the PDF (P() = PDF render position in 10 px units). Key rules (details in STATUS.md):
- symbols / values / refdes exactly from lib/part_map.csv (PAD_A-PAD_D = Proteus A-D, GTR_IN,
  POT1_1 ...; Q4 value NADA; the µ values are in the map); terminals with _common.term(), never
  sheetkit.terminal;
- net names = IPC spelling: the PDF's pre-gnd, sw1-sw3, h4/h5, j4 are PRE-GND, SW1-SW3, H4/H5,
  J4; global labels for PRE-GND, H4, H5, A-F, J1-J4, SW1-SW3, PRE1, EQ, EQ1-EQ3 (table in
  STATUS.md); PRE2 is a local label (sheet 2 only); every #000xx net is a plain wire (none
  crosses a sheet);
- terminal refdes are not net names: PAD_A-PAD_D are on J1-J4 (not on the B+ nets A-D);
- 12AX7 U1-U3: _common.tube() (3 units: A = pins 1-3, B = 6-8, C = heater 4/5; it flags the
  N/C pin 9); G5V-2 RLY1-RLY5: _common.relay() (coil 4/5, pole 1 COM 2 / NC 3 / NO 1, pole 2
  COM 6 / NC 7 / NO 8; find the pole by its COM net); J112: 1 = D, 2 = S, 3 = G, orientation per
  part from the STATUS.md table (Q2-Q6 have D on PRE-GND); C28/C33-C37 C_Polarized_12 (2 = +);
- 1.27 mm grid; helpers in _common.py for the three identical tone stacks (sheet 4) and the
  relay coil + diode block.
After each sheet: tools/p2k/bin/p2k render_sheet kicad/NN_*.kicad_sch (look at it next to
hi-N.png), tools/p2k/bin/p2k compare_netlists --allow-missing --sheet N, tools/erc.sh, then
tools/check_all.sh. Target per sheet: 0 missing on that sheet, 0 compare errors, 0 ERC errors
(warnings explained in STATUS.md; isolated global labels and split warnings for nets with pins on
undrawn sheets are expected until the other sheets exist). Commit and push after each sheet.
After the last sheet: drop --allow-missing in tools/check_all.sh; done = 163/163 parts, every
IPC net complete, 0 wrong-net pins, ERC 0 errors; negative-test once (e.g. a J1 global label on
a wrong pin -> compare fails).

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
temporary files in build/tmp; never run the KiCad AppImage with --version (use tools/p2k/bin/kipy
and tools/p2k/bin/kicad-cli). At the end: STATUS.md updated (per-sheet results, last check output,
findings, p2k candidates, decisions), README.md status line, next_prompt.md replaced with the
Phase 2 (footprints) prompt, commit and push (git push origin main). If something needs a user
decision, stop, record it in STATUS.md, commit and push, and report it.
```
