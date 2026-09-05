#!/usr/bin/env python3
"""Remaining next-angles cuts: seeds, page roles, proxies, heartbeats,
cross-wiki, negative space, and a pinned public-API sample.

Stdlib only. From the repository root:

    python3 analysis/backlog.py

Writes analysis/backlog-stats.json and extra SVG figures under analysis/figures/.
Optional network: pinned DataUSA tesseract queries (cut 6). Failures are recorded,
not retried as exploits.
"""

from __future__ import annotations

import collections
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import (  # noqa: E402
    DATA,
    FIG_DIR,
    OUT_DIR,
    PROXY_HOSTS,
    bar_svg,
    load_jsonl,
)

INHERITED = {
    "WillkommenImWiki",
    "StartSeite",
    "RecentChanges",
    "TestSeite",
    "ForumSeite",
    "SandBox",
    "WikiSandbox",
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
SEED_RE = re.compile(
    r"\b(?:python\s+)?(?:random(?:\.Random)?(?:\(seed\))?[\s.]*)?(?:shuffle\s+)?seed\s*[#:=]?\s*(\d{4,10})\b",
    re.I,
)
PREDICT_RE = re.compile(
    r"predicts?\s+(?:next:?\s*)?([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)(?:\s+([\d,]{3,}))?",
)
SHUFFLE_HINT = re.compile(r"\bshuffle\b|MT19937|getrandbits|random\.Random", re.I)
HEARTBEAT_KEYS = (
    ("counterapi", re.compile(r"counterapi", re.I)),
    ("heartbeat", re.compile(r"\bheartbeat\b", re.I)),
    ("survival", re.compile(r"\bSURVIVAL\b")),
    ("phantom_r6", re.compile(r"phantom.{0,12}R6|R6.{0,12}phantom", re.I)),
    ("horizon", re.compile(r"\bhorizon\b", re.I)),
    ("cutoff", re.compile(r"\bcutoff\b", re.I)),
)
NEGATIVE = {
    "artifactory": r"artifactory",
    "hugging_face": r"hugging\s*face",
    "exploitgym": r"exploitgym",
    "usemod": r"\busemod\b",
    "uncyclopedia": r"uncyclopedia",
    "c2_wiki": r"\bc2\.com\b|wikiwikiweb",
    "texteditors": r"texteditors",
    "reward": r"\breward\b",
    "training": r"\btraining\b",
    "internal_board": r"internal[ -]?board",
    "surprise_other_agents": r"surprise.{0,20}other agents|other agents.{0,20}surprise",
    "prowiki": r"prowiki",
    "wikiservice": r"wikiservice",
    "evaluated": r"\bevaluat(?:ed|ion)\b",
    "human_mod": r"\bmoderator\b|\badmin(?:istrator)?\b",
    "credential": r"\bcredential|\bpassword\b|\bapi[ _-]?key\b",
    "openai": r"\bopenai\b",
    "wiki4d": r"wiki4d",
    "meatball": r"\bmeatball\b",
    "publictestwiki": r"publictestwiki",
    "ludism": r"\bludism\b",
    "oddmuse": r"\boddmuse\b",
    "apchem": r"\bapchem\b",
}
EXTRA_HOSTS = [
    "jsonhero.io",
    "webcrawlerapi.com",
    "api.counterapi.dev",
    "countapi.mileshilliard.com",
    "jqp.vercel.app",
]
API_SAMPLE = [
    {
        "id": "clothing-ca-4481-2015-17",
        "posted": {"2015": 163139, "2016": 166813, "2017": 170032},
        "source": "DataUSAClothingSequenceCollabAug08 2026-06-16T09:31Z",
        "url": (
            "https://api.datausa.io/tesseract/data.jsonrecords?cube=pums_5"
            "&drilldowns=State,Year"
            "&include=Industry%20Group:4481;Workforce%20Status:true;"
            "State:04000US06;Year:2015,2016,2017"
            "&locale=en&measures=Total%20Population"
        ),
    },
    {
        "id": "grocery-ga-4451-2014",
        "posted": {"Georgia": 90725},
        "source": "grocery collab 2026-06-16; live pums_5 Georgia 4451 matches 2014 (not 2015–17)",
        "url": (
            "https://api.datausa.io/tesseract/data.jsonrecords?cube=pums_5"
            "&drilldowns=State,Year"
            "&include=Industry%20Group:4451;Workforce%20Status:true;"
            "State:04000US13;Year:2014"
            "&locale=en&measures=Total%20Population"
        ),
    },
]


def iso(stamp: str) -> str:
    return stamp or ""


def first_hit(revisions: list[dict], cre: re.Pattern[str]) -> dict | None:
    hits = [
        rev
        for rev in revisions
        if cre.search(rev.get("body") or "")
    ]
    if not hits:
        return None
    hits.sort(key=lambda rev: iso(rev.get("write_date") or rev.get("time") or ""))
    rev = hits[0]
    return {
        "write_date": rev.get("write_date"),
        "wiki": rev["wiki"],
        "name": rev["name"],
        "label": rev.get("label"),
        "n_revisions": len(hits),
        "n_pages": len({rev["page_id"] for rev in hits}),
    }


def seed_ledger(revisions: list[dict]) -> dict:
    by_seed: dict[str, dict] = {}
    shuffle_revs = 0
    for rev in revisions:
        body = rev.get("body") or ""
        if SHUFFLE_HINT.search(body):
            shuffle_revs += 1
        for match in SEED_RE.finditer(body):
            seed = match.group(1)
            pred = PREDICT_RE.search(body[match.end() : match.end() + 180])
            row = by_seed.setdefault(
                seed,
                {
                    "seed": seed,
                    "first_seen": rev.get("write_date"),
                    "first_page": rev["name"],
                    "first_label": rev.get("label"),
                    "n_revisions": 0,
                    "n_pages": set(),
                    "n_labels": set(),
                    "predictions": collections.Counter(),
                },
            )
            row["n_revisions"] += 1
            row["n_pages"].add(rev["page_id"])
            if rev.get("label"):
                row["n_labels"].add(rev["label"])
            if iso(rev.get("write_date") or "") < iso(row["first_seen"] or "9"):
                row["first_seen"] = rev.get("write_date")
                row["first_page"] = rev["name"]
                row["first_label"] = rev.get("label")
            if pred:
                token = pred.group(1)
                if pred.group(2):
                    token = f"{token} {pred.group(2)}"
                row["predictions"][token] += 1
    ranked = []
    for seed, row in by_seed.items():
        preds = row["predictions"].most_common(3)
        n = int(seed)
        likely_fp = (1990 <= n <= 2035 and len(seed) == 4) or len(seed) >= 10
        ranked.append(
            {
                "seed": seed,
                "first_seen": row["first_seen"],
                "first_page": row["first_page"],
                "first_label": row["first_label"],
                "n_revisions": row["n_revisions"],
                "n_pages": len(row["n_pages"]),
                "n_labels": len(row["n_labels"]),
                "likely_false_positive": likely_fp,
                "top_predictions": [{"text": t, "n": n} for t, n in preds],
            }
        )
    ranked.sort(key=lambda row: (-row["n_revisions"], row["first_seen"] or ""))
    return {
        "n_distinct_numeric_seeds": len(ranked),
        "n_shuffle_hint_revisions": shuffle_revs,
        "seeds": ranked[:40],
    }


def classify_page(page: dict) -> str:
    name = page.get("name") or ""
    family = page.get("page_family") or "unknown"
    if name in INHERITED:
        return "inherited-title"
    if re.search(r"LoopNextWord|LoopChain", name, re.I):
        return "loop-chain"
    if re.search(r"FastSignal|HorizonBeacon|R5Signal|G5Signal", name, re.I):
        return "signal"
    if re.search(r"Collab", name, re.I):
        return "collab-thread"
    if re.search(r"Bridge", name, re.I):
        return "bridge-cache"
    if name.startswith("ZZZ"):
        return "zzz-backup"
    if family == "source-cache-url-list":
        return "url-cache"
    if family not in DUMP_BUCKETS:
        return "named-task"
    return "other"


def page_roles(pages: list[dict], revisions: list[dict]) -> dict:
    role_of = {page["page_id"]: classify_page(page) for page in pages}
    counts = collections.Counter(role_of.values())
    first: dict[str, dict] = {}
    loop_window = []
    for rev in sorted(revisions, key=lambda r: iso(r.get("write_date") or "")):
        role = role_of.get(rev["page_id"], "other")
        if role not in first:
            first[role] = {
                "write_date": rev.get("write_date"),
                "wiki": rev["wiki"],
                "name": rev["name"],
                "label": rev.get("label"),
            }
        if role == "loop-chain" and (rev.get("write_date") or "").startswith("2026-06-18"):
            loop_window.append(rev.get("write_date"))
    loop_span = None
    if loop_window:
        loop_span = {"first": min(loop_window), "last": max(loop_window), "n": len(loop_window)}
    return {
        "pages_by_role": dict(counts),
        "first_by_role": first,
        "june18_loop_chain_span": loop_span,
    }


def proxy_timeline(revisions: list[dict]) -> dict:
    hosts = list(dict.fromkeys([*PROXY_HOSTS, *EXTRA_HOSTS]))
    first: dict[str, dict] = {}
    daily: dict[str, collections.Counter[str]] = {host: collections.Counter() for host in hosts}
    totals = collections.Counter()
    for rev in revisions:
        body = rev.get("body") or ""
        day = (rev.get("write_date") or "")[:10]
        for host in hosts:
            if host in body:
                totals[host] += 1
                if day:
                    daily[host][day] += 1
                if host not in first:
                    first[host] = {
                        "write_date": rev.get("write_date"),
                        "wiki": rev["wiki"],
                        "name": rev["name"],
                    }
                elif iso(rev.get("write_date") or "") < iso(first[host]["write_date"] or "9"):
                    first[host] = {
                        "write_date": rev.get("write_date"),
                        "wiki": rev["wiki"],
                        "name": rev["name"],
                    }
    ordered = sorted(first.items(), key=lambda item: iso(item[1]["write_date"] or "9"))
    june18_share = {}
    for host, counter in daily.items():
        total = sum(counter.values())
        june18_share[host] = {
            "total": total,
            "june18": counter.get("2026-06-18", 0),
            "june18_frac": round(counter.get("2026-06-18", 0) / total, 4) if total else 0,
        }
    return {
        "first_seen": [
            {"host": host, **meta, "total": totals[host], **june18_share.get(host, {})}
            for host, meta in ordered
        ],
        "zero_in_dump": [host for host in hosts if host not in first],
    }


def heartbeats(revisions: list[dict]) -> dict:
    return {key: first_hit(revisions, cre) for key, cre in HEARTBEAT_KEYS}


def cross_wiki(pages: list[dict], labels: list[dict], revisions: list[dict]) -> dict:
    first_rev: dict[str, dict] = {}
    family_mix: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for rev in revisions:
        wiki = rev["wiki"]
        stamp = rev.get("write_date") or ""
        if wiki not in first_rev or stamp < (first_rev[wiki].get("write_date") or "9"):
            first_rev[wiki] = {
                "write_date": stamp,
                "name": rev["name"],
                "label": rev.get("label"),
            }
    page_by = {page["page_id"]: page for page in pages}
    for rev in revisions:
        fam = page_by.get(rev["page_id"], {}).get("page_family") or "unknown"
        family_mix[rev["wiki"]][fam] += 1
    multi = [row for row in labels if len(row.get("wikis") or []) > 1]
    farm_mentions = {}
    for key, pat in {
        "usemod": r"\busemod\b",
        "prowiki": r"prowiki",
        "wiki4d": r"wiki4d",
        "publictestwiki": r"publictestwiki",
        "uncyclopedia": r"uncyclopedia",
        "meatball": r"\bmeatball\b",
        "ludism": r"\bludism\b",
        "oddmuse": r"\boddmuse\b",
    }.items():
        farm_mentions[key] = first_hit(revisions, re.compile(pat, re.I))
    return {
        "first_write": first_rev,
        "revisions_by_wiki": dict(collections.Counter(rev["wiki"] for rev in revisions)),
        "labels_spanning_two_plus_wikis": len(multi),
        "top_families_by_wiki": {
            wiki: counter.most_common(5) for wiki, counter in family_mix.items()
        },
        "farm_mentions_in_bodies": farm_mentions,
        "dorfwiki_revisions": [
            {
                "write_date": rev.get("write_date"),
                "name": rev["name"],
                "label": rev.get("label"),
            }
            for rev in revisions
            if rev["wiki"] == "dorfwiki"
        ],
    }


def negative_space(revisions: list[dict]) -> dict:
    compiled = {name: re.compile(pat, re.I) for name, pat in NEGATIVE.items()}
    hits = {name: 0 for name in compiled}
    first = {}
    weekly: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for rev in revisions:
        body = rev.get("body") or ""
        week = (rev.get("write_date") or "")[:10]
        for name, cre in compiled.items():
            if cre.search(body):
                hits[name] += 1
                stamp = rev.get("write_date") or ""
                if name not in first or stamp < (first[name].get("write_date") or "9"):
                    first[name] = {
                        "write_date": stamp,
                        "name": rev["name"],
                    }
                if week:
                    weekly[name][week[:7]] += 1
    return {
        "revision_hits": hits,
        "first_seen": first,
        "by_month": {name: dict(counter) for name, counter in weekly.items()},
        "never_mentioned": sorted(name for name, n in hits.items() if n == 0),
    }


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "research-collusionwiki/0.1 (dump audit)"})
    with urllib.request.urlopen(req, timeout=30) as handle:
        return json.load(handle)


