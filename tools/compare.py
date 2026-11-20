#!/usr/bin/env python3
"""p2k compare_netlists with a type-safe sort key (board-local wrapper, STATUS.md p2k candidates;
same wrapper as in the PI / FX loop board repo).

p2k.compare_netlists.natkey() returns mixed lists (['PRES', 1, ''] for PRES1), and pinkey() appends
'-' and the pin: the terminal PRES (['PRES', '-', 1]) against PRES1 (['PRES', 1, '', '-', 1])
compares the str '-' with the int 1 and sorted() raises TypeError as soon as both parts are drawn
(sheet 3: PRES and PRES1-PRES3). Here every token becomes a (kind, value) pair, so numbers and
text never meet. Same arguments and output as `p2k compare_netlists` (--sheet N, --allow-missing,
-v)."""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "p2k"))
from p2k import compare_netlists as cn  # noqa: E402


def natkey(s):
    return [(0, int(t), "") if t.isdigit() else (1, 0, t) for t in re.split(r"(\d+)", str(s))]


def pinkey(rp):
    return natkey(rp[0]) + [(1, 0, "-")] + natkey(rp[1])


cn.natkey, cn.pinkey = natkey, pinkey
sys.exit(cn.main())
