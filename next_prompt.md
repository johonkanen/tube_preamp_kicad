# Next prompt

The Proteus -> KiCad 10 conversion of the preamp is **complete** (Phases 0-5), the **design fixes of
2026-11-20** are done (STATUS.md "Design fixes 2026-11-20") and the **shared-tool migration** is done
(STATUS.md "Shared-tool migration 2026-11-20"): p2k a9a286c, the board-local tools replaced by the shared
tools and `p2k_config.py` keys, no strict-check opt-outs, and the relay design change (RLY1-RLY5 on the
Omron pin numbers with KiCad's stock G5V-2 symbol / footprint; electrically identical, same copper).
`tools/check_all.sh`: ALL CHECKS PASSED (STATUS.md "Last check output"); every commit proven with
`~/dev/proteus2kicad/tools/regress.sh a9a286c tube_preamp_kicad`.

What remains:

1. **Stop generating the board** (the user's call, not before they say so): remove the `make_pcb.sh
   --check` step from `tools/check_all.sh` and say so in STATUS.md; from then on
   `kicad/tube_preamp.kicad_pcb` is edited in KiCad. check_board, assign_nets, DRC, ipc356_diff, the
   round trip and check_removed_tracks keep working on the edited board; record intended differences as
   deviations.
2. The amplifier master repo bumps its submodule (done from the master repo, by the coordinating
   session).

Optional: regenerate the pin-order renders (`tools/p2k/bin/p2k check_pin_order --render`, needs
matplotlib); `reports/pin_order/RLY*.png` still show the former `_ProteusPins` footprint.

Rules (PLAN.md section 5): don't change tools/p2k; report p2k problems instead. Generate, don't
hand-edit; temporary files in build/tmp; never run the KiCad AppImage with --version (use
tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli); run tools/check_all.sh at the start and end; commit
and push (git push origin main).
