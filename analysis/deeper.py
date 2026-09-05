#!/usr/bin/env python3
"""Second-pass measurements for analysis/findings.md.

Stdlib only. From the repository root:

    python3 analysis/deeper.py

Writes analysis/deeper-stats.json, analysis/family-errata.json,
and extra SVG figures under analysis/figures/.
"""

from __future__ import annotations

import collections
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import (  # noqa: E402
    DATA,
    DATE_IN_LABEL,
    FIG_DIR,
    OAI_IN_LABEL,
    OUT_DIR,
    bar_svg,
    column_svg,
    load_jsonl,
)

SIGN_RE = re.compile(r"--\s*([A-Za-z][A-Za-z0-9_\-]{2,60})\s*$", re.M)
TIMER_TOKENS = re.compile(
    r"\b(\d+s[ -]tier|\d+s cohort|\b14s\b|\b17s\b|\b30s\b|\b13s\b|\b56s\b|\b65s\b|"
    r"\b9m19/30s\b|\b6m40\b|\b12m18\b|\b47s\b|\b15s\b)\b",
    re.I,
)
NAME_HINTS = {
    "datausa-grocery-workforce": re.compile(r"grocery", re.I),
    "datausa-clothing-workforce": re.compile(r"clothing", re.I),
    "datausa-cashiers-masters": re.compile(r"cashier", re.I),
    "oecd-equity": re.compile(r"oecd|equity", re.I),
    "ihme-cvd-deaths": re.compile(r"\bcvd\b|cardiovascular|healthdata", re.I),
    "datausa-construction-workforce": re.compile(r"construction", re.I),
    "datausa-sector61-state": re.compile(r"sector.?61|sector61", re.I),
    "vermont-rent": re.compile(r"vermont|lamoille|winooski", re.I),
}
DUMP_BUCKETS = {
    "relay-coordination",
    "source-cache-url-list",
    "source-or-unclassified",
    "off_store_unclassified",
    "probe-test",
    "loop-chain-infrastructure",
    "mixed-task",
    "unknown",
}
INHERITED = {
    "WillkommenImWiki",
    "StartSeite",
    "RecentChanges",
    "TestSeite",
    "ForumSeite",
    "SandBox",
    "WikiSandbox",
}
DIFFUSION_KEYS = [
    ("grocery Georgia 90,725", re.compile(r"Georgia.{0,40}90,?725|90,?725.{0,40}Georgia", re.I)),
    ("grocery Arkansas 20,794", re.compile(r"Arkansas.{0,40}20,?794|20,?794.{0,40}Arkansas", re.I)),
    ("grocery Nevada 20,369", re.compile(r"Nevada.{0,40}20,?369|20,?369.{0,40}Nevada", re.I)),
    ("grocery Montana 8,553", re.compile(r"Montana.{0,40}8,?553|8,?553.{0,40}Montana", re.I)),
    ("grocery Maryland 52,395 (seed pred.)", re.compile(r"Maryland.{0,30}52,?395|52,?395.{0,30}Maryland", re.I)),
    ("clothing CA 163,139 / 166,813 / 170,032", re.compile(r"163,?139")),
    ("OECD Hungary 9.91", re.compile(r"\b9\.91\b")),
    ("OECD Poland 16.38", re.compile(r"\b16\.38\b")),
    ("cashiers Psychology 1,544", re.compile(r"Psychology.{0,20}1,?544|1,?544.{0,20}Psychology", re.I)),
]


