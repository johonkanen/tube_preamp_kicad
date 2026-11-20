# Status: Preamp (`etunen`)

Plan: [PLAN.md](PLAN.md). Playbook: `tools/p2k/CONVERSION_PLAYBOOK.md`.

| Phase | State |
|---|---|
| 0 Skeleton and inventory | **done** 2026-11-20 (Opus 5.5) |
| 1 Schematic | not started; next (next_prompt.md: preparation session) |
| 2 Footprints | not started |
| 3 PCB | not started |
| 4 Verification | not started |
| 5 Clean-up | not started |

## Phase 0 – done (Opus 5.5, 2026-11-20)

- **Inventory measured** (PLAN.md section 1 corrected): **98 nets** (the pre-check said 99; the
  NNAME ids run 00001-00114 with gaps), 366 IPC records, all THT (`317`): 339 component pads (3 N/C:
  pin 9 of U1-U3), **14 vias** (0.508 mm drill, 1.27 mm pad), 13 plated 3.0 mm mounting holes (6.35 mm
  pad on both layers); 0 SMD, 0 free pads; no pours (no `G36` / `%LPC%`), no arcs; 2 copper layers;
  outline 382.79 x 71.905 mm at (-195.357, -45.730). **163 parts** (164 IPC refdes fields incl. the
  blank one): U1-U3 12AX7 (noval), Q1-Q9 J112 (TO92), RLY1-RLY5 G5V-2, R 57, C 35, D1-D5/D8/D9
  1N4001, 47 single-pad terminals.
  Corrections to the pre-check: 98 nets, not 99; the 27 blank-refdes records are 14 vias **and** the
  13 holes (not 27 vias); **`SW1`-`SW3` are terminals** (fly-lead pads on the nets SW1-SW3, the
  relay-coil switch inputs), not switches; `A`-`D` are on the JFET-gate nets J1-J4 (the "relay-control"
  label of the pre-check is loose: the relays are switched through `SW1`-`SW3`).
- **PDF:** 5 pages, rendered with `pdftoppm -r 200 -png source/schematic_pdf/etunen.PDF
  build/tmp/pdf/hi` (`hi-1..5.png`, git-ignored; re-render in later sessions). As on the power amp
  board the 2010 pages have **no title block**, so the SHEETS names describe the content:
  1 **Input stage** (U1, GTR-IN, Q1/Q2, RLY1/RLY2, POTx-y), 2 **Second stage** (U2, RLY3, Q3-Q6),
  3 **EQ stage** (U3, RLY4/RLY5, Q7-Q9, PRES*, MV*, EQOUT), 4 **Tone stacks** (three stacks on
  EQ1-EQ3, HI*/LO* pads), 5 **Supply filter** (R62-R67 / C28, C33-C37 B+ chain on nets A-F,
  PREPOWER/PRERETURN, and the pads A-D, SW1-SW3). Rename in `p2k_config.py` before
  `make_skeleton` if the user prefers other names.
- **`p2k_config.py`** complete for Phase 0: SHEETS, `TRUNCATED_REFDES` (+ `TRUNCATED_NETS`),
  `KICAD_REFDES`, `NET_ALIASES` (empty), blank-refdes drills, `EXPECTED_IPC`, `COPPER`, drills,
  outline. Tables:

  | IPC field | Full Proteus refdes (PDF) | KiCad refdes | Net (check) |
  |---|---|---|---|
  | `GTR-GN` | GTR-GND (sheet 1) | `GTR_GND` | `PRE-GND` |
  | `POT-GN` | POT-GND (sheet 2) | `POT_GND` | `PRE-GND` |
  | `PREPOW` | PREPOWER (sheet 5) | `PREPOWER` | `#00131` (R67-2) |
  | `PRERET` | PRERETURN (sheet 5) | `PRERETURN` | `PRE-GND` |

  `GTR-IN` and `POT1-1` ... `POT3-2` are exactly 6 characters and complete (PDF). Each truncated
  name is unique, so no coordinate keys. `TRUNCATED_NETS` is keyed by the **KiCad** refdes (that is
  how `ipc356` looks it up; negative-tested: a wrong expected net for `GTR_GND` fails).

  | Proteus refdes | KiCad refdes |
  |---|---|
  | `GTR-IN` / `GTR-GND` / `POT-GND` | `GTR_IN` / `GTR_GND` / `POT_GND` |
  | `POT1-1` `POT1-2` `POT2-1` `POT2-2` `POT3-1` `POT3-2` | `POT1_1` `POT1_2` `POT2_1` `POT2_2` `POT3_1` `POT3_2` |
  | `A` / `B` / `C` / `D` | `PAD_A` / `PAD_B` / `PAD_C` / `PAD_D` |

  Same convention as the power amp and tube_psu (`-` as a separator → `_`; there are no sign-led,
  `+`, `'`, `.` or space refdes on this board). Refdes without a trailing number stay (`EQOUT`,
  `PRES`, `PREPOWER`, `PRERETURN`); `H4`, `H5`, `SW1`-`SW3`, `MV0`-`MV3`, `PRES1`-`PRES3` are
  terminals despite their look (`SW*`, `H*` are only names).
  Net names: no `=POWER` nets, `NET_ALIASES` empty. Named nets (IPC spelling): `PRE-GND`, `H4`, `H5`,
  `A`-`F` (B+ filter nodes), `J1`-`J4` (JFET gates), `SW1`-`SW3`, `PRE1`, `PRE2`, `EQ`, `EQ1`-`EQ3`.
  The PDF writes `pre-gnd`, `sw1`-`sw3`, `h4`, `h5`, `j4` in lower case (Proteus ignores case):
  label them in the IPC spelling.
