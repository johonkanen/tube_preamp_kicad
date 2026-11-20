#!/usr/bin/env python3
"""p2k gerber_roundtrip with the two October-2010 vias expected to be missing from the 2010 Excellon
(board-local wrapper, STATUS.md "p2k candidates" 3; same arguments and output as
`p2k gerber_roundtrip`: --check, --kicad-dir DIR, --keep).

p2k_config.py DRILL_EXCELLON is the June 2010 fab drill file (converted to metric by
tools/excellon_metric.py). The baseline is the October 2010 layout, which added two vias
(STATUS.md "Phase 0": Q6-3 moved from net J1 to J4, and the PRE-GND reroute). The shared
compare_excellon() requires the Excellon file and the drill gerber to match 1:1, so it reports
those two via drills as "not in the Excellon file". This wrapper

  - calls the shared compare_excellon() unchanged,
  - removes exactly the errors for EXPECTED_NOT_IN_EXCELLON (a ViaDrill flash of the listed
    diameter within 0.01 mm of the listed position, each at most once) and notes them in the report,
  - adds an error for every listed via the tool did NOT report missing (then the Excellon file or
    the layout is not the one this list was written for),
  - leaves every other Excellon / drill error in place, so anything else still fails --check.
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2k"))
from p2k import gerber_roundtrip as gr  # noqa: E402

# (x, y, drill) in the IPC / gerber frame, mm: the vias added in October 2010.
EXPECTED_NOT_IN_EXCELLON = [
    (33.02, -31.115, 0.508, "via on J4: Q6-3 top track -> bottom track to Q9-3 (October edit)"),
    (-29.337, -42.545, 0.508, "via on PRE-GND: joins the bottom track end to the top PRE-GND track (October reroute)"),
]
POS_TOL = 0.01
MISSING_RE = re.compile(r"excellon: drill gerber ViaDrill ([\d.]+) mm at \(([-\d.]+), ([-\d.]+)\) not in the Excellon file")

_shared = gr.compare_excellon


def compare_excellon(gerber_drills, report):
    errors = _shared(gerber_drills, report)
    found, rest = set(), []
    for e in errors:
        m = MISSING_RE.fullmatch(e)
        i = None
        if m:
            d, x, y = (float(v) for v in m.groups())
            i = next((k for k, (ex, ey, ed, _) in enumerate(EXPECTED_NOT_IN_EXCELLON)
                      if k not in found and abs(d - ed) < 1e-6 and math.hypot(x - ex, y - ey) < POS_TOL), None)
        if i is None:
            rest.append(e)
        else:
            found.add(i)
    for k, (x, y, d, why) in enumerate(EXPECTED_NOT_IN_EXCELLON):
        if k in found:
            report.append(f"   expected, not an error: drill gerber ViaDrill {d} mm at ({x}, {y}) not in the 2010 Excellon file: {why}")
        else:
            rest.append(f"excellon: the October via {d} mm at ({x}, {y}) was expected to be missing from the Excellon file, "
                        "but the tool did not report it (tools/roundtrip.py EXPECTED_NOT_IN_EXCELLON)")
    report.append(f"   {len(found)} of {len(EXPECTED_NOT_IN_EXCELLON)} expected October vias missing from the Excellon file "
                  f"(tools/roundtrip.py), {len(rest)} other mismatches")
    return rest


gr.compare_excellon = compare_excellon
sys.exit(gr.main())
