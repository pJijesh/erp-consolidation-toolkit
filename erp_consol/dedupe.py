"""Find probable duplicate parties (customers or suppliers) and parts.

The scoring model is documented in docs/scoring-models.md. In short: each pair of
records collects points from evidence (tax number, name similarity, postcode and so
on), conflicts subtract points or block an automatic match, and the total decides
the band. Nothing here changes data. It produces a match report and a merge proposal
for a person to review.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations

from .csvio import Table
from .errors import InputError
from .normalise import (
    email_domain,
    normalise_country,
    normalise_description,
    normalise_name,
    normalise_part_number,
    normalise_postcode,
    normalise_tax,
    normalise_uom,
    part_number_relation,
    similarity,
)

AUTO_THRESHOLD = 85
REVIEW_THRESHOLD = 50

PARTY_COLUMNS = {
    "id": "id", "name": "name", "postcode": "postcode", "tax": "tax_number",
    "country": "country", "email": "email", "city": "city",
}
PART_COLUMNS = {
    "part_number": "part_number", "description": "description", "uom": "uom",
    "drawing": "drawing_no", "category": "category",
}

# Points. See docs/scoring-models.md for the reasoning behind each number.
PARTY_WEIGHTS = {"tax_equal": 50, "name_max": 40, "postcode_equal": 15, "email_domain_equal": 5,
                 "tax_differs": -20, "country_differs": -10}
PART_WEIGHTS = {"part_number_equal": 60, "part_number_revision": 35, "drawing_equal": 45,
                "description_max": 30, "uom_equal": 10}
NAME_FLOOR = 0.5  # similarity at or below this earns no points; points scale linearly up to 1.0


@dataclass
class Rec:
    system: str
    id: str
    label: str  # name or description, for reports
    raw: dict[str, str]
    norm: dict[str, str]
    filled: int
    order: tuple = field(default_factory=tuple)
    idx: int = 0  # position in the combined list, the final tie-break so output never depends on memory addresses


@dataclass
class Pair:
    left: Rec
    right: Rec
    score: int
    band: str
    scope: str
    reasons: list[str]
    flags: list[str]


def _band(score: int, flags: list[str], auto: int, review: int) -> str:
    if score >= auto and not flags:
        return "auto"
    if score >= review:
        return "review"
    return "none"


def _scaled(sim: float, maximum: int) -> int:
    return round(maximum * max(0.0, (sim - NAME_FLOOR) / (1.0 - NAME_FLOOR)))


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _cols(table: Table, wanted: dict[str, str], overrides: dict[str, str], required: list[str], optional: list[str]) -> dict[str, str | None]:
    names = {k: overrides.get(k, wanted[k]) for k in wanted}
    req_real = table.resolve([names[k] for k in required], hint="Use --a-map or --b-map to name the column, for example --a-map name=cust_name.")
    out: dict[str, str | None] = {k: req_real[names[k]] for k in required}
    for k in optional:
        out[k] = table.find_column(names[k])
    return out


def load_parties(table: Table, system: str, overrides: dict[str, str], extra_suffixes: frozenset[str] = frozenset()) -> list[Rec]:
    c = _cols(table, PARTY_COLUMNS, overrides, ["id", "name"], ["postcode", "tax", "country", "email", "city"])
    recs: list[Rec] = []
    for row in table.rows:
        get = lambda k: row[c[k]].strip() if c.get(k) else ""
        country = normalise_country(get("country"))
        norm = {
            "name": normalise_name(get("name"), extra_suffixes),
            "postcode": normalise_postcode(get("postcode"), country),
            "tax": normalise_tax(get("tax")),
            "country": country,
            "email_domain": email_domain(get("email")),
        }
        filled = sum(1 for k in ("name", "postcode", "tax", "country", "email", "city") if get(k))
        recs.append(Rec(system, get("id"), get("name"), {k: get(k) for k in PARTY_COLUMNS if c.get(k)}, norm, filled))
    return recs


def load_parts(table: Table, system: str, overrides: dict[str, str], uom_aliases: dict[str, str] | None = None) -> list[Rec]:
    c = _cols(table, PART_COLUMNS, overrides, ["part_number", "description"], ["uom", "drawing", "category"])
    recs: list[Rec] = []
    for row in table.rows:
        get = lambda k: row[c[k]].strip() if c.get(k) else ""
        norm = {
            "part_number": normalise_part_number(get("part_number")),
            "description": normalise_description(get("description")),
            "uom": normalise_uom(get("uom"), uom_aliases),
            "drawing": normalise_part_number(get("drawing")),
        }
        filled = sum(1 for k in ("description", "uom", "drawing", "category") if get(k))
        recs.append(Rec(system, get("part_number"), get("description"), {k: get(k) for k in PART_COLUMNS if c.get(k)}, norm, filled))
    return recs


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_party(a: Rec, b: Rec) -> tuple[int, list[str], list[str]]:
    w = PARTY_WEIGHTS
    pts, reasons, flags = 0, [], []
    sim = similarity(a.norm["name"], b.norm["name"])
    name_pts = _scaled(sim, w["name_max"])
    if name_pts:
        pts += name_pts
        reasons.append(f"name similarity {sim:.2f} (+{name_pts})")
    ta, tb = a.norm["tax"], b.norm["tax"]
    if ta and tb:
        if ta == tb:
            pts += w["tax_equal"]
            reasons.append(f"same tax number (+{w['tax_equal']})")
        else:
            pts += w["tax_differs"]
            flags.append("tax_differs")
            reasons.append(f"different tax numbers ({w['tax_differs']})")
    if a.norm["postcode"] and a.norm["postcode"] == b.norm["postcode"]:
        pts += w["postcode_equal"]
        reasons.append(f"same postcode (+{w['postcode_equal']})")
    if a.norm["email_domain"] and a.norm["email_domain"] == b.norm["email_domain"]:
        pts += w["email_domain_equal"]
        reasons.append(f"same email domain (+{w['email_domain_equal']})")
    ca, cb = a.norm["country"], b.norm["country"]
    if ca and cb and ca != cb:
        pts += w["country_differs"]
        flags.append("country_differs")
        reasons.append(f"different countries ({w['country_differs']})")
    return max(0, min(100, pts)), reasons, flags


def score_part(a: Rec, b: Rec) -> tuple[int, list[str], list[str]]:
    w = PART_WEIGHTS
    pts, reasons, flags = 0, [], []
    rel = part_number_relation(a.norm["part_number"], b.norm["part_number"])
    if rel == "equal":
        pts += w["part_number_equal"]
        reasons.append(f"same part number after normalising (+{w['part_number_equal']})")
    elif rel == "revision":
        pts += w["part_number_revision"]
        flags.append("revision_differs")
        reasons.append(f"part numbers differ only by a revision style suffix (+{w['part_number_revision']})")
    da, db = a.norm["drawing"], b.norm["drawing"]
    if da and db:
        if da == db:
            pts += w["drawing_equal"]
            reasons.append(f"same drawing number (+{w['drawing_equal']})")
        elif rel == "equal":
            flags.append("drawing_differs")
            reasons.append("same part number but different drawing numbers")
    sim = similarity(a.norm["description"], b.norm["description"])
    d_pts = _scaled(sim, w["description_max"])
    if d_pts:
        pts += d_pts
        reasons.append(f"description similarity {sim:.2f} (+{d_pts})")
    ua, ub = a.norm["uom"], b.norm["uom"]
    if ua and ub:
        if ua == ub:
            pts += w["uom_equal"]
            reasons.append(f"same unit of measure (+{w['uom_equal']})")
        else:
            flags.append("uom_differs")
            reasons.append(f"units differ: {ua} and {ub}")
    return max(0, min(100, pts)), reasons, flags


def _pn_root(pn: str) -> str:
    return re.sub(r"(?<=[0-9])[A-Z]{1,2}$", "", pn)


def party_block_keys(r: Rec) -> list[str]:
    # Without a shared tax number or postcode a pair can score at most
    # name_max + email_domain_equal = 45, which is below the review threshold, so
    # these two keys lose no pair that could reach review.
    keys = []
    if r.norm["tax"]:
        keys.append("tax:" + r.norm["tax"])
    if r.norm["postcode"]:
        keys.append("pc:" + r.norm["postcode"])
    return keys


def part_block_keys(r: Rec) -> list[str]:
    # Description and unit alone score at most 40, so a pair needs a part number
    # relationship or a shared drawing number to reach review.
    keys = []
    if r.norm["part_number"]:
        keys += ["pn:" + r.norm["part_number"], "root:" + _pn_root(r.norm["part_number"])]
    if r.norm["drawing"]:
        keys.append("dwg:" + r.norm["drawing"])
    return keys


# ---------------------------------------------------------------------------
# Matching and clustering
# ---------------------------------------------------------------------------


def find_pairs(recs: list[Rec], entity: str, auto: int = AUTO_THRESHOLD, review: int = REVIEW_THRESHOLD) -> list[Pair]:
    if not (0 < review <= auto <= 100):
        raise InputError("Thresholds must satisfy 0 < review <= auto <= 100.")
    scorer = score_party if entity == "party" else score_part
    keyer = party_block_keys if entity == "party" else part_block_keys
    order = {"A": 0, "B": 1}
    for i, r in enumerate(recs):
        r.order = (order.get(r.system, 9), r.id)
        r.idx = i
    blocks: dict[str, list[int]] = defaultdict(list)
    for i, r in enumerate(recs):
        for k in keyer(r):
            blocks[k].append(i)
    seen: set[tuple[int, int]] = set()
    pairs: list[Pair] = []
    for key in sorted(blocks):
        for i, j in combinations(sorted(blocks[key]), 2):
            if (i, j) in seen:
                continue
            seen.add((i, j))
            x, y = (recs[i], recs[j]) if recs[i].order <= recs[j].order else (recs[j], recs[i])
            score, reasons, flags = scorer(x, y)
            band = _band(score, flags, auto, review)
            if band == "none":
                continue
            scope = "cross" if x.system != y.system else f"within_{x.system}"
            pairs.append(Pair(x, y, score, band, scope, reasons, flags))
    pairs.sort(key=lambda p: (-p.score, p.scope, p.left.order, p.right.order))
    return pairs


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[tuple, tuple] = {}

    def find(self, x: tuple) -> tuple:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: tuple, b: tuple) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[max(ra, rb)] = min(ra, rb)


def _key(r: Rec) -> tuple:
    return (r.order[0], r.id, r.idx)


def build_clusters(pairs: list[Pair], within_system: str | None = None) -> list[list[Rec]]:
    """Group records joined by automatic pairs. With within_system, only that system's own pairs are used."""
    uf = _UnionFind()
    recs: dict[tuple, Rec] = {}
    for p in pairs:
        if p.band != "auto":
            continue
        if within_system and p.scope != f"within_{within_system}":
            continue
        for r in (p.left, p.right):
            recs[_key(r)] = r
        uf.union(_key(p.left), _key(p.right))
    groups: dict[tuple, list[Rec]] = defaultdict(list)
    for k, r in recs.items():
        groups[uf.find(k)].append(r)
    clusters = [sorted(g, key=lambda r: (r.order, r.idx)) for g in groups.values()]
    clusters.sort(key=lambda g: g[0].order)
    return clusters