- **`p2k ipc356`** wrote `reference/` (`ipc356_pads.{json,csv}`, `pin_nets_by_component.md`,
  `pins_by_net.md`); `--check` passes. **`p2k check_sources`** passes: 339 ComponentPad + 14 ViaPad +
  13 OtherPad flashes per copper layer and 366 plated drill flashes match the IPC 1:1, one
  SameCoordinates id, outline. Negative tests (temporary config edits, restored): `holes` 12 →
  ipc356 fails; `HOLES_PLATED = False` → both fail; outline height 71.0 → check_sources fails;
  `TRUNCATED_NETS["GTR_GND"]` wrong → ipc356 fails; a `KICAD_REFDES` entry removed → ipc356 fails
  (stale reference). All pass again with the committed config.
- **`tools/check_all.sh`**: KiCad environment, IPC self-check, X2 vs IPC (same as the pilot's Phase 0).
- **October (baseline) vs June 2010 fab Gerbers** (`source/fab_2010/`, RS-274X inch, same frame;
  noted only, the October export stays the baseline): copper and drills compared geometrically
  (0.02 mm tolerance, a throw-away script in build/tmp). Everything is identical except
  1. **Q6-3 J1 → J4**: the June top track Q6-3 (35.69, 3.18) → (34.29, 1.78) → (34.29, -21.59) →
     J1 via (12.70, -24.77) is replaced by a top track Q6-3 → new **via (33.02, -31.115)** and a new
     bottom track (33.02, -31.12) → (44.45, -42.55) → (161.29, -42.55) → (170.69, -40.01) → Q9-3
     (181.48, -29.21);
  2. **ground reroute**: the June bottom 1.27 mm PRE-GND track (-29.34, -42.55) → (5.72, -42.55) →
     C35-1 (7.62, -38.73) is removed; a new **via (-29.337, -42.545)** joins that bottom track end
     to the top PRE-GND track (split there, same geometry).
  So October = June + 2 vias + those tracks; the 2010 Excellon has 364 hits, the October drill 366.
  Holes, pads, outline and all other copper are identical.
- Notes for the later phases:
  - Phase 1: `p2k.pdsprj.dsn_values` **raises** on this board ("parts with several schematic values:
    D"): the single-letter refdes `A`-`D` match strings all over ROOT.DSN (p2k candidate 2). Without
    them it reads 159 values; missing are the `µ` values C4 (`MMK J04 1µ`), C14 (`1µ mmk`), C30
    (`22µ`), C28/C33-C37 (`22µF 450V`) (the pilot's p2k candidate 1). `lyt_parts` (without A-D)
    reads 153 records, missing C28/C33-C37, and C4's layout value is cut to `MMK J04 1`. Take these
    values from the PDF; A-D are `TERMINAL` / package `PIN` like the other 43 terminals.
    Devices: 12AX7 / 9-PIN BELTON NOVAL, J112 / TO92, G5V-2(HI), 1N4001 / DO41, MINRES100K / RES40
    (46), METALFILM1K / 2W METAL FILM RESISTOR (11), ORANGE DROP / XICON / MMK film caps,
    CERAMIC56P / CAP20 (C18, C22, C26), HITEMP10U50V / ELEC-RAD10 (C2), MINELECT10U50V / 22U 100V
    (C30), TERMINAL / PIN (47).
  - Phase 1: 12AX7 is two triodes plus heater in one Proteus symbol (pins 1-9, pin 9 N/C): decide the
    KiCad unit split up front (pilot p2k candidate 8: KiCad `Valve:ECC83` has 3 units with the envelope
    drawn for the heater unit). The heaters go to `H4` / `H5` on every tube sheet; `H4` also feeds
    the relay coils.
  - Phase 1: J112 pin ids: gate always pin 3, but source/drain 1/2 differ per part (Q1: 1 = R3,
    2 = PRE-GND; Q2: 1 = PRE-GND): follow the IPC per refdes.
  - Phase 1: `PRE1`, `PRE2`, `EQ`, `EQ1`-`EQ3`, `J1`-`J4`, `SW1`-`SW3`, `H4`, `H5`, `A`-`F`,
    `PRE-GND` cross sheets (global labels); the terminals `A`-`D` / `SW1`-`SW3` on sheet 5 sit on
    the J/SW nets.
  - Pad / drill families: Q 1.524/0.762, small R/C 1.778/0.762, C2/C30 2.032/0.762, D + 2 W R
    2.286/1.016, RLY + film/electrolytic C 2.54/1.143, terminals 3.048/1.524, noval 4.318/1.727,
    holes 6.35/3.0, vias 1.27/0.508.
  - Phase 4: `DRILL_EXCELLON = "source/fab_2010/etunen - CADCAM Drill.TXT"` lacks exactly the two
    October vias (33.02, -31.115) and (-29.337, -42.545); check how `gerber_roundtrip` reports that
    before adding it (p2k candidate 3).

## Last check output

`tools/check_all.sh` (2026-11-20, end of Phase 0):

```
== KiCad environment
pcbnew 10.0.7
== IPC-D-356A parser self-check
ipc356: nets=98, records=366, refdes_raw=164, tht_records=366, smd_records=0, smd_top=0, smd_bottom=0, nc_pads=3, vias=14, free_pads=0, holes=13, parts=163
ipc356: OK
== Gerber X2 export vs IPC (pads, vias, holes, drills, outline)
  8 gerbers, one SameCoordinates id
  Top Copper: Draw:Conductor 402, Draw:Profile 4, Flash:ComponentPad 339, Flash:OtherPad,Unknown 13, Flash:ViaPad 14
  Bottom Copper: Draw:Conductor 345, Draw:Profile 4, Flash:ComponentPad 339, Flash:OtherPad,Unknown 13, Flash:ViaPad 14
  drills: 366 plated, 0 non-plated
  outline 382.8 x 71.9 mm at (-195.36, -45.73)
check_sources: OK

ALL CHECKS PASSED
```

## Findings about the original design

(Report here; don't fix.)

1. **Q4's schematic value is `NADA`** (sheet 2; ROOT.DSN too), while its layout record is J112 /
   TO92 like Q1-Q9. Presumably a placeholder; the board part is a J112. Phase 1 takes the schematic
   value unless the user decides otherwise.
2. **The schematic matches the October layout**: sheet 2 labels Q6's gate `j4`, sheet 3 Q9's `J4`,
   sheet 5 pad D on `J4`: the October edit was made in the schematic too.
3. **Terminal refdes vs net names**: pads `A`-`D` are on nets J1-J4, while the nets named `A`-`D` are
   the B+ RC filter nodes (R62-R65 / C28, C33-C35) on sheet 5. Not an error (Proteus terminals do not
   join nets by refdes), but easy to confuse; on the board they are separate.
4. **The relay flyback diodes have the anode on `H4`** (D1, D2, D3, D8, D9: A = H4, K = coil / SW
   node) and every coil has one end on `H4`. That is correct only if the switches pull `SW1`-`SW3`
   to a rail **above** `H4` (`H4` is the low heater rail for the coils); worth confirming against
   the built amplifier. D4/D5 OR `SW2`/`SW3` onto RLY4's coil (#00081).
5. **The 250p caps C18/C22/C26 use the Proteus device CERAMIC56P**: device name and value disagree;
   values from the schematic.
6. Export quirks (no effect, as on the power amp): Mechanical 1's X2 FileFunction is
   `NonPlated,1,2,NPTH` although it holds only the profile; solder resist files negative; the CADCAM
   READ-ME says format 4.3 while the files use `FSLAX45Y45`.

## p2k candidates

(Shared-tool limitations met on this board, with the board-local workaround used.)

1. **`TRUNCATED_NETS` keys are looked up by the KiCad refdes and unknown keys are ignored
   silently.** A key in the full-Proteus spelling (e.g. the power amp's `"P.I.GND"`, renamed to
   `PI_GND` by `KICAD_REFDES`) is never checked. Here the keys are the KiCad names (verified by a
   negative test). The shared tool would need: accept either spelling and fail on keys that match no
   refdes.
2. **`p2k.pdsprj.dsn_values` / `lyt_parts` cannot handle single-letter refdes** (`A`-`D`): the refdes
   search matches unrelated one-letter strings and `dsn_values` raises. Workaround for Phase 1: call
   them without `A`-`D` and give those four `TERMINAL` / `PIN` by hand (a board-local override in the
   part-map script, like the pilot's `LATIN1_PARTS`). The shared tool would need: anchor the refdes
   match to the part-record structure. The pilot's candidate 1 (Latin-1 `µ` values dropped) applies
   here too (9 values).
3. **`DRILL_EXCELLON` from a different revision**: the 2010 Excellon lacks the 2 October vias; if
   `gerber_roundtrip` requires a 1:1 match, Phase 4 needs an "expected extra holes" option or a
   board-local wrapper. (Not tried yet.)
4. `p2k ipc356` prints "Net aliases: ." when `NET_ALIASES` is empty (cosmetic, as on the pilot).

## Decisions

- Sheet names (no title blocks in the PDF): Input stage / Second stage / EQ stage / Tone stacks /
  Supply filter, chosen by the agent from the content; the user can rename them (only
  `p2k_config.py`, before `make_skeleton`).
- KiCad refdes: `-` → `_` (`GTR_IN`, `POT1_1`, ...) and the single letters `A`-`D` → `PAD_A`-`PAD_D`
  (agent's choice; `C`/`D` would read as capacitor / diode references, `A`/`B` renamed for
  consistency).
- The October 2010 export is the baseline (user, before Phase 0); the June differences are listed
  above for reference only.
