#!/usr/bin/env bash
# Run every verification step. Exit status is non-zero if any step fails.
# Each phase adds its steps here (playbook principle 5, PLAN.md section 3).
# The tools are the proteus2kicad submodule in tools/p2k; board values in p2k_config.py.
set -u
cd "$(dirname "$0")/.."
[ -x tools/p2k/bin/p2k ] || { echo "tools/p2k missing: git submodule update --init"; exit 1; }
fail=0
step() { echo "== $1"; shift; "$@" || { echo "!! FAILED: $*"; fail=1; }; }

# Phase 0: environment and sources
step "KiCad environment" tools/p2k/bin/kipy -c "import pcbnew; v = pcbnew.GetBuildVersion(); print('pcbnew', v); assert v.startswith('10.0.7'), v"
step "IPC-D-356A parser self-check" tools/p2k/bin/p2k ipc356 --check
step "Gerber X2 export vs IPC (pads, vias, holes, drills, outline)" tools/p2k/bin/p2k check_sources
# Phase 1: schematic
step "Part map up to date" python3 tools/make_part_map.py --check
step "Symbol library up to date" python3 tools/gen_symbols.py --check
step "Symbol pin sets vs IPC" tools/p2k/bin/p2k check_symbols
step "ERC" tools/erc.sh
# tools/compare.py = p2k compare_netlists with a type-safe sort key (PRES next to PRES1-PRES3 crashes
# the shared tool: STATUS.md p2k candidate 9) and, since Phase 5, a check that no two no-connect pins
# share one unconnected-(...) net. All 5 sheets are drawn: no --allow-missing.
step "Netlist comparison vs IPC" python3 tools/compare.py
# Phase 2: footprints
step "Footprint library, map and fp-lib-table up to date" python3 tools/gen_footprints.py --check
step "Footprints vs IPC pad geometry" tools/p2k/bin/kipy -m p2k.check_footprints --pcbnew
step "Pin order vs unmoved KiCad base footprints" tools/p2k/bin/kipy tools/check_pin_order.py
# Phase 3: PCB (build_pcb, rename_holes, gerber_to_tracks with the 14 vias, assign_nets; no pours)
step "PCB rebuilt from schematic + gerbers, up to date" tools/make_pcb.sh --check
step "Board pads, vias, holes vs IPC (position, size, nets 1:1)" tools/p2k/bin/kipy -m p2k.check_board
step "Board copper connectivity (KiCad geometry)" tools/p2k/bin/kipy -m p2k.assign_nets --check
# DRC: 0 shorts / unconnected / parity, no unaccepted errors (DRC_ACCEPTED in p2k_config.py)
step "DRC with schematic parity" tools/p2k/bin/p2k drc
# Phase 4: independent verification from KiCad's own exports (kicad-cli ipcd356, gerbers + drills).
# The round trip runs through tools/roundtrip.py: the shared tool with the 2 October-2010 vias
# expected to be missing from the June-2010 Excellon (STATUS.md "Phase 4", p2k candidate 3).
step "2010 Excellon drill file converted to metric, up to date" python3 tools/excellon_metric.py --check
step "IPC-D-356 from the board vs Proteus (pads, vias, holes, nets)" tools/p2k/bin/p2k ipc356_diff
step "Gerber round trip vs Proteus (copper XOR, coverage, drills, 2010 Excellon)" python3 tools/roundtrip.py --check
# Phase 5: ipc356_diff / gerber_roundtrip accept DRILL_SMALLER by diameter pair only; this board-local
# check (ported from the PI / FX loop board) requires the smaller drills to be exactly the decided pads.
step "Smaller KiCad drills are exactly the 80 decided holes" tools/p2k/bin/kipy tools/check_drill_smaller.py

echo
[ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
