# Next prompt

The Proteus -> KiCad 10 conversion of the preamp is **complete** (Phases 0-5) and the **design fixes of
2026-11-20** are done (STATUS.md "Design fixes 2026-11-20": G5V-2 symbol with Omron's terminal names,
the 9 Proteus track pieces of findings 16 / 20 removed with `REMOVED_TRACKS`, component values
unchanged by user decision, finding 4 unchanged). `tools/check_all.sh`: ALL CHECKS PASSED (STATUS.md
"Last check output").

What remains, in this order:

1. **Shared-tool migration** (in progress 2026-11-20: step 1 bump done; STATUS.md "Shared-tool migration
   2026-11-20"; the remaining steps are in `tools/p2k/docs/CANDIDATES.md` section 7.2) (driven by the coordinating session / the agent consolidating the shared
   proteus2kicad tools): bump the `tools/p2k` pin to the consolidated version, replace board-local
   copies that the shared tools then cover (candidates in STATUS.md "p2k candidates", e.g. 9
   `compare.py`, 13 `check_pin_order.py`, 25 `bottom` THT footprints, 26 `check_drill_smaller.py`,
   27 joined N/C pins, 28-30 from the design fixes: Omron names, `check_removed_tracks.py`,
   `make_pcb.sh` step failures), regenerate everything and require `tools/check_all.sh` to print the
   same results (differences explained in STATUS.md). Not before the coordinating session says the
   shared tools are ready.
2. **Then stop generating the board**: remove the `make_pcb.sh --check` step from `tools/check_all.sh`
   and say so in STATUS.md; from then on `kicad/tube_preamp.kicad_pcb` is edited in KiCad. check_board,
   assign_nets, DRC, ipc356_diff, the round trip, check_drill_smaller and check_removed_tracks keep
   working on the edited board; record intended differences as deviations.
3. Adding this repo as a submodule of the amplifier master repo is done from the master repo.

Rules if anything is changed here before item 2 (PLAN.md section 5): don't change tools/p2k or its pin
except in item 1; generate, don't hand-edit; temporary files in build/tmp; never run the KiCad
AppImage with --version (use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli); run tools/check_all.sh
at the start and end; commit and push (git push origin main).
