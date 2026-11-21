#!/usr/bin/env python3
"""Initial JLCPCB BOM for the rev B preamp (draft, footprints not yet assigned in the schematic).

Usage: python3 -I rev_b/tools/make_bom.py        (from the repo root; needs network)
Writes rev_b/bom/bom_jlcpcb.csv (Comment, Designator, Footprint, LCSC Part #: the columns
tools/jlc/stock_check.py reads) and rev_b/bom/README.md (the table with stock, price and notes).

Each line below names the references, the value, the package chosen from the voltage and power the
part sees, a JLC search keyword and substrings the hit must contain. Selection: a basic part with
orderable stock (canPresaleNumber) for 10 boards if there is one, otherwise the extended part with
stock for 10 boards, minimum purchase within one board's need, then preferred, then cheapest.
pick= forces a C-number. The search goes through JLC's public web API (rev_b/tools/jlc, jlc-tools).
"""
import csv, json, os, re, sys, time, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'jlc'))
import jlc_search  # noqa: E402
OUT = os.path.join(HERE, '..', 'bom')
BOARDS = 10
def rr(s):
    out=[]
    for p in s.split(','):
        p=p.strip()
        m=re.match(r'([A-Z]+)(\d+)-[A-Z]*(\d+)$',p)
        if m: out+= [f"{m[1]}{i}" for i in range(int(m[2]),int(m[3])+1)]
        elif p: out.append(p)
    return out
ITEMS=[]
def add(refs,val,pkg,kw,must=(),note='',lib_ok=True,pick=None):
    ITEMS.append(dict(refs=rr(refs),value=val,pkg=pkg,kw=kw,must=list(must),note=note,pick=pick))
def res(refs,val,pkg,kind='thick',note='',pick=None):
    v=val.replace('k','kΩ').replace('M','MΩ') if val[-1] in 'kM' else val+'Ω'
    must=[v, pkg] + (['Thin Film'] if kind=='thin' else []) + (['±1%'] if kind!='5%' else [])
    add(refs,val,{'0603':'R_0603','0805':'R_0805','1206':'R_1206','2512':'R_2512'}[pkg],
        f"{'thin film ' if kind=='thin' else ''}{v} {pkg}", must, note, pick=pick)
# ---- resistors
logic="R107,R109,R111,R114,R117,R205,R225,R227,R308,R315,R322,R329,R402-R425"
res(logic,"100k","0603",note="gate drive, pull-downs (LV)")
res("R401","10k","0603",note="RESET_N pull-up")
res("R426,R517","10","0603",note="ground / shield soft ties")
res("R110,R112,R113,R115,R116,R118,R303,R305,R307,R309,R310,R312,R314,R316,R317,R319,R321,R323","100k","0805",note="audio path, no DC")
res("R101,R106,R108,R201,R204,R214,R218,R224,R226,R301,R324","1M","0805",note="grid leaks, bleeds, CF grid (0 V across)")
res("R102","68k","0805",note="input grid stopper")
res("R211,R212,R217","470k","0805")
res("R220","680k","0805")
res("R304,R306,R311,R313,R318,R320","22k","0805",note="Baxandall")
res("R327","330k","0805",note="output attenuator (330k -> ~300k at the value pass)")
res("R328","220k","0805")
res("R104","2.7k","0805","thin",note="cathode (DC): thin film for low excess noise")
res("R105,R216,R223,R326","1.5k","0805","thin",note="cathode (DC)")
res("R203","10k","0805","thin",note="cathode (DC)")
res("R206,R222","4.7k","0805","thin",note="cathode (DC)")
res("R207-R210,R213,R219,R228","10M","1206",note="cap bleeds: up to ~300 V at power-up, 1206 for 200 V rating")
res("R507","820k","1206",note="regulator, ~100 V across")
res("R514","270k","1206",note="VB90 divider bottom, 90 V")
res("R511,R512","10k","1206",note="B+ decoupling (provisional)")
res("R515,R516","100","1206",note="heater artificial centre tap, 0.1 W each")
res("R501","330","1206",note="regulator (430 V nodes: 1206 for creepage)")
res("R502","1M","1206",note="regulator")
res("R503,R506","10k","1206",note="regulator")
res("R504","20","1206",note="regulator current sense")
res("R505","1k","1206",note="regulator")
res("R103,R202,R215,R221,R325","100k","2512",note="plate loads: 100-150 V, ~0.15 W (thick film; MELF / thin film preferred for noise if sourced)")
res("R302","47k","2512",note="CF cathode: 92 V, 0.18 W")
res("R509","3.3k","2512",note="B+ decoupling, ~8 mA: ~0.24 W (provisional)")
res("R510","6.8k","2512",note="B+ decoupling, ~5 mA: ~0.17 W (provisional)")
res("R508,R518","220k","2512",note="B+ bleed, 2 in series: 165 V and 0.12 W each (was one 470k)")
res("R513,R519","330k","2512",note="VB90 divider top, 2 in series: 115 V each (was one 680k; VB90 now 0.29 x BP4, about +2 %)")
# ---- capacitors
add("C102,C104,C107,C110,C112,C202,C213,C215,C307,C312,C317,C320","10n","C_0603","10nF 0603 X7R 50V",["10nF","0603","X7R"],"JFET / MOSFET gate RC (not audio)")
add("C401-C407,C509","100n","C_0603","100nF 0603 X7R 50V",["100nF","0603"],"decoupling, ground tie")
for refs,v,kw in [("C106,C109,C207,C305,C315","470p","470pF"),("C303,C313","560p","560pF"),("C310","120p","120pF"),
                  ("C311","820p","820pF"),("C308","2.2n","2.2nF"),("C306,C316","3.3n","3.3nF"),("C304,C314","5.6n","5.6nF")]:
    add(refs,v,"C_0805",f"{kw} 0805 C0G",[kw,"0805",("C0G","NP0")],"audio, low V: C0G")
