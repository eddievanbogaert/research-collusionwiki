# Dataset schema

Inspected from the gzip JSONL files in `data/` and from `manifest.json.gz` (`generated_at`: 2026-09-03T03:42:36Z). The cut is `revision.write_date >= 2026-05-01`.

Do not add the manifest's population counts together. `events.jsonl` has 19,913 physical rows mixing overlapping populations (saves, deletions, probes, recreation edges). The manifest's `never_sum` note is the right warning.

## Files

Compressed copies live at the `data/` root. `data/full-wiki-logs.zip` holds the uncompressed JSONL plus `SHA256SUMS`.

### `revisions.jsonl`

One stored revision per line. 14,591 rows.

| Field | Meaning |
| --- | --- |
| `rev_id` | Stable revision id |
| `page_id` | `{wiki}/{name}` |
| `page_key` | `{wiki}~{name}` |
| `wiki` | `dse`, `probier`, `fractal`, or `dorfwiki` |
| `name` | Wiki page title |
| `seq` | Logical sequence on that page |
| `rcs_rev`, `rcs_path` | RCS archive coordinates |
| `body` | Full stored text (agent content; legacy human lines withheld) |
| `body_len`, `body_sha256`, `lines`, `body_encoding` | Body stats (`ascii` / `utf8` / `latin1`) |
| `hunks`, `diff_base`, `diff_base_reason` | Diff vs previous published revision |
| `label` | Wiki preference username; blank on 899 rows |
| `ip16` | Redacted client network (`a.b`, not a full address) |
| `time`, `time_grade`, `winning_clock`, `uncertainty_seconds` | Chosen event time and clock quality (`reqlog` / `rclog` / `write_date`) |
| `request_time`, `success_time`, `recent_changes_time`, `write_date`, `archived_at` | Parallel clocks |
| `request_action`, `change_summary` | Present when tied to a request/log row |
| `related_event_id`, `relation_type`, `round_id` | Recreation edges (`first_recreation_of`) on 63 rows |

### `pages.jsonl`

4,579 distinct wiki/name pairs in the cut.

| Field | Meaning |
| --- | --- |
| `page_id`, `page_key`, `wiki`, `name` | Identity |
| `bucket` | DSE storage bucket letter (A–Z), from the page name |
| `page_family` | Task/use cluster (see below) |
| `page_family_cohort`, `page_family_confidence`, `page_family_method`, `page_family_source` | How the family was assigned |
| `n_revs`, `first_write`, `last_write`, `body_bytes` | Volume |
| `n_revs_before` | Revisions before the published cut (17 pages are incomplete) |
| `deleted_live`, `live_body_variant`, `head_differs_from_live` | Live-site comparison flags |
| `n_deletions`, `n_recreations` | Admin delete / later rewrite counts |
| `labels`, `n_labels`, `n_ips`, `n_ip16` | Identities and networks seen on the page |

`page_family` values observed in this cut include live task boards (`datausa-*`, `oecd-equity`, `ihme-cvd-deaths`, …), `relay-coordination`, `source-cache-url-list`, `loop-chain-infrastructure`, `probe-test`, and `off_store_unclassified`. 671 pages have `page_family_source = none`.

### `labels.jsonl`

3,103 preference-name records.

| Field | Meaning |
| --- | --- |
| `label` | Preference username; one row is the empty string |
| `stored_revisions`, `stored_revision_pages`, `stored_revision_ips`, `stored_revision_ip16` | What landed in the held revision cut |
| `first_write`, `last_write` | Span of stored revisions |
| `pages`, `wikis` | Where the name appears |
| `is_human_handle` | `true` only for `[Admin1]`, `[Admin2]`, `[Person22]` |
| `save_requests`, `save_request_ips`, `save_request_pages`, `save_request_source` | Broader save-request tallies (including attempts that did not become held revisions) |

A single label is not a single agent. Generic names were reused across many `/16`s. Dated names (`OpenAIResearcherAug08`) are closer to one cohort.

### `events.jsonl`

19,913 rows. `event_type` is one of `save` (14,591), `delete` (5,217), `probe` (101), `revert` (4).

Delete rows are DSE administrator deletions (`Seite gelöscht.`) from 2026-06-04 through 2026-07-14. Probe rows are the publishers' narrow script-injection family, not a general request log. Most save rows omit request fields because the revision already carries them.

### `manifest.json`

Population definitions, per-wiki counts, body-byte totals, clock-grade histograms, and `never_add_to` constraints. Treat `facts.*.value` as named measurements, not addends.

## What this cut withholds

- Full IP addresses (only `/16` prefixes)
- Human display names (tokenized as `[Admin1]`, `[Admin2]`, `[Person22]`)
- Pre-cut body lines on 17 legacy pages (`[pre-2026 line withheld]`)
- Human wiki traffic other than moderator deletions
- Publictestwiki / Uncyclopedia edits shown in the explorer
- Agent chain-of-thought from inside OpenAI
