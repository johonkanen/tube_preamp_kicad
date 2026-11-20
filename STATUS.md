# Status: Preamp (`etunen`)

Plan: [PLAN.md](PLAN.md). Playbook: `tools/p2k/CONVERSION_PLAYBOOK.md`.

| Phase | State |
|---|---|
| 0 Skeleton and inventory | **done** 2026-11-20 (Opus 5.5) |
| 1 Schematic | **done** 2026-11-20 (preparation Opus 5.5, transcription Fable 5.2): 5 sheets, 163/163 parts, netlist = IPC, ERC 0 / 0 |
| 2 Footprints | **done** 2026-11-20 (Opus 5.5): 163/163 parts fit the IPC pads (worst residual 0.001 mm, pcbnew placement 0.001 mm), 16 footprints (13 project + 3 KiCad, + 1 board-only), pin order checked; open: noval socket side (finding 13), KiCad drills smaller than Proteus on RLY1-RLY5, C1/C5/C7/C10, the Orange Drops, C4/C14 |
| 3 PCB | **done** 2026-11-20 (Opus 5.5): board generated and reproducible (`tools/make_pcb.sh`), copper 0 shorts / 0 orphans / 0 opens, check_board OK, **DRC 0 shorts / 0 unconnected / 0 parity, no unaccepted errors** (TO-92 pad 1 round on Q1-Q9, user decision); negative tests done |
| 4 Verification | **done** 2026-11-20 (Fable 5.2, fresh session): `ipc356_diff` OK (366/366 records, 98 nets 1:1), `gerber_roundtrip --check` OK through `tools/roundtrip.py` (0 unexplained clusters, 0 uncovered draws / flashes, 0 drill mismatches; 2010 Excellon 364/364 + the 2 expected October vias), both in `check_all.sh`; PDF re-read against the IPC on all 5 sheets: no disagreement; findings 1-18 confirmed; negative tests done |
| 5 Clean-up | **done** 2026-11-20 (Opus 5.5, clean context): noval sockets U1-U3 on the bottom side with the standard noval numbering (footprint built mirrored; copper, pads, nets unchanged), DRC 36 + 16 accepted errors (was 54 + 16); the PI / FX loop board's two hardened checks ported (`tools/check_drill_smaller.py`, joined no-connect pins in `tools/compare.py` / `tools/erc.sh`); negative tests done; **conversion complete** |
| Design fixes | **done** 2026-11-20 (Opus 5.5, user decisions): G5V-2 symbol relabelled to Omron's terminal names (finding 14), the 9 Proteus track pieces of findings 16 / 20 removed (`REMOVED_TRACKS`), component values unchanged; new check `tools/check_removed_tracks.py`; `make_pcb.sh --check` now stops at a failing step; negative tests done |
| Shared-tool migration | **done** 2026-11-20 (Opus 5.5): step 1 p2k bump to a9a286c (D-R re-baseline), step 2 board-local tools → shared keys (R1 re-baseline, strict opt-outs none), step 3 relay design change (RLY1-RLY5 on `IPC_PIN_IDS`, stock KiCad G5V-2 symbol / footprint; electrically identical); section "Shared-tool migration 2026-11-20" |
| Generation stopped | **2026-11-20** (user decision, Opus 5.5): the committed `kicad/` and `lib/` files are the source, edited in KiCad; generators frozen in `tools/generate/` (never run; `make_pcb.sh` refuses without `--force-regenerate`); `check_all.sh` keeps only the checks against the Proteus truth and KiCad's rules; section "Generation stopped 2026-11-20" |

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

## Phase 1 preparation – done (Opus 5.5, 2026-11-20)

New in this repo (all generated, `--check` in check_all.sh); pieces copied from the power amp
pilot (`~/dev/tube_power_amp_kicad`, read only) and adapted:

- **`tools/make_part_map.py` → `lib/part_map.csv`**: **163 parts**, all on the board (per sheet
  1:36 2:33 3:34 4:39 5:21). Columns `refdes` (KiCad), `sheet` (PDF page), `lib_id`, `value`,
  `device`, `package`, `proteus_refdes` (the 13 renamed terminals: `GTR-IN` … `PAD_A` = `A`),
  `off_board` (empty: none).
  - refdes from `reference/ipc356_pads.json`. **No off-board parts** (`OFF_BOARD` empty): every
    refdes-like word of the PDF text layer is an IPC refdes, a net label (`EQ1`-`EQ3`, `J1`-`J4`,
    `PRE1`, `PRE2`) or value text (`J112`, `MMK J04 1µ`); the PDF has 47 `TERMINAL` words = the 47
    IPC terminals.
  - value = schematic value from ROOT.DSN (`p2k.pdsprj.dsn_values`, called **without `A`-`D`**:
    it raises on single-letter refdes, p2k candidate 2); device / package from ROOT.LYT
    (`lyt_parts`). Board-local overrides:
    - `SINGLE_LETTER_PARTS`: `A`-`D` → value `TERMINAL`, device `TERMINAL`, package `PIN` (ROOT.LYT
      records read by hand: `A TERMINAL TERMINAL PIN J1` … `D … J4`).
    - `LATIN1_PARTS` (pilot p2k candidate 1): values from the PDF for **C4** `MMK J04 1µ`, **C14**
      `1µ mmk`, **C30** `22µ` (device / package from ROOT.LYT as pdsprj reads them; C4's layout value
      is cut to `MMK J04 1`), and the whole record for **C28, C33-C37**: value / device `22µF 450V`,
      package `ELEC D16 R7.5` (ROOT.LYT bytes; pdsprj misses those records). The script fails if
      pdsprj starts reading any of them. The CSV is UTF-8.
    - **Q4 keeps the schematic value `NADA`** (finding 1; device J112 / TO92 from the layout).
  - sheet = PDF page from the text layer; `PAGE_OVERRIDES`: `A`-`D` → 5 (pages 1/2 have the B+ net
    labels A-D), `H4`, `H5` → 3 (the terminals sit at U3; pages 1-3 also have `H4`/`H5` net labels).
    `SW1`-`SW3` resolve to page 5 by themselves (the labels elsewhere are lower case `sw1`-`sw3`).
  - lib_id from the Proteus device (`SYMBOL_BY_DEVICE`): film / ceramic caps (22N XICON, 100N XICON,
    MMK J01, MMK J04 5MM, CERAMIC56P, *ORANGE DROP) → C; HITEMP10U50V, MINELECT10U50V → C_Polarized;
    `22µF 450V` → C_Polarized_12; MINRES100K, METALFILM1K → R; 1N4001 → D; J112; G5V-2(HI) → G5V-2;
    12AX7; TERMINAL → PIN.
- **`tools/gen_symbols.py` → `lib/tube_preamp.kicad_sym`** (9 symbols, all from the KiCad 10
  standard library; no power symbols, the IPC has no `=POWER` nets):

  | Symbol | From | Pins (= IPC ids) |
  |---|---|---|
  | R, C | Device | 1, 2 |
  | C_Polarized | Device:C_Polarized | `+` `-` (C2, C30) |
  | C_Polarized_12 | Device:C_Polarized | **1 = −, 2 = +** (C28, C33-C37; Proteus `*PINOUT ELEC D16 R7.5` + = 2, − = 1; the PDF prints 2 at the + plate) |
  | D | Device:D | `A` `K` |
  | J112 | Device:Q_NJFET_DSG | 1 = D, 2 = S, 3 = G (= the Proteus J112 device, no renumbering) |
  | G5V-2 | Relay:G5V-2_Split, 3 units, pin names hidden | unit 1 coil: 4 = DC1, 5 = DC2; unit 2 pole 1: 2 = COM1, 3 = NC1, 1 = AC1 (NO); unit 3 pole 2: 6 = COM2, 7 = NC2, 8 = AC2 (NO) |
  | 12AX7 | Valve:ECC83, 3 units, **units 1/2 swapped** | unit 1 (A): 1 = A1, 2 = G1, 3 = K1; unit 2 (B): 6 = A2, 7 = G2, 8 = K2; unit 3 (C, heater): 4 = H1, 5 = H2, 9 = HCT (N/C) |
  | PIN | Connector:TestPoint | 1 (the 47 terminals; value `TERMINAL`) |

  **Pinouts (Proteus device / package pin definitions in ROOT.DSN, read by hand; pilot p2k
  candidate 4):**
  - **12AX7** (`*PINOUT 9-PIN BELTON NOVAL`): A1 = 1, G1 = 2, K1 = 3, H1 = 4, H2 = 5, A2 = 6, G2 = 7,
    K2 = 8, HCT = 9: the standard noval pinout, = KiCad ECC83. **Unit split (decided up front):**
    KiCad's units 1 (pins 6/7/8) and 2 (1/2/3) are swapped so that unit A = Proteus element 1
    (pins 1-3) and unit B = element 2 (pins 6-8); unit C = heater (4, 5, 9). KiCad draws the
    envelope for every unit (pilot p2k candidate 8). Pin types: anode, cathode and heater pins
    `passive` (KiCad: output / bidirectional / power_in; the heater and cathode nets have only
    passive parts), grids stay `input` (every grid net has a resistor). **Pin 9 is `passive`, not
    `no_connect`, and gets a no-connect flag** (`_common.tube()` places it): a `no_connect`-type pin
    stays in its own `unconnected-(…)` net in the KiCad 10 netlist even when a wire joins it (ERC
    only warns `no_connect_connected`), so compare_netlists could not catch it being wired by
    mistake; tested both ways in the smoke test (p2k candidate 5).
  - **J112** (device `$PINSHORT` records: `D 1`, `G 3`, `S 2`): **D = 1, S = 2, G = 3**. On the board
    the drain / source roles alternate per part (the J112 is symmetric; the IPC is the truth):

    | Part | pin 1 (D) | pin 2 (S) | pin 3 (G) | PDF (gate always on the right) |
    |---|---|---|---|---|
    | Q1 | #00011 (R3) | PRE-GND | J1 | D at the top (sheet 1) |
    | Q2 | PRE-GND | #00035 (C4/R12) | J2 | S at the top (sheet 1) |
    | Q3 | PRE-GND | #00049 (R19) | J1 | S at the top (sheet 2) |
    | Q4 | PRE-GND | #00050 (C6/R20) | J1 | S at the top (sheet 2) |
    | Q5 | PRE-GND | #00057 (C14/R30) | J1 | S at the top (sheet 2) |
    | Q6 | PRE-GND | #00056 (R29) | J4 | S at the top (sheet 2) |
    | Q7 | #00098 (PRES1) | PRE-GND | J3 | D at the top (sheet 3) |
    | Q8 | #00096 (PRES2) | PRE-GND | J2 | D at the top (sheet 3) |
    | Q9 | #00097 (PRES3) | PRE-GND | J4 | D at the top (sheet 3) |

    So Q2-Q6 have the drain on PRE-GND and the source on the signal node, Q1 and Q7-Q9 the other
    way round (finding 8). KiCad's Q_NJFET_DSG has G on the left, D at the top, S at the bottom:
    "gate right, D at the top" = `place_mirrored(..., axis="y")` (Q1, Q7-Q9); "gate right, S at the
    top" = rotation 180 (Q2-Q6). Check every one against the IPC (compare), not the drawing's look.
  - **G5V-2(HI)** (`*PINOUT G5V-2(HI)`): AC1 = 1, COM1 = 2, NC1 = 3, DC1 = 4, DC2 = 5, COM2 = 6,
    NC2 = 7, AC2 = 8. Confirmed on the PDF: every blade rests on the NC contact (pins 3 / 7), e.g.
    RLY1 pole 1 COM (#00005, U1 anode 2) → NC (#00014, RLY2 COM1), AC (#00020, R8); the coils are
    DC1 = 4 (always H4) and DC2 = 5 (the switch net). Mapped onto KiCad's G5V-2_Split (Omron pins
    1/16 coil, 4/13 COM, 6/11 NC, 8/9 NO): KiCad 1 → 4, 16 → 5, 4 → 2, 6 → 3, 8 → 1, 13 → 6, 11 → 7,
    9 → 8. Pin names (Proteus) hidden on the symbol (they cover the contact drawing). Nets:

    | Relay | coil 4 / 5 | pole 1: COM 2 / NC 3 / NO 1 | pole 2: COM 6 / NC 7 / NO 8 |
    |---|---|---|---|
    | RLY1 | H4 / SW1 | #00005 / #00014 / #00020 | #00017 / #00018 / #00019 |
    | RLY2 | H4 / SW2 | #00014 / #00021 / #00026 | #00018 / #00024 / #00025 |
    | RLY3 | H4 / SW1 | PRE1 / #00046 / #00062 | EQ / PRE2 / #00062 |
    | RLY4 | H4 / #00081 | #00073 / #00079 / #00085 | #00082 / EQ1 / #00084 |
    | RLY5 | H4 / SW3 | #00085 / #00086 / #00090 | #00084 / EQ2 / EQ3 |

    In the PDF the upper drawn switch of RLY1/RLY2/RLY4 is pole 2 (COM 6) and the lower one pole 1
    (COM 2); read the pole from the COM net, not from the position.
  - 1N4001 A/K; electrolytics as in the table. No surprises against the datasheets.
- **`p2k make_skeleton`** → `kicad/` (tube_preamp.kicad_pro, sym-lib-table, root sheet with the 5
  sub-sheets `01 Input stage` … `05 Supply filter`, empty sub-sheets).
  **`tools/erc.sh`** (as the pilot). **`tools/sheets/_common.py`** (from the pilot): `part()`,
  `sh_value()`, `sym()` from the part map; `term()` (terminal with value TERMINAL and the pilot's
  text justification, pilot p2k candidates 3, 7); `P()` (PDF render position in 10 px units →
  sheet point); `place_mirrored()` (pilot p2k candidate 6); new **`tube()`** (places all 3 units of
  a 12AX7 and the pin 9 no-connect flag) and **`relay()`** (all 3 units of a G5V-2).
- **`tools/check_all.sh`**: + part map, symbol library, symbol pins vs IPC, ERC, netlist
  comparison (`--allow-missing` until the 5 sheets are drawn).
- **Smoke test** (scratch copy in build/tmp/smoke, deleted): U1 with `tube()` (3 units, pin 9
  flagged), RLY1 with `relay()` + D1 across the coil, terminals GTR_IN / GTR_GND / PAD_A (on J1),
  R1, R2, R4, Q1, global labels H4, H5, SW1, PRE-GND, J1, dummy local labels on the other pins →
  compare 0 wrong-net pins (U1-9 accepted as N/C), ERC 0 errors (12 isolated-label warnings of
  the dummy labels). Render checked: unit A = pins 1-3, the relay blades rest on NC 3 / 7.
  Negative tests: U1-9 wired to H5 → compare "N/C mismatch: U1-9 … on KiCad net H5" (with pin 9
  as `no_connect` type this was **not** detected: the reason for `passive`); pin 9 without the
  flag → ERC error; Q1 drain on PRE-GND (D/S swapped) → "KiCad net PRE-GND merges IPC nets";
  coil pins 4/5 swapped → 2 merge errors; grid wire missing → compare split error + ERC errors;
  a lower-case label `h4` → only a split **warning** while H4 has undrawn pins (it becomes an
  error once all sheets are drawn); C28 on symbol C_Polarized, a pin renumbered in the library →
  check_symbols fails; part map / library edited → `--check` fails; a wrong / unknown
  `PAGE_OVERRIDES` entry → make_part_map fails.

### Transcription rules (for the sheet sessions)