add("C309","22n","C_1206","22nF 1206 C0G",["22nF","1206",("C0G","NP0")],"Baxandall bass cap: C0G")
add("C208,C211","100n","C_1206","100nF 1206 C0G",["100nF","1206",("C0G","NP0")],"relay-routed coupling, 0 V DC: C0G (film if not stocked)")
add("C209","680n","C_1206","680nF 1206 X7R 50V",["680nF","1206"],"S5 cathode bypass (~1.5 V): X7R for now, film preferred (audition)")
add("C204,C216","1n/630V","C_1206","1nF 1206 C0G 630V",["1nF","1206",("C0G","NP0")],"treble bleed from the plate: needs >= 630 V")
add("C205,C108","2.2n/630V","C_1206","2.2nF 1206 C0G 630V",["2.2nF","1206",("C0G","NP0")],"plate coupling: C108 is drawn as 2.2n without a voltage, it sits on P1 (needs 630 V)")
add("C111","4.7n/630V","C_1206","4.7nF C0G 630V",["4.7nF",("C0G","NP0")],"plate coupling (drawn without a voltage, sits on P1)")
add("C503","100n/630V","C_Rect P10mm (THT film)","100nF 630V film capacitor",["100nF","630V"],"B+ HF decoupling (no 630 V 1206 MLCC in stock)",pick="C2888191")
add("C105,C206,C210,C301,C319","22n/630V","C_Rect P10mm (THT film)","22nF 630V film capacitor",["22nF","630V"],"plate coupling: film. C105 is drawn as 22n without a voltage, it sits on P1")
add("C302","470n/250V","C_Rect P15mm (THT film)","470nF 400V film capacitor",["470nF"],"CF output coupling, 92 V DC: film >= 250 V")
add("C101,C103,C201,C203,C212,C214,C318","22u/25V","CP_Elec_5x5.4 (SMD)","22uF 35V electrolytic SMD",["22uF"],"cathode bypass, AC networks")
add("C501","2.2u/450V","CP_Radial D8 (THT)","2.2uF 450V electrolytic",["2.2uF","450V"],"regulator reference filter")
add("C502","47u/450V","CP_Radial D18 (THT)","47uF 450V electrolytic",["47uF","450V"],"B+ main reservoir")
add("C504-C507","22u/450V","CP_Radial D12.5 (THT)","22uF 450V electrolytic",["22uF","450V"],"per-stage B+ decoupling")
add("C508","10u/250V","CP_Radial D8 (THT)","10uF 250V electrolytic",["10uF","250V"],"VB90 decoupling (heater elevation option too)")
# ---- semis
add("D501-D503","130V 1W","D_SMA","1SMA5952B",["130V","SMA"],"regulator reference string (1.5 W rating)")
add("D504","15V","D_SOD-123","BZT52C15",["15V","SOD-123"],"MOSFET gate protection")
add("D505","1N4007","D_SMA","M7 1000V SMA",["1kV","SMA"],"M7 = SMD 1N4007")
add("Q101,Q102,Q201-Q203","2N7002","SOT-23","2N7002",["SOT-23","60V"],"AC cathode network switches")
add("Q103-Q105,Q301-Q304","MMBFJ113","SOT-23","MMBFJ113",["SOT-23"],"pot-set / mute JFETs")
add("Q501","LND150","SOT-89","LND150N8-G",["SOT-89"],"regulator CCS (SOT-89 for heat; SOT-23 C145393 also exists)")
add("Q502","STP4N80K5","TO-220 (THT)","STP4N80K5",["TO-220"],"pass FET ~1 W: TO-220 on a small heatsink. Only 7 in stock; STD4N80K5 DPAK (C472540) is the SMD option")
add("Q503","MMBTA42","SOT-23","MMBTA42",["SOT-23","300V"],"regulator current limit")
# ---- ICs, relays
add("U401","MCP23S17-E/SS","SSOP-28","MCP23S17-E/SS",["SSOP-28"],"SPI port expander")
add("U402","74LVC1G08","SOT-23-5","74LVC1G08GV",["SOT-23-5"],"unmute AND")
add("U403,U404","DG412DY","SOIC-16","DG412DY-T1-E3",["SOIC-16"],"JFET gate switches, +/-15 V (the only DG412 variant in stock)")
add("U405","ULN2003A","SOIC-16","ULN2003A SOIC-16",["SOP-16"],"relay coil sink")
add("K201-K204","G6K-2F-Y 5VDC","Relay SMD 10x6.5","G6K-2F-Y DC5",["5V"],"proposed; NC/NO pins and coil polarity to check on the datasheet")
# ---- connectors
add("J401","CONTROL 2x7","IDC box header 2.54 2x7 vertical","2x7P 2.54mm IDC Header",["2x7P","IDC Header","Through Hole"],"control ribbon")
add("J504-J506","POTS 2x13","IDC box header 2.54 2x13 vertical","2x13P 2.54mm IDC Header",["2x13P","IDC Header","Through Hole"],"pot ribbons")
add("J501","B+ RAW (2 tabs)","Faston 4.8 mm PCB tab x2","4.8mm PCB quick connect terminal",["4.8"],"HV: 4.8 mm tabs (interfaces.md 4.1); qty is tabs",)
add("J502","HEATER (2 tabs)","Faston 6.3 mm PCB tab x2","6.3mm PCB quick connect terminal",["6.3"],"heaters: 6.3 mm tabs; qty is tabs")
add("J102","CHASSIS (1 tab)","Faston 6.3 mm PCB tab","6.3mm PCB quick connect terminal",["6.3"],"bond wire to the chassis tag (tab size proposed)")
add("J101","INPUT 1x2","KK-254 1x2 vertical","Molex 22-27-2021",["2.54"],"input lead (Lock-2.54)")
add("J507","OUT 1x3","KK-254 1x3 vertical","Molex 22-27-2031",["2.54"],"output, shielded lead (Lock-2.54)")
add("J503","HEATER REF 1x3 + jumper","PinHeader 1x3 2.54","pin header 1x3P 2.54mm",["1x3P","Pin Header","Through Hole"],"plus one 2.54 mm jumper shunt")
add("V1-V3","12AX7 socket","Noval PCB socket (THT)","",[],"not at JLC: source the noval PCB sockets separately (rev A part), tubes not on the BOM")