def choose_survivor(cluster: list[Rec]) -> Rec:
    return sorted(cluster, key=lambda r: (-r.filled, r.order, r.idx))[0]


_COMPARE_FIELDS = {
    "party": [("name", "name"), ("postcode", "postcode"), ("tax", "tax"), ("country", "country"), ("email_domain", "email domain")],
    "part": [("description", "description"), ("uom", "unit"), ("drawing", "drawing number")],
}


def field_notes(entity: str, survivor: Rec, member: Rec) -> str:
    notes_diff, notes_fill = [], []
    for key, label in _COMPARE_FIELDS[entity]:
        sv, mv = survivor.norm.get(key, ""), member.norm.get(key, "")
        if sv and mv and sv != mv:
            notes_diff.append(label)
        elif mv and not sv:
            notes_fill.append(label)
    parts = []
    if notes_diff:
        parts.append("values differ: " + ", ".join(notes_diff))
    if notes_fill:
        parts.append("survivor blank, member has: " + ", ".join(notes_fill))
    return "; ".join(parts)


def merge_proposal(pairs: list[Pair], entity: str) -> list[list[object]]:
    rows: list[list[object]] = []
    clusters = build_clusters(pairs)
    direct: dict[tuple, int] = {}
    for p in pairs:
        if p.band == "auto":
            direct[(_key(p.left), _key(p.right))] = p.score
            direct[(_key(p.right), _key(p.left))] = p.score
    for n, cluster in enumerate(clusters, start=1):
        cid = f"C{n:04d}"
        surv = choose_survivor(cluster)
        keys = {_key(r) for r in cluster}
        weakest = min(s for (a, b), s in direct.items() if a in keys and b in keys)
        for r in sorted(cluster, key=lambda r: (r is not surv, r.order, r.idx)):
            if r is surv:
                role, action, note, linked = "survivor", "keep as the group record", "", "yes"
            else:
                role = "merge_into_survivor"
                action = "propose merge into survivor, after review"
                note = field_notes(entity, surv, r)
                linked = "yes" if (_key(surv), _key(r)) in direct else "no, linked through another record"
            rows.append([cid, role, r.system, r.id, r.label, surv.system, surv.id, len(cluster), weakest, linked, note, action])
    return rows


