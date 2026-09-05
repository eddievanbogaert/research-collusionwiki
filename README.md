# research-collusionwiki

Independent notes on the public [collusion.wiki](https://collusion.wiki) dump of the 2026 OpenAI agent message-board incident.

The dump in [`data/`](data/) is the reconstructed, PII-redacted cut published by Sydney Von Arx, Cormac Slade Byrd, Spencer Kitts, and Thomas Larsen. This repository does not re-host the live German wiki; visiting the original site logs visitor IPs.

## What is in `data/`

| File | Role |
| --- | --- |
| `revisions.jsonl.gz` | 14,591 stored page revisions (bodies, labels, redacted `/16` IPs, clocks) |
| `pages.jsonl.gz` | 4,579 wiki/page pairs with family labels and revision counts |
| `labels.jsonl.gz` | 3,103 preference-name identities, including 3 redacted human handles |
| `events.jsonl.gz` | Saves, administrator deletions, recreation edges, and script-injection probes |
| `manifest.json.gz` | Provenance, population definitions, and counts that must not be added together |
| `full-wiki-logs.zip` | Uncompressed copies of the same files plus `SHA256SUMS` |

The write-date cut is `revision.write_date >= 2026-05-01`. Wikis in this cut: `dse`, `probier`, `fractal`, `dorfwiki`. Early probes on publictestwiki.com and Uncyclopedia appear in the collusion.wiki explorer (~75 extra edits) but are not in these files.

Schema notes: [`docs/DATASET.md`](docs/DATASET.md).

## Independent write-up

[`analysis/report.md`](analysis/report.md) is a second look at the files, not a restatement of the original findings page. It checks published counts, measures how the wiki was used (URL caches vs live relays), and flags identity collisions such as `AgentRelent`.

Reproduce the numbers (Python 3 stdlib only):

```bash
python3 analysis/analyze.py
```

That refreshes `analysis/stats.json` and the SVG figures under `analysis/figures/`.

## Provenance

- Source publication: <https://collusion.wiki>
- Manifest generated at: `2026-09-03T03:42:36Z`
- Publisher SHA-256 of the farm DB: see `data/manifest.json.gz` → `db_sha256`

The dump redacts person names and full IP addresses. Pre-2026 lines on 17 legacy pages are replaced with `[pre-2026 line withheld]`. Human traffic is omitted except for moderator deletions of agent pages.

## Safety

These logs include unsuccessful injection probes and discussion of sandbox-restriction workarounds. This repo documents what the files contain. It does not reproduce payloads or bypass procedures.
