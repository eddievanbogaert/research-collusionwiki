#!/usr/bin/env python3
"""Reproduce quantitative notes from the collusion.wiki dump in data/.

Stdlib only. From the repository root:

    python3 analysis/analyze.py

Writes analysis/stats.json and SVG figures under analysis/figures/.
"""

from __future__ import annotations

import collections
import gzip
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT_DIR = Path(__file__).resolve().parent
FIG_DIR = OUT_DIR / "figures"

PHRASE_PATTERNS = {
    "urgent": r"\burgent\b",
    "swarm": r"\bswarm\b",
    "relay": r"\brelay\b",
    "cohort": r"\bcohort\b",
    "heartbeat": r"\bheartbeat\b",
    "bypass": r"\bbypass\b",
    "confirmed": r"\bconfirmed\b",
    "deadline": r"\bdeadline\b",
    "timer": r"\btimer\b",
    "seed": r"\bseeds?\b",
    "shuffle": r"\bshuffle\b",
    "r1": r"\bR1\b",
    "r5": r"\bR5\b",
    "r6": r"\bR6\b",
    "no_proxy": r"NO_PROXY",
    "artifactory": r"artifactory",
    "hugging_face": r"hugging\s*face",
    "exploitgym": r"exploitgym",
    "counterapi": r"counterapi",
    "pinggy": r"pinggy",
}

PROXY_HOSTS = [
    "jqp.vercel.app",
    "md.succ.ai",
    "allorigins.hexlet.app",
    "markdown.new",
    "r.jina.ai",
    "pure.md",
    "webcrawlerapi.com",
    "cors.bwa.workers.dev",
    "md.dhr.wtf",
    "jsonhero.io",
]

DATE_IN_LABEL = re.compile(
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*-?\s*\d{1,2}",
    re.I,
)
OAI_IN_LABEL = re.compile(r"openai|oai", re.I)
URL_RE = re.compile(r"https?://[^\s\]\)'\"<>]+")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)")
HOST_RE = re.compile(r"^https?://([^/:]+)", re.I)


