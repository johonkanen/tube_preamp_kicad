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
# ERC: fails on errors and on the ERC_FATAL_WARNINGS no_connect_connected / footprint_link_issues
step "ERC" tools/p2k/bin/p2k erc
# compare_netlists with the strict nc_joined (no two no-connect pins in one unconnected-(...) net)
# and net_names (on by default, D-Z). All 5 sheets are drawn: no --allow-missing.
step "Netlist comparison vs IPC" tools/p2k/bin/p2k compare_netlists
# Phase 2: footprints
step "Footprint library, map and fp-lib-table up to date" python3 tools/gen_footprints.py --check
step "Footprints vs IPC pad geometry" tools/p2k/bin/kipy -m p2k.check_footprints --pcbnew
step "Pin order vs unmoved KiCad base footprints" tools/p2k/bin/kipy -m p2k.check_pin_order
# Phase 3: PCB (p2k make_pcb: build_pcb with HOLE_START = 101, gerber_to_tracks with the 14 vias,
# assign_nets, place_refdes; no pours)
step "PCB rebuilt from schematic + gerbers, up to date" tools/make_pcb.sh --check
step "Board pads, vias, holes vs IPC (position, size, nets 1:1)" tools/p2k/bin/kipy -m p2k.check_board
step "Board copper connectivity (KiCad geometry)" tools/p2k/bin/kipy -m p2k.assign_nets --check
# DRC: 0 shorts / unconnected / parity, no unaccepted errors (DRC_ACCEPTED in p2k_config.py)
step "DRC with schematic parity" tools/p2k/bin/p2k drc
# Phase 4: independent verification from KiCad's own exports (kicad-cli ipcd356, gerbers + drills).
# DRILL_SMALLER with pad sets: the smaller KiCad drills are exactly the 80 decided holes (both tools).
# The round trip reads the June-2010 inch Excellon (DRILL_EXCELLON) and expects the 2 October-2010
# vias to be missing from it (EXCELLON_MISSING; STATUS.md "Phase 4").
step "IPC-D-356 from the board vs Proteus (pads, vias, holes, nets)" tools/p2k/bin/p2k ipc356_diff
step "Gerber round trip vs Proteus (copper XOR, coverage, drills, 2010 Excellon)" tools/p2k/bin/p2k gerber_roundtrip --check
# Design fixes 2026-11-20: the Proteus track pieces of findings 16 / 20 are not built (REMOVED_TRACKS);
# the removed pieces are exactly the decided ones and none is on the board.
step "Removed Proteus track pieces are exactly the 9 decided ones" python3 tools/check_removed_tracks.py

echo
[ $fail -eq 0 ] && echo "ALL CHECKS PASSED" || echo "SOME CHECKS FAILED"
exit $fail
