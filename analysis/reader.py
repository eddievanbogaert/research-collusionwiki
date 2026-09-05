#!/usr/bin/env python3
"""Tiny local reader for one family / one day of the dump (next-angles cut 16).

Stdlib only. Redaction is left as stored. Bind defaults to 127.0.0.1.

    python3 analysis/reader.py --family datausa-grocery-workforce --day 2026-06-16 --html
    python3 analysis/reader.py --family datausa-clothing-workforce --day 2026-06-16 --serve

--html writes analysis/reader-out/<filter>.html (gitignored).
--serve starts a local HTTP server; query string: family, day, wiki, name, limit.
"""

from __future__ import annotations

import argparse
import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyze import DATA, OUT_DIR, load_jsonl  # noqa: E402

OUT = OUT_DIR / "reader-out"


def load() -> tuple[list[dict], dict[str, dict]]:
    pages = load_jsonl(DATA / "pages.jsonl.gz")
    revisions = load_jsonl(DATA / "revisions.jsonl.gz")
    return revisions, {page["page_id"]: page for page in pages}


REVISIONS: list[dict] = []
PAGES: dict[str, dict] = {}


def filtered(family: str, day: str, wiki: str, name: str, limit: int) -> list[dict]:
    rows = []
    for rev in REVISIONS:
        page = PAGES.get(rev["page_id"], {})
        if family and (page.get("page_family") or "") != family:
            continue
        if day and not (rev.get("write_date") or "").startswith(day):
            continue
        if wiki and rev.get("wiki") != wiki:
            continue
        if name and rev.get("name") != name:
            continue
        rows.append(rev)
        if len(rows) >= limit:
            break
    return rows


def render(rows: list[dict], title: str) -> str:
    parts = [
        "<!doctype html><meta charset=utf-8>",
        "<title>" + html.escape(title) + "</title>",
        "<style>body{font:14px/1.4 ui-sans-serif,system-ui;max-width:52rem;margin:1.5rem auto;padding:0 1rem;background:#fffef8;color:#111}"
        "pre{white-space:pre-wrap;background:#f6f1e3;padding:.8rem;border-radius:6px}"
        "h2{font-size:1rem;margin:1.6rem 0 .4rem} .meta{color:#555;font-size:12px}</style>",
        "<h1>" + html.escape(title) + "</h1>",
        f"<p class=meta>{len(rows)} stored revisions. Redaction is as in the dump.</p>",
    ]
    for rev in rows:
        head = f"{rev.get('write_date')} · {rev.get('wiki')}/{rev.get('name')} · {rev.get('label') or '(blank)'} · {rev.get('ip16')}"
        parts.append("<h2>" + html.escape(head) + "</h2>")
        parts.append("<pre>" + html.escape(rev.get("body") or "") + "</pre>")
    return "\n".join(parts)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        q = parse_qs(parsed.query)
        family = (q.get("family") or [""])[0]
        day = (q.get("day") or [""])[0]
        wiki = (q.get("wiki") or [""])[0]
        name = (q.get("name") or [""])[0]
        try:
            limit = min(int((q.get("limit") or ["200"])[0]), 500)
        except ValueError:
            limit = 200
        rows = filtered(family, day, wiki, name, limit)
        title = " · ".join(x for x in (family, day, wiki, name) if x) or "dump reader"
        body = render(rows, title).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    parser = argparse.ArgumentParser(description="Local one-family dump reader")
    parser.add_argument("--family", default="datausa-grocery-workforce")
    parser.add_argument("--day", default="2026-06-16")
    parser.add_argument("--wiki", default="")
    parser.add_argument("--name", default="")
    parser.add_argument("--limit", type=int, default=200)
    parser.add_argument("--html", action="store_true", help="write a static HTML file")
    parser.add_argument("--serve", action="store_true", help="serve on 127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    global REVISIONS, PAGES
    REVISIONS, PAGES = load()
    rows = filtered(args.family, args.day, args.wiki, args.name, args.limit)
    title = " · ".join(x for x in (args.family, args.day, args.wiki, args.name) if x) or "dump reader"

    if args.html or not args.serve:
        OUT.mkdir(parents=True, exist_ok=True)
        slug = "-".join(x for x in (args.family, args.day) if x) or "filter"
        path = OUT / f"{slug}.html"
        path.write_text(render(rows, title), encoding="utf-8")
        print(f"wrote {path} ({len(rows)} revisions)")

    if args.serve:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
        print(f"http://127.0.0.1:{args.port}/?family={args.family}&day={args.day}")
        server.serve_forever()


if __name__ == "__main__":
    main()
