#!/bin/bash
# drc.sh BOARD : kicad-cli DRC (zones refilled) -> BOARD.drc.json, summary by type
B=$1; CLI=/home/jari/dev/tube_preamp_kicad/tools/p2k/bin/kicad-cli
# graded against the project's own rules (a routing step may have rewritten the sibling .kicad_pro)
P="$(cd "$(dirname "$0")" && pwd)/../kicad/tube_preamp_revb"
for x in pro dru; do cp "$P.kicad_$x" "${B%.kicad_pcb}.kicad_$x"; done
$CLI pcb drc --refill-zones --format json --severity-error -o "${B%.kicad_pcb}.drc.json" "$B" >/dev/null 2>&1
python3 - "${B%.kicad_pcb}.drc.json" "${2:-}" <<'PY'
import json,sys,collections
d=json.load(open(sys.argv[1])); c=collections.Counter(v["type"] for v in d["violations"])
print("violations:", dict(c), "| unconnected:", len(d.get("unconnected_items",[])))
if sys.argv[2]:
    for v in d["violations"]:
        if sys.argv[2] in v["type"]: print(" ", v["description"][:60], "|", " / ".join(i["description"][:70] for i in v["items"]))
PY