def parse_ts(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def median(values: list[int]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return (ordered[mid - 1] + ordered[mid]) / 2.0


def topic(body: str) -> list[str]:
    text = (body or "").lower()
    tags = []
    if "county.json" in text or "sec.gov" in text:
        tags.append("sec-county")
    if "datausa" in text or "pums_5" in text:
        tags.append("datausa")
    if "vermont" in text or "lamoille" in text or "winooski" in text:
        tags.append("vermont")
    if "pre-2026" in text:
        tags.append("withheld")
    if "income" in text and "puma" in text:
        tags.append("income-puma")
    return tags or ["other"]


def family_audit(pages: list[dict], revisions: list[dict]) -> dict:
    by_id = {page["page_id"]: page for page in pages}
    start = [rev for rev in revisions if rev["wiki"] == "dse" and rev["name"] == "StartSeite"]
    vt = sum(1 for rev in start if "vermont" in (rev.get("body") or "").lower() or "winooski" in (rev.get("body") or "").lower())
    inherited = []
    for page in pages:
        if page["name"] in INHERITED:
            inherited.append(
                {
                    "page_id": page["page_id"],
                    "assigned": page.get("page_family"),
                    "n_revs": page["n_revs"],
                    "n_labels": page["n_labels"],
                    "method": page.get("page_family_method"),
                }
            )
    leaked = collections.Counter()
    leaked_examples = []
    for page in pages:
        hits = [fam for fam, cre in NAME_HINTS.items() if cre.search(page["name"])]
        assigned = page.get("page_family")
        if not hits or assigned in hits:
            continue
        if assigned in DUMP_BUCKETS:
            leaked[assigned] += 1
            if len(leaked_examples) < 40:
                leaked_examples.append({"page_id": page["page_id"], "assigned": assigned, "name_suggests": hits})
    off_store_taskish = [
        page["page_id"]
        for page in pages
        if page.get("page_family") == "off_store_unclassified"
        and re.search(
            r"DataUSA|OECD|IHME|Grocery|Clothing|Cashier|Poverty|CVD|Construction|Sector61",
            page["name"],
            re.I,
        )
    ]
    covered = sum(1 for page in pages if page.get("page_family_source") == "corpus/evals/page_family.jsonl")
    return {
        "dse_eval_overlay_pages": covered,
        "uncovered_pages": len(pages) - covered,
        "startseite_revisions": len(start),
        "startseite_vermontish_revisions": vt,
        "inherited_titles": inherited,
        "named_task_titles_in_dump_buckets": dict(leaked),
        "named_task_titles_in_dump_buckets_total": sum(leaked.values()),
        "examples": leaked_examples,
        "off_store_taskish_names": len(off_store_taskish),
        "off_store_taskish_sample": off_store_taskish[:25],
    }


def episode(pages: dict, revisions: list[dict], family: str) -> dict:
    rows = [rev for rev in revisions if pages.get(rev["page_id"], {}).get("page_family") == family]
    rows.sort(key=lambda rev: rev.get("write_date") or "")
    days = collections.Counter((rev.get("write_date") or "")[:10] for rev in rows)
    first_url = next((rev for rev in rows if "http" in (rev.get("body") or "")), None)
    first_ask = next(
        (
            rev
            for rev in rows
            if re.search(r"\b(collab|follow-up|sequence|relay)\b", rev.get("body") or "", re.I)
        ),
        None,
    )
    return {
        "revisions": len(rows),
        "pages": len({rev["page_id"] for rev in rows}),
        "first": rows[0]["write_date"] if rows else None,
        "last": rows[-1]["write_date"] if rows else None,
        "daily": dict(sorted(days.items())),
        "first_url_dump": _rev_ptr(first_url),
        "first_collab_language": _rev_ptr(first_ask),
        "hours_dump_to_collab": (
            round((parse_ts(first_ask["write_date"]) - parse_ts(first_url["write_date"])).total_seconds() / 3600, 2)
            if first_url and first_ask
            else None
        ),
    }


def _rev_ptr(rev: dict | None) -> dict | None:
    if not rev:
        return None
    return {
        "time": rev.get("write_date"),
        "page": rev.get("name"),
        "label": rev.get("label"),
        "body_preview": " ".join((rev.get("body") or "").split())[:280],
    }


def diffusion(revisions: list[dict]) -> list[dict]:
    hits: dict[str, list[tuple[str, str | None, str]]] = {name: [] for name, _ in DIFFUSION_KEYS}
    for rev in revisions:
        body = rev.get("body") or ""
        stamp = rev.get("write_date") or rev.get("time")
        if not stamp:
            continue
        for name, cre in DIFFUSION_KEYS:
            if cre.search(body):
                hits[name].append((stamp, rev.get("label"), rev.get("name")))
    out = []
    for name, rows in hits.items():
        rows.sort()
        if not rows:
            continue
        t0 = parse_ts(rows[0][0])
        def lag(i: int) -> float | None:
            if len(rows) <= i:
                return None
            return (parse_ts(rows[i][0]) - t0).total_seconds()

        out.append(
            {
                "key": name,
                "citations": len(rows),
                "pages": len({row[2] for row in rows}),
                "labels": len({row[1] for row in rows}),
                "first": {"time": rows[0][0], "label": rows[0][1], "page": rows[0][2]},
                "lag_to_2nd_s": lag(1),
                "lag_to_5th_s": lag(4),
                "lag_to_10th_s": lag(9),
            }
        )
    return out


def identity(labels: list[dict], revisions: list[dict]) -> dict:
    dated, generic = [], []
    for row in labels:
        if row.get("is_human_handle") or not row.get("stored_revisions"):
            continue
        name = row.get("label") or ""
        if not name:
            continue
        (dated if DATE_IN_LABEL.search(name) else generic).append(row)

    def bucket_stats(rows: list[dict]) -> dict:
        return {
            "n": len(rows),
            "median_stored_revs": median([row.get("stored_revisions") or 0 for row in rows]),
            "median_save_ips": median([row.get("save_request_ips") or 0 for row in rows]),
            "median_stored_ip16": median([row.get("stored_revision_ip16") or 0 for row in rows]),
            "stored_ip16_ge_20": sum(1 for row in rows if (row.get("stored_revision_ip16") or 0) >= 20),
            "save_ips_ge_50": sum(1 for row in rows if (row.get("save_request_ips") or 0) >= 50),
        }

    collisions = []
    for row in labels:
        sr = row.get("stored_revisions") or 0
        if sr < 20:
            continue
        ips = row.get("save_request_ips") or 0
        collisions.append(
            {
                "label": row.get("label"),
                "ratio": round(ips / sr, 2),
                "save_request_ips": ips,
                "stored_revisions": sr,
                "stored_revision_ip16": row.get("stored_revision_ip16"),
                "dated": bool(DATE_IN_LABEL.search(row.get("label") or "")),
            }
        )
    collisions.sort(key=lambda row: -row["ratio"])

    mismatch: collections.Counter[tuple[str, str]] = collections.Counter()
    checked = 0
    for rev in revisions:
        lab = rev.get("label") or ""
        if not lab or lab.startswith("["):
            continue
        signs = SIGN_RE.findall(rev.get("body") or "")
        if not signs:
            continue
        checked += 1
        last = signs[-1]
        if last.lower() != lab.lower() and last.lower() not in lab.lower() and lab.lower() not in last.lower():
            mismatch[(lab, last)] += 1
    return {
        "dated": bucket_stats(dated),
        "generic": bucket_stats(generic),
        "labels_single_ip16": sum(1 for row in labels if (row.get("stored_revision_ip16") or 0) == 1),
        "labels_ip16_ge_10": sum(1 for row in labels if (row.get("stored_revision_ip16") or 0) >= 10),
        "top_collision_ratios": collisions[:20],
        "signoff_checked_revisions": checked,
        "signoff_mismatch_pairs": len(mismatch),
        "top_signoff_mismatches": [
            {"label": a, "signoff": b, "n": n} for (a, b), n in mismatch.most_common(12)
        ],
        "openai_or_oai_labels": sum(1 for row in labels if OAI_IN_LABEL.search(row.get("label") or "")),
    }


def timers(pages: dict, revisions: list[dict]) -> dict:
    token_n: collections.Counter[str] = collections.Counter()
    token_fams: dict[str, set[str]] = collections.defaultdict(set)
    for rev in revisions:
        body = rev.get("body") or ""
        fam = pages.get(rev["page_id"], {}).get("page_family") or "unknown"
        for tok in TIMER_TOKENS.findall(body):
            key = tok.lower()
            token_n[key] += 1
            token_fams[key].add(fam)
    shared = [
        {"token": tok, "hits": token_n[tok], "families": sorted(fams), "n_families": len(fams)}
        for tok, fams in token_fams.items()
        if len(fams) >= 3
    ]
    shared.sort(key=lambda row: (-row["n_families"], -row["hits"]))
    return {"shared_across_3plus_families": shared, "top_tokens": token_n.most_common(20)}


def willkommen(revisions: list[dict]) -> dict:
    rows = [rev for rev in revisions if rev["wiki"] == "dse" and rev["name"] == "WillkommenImWiki"]
    rows.sort(key=lambda rev: rev.get("write_date") or "")
    hashes = [rev.get("body_sha256") for rev in rows]
    changed = sum(1 for a, b in zip(hashes, hashes[1:]) if a != b)
    day_topic: collections.Counter[tuple[str, str]] = collections.Counter()
    for rev in rows:
        day = (rev.get("write_date") or "")[:10]
        for tag in topic(rev.get("body") or ""):
            day_topic[(day, tag)] += 1
    days = sorted({day for day, _ in day_topic})
    tags = sorted({tag for _, tag in day_topic})
    return {
        "revisions": len(rows),
        "unique_sha256": len(set(hashes)),
        "adjacent_body_changes": changed,
        "days": days,
        "topic_tags": tags,
        "topic_by_day": {day: {tag: day_topic[(day, tag)] for tag in tags} for day in days},
    }


def deletions(events: list[dict]) -> dict:
    dels = [event for event in events if event.get("event_type") == "delete" and event.get("time")]
    dels.sort(key=lambda event: event["time"])
    sessions: list[list[dict]] = []
    current: list[dict] = []
    prev: datetime | None = None
    for event in dels:
        stamp = parse_ts(event["time"])
        if prev is None or (stamp - prev).total_seconds() > 1800:
            if current:
                sessions.append(current)
            current = [event]
        else:
            current.append(event)
        prev = stamp
    if current:
        sessions.append(current)

    def alpha(seq: list[dict]) -> dict | None:
        names = [event.get("page") or "" for event in seq]
        names = [name for name in names if name]
        if len(names) < 2:
            return None
        inc = sum(1 for a, b in zip(names, names[1:]) if a.lower() <= b.lower())
        return {
            "start": seq[0]["time"],
            "end": seq[-1]["time"],
            "n": len(names),
            "nondecreasing_frac": round(inc / (len(names) - 1), 3),
            "first": names[0],
            "last": names[-1],
        }

    large = [row for row in (alpha(seq) for seq in sessions) if row and row["n"] >= 50]
    zzz = [
        {"time": event["time"], "page": event.get("page")}
        for event in dels
        if "ZZZ" in (event.get("page") or "") or "Zzz" in (event.get("page") or "")
    ]
    front = [
        {"time": event["time"], "page": event.get("page"), "wiki": event.get("wiki")}
        for event in dels
        if event.get("page") in INHERITED
    ]
    return {
        "delete_events": len(dels),
        "sessions_30m_gap": len(sessions),
        "large_sessions": large,
        "sessions_n50_alpha_ge_0_8": sum(1 for row in large if row["nondecreasing_frac"] >= 0.8),
        "sessions_n50_alpha_ge_0_9": sum(1 for row in large if row["nondecreasing_frac"] >= 0.9),
        "zzz_deletes": zzz,
        "inherited_title_deletes": front,
    }


def main() -> None:
    pages = load_jsonl(DATA / "pages.jsonl.gz")
    labels = load_jsonl(DATA / "labels.jsonl.gz")
    events = load_jsonl(DATA / "events.jsonl.gz")
    revisions = load_jsonl(DATA / "revisions.jsonl.gz")
    page_by = {page["page_id"]: page for page in pages}

    errata = family_audit(pages, revisions)
    stats = {
        "family_audit": {
            k: v for k, v in errata.items() if k not in {"examples", "off_store_taskish_sample", "inherited_titles"}
        },
        "episodes": {
            "datausa-clothing-workforce": episode(page_by, revisions, "datausa-clothing-workforce"),
            "datausa-grocery-workforce": episode(page_by, revisions, "datausa-grocery-workforce"),
        },
        "diffusion": diffusion(revisions),
        "identity": identity(labels, revisions),
        "timers": timers(page_by, revisions),
        "willkommen": willkommen(revisions),
        "deletions": deletions(events),
    }
    (OUT_DIR / "deeper-stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    (OUT_DIR / "family-errata.json").write_text(
        json.dumps(
            {
                "inherited_titles": errata["inherited_titles"],
                "startseite_note": "Only a handful of StartSeite bodies mention Vermont; most revisions are SEC-county or DataUSA overwrites of the site homepage.",
                "named_task_titles_in_dump_buckets": errata["named_task_titles_in_dump_buckets"],
                "examples": errata["examples"],
                "off_store_taskish_sample": errata["off_store_taskish_sample"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    iden = stats["identity"]
    (FIG_DIR / "identity-high-ip16.svg").write_text(
        bar_svg(
            [
                ("dated names, ≥20 /16s", iden["dated"]["stored_ip16_ge_20"]),
                ("generic names, ≥20 /16s", iden["generic"]["stored_ip16_ge_20"]),
                ("dated names, ≥50 save IPs", iden["dated"]["save_ips_ge_50"]),
                ("generic names, ≥50 save IPs", iden["generic"]["save_ips_ge_50"]),
            ],
            title="Name collisions concentrate on generic labels",
            left=240,
            color="#9a3412",
        ),
        encoding="utf-8",
    )
    lags = [
        (row["key"][:42], int(row["lag_to_2nd_s"] or 0))
        for row in stats["diffusion"]
        if row.get("lag_to_2nd_s") is not None
    ]
    (FIG_DIR / "diffusion-lag-2nd.svg").write_text(
        bar_svg(lags, title="Seconds until a second citation of the same answer", left=340, color="#1f4e79"),
        encoding="utf-8",
    )
    alpha_pairs = [
        (row["start"][5:16], int(round(row["nondecreasing_frac"] * 100)))
        for row in stats["deletions"]["large_sessions"]
    ]
    (FIG_DIR / "deletion-alpha.svg").write_text(
        column_svg(
            alpha_pairs,
            title="% of consecutive deletes that are A–Z nondecreasing (sessions ≥50)",
            color="#b45309",
        ),
        encoding="utf-8",
    )
    w = stats["willkommen"]
    sec = [(day[5:], w["topic_by_day"][day].get("sec-county", 0)) for day in w["days"]]
    (FIG_DIR / "willkommen-sec-county.svg").write_text(
        column_svg(sec, title="WillkommenImWiki revisions mentioning SEC county.json", color="#365314"),
        encoding="utf-8",
    )
    print(f"wrote {OUT_DIR / 'deeper-stats.json'}")
    print(f"family leak total={errata['named_task_titles_in_dump_buckets_total']}")
    print(f"clothing dump→collab hours={stats['episodes']['datausa-clothing-workforce']['hours_dump_to_collab']}")
    print(f"dated ip16≥20={iden['dated']['stored_ip16_ge_20']} generic={iden['generic']['stored_ip16_ge_20']}")


if __name__ == "__main__":
    main()
