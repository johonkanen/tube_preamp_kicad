#!/bin/bash
# Placement: rev_b/kicad board from tools/make_pcb.py (fixed parts placed, the rest parked) ->
# KiCadRoutingTools place_simple with groups.json / intent.json (make_groups.py) -> build/placed.kicad_pcb.
# Deterministic for a given seed. Run from anywhere; needs ~/dev/KiCadRoutingTools.
set -euo pipefail
L="$(cd "$(dirname "$0")" && pwd)"; B="$L/build"; KRT=~/dev/KiCadRoutingTools; PY="$KRT/.venv/bin/python -X utf8"
SEED=${SEED:-7}
mkdir -p "$B"
cp "$L/../kicad/tube_preamp_revb."{kicad_pcb,kicad_pro,kicad_dru} "$B/"
cd "$KRT"
# Q502 on its drain pour, Q503 in the pour's F cut-out (draw_pours.py), both held
$PY py_placer/place_pose.py "$B/tube_preamp_revb.kicad_pcb" "$B/locked.kicad_pcb" set Q502 138.5 24.0 --rot 0 \
    set Q503 146.0 31.5 --rot 0 lock Q502 Q503 V1 V2 V3 \
    J101 J102 J401 J501 J502 J503 J504 J505 J506 J507 H101 H102 H103 H104 H105 H106 H107 H108 H109 H110 H111 H112 H113 >/dev/null
$PY py_tools/check_floorplan.py "$B/locked.kicad_pcb" --emit-intent "$B/emitted_intent.json" >/dev/null
python3 "$L/make_groups.py" "$B/emitted_intent.json"
$PY py_placer/place_simple.py "$B/locked.kicad_pcb" "$B/placed.kicad_pcb" --groups "$L/groups.json" \
    --intent "$L/intent.json" --seed "$SEED" --halo-coef 0.6 --json "$B/placed.json" | grep -v "^  " | tail -3
