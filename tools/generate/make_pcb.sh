#!/usr/bin/env bash
# FROZEN HISTORY - DO NOT RUN (STATUS.md "Generation stopped 2026-11-20").
# Phase 3 build chain of kicad/tube_preamp.kicad_pcb: the shared `p2k make_pcb [--check]` with the
# default PCB_STEPS (build_pcb with the holes H101-H113 from HOLE_START, gerber_to_tracks with the 14
# vias and REMOVED_TRACKS, assign_nets, place_refdes; no pours on this board).
# Since 2026-11-20 the committed kicad/tube_preamp.kicad_pcb is the source, edited in KiCad; a run
# would overwrite the hand edits with the Proteus copper. It refuses to run without the explicit
# first argument --force-regenerate (run from the repo root).
if [ "${1:-}" != "--force-regenerate" ]; then
    echo "make_pcb.sh: generation stopped 2026-11-20 (STATUS.md); the board is edited in KiCad." >&2
    echo "make_pcb.sh: refusing to regenerate kicad/tube_preamp.kicad_pcb without --force-regenerate" >&2
    exit 2
fi
shift
cd "$(dirname "$0")/../.."
exec tools/p2k/bin/p2k make_pcb "$@"
