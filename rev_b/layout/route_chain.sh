#!/bin/bash
# Routing chain: build/placed.kicad_pcb (place.sh) -> build/route/NN_*.kicad_pcb -> build/routed.kicad_pcb.
# One KRT step per net group (routing.json), each step's nets locked before the next.
#   ./route_chain.sh [FROM [LAST]]   (step numbers; resumes from build/route/<FROM-1>_*.kicad_pcb)
set -euo pipefail
L="$(cd "$(dirname "$0")" && pwd)"; R="$L/build/route"; S=~/.claude/skills/kicad-agentic-routing/scripts
export ROUTING_CONFIG="$L/routing.json" KICAD_PYTHON=/home/jari/dev/tube_preamp_kicad/tools/p2k/bin/kipy
FROM=${1:-1}; LAST=${2:-99}
mkdir -p "$R"
prev() { ls "$R"/$(printf %02d $(( $1 - 1 )))_*.kicad_pcb 2>/dev/null | head -1 || true; }
step() {   # step N NAME GROUP [route.py opts]
    local n=$1 name=$2 grp=$3; shift 3
    [ "$n" -lt "$FROM" ] || [ "$n" -gt "$LAST" ] && return 0
    local in; in=$(prev "$n")
    local out="$R/$(printf %02d "$n")_$name.kicad_pcb"
    echo "== $n $name ($grp)"
    python3 -I "$S/route_step.py" "$in" "$out" "$grp" "$@"
    source "$S/kenv.sh"; kpy "$S/lock_tracks.py" "$out" lock "$grp" >/dev/null
}
if [ "$FROM" -le 1 ] && [ "$LAST" -ge 1 ]; then
    for x in pro dru; do cp "$L/../kicad/tube_preamp_revb.kicad_$x" "$L/build/placed.kicad_$x"; cp "$L/../kicad/tube_preamp_revb.kicad_$x" "$R/00_heater_drawn.kicad_$x"; done
    rm -f "$R"/0[1-9]_*
    K=/home/jari/dev/tube_preamp_kicad/tools/p2k/bin/kipy
    $K "$L/draw_heater.py" "$L/build/placed.kicad_pcb" "$R/00_heater_drawn.kicad_pcb" 2>&1 | grep -v "memory leak"
    $K "$L/draw_pours.py" "$R/00_heater_drawn.kicad_pcb" "$R/00_heater_drawn.kicad_pcb" 2>&1 | grep -v "memory leak"
fi
step 1 heater heater --via-cost 200
step 2 hv hv
step 3 mv mv
step 4 v90 v90
step 5 ctl ctl --grid-step 0.05
step 6 audio audio
step 7 leftover ctl,audio --max-iterations 20000000 --layer-costs 1 1
# GNDA pours on F and B, pads joined by vias, the two pours stitched (KRT route_planes)
if [ 8 -ge "$FROM" ] && [ 8 -le "$LAST" ]; then
    echo "== 8 gnda pours"
    in=$(prev 8); out="$R/08_gnda.kicad_pcb"
    for x in pro dru; do cp "$L/../kicad/tube_preamp_revb.kicad_$x" "${out%.kicad_pcb}.kicad_$x"; done
    ( cd ~/dev/KiCadRoutingTools && KICAD_PYTHON=$KICAD_PYTHON .venv/bin/python -X utf8 py_router/route_planes.py "$in" "$out" \
        --nets GNDA GNDA --plane-layers F.Cu B.Cu --stitch-vias --stitch-pitch 10 --via-size 0.8 --via-drill 0.4 \
        --escalation board --no-fix-drc-settings > "${out%.kicad_pcb}.log" 2>&1 ) || { tail -20 "${out%.kicad_pcb}.log"; exit 1; }
    grep -E "^(Total|Planes|.*islands?|.*unconnected)" "${out%.kicad_pcb}.log" | tail -8 || true
fi
# join the pours' islands (KRT repair_planes), then drop what stays floating
if [ 9 -ge "$FROM" ] && [ 9 -le "$LAST" ]; then
    echo "== 9 gnda repair"
    in=$(prev 9); out="$R/09_repair.kicad_pcb"
    for x in pro dru; do cp "$L/../kicad/tube_preamp_revb.kicad_$x" "${out%.kicad_pcb}.kicad_$x"; done
    ( cd ~/dev/KiCadRoutingTools && KICAD_PYTHON=$KICAD_PYTHON .venv/bin/python -X utf8 py_router/repair_planes.py "$in" --output "$out" \
        --nets GNDA GNDA --plane-layers F.Cu B.Cu --via-size 0.8 --via-drill 0.4 --escalation board --no-fix-drc-settings > "${out%.kicad_pcb}.log" 2>&1 ) || { tail -20 "${out%.kicad_pcb}.log"; exit 1; }
    grep -E "JSON_SUMMARY" "${out%.kicad_pcb}.log" | cut -c1-300 || true
    $KICAD_PYTHON "$L/finalize.py" "$out" "$out" 2>&1 | grep -v "memory leak"
    cp "$out" "$L/build/routed.kicad_pcb"; for x in pro dru; do cp "${out%.kicad_pcb}.kicad_$x" "$L/build/routed.kicad_$x"; done
fi
