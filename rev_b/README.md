# Preamp rev B (design D): first-draft schematic

The next preamp board, from the simulations in
[tube_amplifier_kicad](https://github.com/johonkanen/tube_amplifier_kicad) (branch `tube_preamps`):
`sim/preamp_voicing` (design D, `ours/chain_d.py` + `ours/fit_design_D.json`) and
`docs/preamp_board_plan.md`. Rev A (the as-built `etunen` conversion) at the repo root is not
touched; `rev_b/` is its own p2k board root (`p2k_config.py`, PROJECT `tube_preamp_revb`).

Three channels (clean / crunch / lead) on one shared 3x12AX7 cascade: S1, S2, (S5), S3, a
self-biased CF, three Baxandalls, S4 recovery, attenuator, output mute. Switching follows CH-5
(DC-neutral): 7 MMBFJ113 shunts (6 pot-set selections + output mute), 5 2N7002 low-side AC
cathode networks, 4 G6K-2 relays (S2 treble bleed, S5 routing, c2, S3 treble bleed), 16 control
lines from an MCP23S17.

## Build

```
python3 rev_b/tools/make_lib.py          # lib/tube_preamp_revb.kicad_sym from KiCad's stock libraries (flattened)
python3 rev_b/tools/make_project.py      # project, root sheet, empty sub-sheets
python3 rev_b/tools/sheets/draw_all.py   # draws all five sheets (overwrites them)
```

The sheets are generated: edit `tools/sheets/draw_all.py`, not the `.kicad_sch` files, until the
draft is frozen. Drawing style is netlist-first (parts on a grid, a wire stub and a label on every
pin), exact for ERC and the netlist; a tidy layout pass comes later. ERC: 0 errors, 0 warnings
(KiCad 10, `kicad-cli sch erc`).

| Sheet | Contents |
|---|---|
| 01 | Input jack, 68k, S1 (V1 pins 1-3) with its DC 2.7k and two MOSFET AC networks; per-channel coupling cap, gain pot (ribbon), bright cap, JFET T-selection into S2 |
| 02 | S2 (V1 6-8), S5 (V2 1-3), S3 (V2 6-8); relays K201-K204; the AC networks |
| 03 | CF (V3 1-3, grid at 90 V), three Baxandalls (pots on the ribbons), JFET-selected post-gain into S4 (V3 6-8), 330k / 220k attenuator, output mute JFET |
| 04 | Control ribbon, MCP23S17, 2x DG412 (JFET gates 0 / -15 V), 74LVC1G08 (unmute = GPA6 AND MUTE_ALL_N), ULN2003 (relay coils) |
| 05 | B+ regulator (as `sim/preamp_supply/reg.py`), RC decoupling per stage, 90 V CF bias, heaters + reference jumper, three 26-pin pot ribbons, output |

## Draft decisions and open items

- Values follow the 2026-11-20 refit of design D (gain-knob penalty): the lead's 470k pad and 1 nF
  bright cap are gone. The refit also gave S2 a lead-only 4.7k + 22 µF network; it is drawn
  **permanent** (no switch), in parallel with the clean / crunch switched 22 µF, which keeps the
  control lines at 16. Simulated: identical fit (crunch cost 10.03 → 10.04, others unchanged).
- Fail-safe muting: DG412 is normally open, so with no logic supply, reset, or no -15 V every JFET
  gate sits at 0 V (JFET on) and the output is muted; a missing control ribbon pulls MUTE_ALL_N low.
- 2N7002 gates run from the expander's 5 V (the plan said 10 V); Rds(on) at 5 V is a few ohms
  against 1.5k-10k cathode resistors. Check the 22 µF / 1M bleed timing with the real Vgs(th).
- G6K-2 NC / NO contact pins, and the coil (5 V, about 30 mA each, 4 coils) to check against the
  Omron datasheet; the relay part number is still open.
- Open from the fit: the crunch's gain knob stays at 0.9 and its JFET node at 9.3 V peak with 1 V
  in (limit 8 V); a pad on the crunch's input network is the next fix.
- B+ decoupling resistors (3.3k / 6.8k / 10k / 10k) are provisional until the stage currents are
  summed; the simulations used 300 V at the plates' supply.
- Footprints are not assigned yet.
