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
python3 -I rev_b/tools/make_footprints.py  # project footprints, lib/footprint_map.csv (from make_bom.py), fp-lib-table
python3 rev_b/tools/sheets/draw_all.py   # draws all five sheets (overwrites them); Footprint fields from the map
python3 -I rev_b/tools/make_footprints.py --check   # every part has a footprint, symbol pins = pads
tools/p2k/bin/kipy rev_b/tools/make_pcb.py   # NEW board from the netlist (refuses once it has tracks)
```

`make_pcb.py` is for the start only: once placement begins, the board is edited in KiCad and
schematic changes go in with Update PCB from Schematic (the footprints carry the schematic links).

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
  in (limit 8 V); a pad on the crunch's input network is the next fix. The footprint is in: R119
  (0805) between C108 and the crunch gain pot's top, fitted as a 0R link until the voicing sim
  sets the value (2026-11-22).
- B+ decoupling resistors (3.3k / 6.8k / 10k / 10k) are provisional until the stage currents are
  summed; the simulations used 300 V at the plates' supply. All four are 2512 (2026-11-22), so a
  later value change doesn't touch the layout.
- HV resistors split for 200 V 2512 parts (2026-11-21): the B+ bleed is R508 + R518 (2 x 220k, 165 V
  each) and the VB90 divider top R513 + R519 (2 x 330k, 115 V each; 660k with R514 270k gives
  VB90 = 0.29 x BP4, about +2 % on the old 680k). The regulator's foldback resistor is R507 + R520 +
  R521 (3 x 270k = 810k, was one 820k 1206): it sees the whole 430 V raw rail at start-up or into a
  short, 145 V per part. The reference filter Rf is R502 + R525 + R526 (3 x 330k = 990k, was one
  1M 1206; 2026-11-22, found by the PI + FX session): the 390 V zener reference sits across it while
  C501 charges, 130 V per part. Checked the rest of the board from the netlist: no other resistor
  sees more than 200 V in normal operation. The 10M cap bleeds (relay networks) see under 100 V at
  start-up and short recovery, and only a ~300 V pulse (22-220 ms) if B+ is hard-shorted; kept as 1206 (main session
  2026-11-22: the 200 V rule covers normal operation and start-up, a decaying fault pulse within the
  part's short-time overload rating is acceptable).
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
- Drain resistor R522 + R523 + R524 (3 x 1.5k 2512 = 4.5k, raw rail to Q502's drain, placed off
  Q502's pour), user 2026-11-22 with the 70 C design temperature under the plate: it takes about
  68 V of the drop, so Q502 dissipates 0.5 W instead of 1.5 W and Q503 stays near 87-91 C at 70 C
  ambient (limit about 22 mA, 19 mA at 420 V raw; start-up works). Without it the regulator lost
  start-up above 60 C ambient. Short unchanged. See tube_amplifier_kicad docs/preamp_regulator.md
  and sim/preamp_supply/results/thermal_foldback.md.
- Footprints (2026-11-22): every part has one, chosen on its line in `tools/make_bom.py` (the BOM
  and the footprints come from the same list; [bom/](bom/README.md), JLC search and stock check from
  the jlc-tools submodule rev_b/tools/jlc). KiCad stock footprints except three Faston tab
  footprints and the rev A noval socket (rev_b/lib/tube_preamp_revb.pretty). The generic transistor
  symbols got package pin numbers (make_lib.py: Q501 / Q502 1 G, 2 D, 3 S; Q503 1 B, 2 E, 3 C).
  Values set at the same time: R327 300k (for the PI + FX's 1 MΩ input), C105 / C108 / C111
  marked 630 V.
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
  ≤ 50 pF. The 1 MΩ load costs about 1.1 dB: the attenuator's 330k is now 300k (R327, 2026-11-22). Fallback if the cable can't be short: the divider moves to the receiver, which needs
  a re-run of sim/preamp_voicing/switching_real.py (mute depth). The connector pinouts are the
  interfaces.md contract: propose changes through the main-branch session.

## Layout (decisions 2026-11-22, user: "make decisions that allow completing the layout")

`kicad/tube_preamp_revb.kicad_pcb` is started (`tools/make_pcb.py`): outline, holes, sockets, the
interface connectors placed, net classes and clearance rules set, every other part parked below
the board by sheet. DRC with schematic parity: only the unrouted connections. Choices made so the
layout can be finished; to check against the other boards when they are laid out.

- **Frame:** the `etunen` outline (382.79 x 71.91 mm) in rev A's coordinates: chassis x = board
  x + 198.73, chassis y = board y + 42.35. The top edge (y -26.175) is the front, the left end is
  the input end. KiCad's front (F) side is the component side, facing down.
- **Board:** 2 layers, 1.6 mm, 2 oz copper (the regulator's 40 K/W pour estimate assumed 2 oz; set it in
  Board Setup > Physical Stackup before the fab outputs, the generated board has the default 1 oz).
  Min track / space 0.2 mm.
- **Sockets:** V1-V3 on the solder side (B), at rev A's U1-U3 positions and orientation (pads
  checked: 0.00 mm). The rev A footprint got a round courtyard and silk outline (the rectangle
  clipped the standoff holes H103-H105).
- **Mounting holes:** H101-H113 at the rev A positions, 3.2 mm, not plated, with an 8 mm copper
  keep-out. The chassis bond is J102 only (grounding.md §5a), so no hole is plated.
- **Pot ribbons:** J504 (clean) and J505 (crunch) between V1 and V2, J506 (lead) between V2 and
  V3, long axis along the front edge, body front edge 20 mm behind the board edge, odd (GND) pins
  on the rear row. Centres at board x -112 / -62 / 25 = **chassis x 86.7 / 136.7 / 223.7**, body
  front edge at chassis y 36.2. Three 41 mm headers don't fit in one gap between sockets; the
  lead's gain-pot lines then run about 120 mm to V1, inside the ground pour. Each channel's
  Baxandall and post-gain JFET go next to its header.
- **Other connectors:** J101 input and J102 chassis tab at the left end (chassis x about 9);
  J401 at the right end, clear of H102 (chassis x 375-385, y 27-54, about 60 mm from the control
  board's connector); J501 B+ raw tabs at the rear right (chassis x 357 / 372); J502 heater tabs
  (chassis x 290 / 303) and the J503 heater-reference jumper at the rear, next to the right
  socket; J507 output at the rear, chassis x 328-333 (toward the PI + FX board).
- **Faston tabs:** footprints per interfaces.md 4.1 (2 legs on 5.00 mm, 1.4 mm drill): J501 two
  4.8 mm tabs 15 mm apart (HV, insulated receptacles), J502 two 6.3 mm tabs 12.7 mm apart, J102 one
  6.3 mm tab.
- **Zones** (drawn on User.Comments): the 15 mm front strip (≤ 5 mm parts) along the whole front
  edge; the regulator at the right end (x 120-172, behind the control block); the control logic
  (U401-U405, the DGND island) next to J401, joined to AGND only by R426 / C407 there.
- **Regulator copper:** Q502's tab (drain, BP_DRN) on a pour of at least 6 cm² per side, F and B,
  stitched with vias. Q503 sits on F in a cut-out of that pour, over the B-side drain copper (1.6 mm
  FR-4 between: thermal coupling without an electrical connection). R522-R524 off the pour.
- **Clearance** (`kicad/tube_preamp_revb.kicad_dru`, IPC-2221B B2 uncoated, review N57): net
  classes HV (300-430 V: raw rail, regulator, B+, BP1-BP4, the treble-bleed nodes), MV (100-300 V:
  plates, zener string, dividers), V90 (about 90 V: CF cathode and grid, VB90; 0.6 mm), HEATER
  (1.2 mm track, 0.6 mm clearance). HV to low voltage 2.5 mm, HV to MV / V90 1.25 mm, MV to low
  voltage 1.25 mm. Two accepted exceptions inside a part: K201 / K204 coil pad 1 to contact pad 2
  is 2.4 mm (the relay's own coil-contact insulation), and C501's pads are 1.9 mm apart (its 3.5 mm
  lead pitch).

Next: place the parked parts by stage around their sockets, the pours, then route (the
`kicad-agentic-routing` skill or by hand).