def search(kw, n=50, lib=None):
    body = dict({"keyword": kw, "currentPage": 1, "pageSize": n}, **({"componentLibraryType": lib} if lib else {}))
    req = urllib.request.Request(jlc_search.URL, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": jlc_search.UA})
    for _ in range(3):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30))
            break
        except Exception:
            time.sleep(2)
            d = {}
    time.sleep(0.3)
    out = []
    for c in ((d.get("data") or {}).get("componentPageInfo") or {}).get("list") or []:
        pr = sorted(c.get("componentPrices") or [], key=lambda p: p["startNumber"])
        out.append(dict(lcsc=c["componentCode"], mpn=c.get("componentModelEn") or "", mfr=c.get("componentBrandEn") or "",
                        pkg=c.get("componentSpecificationEn") or "", desc=c.get("describe") or "",
                        lib="basic" if c.get("componentLibraryType") == "base" else "extended",
                        pref=bool(c.get("preferredComponentFlag")), free=c.get("canPresaleNumber") or 0,
                        minq=c.get("minPurchaseNum") or 1, price=pr[0]["productPrice"] if pr else None))
    return out


def ok(c, it):
    t = " ".join((c["desc"], c["pkg"], c["mpn"]))
    return all((any(x in t for x in m) if isinstance(m, tuple) else m in t) for m in it["must"])


