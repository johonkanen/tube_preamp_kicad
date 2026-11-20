# tools/generate - frozen history, do not run

**Generation stopped 2026-11-20 (user decision, STATUS.md "Generation stopped 2026-11-20").**
Since then the committed KiCad files of rev A (`kicad/`, `lib/`) are the source and are edited in
KiCad. These scripts generated them from the Proteus data during the conversion (Phases 1-5, the
design fixes and the shared-tool migration). They are kept as the record of how every file was
made, not as tools: running one would overwrite the hand edits with the Proteus state.

| Script | Wrote |
|---|---|
| `make_part_map.py` | `lib/part_map.csv` |
| `gen_symbols.py` | `lib/tube_preamp.kicad_sym` |
| `sheets/sheet01-05.py` (+ `_common.py`) | `kicad/*.kicad_sch` (`p2k sheets` looked in `tools/sheets/`, which is gone) |
| `gen_footprints.py` | `lib/footprint_map.csv`, `lib/tube_preamp.pretty/`, `kicad/fp-lib-table` |
| `make_pcb.sh` | `kicad/tube_preamp.kicad_pcb` (`p2k make_pcb`); refuses to run without `--force-regenerate` |

At the stop commit every script reproduced the committed files byte for byte (`--check`).

Still used: `gen_footprints.py` is **imported** (never run) by `p2k check_pin_order` for its
`RULES` / `PROJECT` specs (`p2k_config.py` `FOOTPRINT_SCRIPT`). Keep it importable.

The checks in `tools/check_all.sh` compare the committed files against the Proteus truth (IPC
netlist, gerbers, drills) and KiCad's rules. An intended difference from Proteus is recorded as a
deviation (config key with a reason, STATUS.md), never hidden.
