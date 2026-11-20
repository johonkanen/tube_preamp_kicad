# Next prompt

The Proteus -> KiCad 10 conversion of the preamp is **complete** (Phases 0-5 done, STATUS.md;
`tools/check_all.sh`: ALL CHECKS PASSED, STATUS.md "Last check output"). There is no further
conversion phase to run.

What remains open (user's call, not an agent task until the user answers):

1. **Component values** of R13, R22, R27, R30, R34, R51 and Q4 (`NADA`), including the R34 / R51
   swap between schematic and layout (STATUS.md findings 1, 7, 11, 21). The schematic values are used
   until the user checks the built board. When answered: change the values in the sheet scripts
   (`tools/sheets/`), re-run them and `tools/check_all.sh`, record the decision in STATUS.md.
2. **When the board stops being generated**: at the first manual layout change in KiCad (the user's
   call). Then remove the `make_pcb.sh --check` step from `tools/check_all.sh`, say so in STATUS.md,
   and record intended differences as deviations (check_board, assign_nets, DRC, ipc356_diff,
   gerber_roundtrip and check_drill_smaller keep working on the edited board).
3. p2k candidates (STATUS.md "p2k candidates", e.g. 25-27: `bottom` THT footprints, per-refdes
   `DRILL_SMALLER`, joined no-connect pins) are for the shared proteus2kicad repo, not this one.
4. Adding this repo as a submodule of the amplifier master repo is done from the master repo.

Rules if anything is changed here later (PLAN.md section 5): don't change tools/p2k or its pin;
generate, don't hand-edit (until item 2); temporary files in build/tmp; never run the KiCad AppImage
with --version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli); run tools/check_all.sh at the
start and end; commit and push (git push origin main).
