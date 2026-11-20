#!/usr/bin/env bash
# Phase 3 build chain of kicad/tube_preamp.kicad_pcb: the shared `p2k make_pcb [--check]` with the
# default PCB_STEPS (build_pcb with the holes H101-H113 from HOLE_START, gerber_to_tracks with the 14
# vias and REMOVED_TRACKS, assign_nets, place_refdes; no pours on this board). Kept as the entry
# point that tools/check_all.sh and proteus2kicad's tools/regress.sh call (run from the repo root).
exec tools/p2k/bin/p2k make_pcb "$@"
