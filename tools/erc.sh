#!/usr/bin/env bash
# ERC of the project schematic; fails on ERC errors, on footprint_link_issues warnings (a Footprint
# field that names a missing library / footprint, e.g. without kicad/fp-lib-table) and on the warning
# no_connect_connected (a pin with a no-connect flag that is wired: for this conversion a netlist
# error; ported in Phase 5 from the PI / FX loop board, as the power amp pilot). Other warnings are
# listed only. Full report: reports/erc.rpt
set -u
cd "$(dirname "$0")/.."
# Optional arguments (negative tests on a scratch copy): tools/erc.sh [root schematic [report file]]
sch=${1:-kicad/tube_preamp.kicad_sch}
rpt=${2:-reports/erc.rpt}
mkdir -p "$(dirname "$rpt")"
tools/p2k/bin/kicad-cli sch erc --severity-all -o "$rpt" "$sch" >/dev/null || exit 1
errs=$(grep -c '; error' "$rpt")
warns=$(grep -c '; warning' "$rpt")
echo "erc: $errs errors, $warns warnings ($rpt)"
links=$(grep -c "footprint_link_issues" "$rpt")
[ "$links" -eq 0 ] || echo "erc: $links footprint_link_issues (Footprint fields vs fp-lib-table)"
ncc=$(grep -c '^\[no_connect_connected\]' "$rpt")
[ "$ncc" -eq 0 ] || { echo "erc: $ncc no_connect_connected (a no-connect pin is wired):"; grep -A3 '^\[no_connect_connected\]' "$rpt"; }
[ "$errs" -eq 0 ] && [ "$links" -eq 0 ] && [ "$ncc" -eq 0 ]
