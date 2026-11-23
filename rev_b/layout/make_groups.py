#!/usr/bin/env python3
"""Placement groups and floorplan intent for KiCadRoutingTools' place_simple (rev B preamp).

Writes rev_b/layout/groups.json and rev_b/layout/intent.json from the emitted intent (argv[1])
plus the zones and keep-outs below. Board coordinates (rev A frame): x -195.4..187.4,
y -26.2 (front) .. 45.7 (rear). Layout decisions: rev_b/README.md, "Layout".
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
X0, X1, Y0, Y1 = -195.357, 187.433, -26.175, 45.730
STRIP = Y0 + 15.0
# heater pair (draw_heater.py): front run y, rearward run x; pin 4 x of each socket
HT_Y, HT_X = -21.0, 87.5
PIN4 = {"V1": -159.34, "V2": -20.28, "V3": 63.54}
POUR = (127.0, 12.5, 152.0, 37.0)      # Q502 drain pour, F and B (25 x 24.5 mm = 6.1 cm2)

def rng(p, a, b): return [f"{p}{i}" for i in range(a, b + 1)]

# name, refs, zone [x0, y0, x1, y1], near, why
G = [
 ("v1a", ["J101", "J102", "R101", "R102", "R103", "R104", "R105", "C101", "Q101", "R106", "R107", "C102",
          "C103", "Q102", "R108", "R109", "C104"],
  [X0, Y0, -138, Y1], ["v1b", "in_mix"], "V1a input stage: grid stopper at pin 2, cathode and its two bypass switches, BP1 decoupling"),
 ("bplus", ["R509", "C504", "R510", "C505", "R511", "C506", "R512", "C507"],
  [-175, 24, 112, Y1], ["supply"], "B+ dropping resistors and decoupling caps in one row along the rear edge, as rev A (BP at the regulator end, BP1 at V1)"),
 ("v1b", ["R203", "R206", "C203", "C201", "Q201", "R204", "R205", "C202", "R202"],
  [-175, -5, -125, Y1], ["v1a", "in_mix", "s2"], "V1b cathode with its bypass switch, plate load, BP2 decoupling"),
 ("in_mix", ["C105", "C108", "R119", "R110", "Q103", "R111", "C107", "R419", "R112", "R113", "Q104", "R114", "C110", "R420",
             "R115", "R116", "Q105", "R117", "C112", "R421", "R118", "R201", "C111"],
  [-150, -6.3, -100, 30], ["v1a", "v1b"], "the three pre-gain coupling caps off P1, the channel JFET mutes and mixing resistors to GX2 (V1 pin 7)"),
 ("ch_clean", ["C106"] + rng("C", 303, 306) + rng("R", 303, 306), [-136, Y0, -88, -6.3], [], "clean bright cap and tone stack in front of J504"),
 ("ch_crunch", ["C109"] + rng("C", 308, 311) + rng("R", 310, 313), [-87, Y0, -36, -6.3], [], "crunch bright cap and tone stack in front of J505"),
 ("ch_lead", rng("C", 313, 316) + rng("R", 317, 320), [2, Y0, 48, -6.3], [], "lead tone stack in front of J506"),
 ("s2", ["K201", "K202", "C204", "C205", "C206", "C207", "R207", "R208", "R209", "R210", "R211", "R212"],
  [-125, 4, -30, Y1], ["v1b", "v2"], "V1b plate: bright relay, coupling select relay and the 470k/470k divider to GX2B"),
 ("v2", ["K203", "C208", "R213", "R214", "R215", "R216", "C209", "C210", "R217", "R218", "C211", "R219", "R220",
         "R221", "R222", "R223", "R224", "R225", "R226", "R227", "C212", "C213", "C214", "C215", "Q202", "Q203",
         "C216", "K204", "R228", "C301"],
  [-60, -6.3, 50, Y1], ["s2", "cf"], "V2: stage select relay, V2a and V2b with cathode switches, bright relay on P3, BP3 decoupling"),
 ("cf", ["R301", "R302", "C302", "C508", "R514", "R519", "R513"],
  [35, -6.3, 105, Y1], ["v2", "tone_mix", "v3b"], "V3a cathode follower: grid bias (VB90 divider), cathode resistor, output cap to SIN; BP4 decoupling"),
 ("tone_mix", ["R307", "Q301", "R308", "C307", "R422", "R309", "R314", "Q302", "R315", "C312", "R423", "R316",
               "R321", "Q303", "R322", "C317", "R424", "R323", "R324"],
  [40, -19.6, 86, 30], ["cf", "v3b"], "presence-wiper mutes and mixing resistors to GX4 (V3 pin 7)"),
 ("v3b", ["R325", "R326", "C318", "C319", "R327", "R328", "Q304", "C320", "R329", "R425", "C509", "R517"],
  [60, -6.3, 140, Y1], ["cf", "tone_mix"], "V3b plate load, cathode, output divider, output mute, J507 shield RC"),
 ("supply", ["Q501", "Q502", "Q503", "C501", "C502", "C503", "D501", "D502", "D503", "D504", "D505", "R501", "R502",
             "R503", "R504", "R505", "R506", "R507", "R508", "R518", "R520", "R521", "R522", "R523", "R524", "R525", "R526",
             "R515", "R516"],
  [95, -8, X1, 40], ["v3b"], "B+ regulator (430 V raw from J501), bleeder, heater reference resistors"),
 ("control", rng("U", 401, 405) + rng("C", 401, 407) + rng("R", 401, 418) + ["R426"],
  [118, Y0, 176, 9.5], [], "control logic: port expander, JFET drive switches, relay driver; DGND island at J401"),
]

def main():
    intent = json.load(open(sys.argv[1]))
    groups = []
    for name, refs, zone, near, why in G:
        groups.append({"name": name, "role": "core", "refs": refs, "near": near, "side": "F", "why": why,
                       **({"edge": "S"} if name == "bplus" else {})})
    json.dump({"schema": 1, "board": "rev_b/kicad/tube_preamp_revb.kicad_pcb", "groups": groups},
              open(os.path.join(HERE, "groups.json"), "w"), indent=1)
    intent["blocks"] = [{"name": n, "refs": r, "zone": z, "side": "F", "note": w} for n, r, z, _, w in G]
    tall = ["C105", "C206", "C210", "C301", "C319", "C302", "C503", "C501", "C502", "C504", "C505", "C506", "C507",
            "C508", "C101", "C103", "C201", "C203", "C212", "C214", "C318", "K201", "K202", "K203", "K204", "Q502"]
    allrefs = [r for _, refs, _, _, _ in G for r in refs]
    short = [r for r in allrefs if r not in tall and not r.startswith(("V", "J"))]
    ko = [{"name": "front strip (<= 5 mm parts)", "rect": [X0, Y0, X1, STRIP], "sides": ["F"],
           "allow": short + ["H1*", "J101"], "why": "interfaces.md 12.2"},
          {"name": "pot pins", "rect": [-18.73, Y0, 179.0, Y0 + 4.0], "sides": ["F", "B"], "why": "front panel pot pins (README Layout)"}]
    holes = {"H101": (-189.87, -20.32), "H102": (183.13, -20.32), "H103": (-170.87, -15.82), "H104": (-31.86, -15.82),
             "H105": (52.13, -15.82), "H106": (-139.37, -12.82), "H107": (-0.86, -12.82), "H108": (82.14, -12.82),
             "H109": (-160.37, 9.68), "H110": (-20.86, 9.68), "H111": (63.13, 9.68), "H112": (-189.87, 40.68),
             "H113": (183.13, 40.68)}
    for h, (x, y) in holes.items():
        ko.append({"name": f"{h} copper keep-out", "circle": [x, y, 4.0], "sides": ["F", "B"], "allow": [h], "why": "standoff"})
    for j, (x0, x1) in (("J504", (-132.9, -91.1)), ("J505", (-82.9, -41.1)), ("J506", (4.1, 45.9))):
        ko.append({"name": f"{j} ribbon bend", "rect": [x0, STRIP, x1, -6.2], "sides": ["F"],
                   "allow": [r for r in allrefs if r not in ("C502", "C504", "C505", "C506", "C507")],
                   "why": "front panel ribbon bends up into the header (<= 20 / 38 mm)"})
    # Heater pair (draw_heater.py): broadside on F and B along the front edge at y HT_Y, rearward along
    # x HT_X to J502; spurs into each socket. Kept free of every part on F, of through-hole parts on B.
    for sides in (["F"], ["B"]):
        kw = {"sides": sides, "why": "heater pair (draw_heater.py)"}
        ko.append({"name": f"heater front run {sides[0]}", "rect": [-160.5, HT_Y - 1.4, HT_X + 1.4, HT_Y + 1.4], **kw})
        ko.append({"name": f"heater rear run {sides[0]}", "rect": [HT_X - 1.4, HT_Y - 1.4, HT_X + 3.6, 34.0], **kw})
        ko.append({"name": f"heater to J502 {sides[0]}", "rect": [HT_X - 1.4, 25.6, 106.0, 37.0], **kw})
    ko.append({"name": "in front of the heater run", "rect": [-160.5, Y0, HT_X + 3.6, HT_Y], "sides": ["F", "B"],
               "why": "the broadside heater pair walls it off on both layers"})
    for v, x4 in PIN4.items():
        ko.append({"name": f"{v} heater stubs", "rect": [x4 - 1.0, HT_Y, x4 + 7.5, -15.0], "sides": ["F"],
                   "why": "HTR1 stubs to pins 4, 5"})
    # Q502 drain pour (draw_pours.py): F and B, Q502 / Q503 only (Q503 sits in a cut-out of the F pour).
    ko.append({"name": "Q502 drain pour", "rect": list(POUR), "sides": ["F", "B"], "allow": ["Q502", "Q503"],
               "why": "regulator heat spreading, >= 6 cm2 per side (README Layout)"})
    intent["keepouts"] = ko
    json.dump(intent, open(os.path.join(HERE, "intent.json"), "w"), indent=1)
    print(len(allrefs), "parts in", len(G), "groups")

if __name__ == "__main__":
    main()