MERGE_HEADER = [
    "cluster_id", "role", "system", "id", "name_or_description", "survivor_system", "survivor_id",
    "cluster_size", "weakest_pair_score", "directly_matched_to_survivor", "fields_to_check", "action",
]
MATCH_HEADER = ["scope", "band", "score", "left_system", "left_id", "left_label", "right_system", "right_id", "right_label", "reasons", "flags"]


def match_rows(pairs: list[Pair]) -> list[list[object]]:
    return [
        [p.scope, p.band, p.score, p.left.system, p.left.id, p.left.label, p.right.system, p.right.id, p.right.label,
         "; ".join(p.reasons), ";".join(sorted(p.flags))]
        for p in pairs
    ]


def summarise(entity: str, recs: list[Rec], pairs: list[Pair], labels: dict[str, str], auto: int, review: int) -> dict:
    systems = sorted({r.system for r in recs})
    per_system = {}
    for s in systems:
        n = sum(1 for r in recs if r.system == s)
        within_clusters = build_clusters(pairs, within_system=s)
        dup = sum(len(c) - 1 for c in within_clusters)
        per_system[s] = {
            "label": labels.get(s, s),
            "records": n,
            "within_duplicate_records": dup,
            "within_duplicate_rate": round(dup / n, 4) if n else 0.0,
        }
    all_clusters = build_clusters(pairs)
    cross_clusters = sum(1 for c in all_clusters if len({r.system for r in c}) > 1)
    total = len(recs)
    review_pairs = sum(1 for p in pairs if p.band == "review")
    return {
        "kind": "dedupe",
        "entity": entity,
        "records": total,
        "auto_pairs": sum(1 for p in pairs if p.band == "auto"),
        "review_pairs": review_pairs,
        "review_pairs_per_100_records": round(100 * review_pairs / total, 2) if total else 0.0,
        "clusters": len(all_clusters),
        "clusters_spanning_both_systems": cross_clusters,
        "thresholds": {"auto": auto, "review": review},
        "systems": per_system,
    }