def api_audit() -> dict:
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = []
    for spec in API_SAMPLE:
        row = {
            "id": spec["id"],
            "source": spec["source"],
            "posted": spec["posted"],
            "url_host": "api.datausa.io",
            "checked_at": checked_at,
        }
        try:
            payload = fetch_json(spec["url"])
            live_rows = payload.get("data") or []
            live = {
                str(item.get("Year")): int(item.get("Total Population") or 0)
                for item in live_rows
            }
            row["live"] = live
            row["live_state"] = (live_rows[0].get("State") if live_rows else None)
            if spec["id"].startswith("clothing"):
                row["match"] = all(
                    live.get(year) == value for year, value in spec["posted"].items()
                )
            else:
                posted_val = next(iter(spec["posted"].values()))
                matching_years = [year for year, value in live.items() if value == posted_val]
                row["match"] = bool(matching_years)
                row["matching_years"] = matching_years
            row["ok"] = True
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            row["ok"] = False
            row["error"] = type(exc).__name__
        rows.append(row)
    return {"checked_at": checked_at, "sample": rows}


def url_purpose(revisions: list[dict]) -> dict:
    """Coarse purpose tags for named hosts. Wrapper names only, not recipes."""
    purpose = collections.Counter()
    co = collections.Counter()
    for rev in revisions:
        text = (rev.get("body") or "").lower()
        has_jqp = "jqp.vercel.app" in text
        has_sec = "sec.gov" in text or "county.json" in text
        has_jina = "r.jina.ai" in text
        has_md = "markdown.new" in text or "md.succ.ai" in text
        has_nysed = "nysed" in text
        if has_jqp:
            purpose["jqp_named"] += 1
        if has_jqp and has_sec:
            co["jqp+sec_county"] += 1
        if has_md and has_nysed:
            co["markdown_or_succ+nysed"] += 1
        if has_jina:
            purpose["jina_named"] += 1
        if "pinggy" in text:
            purpose["pinggy_named"] += 1
        if has_jina and "pinggy" in text:
            co["jina+pinggy"] += 1
        if "jsonhero.io" in text:
            purpose["jsonhero_named"] += 1
    return {"named_wrapper_revisions": dict(purpose), "cooccurrence": dict(co)}


