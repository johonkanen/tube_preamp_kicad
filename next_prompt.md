# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

Phase 3 is done (STATUS.md "Phase 3"; the TO-92 pad 1 question was answered by the user: option (a),
round 1.5 mm pad 1 on Q1-Q9). Next is Phase 4, verification, in a fresh session (Fable).

```
Do Phase 4 (independent verification) of the Proteus -> KiCad 10 conversion in
/home/jari/dev/tube_preamp_kicad (model: Fable, fresh session, per playbook section 6).

State: Phases 0-3 done (STATUS.md). tools/make_pcb.sh builds kicad/tube_preamp.kicad_pcb reproducibly
from the schematic and the Proteus gerbers (747 tracks, 14 vias, 13 mounting holes H101-H113);
check_board OK; assign_nets 114 groups / 0 shorts / 0 orphans / 0 opens; p2k drc 0 shorts /
0 unconnected / 0 parity / no unaccepted errors (DRC_ACCEPTED = courtyards_overlap +
pth_inside_courtyard: the Proteus placement). tools/check_all.sh passes with the DRC step.

Read first: PLAN.md, STATUS.md (all of "Phase 2" footprint and drill tables, "Phase 3", "Findings",
"p2k candidates" 3, 18, 21, 22, "Decisions"), tools/p2k/CONVERSION_PLAYBOOK.md (section 3
"Phase 4", 5), tools/p2k/README.md (gerber_roundtrip, ipc356_diff, DRILL_SMALLER, DRILL_EXCELLON).
Run tools/check_all.sh first and compare with STATUS.md "Last check output" (ALL CHECKS PASSED).
Example (read only): ~/dev/tube_power_amp_kicad (Phase 4 done): tools/excellon_metric.py,
tools/phase4_checks.py, p2k_config.py "Phase 4 checks", STATUS.md "Phase 4".

Known facts for this board:
- Drills are decided (user, 2026-11-20): the KiCad drills are kept everywhere; p2k_config.py
  DRILL_SMALLER has (1.143, 0.7) RLY1-RLY5, (1.143, 1.0) C1/C5/C7/C10, (1.143, 1.1) the 14 Orange
  Drops, (0.762, 0.75) C4/C14, so ipc356_diff and gerber_roundtrip report but accept them.
- TO-92 Q1-Q9: KiCad pads 1.5 mm round (pad 1 made round by tools/gen_footprints.py `pad_shapes`,
  user decision (a); pin-1 dot on silk / fab, `pin1_dot`) vs Proteus round 1.524; drills 0.8 vs
  0.762 (larger). Other KiCad pads differ in
  size from Proteus (STATUS.md "Phase 2" table: larger on the 2 W resistors and CAP20 discs).
- The 2010 Excellon is inch (source/fab_2010/etunen - CADCAM Drill.TXT: M48 / INCH, 7 tools,
  364 hits); p2k.gerber_roundtrip reads metric 4.3 only, so convert it board-locally as the pilot does
  (copy ~/dev/tube_power_amp_kicad/tools/excellon_metric.py -> reference/fab_2010_drill_metric.drl,
  change the source file name, `--check` step in check_all.sh) and set DRILL_EXCELLON.
- The June-2010 fab drill file lacks exactly the 2 October vias (364 vs 366 holes; p2k candidate 3):
  (33.02, -31.115) and (-29.337, -42.545) (STATUS.md "Phase 0"). The Excellon cross-check must expect
  exactly those 2 missing holes (record them by position in STATUS.md); use a board-local wrapper or
  the pilot's phase4_checks.py pattern if gerber_roundtrip requires 1:1, and fail on anything else.
- Mounting holes are H101-H113 (ipc356_diff matches plated board-only holes by `H\d+`, which accepts
  them; p2k candidate 18).
- No pours on this board; 14 vias 1.27 / 0.508; 3 N/C pads (U1-U3 pin 9).

Do (playbook Phase 4):
1. p2k gerber_roundtrip (KiCad gerbers + drill vs Proteus, XOR per copper layer, coverage both ways,
   drill comparison incl. the Excellon), --check clean apart from the recorded drill decisions and
   the 2 missing October vias; overlay PNGs in reports/ if the pilot commits them.
2. p2k ipc356_diff (kicad-cli ipcd356 vs the Proteus IPC file): every pad / via / hole within
   0.05 mm, same side, THT, nets 1:1, N/C equal.
3. Add both (and the Excellon conversion --check) to tools/check_all.sh.
4. Review: read the generating scripts (tools/*.py, tools/sheets, p2k_config.py), spot-check the
   easy-to-get-wrong places (mounting holes H101-H113 vs the terminals H4 / H5, N/C pin 9, the noval
   pin ids, relay renumbering, electrolytic / diode polarity, TO-92 pin 1 with the round pad, the
   dangling 0.0635 mm track stub of finding 16, single-pin nets), confirm or refute every finding.
5. Negative-test every new check (move a track, change a net, shift a pad 0.1 mm, remove a drill);
   restore, the board and reports must be byte-identical afterwards.
6. STATUS.md (phase table, a "Phase 4" section, last check output, decisions), README.md status;
   replace next_prompt.md with the Phase 5 prompt (Phase 5 = user decisions first: the noval sockets
   U1-U3 to the bottom side with the standard numbering (user decision), silk / refdes clean-up); commit and push (git push origin main).

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them; keep
the no-connect rule (U1-U3 pin 9: passive pin + no-connect flag); generate, don't hand-edit;
temporary files in build/tmp; never run the KiCad AppImage with --version (use tools/p2k/bin/kipy
and tools/p2k/bin/kicad-cli); the noval sockets stay on the top side with the Proteus ids until
Phase 5. Still open for the user (do not decide): the values of R13, R22, R27, R30, R34, R51 and
Q4. If something needs a user decision, stop, record it in STATUS.md, commit and push, and report it.
```