- **Symbols and values**: only `tube_preamp:` symbols, exactly the `lib_id` and `value` of
  `lib/part_map.csv` per refdes (`_common.sym(ref)`, `sh_value(ref)`; the µ values are in the map;
  Q4's value is `NADA`). Refdes = the `refdes` column: `GTR_IN`, `GTR_GND`, `POT_GND`,
  `POT1_1` … `POT3_2`, `PAD_A`-`PAD_D` (Proteus `A`-`D`); the others as in the PDF.
  Terminals with `_common.term()` (never `sheetkit.terminal`: wrong value, texts over the circle).
- **Net names = IPC names** (`reference/pins_by_net.md`), whatever case the PDF writes. **The PDF
  writes `pre-gnd` (sheet 1), `sw1` / `sw2` / `sw3` (sheets 1-3), `h4` / `h5` (sheet 1, at U1) and
  `j4` (sheet 2, Q6): label them `PRE-GND`, `SW1`-`SW3`, `H4`, `H5`, `J4`** (KiCad names are
  case-sensitive; Proteus ignores case). Named nets and their sheets (global labels on every sheet
  they appear on):

  | Net | Sheets | Pins |
  |---|---|---|
  | `PRE-GND` | 1-5 | 45 pins (ground) |
  | `H4` | 1, 2, 3 | heater pin 4 of U1-U3, every relay coil pin 4, D1/D2/D3/D8/D9 anodes, terminal H4 (sheet 3) |
  | `H5` | 1, 2, 3 | U1-U3 pin 5, terminal H5 (sheet 3) |
  | `A` | 1, 5 | R6-1, R62-1, C28-2 |
  | `B` | 1, 5 | R7-1, R62-2, R63-1, C33-2 |
  | `C` | 2, 5 | R22-2, C8-1, R63-2, R64-1, C34-2 |
  | `D` | 2, 5 | R23-2, R64-2, R65-1, C35-2 |
  | `E` | 3, 5 | U3-1, R33-2, R65-2, R66-1, C36-2 (sheet 3 label `E` above U3 pin 1) |
  | `F` | 3, 5 | R34-2, R66-2, R67-1, C37-2 |
  | `J1` | 1, 2, 5 | Q1/Q3/Q4/Q5 gates, PAD_A |
  | `J2` | 1, 3, 5 | Q2/Q8 gates, PAD_B |
  | `J3` | 3, 5 | Q7 gate, PAD_C |
  | `J4` | 2, 3, 5 | Q6/Q9 gates, PAD_D |
  | `SW1` | 1, 2, 5 | RLY1-5, RLY3-5, D1-K, D3-K, terminal SW1 |
  | `SW2` | 1, 3, 5 | RLY2-5, D2-K, D5-A, terminal SW2 |
  | `SW3` | 3, 5 | RLY5-5, D9-K, D4-A, terminal SW3 |
  | `PRE1` | 1, 2 | R15-1, RLY3-2 |
  | `EQ` | 2, 3 | RLY3-6, C10-1 |
  | `EQ1` / `EQ2` / `EQ3` | 3, 4 | RLY4-7 / RLY5-7 / RLY5-8 and the tone-stack inputs (C18/R35, C22/R38, C26/R41) |
  | `PRE2` | 2 only | RLY3-7, U2-6, R23-1, R50-1 → **local** label `PRE2` (two on sheet 2) |

  All other nets are Proteus auto-names (`#000xx`): plain wires; **none crosses a sheet**. There
  are no single-pin nets besides the N/C pins.
- **Terminal refdes are not net names**: the terminals `PAD_A`-`PAD_D` (sheet 5) are on **J1-J4**,
  not on the B+ nets A-D (sheet 5 draws `J1`-`J4` labels on them: global labels `J1`-`J4`). Only
  the terminals `H4`, `H5` (sheet 3) and `SW1`-`SW3` (sheet 5) share their net's name. `PREPOWER`
  is on #00131 (R67-2), `PRERETURN`, `GTR_GND`, `POT_GND`, `MV0` on PRE-GND. Never put a label
  named after a terminal on a wire unless the table above says so.
- **12AX7 (U1-U3)**: `tube(sh, ref, a, b, heater)` places all three units (unit A = pins 1-3,
  unit B = 6-8, unit C = heater 4/5) and the no-connect flag on pin 9; heater pins 4 → `H4`, 5 →
  `H5` (global labels, as the PDF's h4/h5 / H4/H5 labels at each tube). KiCad's symbol has the
  cathode at the bottom and the anode at the top like the Proteus one; the heater is its own
  unit (place it below the tube, where the PDF draws pins 4/5/9).
- **G5V-2 (RLY1-RLY5)**: `relay(sh, ref, coil, pole1, pole2)` places all three units; pole 1 =
  COM 2 / NC 3 / NO 1, pole 2 = COM 6 / NC 7 / NO 8 (table above; identify the pole in the PDF by
  its COM net). The diode across each coil: anode on H4 (finding 4).
- **J112 (Q1-Q9)**: pins 1 = D, 2 = S, 3 = G; orientation per part from the table above (Q2-Q6
  have D on PRE-GND: rotation 180; Q1, Q7-Q9: `place_mirrored(axis="y")`).
- **Electrolytics**: C2 / C30 `C_Polarized` (`+` / `-`), C28 / C33-C37 `C_Polarized_12` (pin 2 = +
  on the B+ node, pin 1 = − on PRE-GND).
- **N/C pins**: only U1-U3 pin 9 (flagged by `tube()`). No other pin is left open.
- **Grid 1.27 mm**: symbols, wires and labels on the grid (`g(n)`, `P(x, y)` = PDF render position in
  10 px units of `build/tmp/pdf/hi-N.png`); `p2k.sheetkit` helpers (`vert2`, `horiz2`,
  `glabel_left/right`, `label_left/right`, …). Repeated blocks as helpers in `tools/sheets/_common.py`:
  the three identical tone stacks of sheet 4 (EQn input, C 250p, R 220k, LOnX/LOnW/LOnO terminals,
  C 1N / 4N7, R 220K to HInW, R 4k7, C 2N2 to HInX; offsets per stack), and the relay coil + diode
  block (sheets 1-3).
- One script per sheet, `tools/sheets/sheetNN.py` (NN = PDF page), rebuilding `kicad/NN_*.kicad_sch`
  from scratch (two runs byte-identical); render with `tools/p2k/bin/p2k render_sheet
  kicad/NN_*.kicad_sch` and compare with `build/tmp/pdf/hi-N.png` (`pdftoppm -r 200 -png
  source/schematic_pdf/etunen.PDF build/tmp/pdf/hi`).
- After each sheet: `tools/p2k/bin/p2k compare_netlists --allow-missing --sheet N` and
  `tools/erc.sh`, then `tools/check_all.sh`. Target per sheet: 0 missing on that sheet, 0 compare
  errors, 0 ERC errors (warnings explained here). Expected while sheets are missing: isolated
  global-label warnings, split **warnings** for nets with pins on undrawn sheets, and ERC
  `pin_not_driven` errors for a J112 gate whose net has no terminal yet (draw sheet 5 first: its
  PAD_A-PAD_D drive J1-J4). After the last sheet: drop `--allow-missing` in check_all.sh.
- **Suggested order**: 5 Supply filter (21 parts: the label vocabulary A-F, J1-J4, SW1-SW3,
  PRE-GND) → 4 Tone stacks (39, three identical stacks) → 1 Input stage (36) → 2 Second stage (33)
  → 3 EQ stage (34).

## Phase 1 transcription – done (Fable 5.2, 2026-11-20)

One script per sheet, `tools/sheets/sheetNN.py`, rebuilding `kicad/NN_*.kicad_sch` from scratch (two
runs byte-identical, checked for all five). Order 5, 4, 1, 2, 3, one commit per sheet.

| Sheet | Parts | Compare (`--sheet N`) | ERC after the sheet |
|---|---|---|---|
| 5 Supply filter | 21/21 | 0 wrong-net pins, 0 errors | 0 errors, 7 warnings (isolated J1-J4 / SW1-SW3 labels: other sheets undrawn) |
| 4 Tone stacks | 39/39 | 0 / 0 | 0 errors, 7 warnings (same) |
| 1 Input stage | 36/36 | 0 / 0 | 0 errors, 5 warnings (PRE1, H5, J3, J4, SW3 labels alone) |
| 2 Second stage | 33/33 | 0 / 0 | 0 errors, 3 warnings (EQ, J3, SW3 labels alone) |
| 3 EQ stage | 34/34 | 0 / 0 | **0 errors, 0 warnings** |

**Result:** 163/163 parts, 339 pins compared, 0 wrong-net pins, all 98 IPC nets complete (compare
counts 101 = 98 nets + the 3 N/C pads U1-9, U2-9, U3-9), 0 missing, 0 extra; ERC 0 errors, 0 warnings.
`tools/check_all.sh` runs the comparison without `--allow-missing` now.

- **Method:** the nets come from `reference/pins_by_net.md` (the IPC), the layout and the
  topology from the PDF pages; where the drawing was laid out, the PDF connection was looked at
  next to the IPC net and no disagreement between the PDF and the IPC was noticed. This is not
  an independent pin-by-pin reading of the PDF (compare against the IPC is the oracle; Phase 4
  re-reads).
- **Layout vs the PDF** (same nets; noted in each script's docstring): `P()` positions of the
  PDF render are kept where possible. The KiCad 12AX7 is three units, so each tube is drawn as
  triode A, triode B **mirrored** (grid and cathode on the right, like the right half of the
  Proteus symbol; `tube(..., mirror_b=True)`) and a separate heater unit (sheet 1: lower right,
  sheet 2: between the cathode networks, sheet 3: upper right together with the pads H4 / H5);
  everything right of a tube is 6 or more grid units further right. The relay poles are
  KiCad's G5V-2 units at rotation 270 (COM left, NC upper right, NO lower right; the blade rests
  on NC as in the PDF), coils at rotation 180 (pin 5 at the top), the diode beside the coil; the
  relay blocks are wider than in the PDF. Sheet 2: R50 runs straight down to the rail (the PDF
  jogs it). Sheet 3: Q7-Q9 / PRES1-PRES3 and the relay block are further right.
- **Helpers added to `tools/sheets/_common.py`:** `tube(mirror_b=)` with text placement,
  `relay()` text placement (centred texts beside the coil / above each pole), `coil_block()`
  (diode across a coil, H4 / SWn labels below; `sw_label=False` for RLY4 whose pin 5 is #00081),
  `hcap()` (horizontal capacitor with the texts clear of the plates), `tone_stack()` (sheet 4).
- **`tools/compare.py`** (board-local wrapper, p2k candidate 9): `p2k compare_netlists` raised
  `TypeError: '<' not supported between instances of 'int' and 'str'` as soon as sheet 3 was
  drawn (PRES next to PRES1-PRES3). check_all.sh calls the wrapper.
- **Labels:** global labels for PRE-GND, H4, H5, A-F, J1-J4, SW1-SW3, PRE1, EQ, EQ1-EQ3 in the
  IPC spelling; PRE2 two local labels on sheet 2; all #000xx nets are wires. A note text on each
  sheet lists the PDF's lower-case labels and the renamed terminals.
- **Negative test** (restored afterwards): sheet 1's `J1` global label moved from Q1's gate onto
  the `A` wire → compare 2 errors ("KiCad net A merges IPC nets [J1 …] [A …]", "IPC net J1
  split … [unconnected-(Q1-G-Pad3): Q1-3]", 4 wrong-net pins), ERC 2 errors. During the work the
  checks also caught a real slip: sheet 5's first run had no junction where the ground rail
  passes C28 → split warning `unconnected-(C28---Pad1)` and an ERC error.
- `reports/render/` (schematic PNGs of `p2k render_sheet`) is git-ignored.

## Phase 2 – done (Opus 5.5, 2026-11-20)

New in this repo (all generated, in check_all.sh); pieces taken from the power amp pilot
(`~/dev/tube_power_amp_kicad`, read only: its `gen_footprints.py` specs for the fly-lead terminal,
DO-41, TO-92 P2.03, 2 W resistor, 22n Xicon, mounting hole, the fp-lib-table helper, and its
`check_pin_order.py`):

- **`p2k_config.py`**: `FOOTPRINT_PAD_SIZES = "kicad"` (the default, explicit), `OFF_BOARD_PARTS = {}`
  (every part is on the board), `HOLE_FOOTPRINT = tube_preamp:MountingHole_3.0mm_PTH_Pad6.35mm` /
  `HOLE_VALUE` (for Phase 3 `build_pcb`).
- **`tools/gen_footprints.py`** (RULES + PROJECT, `p2k.footprints.run`) → `lib/footprint_map.csv`
  (163 rows), `lib/tube_preamp.pretty/` (14 files: 13 used + the board-only mounting hole) and
  **`kicad/fp-lib-table`** (written and `--check`ed by the board script, pilot p2k candidate 12).
  One rule per Proteus package, matched on `package` + span + pad size + drill.
- Sheet scripts re-run: the 179 placed symbol units (163 parts + the 2 extra units of each 12AX7 and
  G5V-2) carry their footprint; nothing else changed in the sheets (diff = the Footprint lines only;
  two runs byte-identical); ERC 0/0, compare unchanged.
- **`tools/check_pin_order.py`** (board script from the pilot, p2k candidate 13): fits the
  **unmoved** KiCad base footprints with the generator's renumbering (imported from
  `gen_footprints.PROJECT`) onto the IPC pads, both unmirrored and mirrored, plus an ideal
  standard noval on the Proteus pitch circle; new here: **derived pads stay on the renumbered base
  pads** (`MOVE_LIMIT`: only the intended pitch change) and **polarity** stated independently
  (`POLARITY`: the marked KiCad pad 1 = `+` / `2` / `K` from the Proteus pinouts), because a wrong
  renumbering of a two-pad part fits either way round and `derive()` would move the pads onto the
  IPC positions (p2k candidate 14). `--render` (system python3 with matplotlib) writes
  `reports/pin_order/<ref>.png`.
- **`tools/check_all.sh`**: + footprint library / map / fp-lib-table up to date
  (`gen_footprints.py --check`), footprints vs IPC pads (`kipy -m p2k.check_footprints --pcbnew`),
  pin order (`kipy tools/check_pin_order.py`).

### Footprints and fit

| Parts | Proteus package (2010) | Footprint | How | Pads IPC → footprint (mm, pad / drill) |
|---|---|---|---|---|
| 46 R (R1-R5, R8-R21, R24-R32, R34-R51) | RES40 | `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` | KiCad, unchanged | 1.778/0.762 → 1.6/0.8 |
| R6, R7, R22, R23, R33, R62-R67 | 2W METAL FILM RESISTOR | `R_Axial_DIN0414_L11.9mm_D4.5mm_P19.05mm_Horizontal` | derived from `..._P20.32mm` (pilot) | 2.286/1.016 → **2.4**/1.2 |
| C1, C5, C7, C10 | 22N XICON | `C_Rect_L13.0mm_W6.0mm_P9.70mm` | derived from `C_Rect_L13.0mm_W6.0mm_P10.00mm_FKS3_FKP3_MKS4` (pilot; silk 12.8 x 6.0) | 2.54/1.143 → 2.0/**1.0** |
| C8, C11-C13, C16, C17, C19-C21, C23-C25, C27, C29 | 1N / 2N2 / 3N3 / 4N7 ORANGE DROP | `C_Rect_L16.5mm_W7.0mm_P9.70mm` | derived from `C_Rect_L16.5mm_W7.0mm_P15.00mm_MKT` (Proteus silk 15.1 x 6.7 mm; KiCad's nearest box), pads moved 2.65 mm in | 2.54/1.143 → 2.2/**1.1** |
| C15 | 100N XICON | `C_Rect_L24.0mm_W7.0mm_P20.00mm` | derived from `C_Rect_L24.0mm_W7.0mm_P22.50mm_MKT` (silk 23.1 x 6.0) | 2.54/1.143 → 2.4/1.2 |
| C3, C6, C9 | MMK 2.5*7.2 | `Capacitor_THT:C_Rect_L7.2mm_W2.5mm_P5.00mm_FKS2_FKP2_MKS2_MKP2` | KiCad, unchanged (silk 7.2 x 2.5) | 1.778/0.762 → 1.6/0.8 |
| C4, C14 | MMK J04 | `Capacitor_THT:C_Rect_L7.2mm_W5.0mm_P5.00mm` | KiCad, unchanged (silk 7.2 x 5.0) | 1.778/0.762 → 1.5/**0.75** |
| C18, C22, C26 | CAP20 | `C_Disc_D7.5mm_W2.5mm_P5.08mm` | derived from `C_Disc_D7.5mm_W2.5mm_P5.00mm` | 1.778/0.762 → **2.0**/1.0 |
| C2 | ELEC-RAD10 | `CP_Radial_D6.3mm_P2.54mm_PM` | derived from `CP_Radial_D6.3mm_P2.50mm`, pads 1 → `+`, 2 → `-`, moved to P2.54 | 2.032/0.762 → 1.6/0.8 |
| C30 | 22U 100V | `CP_Radial_D6.3mm_P2.50mm_PM` | same base, pads 1 → `+`, 2 → `-` | 2.032/0.762 → 1.6/0.8 |
| C28, C33-C37 | ELEC D16 R7.5 | `CP_Radial_D16.0mm_P7.50mm_Pin2Plus` | KiCad `CP_Radial_D16.0mm_P7.50mm`, pads **1 → `2`, 2 → `1`** (Proteus + = 2) | 2.54/1.143 → 2.4/1.2 |
| D1-D5, D8, D9 | DO41 | `D_DO-41_SOD81_P10.16mm_Horizontal_AK` | KiCad, pads 1 → `K` (band), 2 → `A` (pilot) | 2.286/1.016 → 2.2/1.1 |
| Q1-Q9 | TO92 | `TO-92_Inline_P2.03mm` | derived from `TO-92_Inline_Wide` (pilot; Proteus P2.032), no renumbering (J112 1 = D, 2 = S, 3 = G = KiCad pads 1-3) | 1.524/0.762 → 1.5/0.8 |
| RLY1-RLY5 | G5V-2(HI) | `Relay_DPDT_Omron_G5V-2_ProteusPins` | KiCad `Relay_DPDT_Omron_G5V-2`, Omron pads renumbered to the Proteus ids (below), pads not moved | 2.54/1.143 → **1.4/0.7** |
| U1-U3 | 9-PIN BELTON NOVAL | `Valve_Noval_Belton_PCD21.00mm` | **built from the IPC pads** (U1): KiCad `Valve_Noval_P` is on a 2.54 mm grid; Proteus: 9 pads on a 21.00 mm pitch circle (10 positions at 36°, gap between 9 and 1); body = the Proteus Top Assembly rectangle 26.4 x 25.4 mm (read from the gerber, `noval_body()`) | 4.318/1.727 (Proteus) |
| 47 terminals | PIN | `FlyLead_Pad_D3.048mm_Drill1.524mm` | built from the IPC pads (GTR_IN), same name as on the power amp | 3.048/1.524 (Proteus) |
| 13 holes (Phase 3) | mounting holes | `MountingHole_3.0mm_PTH_Pad6.35mm` | board-only, plated, pad number 1, no net (pilot) | 6.35/3.0 (Proteus) |

`check_footprints`: **163/163 parts, 339 pads, worst residual 0.001 mm**; `--pcbnew` placement worst
0.001 mm; every part on the top side (no THT pattern fits only mirrored); `reports/footprint_fit.csv`
(placement for Phase 3) and `reports/footprint_pads.csv` written. The six resistors with stale
layout values (finding 7) and Q4 `NADA` (finding 1) have the layout packages RES40 / 2 W / TO92 like
their families, so the open value questions do not touch the footprints.

**Pad size / drill differences KiCad vs Proteus, per refdes** (for Phase 3 DRC and Phase 4; a
**user decision**, left open here):

| KiCad vs Proteus | Parts | Pad (KiCad / Proteus) | Drill (KiCad / Proteus) |
|---|---|---|---|
| **pad larger** | R6, R7, R22, R23, R33, R62-R67 | 2.4 / 2.286 (+0.057 per side) | 1.2 / 1.016 (larger) |
| **pad larger** | C18, C22, C26 | 2.0 / 1.778 (+0.111 per side) | 1.0 / 0.762 (larger) |
| **drill smaller** | **RLY1-RLY5** | 1.4 / 2.54 | **0.7 / 1.143** (-0.443) |
| **drill smaller** | C1, C5, C7, C10 | 2.0 / 2.54 | **1.0 / 1.143** (as the power amp's C1-C6) |
| **drill smaller** | C8, C11-C13, C16, C17, C19-C21, C23-C25, C27, C29 | 2.2 / 2.54 | **1.1 / 1.143** |
| **drill smaller** | C4, C14 | 1.5 / 1.778 | **0.75 / 0.762** |
| smaller pad, larger drill | 46 RES40 R, C3/C6/C9, C2, C30, C15, C28/C33-C37, D*, Q* | smaller | larger |
| equal (Proteus pads) | U1-U3, 47 terminals, 13 holes | = | = |

So Phase 4 (`ipc356_diff`, `gerber_roundtrip`) will report drill mismatches for **RLY1-RLY5 (0.7 vs
1.143), C1/C5/C7/C10 (1.0 vs 1.143), the 14 Orange Drops (1.1 vs 1.143) and C4/C14 (0.75 vs 0.762)**:
either `DRILL_SMALLER` entries `(1.143, 0.7)`, `(1.143, 1.0)`, `(1.143, 1.1)`, `(0.762, 0.75)` or Proteus
drills (`ipc_sizes`) on those footprints. The relay is the big one: the 2010 board was built with
1.143 mm relay holes; KiCad's G5V-2 footprint uses 0.7 mm. The KiCad pads are larger than Proteus
only on the 2 W resistors and the CAP20 discs (clearance to check in the Phase 3 DRC).

### Pin order (`tools/check_pin_order.py`, renders in `reports/pin_order/`)

| Parts | Unmoved KiCad base | Unmirrored | Mirrored | Result |
|---|---|---|---|---|
| Q1-Q9 (J112) | TO-92_Inline_Wide | 0.508 @ 180° (pitch 2.54 vs 2.032) | 0.508 | inline: body marker decides; KiCad flat side = Proteus flat side on **all nine** (renders): **1 = D, 2 = S, 3 = G on the JEDEC pads 1-3, as KiCad**. The D / S swap of finding 8 is only the net role (Q2-Q6 drain on PRE-GND); the pad order is the same on every part, no pinout oddity |
| D1-D5, D8, D9 | D_DO-41 (1 = K) | 0.000 | 0.000 | KiCad band at K = Proteus band at K on all seven: **polarity as KiCad** |
| C2, C30 | CP_Radial_D6.3 (1 = +) | 0.020 / 0.000 | same | KiCad `+` / square pad at the Proteus `+` mark: **polarity as KiCad** |
| C28, C33-C37 | CP_Radial_D16.0 (1 = + → Proteus `2`) | 0.000 | 0.000 | KiCad `+` at pin 2 = Proteus `+` mark at pin 2 on all six |
| RLY1-RLY5 | Relay_DPDT_Omron_G5V-2, Omron 16/13/11/9 → 4/2/3/1, 1/4/6/8 → 5/6/7/8 | **0.000** | 7.620 | by pad position: Proteus coil pin 4 + pole 1 (COM 2, NC 3, NO 1) sit on the Omron **16 / 13 / 11 / 9** column, coil pin 5 + pole 2 (6 / 7 / 8) on **1 / 4 / 6 / 8** (KiCad top view) |
| RLY1-RLY5 | same base, Phase 1 symbol mapping (Omron 1/4/6/8 → 4/2/3/1) | 7.620 | **0.000** | the column-for-column reading of the symbol mapping fits only mirrored (finding 14) |
| U1-U3 | Valve:Valve_Noval_P | **17.631** | **2.972** | only the **mirrored** KiCad noval matches; ideal standard noval on the 21.00 mm circle: unmirrored 19.319, mirrored **0.007** (finding 13) |

Derived footprints: pads moved from the renumbered base only by the pitch change (TO-92 0.508, DIN0414
0.635, C_Rect 0.15 / 2.65 / 1.25, disc 0.04, C2 0.02, the rest 0.000). Polarity: marked KiCad pad 1
= `+` (C2, C30), `2` (C28, C33-C37), `K` (diodes).

**The noval sockets are the oddity** (finding 13), as the octal sockets on the power amp: the
Proteus pad ids run 1 → 9 **clockwise seen from the component (top) side** (1 lower left, 2 left,
3 upper left, 4 / 5 top, ..., 9 bottom; in the IPC frame pin k at -144° - 36°(k-1)); the noval
standard (KiCad) runs clockwise seen from the pin / solder side. The footprint keeps the Proteus ids
and the top side (reproduces Proteus; copper identical either way). **User question.**

**Negative tests** (restored afterwards; a scratch script in build/tmp, not committed): (1) 22N XICON rule → the unmoved KiCad
`C_Rect_L13.0mm_W6.0mm_P10.00mm` → `gen_footprints --check` out of date (exit 1); check_footprints
"schematic footprint != map (re-run the sheet scripts)"; after re-running the sheets "residual 0.150
mm" on C1/C5/C7/C10 (exit 1). (2) noval pad 4 moved 0.1 mm in the library file → `--check` out of
date, check_footprints U1-U3 residual 0.089 (exit 1). (3a) TO-92 pads 2/3 swapped in the library
file → `--check` out of date, check_footprints Q1-Q9 residual 2.032 (exit 1). (3b) relay renumbering
COM1 / NC1 swapped in gen_footprints (library regenerated) → **check_footprints still OK** (derive
moves the pads onto the IPC), check_pin_order fails (unmirrored fit 5.080, derived pads moved 5.080).
(3c) C28 family renumbering dropped / C2 `+` / `-` swapped (library regenerated) → check_footprints OK,
check_pin_order fails on `POLARITY` (before `POLARITY` was added this was not caught: p2k candidate
14). (4) noval expectation set to unmirrored → check_pin_order FAILED. (5) `kicad/fp-lib-table`
removed → `--check` exit 1. All pass again with the committed files.

## Phase 3 – PCB – done (Opus 5.5, 2026-11-20)

`kicad/tube_preamp.kicad_pcb` is generated: `tools/make_pcb.sh` runs the shared tools (a few
seconds), two runs give a byte-identical board; `tools/make_pcb.sh --check` (in `check_all.sh`)
rebuilds it in `build/tmp/make_pcb_check` (with a copy of the `.kicad_pro`) and compares the board,
`reports/pour_nets.json` (empty) and the stage A/B part of `reports/assign_nets.txt`. Do not hand-edit
the board. `build_pcb` writes the design rules into `kicad/tube_preamp.kicad_pro` (committed).
Scripts taken from the power amp pilot (read only): `make_pcb.sh` (+ the hole rename step) and
`tools/measure_gaps.py` (unchanged copy).

The first session stopped at the DRC: 2 clearance errors caused by the KiCad TO-92 square pad 1
(below). **User decision 2026-11-20: option (a), a round pad 1 at the KiCad size 1.5 mm on Q1-Q9.**
Applied board-locally in `tools/gen_footprints.py` (spec key `pad_shapes`, below); since then the DRC
has no unaccepted errors and is a step of `check_all.sh` ("DRC with schematic parity", `p2k drc`).

### Steps (tools/make_pcb.sh)

| Step | Tool | Result |
|---|---|---|
| 3a | `p2k.build_pcb` | 163 footprints with nets and symbol links at `reports/footprint_fit.csv`; 2 Cu layers (Top / Bottom Copper → F.Cu / B.Cu); outline 382.79 × 71.905 mm (4 Mechanical 1 segments); 13 mounting holes = `tube_preamp:MountingHole_3.0mm_PTH_Pad6.35mm` at the IPC hole records (plated, no net); thickness 1.6 mm; rules below; 101 board nets (98 IPC nets + the 3 `unconnected-(…)` pin-9 nets). |
| 3a' | `tools/rename_holes.py` (board-local) | holes H1-H13 → **H101-H113**: `build_pcb` hard-codes the hole refdes `H<n>`, and this board has the schematic terminals **H4 and H5** (heater fly-lead pads): with holes H4 / H5 the pads collided in `ipc_to_kicad_nets` ("IPC net H4 spans KiCad nets ['', 'H4']", assign_nets failed) and the references were duplicated. The H prefix is kept because Phase 4 `ipc356_diff` recognises plated board-only holes by `H\d+` (p2k candidate 18). |
| 3b | `p2k.gerber_to_tracks` | 747 tracks (F.Cu 402 / B.Cu 345), **14 vias (IPC 14)**, 0 pours, 8 profile draws skipped; every pad flash (339 per layer) lands on a footprint pad, every OtherPad flash on a mounting-hole pad, every drill on a pad hole or via. |
| 3c | `p2k.assign_nets` | stage A = stage B (no pours): **114 groups (98 nets + 13 holes + 3 N/C pin-9 pads), 0 shorts, 0 orphans, 0 opens**; 761/761 tracks + vias got their net. |
| 3e | `p2k.place_refdes` | 119 references kept, 57 moved (sizes 1.0, 0.8 mm) – as the pilot. |
| check | `p2k.check_board` | 339 pads within 0.001 mm and on the IPC nets (98 IPC nets 1:1), 13 mounting holes (size, plating, no net), 747 tracks, 14 vias, 0 zones: **OK**. |
| check | `p2k.assign_nets --check` | KiCad geometry: 114 groups, 0 shorts, 0 orphans, 0 opens, 0 items with a foreign net: **OK**. |
| check | `p2k drc` | **0 shorts, 0 unconnected, 0 parity, 0 unaccepted errors** (176 items: 54 + 16 accepted errors, 106 warnings, below). In `check_all.sh`. |

Hole refdes vs README's mechanical table (positions relative to the lower-left outline corner):
H101 = README H7 (5.492, 66.05), H102 = H12, H103 = H13, H104 = H2, H105 = H8, H106 = H1, H107 = H3,
H108 = H9, H109 = H5, H110 = H4, H111 = H10, H112 = H6, H113 = H11 (`build_pcb` numbers the top row
first, left to right).

### Design rules (p2k_config.py `PCB_RULES`, `PCB_THICKNESS`)

Measured on the Proteus copper (`tools/measure_gaps.py`, assign_nets stage B geometry = Proteus pad
flashes + tracks + vias): smallest different-net gap **0.381 mm** (15 mil) pad–track (RLY1-6 / the
RLY1 NC1 track on F.Cu) and track–via (RLY4A-DC2 track / via on J2 at (-16.51, -28.575)); track–track
0.390 (a 45° track by a straight one, B.Cu near (76.8, -27.9)); pad–pad 0.468 (C30 + / −, P2.50 with
2.032 mm pads); copper to outline ≥ **0.521 mm** (terminal H4); drill to drill ≥ 1.270 mm (TO-92,
1.232 with the KiCad 0.8 drills); thinnest conductor 0.508 mm; the 14 vias 1.27 / 0.508 mm.
Rules: clearance **0.38** (also the netclass clearance), min track 0.5, min via 1.2, min annular 0.3
(via 0.381; smallest KiCad pad ring 0.35), min drill 0.5, hole clearance 0.25, hole-to-hole 1.0,
copper-to-edge 0.5; Default netclass track 0.508, via 1.27 / 0.508 (= the Proteus vias).
Thickness **1.6 mm**: the 2010 fab READ-ME has no stack-up; the 2026 export's READ-ME lists Proteus
8's default 2-layer stack (2 × 0.036 Cu + 1.483 FR4 = 1.555 mm + resist), written when the design was
re-saved – not the 2010 order (as the pilot; change `PCB_THICKNESS` if the board measures otherwise).

### KiCad pads: the larger pads are fine; TO-92 pad 1 made round (user decision (a))

The KiCad pads larger than Proteus (2 W resistors R6, R7, R22, R23, R33, R62-R67: 2.4 vs 2.286; CAP20
discs C18, C22, C26: 2.0 vs 1.778) give **no** DRC error at 0.38 mm. The drills are decided
(`DRILL_SMALLER`) and DRC does not touch them.

**2 clearance errors, Q4 and Q6**: the KiCad TO-92 footprint (`TO-92_Inline_P2.03mm`, derived from
`TO-92_Inline_Wide`) has a **square 1.5 × 1.5 mm pad 1**; Proteus has a **round 1.524 mm** pad. On Q4
and Q6 a 0.508 mm F.Cu track leaves pad 2 (the source, `Net-(Q4-S)` / `Net-(Q6-S)`) at 45° and passes
the corner of pad 1 (PRE-GND):

| Refdes | Track (KiCad frame) | Pad 1 | Gap Proteus (round 1.524) | Gap KiCad (square 1.5) | Gap with a round 1.5 pad |
|---|---|---|---|---|---|
| Q4 | (-36.957, 21.59) → (-35.052, 23.495), Net-(Q4-S) | (-36.957, 23.622), PRE-GND | 0.421 | **0.122** | 0.433 |
| Q6 | (33.655, -3.175) → (29.845, 0.635), Net-(Q6-S) | (31.623, -3.175), PRE-GND | 0.421 | **0.122** | 0.433 |

(Track centre line 1.437 mm from the pad-1 centre; the square corner reaches 1.061 mm.) The other seven
J112s (same footprint) have no track that close. A rounded-rectangle pad 1 does not help unless it is
practically round (corner radius ≥ 0.62 mm). **Options for the user**: (a) round pad 1 (KiCad size
1.5 mm) on the TO-92 footprint for all Q1-Q9 (pin 1 then marked only by silk; gap 0.433); (b) the
Proteus pads (round 1.524 / 0.762, `ipc_sizes`) on Q1-Q9 (gap 0.421, as built); (c) keep the square
pad and accept the two errors (0.122 mm copper gap; not recommended, and `DRC_ACCEPTED` works per
error type, so it would also hide every other clearance error). (a) or (b) only on Q4 / Q6 would need
a second footprint.

**Applied: (a)** (user, 2026-11-20). `TO-92_Inline_P2.03mm` keeps KiCad's 1.5 mm pads / 0.8 mm drills
and the derived positions; only pad 1's shape changes from `rect` to `circle`. The shared
`footprints.derive()` has no pad-shape override, so `tools/gen_footprints.py` wraps it
(`derive_with_pad_shapes`, reads the board-local spec key `pad_shapes={"1": "circle"}`; fails if a
named pad is not exactly one `rect` pad in the base, or a circle would get a non-square size; p2k
candidate 22). The footprint name is unchanged (the sheets were not re-run); the library file and
the 9 Q footprints in the board differ only in the pad-1 shape, the pin-1 dot (below) and the descr
("…, round pad 1, pin-1 dot"). Re-checked: `check_footprints`
163/163, worst residual 0.001 mm (position-only check, unchanged); `check_pin_order` OK unchanged
(it fits the unmoved KiCad base; TO-92 has no `POLARITY` entry: the body marker decides, as
recorded in "Pin order"); measured on the rebuilt board (pcbnew, pad circle vs track centre line):
**Q4 0.433 mm, Q6 0.433 mm** (= the "round 1.5 pad" column above).

**Pin 1 marking without the square pad**: KiCad's TO-92 silk (F.SilkS) and fab (F.Fab) outline is
the body with the flat side as a straight line on the +y side and the round back as arcs, but it is
**left-right symmetric** about the middle pad: it shows which way the flat side faces, not which end
is pin 1 (only the JEDEC convention "flat side towards you, leads 1-2-3 left to right" does). KiCad's
square pad was the only explicit pin-1 mark. So, as on the PI / FX loop board (coordinating session,
for consistency between the 2010 boards; `~/dev/tube_pi_fxloop_kicad` `PIN1_DOT`, read only),
`gen_footprints.py` adds a **filled dot, radius 0.2 mm, on F.SilkS (stroke 0.12) and F.Fab (0.1) at
(-0.45, 1.35)** in the footprint frame (spec key `pin1_dot`, value `PIN1_DOT`): left of pad 1 on the
flat side, about 0.6 mm from the pad-1 copper (centre 1.655 mm from the pad centre), inside the
courtyard (x ≥ -1.01). The generated dot is byte-identical to the PI / FX one (same derived
footprint, pad 1 at (0.508, 0)). Nothing on this board argues against it: the DRC counts are
unchanged (silk_over_copper 74, silk_overlap 31; no DRC item names a Q dot), and Phase 2 checked
that the KiCad flat side lies on the Proteus flat side on all nine J112s, so the dot sits at the
drain (pad 1) on every part. Proteus' TO92 had round pads for all three pins.

### Remaining DRC items (`DRC_ACCEPTED`)

| Type | Count | Why it stays |
|---|---|---|
| shorting_items / unconnected / schematic parity | 0 / 0 / 0 | – |
| clearance (error) | 0 | (was 2 at the square TO-92 pad 1 of Q4 / Q6; pad 1 round since the user decision) |
| courtyards_overlap (error) | 54 | KiCad courtyards vs the Proteus placement (parts exactly at the Proteus positions): U1-U3 (courtyard = the Proteus Top Assembly rectangle 26.4 × 25.4) with their three mounting holes each (H103/H106/H109, H104/H107/H110, H105/H108/H111) and C4, R1, R5, C9, Q5, R18, R30, R33, H5; film caps / resistors closer than KiCad's courtyards (C1/R6, C8/R22, C16/C17, C20/C21, C20/R40/R42, C24/C25, R24/R25, R25/C13, R44/C15, R62/C28, C37/R67, C30/R48, R7/R15, R3/R11, R4/R5, R4/C4, R9/R10, R12/R5, R23/R49/R50, R29/R31, R36/C25, R43/C24/C25, R36/C16), Q7/Q8, Q8/Q9, terminals at film caps (HI1X/C19, HI2X/C23, HI3X/C27, LO1W/C16/C17, LO2W/C17, LO3O/C16, EQOUT/C29). Accepted. |
| pth_inside_courtyard (error) | 16 | same placement: H103-H105 inside the U1-U3 body rectangle; R1, C4 (U1), R18, C9, R30 (U2); R50 ×2 (R23), R67 (C37), R36 (C16), R40 (C20), R43 (C24), R4 (C4), R44 (C15). Accepted. |
| silk_over_copper / silk_overlap (warning) | 74 / 31 | KiCad footprint silk and reference positions on the Proteus placement (Phase 5). |
| track_dangling (warning) | 1 | a 0.0635 mm Proteus track stub on B.Cu at (88.9, 0.762) → (88.9, 0.6985), Net-(RLY4B-COM1), inside the 0.508 mm track bend (finding 16). Harmless; reproduces the Proteus copper. |

### Negative tests (restored; the board is byte-identical afterwards, sha1 3e0c122c…)

Each change made in the board file (scratch script `build/tmp/negtest.sh`, not committed), then
`make_pcb.sh --check`, `check_board`, `assign_nets --check`, `p2k drc`:

| Change | make_pcb --check | check_board | assign_nets --check | p2k drc |
|---|---|---|---|---|
| a via (H4, (-91.821, 9.271) IPC) deleted (first session) | not up to date (exit 1) | **IPC via … H4: no board via** | **open H4: 2 groups** | – |
| track moved 1 mm (F.Cu (83.185, 3.175) → (73.66, 3.175), Net-(U3B-A2), y + 1) | **not up to date** | OK (no track geometry check) | **open Net-(U3B-A2): [R51-1] [U3-6]** | **1 unconnected** (FAILED) |
| a segment's net changed in the file (F.Cu (71.12, 0.635) → (71.12, -8.18): Net-(U3B-A2) → PRE-GND) | **not up to date** | OK | OK | OK |
| a pad net changed (R51 pad 1: Net-(U3B-A2) → PRE-GND) | **not up to date** | **IPC net #00068 spans KiCad nets …, R51-1 / U3-6 wrong** | **IPC net #00068 spans KiCad nets** (exit 1) | **1 short, 1 unconnected, 1 parity, 1 solder_mask_bridge** |
| footprint moved 0.5 mm (Q4 x + 0.5) | **not up to date** | **Q4-1/2/3: 0.500 mm from the IPC pad** | OK (pads still touch their tracks) | **2 clearance** (0.079 mm) |

As on the pilot: **a segment's net edited in the file is caught only by the byte compare** of
`make_pcb.sh --check` (pcbnew re-derives the track nets from the connected pads on load, so
check_board, assign_nets and DRC all pass). Every change fails at least one `check_all.sh` step. (Run on the board before and after the pin-1
dot: same results.)

## Phase 4 – independent verification – done (Fable 5.2, fresh session, 2026-11-20)

A different reader than the sessions that built the board. Nothing in `kicad/`, `lib/` or the
generators changed: the board is still sha1 3e0c122c… and `make_pcb.sh --check` is byte-identical.
New: `tools/excellon_metric.py`, `reference/fab_2010_drill_metric.drl`, `tools/roundtrip.py`,
`DRILL_EXCELLON` in `p2k_config.py`, three steps in `tools/check_all.sh`, `reports/roundtrip/`.

### 1. `p2k ipc356_diff` (kicad-cli ipcd356 of the board vs the Proteus IPC file)

```
ipc356_diff: Proteus 366 records, KiCad 366; matched 366 (339 pads incl. 3 N/C, 14 vias, 13 holes), worst position offset 0.002 mm (limit 0.05)
ipc356_diff: 98 Proteus nets mapped 1:1 onto KiCad nets, 0 mismatches
ipc356_diff: KiCad drill larger (footprint kept): 129x 0.762->0.8, 6x 0.762->1.001, 14x 1.016->1.1, 22x 1.016->1.199, 14x 1.143->1.199
ipc356_diff: KiCad drill smaller, accepted (DRILL_SMALLER): 4x 0.762->0.749, 40x 1.143->0.701, 8x 1.143->1.001, 28x 1.143->1.1
ipc356_diff: pads with another size in KiCad (info): C 70, D 14, Q 27, R 114, RLY 40
ipc356_diff: OK
```

Every pad / via / hole within 0.05 mm (worst 0.002: kicad-cli writes 0.0001 inch), all THT, both
sides, nets 1:1 by pad sets, the 3 N/C pads (U1-U3 pin 9) on `unconnected-(…)` nets, the 13 holes
H101-H113 matched as plated board-only holes without a net (the `H\d+` pattern accepts them; the
terminals H4 / H5 are matched as pads on the nets H4 / H5). The smaller drills are exactly the four
recorded pairs: 4 (C4, C14), 40 (RLY1-RLY5), 8 (C1, C5, C7, C10), 28 (the 14 Orange Drops) = 80 holes.

### 2. `p2k gerber_roundtrip` (KiCad gerbers + drills vs the Proteus gerbers)

Run as `python3 tools/roundtrip.py --check` (below). Raster 0.025 mm, tolerance 0.05 mm.

| Layer | Proteus / KiCad copper (mm²) | XOR beyond 0.05 mm: only Proteus / only KiCad | Clusters ≥ 0.01 mm² | Draws / flashes off the other copper |
|---|---|---|---|---|
| F.Cu | 3951.6 / 3736.4 | 188.53 / 12.69 | 339, all `pad shape` | 0 Proteus (406 draws, 366 flashes), 0 KiCad (402 draws, 366 flashes) |
| B.Cu | 3586.7 / 3368.3 | 190.62 / 12.56 | 317, all `pad shape` | 0 / 0 |

No `other`, `clearance` or `zone fill` cluster (no pours on this board): every difference is a pad
whose KiCad size or shape differs from the Proteus flash (the Phase 2 table: relays 2.54 → 1.4,
film caps, resistors, electrolytics; "only KiCad" = the larger 2 W resistor / CAP20 pads and the
rounded-rectangle marked pads of the diodes and the D16 electrolytics; the per-footprint sums are in
`roundtrip.txt`). The 4 extra Proteus draws per layer are the profile draws in the
copper files. Overlays `reports/roundtrip/F_Cu.png`, `B_Cu.png` and the report `roundtrip.txt` are
committed (as the pilot); two runs give byte-identical files.

Drills: Proteus 366 = KiCad 366, all matched within 0.05 mm, 0 mismatches; diameters as in the
ipc356_diff lines above (14 vias 0.508 = 0.508, 47 terminals 1.524, 27 noval 1.7272 → 1.727, 13
holes 3.0; larger and the four accepted smaller pairs).

**2010 Excellon cross-check** (`DRILL_EXCELLON = reference/fab_2010_drill_metric.drl`):

- `tools/excellon_metric.py` (copy of the pilot's, source file name changed) converts
  `source/fab_2010/etunen - CADCAM Drill.TXT` (M48 / INCH, 7 tools, 364 hits) to metric 4.3;
  `--check` is a `check_all.sh` step. The shared reader is metric-only (p2k candidate 23).
- The shared tool alone reports **exactly 2 mismatches**, the two vias added in October 2010:
  `excellon: drill gerber ViaDrill 0.508 mm at (-29.337, -42.545) not in the Excellon file` (via on
  **PRE-GND**) and `… at (33.02, -31.115) …` (via on **J4**); 364 of 364 Excellon holes match a
  drill gerber flash within 0.05 mm (12 × 0.508, 139 × 0.762, 36 × 1.016, 90 × 1.143, 47 × 1.524,
  27 × 1.7272, 13 × 2.9997 = 3.0).
- `tools/roundtrip.py` (board-local wrapper, p2k candidate 3) calls the shared
  `compare_excellon()` unchanged and takes out exactly those two errors, matched by position
  (0.01 mm), diameter 0.508 and function `ViaDrill` (`EXPECTED_NOT_IN_EXCELLON`); it adds an error
  if one of them is *not* reported missing, and leaves every other error in place. The report
  lists them as "expected, not an error". This agrees with the Phase 0 comparison of the June and
  October copper (October = June + 2 vias + the tracks at them).

### 3. Independent reading of the PDF against the IPC (all 5 sheets)

Phase 1 took the nets from the IPC and the PDF only for the layout. Here every connection of the
PDF was read from the drawing first (pages rendered at 400 dpi, in quadrants; wires, junction dots,
crossings without a dot, labels, terminal names, tube pin numbers, capacitor / diode polarity, the
resting contact of each relay blade, the gate side of each J112), written down as nets, and then
compared with `reference/pins_by_net.md`. KiCad equals the IPC by `compare` (0 wrong-net pins), and
the relay / diode block of the KiCad sheet 3 render was looked at next to the PDF (blades resting
on pins 7 / 3, diode cathodes on the coil pin-5 nodes).

**Result: no disagreement between the PDF and the IPC on any sheet.** Read and compared:

| Sheet | Nets read from the PDF (all of the sheet's parts) | Dense places checked |
|---|---|---|
| 1 Input stage (36 parts) | #00000, #00001, #00005-#00009, #00011, #00014, #00017-#00021, #00024-#00031, #00035, A, B, J1, J2, PRE1, SW1, SW2, H4, H5, PRE-GND | RLY1 / RLY2 both poles (COM, resting and other contact of each), the two coil + diode blocks, the R47 return under U1 (crosses the C5, pin-8, pin-7 and J2 wires without a dot), R13-R14-R15 / C5, Q1 (D at R3), Q2 (S at C4 / R12) |
| 2 Second stage (33) | #00037, #00041-#00044, #00046, #00047, #00049, #00050, #00053-#00057, #00062, #00064, C, D, EQ, PRE1, PRE2, J1, J4 (`j4`), SW1, H4, H5, PRE-GND | RLY3 (the two other contacts joined, nothing else on them; the R16 wire crosses that link without a dot), the C7 / C11 / C13 / R24-R26 / C12 network, the C11-C13 node down to R31 (crosses the C13 and pin-7 wires), R50's jogged return, Q3-Q6 (S at the top), POT-GND |
| 3 EQ stage (34) | #00068, #00073-#00076, #00079, #00081, #00082, #00084-#00086, #00090, #00092, #00095-#00098, #00102, E, F, EQ, EQ1-EQ3, J2-J4, SW2, SW3, H4, H5, PRE-GND | RLY4 / RLY5 both poles and the chain between them (#00084, #00085), D4 / D5 (cathodes on the RLY4 coil node, anodes on sw3 / sw2), D8, D9, the R34 / R51 / EQOUT / C29 column crossing four wires, U3 pin 1 on E, the H4 / H5 pads |
| 4 Tone stacks (39) | #00103-#00124 (3 × 6 nets), EQ1-EQ3, PRE-GND | each stack: C 250p + R 220k on EQn, LOnX / LOnW / LOnO, R 220K to HInW, R 4k7 and C 2N2 on the ground rail, C 2N2 to HInX |
| 5 Supply filter (21) | A-F, #00131, PRE-GND, J1-J4 on the pads A-D, SW1-SW3 | electrolytic pin 2 at the hollow (+) plate on the B+ node, pin 1 on PRE-GND |

All 98 IPC nets are covered. What the PDF **cannot** show, so this reading cannot check (it rests on
the Proteus pinouts of "Phase 1 preparation" and the footprint / pin-order checks of Phase 2):
the pin id of each end of a resistor or unpolarised capacitor (the PDF prints no pin numbers there;
only the net membership per part was compared), the relay pin numbers (not printed; read as "COM /
resting contact / other contact" per pole and compared with COM 2 / NC 3 / NO 1 and COM 6 / NC 7 /
NO 8 – consistent on all ten poles, and the footprint renumbering puts COM / NC / NO on the Omron
COM / NC / NO pads 13 / 11 / 9 and 4 / 6 / 8), the coil pin 4 / 5 assignment (read as "the end on
H4" / "the end on the switch net"), and the J112 pins 1 / 2 (read from the gate side of the
symbol: gate drawn next to the source; Q1, Q7-Q9 source on PRE-GND, Q2-Q6 source on the signal
node, as the table in "Phase 1 preparation").

One reading trap, not a disagreement (finding 19): on sheet 3 the `H4` net terminal of U3 pin 4
ends directly above the junction of the C15 / R45 / RLY4-COM2 wire (#00082), with the rotated
label text between the terminal circle and the junction dot. At 1200 dpi there is no wire between
them; the IPC agrees (#00082 = C15-2, R45-2, RLY4-6; H4 has none of them).

### 4. Review of the generators and spot checks (pcbnew, scratch script in build/tmp)

Read: `p2k_config.py`, `tools/gen_symbols.py`, `tools/gen_footprints.py` (specs), `tools/rename_holes.py`,
`tools/make_pcb.sh`, `tools/compare.py`, `tools/sheets/_common.py`, `tools/check_all.sh`.

| Spot check | Result |
|---|---|
| Mounting holes vs the terminals H4 / H5 | 13 footprints `MountingHole_3.0mm_PTH_Pad6.35mm` H101-H113, pad 6.35 / drill 3.0, no net, board-only; terminals `H4` (79.375, 24.13) on net H4 and `H5` (79.375, 20.32) on net H5, `FlyLead_Pad` 3.048 / 1.524; no duplicate reference; the `H*` references are H101-H113, H4, H5 and the nine HInX / W / O pads |
| N/C pin 9 | U1-9, U2-9, U3-9 on `unconnected-(UnC-HCT-Pad9)`; no track end or via within 2.5 mm of any of them; IPC `N/C` × 3; symbol pin `passive` + no-connect flag (rule kept) |
| Noval pin ids | IPC pads of U1-U3 on a 21.0 mm circle, pin k at −144° − 36°(k−1) (Y up, top view): clockwise seen from the top = mirrored against the noval standard (finding 13 confirmed); pads 1-9 on the IPC nets, offset 0.000 |
| Relay renumbering | footprint Omron 16 / 13 / 11 / 9 → 4 / 2 / 3 / 1 and 1 / 4 / 6 / 8 → 5 / 6 / 7 / 8: G5V-2 coil 1 / 16, COM 4 / 13, NC 6 / 11, NO 8 / 9, so Proteus COM / NC / NO sit on Omron COM / NC / NO pads on both poles; RLY1 pads 1-8 on the IPC nets (finding 14 confirmed: the symbol mapping is the mirror image, electrically the same) |
| Electrolytic polarity | C28: marked pad = `2` on net A (B+), pad 1 PRE-GND; C2 / C30: marked pad `+` on the cathode-bypass / bias node, `-` on PRE-GND; PDF: hollow plate (+) at pin 2 / `+` |
| Diode polarity | D1, D8: marked pad `K` on SW1 / #00081, `A` on H4; D4: `A` on SW3, `K` on #00081 – as the PDF (cathodes towards the coil's switch end) |
| TO-92 pin 1 | Q1-Q9 all three pads round 1.5 / 0.8; Q1 pad 1 on the drain net (R3), Q4 pad 1 on PRE-GND; DRC 0 clearance errors |
| Finding 16 stub | present: B.Cu (88.9, 0.762) → (88.9, 0.6985) (KiCad frame), 0.0635 mm long, width 0.508, Net-(RLY4B-COM1); the round trip covers it both ways |
| Single-pin nets | none in the IPC (smallest net 2 pins) besides the 3 N/C pads; 98 IPC nets ↔ 98 KiCad nets 1:1 by pads (own script) |
| Vias | 14, all 1.27 / 0.508, on PRE-GND 2, H4 2, EQ 1, #00081 2, J1 1, J2 5, J4 1 = the IPC |

**Earlier findings: all confirmed, none refuted.** 1 (Q4 `NADA` in the PDF, J112 / TO92 in
ROOT.LYT), 2 (`j4` at Q6, `J4` at Q9 and pad D), 3, 4 (D1, D2, D3, D8, D9 anode on H4; D4 / D5
anodes on sw3 / sw2, cathodes on #00081), 5 (CERAMIC56P / 250p), 6 (Mechanical 1 `NonPlated,1,2,NPTH`,
`FSLAX45Y45` vs READ-ME "4.3"), 7 (ROOT.LYT read again: R13 10M, R22 100k/2W, R27 22k, R30 1k8,
R34 100k, R51 22k, Q4 J112; the PDF has the schematic values 0R, 220k/2W, 120k, 2k2, 22k, 100k –
note that **R34 and R51 are exactly swapped** between schematic (22k / 100k) and layout (100k /
22k)), 8, 9, 10, 11, 12 (PDF), 13, 14 (above), 15 (C2 P2.54, C30 P2.50), 16 (above), 17 (three
holes 16.3-18.0 mm from each socket centre), 18 (DRC clean with the round pad).

New, small (added to "Findings" as 19-21): the H4 label trap of sheet 3, eight more very short
Proteus track draws besides the stub of finding 16 (two of them of zero length), and the R34 / R51
swap noted under finding 7.

### 5. Negative tests of the new checks (all restored)

Board changes on a scratch copy (`P2K_PCB` / `P2K_REPORTS` in build/tmp/neg4, scratch script
`build/tmp/neg4.py`, not committed); Excellon / config changes in place with a restore
(`build/tmp/neg4b.sh`). Afterwards `git status` shows only this session's files, the board is sha1
3e0c122c… and `reports/roundtrip/*` are byte-identical (sha1 62625ba8… / acfeab39… / 8dce1b5c…).

| Change | ipc356_diff | roundtrip.py --check |
|---|---|---|
| none (scratch copy) | OK | OK |
| track moved 1 mm (B.Cu (-80.772, 12.7) → (-71.58, 12.7), y + 1) | OK (pads only) | **FAILED**: 2 `other` clusters (5.29 / 4.76 mm²), 2 uncovered draws |
| that track's width 0.508 → 0.25 | OK | **FAILED**: 2 `other` clusters (only Proteus 0.88 / 0.66 mm²) |
| pad net R51-1 → PRE-GND | **FAILED**: #00068 spans 2 KiCad nets, PRE-GND spans 2 Proteus nets | OK (no geometry change) |
| footprint R51 shifted 0.1 mm | **FAILED**: R51-1 / -2 nearest record 0.099 mm away | **FAILED**: 4 drill mismatches |
| via J1 (12.7, -24.765) removed | **FAILED**: Proteus via has no KiCad record | **FAILED**: 2 `other` clusters + 1 drill |
| terminal H5 drill 1.524 → 1.4 | **FAILED**: drill … is smaller | **FAILED**: … is smaller |
| a segment's net edited in the file | OK | OK – as in Phase 3 and on the pilot, caught only by the byte compare of `make_pcb.sh --check` |
| one hole deleted from the converted Excellon | – (`excellon_metric --check` **not up to date**) | **FAILED**: `ComponentDrill 0.762 at (-143.002, -3.175) not in the Excellon file` |
| October via (33.02, -31.115) added to the Excellon | – (**not up to date**) | **FAILED**: "the October via … was expected to be missing …" |
| Excellon tool T04 0.762 → 0.8 | – (**not up to date**) | **FAILED**: 139 drill mismatches |
| `DRILL_SMALLER` entry (1.143, 0.7) removed | **FAILED**: 40 × RLY drill is smaller | **FAILED**: 40 drill mismatches |
| wrapper list position 33.02 → 34.02 (scratch copy of the wrapper) | – | **FAILED**: the real via reported + "expected to be missing" |

Every change fails at least one `check_all.sh` step.

## Phase 5 – clean-up – done (Opus 5.5, clean context, 2026-11-20)

Verified state first: `tools/check_all.sh` printed exactly the Phase 4 "Last check output" (ALL CHECKS
PASSED, compared line by line).

### User decisions (2026-11-20, answered through the coordinating session before this session)

1. Noval sockets U1-U3 to the **bottom side with the standard noval numbering** (already decided after
   Phase 2): build the footprint mirrored as the power amp pilot did (a plain pcbnew Flip mirrors the
   pads and fails the checks).
2. Reference texts placed automatically (`p2k place_refdes` in `tools/make_pcb.sh`, as the pilot).
3. The short / dangling Proteus track pieces (findings 16 and 20) are **kept as drawn**; no
   `REMOVED_TRACKS`.
4. The TO-92 pin-1 dot is kept.
5. Body graphics (KiCad library graphics), KiCad pad sizes, sheet names and the 1.6 mm thickness are kept.
6. The board **stays generated**; stopping generation is the user's call at the first hand edit.

Still open (report only): the values of R13, R22, R27, R30, R34, R51 and Q4, including the R34 / R51
swap (findings 1, 7, 11, 21).

### Noval sockets on the bottom side (decision 1)

- `tools/gen_footprints.py`: the spec `Valve_Noval_Belton_PCD21.00mm` gets the board-local key
  `bottom=True`; a wrapper around `footprints.build_library` (the pilot's code) marks the IPC pads of
  the spec's `ipc` part (U1) as bottom side, so the shared `from_ipc` builds the footprint **mirrored**
  (the shared tool mirrors only bottom SMD parts: THT pads are `both` in the IPC file; p2k candidate 25).
  Footprint name, pad numbers (= the IPC / standard pin ids 1-9), pad sizes, drills unchanged; the pad
  and graphics x coordinates are mirrored (the body rectangle is symmetric up to 0.001 mm). In the
  footprint's own view the pads now run in the **standard noval direction** (as KiCad's
  `Valve:Valve_Noval_P`). The descr and the footprint-map note say "standard noval numbering, mounted
  on the solder side". The symbols are unchanged (pins 1-9 = Proteus / standard ids; pin 9 passive +
  no-connect flag); the sheets did not need a re-run (same footprint name).
- `p2k.check_footprints` then finds that the pattern fits **only mirrored** and writes U1-U3 as
  `bottom` (orientation 180) into `reports/footprint_fit.csv`; `build_pcb` flips them: footprint layer
  B.Cu, silk / Fab / courtyard on B.SilkS / B.Fab / B.CrtYd, the reference on B.SilkS. **No 3D model**
  (the IPC-built footprint never had one).
- Copper unchanged: check_footprints worst 0.001 mm, check_board, assign_nets, `ipc356_diff`
  366/366 and `tools/roundtrip.py` print exactly the Phase 4 output; `place_refdes` 119 kept / 57
  moved as before.
- `tools/check_pin_order.py` keeps the Phase 2 facts (the unmoved KiCad `Valve_Noval_P` and the ideal
  standard noval fit the Proteus ids only mirrored) and adds `bottom_side_noval()` (as the pilot's
  `bottom_side_octal()`): (a) the project footprint vs an ideal standard noval in the footprint frame:
  unmirrored **0.007**, mirrored 19.319 → standard numbering; (b) the project footprint vs the IPC pads
  of U1-U3: unmirrored 19.315, mirrored **0.001** → bottom side; (c) `reports/footprint_fit.csv`:
  bottom = exactly U1-U3; (d) the board (`pcb.board_file()`, `P2K_PCB` overrides): U1-U3 on B.Cu, the
  other 173 footprints on F.Cu.

### References (decision 2)

Already a step of `tools/make_pcb.sh` since Phase 3 (`p2k.place_refdes`, defaults): 119 kept, 57 moved,
unchanged by the socket move (the U1-U3 references are now on B.SilkS). No DRC silk warning involves a
reference text.

### DRC before / after (accepted error types in `p2k_config.py` `DRC_ACCEPTED`, texts updated)

| Type | Phase 4 | Phase 5 |
|---|---|---|
| shorts / unconnected / parity / clearance | 0 | 0 |
| courtyards_overlap (error, accepted) | 54 | **36**: the 18 pairs of the socket courtyards (U1-U3 with their 9 mounting holes and with C4, R1, R5, C9, Q5, R18, R30, R33, H5) are gone; left: film caps / resistors closer than the KiCad courtyards, Q7/Q8/Q9, terminals at film caps (list in "Phase 3") |
| pth_inside_courtyard (error, accepted) | 16 | **16**: unchanged; H103-H105 and R1, C4 (U1), R18, C9, R30 (U2) now in the B-side socket courtyard (a THT pad is on both sides, as the pilot's VB pads) |
| silk_over_copper (warning) | 74 | **74**: 16 of them the socket body rectangle on B.SilkS over the THT pads of the mounting holes (finding 17) and R1, C4, R18, C9, R30, R33, H5; the rest library silk over pads |
| silk_overlap (warning) | 31 | **21** |
| track_dangling (warning) | 1 | **1** (finding 16 stub, kept: decision 3) |
| total | 176 | **148** |

`p2k drc` fails only on errors; warning counts are not enforced (a board change is caught by the
`make_pcb.sh --check` byte compare).

### Hardened checks ported from the PI / FX loop board (`~/dev/tube_pi_fxloop_kicad`, read only)

- **`tools/check_drill_smaller.py`** (new step in `check_all.sh`, "Smaller KiCad drills are exactly the
  80 decided holes"): `ipc356_diff` and `gerber_roundtrip` accept a smaller KiCad drill by the
  **diameter pair** in `DRILL_SMALLER` only, so any other pad with the same pair would pass silently
  (p2k candidate 26). The check reads the IPC file with its own parser, finds the board hole at every
  record (0.05 mm) and requires the smaller drills to be exactly RLY1-RLY5 pads 1-8 (40 × 1.143 → 0.7),
  C1/C5/C7/C10 (8 × 1.143 → 1.0), the 14 Orange Drops (28 × 1.143 → 1.1) and C4/C14 (4 × 0.762 →
  0.75), and the `DRILL_SMALLER` pairs to be exactly the decided ones. Same code as PI / FX, this
  board's `EXPECTED`.
- **Joined no-connect pins**: `p2k compare_netlists` treats each pin of a KiCad `unconnected-(...)` net
  as a singleton, so two N/C pins wired together pass. `tools/compare.py` now also requires exactly one
  pin per `unconnected-(...)` net (here pin 9 of U1-U3); `tools/erc.sh` now fails on the ERC warnings
  `no_connect_connected` and `footprint_link_issues` (and takes an optional schematic / report path for
  scratch tests). Both as on PI / FX (p2k candidate 27).

### Negative tests (scratch files in build/tmp/neg, not committed; all restored, `check_all.sh` afterwards ALL CHECKS PASSED)

| Change | Caught by |
|---|---|
| S1: scratch board, U2 flipped back to F (pcbnew `Flip`) | **check_pin_order** "wrong layer for ['U2']"; **check_board** U2 pads 6.5-21 mm off |
| S2: the Phase 4 board (sockets on top, Proteus ids) with U1-U3 pcbnew-`Flip`ped to B = the mirrored ids of a plain flip | check_pin_order passes (it checks the layer only), but **check_board** (U1-1 17.0 mm off, ...) and **ipc356_diff** ("KiCad pad U2-8 … no Proteus record") fail; the byte compare of make_pcb --check too |
| S3: `bottom=True` removed from the noval spec | **gen_footprints --check** out of date; after regenerating: check_footprints OK (fits unmirrored, top), **check_pin_order FAILED** (no standard numbering, not mirrored-only, footprint_fit.csv sides) and **make_pcb --check** not up to date |
| D1: scratch board, C3 drills 0.8 → 0.75 (pair (0.762, 0.75) is in `DRILL_SMALLER`) | **ipc356_diff OK** ("6x 0.762->0.749" accepted): the gap; **check_drill_smaller FAILED** "C3-1 / C3-2 … not a decided hole" |
| D2: scratch board, RLY1 pad 1 drill 0.7 → 1.143 | **check_drill_smaller** "RLY1-1: expected a board drill smaller …" |
| D3: pair `(0.762, 0.75)` removed from `DRILL_SMALLER` | **check_drill_smaller** "DRILL_SMALLER pairs … != the decided pairs" |
| N1: scratch schematic copy, U1 pin 9 and U2 pin 9 joined by a global label NCJOIN | **erc.sh** exit 1 ("2 no_connect_connected"; before Phase 5 only a counted warning); **tools/compare.py** "N/C mismatch … merges IPC nets" (a named net was already caught) |
| N2: exported netlist edited so U1-9 and U2-9 share `unconnected-(U1C-HCT-Pad9)` | base compare_netlists logic "compare: OK" (the gap; the shared CLI itself crashes on candidate 9), **tools/compare.py** "joins 2 pins: U1-9 U2-9 … FAILED" (exit 1) |

### Left open / when the board stops being generated

**Done 2026-11-20: generation stopped (user decision), section "Generation stopped 2026-11-20".**

- The values of R13, R22, R27, R30, R34, R51 and Q4 (incl. the R34 / R51 swap, finding 21): open, report
  only; the schematic values are used until the user checks the built board.
- Per the playbook (section 3, Phase 5) and decision 6: the board stops being generated at the **first
  manual layout change in KiCad – the user's call**. Until then `tools/make_pcb.sh` is the only way to
  change the board. At the first hand edit: remove the `make_pcb.sh --check` step from
  `tools/check_all.sh` and say so here; check_board / assign_nets / DRC / ipc356_diff / gerber_roundtrip
  / check_drill_smaller keep working on the edited board and show the intended differences (record them
  as deviations).
- Silk / courtyard warnings above (library graphics and the Proteus socket body on the Proteus
  placement), kept by decision 5.

## Design fixes 2026-11-20 (Opus 5.5)

Verified state first: `tools/check_all.sh` printed ALL CHECKS PASSED (the Phase 5 "Last check output").
The user decisions are under "Decisions" (**User decisions 2026-11-20, design fixes**). Aim: a clean
starting point for the redesign; the component values stay as they are. Everything is done in the
generators and the board is regenerated (`tools/make_pcb.sh`), nothing by hand.

### Finding 14: G5V-2 symbol with Omron's terminal names (no copper change)

- `tools/gen_symbols.py` `g5v2()`: the symbol now uses the **same physical mapping as the footprint**
  (`tools/gen_footprints.py`, Proteus 4 / 2 / 3 / 1 on Omron 16 / 13 / 11 / 9 and 5 / 6 / 7 / 8 on
  Omron 1 / 4 / 6 / 8) instead of the Phase 1 mirror image. Pin **numbers stay the Proteus / IPC ids**
  (every check compares against the IPC; the footprint pads are the same ids); pin **names** are
  Omron's terminal names, hidden as before:

  | Proteus id (pin number) | 4 | 5 | 2 | 3 | 1 | 6 | 7 | 8 |
  |---|---|---|---|---|---|---|---|---|
  | Proteus name (before) | DC1 | DC2 | COM1 | NC1 | AC1 | COM2 | NC2 | AC2 |
  | Omron name (now) | COIL16 | COIL1 | COM13 | NC11 | NO9 | COM4 | NC6 | NO8 |
  | unit | A | A | B | B | B | C | C | C |

  KiCad's `G5V-2_Split` units 2 (4 / 6 / 8) and 3 (13 / 11 / 9) are swapped so that unit B stays the
  Proteus pole 1 (now Omron 13 / 11 / 9) and unit C the Proteus pole 2 (Omron 4 / 6 / 8); the poles are
  drawn identically, so the sheets' pole wiring is unchanged. KiCad's coil has terminal 1 at the top: the
  sheets now place the coil **unrotated** (was rotation 180), so Proteus 5 (Omron 1) is still at the top
  and the coil / diode wiring is at the same positions (`tools/sheets/sheet01-03.py`, `_common.relay()`
  docstring). Sheets 4 and 5 unchanged.
- KiCad's automatic net names follow the pin names: `Net-(RLY4B-COM1)` is now `Net-(RLY4B-COM13)`,
  `Net-(RLY3B-NC1)` → `Net-(RLY3B-NC11)` etc. (the findings below keep the old names where they were
  written). No check depends on these names (all compare by pad sets).
- `tools/check_pin_order.py`: the "symbol map" row now reads the Omron terminal numbers from the pin
  names of `lib/tube_preamp.kicad_sym` (`relay_symbol_map()`) and expects them to fit the IPC pads
  **unmirrored** (0.000 mm; Phase 1 mapping: only mirrored). A wrong name now fails there.
- Electrically identical: compare 339 pins / 0 wrong-net, ERC 0 / 0, check_board, ipc356_diff, DRC
  parity unchanged; the footprints and `reports/footprint_fit.csv` are unchanged.

### Findings 16 and 20: Proteus track pieces removed (`REMOVED_TRACKS`)

Reverses Phase 5 decision 3. `p2k_config.py` `REMOVED_TRACKS` lists the 9 Conductor draws (IPC frame,
exactly as drawn); `gerber_to_tracks` does not build them, `gerber_roundtrip` drops them from the
Proteus side:

| Layer | Draw (IPC frame, Y up) | Length | Net | Finding |
|---|---|---|---|---|
| B.Cu | (88.9, -0.762) → (88.9, -0.6985) | 0.0635 | RLY4 COM13 (was `Net-(RLY4B-COM1)`) | 16 (the DRC `track_dangling`) |
| F.Cu | (-61.087, -1.905), zero length | 0 | RLY3 NC11 | 20 |
| F.Cu | (-61.722, -22.225), zero length | 0 | H4 | 20 |
| F.Cu | (-139.7635, -16.5735) → (-139.7635, -16.4465) | 0.127 | PRE-GND | 20 |
| F.Cu | (-130.81, -38.735) → (-130.8735, -38.7985) | 0.090 | PRE-GND | 20 |
| F.Cu | (-60.96, -1.905) → (-61.087, -1.905) | 0.127 | RLY3 NC11 | 20 |
| B.Cu | (-18.87074, 24.13) → (-19.05, 24.13) | 0.179 | H5 | 20 |
| B.Cu | (-114.427, -18.415) → (-114.3, -18.415) | 0.127 | H4 | 20 |
| B.Cu | (-43.942, -6.858) → (-43.942, -6.985) | 0.127 | PRE-GND | 20 |

(The coordinates of finding 20 were written as "KiCad frame" but are the IPC / Gerber frame, as here;
the next short draw, 0.278 mm B.Cu at (-170.942, -30.988), was not in finding 20 and is kept.)

- Board: 738 tracks (was 747), 14 vias; assign_nets 114 groups, 0 shorts / orphans / opens (no
  connection depended on a piece); check_board, ipc356_diff OK; DRC 147 violations (was 148): the
  `track_dangling` warning is gone, 0 shorts / unconnected / parity; round trip OK (coverage 0 / 0, F.Cu
  401 Proteus draws compared + 5 removed, B.Cu 345 + 4).
- New board-local check **`tools/check_removed_tracks.py`** (step in `check_all.sh`): `REMOVED_TRACKS`
  is exactly the 9 decided pieces (own list, not read from the config), each is one Proteus Conductor
  draw, and no board track lies on those endpoints. `gerber_to_tracks` already fails on an entry without
  a draw, but `gerber_roundtrip` does not (p2k candidate 29), and only the `make_pcb.sh --check` byte
  compare would notice a dropped entry - which goes when generation stops.

### `tools/make_pcb.sh --check` stopped at no failing step (fixed)

`run >log || { ... }` disables `set -e` inside `run`, so in `--check` mode a failing step (found here:
gerber_to_tracks' REMOVED_TRACKS error) was passed over, the next steps ran on the unsaved board, and the
ERROR line was filtered from the printed summary; the check still failed, but only as "not up to date".
Each step now ends with `|| return 1`, and `--check` prints the log and "make_pcb: FAILED". The same
pattern is probably in the other boards' copies of the pilot script (not checked from here).

### Negative tests (scratch, all restored; the generators re-run byte-identical, `check_all.sh` afterwards ALL CHECKS PASSED)

| Change | Caught by |
|---|---|
| T1: the zero-length H4 entry removed from `REMOVED_TRACKS` | **make_pcb --check** (board and assign_nets.txt not up to date: the piece is built again), **check_removed_tracks** "missing [('F.Cu', -61.722, -22.225, …)]"; `tools/roundtrip.py` passes (the piece lies on its own copper: the gap the new check closes) |
| T2: a non-existent track `("F.Cu", 1.0, 2.0, 3.0, 4.0)` added to `REMOVED_TRACKS` | **gerber_to_tracks** "REMOVED_TRACKS: 10 listed, found 9 draws (missing …)" → **make_pcb --check FAILED** (after the fix above), **check_removed_tracks** "extra […]"; `tools/roundtrip.py` passes (p2k candidate 29) |
| T3: the old board (pieces built) given to check_removed_tracks | **check_removed_tracks** 9 × "is the removed piece" |
| R1: relay pins 2 and 3 swapped in `g5v2()` (Proteus COM1 / NC1 drawn on each other's position), library and sheets regenerated | **compare.py** "Net-(RLY1B-NC11) merges IPC nets [#00014 …] [#00026 …]" (exit 1); scratch board from it: **assign_nets**, **check_board** and **ipc356_diff** "spans IPC nets ['#00014', '#00026']"; gen_symbols / make_pcb --check out of date |
| R2: relay pin names COM13 / NC11 swapped (numbers and positions right) | **check_pin_order** "(symbol map): best fit unmirrored 5.080 mm, expected <= 0.01"; **gen_symbols --check** out of date |

ERC stays 0 / 0 in R1 (a passive pin on the wrong wire is not an ERC matter): the netlist comparison is
what catches it.

### Unchanged by decision

- Component values (R13, R22, R27, R30, R34, R51, Q4 `NADA`, the R34 / R51 swap of finding 21, the 250p
  CERAMIC56P of finding 5): as they are.
- Finding 4 (flyback diodes, anode on H4): no change unless the real board shows otherwise.
- The board stays generated until after the shared-tool migration; then generation stops (see
  next_prompt.md).

## Shared-tool migration 2026-11-20 (Opus 5.5)

The coordinated migration to the shared proteus2kicad tools (the per-board prompt in
`tools/p2k/docs/CANDIDATES.md` section 7.2; decisions in that file's "Decisions": D-R, D-Z, R1, "PR
relays"). Every commit is proven from a clean clone with `~/dev/proteus2kicad/tools/regress.sh a9a286c
tube_preamp_kicad` (clone, regenerate every generated file, `check_all.sh`, clean `git status`).

Commits (each pushed; regression `regress.sh a9a286c tube_preamp_kicad` per commit):

| Step | Commit | Regression |
|---|---|---|
| 1 bump + D-R + temporary `hole_refdes` exception | 3288dc6 | PASS (80 s) |
| 2 migration (board-local tools → shared keys) | 14039d4 | PASS (94 s) |
| 3 relay design change | ca0e910 | PASS (75 s) |
| record (this table, STATUS / README / next_prompt only) | the commit after ca0e910 | PASS |

### Step 1: p2k bump, D-R re-baseline, temporary strict exception

- `tools/p2k` c5682dd → **a9a286c** (proteus2kicad main; all code is in 2fb1563 = batch Z, a9a286c adds
  docs only).
- **D-R re-baseline** (batch R report texts): `p2k ipc356` changes exactly 1 line of
  `reference/pin_nets_by_component.md` (`Net aliases: .` → `Net aliases: none.`); `.csv` / `.json`
  unchanged. Committed with the bump.
- **D-Z strict defaults:** every id of `board.STRICT_DEFAULT` is now on. `hole_refdes` fails (the mounting
  holes are built as H1-H13 and renamed by `tools/rename_holes.py`; the schematic has the heater terminals
  H4 / H5), so step 1 adds the temporary `STRICT_CHECKS_OFF = {"hole_refdes": "H4 / H5 until the
  HOLE_START = 101 migration"}`; step 2 removes it. The other strict checks pass (`nc_joined`,
  `net_names`, `track_nets`, `roundtrip_counts`, `derive_max_move`, `no_connect_pin_type`); they print to
  stdout only, so no generated file changes.
- Every other generated file is byte-identical; `check_all.sh` ALL CHECKS PASSED (the new lines in the
  output: the strict-check lines, the footprint fit lines of `footprints.run`, the `build_pcb` hole-refdes
  warning, compare's net count wording).

### Step 2: migration to the shared tools (board-local tools → p2k keys)

Every generated file is byte-identical (`lib/`, `kicad/` incl. the board file and `fp-lib-table`,
`reference/`, the committed reports and overlay PNGs) except the accepted R1 re-baseline: the one line
`== excellon (fab_2010_drill_metric.drl): …` → `== excellon (etunen - CADCAM Drill.TXT): …` of
`reports/roundtrip/roundtrip.txt` (the Excellon file name; same 364 holes, 2 expected mismatches).

| Board-local (deleted or reduced) | Shared (p2k a9a286c) | Config / board script |
|---|---|---|
| `tools/make_part_map.py` readers, `SINGLE_LETTER_PARTS`, `LATIN1_PARTS` | `part_map.run(SPEC)` | SPEC in `tools/make_part_map.py` (`LATIN1 = True`, `SYMBOL_BY_DEVICE`, `PAGE_OVERRIDES`, `FIELDS` with `off_board`, `COMMENT` = the old first line, unchanged) |
| `gen_symbols.py` `pin_types()`, `swap_units()`, `hide_pin_names()` | `symgen.from_std(pin_types=, units=, hide_pin_names=True)` | `ecc83()`, `g5v2()` |
| sheets `_common.py` `place_mirrored()`, `term()` body, `hcap()` body; sheets 1-3 `gnd(p)` | `place(..., 0, mirror="y")`, `sheetkit.terminal(..., justify="away")`, `place(text_gap=3.81)` (through `horiz2`), `sheetkit.rail(sh, p, y=P(0, GND)[1])` | `term()` / `hcap()` stay as one-line calls |
| `tools/compare.py` | `p2k compare_netlists` (strict `nc_joined`, `net_names` on by default) | – |
| `tools/erc.sh` | `p2k erc` | `ERC_FATAL_WARNINGS = {"no_connect_connected", "footprint_link_issues"}` |
| `gen_footprints.py` `fp_lib_table()`, `build_library` (`bottom`), `derive_with_pad_shapes` (`pad_shapes`, `pin1_dot`), `noval_body()` | `footprints.run` | `FP_LIB_TABLE = True`; spec keys `bottom=True`, `pads={"1": dict(shape="circle", expect_shape="rect")}`, `pin1_dot`, `body_from=dict(centre=(-156.1, 6.168), min_len=20, radius=19, expect=4)` |
| `tools/check_pin_order.py` | `kipy -m p2k.check_pin_order` | `PIN_ORDER` (11 entries: 5 `spec=` groups, `polarity` K / + / + / 2, the relay footprint and the relay symbol map `symbol_renumber=`, Valve_Noval_P, ideal noval on the IPC, noval footprint vs ideal, noval footprint on the IPC with `other=0.02`), `PIN_ORDER_BOTTOM = {"U1", "U2", "U3"}`, `PIN_ORDER_MAX_MOVE` = the former `MOVE_LIMIT` |
| `tools/rename_holes.py` and its make_pcb step | `build_pcb` | `HOLE_START = 101`; the temporary `hole_refdes` exception removed |
| `tools/roundtrip.py` | `p2k gerber_roundtrip --check` | `EXCELLON_MISSING` (the 2 October vias), `EXCELLON_MISSING_LABELS = dict(file="2010 Excellon file", items="expected October vias", source="tools/roundtrip.py")` (report lines word for word) |
| `tools/check_drill_smaller.py` | `ipc356_diff`, `gerber_roundtrip` | `DRILL_SMALLER` `(reason, pads)`: RLY1-RLY5; C1 / C5 / C7 / C10; the 14 Orange Drops; C4 / C14 |
| `tools/excellon_metric.py`, `reference/fab_2010_drill_metric.drl` (R1) | `gerber_roundtrip` reads inch | `DRILL_EXCELLON = "source/fab_2010/etunen - CADCAM Drill.TXT"` |
| `tools/make_pcb.sh` (template) | `p2k make_pcb [--check]` | default `PCB_STEPS`; `tools/make_pcb.sh` = `exec tools/p2k/bin/p2k make_pcb "$@"` |
| `tools/measure_gaps.py` | `kipy -m p2k.measure_gaps` | – |

Kept: `tools/check_removed_tracks.py` (a board decision guard: the removed Proteus pieces are exactly
the 9 decided ones; not a p2k workaround). **Strict opt-outs: none** (`STRICT_CHECKS_OFF` absent; the
default set, incl. `hole_refdes`, passes). The p2k candidates are marked in "p2k candidates" below.
`check_all.sh` output: the same results; the pin-order table is printed in the shared layout (every
residual, angle, move and polarity equal), and the lines of the deleted steps (`rename_holes`,
`excellon_metric`, `check_drill_smaller`) and the `build_pcb` hole WARNING are gone.

Negative tests (scratch edits, all restored; the tree afterwards as committed):

| Test | Result |
|---|---|
| N1 relay footprint renumbering COM / NC swapped (`"13": "3", "11": "2"`) | check_pin_order FAILED: relay group unmirrored 5.080, `Relay_DPDT_Omron_G5V-2_ProteusPins` pads moved 5.080 mm (limit 0.001) |
| N2 C2 renumbering + / - swapped | FAILED: "the marked base pad 1 is pin '-', expected '+'", pads moved 2.520 mm (limit 0.03) |
| N3 Valve_Noval_P entry expected unmirrored | FAILED: "mirrored 2.972, expected unmirrored <= 3.1" |
| N4 symbol pin names COM13 / NC11 swapped in the library | FAILED: symbol map unmirrored 5.080 |
| N5 `PIN_ORDER_BOTTOM` without U2 | FAILED: footprint_fit.csv and the board have U2 on the bottom |
| D1 C10 removed from its `DRILL_SMALLER` pad set | ipc356_diff FAILED: "C10-1 / C10-2: KiCad drill smaller, not in the entry's pad set" |
| E1 one October via removed from `EXCELLON_MISSING` | gerber_roundtrip FAILED: "ViaDrill 0.508 mm at (-29.337, -42.545) not in the Excellon file" |
| H1 `HOLE_START` removed | make_pcb FAILED at step build_pcb: "ERROR mounting hole refdes equal schematic refdes: H4 H5" (strict `hole_refdes`) |

### Step 3: relay design change (RLY1-RLY5 on Omron pin numbers; electrically identical)

Coordinating-session decision "PR relays" (`tools/p2k/docs/CANDIDATES.md` "Decisions"; user-approved),
as tube_pi_fxloop_kicad's SERIES_MIX:

- `p2k_config.py` `IPC_PIN_IDS = {f"RLY{i}": {"1": "9", "2": "13", "3": "11", "4": "16", "5": "1", "6": "4",
  "7": "6", "8": "8"} for i in range(1, 6)}`: the Proteus G5V-2(HI) pin ids → the Omron pin numbers (the
  inverse of the former footprint renumbering, so the physical mapping of finding 14 / Phase 2).
- Symbol: KiCad's stock `Relay:G5V-2` unchanged (`from_std("Relay", "G5V-2", "G5V-2", "RLY", "G5V-2(HI)")`;
  one unit: coil 1 / 16, pole COM 4 / NC 6 / NO 8, pole COM 13 / NC 11 / NO 9); the G5V-2_Split copy with
  Omron names on the Proteus ids (`g5v2()` of the design fixes) is gone.
- Footprint: stock `Relay_THT:Relay_DPDT_Omron_G5V-2` (rule in `tools/gen_footprints.py`); the project
  footprint `Relay_DPDT_Omron_G5V-2_ProteusPins` and its spec / `PIN_ORDER_MAX_MOVE` entry are deleted.
- Sheets 1-3 redrawn for the one-unit symbol (`_common.relay()`: turned 270, coil on top, COM left, NC
  upper / NO lower right; `coil_block()`: the coil diode above the coil, H4 / SW labels pointing up).
  The contacts sit exactly where the pole units were (Omron pole 4 / 6 / 8 = the former unit C, pole
  13 / 11 / 9 = unit B, 8 grid units lower), so the contact wiring is unchanged except RLY5's lower pole
  (2 grid units higher than its former unit: the wires to RLY4 NO 9, MV2 and MV3 follow) and RLY4's coil
  feed: D4 / D5 (#00081 from SW3 / SW2) now stand right of the coil diode instead of below the relay.
  Rendered and checked (build/tmp, not committed).
- `PIN_ORDER`: the relay entries as PF's: the unmoved stock G5V-2 on the Omron ids fits unmirrored
  (0.000), and the Phase 1 symbol mapping (Proteus 4 / 2 / 3 / 1 on Omron 1 / 4 / 6 / 8) in today's ids fits
  only mirrored (0.000 mirrored, 7.620 unmirrored), which proves `IPC_PIN_IDS` is the physical mapping.
- `REMOVED_TRACKS` reason texts follow the new auto net names (Net-(U3B-G2), Net-(R16-Pad1); keys
  unchanged), `tools/check_removed_tracks.py` comment likewise.

Proof of "electrically identical" (old = step 2 commit, new = this commit):

- Every IPC record (refdes, pin, x, y, net) of `reference/ipc356_pads.json` equals the old one with the
  RLY pins mapped through `IPC_PIN_IDS` (366 records): every relay pin stays on its IPC net.
- Board (pcbnew, scratch script): tracks and vias identical (752 items: start, end, width, layer); every
  pad identical in position, size, drill and shape (352 pads, RLY pads renumbered by the map); the pad /
  track sets per net identical (101 nets). 20 auto net names change, all `Net-(RLY…)` names of the
  former split symbol (e.g. Net-(RLY4B-COM13) → Net-(U3B-G2), Net-(RLY3B-NC11) → Net-(R16-Pad1),
  Net-(RLY4A-COIL1) → Net-(D4-PadK)). The board file diff is large (pad numbers, net names, item order)
  but the copper is the same.
- compare_netlists (98 / 98 nets, 0 wrong-net pins), ERC 0 / 0, check_footprints, check_board,
  assign_nets, DRC (same accepted counts), ipc356_diff (366 / 366, 98 nets 1:1) and gerber_roundtrip (same
  XOR areas and clusters; `reports/roundtrip/roundtrip.txt` equals the old one as a multiset of lines
  after normalising the RLY pin ids, `Net-(…)` names and the relay footprint name) all pass.

Expected changes (design change, electrically identical): `reference/*` (RLY pin ids), `lib/part_map.csv`
unchanged, `lib/tube_preamp.kicad_sym` (G5V-2), `lib/footprint_map.csv` (RLY1-RLY5 footprint),
`lib/tube_preamp.pretty/Relay_DPDT_Omron_G5V-2_ProteusPins.kicad_mod` deleted, `kicad/01-03_*.kicad_sch`,
`kicad/tube_preamp.kicad_pcb` (RLY pad numbers, auto net names), `reports/footprint_fit.csv` /
`footprint_pads.csv` (RLY footprint and pad ids), `reports/roundtrip/roundtrip.txt` (names). The pin-order
renders `reports/pin_order/RLY*.png` (visual aids, not regenerated by the checks) still show the former
`_ProteusPins` footprint; regenerate with `p2k check_pin_order --render` (needs matplotlib) if wanted.

Negative tests (scratch, all restored; full regeneration and `check_all.sh` afterwards):

| Test | Result |
|---|---|
| R1 RLY1 `IPC_PIN_IDS` with COM 13 / NC 11 swapped (`"2": "11", "3": "13"`) | check_pin_order FAILED (stock G5V-2 unmirrored 5.080; Phase 1 mapping mirrored 5.080); compare_netlists 3 wrong-net pins (#00005 / #00014 split and merged at RLY1-11 / RLY1-13); check_footprints FAILED (RLY1 residual 5.080 mm on pads 11 / 13) |
| R2 sheet 1: RLY1 NC 6 and NO 8 swapped in the drawing | compare_netlists 3 wrong-net pins (#00018 / #00019 at RLY1-6 / RLY1-8) |

**Strict opt-outs after the migration: none.**

## Generation stopped 2026-11-20 (Opus 5.5)

**User decision 2026-11-20** (through the coordinating session): rev A (this board at the repo
root) is no longer generated from the Proteus data. From now on the committed KiCad files
(`kicad/`, `lib/`) are the source and are edited in KiCad. Last generated state: commit
`e219d15` (main). At that commit every generator reproduced the committed files byte for byte
(`make_part_map.py`, `gen_symbols.py`, `gen_footprints.py` `--check`: up to date; `make_pcb.sh
--check`: "board rebuilt from scratch, byte-identical"), run once more from `tools/generate/`
after the move. Generation stopped with the commit that records this section. Rev B (the
redesign) is a separate project in `rev_b/` and is not touched or checked here.

### What changed

- **Generators frozen**: `tools/make_part_map.py`, `tools/gen_symbols.py`, `tools/sheets/`,
  `tools/gen_footprints.py` and `tools/make_pcb.sh` moved to `tools/generate/` (repo-root paths
  inside adjusted so they stay importable), with `tools/generate/README.md` saying that they are
  frozen history and must not be run. `tools/generate/make_pcb.sh` refuses to run (exit 2)
  unless its first argument is `--force-regenerate`. `p2k sheets` finds no `tools/sheets/` any more.
- **Still imported**: `p2k check_pin_order` imports `tools/generate/gen_footprints.py` for its
  `RULES` / `PROJECT` specs (`PIN_ORDER` spec= entries, `PIN_ORDER_MAX_MOVE`); new config key
  `FOOTPRINT_SCRIPT = "tools/generate/gen_footprints.py"` in `p2k_config.py`.
- **`tools/check_all.sh`**: removed the steps that regenerate or byte-compare generated files:
  `make_part_map.py --check`, `gen_symbols.py --check`, `gen_footprints.py --check`, `make_pcb.sh
  --check` (there was no `p2k sheets --check` step). Kept, all on the committed files:
  1. KiCad environment (pcbnew 10.0.7)
  2. `p2k ipc356 --check` - Proteus IPC parse counts and `reference/` vs the Proteus IPC (the
     tables are derived from the Proteus truth, not from KiCad; the other checks read them)
  3. `p2k check_sources` - Gerber X2 export vs IPC
  4. `p2k check_symbols` - symbol pin sets vs IPC
  5. `p2k erc`
  6. `p2k compare_netlists` (strict nc_joined, net_names)
  7. `p2k check_footprints --pcbnew` - footprints vs IPC pad geometry
  8. `p2k check_pin_order`
  9. `p2k check_board` - pads, vias, holes vs IPC
  10. `p2k assign_nets --check` - copper connectivity
  11. `p2k drc` - schematic parity, strict defaults, `DRC_ACCEPTED`
  12. `p2k ipc356_diff` - KiCad's IPC-D-356 export vs Proteus
  13. `p2k gerber_roundtrip --check` - KiCad gerbers / drills vs Proteus, 2010 Excellon
  14. `tools/check_removed_tracks.py` - never regenerated anything (it reads the board file, the
      config and the Proteus gerbers); only its docstring was updated.
- `check_all.sh` checks only the rev A files at the root (the p2k tools find the board through
  `p2k_config.py` at the root; no step globs files); `rev_b/` is not scanned.

### Working on rev A from now on

Edit `kicad/tube_preamp.kicad_pcb`, the sheets and `lib/` in KiCad 10, then run
`tools/check_all.sh`. A change that makes the board differ from the Proteus truth (copper, pads,
nets, drills) makes a check fail on purpose: record it as a deviation (the matching
`p2k_config.py` key with a reason - `REMOVED_TRACKS`, `DRILL_SMALLER`, the `ROUNDTRIP` deviation
hooks, `DRC_ACCEPTED`, ... - and a line in STATUS.md), never hide it by loosening a check.

### Negative tests (scratch copies in build/tmp/neg, rev_b/ and .git excluded; edits saved with pcbnew)

| Edit (scratch copy) | Result |
|---|---|
| Track J4 F.Cu (33.02, 5.207)-(33.02, 31.115) moved 0.3 mm across (x) | **FAILED**: `gerber_roundtrip` (2 unexplained clusters, 1 draw without copper in the other set); all other checks pass (the track still touches its pads) |
| The same track moved 2.0 mm across (x) | **FAILED**: `assign_nets --check`, `drc`, `gerber_roundtrip`; `check_board` and `ipc356_diff` pass (they compare pads / vias / holes and their nets, not track geometry) |
| The same track moved 0.3 mm along its own axis (y) | passes: both ends stay inside the pads, so the extra copper is in the pad-shape clusters of the round trip (tolerance limit, not a hidden deviation: no net or connection changes) |
| R1 reference text moved 0.5 mm (copper-neutral; pcbnew save otherwise byte-identical) | **ALL CHECKS PASSED** |

`tools/generate/make_pcb.sh --check` without the flag: refuses, exit 2. The real repo:
`tools/check_all.sh` ALL CHECKS PASSED (below), `git status` clean apart from the commit.

## Last check output

`tools/check_all.sh` (2026-11-20, after generation stopped: p2k a9a286c, no strict opt-outs, 14 steps; exit status 0):

```
== KiCad environment
pcbnew 10.0.7
== IPC-D-356A parse self-check (counts) and reference/ vs the Proteus IPC
ipc356: nets=98, records=366, refdes_raw=164, tht_records=366, smd_records=0, smd_top=0, smd_bottom=0, nc_pads=3, vias=14, free_pads=0, holes=13, parts=163
ipc356: OK
ipc356: pin ids renamed (IPC_PIN_IDS): RLY1 1->9 2->13 3->11 4->16 5->1 6->4 7->6 8->8; RLY2 1->9 2->13 3->11 4->16 5->1 6->4 7->6 8->8; RLY3 1->9 2->13 3->11 4->16 5->1 6->4 7->6 8->8; RLY4 1->9 2->13 3->11 4->16 5->1 6->4 7->6 8->8; RLY5 1->9 2->13 3->11 4->16 5->1 6->4 7->6 8->8
== Gerber X2 export vs IPC (pads, vias, holes, drills, outline)
  8 gerbers, one SameCoordinates id
  Top Copper: Draw:Conductor 402, Draw:Profile 4, Flash:ComponentPad 339, Flash:OtherPad,Unknown 13, Flash:ViaPad 14
  Bottom Copper: Draw:Conductor 345, Draw:Profile 4, Flash:ComponentPad 339, Flash:OtherPad,Unknown 13, Flash:ViaPad 14
  drills: 366 plated, 0 non-plated
  outline 382.8 x 71.9 mm at (-195.36, -45.73)
check_sources: OK
== Symbol pin sets vs IPC
  12AX7                  3  pins  9  U1 U2 U3
  C                     27  pins  2  C1 C3 C4 C5 C6 C7 C8 C9 ...
  C_Polarized            2  pins  2  C2 C30
  C_Polarized_12         6  pins  2  C28 C33 C34 C35 C36 C37
  D                      7  pins  2  D1 D2 D3 D4 D5 D8 D9
  G5V-2                  5  pins  8  RLY1 RLY2 RLY3 RLY4 RLY5
  J112                   9  pins  3  Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 ...
  PIN                   47  pins  1  GTR_GND GTR_IN POT1_1 POT1_2 POT2_1 POT2_2 POT3_1 POT3_2 ...
  R                     57  pins  2  R1 R2 R3 R4 R5 R6 R7 R8 ...
symbols: 9 part types, 163 refdes, 0 power symbols
symbols: OK
== ERC
erc: 0 errors, 0 warnings (reports/erc.rpt)
== Netlist comparison vs IPC
compare: parts 163/163 present, 0 missing, 0 extra; pins compared 339, wrong-net pins 0; IPC nets touched 98, complete 98 (+ 3 N/C / no-net pins)
compare: per sheet (drawn/total) 1:36/36 2:33/33 3:34/34 4:39/39 5:21/21
compare: OK
== Footprints vs IPC pad geometry
check_footprints: pcbnew placement of 163 parts, worst pad offset 0.001 mm
check_footprints: note: U1: THT pad pattern fits only mirrored -> bottom side
check_footprints: note: U2: THT pad pattern fits only mirrored -> bottom side
check_footprints: note: U3: THT pad pattern fits only mirrored -> bottom side
check_footprints: 163/163 parts fitted, 339 pads, 16 footprints, worst residual 0.001 mm (limit 0.05)
check_footprints: OK
== Pin order vs unmoved KiCad base footprints
check                    base (unmoved)                                     unmirrored         mirrored  result
Q1 Q2 Q3 Q4 Q5 Q6 Q7 Q8 Q9 TO-92_Inline_Wide                               0.508 @   180    0.508 @     0  unmirrored 0.508  (TO-92_Inline_Wide is P2.54, Proteus P2.032)
D1 D2 D3 D4 D5 D8 D9     polarity: base pad 1 (marked) = pin 'K' (expected 'K')
D1 D2 D3 D4 D5 D8 D9     D_DO-41_SOD81_P10.16mm_Horizontal               0.000 @   180    0.000 @     0  unmirrored 0.000
C2                       polarity: base pad 1 (marked) = pin '+' (expected '+')
C2                       CP_Radial_D6.3mm_P2.50mm                        0.020 @   180    0.020 @     0  unmirrored 0.020  (P2.50 vs P2.54)
C30                      polarity: base pad 1 (marked) = pin '+' (expected '+')
C30                      CP_Radial_D6.3mm_P2.50mm                        0.000 @   270    0.000 @    90  unmirrored 0.000
C28 C33 C34 C35 C36 C37  polarity: base pad 1 (marked) = pin '2' (expected '2')
C28 C33 C34 C35 C36 C37  CP_Radial_D16.0mm_P7.50mm                       0.000 @   270    0.000 @    90  unmirrored 0.000
RLY1 RLY2 RLY3 RLY4 RLY5 Relay_DPDT_Omron_G5V-2                          0.000 @   180    7.620 @   180  unmirrored 0.000  (Omron ids (IPC_PIN_IDS) on the unmoved KiCad G5V-2)
RLY1 RLY2 RLY3 RLY4 RLY5 (Phase 1 mapping) Relay_DPDT_Omron_G5V-2                          7.620 @   180    0.000 @   180  mirrored 0.000  (the Phase 1 symbol mapping fits only mirrored)
U1 U2 U3                 Valve_Noval_P                                  17.631 @ 150.3    2.972 @     0  mirrored 2.972
U1 U2 U3 (ideal)         ideal n=9 PCD 21 mm                            19.319 @   162    0.007 @   342  mirrored 0.007  (ideal standard noval, PCD 21.00 mm)
noval footprint vs ideal Valve_Noval_Belton_PCD21.00mm                   0.007 @   342   19.319 @   198  unmirrored 0.007  (standard noval numbering in the footprint's own view)
U1 U2 U3 (project)       Valve_Noval_Belton_PCD21.00mm                  19.315 @   144    0.001 @     0  mirrored 0.001  (fits only mirrored = bottom side)
derived                  CP_Radial_D16.0mm_P7.50mm_Pin2Plus                   pads moved  0.000 mm (limit 0.001)
derived                  CP_Radial_D6.3mm_P2.50mm_PM                          pads moved  0.000 mm (limit 0.001)
derived                  CP_Radial_D6.3mm_P2.54mm_PM                          pads moved  0.020 mm (limit 0.03)
derived                  C_Disc_D7.5mm_W2.5mm_P5.08mm                         pads moved  0.040 mm (limit 0.05)
derived                  C_Rect_L13.0mm_W6.0mm_P9.70mm                        pads moved  0.150 mm (limit 0.16)
derived                  C_Rect_L16.5mm_W7.0mm_P9.70mm                        pads moved  2.650 mm (limit 2.66)
derived                  C_Rect_L24.0mm_W7.0mm_P20.00mm                       pads moved  1.250 mm (limit 1.26)
derived                  D_DO-41_SOD81_P10.16mm_Horizontal_AK                 pads moved  0.000 mm (limit 0.001)
derived                  R_Axial_DIN0414_L11.9mm_D4.5mm_P19.05mm_Horizontal   pads moved  0.635 mm (limit 0.64)
derived                  TO-92_Inline_P2.03mm                                 pads moved  0.508 mm (limit 0.51)
bottom                   footprint_fit.csv and kicad/tube_preamp.kicad_pcb: U1 U2 U3 bottom (B.Cu), the other 173 footprints top
check_pin_order: OK (11 checks as recorded)
== Board pads, vias, holes vs IPC (position, size, nets 1:1)
check_board: 176 footprints, 339 pads, worst pad offset 0.001 mm (limit 0.05), 98 IPC nets mapped 1:1, 13 mounting holes
check_board: 738 tracks, 14 vias, 0 zones
check_board: 752 track / via nets in the board file = their copper group's net (track_nets)
check_board: OK
== Board copper connectivity (KiCad geometry)
assign_nets: after zone fill: 114 groups, 0 shorts, 0 orphans, 0 opens, 0 items with a foreign net
assign_nets: OK (report reports/assign_nets.txt)
== DRC with schematic parity
drc: 147 violations, 0 shorts, 0 unconnected, 0 parity issues (reports/drc.json)
drc:     36 error    courtyards_overlap  accepted: KiCad courtyards vs the Proteus placement (36 pairs, parts exactly at the Proteus positions): film caps and resistors packed closer than the KiCad courtyards, Q7-Q9, terminals at film caps (the noval sockets U1-U3 are on the bottom side since Phase 5)
drc:     16 error    pth_inside_courtyard  accepted: the same Proteus placement: 16 pads (R / C pads in neighbouring film-cap / resistor courtyards; mounting holes H103-H105 and R1, C4, R18, C9, R30 in the B-side noval socket courtyards: a THT pad is on both sides)
drc:     74 warning  silk_over_copper
drc:     21 warning  silk_overlap
drc: OK
== IPC-D-356 from the board vs Proteus (pads, vias, holes, nets)
ipc356_diff: Proteus 366 records, KiCad 366; matched 366 (339 pads incl. 3 N/C, 14 vias, 13 holes), worst position offset 0.002 mm (limit 0.05)
ipc356_diff: 98 Proteus nets mapped 1:1 onto KiCad nets, 0 mismatches
ipc356_diff: KiCad drill larger (footprint kept): 129x 0.762->0.8, 6x 0.762->1.001, 14x 1.016->1.1, 22x 1.016->1.199, 14x 1.143->1.199
ipc356_diff: KiCad drill smaller, accepted (DRILL_SMALLER): 4x 0.762->0.749, 40x 1.143->0.701, 8x 1.143->1.001, 28x 1.143->1.1
ipc356_diff: pads with another size in KiCad (info): C 70, D 14, Q 27, R 114, RLY 40
ipc356_diff: 3 unconnected-(...) nets, one record each (nc_joined)
ipc356_diff: OK
== Gerber round trip vs Proteus (copper XOR, coverage, drills, 2010 Excellon)
roundtrip: F.Cu   XOR  260.90 mm^2, beyond 0.05 mm: only Proteus 188.53, only KiCad  12.69 mm^2; clusters >= 0.01 mm^2: 339 pad shape; draws/flashes off the other copper: 0 Proteus, 0 KiCad
roundtrip: B.Cu   XOR  264.42 mm^2, beyond 0.05 mm: only Proteus 190.62, only KiCad  12.56 mm^2; clusters >= 0.01 mm^2: 317 pad shape; draws/flashes off the other copper: 0 Proteus, 0 KiCad
roundtrip: Proteus objects not compared (recorded deviations, all layers): 9 Conductor draws (REMOVED_TRACKS)
roundtrip: drills 0 mismatches; KiCad drill smaller, accepted (DRILL_SMALLER): 4x 0.762->0.75, 40x 1.143->0.7, 8x 1.143->1.0, 28x 1.143->1.1; report reports/roundtrip/roundtrip.txt, overlays reports/roundtrip/*.png
roundtrip: counts (roundtrip_counts): KiCad track draws / flashes per layer F.Cu 397 / 366, B.Cu 341 / 366: tracks as gerber_to_tracks builds them, flashes = Proteus
roundtrip: OK
== Removed Proteus track pieces are exactly the 9 decided ones
check_removed_tracks: 9 decided pieces, 9 in REMOVED_TRACKS, all Proteus draws, none of 738 board tracks
check_removed_tracks: OK

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
   **User 2026-11-20: no change unless the real board shows otherwise** (design fixes).
5. **The 250p caps C18/C22/C26 use the Proteus device CERAMIC56P**: device name and value disagree;
   values from the schematic.
6. Export quirks (no effect, as on the power amp): Mechanical 1's X2 FileFunction is
   `NonPlated,1,2,NPTH` although it holds only the profile; solder resist files negative; the CADCAM
   READ-ME says format 4.3 while the files use `FSLAX45Y45`.
7. **Stale layout values**: ROOT.LYT (layout) and ROOT.DSN (schematic) disagree for six resistors
   (plus Q4, finding 1): **R13** 0R (schematic) / 10M (layout), **R22** 220k/2W / 100k/2W, **R27**
   120k / 22k, **R30** 2k2 / 1k8, **R34** 22k / 100k, **R51** 100k / 22k. The part map takes the
   schematic values (playbook: ROOT.LYT values can be stale); which values are on the built board
   is for the user to confirm before a BOM is made from rev A. Also: R33 `220k` (no `/2W` in the
   value) uses the 2 W metal-film package; R36/R40/R43 are written `220K`, the others `220k`.
8. **J112 drain / source alternate** (Phase 1 pinout reading, Proteus J112: D = 1, S = 2, G = 3):
   Q1 and Q7-Q9 have the drain on the signal node and the source on PRE-GND, Q2-Q6 the drain on
   PRE-GND. The J112 is a symmetric switching JFET, so no electrical effect; noted for the
   footprint / pin-order check of Phase 2 (both orientations are on the board).
9. **RLY3's two NO contacts are joined** (pins 1 and 8 both on #00062, sheet 2) and RLY4/RLY5
   chain their contacts (RLY4-1 / RLY5-2 #00085, RLY4-8 / RLY5-6 #00084): as drawn, no error;
   noted to help the reading of sheets 2 and 3.

10. **U3 triode A is a cathode follower with its anode directly on `E`** (no anode resistor; R33
    from `E` only feeds the grid bias node R33 / R48 / C30 → R49). As drawn in the PDF and in the
    IPC (E: U3-1, R33-2); noted for the reading of sheet 3.
11. **R13 is `0R`** in series with R14 (10M) between the C5 / R15 node and the grid of U1 triode B
    (layout value 10M, finding 7): which one is on the board decides whether the divider is
    10M or 20M.
12. **MV0 is a ground pad** (on PRE-GND, sheet 3), as are GTR-GND, POT-GND and PRERETURN: four
    ground fly-lead pads on this board.

13. **Noval socket pin numbering is mirrored against the noval standard** (Phase 2; the same as the
    power amp's octal sockets, its finding 10). The Proteus `9-PIN BELTON NOVAL` pads of U1-U3 run
    1 → 9 clockwise seen from the component (top) side; the standard (and KiCad's `Valve_Noval_P`)
    runs clockwise seen from the pins, i.e. from the solder side of a top-mounted socket. Proteus
    places U1-U3 on the top (Top Silk / Top Assembly). With a 12AX7 in a top-mounted socket, no
    rotation makes it work (with the gaps aligned, tube pin 1, anode A1, would sit on pad 9, which has
    no net, and tube pin 9 on pad 1). Since the preamp was built and played, the sockets were most likely **mounted on the solder
    side** (tubes below the board; then the pattern is correct), or wired differently. **Please
    confirm with the built preamp** which side the sockets are on. The conversion keeps the Proteus
    pads, ids and top side (copper identical either way); if they are on the solder side, Phase 5 can
    move the socket footprint to B (silk / courtyard / 3D model) with standard numbering. Pitch circle
    21.00 mm, pads 4.318 / 1.727 mm. **User: the sockets are on the solder side; done in Phase 5**
    (U1-U3 on B with the standard numbering, copper unchanged).
14. **G5V-2 pin ids by pad position** (Phase 2): the Proteus coil pin 4 and pole 1 (COM 2, NC 3,
    NO 1) sit on the Omron 16 / 13 / 11 / 9 column (KiCad top view), coil pin 5 and pole 2 (6 / 7 / 8)
    on Omron 1 / 4 / 6 / 8. The Phase 1 symbol mapping read Proteus 4 / 2 / 3 / 1 as Omron 1 / 4 / 6 /
    8, which is the mirror image. The G5V-2 pattern (2 x 4) and the relay (two identical poles, coil
    pins 1 / 16 interchangeable on the standard non-latching type) are mirror-symmetric, so both
    readings describe the same part: no electrical effect. Only a polarized or latching coil variant
    would make the coil orientation matter (Omron 1 / 16 then fixed); not the case on this board as far
    as the schematic shows (flyback diodes D1-D3, D8, D9 across the coils, finding 4).
    **Fixed 2026-11-20 (user decision)**: the symbol uses the footprint's physical mapping and Omron's
    terminal names (COIL16 / COIL1, COM13 / NC11 / NO9, COM4 / NC6 / NO8); pin numbers = Proteus ids,
    every pin on its net, no copper change ("Design fixes 2026-11-20").
15. Smaller Proteus details seen in Phase 2: C2 (ELEC-RAD10) is P2.54 while C30 (22U 100V) is P2.50
    (both 6.3 mm cans); the CAP20 discs are P5.08; the 22n Xicon and Orange Drop films are P9.70 (not
    a 10 / 10.16 grid), the 100n Xicon P20.00; the TO-92 pitch is 2.032 mm (80 mil); the relay holes
    are 1.143 mm (KiCad 0.7); the C28 / C33-C37 electrolytics match KiCad's D16 P7.5 exactly.

16. **A 0.0635 mm track stub in the Proteus copper** (Phase 3): B.Cu, (88.9, 0.762) → (88.9, 0.6985)
    (KiCad frame), Net-(RLY4B-COM1), at the bend of the RLY4-2 track; it lies inside the 0.508 mm
    track (KiCad DRC `track_dangling` warning). No electrical effect; kept, as built.
    **Removed 2026-11-20 (user decision, `REMOVED_TRACKS`; "Design fixes 2026-11-20").**
17. **Each noval socket has three mounting holes around it** (Phase 3), about 16.3-18.0 mm from the
    socket footprint origin: H103 / H106 / H109 (U1), H104 / H107 / H110 (U2), H105 / H108 / H111
    (U3); one of each set (H103-H105) lies inside the Proteus Top Assembly rectangle of the socket
    (26.4 × 25.4 mm). Fits the user's answer that the sockets are on the solder side (a socket
    bracket or standoffs); noted for the Phase 5 bottom-side socket footprint (courtyard).
18. **Two TO-92 tracks pass pad 1 at 0.421 mm** (Q4, Q6, Phase 3): fine with Proteus' round pads,
    0.122 mm with KiCad's square pad 1 (user question, "Phase 3").

19. **Sheet 3: the `H4` net terminal of U3 pin 4 sits directly above a junction of another net**
    (Phase 4 PDF reading): the terminal circle, its rotated label `H4` and then the junction dot of
    the C15 / R45 / RLY4-COM2 wire (#00082) are in one vertical line. No wire joins them (checked at
    1200 dpi; the IPC agrees). A reading trap in the PDF only; nothing on the board.
20. **More very short Proteus track draws** (Phase 4), besides the stub of finding 16 (IPC / Gerber
    frame; written "KiCad frame" before, corrected 2026-11-20):
    two of **zero length** on F.Cu at (-61.722, -22.225), H4, and (-61.087, -1.905),
    Net-(RLY3B-NC1); and 0.09-0.18 mm pieces on F.Cu (-130.81, -38.735) and (-139.7635, -16.5735),
    PRE-GND, (-60.96, -1.905), Net-(RLY3B-NC1), and on B.Cu (-43.942, -6.858), PRE-GND, (-19.05,
    24.13), H5, (-114.3, -18.415), H4. All lie on their own net's copper (track joints of the 2010
    routing); DRC reports only the finding-16 stub. Kept, as built (user decision Phase 5: no
    `REMOVED_TRACKS`, also for the finding-16 stub). **Removed 2026-11-20 (user decision, reverses
    that: all 8 pieces in `REMOVED_TRACKS`; "Design fixes 2026-11-20").**
21. **R34 and R51 are exactly swapped between the schematic and the layout values** (finding 7 read
    again in Phase 4): schematic R34 22k / R51 100k, layout R34 100k / R51 22k. They are the two
    resistors in series from `F` to U3's anode (pin 6) with EQOUT / C29 tapped between them, so the
    order decides the output level at EQOUT. Part of the open value question (finding 7).

## p2k candidates

(Shared-tool limitations met on this board, with the board-local workaround used.)

1. **`TRUNCATED_NETS` keys are looked up by the KiCad refdes and unknown keys are ignored
   silently.** A key in the full-Proteus spelling (e.g. the power amp's `"P.I.GND"`, renamed to
   `PI_GND` by `KICAD_REFDES`) is never checked. Here the keys are the KiCad names (verified by a
   negative test). The shared tool would need: accept either spelling and fail on keys that match no
   refdes.
    **Shared-tool migration 2026-11-20:** not migrated: still open in p2k (CANDIDATES.md I1 `truncated_nets_keys`); the keys here are the KiCad names (checked).
2. **`p2k.pdsprj.dsn_values` / `lyt_parts` cannot handle single-letter refdes** (`A`-`D`): the refdes
   search matches unrelated one-letter strings and `dsn_values` raises. Workaround for Phase 1: call
   them without `A`-`D` and give those four `TERMINAL` / `PIN` by hand (a board-local override in the
   part-map script, like the pilot's `LATIN1_PARTS`). The shared tool would need: anchor the refdes
   match to the part-record structure. The pilot's candidate 1 (Latin-1 `µ` values dropped) applies
   here too (9 values).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (P2: one-character refdes read in the refdes slot); `SINGLE_LETTER_PARTS` dropped, `tools/make_part_map.py` is a `part_map.run` SPEC.
3. **`DRILL_EXCELLON` from a different revision**: the 2010 Excellon lacks the 2 October vias; if
   `gerber_roundtrip` requires a 1:1 match, Phase 4 needs an "expected extra holes" option or a
   board-local wrapper. **Phase 4:** it does require 1:1 (2 drill mismatches, `--check` fails).
   Board-local answer: `tools/roundtrip.py` wraps `gerber_roundtrip.compare_excellon` and accepts
   exactly the listed positions (`EXPECTED_NOT_IN_EXCELLON`), failing if a listed one is not
   reported missing. The shared tool would need: a config key such as `EXCELLON_MISSING = {(x, y):
   reason}` (every entry must match a drill gerber flash absent from the Excellon file).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (R2 `EXCELLON_MISSING` + `EXCELLON_MISSING_LABELS`, report lines word for word); `tools/roundtrip.py` deleted.
4. `p2k ipc356` prints "Net aliases: ." when `NET_ALIASES` is empty (cosmetic, as on the pilot).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (I3; `Net aliases: none.`, D-R re-baseline in step 1).
5. **A `no_connect`-type symbol pin hides wiring mistakes from `compare_netlists`**: in the KiCad 10
   kicadxml netlist such a pin stays in its own `unconnected-(…)` net even when a wire joins it to a
   net (ERC only warns `no_connect_connected`), so an N/C pad wired by mistake is not an N/C
   mismatch for compare. Found in the smoke test (12AX7 pin 9 wired to H5: compare OK). Board-local
   answer: pin 9 is `passive` with a no-connect flag (compare then reports the mistake; a missing
   flag is an ERC error). The pilot's EL34 pin 6 (`no_connect` type, left open) has the same blind
   spot. The shared tools would need: compare_netlists to fail on any `no_connect_connected` ERC
   item or read the pin's wires, or a playbook rule "N/C pads = passive pin + no-connect flag".
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (S7 strict `no_connect_pin_type`, on by default; playbook N/C rule G3). The board already used passive + no-connect flag.
6. **Part-map generator, third copy** (`tools/make_part_map.py`: pilot script + `SINGLE_LETTER_PARTS`
   and a `LATIN1_PARTS` that can keep the pdsprj device / package): the pilot's candidate 5 (a shared
   `p2k.part_map` with config keys) is now wanted by three boards.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (M1 `p2k.part_map`, `LATIN1 = True`; P1 Latin-1 values); `SINGLE_LETTER_PARTS` / `LATIN1_PARTS` dropped.
7. **symgen helpers written board-locally** in `tools/gen_symbols.py`: `pin_types()` (pilot
   candidate 9), `swap_units()` (renumber the units of a std symbol: ECC83 units 1/2) and
   `hide_pin_names()` (G5V-2_Split with Proteus pin names). A shared `from_std(..., pin_types=,
   units=, hide_pin_names=)` would cover them.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (S1 / S2: `from_std(pin_types=, units=, hide_pin_names=True)`); the three board helpers deleted.
8. Pilot candidates 3, 6, 7, 8 apply here unchanged and are handled the pilot's way in
   `tools/sheets/_common.py` (`term()`, `place_mirrored()`, terminal text justification, a heater
   unit per tube placed by `tube()`). `TRUNCATED_NETS` keys checked (pilot candidate 11 / candidate
   1 here): they are the KiCad refdes.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (K1 `place(mirror=)`, K4 `terminal(..., symbol=, value=, justify="away")`); `place_mirrored()` deleted, `term()` is a one-line call of `sheetkit.terminal`; `tube()` / `relay()` stay (board helpers placing the units).

9. **`compare_netlists` crashes on a refdes without a number next to a numbered one with the
   same prefix** (here `PRES` and `PRES1`-`PRES3`, sheet 3; found first on the PI / FX board with
   `SEND` / `SEND1`): `natkey()` / `pinkey()` build mixed str / int sort keys and `sorted()`
   raises `TypeError`. Board-local answer: `tools/compare.py`, a wrapper that replaces the two
   key functions with type-safe ones and calls `compare_netlists.main()` (same arguments and
   output; copied from `~/dev/tube_pi_fxloop_kicad/tools/compare.py`). The shared tool needs the
   same key.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (C1 type-safe keys); `tools/compare.py` deleted, check_all runs `p2k compare_netlists`.
10. **`sch_builder.Sheet.place` text placement**: (a) horizontal two-pin parts get Reference /
    Value at ±2.54 mm, which overlaps capacitor plates (board-local `hcap()` with `ref_at` /
    `value_at`); (b) multi-unit symbols placed rotated or mirrored keep the library field
    offsets, which land on the body (board-local text positions in `relay()` and `tube()`);
    (c) no option to hide the Value of the extra units, so every relay / tube unit prints it.
    A shared `place(..., mirror=, text=)` for multi-pin parts would cover these and pilot
    candidate 6.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c: (a) K2 `text_gap` (`hcap()` = `horiz2(..., text_gap=3.81)`); (b) K1 `fields_auto` and (c) K3 `hide_value` exist but are not used (the sheets keep their explicit text positions and stay byte-identical).
11. **sheetkit has no "wire to rail with junction" helper**: every sheet script defines its own
    `gnd(p)` (wire straight down to the ground rail + junction). A missing junction where a rail
    passes a pin end is only a compare *warning* while other sheets are undrawn (it became
    visible through the ERC error); candidate for a `sheetkit.rail()` helper.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (K5 `sheetkit.rail()`); the per-sheet `gnd(p)` of sheets 1-3 deleted.

12. **`footprints.run` does not write `kicad/fp-lib-table`** (pilot candidate 12): the board script
    writes and `--check`s it (`fp_lib_table()`, copied from the pilot).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (F1 `FP_LIB_TABLE = True`); `fp_lib_table()` deleted.
13. **Pin-order check written board-locally** (pilot candidate 13): `tools/check_pin_order.py`
    (unmoved base + renumbering, both mirror states, ideal noval on the pitch circle, the second relay
    reading, `--render`). A shared `p2k.check_pin_order` with config (groups, expectations, ideal
    circular sockets with n positions / gap) would serve the octal and noval boards alike.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (F11 `p2k check_pin_order`: `PIN_ORDER` 11 entries, `PIN_ORDER_BOTTOM`, `PIN_ORDER_MAX_MOVE`); `tools/check_pin_order.py` deleted, negative tests repeated (STATUS.md "Shared-tool migration 2026-11-20").
14. **`footprints.derive()` with `ipc` hides a wrong renumbering**: it fits the renumbered base onto
    the IPC pads and moves every pad onto its IPC position, so a wrong renumbering gives pads moved
    by a pitch (graphics, band, `+`, pin-1 mark left behind) and `check_footprints` passes by
    construction; for two-pad parts even the unmoved-base pin-order fit cannot tell (180° fits).
    Board-local answer in `tools/check_pin_order.py`: `MOVE_LIMIT` (derived pads may move only by the
    intended pitch change) and `POLARITY` (the pin on the marked base pad 1, stated from the Proteus
    pinouts); negative-tested (relay COM / NC swap, C28 / C2 polarity). The shared tool would need: a
    spec key `max_move` (fail when a pad moves more) and `marked_pad` / polarity, or report the
    per-pad move in the library build.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (F3 spec `max_move` / strict `derive_max_move`; `PIN_ORDER_MAX_MOVE` = the former `MOVE_LIMIT`, `polarity` = the former `POLARITY`).
15. **Rule condition `package` takes one value**: the four Orange Drop packages (`1N` / `2N2` / `3N3` /
    `4N7 ORANGE DROP`, same footprint) need four identical rules. A tuple / set for `package` /
    `device` would help.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (F6 tuple / set `package`); not used here: the four Orange Drop rules stay (not in the migration list; the output is identical either way).
16. `body_poly` from a gerber again (pilot candidate 14): `noval_body()` reads the socket rectangle of
    the Top Assembly at generation time (a spec key `body_from=("Top Assembly", refdes)` would cover
    the octal and noval cases).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (F5 spec `body_from`); `noval_body()` deleted.
17. Board-script pitfall (not a p2k bug): `check_pin_order.py` imports `gen_footprints.PROJECT`; an
    edit of the same size within the same second left a stale `tools/__pycache__/*.pyc` in a
    negative test, so the script sets `sys.dont_write_bytecode`.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (G1; `check_pin_order` imports the footprint script without bytecode).

18. **`build_pcb` hard-codes the mounting-hole refdes `H<n>`**, which collides with schematic
    refdes `H4` / `H5` (heater terminals) on this board: `pcb.ipc_to_kicad_nets` keys pads by
    (refdes, pad number), so assign_nets failed with "IPC net H4 spans KiCad nets ['', 'H4']", and the
    board had duplicate references. Board-local answer: `tools/rename_holes.py` after `build_pcb`
    (H1-H13 → H101-H113). The shared tools would need: a `HOLE_PREFIX` / start-number key (like
    `FREE_PAD_PREFIX`) that fails on a collision with a schematic refdes, `ipc_to_kicad_nets` keyed on
    non-board-only footprints only, and `ipc356_diff`'s hole pattern (`H\d+`) taken from the same key.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (B1 `HOLE_START = 101`, strict `hole_refdes`); `tools/rename_holes.py` and its make_pcb step deleted, board file identical.
19. `tools/measure_gaps.py` is now copied into a third board (tube_psu → power amp → here,
    unchanged): a shared `p2k.measure_gaps` would do.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (B11 `kipy -m p2k.measure_gaps`); `tools/measure_gaps.py` deleted.
20. **`DRC_ACCEPTED` is per error type**: accepting one known clearance item (e.g. Q4 / Q6 here, if
    the user chose that) would hide every other clearance error. An item-level acceptance (type +
    refdes / position) would be needed for that option.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (B7 `DRC_ACCEPTED_ITEMS`); not needed here (no single clearance item is accepted).
21. **Footprint pad *shape* is not in the Phase 2 pad comparison**: `check_footprints` and the
    Phase 2 table compare pad positions and sizes; KiCad's square pin-1 pads (TO-92 1.5 × 1.5 vs
    Proteus round 1.524) are "smaller" by size but reach 0.30 mm further along the diagonal. A
    `check_footprints` note per part where the KiCad pad extends beyond the Proteus pad (polygon, not
    size) would flag such Phase 3 DRC conflicts in Phase 2.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (CF2, strict `pad_extent`, opt-in): not turned on (it needs pad decisions on every board, D-Z).

22. **`footprints.derive()` has no pad-shape override**: KiCad's square pin-1 pad cannot be made round
    from the spec (here the TO-92 pad 1, user decision (a); `ipc_sizes` would also change size and
    drill). Board-local answer: `tools/gen_footprints.py` wraps `footprints.derive` with
    `derive_with_pad_shapes` (spec keys `pad_shapes={pad: shape}` and `pin1_dot=(x, y, r)`, the
    same pin-1 dot as tube_pi_fxloop_kicad) and assigns it to the module
    attribute, which `build_library()` calls. The shared tool would need: a spec key `pad_shapes` (or
    `pad_overrides` with shape / size / drill per pad) in `derive()`, plus a pin-1 marker option
    for footprints whose only pin-1 mark was the square pad (two boards now).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (F4 spec `pads={"1": dict(shape="circle", expect_shape="rect")}` and `pin1_dot`); `derive_with_pad_shapes` deleted.

23. **`gerber_roundtrip.parse_excellon` reads metric 4.3 only** and ignores the `INCH` header line
    (pilot candidate): the 2010 fab drill file is inch 2.4. Board-local answer: the pilot's
    `tools/excellon_metric.py` copied (third use would make it a shared `p2k` converter or an inch
    branch in `parse_excellon`).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (R1: `DRILL_EXCELLON` = the inch source file); `tools/excellon_metric.py` and `reference/fab_2010_drill_metric.drl` deleted (accepted re-baseline: the `== excellon (...)` line of `reports/roundtrip/roundtrip.txt`).
24. `ipc356_diff` and `gerber_roundtrip` do not see a track net edited in the board file (pcbnew
    re-derives it on load; pilot observation, repeated here in the Phase 4 negative tests): only the
    byte compare of `make_pcb.sh --check` catches it. Once the board is edited by hand (after
    Phase 5) that step goes away; `assign_nets --check` and the DRC remain.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (B10 strict `track_nets`, on by default: check_board reads the track / via nets from the file).
25. **`footprints.from_ipc` mirrors only bottom SMD parts** (pilot candidate 24, second board): a THT
    socket mounted on the solder side has to be marked bottom by a board-local `build_library` wrapper
    (spec key `bottom`) so the footprint is built mirrored; a shared spec key `bottom=True` would do.
    `check_pin_order.bottom_side_noval()` is the board-local check of the result.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (F2 spec `bottom=True`, `PIN_ORDER_BOTTOM`); the `build_library` wrapper deleted.
26. **`DRILL_SMALLER` is matched by diameter pair only** in `ipc356_diff` and `gerber_roundtrip` (PI / FX
    candidate): another pad with the same pair passes and only changes a count (negative test D1).
    Board-local answer: `tools/check_drill_smaller.py` (copied from PI / FX, third repo would justify a
    per-refdes `DRILL_SMALLER` in p2k).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (R3 `DRILL_SMALLER` `(reason, pads)`); `tools/check_drill_smaller.py` deleted (negative test: C10 unlisted fails).
27. **`compare_netlists` lets two no-connect pins share one `unconnected-(...)` net** (PI / FX
    candidate; negative test N2) and ERC `no_connect_connected` is only a warning: board-local checks
    in `tools/compare.py` and `tools/erc.sh` (copied from PI / FX).
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (C2 strict `nc_joined` in compare_netlists, R4 in ipc356_diff; E1 `p2k erc` with `ERC_FATAL_WARNINGS`); `tools/compare.py` / `tools/erc.sh` deleted.
28. **`symgen.from_std` renames pins but cannot carry a pin-name scheme separate from the IPC ids**
    as data (finding 14 here): the Omron names are written per board in `gen_symbols.py`, and the
    pin-order check reads them back from the library by a name pattern (`check_pin_order.py`
    `relay_symbol_map()`). A shared "physical terminal name" field per footprint renumbering would let
    one table drive the footprint renumbering, the symbol names and the check.
    **Shared-tool migration 2026-11-20:** not migrated (no shared key); made moot by the relay design change (step 3): the IPC pin ids are the Omron numbers (`IPC_PIN_IDS`), symbol and footprint are KiCad's stock G5V-2, and `check_pin_order` fits the stock footprint directly.
29. **`gerber_roundtrip` does not fail on a `REMOVED_TRACKS` entry without a Proteus draw** (only
    `gerber_to_tracks` does), and no shared check requires the removed set to be exactly a decided one:
    a dropped entry passes the round trip when the piece lies on its own net's copper (design fixes
    2026-11-20, negative tests T1 / T2). Board-local: `tools/check_removed_tracks.py`.
    **Shared-tool migration 2026-11-20:** not migrated: `tools/check_removed_tracks.py` is kept as a board decision guard (the removed set equals the decided one); p2k a9a286c covers part of it (I7: gerber_to_tracks fails on an entry without a draw; strict `roundtrip_counts`).
30. **Board `make_pcb.sh` copies: `run >log || {...}` disables `set -e` in `run`** (fixed here
    2026-11-20 with `|| return 1` per step): a failing step in `--check` mode is passed over and its
    ERROR line filtered out. Probably in every board copied from the pilot.
    **Shared-tool migration 2026-11-20:** solved in p2k a9a286c (B12 `p2k make_pcb` stops at the first failing step); `tools/make_pcb.sh` is the one-liner `exec tools/p2k/bin/p2k make_pcb "$@"`.

## Decisions

- **User decision 2026-11-20, generation stopped**: stop generating rev A (the root board) from the
  Proteus data. From now on the committed KiCad files (`kicad/`, `lib/`) are the source, edited in KiCad.
  Last generated state: commit `e219d15` (byte-identical with every generator); stopped in the commit
  that adds section "Generation stopped 2026-11-20". Generators frozen in `tools/generate/`; `check_all.sh`
  keeps only the checks of the committed files against the Proteus truth and KiCad's rules; deviations
  from Proteus are recorded, never hidden. Rev B is in `rev_b/`.
- **User decisions 2026-11-20, design fixes** (through the coordinating session, after Phase 5):
  1. Fix the design findings in the KiCad design, but **leave the component VALUES as they are**
     (R13, R22, R27, R30, R34, R51, Q4; the R34 / R51 swap of finding 21; finding 5: all unchanged).
     The boards will be redesigned; the aim is a clean starting point.
  2. **Finding 4** (relay flyback diodes, anode on H4): no change unless the real board shows otherwise.
  3. **Finding 14**: relabel the G5V-2 relay symbol to Omron's pin / pole names (electrically
     identical, no copper change); every pin stays on its net; compare / check_board / ipc356_diff must
     still pass.
  4. **Findings 16 and 20**: REMOVE the dangling / zero-length Proteus track pieces with
     `REMOVED_TRACKS` (**reverses Phase 5 decision 3**); the checks accept recorded removals.
  5. Generation stops later (after the shared-tool migration); the board stays generated for now.
- Design fixes (agent's choices, no user decision needed): Omron names `COIL16 / COIL1 / COM13 / NC11 /
  NO9 / COM4 / NC6 / NO8` as pin names with the Proteus ids kept as pin numbers; KiCad units 2 / 3
  swapped and the coil placed unrotated so the sheet wiring stays where it was; all 9 short pieces of
  findings 16 / 20 removed (not the 0.278 mm draw outside finding 20); new check
  `tools/check_removed_tracks.py`; the `make_pcb.sh --check` step-failure fix.

- Sheet names (no title blocks in the PDF): Input stage / Second stage / EQ stage / Tone stacks /
  Supply filter, chosen by the agent from the content; the user can rename them (only
  `p2k_config.py`, before `make_skeleton`).
- KiCad refdes: `-` → `_` (`GTR_IN`, `POT1_1`, ...) and the single letters `A`-`D` → `PAD_A`-`PAD_D`
  (agent's choice; `C`/`D` would read as capacitor / diode references, `A`/`B` renamed for
  consistency).
- The October 2010 export is the baseline (user, before Phase 0); the June differences are listed
  above for reference only.
- Phase 1 preparation (agent's choices, no user decision needed): 12AX7 from KiCad's ECC83 with
  units 1/2 swapped (unit A = pins 1-3, B = 6-8, C = heater 4/5/9); pin 9 `passive` + no-connect
  flag (not `no_connect` type, p2k candidate 5); G5V-2 from KiCad's G5V-2_Split (coil and the two
  poles as units, so the drawing can follow the PDF), Proteus pin names hidden; J112 = KiCad
  Q_NJFET_DSG (pins already D/S/G = 1/2/3); a second polarized-capacitor symbol `C_Polarized_12`
  for the pins 1/2 electrolytics; all 47 terminals one symbol `PIN` with value `TERMINAL`; values
  = schematic values incl. Q4 `NADA` (finding 1) and the six resistors whose layout value differs
  (finding 7); named nets keep the IPC spelling (upper case) where the PDF writes lower case.
- Phase 1 transcription (agent's choices, no user decision needed): triode B of each 12AX7 drawn
  mirrored and the heater as a separate unit away from the triodes; relay poles at rotation 270
  with COM on the left; relay blocks wider than in the PDF; `tools/compare.py` wrapper instead of
  the shared compare (p2k candidate 9); schematic renders not committed.
- Phase 2 (agent's choices, no user decision needed): KiCad pad sizes (`FOOTPRINT_PAD_SIZES =
  "kicad"`, the playbook default) with the pad centres on the Proteus positions; derived footprints
  where KiCad has the package at another pitch or with other pin ids (2 W resistor, 22n / 100n Xicon,
  Orange Drop, CAP20, the three electrolytic families, DO-41, TO-92, G5V-2); the Orange Drop body is
  KiCad's 16.5 x 7 mm box (Proteus silk 15.1 x 6.7), the 100n Xicon KiCad's 24 x 7 (silk 23.1 x 6.0);
  built from the IPC pads: noval socket (pitch circle differs from KiCad's grid footprint) and the
  fly-lead terminal; the noval footprint keeps the Proteus pin ids and the top side (finding 13);
  the relay renumbering that fits without a mirror (finding 14); footprint names describe the
  Proteus geometry (`_P9.70mm`, `_PM` = pads +/-, `_Pin2Plus`, `_AK`, `_ProteusPins`, `_PCD21.00mm`);
  `reports/footprint_*.csv` and `reports/pin_order/` committed (as the pilot).
- **User decisions 2026-11-20** (through the coordinating session, after Phase 2):
  1. **The noval sockets U1-U3 are mounted on the bottom (solder) side** (finding 13): the Proteus
     pattern is correct for a socket on the solder side. As on the power amp, moving the socket
     footprints to B with the standard noval numbering is **Phase 5** work (silk / courtyard / 3D
     model; copper unchanged). Phase 3 keeps the Proteus ids on the top side.
  2. **Drills: keep the KiCad drills everywhere**, including RLY1-RLY5 (0.7 vs Proteus 1.143 mm),
     C1/C5/C7/C10 (1.0 vs 1.143), the 14 Orange Drops (1.1 vs 1.143) and C4/C14 (0.75 vs 0.762).
     Recorded as `DRILL_SMALLER` in `p2k_config.py` (`(1.143, 0.7)`, `(1.143, 1.0)`, `(1.143, 1.1)`,
     `(0.762, 0.75)`, reason "user decision 2026-11-20"), so the Phase 4 checks accept them.
  3. **Pad sizes**: only if the Phase 3 DRC forces a change: stop and report (unchanged rule).
- Phase 3 (agent's choices, no user decision needed): `PCB_RULES` from the measured Proteus gaps
  (clearance 0.38, Default netclass via = the Proteus via 1.27 / 0.508), `PCB_THICKNESS` 1.6 mm (as
  the pilot); mounting holes renamed H101-H113 (`tools/rename_holes.py`, p2k candidate 18);
  `place_refdes` in `make_pcb.sh` as the pilot; `DRC_ACCEPTED` = courtyards_overlap and
  pth_inside_courtyard (Proteus placement).
- **User decision 2026-11-20** (through the coordinating session, Phase 3): **TO-92 pad 1 = option
  (a), a ROUND pad at the KiCad size 1.5 mm on Q1-Q9** (instead of KiCad's square pin-1 pad, which
  was 0.122 mm from a track on Q4 and Q6; round: 0.433). Applied in `tools/gen_footprints.py`
  (`pad_shapes`, p2k candidate 22); drills stay KiCad's 0.8 mm. Pin 1 (the outline is symmetric) is
  marked by a filled 0.2 mm dot added on silk and fab, same position as the PI / FX loop board (coordinating session, for
  consistency; "Phase 3").
- Phase 3 finish (agent's choices): the DRC step in `check_all.sh` with the existing `DRC_ACCEPTED`
  (courtyards_overlap, pth_inside_courtyard).
- Phase 4 (agent's choices, no user decision needed): the round trip runs through the board-local
  wrapper `tools/roundtrip.py` (the 2 October vias expected to be missing from the 2010 Excellon,
  by position); `reports/roundtrip/` (report + overlay PNGs) committed as on the pilot; no
  `ROUNDTRIP` overrides (defaults: raster 0.025, tolerance 0.05 mm).
- **User decisions 2026-11-20 for Phase 5** (through the coordinating session):
  1. Noval sockets U1-U3 to the **bottom side with the standard numbering** (already decided): the
     footprint is built mirrored as the pilot did (a plain pcbnew Flip mirrors the pads and fails the
     checks).
  2. Reference texts placed automatically (`place_refdes` in `make_pcb.sh`, as the pilot).
  3. The short / dangling Proteus track pieces (findings 16 and 20) are kept as drawn; no
     `REMOVED_TRACKS`. **Reversed 2026-11-20** (design fixes, decision 4).
  4. The TO-92 pin-1 dot is kept.
  5. Body graphics, pad sizes, sheet names and the 1.6 mm thickness are kept.
  6. The board stays generated; stopping generation is the user's call at the first hand edit.
- Phase 5 (agent's choices, no user decision needed): the pilot's `bottom` spec key and
  `build_library` wrapper; `bottom_side_noval()` in `check_pin_order.py`; `DRC_ACCEPTED` texts updated
  (36 courtyards_overlap, 16 pth_inside_courtyard); the PI / FX loop board's `check_drill_smaller.py`
  and joined-N/C checks ported (`compare.py`, `erc.sh`), `check_drill_smaller` added to `check_all.sh`.
- ~~Still open for the user: the values of R13, R22, R27, R30, R34, R51 and Q4~~ - answered
  2026-11-20: the values stay as they are (design fixes, decision 1).
