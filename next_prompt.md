# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/tube_preamp_kicad to KiCad 10: Phase 1 preparation
(part map, symbols, skeleton, compare/ERC in check_all). Phase 0 is done (163 parts, 98 nets,
check_all passes).

Read, in this order: PLAN.md, STATUS.md (phase table, "Phase 0" incl. "Notes for the later
phases", "Findings", "p2k candidates", "Decisions"), tools/p2k/CONVERSION_PLAYBOOK.md (sections 1,
3 "Phase 1", 5), tools/p2k/README.md (check_symbols, compare_netlists, make_skeleton, symgen,
sheetkit, pdsprj, pdftext; lib/part_map.csv columns). Run tools/check_all.sh first and compare
with STATUS.md "Last check output". Render the PDF: pdftoppm -r 200 -png
source/schematic_pdf/etunen.PDF build/tmp/pdf/hi.

The power amp board (~/dev/tube_power_amp_kicad, same 2010 Proteus export, Phase 1 done) is the
pilot: READ ONLY, never change it. Reuse its pieces (copy and adapt into this repo):
- tools/make_part_map.py -> lib/part_map.csv (SYMBOL_BY_DEVICE, PAGE_OVERRIDES, OFF_BOARD,
  LATIN1_PARTS for the µ values; here also an override for the single-letter pads A-D, because
  p2k.pdsprj.dsn_values raises on them: STATUS.md p2k candidate 2);
- tools/gen_symbols.py -> lib/tube_preamp.kicad_sym (KiCad std symbols renumbered to the IPC
  ids; ERC pin types set to passive where parallel / passive-only nets need it, pilot p2k
  candidate 9);
- tools/erc.sh, tools/check_all.sh step list, tools/sheets/_common.py (term(), place_mirrored(),
  P() coordinate helper, the per-channel helper pattern);
- its STATUS.md "Phase 1 preparation" and "Transcription rules" (layout of the rules section),
  and its p2k candidates 3, 6, 7, 8 (terminal symbol/value, mirroring, terminal text
  justification, multi-unit valve symbols).
Reference conversion: ~/dev/tube_psu_kicad (read only).

Do:
1. lib/part_map.csv: 163 parts (refdes = KiCad refdes from reference/ipc356_pads.json; PAD_A-
   PAD_D, GTR_IN, POT1_1 ... per p2k_config.KICAD_REFDES), sheet = PDF page (p2k.pdftext; resolve
   the terminal names that also appear as net labels: A-D, SW1-SW3, H4, H5 are terminals on sheet
   5 / 3 but labels elsewhere), value from ROOT.DSN (µ values and A-D by override; Q4 is `NADA`
   in the schematic, STATUS.md finding 1: keep it and note it), device/package from ROOT.LYT.
   Check whether any part is drawn in the PDF but not on the board (OFF_BOARD).
2. Symbols: 12AX7 (decide the unit split up front: KiCad Valve:ECC83 has 3 units; pin 9 is N/C
   in the IPC), J112 (N-JFET, IPC pins 1/2/3 with gate = 3; source/drain vary per part: read the
   Proteus device pinout from ROOT.DSN by hand, pilot p2k candidate 4), G5V-2(HI) relay (8 IPC
   pins: map them to the DPDT contacts and coil from the PDF and the IPC nets), 1N4001 (A/K),
   electrolytics (+/- or 1/2: C28/C33-C37 use pins 1/2 in the PDF), R, C, TERMINAL (one PIN symbol).
3. tools/p2k/bin/p2k make_skeleton -> kicad/ (5 sheets from p2k_config.SHEETS).
4. tools/check_all.sh: + part map --check, gen_symbols --check, check_symbols, ERC, compare_netlists
   --allow-missing. Smoke test on a scratch copy in build/tmp (one tube, a relay, a terminal,
   a global label), negative tests, then delete it.
5. Write the transcription rules into STATUS.md (net names = IPC spelling, lower-case PDF labels,
   global labels for the cross-sheet nets, terminal refdes are not net names, N/C pins, grid,
   one script per sheet tools/sheets/sheetNN.py, suggested order: 5, 4, 1, 2, 3).

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
temporary files in build/tmp; never run the KiCad AppImage with --version (use tools/p2k/bin/kipy
and tools/p2k/bin/kicad-cli). At the end: STATUS.md updated (results, last check output, findings,
p2k candidates, decisions), README.md status line, next_prompt.md replaced with the transcription
prompt, commit and push (git push origin main). If something needs a user decision, stop, record
it in STATUS.md, commit and push, and report it.
```
