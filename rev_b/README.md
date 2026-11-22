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
- Relays: Omron G6K-2F-Y 5 VDC, decided 2026-11-22 (main session; same part on the PI + FX board).
  Checked against the Omron G6K datasheet (top view): coil + pin 1, - pin 8; pole 1 COM 3, NC 4,
  NO 2; pole 2 COM 6, NC 5, NO 7. Every switched function is on the NO contacts, so energized =
  the lead / crunch setting and an unpowered board sits in the clean wiring (the first draft had
  2 / 4 and 5 / 7 the other way round; fixed 2026-11-22). Coil 21.1 mA at 5 V (237 Ω), 4 coils.
  Contacts carry no DC (10M bleeds, CH-5 rule 3); K201 / K204 sit at the B+ DC level, within the
  coil-to-contact insulation of the -Y (3.2 mm) version.
- Open from the fit: the crunch's gain knob stays at 0.9 and its JFET node at 9.3 V peak with 1 V
  in (limit 8 V); a pad on the crunch's input network is the next fix.
- B+ decoupling resistors (3.3k / 6.8k / 10k / 10k) are provisional until the stage currents are
  summed; the simulations used 300 V at the plates' supply.
- HV resistors split for 200 V 2512 parts (2026-11-21): the B+ bleed is R508 + R518 (2 x 220k, 165 V
  each) and the VB90 divider top R513 + R519 (2 x 330k, 115 V each; 660k with R514 270k gives
  VB90 = 0.29 x BP4, about +2 % on the old 680k). The regulator's foldback resistor is R507 + R520 +
  R521 (3 x 270k = 810k, was one 820k 1206): it sees the whole 430 V raw rail at start-up or into a
  short, 145 V per part.
- Regulator short-circuit protection by thermal foldback (user 2026-11-21): Q502 is an STD4N80K5 DPAK
  on a copper pour, and Q503 (the current-limit NPN) sits on the same pour, thermally coupled but
  not electrically connected. Q503's Vbe falls about 2 mV/K, so a short heats the pour and folds the
  current back further; R507 stays about 820k (now 3 x 270k), R504 goes 20R -> 13R to keep the normal limit above the
  10-15 mA load when Q503 is warm. Simulated (sim/preamp_supply model, whole circuit at one
  temperature, 330 V output):

  | Q503 temperature | 0 C | 27 C | 50 C | 70 C | 85 C | 100 C |
  |---|---|---|---|---|---|---|
  | Normal limit (mA) | 38 | 33 | 28.5 | 25 | 22 | 19 |
  | Into a short (mA / W in Q502) | 16.5 / 7.1 | 12.3 / 5.3 | 8.6 / 3.7 | 5.4 / 2.3 | 3.0 / 1.3 | 0.5 / 0.2 |

  Start-up and recovery after a short work at every temperature. With about 30 K/W from the pour
  to Q503 the short settles near 80 C and 2 W. Lowering R507 instead was rejected: 700k gives 4 mA
  at 27 C but no start-up above about 70 C. Bench check: short B+ and watch the current settle.
- Footprints are not assigned yet. An initial JLCPCB BOM with proposed packages is in [bom/](bom/README.md)
  (`python3 -I rev_b/tools/make_bom.py`; JLC search and stock check from the jlc-tools submodule
  rev_b/tools/jlc, pinned like efinix_soc_board's).
- Grounding (tube_amplifier_kicad docs/grounding.md §5a, confirmed by the user 2026-11-21): AGND
  (GNDA) is the signal and power star, its only entry J501 pin 2; the switch references (JFET and
  MOSFET sources, their gate caps, the JFET-gate pull-downs R419-R425) are AGND. Sheet 04's logic,
  expander pull-downs, ULN2003, relay coils and DG412 GND / rail decoupling are a DGND (GNDD) island
  joined to AGND only by R426 10 Ω ∥ C407 100 nF next to J401. Chassis bond: the CHASSIS pad J102
  next to J101: insulated input jack plus a bolted chassis tag wired to J102 (user, 2026-11-21;
  interfaces.md IF-1). J507 pin 3 is the shield, soft-tied here (R517 10 Ω ∥ C509 100 nF), solid at the
  PI + FX end. Heater reference stays on J503.
- Layout constraint (tube_amplifier_kicad docs/interfaces.md §12.2, components down confirmed by the
  user 2026-11-21; replaces the earlier "headers pass under the front edge" rule): the board hangs
  15 mm below the plate with its components down and the novals on the solder side. Along the front
  edge, at least at the three pot-ribbon positions, keep a strip 15 mm deep where no part is taller
  than 5 mm (SMD passives and SOT-23 only: no film or electrolytic caps, relays or headers). J504-J506
  are vertical shrouded headers on the downward face, set back about 20 mm from the front edge, and
  nothing (mated socket included) protrudes past the edge. Final check: the 3D fit with the front
  panel board once this board is laid out. Standoffs 15 mm; the `etunen` outline stays.
- Pot direction: on every pot ribbon line the CW (clockwise-end) lug takes the TOP net. Bass and
  treble: TOP is the boost end (C1 / C3 from the CF), BOT the cut end (22k to GND), so clockwise =
  more; gain and post: TOP is the signal, the bottom GND (confirmed to the front panel session
  2026-11-21). Pots (front panel board, decided 2026-11-22): Alpha 16 mm PCB pots (RV16AF-41
  class, M7 bushing); gain and post-gain 1M log, treble and bass 1M linear.
- Start-up (2026-11-22): the amp plays before Linux boots; the control board's FPGA brings it up on
  its own, so this board sees RESET_N, the SPI write, then unmute a few seconds after power-on.
- J401 placement: the control board (126 x 92 mm at chassis x 426-552, y 30-122) has its preamp
  ribbon connector on its front edge at about x 438-464, roughly 50-80 mm from J401 at this
  board's right end (main session 2026-11-22).
- Output (J507), agreed in tube_amplifier_kicad docs/interfaces.md §10 (2026-11-20): Zout about
  140k; the PI + FX input is ≥ 1 MΩ with a buffer at its connector, total capacitance on OUT
  ≤ 50 pF. The 1 MΩ load costs about 1.1 dB: change the attenuator's 330k to about 300k at the next
  value pass. Fallback if the cable can't be short: the divider moves to the receiver, which needs
  a re-run of sim/preamp_voicing/switching_real.py (mute depth). The connector pinouts are the
  interfaces.md contract: propose changes through the main-branch session.
