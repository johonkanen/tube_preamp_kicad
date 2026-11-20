# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/tube_preamp_kicad to KiCad 10: Phase 3 (PCB; model:
Opus per playbook section 6). Phases 0-2 are done: 5 sheets, 163/163 parts, the KiCad netlist
equals the IPC netlist (98 nets, 0 wrong-net pins), ERC 0 / 0; every footprint fits the IPC pads
(worst residual 0.001 mm, reports/footprint_fit.csv = the placement), pin order checked;
tools/check_all.sh passes.

Read, in this order: PLAN.md, STATUS.md (phase table, "Phase 2" incl. the pad size / drill
differences per refdes and the pin-order table, "Findings" 13-15, "p2k candidates",
"Decisions" incl. the open user questions), tools/p2k/CONVERSION_PLAYBOOK.md (sections 1,
3 "Phase 3", 5), tools/p2k/README.md (pcb, build_pcb, gerber_to_tracks, assign_nets,
check_board, drc; config keys PCB_RULES, PCB_THICKNESS, HOLE_FOOTPRINT / HOLE_VALUE, VIA_DRILLS,
DRC_ACCEPTED). Run tools/check_all.sh first and compare with STATUS.md "Last check output"
(ALL CHECKS PASSED). Examples (read only, never change those repos):
~/dev/tube_power_amp_kicad (same 2010 Proteus export, Phase 3 done: tools/make_pcb.sh,
tools/measure_gaps.py, p2k_config.py PCB_RULES / PCB_THICKNESS / DRC_ACCEPTED, STATUS.md
"Phase 3"), ~/dev/tube_psu_kicad (a board with vias: its make_pcb.sh and Phase 3 notes).

Board facts (PLAN.md section 1): 2 copper layers (Top 402 / Bottom 345 conductor draws, widths
0.508 / 1.016 / 1.27 mm), no pours (no G36 / %LPC%), 14 vias (0.508 mm drill, 1.27 mm pad;
VIA_DRILLS set), no free pads, 13 plated 3.0 mm mounting holes with 6.35 mm pads (HOLE_FOOTPRINT
set), outline 382.79 x 71.905 mm, all 163 parts THT on the top side.

Do:
1. Measure the smallest Proteus gaps (track-track, track-pad, pad-pad, to the edge; the pilot's
   tools/measure_gaps.py) and fill PCB_RULES and PCB_THICKNESS in p2k_config.py (1.6 mm, the 2010
   standard, unless the sources say otherwise; via values from the 14 Proteus vias).
2. tools/make_pcb.sh (as the pilot, plus the vias: build_pcb, gerber_to_tracks, assign_nets; no
   pours_to_zones) -> kicad/tube_preamp.kicad_pcb, with --check (rebuild in build/tmp, byte
   compare; two runs identical).
3. assign_nets: 0 shorts / 0 orphans / 0 opens; check_board passes (pads, holes, vias, nets 1:1).
4. DRC with schematic parity (p2k drc): 0 shorts, 0 unconnected, 0 parity. KiCad pads are larger
   than Proteus only on the 2 W resistors R6, R7, R22, R23, R33, R62-R67 (2.4 vs 2.286) and the CAP20
   discs C18, C22, C26 (2.0 vs 1.778); everything else is smaller or equal. List the remaining DRC
   items with reasons (DRC_ACCEPTED: courtyard overlaps of the Proteus placement are expected). If
   DRC forces Proteus pad sizes or drills on some parts, that is a user decision: stop, record the
   per-refdes conflicts in STATUS.md, commit, push and report.
5. Add the steps to tools/check_all.sh (make_pcb.sh --check, check_board, assign_nets --check,
   drc) and negative-test them (move a track, change a net, remove a via).

Open user questions (do not decide them): the noval socket side (STATUS.md finding 13; the
footprint keeps the Proteus ids on the top side); the KiCad drills smaller than Proteus on
RLY1-RLY5 (0.7 vs 1.143), C1/C5/C7/C10 (1.0 vs 1.143), the Orange Drops (1.1 vs 1.143), C4/C14
(0.75 vs 0.762) (Phase 4 DRILL_SMALLER or Proteus drills); the values of R13, R22, R27, R30, R34,
R51 and Q4 (findings 1, 7, 11; schematic values are used).

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
keep the no-connect rule (U1-U3 pin 9: passive pin + no-connect flag); temporary files in
build/tmp; never run the KiCad AppImage with --version (use tools/p2k/bin/kipy and
tools/p2k/bin/kicad-cli). At the end: STATUS.md updated (results, last check output, findings,
p2k candidates, decisions), README.md status line, next_prompt.md replaced with the Phase 4
(verification) prompt, commit and push (git push origin main). If something needs a user
decision, stop, record it in STATUS.md, commit and push, and report it.
```