def select(it):
    q = len(it["refs"])
    if it["pick"]:
        hits = [c for c in search(it["pick"], 5) if c["lcsc"] == it["pick"]]
        return hits[0] if hits else None
    if not it["kw"]:
        return None
    b = [c for c in search(it["kw"], 50, "base") if ok(c, it) and c["free"] >= q * BOARDS and c["minq"] <= q]
    if b:
        return b[0]
    e = sorted((c for c in search(it["kw"], 50) if ok(c, it)),
               key=lambda c: (-(c["free"] >= max(50, q * BOARDS)), -(c["minq"] <= q), -c["pref"], c["price"] or 9))
    return e[0] if e else None


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for it in ITEMS:
        c = select(it)
        rows.append((it, c))
        print(f"{len(it['refs']):>3} {it['value'][:16]:16} {(c or {}).get('lcsc', '-'):>10} {(c or {}).get('free', 0):>8}", flush=True)
    with open(os.path.join(OUT, 'bom_jlcpcb.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["Comment", "Designator", "Footprint", "LCSC Part #"])
        for it, c in rows:
            w.writerow([c["mpn"] if c else it["value"], ",".join(it["refs"]), it["pkg"], c["lcsc"] if c else ""])
    tot = sum(len(it["refs"]) * (c["price"] or 0) for it, c in rows if c)
    nb = sum(1 for _, c in rows if c and c["lib"] == "extended")
    low = [(it, c) for it, c in rows if c and c["free"] < len(it["refs"]) * BOARDS]
    md = ["# Rev B preamp: initial JLCPCB BOM", "",
          f"Generated by `tools/make_bom.py` on {time.strftime('%Y-%m-%d')} from the first-draft schematic (no footprints",
          "assigned yet: the Footprint column is the package this BOM proposes). Stock is JLC's orderable quantity",
          f"(canPresaleNumber) on that day; price is the 1-piece unit price in USD. {len(rows)} lines,",
          f"{sum(len(i['refs']) for i in ITEMS)} references, {nb} extended-part lines (JLC's loading fee, about USD 3 per extended type and order, applies).",
          f"Parts total about **USD {tot:.0f} per board** at single-piece prices, before assembly fees and the parts JLC does not stock.", "",
          "Package rules: 0603 for logic and gate drive; 0805 for low-voltage audio (thin film where a cathode resistor",
          "carries DC); 1206 (200 V) where a node can reach 100-300 V; 2512 (1 W, 200 V) for plate loads, the CF cathode",
          "and the B+ decoupling; C0G for every audio capacitor; film (THT) for the 22 nF plate couplings and the CF",
          "output cap; electrolytics above 50 V are THT radial.", "",
          "| Qty | Value | Designators | Package | LCSC | MPN | Type | Stock | USD | Note |", "|---|---|---|---|---|---|---|---|---|---|"]
    for it, c in rows:
        refs = ", ".join(it["refs"]) if len(it["refs"]) <= 6 else ", ".join(it["refs"][:4]) + f", ... ({len(it['refs'])})"
        if c:
            md.append(f"| {len(it['refs'])} | {it['value']} | {refs} | {it['pkg']} | {c['lcsc']} | {c['mpn']} | {c['lib']} | {c['free']} | {c['price']} | {it['note']} |")
        else:
            md.append(f"| {len(it['refs'])} | {it['value']} | {refs} | {it['pkg']} | — | — | — | — | — | {it['note']} |")
    md += ["", "## Open points", ""]
    md += [f"- Low stock for {BOARDS} boards: " + ", ".join(f"{it['refs'][0]} {c['lcsc']} ({c['free']})" for it, c in low)] if low else []
    md += [
           "- C105 (22n), C108 (2.2n) and C111 (4.7n) are drawn without a voltage, but they couple the S1 plate (P1):",
           "  the BOM gives them 630 V parts. Put the voltage in the schematic values at the next value pass.",
           "- Q502: STP4N80K5 has little stock; STD4N80K5 (DPAK, C472540) is the SMD alternative (about 1 W on copper).",
           "- K201-K204: G6K-2F-Y DC5 proposed; check NC / NO pins and coil polarity against the datasheet.",
           "- Faston tabs: check that the BTC-3 parts have 2 legs on 5.00 mm with 1.4 mm drill (interfaces.md 4.1).",
           "- C209 (680 nF, S5 cathode bypass) is X7R for now; a film part would avoid the X7R voltage coefficient.",
           "- Plate loads are 2512 thick film; MELF or thin film would be quieter but JLC had no stock.",
           "- Not from JLC: three noval PCB sockets, one 2.54 mm jumper shunt (J503), the tubes.",
           "- Values are the first draft: the value pass (330k -> ~300k, B+ decoupling, crunch pad) changes some lines.",
           "", "Check stock before ordering: `python3 -I rev_b/tools/jlc/stock_check.py rev_b/bom/bom_jlcpcb.csv --boards N`."]
    with open(os.path.join(OUT, 'README.md'), 'w') as f:
        f.write("\n".join(md) + "\n")


if __name__ == '__main__':
    main()
