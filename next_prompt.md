# Next prompt

Ready-to-paste prompt for the next agent session. Replaced at the end of every session.

```
Convert the Proteus board in /home/jari/dev/tube_preamp_kicad to KiCad 10: Phase 0 (skeleton and inventory).

Read, in this order: PLAN.md, STATUS.md, tools/p2k/CONVERSION_PLAYBOOK.md (sections 1-3 and 5),
tools/p2k/README.md (the p2k_config.py keys), README.md. The finished reference conversion is
~/dev/tube_psu_kicad (same tools): read its p2k_config.py, tools/check_all.sh and STATUS.md
"Phase 0" for how it was done. Read it only; don't change it.

Do Phase 0 as the playbook and PLAN.md section 3 describe:
- inventory the sources (gerber layers, pours, drills, IPC counts) and correct PLAN.md section 1;
- render the PDF pages (build/tmp or reference/), take the sheet names from the title blocks;
- complete p2k_config.py: SHEETS, truncated-refdes table, KiCad refdes map (references with spaces,
  '+', ''' or dots, single-letter pads like C/D, names starting with a sign), net aliases, expected
  IPC counts, copper layers, drills, outline;
- run tools/p2k/bin/p2k ipc356 (writes reference/) with --check, and p2k check_sources;
- create tools/check_all.sh with those steps and make it pass.

Rules (PLAN.md section 5): don't change tools/p2k or its pin (board-local workarounds, noted in
STATUS.md "p2k candidates"); don't touch other repos; report design findings, don't fix them;
temporary files in build/tmp; never run the KiCad AppImage with --version (use tools/p2k/bin/kipy and
tools/p2k/bin/kicad-cli). At the end: STATUS.md updated (Phase 0 result, check output, findings),
next_prompt.md replaced with the Phase 1 preparation prompt, commit and push.
```
