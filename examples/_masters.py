"""Synthetic customer, supplier and part masters for the two fictional manufacturers.

ERP A belongs to Marrowdale Castings Limited (UK). ERP B belongs to Norvane Dichtungen GmbH (Germany).
Both are invented. Some records are deliberately messy and some are deliberate duplicates, so the
tools have something to find. The expected outcome for each planted pair is written to examples/truth
and is used by the tests.
"""

from __future__ import annotations

import csv
import os
import random
from difflib import SequenceMatcher

SYL1 = ["Cor", "Ost", "Van", "Hel", "Quen", "Tav", "Brel", "Yar", "Fen", "Dun", "Sel", "Pen", "Kes", "Wil", "Hal", "Dor",
        "Rav", "Ash", "Bax", "Cal", "Del", "Eld", "Fal", "Gar", "Hox", "Jor", "Kel", "Lor", "Mon", "Orm", "Pol", "Rin",
        "Sar", "Tor", "Ven", "Wex", "Yol", "Zan", "Ald", "Bryn", "Crev", "Dray", "Esk", "Fyn", "Gul", "Harn"]
SYL2 = ["vane", "trel", "try", "brook", "moor", "isk", "den", "wick", "warth", "marrow", "brae", "nock", "ham", "ley",
        "ton", "ford", "well", "stead", "croft", "mere", "shaw", "by", "hurst", "gate", "wyn", "lock", "thorn", "dale"]
DESC = ["Engineering", "Fabrications", "Hydraulics", "Fasteners", "Metals", "Coatings", "Logistics", "Packaging", "Tooling",
        "Bearings", "Plastics", "Electrical", "Controls", "Haulage", "Industrial Supplies", "Abrasives", "Lubricants", "Pumps",
        "Valves", "Machining", "Instruments", "Fixings", "Steel Stockholders", "Heat Treatment", "Pattern Makers",
        "Testing Services", "Manufacturing", "International"]
TRADING_NAMES = ["Midlands Precision Supply", "Northern Works Trading", "Allied Component Services", "Home Counties Industrial"]
GB_SUFFIX = ["Ltd", "Limited", "Ltd", "Limited", "PLC"]
DE_SUFFIX = ["GmbH", "GmbH", "GmbH & Co. KG", "AG", "KG"]
GB_TOWNS = [("Wolverhampton", "WV"), ("Walsall", "WS"), ("Sheffield", "S"), ("Leeds", "LS"), ("Derby", "DE"), ("Nottingham", "NG"),
            ("Stoke-on-Trent", "ST"), ("Coventry", "CV"), ("Bolton", "BL"), ("Preston", "PR"), ("Telford", "TF"), ("Redditch", "B"),
            ("Doncaster", "DN"), ("Cardiff", "CF"), ("Swindon", "SN"), ("Reading", "RG")]
DE_TOWNS = [("Stuttgart", "70"), ("Koeln", "50"), ("Duesseldorf", "40"), ("Nuernberg", "90"), ("Dortmund", "44"), ("Leipzig", "04"),
            ("Dresden", "01"), ("Hannover", "30"), ("Bremen", "28"), ("Essen", "45"), ("Duisburg", "47"), ("Augsburg", "86"),
            ("Mannheim", "68")]
DE_TOWN_DISPLAY = {"Koeln": "Köln", "Duesseldorf": "Düsseldorf", "Nuernberg": "Nürnberg"}
GB_STREET = ["Foundry", "Canal", "Mill", "Forge", "Station", "Industrial", "Brook", "Enterprise", "Furnace", "Quarry"]
GB_STREET_END = ["Road", "Way", "Lane", "Park", "Street"]
DE_STREET = ["Industriestraße", "Am Hafen", "Werkstraße", "Gewerbepark", "Hüttenweg", "Bahnhofstraße", "Schmiedegasse"]
LETTERS = "ABDEFGHJLNPQRSTUWXYZ"


def _stems(rng, n):
    out = []
    tries = 0
    while len(out) < n and tries < 20000:
        tries += 1
        s = rng.choice(SYL1) + rng.choice(SYL2)
        if any(SequenceMatcher(None, s.lower(), o.lower()).ratio() > 0.72 for o in out):
            continue
        out.append(s)
    assert len(out) == n
    return out


def _digits(rng, n):
    return "".join(str(rng.randint(0, 9)) for _ in range(n))


