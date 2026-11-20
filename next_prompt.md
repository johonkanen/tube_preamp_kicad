# Next prompt

Rev A (the converted Proteus board at the repo root) is **complete and no longer generated**:
user decision 2026-11-20, STATUS.md "Generation stopped 2026-11-20". The committed KiCad files
(`kicad/`, `lib/`) are the source and are edited in KiCad. The generators are frozen in
`tools/generate/` (history; never run them, `make_pcb.sh` refuses without `--force-regenerate`).
`tools/check_all.sh`: ALL CHECKS PASSED (STATUS.md "Last check output"), 14 steps that check the
committed files against the Proteus truth and KiCad's rules; nothing is regenerated.

Rev B (the redesign) lives in `rev_b/` and belongs to its own sessions: don't touch it from a rev A
session, and `git pull --rebase` before pushing (those sessions push to main too).

What remains for rev A:

1. Nothing planned. Any hand edit in KiCad: run `tools/check_all.sh`; an intended difference from
   Proteus fails a check and is recorded as a deviation (config key with a reason + STATUS.md),
   never hidden by loosening a check.
2. The amplifier master repo bumps its submodule (the coordinating session).

Optional: regenerate the pin-order renders (`tools/p2k/bin/p2k check_pin_order --render`, needs
matplotlib); `reports/pin_order/RLY*.png` still show the former `_ProteusPins` footprint.
Note for proteus2kicad: `tools/regress.sh` regenerates every file with the board's own scripts
(`tools/gen_*.py`, `tools/sheets/`, `tools/make_pcb.sh`); those are gone from these paths, so this
board can no longer be a regress.sh target past the stop commit (use an older commit as BOARD@REV).

Rules (PLAN.md section 5): don't change tools/p2k (rev_b/ imports it at that path and pin); report
p2k problems instead. Temporary files in build/tmp; never run the KiCad AppImage with --version
(use tools/p2k/bin/kipy and tools/p2k/bin/kicad-cli); run tools/check_all.sh at the start and end;
commit and push (git pull --rebase; git push origin main).
