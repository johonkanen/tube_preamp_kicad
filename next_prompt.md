# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

Phase 3 stopped for a user decision (the TO-92 pad 1 of Q1-Q9, STATUS.md "Phase 3"). Paste the
block below **after** the user has answered and written the answer into it (replace `<ANSWER>`).
Phase 4 notes for the session after that are below the block.

```
Finish Phase 3 (PCB) of the Proteus -> KiCad 10 conversion in /home/jari/dev/tube_preamp_kicad
(model: Opus per playbook section 6), then write the Phase 4 prompt.

State: Phases 0-2 done. Phase 3 stopped at the DRC (STATUS.md "Phase 3"): tools/make_pcb.sh builds
kicad/tube_preamp.kicad_pcb reproducibly (build_pcb, tools/rename_holes.py = holes H101-H113 because
the terminals H4 / H5 exist, gerber_to_tracks with the 14 vias, assign_nets, place_refdes), copper
114 groups / 0 shorts / 0 orphans / 0 opens, check_board OK, DRC 0 shorts / 0 unconnected / 0 parity,
DRC_ACCEPTED = courtyards_overlap + pth_inside_courtyard, but 2 clearance errors: the KiCad TO-92
footprint (TO-92_Inline_P2.03mm) has a square 1.5 mm pad 1, and on Q4 and Q6 a 45-degree track from
pad 2 passes its corner at 0.122 mm (Proteus round 1.524 pad: 0.421; round 1.5 pad: 0.433).

User decision on the TO-92 pad 1: <ANSWER: (a) round 1.5 mm pad 1 on Q1-Q9 / (b) Proteus pads
round 1.524 / 0.762 on Q1-Q9 / (c) keep square, accept the 2 errors>.

Read first: PLAN.md, STATUS.md ("Phase 2" footprint table and pin-order table, "Phase 3", "Findings"
13-18, "p2k candidates" 14 and 18-21, "Decisions"), tools/p2k/CONVERSION_PLAYBOOK.md (sections 3
"Phase 3"/"Phase 4", 5), tools/p2k/README.md (footprints spec keys incl. ipc_sizes, drc,
DRC_ACCEPTED). Run tools/check_all.sh first and compare with STATUS.md "Last check output" (ALL
CHECKS PASSED, without a DRC step). Example (read only): ~/dev/tube_power_amp_kicad (Phase 3/4 done).

Do:
1. Apply the decision in tools/gen_footprints.py (the TO-92 rule/spec; for (c) instead record it,
   noting p2k candidate 20: DRC_ACCEPTED is per type), regenerate the library (gen_footprints.py),
   re-run the sheet scripts only if a footprint name changes, then check_footprints and
   tools/check_pin_order.py (the TO-92 polarity / pin-1 marking must stay right; update its
   expectations and STATUS.md if the marked pad changes), then tools/make_pcb.sh.
2. p2k drc: 0 shorts, 0 unconnected, 0 parity, no unaccepted errors; check that the gaps of Q4 / Q6
   match the table in STATUS.md "Phase 3".
3. Add "DRC with schematic parity" (tools/p2k/bin/p2k drc) to tools/check_all.sh (replace the
   comment there) and finish the negative tests: move a track (expect make_pcb --check, assign_nets
   --check open, drc unconnected), change a segment's net in the file (only the byte compare catches
   it - the pilot's pitfall), change a pad net, move a footprint; one via removal is already done.
   Restore; the board must be byte-identical afterwards.
4. STATUS.md (phase table, Phase 3 section -> done, last check output, decisions), README.md status
   line; replace next_prompt.md with the Phase 4 prompt (notes below in the current next_prompt.md);
   commit and push (git push origin main).

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them; keep
the no-connect rule (U1-U3 pin 9: passive pin + no-connect flag); temporary files in build/tmp;
never run the KiCad AppImage with --version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli);
the noval sockets stay on the top side with the Proteus ids until Phase 5 (user: they are on the
solder side; Phase 5 moves the footprint to B with standard numbering). Still open for the user (do
not decide): the values of R13, R22, R27, R30, R34, R51 and Q4. If something else needs a user
decision, stop, record it in STATUS.md, commit and push, and report it.
```

## Notes for the Phase 4 prompt (verification; Fable, fresh session)

Put these into the Phase 4 prompt when Phase 3 is done:

- **Drills are decided** (user, 2026-11-20): the KiCad drills are kept everywhere; `p2k_config.py`
  `DRILL_SMALLER` has `(1.143, 0.7)` RLY1-RLY5, `(1.143, 1.0)` C1/C5/C7/C10, `(1.143, 1.1)` the 14
  Orange Drops, `(0.762, 0.75)` C4/C14, so `ipc356_diff` and `gerber_roundtrip` report but accept them.
  (If the TO-92 decision was (b), Q1-Q9 then have Proteus drills.)
- **The 2010 Excellon is inch** (`source/fab_2010/etunen - CADCAM Drill.TXT`: M48 / INCH, 7 tools,
  364 hits); `p2k.gerber_roundtrip` reads metric 4.3 only, so convert it board-locally as the pilot
  does (`~/dev/tube_power_amp_kicad/tools/excellon_metric.py` -> `reference/fab_2010_drill_metric.drl`,
  `--check` in check_all.sh; change the source file name) and set `DRILL_EXCELLON`.
- **The June-2010 fab drill file lacks the 2 October vias** (364 vs 366 holes; p2k candidate 3): the
  Excellon cross-check must expect exactly those 2 missing holes (record them by position in
  STATUS.md; a board-local wrapper or the pilot's `phase4_checks.py` pattern if gerber_roundtrip
  requires 1:1).
- Mounting holes are H101-H113 (`ipc356_diff` matches plated holes by `H\d+`, which accepts them).
- Pilot pieces to read (read only): `~/dev/tube_power_amp_kicad` tools/excellon_metric.py,
  tools/phase4_checks.py, p2k_config.py "Phase 4 checks", STATUS.md "Phase 4".