def make_org(rng, stem, country):
    desc = rng.choice(DESC)
    if country == "GB":
        town, area = rng.choice(GB_TOWNS)
        pc = f"{area}{rng.randint(1, 20)} {rng.randint(1, 9)}{rng.choice(LETTERS)}{rng.choice(LETTERS)}"
        street = f"Unit {rng.randint(1, 40)}, {rng.choice(GB_STREET)} {rng.choice(GB_STREET_END)}"
        suffix = rng.choice(GB_SUFFIX)
        tax = "GB" + _digits(rng, 9)
    else:
        town, prefix = rng.choice(DE_TOWNS)
        pc = prefix + _digits(rng, 3)
        street = f"{rng.choice(DE_STREET)} {rng.randint(1, 60)}"
        suffix = rng.choice(DE_SUFFIX)
        tax = "DE" + _digits(rng, 9)
        town = DE_TOWN_DISPLAY.get(town, town)
    domain = f"{stem.lower()}-{desc.lower().replace(' ', '')}.example"
    return {"stem": stem, "desc": desc, "country": country, "town": town, "street": street, "postcode": pc,
            "tax": tax, "suffix": suffix, "email": f"accounts@{domain}", "domain": domain}


def display_name(org, style=0, rng=None):
    base = f"{org['stem']} {org['desc']}"
    suf = org["suffix"]
    if style == 1:  # alternative suffix spelling
        suf = {"Ltd": "Limited", "Limited": "Ltd.", "PLC": "plc", "GmbH": "GmbH.", "AG": "AG", "KG": "KG",
               "GmbH & Co. KG": "GmbH u. Co. KG"}.get(suf, suf)
        return f"{base} {suf}"
    if style == 2:  # upper case
        return f"{base} {suf}".upper()
    if style == 3:  # comma and double space
        return f"{base},  {suf}"
    if style == 4:  # typo in the stem
        s = org["stem"]
        i = max(2, len(s) // 2)
        return f"{s[:i] + s[i + 1:]} {org['desc']} {suf}"
    if style == 5:  # trading style, no legal form
        return f"{base}"
    return f"{base} {suf}"


def fmt_tax(rng, tax, style=0):
    if style == 0:
        return tax
    if style == 1:
        return tax[:2] + " " + " ".join([tax[2:5], tax[5:8], tax[8:]])
    if style == 2:
        return tax[2:]
    return tax.lower()


def fmt_pc(pc, country, style=0):
    if style == 0:
        return pc
    if country == "GB":
        return pc.replace(" ", "").lower() if style == 1 else pc.replace(" ", "  ")
    return pc.lstrip("0") if style == 1 else pc


def party_record(org, *, name=None, tax=None, pc=None, email=True, system="A"):
    return {
        "name": name if name is not None else display_name(org),
        "street": org["street"], "town": org["town"],
        "postcode": pc if pc is not None else org["postcode"],
        "country": org["country"], "tax": tax if tax is not None else org["tax"],
        "email": org["email"] if email else "", "org": org,
    }


def country_text(rng, system, country):
    if system == "A":
        return {"GB": rng.choice(["GB", "GB", "UK", "United Kingdom"]), "DE": rng.choice(["DE", "Germany"])}[country]
    return {"GB": rng.choice(["GB", "GBR"]), "DE": rng.choice(["DE", "DE", "DEU"])}[country]


def messy_email(rng, email):
    r = rng.random()
    if r < 0.03:
        return email.replace("@", "")
    if r < 0.06:
        return email + " "
    if r < 0.09:
        return "n/a"
    if r < 0.20:
        return ""
    return email


def created(rng, system, k):
    y, m, d = 2018 + rng.randint(0, 7), rng.randint(1, 12), rng.randint(1, 28)
    if system == "A":
        return f"{d:02d}/{m:02d}/{y}" if rng.random() < 0.15 else f"{y}-{m:02d}-{d:02d}"
    return f"{d:02d}.{m:02d}.{y}"


def singleton_corruption(rng, rec):
    """Random messiness for records that are not part of a planted pair."""
    r = rng.random()
    if r < 0.10:
        rec["tax"] = ""
    elif r < 0.14:
        rec["tax"] = rec["tax"][:-1]  # one digit short, fails the format check
    r = rng.random()
    if r < 0.08:
        rec["postcode"] = fmt_pc(rec["postcode"], rec["country"], 1)
    elif r < 0.16:
        rec["postcode"] = rec["postcode"][:-1]  # truncated
    if rng.random() < 0.03:
        rec["town"] = ""
    if rng.random() < 0.10:
        rec["name"] = rec["name"].upper()


def generate_parties(rng, kind, n_a_only, n_b_only, n_both, dup_a, dup_b, id_a0, id_b0):
    """Return (A rows, B rows, expected pairs). Rows are dicts with canonical keys plus 'id'."""
    total = n_a_only + n_b_only + n_both + 12
    stems = _stems(rng, total)
    it = iter(stems)
    orgs_a = [make_org(rng, next(it), "GB" if rng.random() < 0.8 else "DE") for _ in range(n_a_only)]
    orgs_b = [make_org(rng, next(it), "DE" if rng.random() < 0.8 else "GB") for _ in range(n_b_only)]
    orgs_both = [make_org(rng, next(it), "GB" if i % 3 != 2 else "DE") for i in range(n_both)]
    a_rows, b_rows, pairs = [], [], []

    def add(rows, system, rec, scenario):
        rec["system"] = system
        rec["scenario"] = scenario
        rows.append(rec)
        return rec

    for o in orgs_a:
        rec = party_record(o)
        singleton_corruption(rng, rec)
        add(a_rows, "A", rec, "single")
    for o in orgs_b:
        rec = party_record(o)
        singleton_corruption(rng, rec)
        add(b_rows, "B", rec, "single")

    # Cross-system duplicates: the same organisation held in both ERPs.
    for i, o in enumerate(orgs_both):
        s = i % 5
        ra = add(a_rows, "A", party_record(o), "cross")
        if s == 0:      # suffix and case variant, tax and postcode formatted differently: automatic
            rb = party_record(o, name=display_name(o, 1 if i % 2 else 2), tax=fmt_tax(rng, o["tax"], 1), pc=fmt_pc(o["postcode"], o["country"], 1))
            band = "auto"
        elif s == 1:    # no tax number held in ERP B: review
            rb = party_record(o, name=display_name(o, 1), tax="")
            band = "review"
        elif s == 2:    # typo in the name, same tax and postcode: automatic
            rb = party_record(o, name=display_name(o, 4), tax=fmt_tax(rng, o["tax"], 2))
            band = "auto"
        elif s == 3:    # moved site, same legal entity: automatic on tax number and name
            other = make_org(rng, o["stem"], o["country"])
            rb = party_record(o, name=display_name(o, 3), pc=other["postcode"])
            band = "auto"
        else:           # trading name, same tax and postcode: review
            rb = party_record(o, name=rng.choice(TRADING_NAMES), pc=o["postcode"])
            band = "review"
        add(b_rows, "B", rb, "cross")
        ra["pair"], rb["pair"] = i, i
        pairs.append((ra, rb, band, f"cross system, variant {s}"))

    # Within-system duplicates.
    for rows, system, count, label in ((a_rows, "A", dup_a, "A"), (b_rows, "B", dup_b, "B")):
        candidates = [r for r in rows if r["scenario"] == "single"][:count]
        for j, base in enumerate(candidates):
            org = base["org"]
            base["scenario"] = "within"
            # keep the base record clean so the planted expectation is exact
            base.update(party_record(org, name=display_name(org)))
            kind_ = j % 3
            if kind_ == 0:
                dup = party_record(org, name=display_name(org, 2), tax=fmt_tax(rng, org["tax"], 1))
                band = "auto"
            elif kind_ == 1:
                dup = party_record(org, name=display_name(org, 3), tax="")
                dup["postcode"] = base["postcode"]
                band = "review"
            else:
                dup = party_record(org, name=display_name(org, 1), pc="")
                band = "auto"
            add(rows, system, dup, "within")
            pairs.append((base, dup, band, f"within {label}, variant {kind_}"))

    # Traps: records that look alike but should not be merged automatically.
    t_orgs = [make_org(rng, next(it), "GB") for _ in range(4)]
    o1 = t_orgs[0]
    o1b = dict(o1, desc=o1["desc"] + " Supplies", tax="GB" + _digits(rng, 9), postcode="WV99 1ZZ", street="Unit 1, Trap Road")
    r1, r2 = add(a_rows, "A", party_record(o1), "trap"), add(b_rows, "B", party_record(o1b), "trap")
    pairs.append((r1, r2, "none", "similar names, different tax number and postcode"))
    o2 = t_orgs[1]
    o2b = dict(o2, desc="Group Holdings", tax="GB" + _digits(rng, 9))
    r1, r2 = add(a_rows, "A", party_record(o2), "trap"), add(a_rows, "A", party_record(o2b, pc=o2["postcode"]), "trap")
    pairs.append((r1, r2, "none", "parent and subsidiary at one address, different tax numbers"))
    o3 = t_orgs[2]
    r1 = add(a_rows, "A", party_record(o3), "trap")
    r2 = add(b_rows, "B", party_record(o3, name=f"{o3['stem']} Trading", pc=make_org(rng, "Zzz", o3["country"])["postcode"]), "trap")
    pairs.append((r1, r2, "review", "same tax number, different name and postcode"))
    o4 = t_orgs[3]
    r1 = add(a_rows, "A", party_record(o4), "trap")
    r2 = add(a_rows, "A", party_record(o4, name=display_name(o4, 2), tax=""), "trap")
    pairs.append((r1, r2, "review", "same name and postcode, tax number missing on one"))

    # Assign IDs after all rows exist, shuffle for realism, and plant two duplicate keys in singletons.
    for rows, system, start, prefix in ((a_rows, "A", id_a0, "C" if kind == "customer" else "S"),
                                         (b_rows, "B", id_b0, "K" if kind == "customer" else "L")):
        rng.shuffle(rows)
        n = start
        for r in rows:
            n += rng.randint(1, 4)
            r["id"] = f"{prefix}{n}"
        singles = [r for r in rows if r["scenario"] == "single"]
        if len(singles) >= 4:
            singles[1]["id"] = singles[0]["id"]
            singles[3]["id"] = singles[2]["id"]
        for r in rows:
            r["country_text"] = country_text(rng, system, r["country"])
            r["email"] = messy_email(rng, r["email"]) if r["scenario"] != "trap" else r["email"]
            r["created"] = created(rng, system, 0)
    return a_rows, b_rows, pairs


def write_parties(data_dir, truth_dir, kind, rows_a, rows_b, pairs, prefix_a, prefix_b):
    def path(*p):
        return os.path.join(data_dir, *p)
    with open(path(f"erp_a_{kind}s.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["cust_id" if kind == "customer" else "supplier_id", "cust_name" if kind == "customer" else "supplier_name",
                    "address_1", "city", "postcode", "country", "vat_no", "email", "created"])
        for r in sorted(rows_a, key=lambda r: r["id"]):
            w.writerow([r["id"], r["name"], r["street"], r["town"], r["postcode"], r["country_text"], r["tax"], r["email"], r["created"]])
    with open(path(f"erp_b_{kind}s.csv"), "w", encoding="cp1252", newline="") as fh:
        w = csv.writer(fh, delimiter=";", lineterminator="\n")
        w.writerow(["account_no", "account_name", "street", "town", "zip", "country_code", "tax_id", "contact_email", "date_created"])
        for r in sorted(rows_b, key=lambda r: r["id"]):
            w.writerow([r["id"], r["name"], r["street"], r["town"], r["postcode"], r["country_text"], r["tax"], r["email"], r["created"]])
    os.makedirs(truth_dir, exist_ok=True)
    with open(os.path.join(truth_dir, f"expected_pairs_{kind}s.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["left_system", "left_id", "right_system", "right_id", "expected_band", "acceptable_bands", "scenario"])
        for l, r, band, why in sorted(pairs, key=lambda p: (p[0]["system"], p[0]["id"], p[1]["system"], p[1]["id"])):
            if (l["system"], l["id"]) > (r["system"], r["id"]):
                l, r = r, l
            w.writerow([l["system"], l["id"], r["system"], r["id"], band, band, why])


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------

FAMILIES = [("Gate valve body", "MC", "CAST", "EA"), ("Pump housing", "MC", "CAST", "EA"), ("Impeller", "MC", "CAST", "EA"),
            ("Flange blank", "MC", "CAST", "EA"), ("Bearing bracket", "MM", "MACH", "EA"), ("Seal ring", "MM", "MACH", "EA"),
            ("Shaft sleeve", "MM", "MACH", "EA"), ("Gland follower", "MM", "MACH", "EA"), ("Bolt set", "FX", "FIX", "BOX"),
            ("Gasket pack", "FX", "FIX", "BOX"), ("Stud kit", "FX", "FIX", "SET"), ("Pattern plate", "TL", "TOOL", "EA"),
            ("Core box", "TL", "TOOL", "EA")]
SIZES = ["DN25", "DN40", "DN50", "DN80", "DN100", "DN150"]
MATERIALS = [("ductile iron", "DI"), ("cast iron", "CI"), ("stainless steel", "SS"), ("bronze", "bronze")]
BULK = [("Moulding sand", "KG"), ("Ferro silicon alloy", "KG"), ("Welding wire 1.2mm", "KG"), ("Cutting fluid", "L"),
        ("Steel bar 40mm dia", "M"), ("Steel bar 60mm dia", "M"), ("Hydraulic hose 25mm", "M"), ("Coolant concentrate", "L")]
B_UOM = {"EA": "ST", "KG": "KG", "M": "MTR", "L": "LTR", "BOX": "CTN", "SET": "SET"}


def generate_parts(rng, data_dir, truth_dir):
    combos = [(f, s, m) for f in FAMILIES for s in SIZES for m in MATERIALS]
    rng.shuffle(combos)
    base = []
    core = 10000
    for fam, size, mat in combos[:62]:
        core += rng.randint(3, 40)
        base.append({"fam": fam[0], "prefix": fam[1], "cat": fam[2], "uom": fam[3], "size": size, "mat": mat, "core": core,
                     "rev": rng.choice(["", "", "B", "C"]), "drawing": f"{core + 70000}"})
    for name, uom in BULK:
        core += rng.randint(3, 40)
        base.append({"fam": name, "prefix": "RM", "cat": "RAW", "uom": uom, "size": "", "mat": None, "core": core, "rev": "",
                     "drawing": ""})

    def a_desc(p):
        return " ".join(x for x in [p["fam"], p["size"], p["mat"][0] if p["mat"] else ""] if x)

    def b_desc(p, v):
        parts = [p["fam"], p["size"], p["mat"][1] if p["mat"] else ""]
        text = " ".join(x for x in parts if x)
        if v == 0:
            return text.upper()
        if v == 1:
            return f"{p['mat'][0] if p['mat'] else ''} {p['fam']} {p['size']}".strip()
        return text.replace("DN", "DN ")

    n = len(base)
    a_idx = list(range(0, 50))
    b_only = list(range(50, n))
    overlap = a_idx[:30]
    a_rows, b_rows, pairs = [], [], []

    def a_part_no(p):
        return f"{p['prefix']}-{p['core']}" + (f"-{p['rev']}" if p["rev"] else "")

    for i in a_idx:
        p = base[i]
        a_rows.append({"pn": a_part_no(p), "desc": a_desc(p), "uom": p["uom"], "drawing": f"DRG-{p['drawing']}" if p["drawing"] else "",
                       "cat": p["cat"], "status": rng.choice(["Active", "Active", "Active", "Obsolete"]), "idx": i})
    styles = ["s1"] * 12 + ["s2"] * 5 + ["s3"] * 7 + ["s4"] * 3 + ["s5"] * 3
    for i, st in zip(overlap, styles):
        p = base[i]
        a = a_rows[i]
        row = {"pn": f"{p['prefix']}{p['core']}", "desc": b_desc(p, rng.randint(0, 2)), "uom": B_UOM[p["uom"]],
               "drawing": f"DRG {p['drawing']}" if p["drawing"] else "", "cat": p["cat"], "status": "Active", "idx": i}
        acceptable = None
        if st == "s1":      # compact number, revision letter dropped: equal when ERP A has no revision
            expected = "review" if p["rev"] else "auto"
        elif st == "s2":    # zero padded number, revision kept: equal after normalising
            row["pn"] = f"{p['prefix']}-{p['core']:07d}" + (f"-{p['rev']}" if p["rev"] else "")
            expected = "auto"
        elif st == "s3":    # different numbering, matched through the drawing number
            row["pn"] = f"5{rng.randint(100, 999)}-{rng.randint(1000, 9999)}"
            expected = "review" if p["drawing"] else "none"
            acceptable = "review|auto" if p["drawing"] else "none"
        elif st == "s4":    # different numbering and no drawing number: a known miss
            row["pn"] = f"5{rng.randint(100, 999)}-{rng.randint(1000, 9999)}"
            row["drawing"] = ""
            expected = "none"
        else:               # same number, different unit of measure
            row["pn"] = f"{p['prefix']}{p['core']}" + (p["rev"] if p["rev"] else "")
            row["uom"] = "KG" if p["uom"] != "KG" else "ST"
            expected = "review"
        b_rows.append(row)
        pairs.append((("A", a["pn"]), ("B", row["pn"]), expected, acceptable or expected, f"cross system, {st}"))
    for i in b_only:
        p = base[i]
        b_rows.append({"pn": f"{p['prefix']}{p['core']}", "desc": b_desc(p, rng.randint(0, 2)), "uom": B_UOM[p["uom"]],
                       "drawing": f"DRG {p['drawing']}" if p["drawing"] else "", "cat": p["cat"], "status": "Active", "idx": i})

    # Within-system duplicates: the same part entered twice with different number formatting.
    for i in (32, 38, 44):
        p = base[i]
        dup = {"pn": f"{p['prefix']} {p['core']}" + (f" {p['rev']}" if p["rev"] else ""), "desc": a_desc(p).upper(), "uom": p["uom"],
               "drawing": f"DRG-{p['drawing']}" if p["drawing"] else "", "cat": p["cat"], "status": "Active", "idx": i}
        a_rows.append(dup)
        exp = "auto" if p["drawing"] else "auto"
        pairs.append((("A", a_rows[i]["pn"]), ("A", dup["pn"]), exp, exp, "within A, formatting variant"))
    for i in (55, 58):
        p = base[i]
        src = next(r for r in b_rows if r["idx"] == i)
        dup = dict(src, pn=f"{p['prefix']}-{p['core']:07d}", desc=src["desc"].title())
        b_rows.append(dup)
        pairs.append((("B", src["pn"]), ("B", dup["pn"]), "auto", "auto", "within B, zero padded variant"))

    # Trap: a neighbouring part number with the same description is a different part.
    p = base[1]
    a_rows.append({"pn": f"{p['prefix']}-{p['core'] + 1}", "desc": a_desc(p), "uom": p["uom"], "drawing": f"DRG-{p['drawing']}x",
                   "cat": p["cat"], "status": "Active", "idx": -1})
    pairs.append((("A", a_rows[1]["pn"]), ("A", a_rows[-1]["pn"]), "none", "none", "neighbouring part numbers, different parts"))

    rng.shuffle(a_rows)
    rng.shuffle(b_rows)
    os.makedirs(truth_dir, exist_ok=True)
    with open(os.path.join(data_dir, "erp_a_parts.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["part_no", "description", "uom", "drawing_no", "category", "status"])
        for r in sorted(a_rows, key=lambda r: r["pn"]):
            w.writerow([r["pn"], r["desc"], r["uom"], r["drawing"], r["cat"], r["status"]])
    with open(os.path.join(data_dir, "erp_b_parts.csv"), "w", encoding="cp1252", newline="") as fh:
        w = csv.writer(fh, delimiter=";", lineterminator="\n")
        w.writerow(["item_no", "item_text", "unit", "drawing", "item_group", "status"])
        for r in sorted(b_rows, key=lambda r: r["pn"]):
            w.writerow([r["pn"], r["desc"], r["uom"], r["drawing"], r["cat"], r["status"]])
    with open(os.path.join(truth_dir, "expected_pairs_parts.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["left_system", "left_id", "right_system", "right_id", "expected_band", "acceptable_bands", "scenario"])
        for l, r, band, ok, why in sorted(pairs, key=lambda p: (p[0], p[1])):
            if l > r:
                l, r = r, l
            w.writerow([l[0], l[1], r[0], r[1], band, ok, why])


def generate(data_dir, truth_dir, seed):
    os.makedirs(data_dir, exist_ok=True)
    rng = random.Random(f"{seed}:customers")
    a, b, pairs = generate_parties(rng, "customer", 26, 22, 14, 6, 4, 10000, 400100)
    write_parties(data_dir, truth_dir, "customer", a, b, pairs, "C", "K")
    rng = random.Random(f"{seed}:suppliers")
    a, b, pairs = generate_parties(rng, "supplier", 18, 15, 8, 4, 3, 20000, 700100)
    write_parties(data_dir, truth_dir, "supplier", a, b, pairs, "S", "L")
    generate_parts(random.Random(f"{seed}:parts"), data_dir, truth_dir)
