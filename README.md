# tube_preamp_kicad

KiCad 10 migration of the 3-tube 12AX7 preamp (`etunen`) of the tube amplifier, from Proteus. The schematic is redrawn from
the Proteus PDF and the PCB is rebuilt from the Gerber X2 export, so that every pad, track,
via and pour carries a net from the new schematic. The IPC-D-356A netlist of the CADCAM export
is the reference that every check compares against.

This is **rev A, the as-built baseline**. The redesign (ribbon cables, PCB-mount pots, the new
power section) starts from it. The amplifier project, its specification and the hardware state
are in [tube_amplifier_kicad](https://github.com/johonkanen/tube_amplifier_kicad), which includes
this repo as a submodule once the conversion is verified.

## Method

The shared [proteus2kicad](https://github.com/johonkanen/proteus2kicad) tools, a submodule in
`tools/p2k` (clone with `git clone --recurse-submodules`, or run `git submodule update --init`).
The phases and checks are in `tools/p2k/CONVERSION_PLAYBOOK.md`. Everything specific to this
board is in `p2k_config.py`.

## Status

Conversion plan: [PLAN.md](PLAN.md); progress: [STATUS.md](STATUS.md); prompt for the next agent session: [next_prompt.md](next_prompt.md).

Phase 0 (skeleton and inventory) done 2026-11-20: `p2k_config.py` complete, `reference/`
tables from the IPC netlist. Phase 1 (schematic) done 2026-11-20: `lib/part_map.csv` (163 parts),
`lib/tube_preamp.kicad_sym` (9 symbols, pins = IPC ids), 5 sheets drawn by `tools/sheets/sheet01-05.py`:
163/163 parts, the KiCad netlist equals the Proteus IPC netlist (98 nets, 0 wrong-net pins), ERC
0 errors / 0 warnings. Phase 2 (footprints) done 2026-11-20: `tools/gen_footprints.py` →
`lib/footprint_map.csv` and `lib/tube_preamp.pretty`, all 163 parts fit the IPC pads (worst residual
0.001 mm), pin order checked (`tools/check_pin_order.py`). User decisions 2026-11-20: the noval
sockets are on the solder side (bottom footprint in Phase 5), the KiCad drills are kept (`DRILL_SMALLER`).
Phase 3 (PCB) done 2026-11-20: `tools/make_pcb.sh` builds `kicad/tube_preamp.kicad_pcb`
reproducibly (747 tracks, 14 vias, 13 mounting holes H101-H113), copper 0 shorts / 0 orphans / 0
opens, `check_board` OK, DRC 0 shorts / 0 unconnected / 0 parity / no unaccepted errors (user
decision 2026-11-20: round 1.5 mm TO-92 pad 1 on Q1-Q9). Still open for the user: the values of R13,
R22, R27, R30, R34, R51 and Q4. `tools/check_all.sh` passes (with the DRC step). Next: Phase 4
verification (next_prompt.md).

Built in about 2010 from the June 2010 Gerbers (`source/fab_2010/`). The Proteus layout was edited in October 2010: Q6 pin 3 moves from net J1 to a new net J4 (Q6-3, Q9-3, pad D), plus a ground reroute. The export in `source/cadcam/` is the October version. Holes, outline and tube sockets are identical to the fabricated board. Accepted as the baseline, since the board gets redesigned.

## Source

etunen.DSN/.LYT (Proteus 7, 2010), opened and saved in Proteus 8.12 as `etunen.pdsprj`. Exported 2026-11-19 from Proteus 8.12 SP2: schematic PDF, Gerber X2 CADCAM (metric)
with the IPC-D-356A netlist.

## Mechanical baseline

From the export (the fit reference for the redesign; the KiCad file is
`mechanical/preamp_etunen.kicad_pcb` in tube_amplifier_kicad):

```
outline: 382.79 x 71.91 mm, lower-left corner at (-195.357, -45.730) in the Proteus frame
copper layers: 2; components: 163; mounting holes: 13
mounting holes (relative to the lower-left outline corner, mm; KiCad refdes H101-H113,
mapping in STATUS.md "Phase 3"):
  H1: x   55.992  y   58.550  drill 3.00 plated
  H2: x  163.492  y   61.550  drill 3.00 plated
  H3: x  194.492  y   58.550  drill 3.00 plated
  H4: x  174.492  y   36.050  drill 3.00 plated
  H5: x   34.992  y   36.050  drill 3.00 plated
  H6: x    5.492  y    5.050  drill 3.00 plated
  H7: x    5.492  y   66.050  drill 3.00 plated
  H8: x  247.492  y   61.550  drill 3.00 plated
  H9: x  277.492  y   58.550  drill 3.00 plated
  H10: x  258.492  y   36.050  drill 3.00 plated
  H11: x  378.492  y    5.050  drill 3.00 plated
  H12: x  378.492  y   66.050  drill 3.00 plated
  H13: x   24.492  y   61.550  drill 3.00 plated
```

## Layout

```
source/         Proteus exports (read-only)
  cadcam/         Gerber X2 export with the IPC-D-356A netlist (the reference)
  schematic_pdf/  schematic PDF to redraw from
  *.pdsprj        Proteus project (schematic values, devices, packages, pin names)
  fab_2010/       the RS-274X Gerbers the boards were made from (June 2010)
reference/      tables derived from the IPC netlist (p2k ipc356): pads, pin -> net, pins by net
tools/p2k/       proteus2kicad (submodule)
tools/check_all.sh  every verification step (run at the start and end of a session)
p2k_config.py   board configuration for the tools
```
