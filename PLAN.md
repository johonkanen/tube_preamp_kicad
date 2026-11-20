# Conversion plan: Preamp (`etunen`)

Goal: redraw the Proteus schematic in KiCad 10 and rebuild the PCB from the Proteus Gerber X2
export, so that every pad, track, via and pour carries a net from the new schematic, and **prove
with scripted checks** that the KiCad design is electrically identical to the Proteus one. The
result is **rev A, the as-built baseline** for the redesign (see README.md).

This plan follows the generic playbook **`tools/p2k/CONVERSION_PLAYBOOK.md`** (read it first) and
lists only what is specific to this board. The finished reference is `~/dev/tube_psu_kicad`
(same proteus2kicad version, Phases 0-5 done): look at its `tools/`, `p2k_config.py`, PLAN.md and
STATUS.md for how each step was done.

**Order:** Run after the power amp pilot has finished Phase 1 (or at least Phase 0), and read its STATUS.md findings first: same 2010 / Proteus 7 export, same kinds of fly-lead pads.

## 1. Inventory (measured in Phase 0, 2026-11-20)

| Item | Value |
|---|---|
| Proteus project | `source/etunen.pdsprj` (values, devices, packages, pin names via `p2k.pdsprj`; ROOT.DSN, ROOT.LYT, ROOT.CDB, PROJECT.XML) |
| Schematic PDF | `source/schematic_pdf/etunen.PDF`, 5 pages, **no title blocks** (sheet names chosen from the content, `p2k_config.py` SHEETS): 1 Input stage, 2 Second stage, 3 EQ stage, 4 Tone stacks, 5 Supply filter |
| CADCAM export | `source/cadcam/` (October 2010 layout; Gerber X2, `FSLAX45Y45`, metric, one `SameCoordinates` id, no arcs): Top/Bottom Copper, Top Silk, Top/Bottom Solder Resist (negative), Top Assembly, Mechanical 1 (outline only; its X2 FileFunction says `NonPlated,1,2,NPTH`), Drill TOP-BOT Plated; no NonPlated drill file |
| IPC netlist (the reference) | `source/cadcam/etunen - CADCAM Netlist.IPC`: **98 nets** (not 99; NNAME ids 00001-00114 with gaps), 366 records (all THT `317`): 339 component pads (3 of them N/C: pin 9 of U1-U3) + 14 vias + 13 holes |
| Copper layers | 2 (Top, Bottom); conductor draws: Top 402 (0.508 x305, 1.016 x40, 1.27 x57 mm), Bottom 345 (0.508 x271, 1.016 x47, 1.27 x27 mm) |
| Pours | none (no `G36` regions, no `%LPC%`) |
| Vias / free pads | 14 vias (0.508 mm drill, 1.27 mm pad: nets PRE-GND 2, H4 2, #00073 2, J2 5, EQ 1, J1 1, J4 1); no free pads |
| Outline | 382.79 x 71.905 mm, lower-left (-195.357, -45.730) (Mechanical 1, 4 `Profile` draws) |
| Parts | **163** (164 IPC refdes fields incl. the blank one of vias / holes): U1-U3 (12AX7, noval), Q1-Q9 (J112, TO92), RLY1-RLY5 (G5V-2), R 57, C 35, D 7 (1N4001), and 47 single-pad terminals (Proteus device TERMINAL) |
| Drills | all plated: 0.508 (14 vias), 0.762 (139), 1.016 (36), 1.143 (90), 1.524 (47), 1.727 (27), 3.0 (13 holes) = 366; the 2010 Excellon `source/fab_2010/etunen - CADCAM Drill.TXT` (inch, same frame) has 364 hits: the same except the 2 vias added in October (Phase 4 `DRILL_EXCELLON` cross-check, expect those 2) |
| Technology | through-hole only |
| Mounting holes | 13, 3.0 mm **plated** with a 6.35 mm pad on both layers, in the plated drill file (`OtherDrill`); positions in README.md "Mechanical baseline" (match the IPC) |

## 2. Board-specific notes and expected pitfalls

- Built about 2010 from the June 2010 Gerbers (`source/fab_2010/`). The Proteus layout was edited in October 2010 (Q6 pin 3 from net J1 to a new net J4 with Q9-3 and pad D, plus a ground reroute). **The baseline is the October export in `source/cadcam/`**, accepted by the user; don't "fix" it towards the fab Gerbers.
- 3 noval sockets (U1-U3, 9 pins), 12AX7s.
- 47 single-pad parts are fly-lead pads: the tone-stack and pot connections (`HI1O`/`HI1W`/`HI1X` ... `LO3X`, `POT1-1` ... `POT3-2`, `POT-GND`), master (`MV0`-`MV3`), presence (`PRES`, `PRES1`-`PRES3`), guitar input (`GTR-IN`, `GTR-GND`), `EQOUT`, `PREPOWER`/`PRERETURN` (B+), heaters (`H4`, `H5`), the relay-coil switch pads `SW1`-`SW3` and the JFET-gate control pads `A`, `B`, `C`, `D` (on nets J1-J4). Four names are truncated to 6 characters in the IPC (`GTR-GN`, `POT-GN`, `PREPOW`, `PRERET`); `A`-`D` become `PAD_A`-`PAD_D` (the single letters `C`/`D` would read as capacitor / diode references) and the names with `-` get `_` (`p2k_config.py`, STATUS.md "Phase 0").
- 5 relays (`RLY*`, G5V-2, 8 pads): check their pin ids during the footprint fit. (Phase 0: `SW1`-`SW3` are terminals, not switches.)
- 27 IPC records without refdes: 14 vias and 13 mounting holes.
- Terminal refdes are not net names: pad `A` is on net J1, while net `A` is the first B+ filter node (R6, R62, C28); likewise `B`-`D`. Only `H4`, `H5` and `SW1`-`SW3` share their net's name.

## 3. Phases

As in the playbook, section 3. Board-specific done criteria:

| Phase | Done when |
|---|---|
| 0 Skeleton and inventory | `p2k_config.py` complete (sheet names from the PDF title blocks or, without them, from the content, truncated-refdes table, KiCad refdes map, net aliases, expected IPC counts, layers, drills, outline); `p2k ipc356 --check` and `p2k check_sources` pass; `reference/` cheat sheets written; `tools/check_all.sh` runs; PLAN.md section 1 corrected with the measured inventory |
| 1 Schematic | all 163 parts drawn; `compare_netlists` 0 wrong-net pins, every IPC net complete; ERC 0 errors (warnings explained) |
| 2 Footprints | every part fits the IPC pads within 0.05 mm (`check_footprints`); pin-order oddities reported |
| 3 PCB | copper 0 shorts / 0 orphans / 0 opens after zone fill; DRC 0 shorts, 0 unconnected, 0 parity; remaining DRC items listed and justified; `make_pcb.sh --check` reproducible |
| 4 Verification | `gerber_roundtrip --check` and `ipc356_diff` pass and are in `check_all.sh`; every new check negative-tested; preferably a different session/model |
| 5 Clean-up | only the user's choices (pad sizes, silk, refdes positions) |

When all phases are done: STATUS.md says so, and the amplifier master repo can add this repo as a
submodule (that step is done from the master repo, not here).

## 4. Effort

The playbook's estimates are for a ~270-part, 4-layer, 11-sheet board. This board has
163 parts on 5 sheets and 2 copper layers: scale accordingly.

## 5. Rules for this conversion

Several board conversions run **in parallel**, each in its own repo and session. To keep them
independent:

1. **Don't change the shared tools** in `tools/p2k` (proteus2kicad), and don't move the submodule
   pin (c5682dd). If a tool can't handle something on this board, write a board-local script in
   `tools/` (or a config key the tool already has) and record it in STATUS.md under
   "p2k candidates", with what the shared tool would need. The tool changes are made later, in one
   place, with the ac_psu regression.
2. **Don't touch other repositories.** In particular not `~/dev/tube_amplifier_kicad` (the
   amplifier master repo: it adds this repo as a submodule once the conversion is verified) and not
   `~/dev/ac_psu_kicad` (another session's work in progress). `~/dev/tube_psu_kicad` is the
   finished reference: read it, don't change it.
3. **Reproduce Proteus.** Problems in the original design are reported in STATUS.md
   ("Findings"), not fixed. The redesign happens later, from this baseline.
4. **Generate, don't hand-edit** (playbook section 1): every file in `kicad/`, `lib/` and
   `reference/` is written by a script and is reproducible.
5. **Temporary files in `build/tmp/`** (git-ignored). Never run the KiCad AppImage with
   `--version` (it starts the GUI and hangs); use `tools/p2k/bin/kipy` and `tools/p2k/bin/kicad-cli`.
6. **Commit and push at the end of every phase** (and at the end of a session), with
   STATUS.md and next_prompt.md updated in the same commit.
7. **Ask the user** where the playbook says to (pad sizes when DRC forces them, Phase 5 choices,
   anything that changes the design).

## 6. Session protocol

- Start every session by reading PLAN.md, STATUS.md and `tools/p2k/CONVERSION_PLAYBOOK.md`, then
  run `tools/check_all.sh` (from Phase 0 on) and compare with the last result in STATUS.md.
- One session per phase (Phase 1 transcription may take several, a few sheets each).
- End every session with: `tools/check_all.sh` passing for everything done so far, STATUS.md
  updated (phase state, last check output, findings, p2k candidates, decisions), next_prompt.md
  replaced with the prompt for the next session, commit and push.
