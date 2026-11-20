# Next prompt

The Proteus -> KiCad 10 conversion of the preamp is **complete** (Phases 0-5) and the **design fixes of
2026-11-20** are done (STATUS.md "Design fixes 2026-11-20"). The **shared-tool migration** (STATUS.md
"Shared-tool migration 2026-11-20", prompt in `tools/p2k/docs/CANDIDATES.md` section 7.2) is in
progress: step 1 (bump to p2k a9a286c, D-R re-baseline) and step 2 (board-local tools replaced by the
shared tools and `p2k_config.py` keys, no strict opt-outs) are done. `tools/check_all.sh`: ALL CHECKS
PASSED (STATUS.md "Last check output").

What remains, in this order:

1. **Relay design change** (step 3 of CANDIDATES.md section 7.2, coordinating-session decision "PR
   relays"): RLY1-RLY5 on `IPC_PIN_IDS` (Proteus G5V-2(HI) pins -> Omron pin numbers, PF's map), KiCad's
   stock `Relay:G5V-2` symbol and `Relay_THT:Relay_DPDT_Omron_G5V-2` footprint, the relays redrawn on
   sheets 1-3; electrically identical. Prove each commit with `~/dev/proteus2kicad/tools/regress.sh
   a9a286c tube_preamp_kicad`.
2. **Then stop generating the board** (the user's call): remove the `make_pcb.sh --check` step from
   `tools/check_all.sh` and say so in STATUS.md; from then on `kicad/tube_preamp.kicad_pcb` is edited
   in KiCad. check_board, assign_nets, DRC, ipc356_diff, the round trip and check_removed_tracks keep
   working on the edited board; record intended differences as deviations.
3. The amplifier master repo bumps its submodule (done from the master repo).

Rules (PLAN.md section 5): don't change tools/p2k; report p2k problems instead. Generate, don't
hand-edit; temporary files in build/tmp; never run the KiCad AppImage with --version (use
tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli); run tools/check_all.sh at the start and end; commit
and push (git push origin main).