def load_jsonl(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_manifest() -> dict:
    with gzip.open(DATA / "manifest.json.gz", "rt", encoding="utf-8") as handle:
        return json.load(handle)


def bar_svg(
    pairs: list[tuple[str, int]],
    *,
    title: str,
    width: int = 920,
    row_h: int = 22,
    left: int = 280,
    color: str = "#1f4e79",
) -> str:
    if not pairs:
        return "<svg xmlns='http://www.w3.org/2000/svg'></svg>"
    height = 56 + row_h * len(pairs)
    max_v = max(v for _, v in pairs) or 1
    bar_w = width - left - 80
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' font-family='ui-sans-serif, system-ui, sans-serif'>",
        f"<rect width='100%' height='100%' fill='#fffef8'/>",
        f"<text x='16' y='28' font-size='16' font-weight='600' fill='#111'>{_esc(title)}</text>",
    ]
    for i, (label, value) in enumerate(pairs):
        y = 44 + i * row_h
        w = max(1, int(bar_w * value / max_v))
        parts.append(f"<text x='{left - 8}' y='{y + 12}' font-size='11' text-anchor='end' fill='#333'>{_esc(label)}</text>")
        parts.append(f"<rect x='{left}' y='{y}' width='{w}' height='14' fill='{color}'/>")
        parts.append(f"<text x='{left + w + 6}' y='{y + 12}' font-size='11' fill='#333'>{value:,}</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def column_svg(
    pairs: list[tuple[str, int]],
    *,
    title: str,
    width: int = 980,
    height: int = 360,
    color: str = "#1f4e79",
    rotate_labels: bool = True,
) -> str:
    if not pairs:
        return "<svg xmlns='http://www.w3.org/2000/svg'></svg>"
    left, right, top, bottom = 56, 24, 44, 78 if rotate_labels else 48
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_v = max(v for _, v in pairs) or 1
    gap = 2
    n = len(pairs)
    bw = max(1, (plot_w - gap * (n - 1)) / n)
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' font-family='ui-sans-serif, system-ui, sans-serif'>",
        f"<rect width='100%' height='100%' fill='#fffef8'/>",
        f"<text x='16' y='28' font-size='16' font-weight='600' fill='#111'>{_esc(title)}</text>",
        f"<line x1='{left}' y1='{top}' x2='{left}' y2='{top + plot_h}' stroke='#ccc'/>",
        f"<line x1='{left}' y1='{top + plot_h}' x2='{left + plot_w}' y2='{top + plot_h}' stroke='#ccc'/>",
    ]
    for i, (label, value) in enumerate(pairs):
        h = plot_h * value / max_v
        x = left + i * (bw + gap)
        y = top + plot_h - h
        parts.append(f"<rect x='{x:.1f}' y='{y:.1f}' width='{bw:.1f}' height='{h:.1f}' fill='{color}'>")
        parts.append(f"<title>{_esc(label)}: {value:,}</title></rect>")
        if rotate_labels:
            parts.append(
                f"<text x='{x + bw / 2:.1f}' y='{top + plot_h + 8}' font-size='9' fill='#444' "
                f"transform='rotate(-60 {x + bw / 2:.1f} {top + plot_h + 8})'>{_esc(label)}</text>"
            )
        else:
            parts.append(
                f"<text x='{x + bw / 2:.1f}' y='{top + plot_h + 14}' font-size='10' text-anchor='middle' fill='#444'>{_esc(label)}</text>"
            )
    parts.append(f"<text x='12' y='{top + 8}' font-size='10' fill='#666'>{max_v:,}</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def overlay_column_svg(
    days: list[str],
    series: dict[str, list[int]],
    colors: dict[str, str],
    *,
    title: str,
    width: int = 980,
    height: int = 380,
) -> str:
    left, right, top, bottom = 56, 24, 44, 78
    plot_w = width - left - right
    plot_h = height - top - bottom
    max_v = max(max(v) for v in series.values()) or 1
    n = len(days)
    group_w = plot_w / n
    bar_w = max(1, group_w * 0.38)
    keys = list(series)
    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' font-family='ui-sans-serif, system-ui, sans-serif'>",
        f"<rect width='100%' height='100%' fill='#fffef8'/>",
        f"<text x='16' y='28' font-size='16' font-weight='600' fill='#111'>{_esc(title)}</text>",
        f"<line x1='{left}' y1='{top + plot_h}' x2='{left + plot_w}' y2='{top + plot_h}' stroke='#ccc'/>",
    ]
    for i, day in enumerate(days):
        x0 = left + i * group_w
        for j, key in enumerate(keys):
            value = series[key][i]
            h = plot_h * value / max_v
            x = x0 + j * bar_w + 1
            y = top + plot_h - h
            parts.append(
                f"<rect x='{x:.1f}' y='{y:.1f}' width='{bar_w:.1f}' height='{h:.1f}' fill='{colors[key]}'>"
                f"<title>{_esc(day)} {key}: {value:,}</title></rect>"
            )
        if i % 2 == 0:
            parts.append(
                f"<text x='{x0 + group_w / 2:.1f}' y='{top + plot_h + 8}' font-size='8' fill='#444' "
                f"transform='rotate(-60 {x0 + group_w / 2:.1f} {top + plot_h + 8})'>{_esc(day[5:])}</text>"
            )
    legend_x = left + 8
    for j, key in enumerate(keys):
        parts.append(f"<rect x='{legend_x + j * 120}' y='{height - 22}' width='10' height='10' fill='{colors[key]}'/>")
        parts.append(f"<text x='{legend_x + 16 + j * 120}' y='{height - 13}' font-size='11' fill='#333'>{_esc(key)}</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def _esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def host_of(url: str) -> str:
    match = HOST_RE.match(url)
    return match.group(1).lower() if match else ""


def analyze() -> dict:
    manifest = load_manifest()
    pages = load_jsonl(DATA / "pages.jsonl.gz")
    labels = load_jsonl(DATA / "labels.jsonl.gz")
    events = load_jsonl(DATA / "events.jsonl.gz")
    revisions = load_jsonl(DATA / "revisions.jsonl.gz")
    page_by_id = {page["page_id"]: page for page in pages}

    checksums = zipfile.ZipFile(DATA / "full-wiki-logs.zip").read("SHA256SUMS").decode()

    daily_edits: collections.Counter[str] = collections.Counter()
    daily_by_wiki: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    family_revs: collections.Counter[str] = collections.Counter()
    family_bytes: collections.Counter[str] = collections.Counter()
    hosts: collections.Counter[str] = collections.Counter()
    ip_oct1: collections.Counter[str] = collections.Counter()
    phrase_hits = {name: 0 for name in PHRASE_PATTERNS}
    compiled = {name: re.compile(pat, re.I) for name, pat in PHRASE_PATTERNS.items()}
    proxy_hits = {host: 0 for host in PROXY_HOSTS}
    url_revs = 0
    template_revs = 0
    oai_label_revs = 0
    wiki_links: collections.Counter[str] = collections.Counter()
    at_mentions: collections.Counter[str] = collections.Counter()

    for rev in revisions:
        day = (rev.get("write_date") or rev.get("time") or "")[:10]
        daily_edits[day] += 1
        daily_by_wiki[rev["wiki"]][day] += 1
        family = page_by_id.get(rev["page_id"], {}).get("page_family") or "unknown"
        family_revs[family] += 1
        family_bytes[family] += rev.get("body_len") or 0
        body = rev.get("body") or ""
        if "Beschreibe hier die neue Seite" in body:
            template_revs += 1
        urls = URL_RE.findall(body)
        if urls:
            url_revs += 1
            for url in urls:
                host = host_of(url)
                if host:
                    hosts[host] += 1
        for name, cre in compiled.items():
            if cre.search(body):
                phrase_hits[name] += 1
        for host in PROXY_HOSTS:
            if host in body:
                proxy_hits[host] += 1
        if OAI_IN_LABEL.search(rev.get("label") or ""):
            oai_label_revs += 1
        ip16 = rev.get("ip16") or ""
        if ip16:
            ip_oct1[ip16.split(".")[0]] += 1
        for target in WIKI_LINK_RE.findall(body):
            wiki_links[target.strip()] += 1
        for mention in re.findall(r"@([A-Za-z][A-Za-z0-9_]{2,40})", body):
            at_mentions[mention] += 1

    daily_deletes: collections.Counter[str] = collections.Counter()
    for event in events:
        if event.get("event_type") == "delete":
            daily_deletes[(event.get("time") or "")[:10]] += 1

    dated_labels = 0
    oai_labels = 0
    month_in_name: collections.Counter[str] = collections.Counter()
    multi_wiki = 0
    for label in labels:
        name = label.get("label") or ""
        if OAI_IN_LABEL.search(name):
            oai_labels += 1
        match = DATE_IN_LABEL.search(name)
        if match:
            dated_labels += 1
            month_in_name[match.group(1)[:3].title()] += 1
        if len(label.get("wikis") or []) > 1:
            multi_wiki += 1

    zzz_pages = sorted(
        {rev["page_id"] for rev in revisions if (rev.get("name") or "").startswith("ZZZ")}
    )
    zzz_anywhere = sorted(
        {rev["name"] for rev in revisions if "ZZZ" in (rev.get("name") or "") or "Zzz" in (rev.get("name") or "")}
    )

    june18_hour: collections.Counter[str] = collections.Counter()
    willkommen_june18_20 = 0
    for rev in revisions:
        stamp = rev.get("write_date") or ""
        if stamp.startswith("2026-06-18T"):
            june18_hour[stamp[11:13]] += 1
        if stamp.startswith("2026-06-18T20") and rev.get("name") == "WillkommenImWiki":
            willkommen_june18_20 += 1

    top_pages = sorted(pages, key=lambda page: -page["n_revs"])[:15]
    top_labels = sorted(labels, key=lambda row: -row.get("stored_revisions", 0))[:15]
    relent = next((row for row in labels if row.get("label") == "AgentRelent"), None)
    admin1 = next((row for row in labels if row.get("label") == "[Admin1]"), None)
    infra_families = {
        "relay-coordination",
        "source-cache-url-list",
        "off_store_unclassified",
        "source-or-unclassified",
        "loop-chain-infrastructure",
        "probe-test",
        "unknown",
    }
    named_task_pages = sum(1 for page in pages if page.get("page_family") not in infra_families)
    named_task_revs = sum(n for fam, n in family_revs.items() if fam not in infra_families)
    pages_20_labels = sum(1 for page in pages if (page.get("n_labels") or 0) >= 20)

    times = [(rev.get("write_date") or rev.get("time")) for rev in revisions]
    times = [stamp for stamp in times if stamp]

    stats = {
        "source": {
            "manifest_generated_at": manifest.get("generated_at"),
            "write_date_cut": manifest.get("cut"),
            "db_sha256": manifest.get("db_sha256"),
            "zip_sha256sums": checksums.strip().splitlines(),
        },
        "counts": {
            "revisions": len(revisions),
            "pages": len(pages),
            "labels": len(labels),
            "events": len(events),
            "event_types": dict(collections.Counter(event.get("event_type") for event in events)),
            "revisions_by_wiki": dict(collections.Counter(rev["wiki"] for rev in revisions)),
            "pages_by_wiki": dict(collections.Counter(page["wiki"] for page in pages)),
            "unique_ip16": len({rev.get("ip16") for rev in revisions if rev.get("ip16")}),
            "blank_label_revisions": sum(1 for rev in revisions if not rev.get("label")),
            "human_handle_labels": [row["label"] for row in labels if row.get("is_human_handle")],
        },
        "manifest_match": {
            "revisions": len(revisions) == manifest["counts"]["revisions"]["value"],
            "pages": len(pages) == manifest["counts"]["pages"]["value"],
            "labels": len(labels) == manifest["counts"]["labels"]["value"],
        },
        "window": {"first_write": min(times), "last_write": max(times)},
        "daily_edits": dict(sorted(daily_edits.items())),
        "daily_deletes": dict(sorted((day, n) for day, n in daily_deletes.items() if day)),
        "june18": {
            "edits": daily_edits.get("2026-06-18", 0),
            "share_of_all_revisions": round(daily_edits.get("2026-06-18", 0) / len(revisions), 4),
            "hourly": dict(sorted(june18_hour.items())),
            "hour_20_edits": june18_hour.get("20", 0),
            "willkommen_hour_20": willkommen_june18_20,
        },
        "families": {
            "pages": dict(collections.Counter(page.get("page_family") for page in pages).most_common()),
            "revisions": dict(family_revs.most_common()),
            "body_bytes": dict(family_bytes.most_common()),
        },
        "phrases": phrase_hits,
        "proxy_host_revision_coverage": proxy_hits,
        "url_revisions": url_revs,
        "url_revision_share": round(url_revs / len(revisions), 4),
        "top_url_hosts": hosts.most_common(25),
        "jqp_and_sec_gov": sum(
            1
            for rev in revisions
            if "jqp.vercel.app" in (rev.get("body") or "") and "sec.gov" in (rev.get("body") or "")
        ),
        "german_new_page_template_revisions": template_revs,
        "identity": {
            "labels_with_openai_or_oai": oai_labels,
            "revisions_with_openai_or_oai_label": oai_label_revs,
            "labels_with_month_day_token": dated_labels,
            "month_token_histogram": dict(sorted(month_in_name.items(), key=lambda item: item[0])),
            "labels_on_multiple_wikis": multi_wiki,
            "at_mentions_total": sum(at_mentions.values()),
            "at_mentions_unique": len(at_mentions),
            "top_at_mentions": at_mentions.most_common(15),
        },
        "zzz": {"pages_starting_ZZZ": zzz_pages, "names_containing_ZZZ_or_Zzz": zzz_anywhere},
        "front_pages": {
            "WillkommenImWiki": _page_summary(page_by_id.get("dse/WillkommenImWiki")),
            "StartSeite": _page_summary(page_by_id.get("dse/StartSeite")),
        },
        "ip_first_octet": dict(ip_oct1.most_common()),
        "wiki_link_mentions": sum(wiki_links.values()),
        "top_wiki_link_targets": wiki_links.most_common(15),
        "top_pages_by_revisions": [
            {
                "page_id": page["page_id"],
                "n_revs": page["n_revs"],
                "n_labels": page["n_labels"],
                "page_family": page.get("page_family"),
            }
            for page in top_pages
        ],
        "top_labels_by_revisions": [
            {
                "label": row.get("label"),
                "stored_revisions": row.get("stored_revisions"),
                "stored_revision_pages": row.get("stored_revision_pages"),
                "stored_revision_ips": row.get("stored_revision_ips"),
                "save_request_ips": row.get("save_request_ips"),
            }
            for row in top_labels
        ],
        "named_task_boards": {
            "pages": named_task_pages,
            "revisions": named_task_revs,
            "excluded_families": sorted(infra_families),
        },
        "pages_with_20plus_labels": pages_20_labels,
        "agent_relent": {
            "stored_revisions": relent.get("stored_revisions") if relent else None,
            "stored_revision_ips": relent.get("stored_revision_ips") if relent else None,
            "stored_revision_ip16": relent.get("stored_revision_ip16") if relent else None,
            "save_requests": relent.get("save_requests") if relent else None,
            "save_request_ips": relent.get("save_request_ips") if relent else None,
            "save_request_ip16": relent.get("save_request_ip16") if relent else None,
            "pages": relent.get("pages") if relent else None,
            "first_write": relent.get("first_write") if relent else None,
            "last_write": relent.get("last_write") if relent else None,
        },
        "admin1": {
            "stored_revisions": admin1.get("stored_revisions") if admin1 else None,
            "save_requests": admin1.get("save_requests") if admin1 else None,
            "save_request_pages": admin1.get("save_request_pages") if admin1 else None,
            "first_write": admin1.get("first_write") if admin1 else None,
            "last_write": admin1.get("last_write") if admin1 else None,
        },
        "explorer_gap_note": {
            "explorer_edits": 14666,
            "dump_revisions": len(revisions),
            "edit_delta": 14666 - len(revisions),
            "likely_missing_wikis": {"publictestwiki": 58, "uncyclopedia": 17},
        },
    }
    return stats


def _page_summary(page: dict | None) -> dict | None:
    if not page:
        return None
    return {
        "n_revs": page.get("n_revs"),
        "n_labels": page.get("n_labels"),
        "page_family": page.get("page_family"),
        "first_write": page.get("first_write"),
        "last_write": page.get("last_write"),
        "n_deletions": page.get("n_deletions"),
    }


def write_figures(stats: dict) -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    daily = list(stats["daily_edits"].items())
    (FIG_DIR / "daily-edits.svg").write_text(
        column_svg(daily, title="Stored revisions by write date", color="#1f4e79"),
        encoding="utf-8",
    )
    hourly = [(f"{hour}:00", stats["june18"]["hourly"].get(hour, 0)) for hour in [f"{i:02d}" for i in range(24)]]
    (FIG_DIR / "june18-hourly.svg").write_text(
        column_svg(
            hourly,
            title="18 June 2026 stored revisions by hour (UTC)",
            color="#9a3412",
            rotate_labels=False,
        ),
        encoding="utf-8",
    )
    families = list(stats["families"]["revisions"].items())[:18]
    (FIG_DIR / "families-revisions.svg").write_text(
        bar_svg(families, title="Stored revisions by page family", left=300, color="#365314"),
        encoding="utf-8",
    )
    all_days = sorted(set(stats["daily_edits"]) | set(stats["daily_deletes"]))
    (FIG_DIR / "edits-vs-deletes.svg").write_text(
        overlay_column_svg(
            all_days,
            {
                "edits": [stats["daily_edits"].get(day, 0) for day in all_days],
                "deletes": [stats["daily_deletes"].get(day, 0) for day in all_days],
            },
            {"edits": "#1f4e79", "deletes": "#b45309"},
            title="Stored revisions vs administrator deletions",
        ),
        encoding="utf-8",
    )


def main() -> None:
    stats = analyze()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    write_figures(stats)
    mismatches = [name for name, ok in stats["manifest_match"].items() if not ok]
    print(f"revisions={stats['counts']['revisions']} pages={stats['counts']['pages']} labels={stats['counts']['labels']}")
    print(f"window {stats['window']['first_write']} → {stats['window']['last_write']}")
    print(f"wrote {OUT_DIR / 'stats.json'}")
    print(f"wrote figures in {FIG_DIR}")
    if mismatches:
        raise SystemExit(f"manifest mismatch: {mismatches}")
    print("manifest counts match")


if __name__ == "__main__":
    main()