def render_markdown(name: str, entity: str, summary: dict, pairs: list[Pair], limit: int = 40) -> str:
    s = summary
    lines = [f"# Duplicate report: {name}", ""]
    lines += [
        f"- Record type: {'party (customer or supplier)' if entity == 'party' else 'part'}",
        f"- Records compared: {s['records']}",
        f"- Thresholds: automatic match at {s['thresholds']['auto']} or more with no conflict flags; review from {s['thresholds']['review']}",
        f"- Automatic pairs: {s['auto_pairs']}; pairs needing review: {s['review_pairs']} "
        f"({s['review_pairs_per_100_records']} per 100 records)",
        f"- Proposed merge groups: {s['clusters']}, of which {s['clusters_spanning_both_systems']} include records from both systems",
    ]
    for key in sorted(s["systems"]):
        st = s["systems"][key]
        lines.append(
            f"- {st['label']}: {st['records']} records, {st['within_duplicate_records']} would be merged away "
            f"within the same system ({st['within_duplicate_rate'] * 100:.1f}%)"
        )
    lines += ["", "An automatic pair is a proposal, not a decision. Fuzzy matching makes mistakes in both directions, "
              "so every merge needs a named person to approve it. No data has been changed.", ""]
    for band, title in (("auto", "Automatic pairs"), ("review", "Pairs needing review")):
        subset = [p for p in pairs if p.band == band]
        lines += [f"## {title} ({len(subset)})", ""]
        if not subset:
            lines += ["None.", ""]
            continue
        lines += ["| Score | Scope | Left | Right | Why |", "|---:|---|---|---|---|"]
        for p in subset[:limit]:
            lines.append(
                f"| {p.score} | {p.scope} | {p.left.system} {p.left.id} {p.left.label} | {p.right.system} {p.right.id} {p.right.label} | "
                f"{'; '.join(p.reasons)}{' [' + ','.join(sorted(p.flags)) + ']' if p.flags else ''} |"
            )
        if len(subset) > limit:
            lines.append(f"\nThe first {limit} are shown. The full list is in the matches CSV.")
        lines.append("")
    return "\n".join(lines)