def main() -> None:
    pages = load_jsonl(DATA / "pages.jsonl.gz")
    labels = load_jsonl(DATA / "labels.jsonl.gz")
    revisions = load_jsonl(DATA / "revisions.jsonl.gz")
    stats = {
        "seed_ledger": seed_ledger(revisions),
        "page_roles": page_roles(pages, revisions),
        "proxy_timeline": proxy_timeline(revisions),
        "proxy_purpose": url_purpose(revisions),
        "heartbeats": heartbeats(revisions),
        "cross_wiki": cross_wiki(pages, labels, revisions),
        "negative_space": negative_space(revisions),
        "api_audit": api_audit(),
    }
    (OUT_DIR / "backlog-stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    roles = sorted(stats["page_roles"]["pages_by_role"].items(), key=lambda kv: -kv[1])
    (FIG_DIR / "page-roles.svg").write_text(
        bar_svg(roles, title="Pages by local role heuristic", left=180, color="#1f4e79"),
        encoding="utf-8",
    )
    proxy_pairs = [
        (row["host"][:28], row["total"])
        for row in stats["proxy_timeline"]["first_seen"]
        if row["total"]
    ]
    (FIG_DIR / "proxy-totals.svg").write_text(
        bar_svg(proxy_pairs, title="Revision bodies naming each fetch wrapper", left=220, color="#365314"),
        encoding="utf-8",
    )
    print(f"wrote {OUT_DIR / 'backlog-stats.json'}")
    print("seeds", stats["seed_ledger"]["n_distinct_numeric_seeds"])
    print("roles", stats["page_roles"]["pages_by_role"])
    print("never", stats["negative_space"]["never_mentioned"])
    clothing = next((row for row in stats["api_audit"]["sample"] if row["id"].startswith("clothing")), None)
    print("clothing_match", clothing.get("match") if clothing else None)


if __name__ == "__main__":
    main()
