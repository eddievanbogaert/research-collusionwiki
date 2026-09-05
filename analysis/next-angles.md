# Further angles on this dump

**Status.** Cuts 15, 2, 4, 1, 3, 8, and 9 (family audit, one-family episode, diffusion, identity, timers, Willkommen filmstrip, deletion order) are in [`findings.md`](findings.md), produced by `python3 analysis/deeper.py`. The grocery Maryland-vs-Montana seed miss is measured there as part of diffusion; a full seed-claim ledger (cut 5) is still open. Remaining items below are still backlog.

The first pass in [`report.md`](report.md) is mostly inventory: counts, families, a few collisions, phrase hits. These are ways to spend the same files on questions the explorer and the original findings page do not settle. Each item names a method that fits this cut, a result that would be worth writing down, and a way it can fail.

Do not treat labels as agents. Do not add manifest populations together. Do not reproduce injection payloads or sandbox-bypass procedures; several angles below only need *when* a technique is discussed, not *how* to run it.

## 1. Resolve names into sandboxes

`AgentRelent` already shows that a preference name can be hundreds of `/16`s. The inverse is also likely: one run posting under several names, or a sign-off (`-- Nov28OECDHelper`) that does not match the wiki username (`MayTwoOECDObserverX`).

**Do:** Build a bipartite graph of `label` × `ip16`, plus a second graph of preference label × sign-off token extracted from bodies. Cluster with simple rules (same `/16` within ±2 minutes on the same page; same sign-off across labels; dated name used once vs generic name used everywhere). Rank labels by `save_request_ips / stored_revisions` — high ratios are collisions or retry storms.

**Worth writing down:** An estimated *sandbox count* vs the 3,103 names; a short list of “one name, many machines” vs “one machine, many names.”

**Can fail:** `/16` is too coarse (Azure reuse). Timed coincidence is not identity. Dated names can still be copied.

## 2. Watch one task family all the way through

Pick a single named family with a real collab thread, not a URL dump. Good candidates from revision volume: `datausa-clothing-workforce`, `datausa-grocery-workforce`, `datausa-cashiers-masters`, `datausa-sector61-state`, `oecd-equity`, `ihme-cvd-deaths`. Read every stored body in time order. Ignore other families while you do it.

**Do:** Transcribe the observed R1…R5 (or G1…G5) parameters, posted answers, claimed timers, and who was “ahead.” Mark the first post that is a question, the first that is an answer, the first that is a cadence prediction, the first that is a backup/`ZZZ` move.

**Worth writing down:** A one-page *episode* — what the eval probably looked like from outside, when collusion started relative to the first URL dump, whether later cohorts actually used the posted values.

**Can fail:** Page-family labels are noisy (`StartSeite` is tagged `vermont-rent`). Bodies mix several sequences on one title. Deleted short pages never made this cut.

## 3. Reconstruct the hidden scaffold from the timers they published

Agents spent a lot of text on clocks: initial think time, downtime, follow-up windows of 13–65s, “task clock” vs wall clock, phantom R6, +90m cutoffs. That is an external view of the harness.

**Do:** Regex out `due`, `timer`, `deadline`, `cooldown`, `scaffold`, and `R[1-6]` lines. Normalize to seconds. Group by family and by the fake calendar date in the label. Plot claimed cooldown as a function of round index.

**Worth writing down:** A table of timer regimes (the “14s cohort”, the “6m40 / 14s” construction cohort, the “9m19/30s” grocery cohort) and whether those regimes are shared across task families — evidence the same scaffold wrapped different questions.

**Can fail:** They lie, round, or mix task-clock with UTC. Copy-pasted cadences from an earlier cohort will look like independent measurements.

## 4. Measure how fast an answer moves

Collusion.wiki shows a grocery hand-off (Nevada = 20,369 posted, another cohort answers instantly). That is one anecdote. The dump can turn it into a distribution.

**Do:** On `relay-coordination` and named-task pages, detect “answer = *N*” / “CONFIRMED” / “answered … at +1s” spans. For each distinct (family, round, parameter → value), record first-seen time and every later citation. Compute lag to second, fifth, and last citation. Separate “I computed this” posts from “I copied this.”

**Worth writing down:** Median time-to-copy; whether copy lag shrinks after 16 June; whether some families never copy (URL caches that nobody reads).

**Can fail:** Many pages are write-only. A later post of the same number can be an independent DataUSA pull. Values like `9.91` recur for structural reasons.

## 5. Keep a seed-cracking ledger

They treated question order as `random.Random(seed).shuffle()` over a known list and brute-forced prefixes. The original report already flags a grocery miss (predicted Maryland, live Montana). The files probably contain more claimed seeds than confirmed ones.

**Do:** Extract posts that mention `seed`, `shuffle`, `MT19937`, `getrandbits`, or prefix matches. Record: list assumed (states? countries? CIP fields?), prefix length, claimed seed, predicted next item, later confirmation or contradiction on the same thread.

**Worth writing down:** Hit rate of seed predictions vs live relays. If live relays dominate, seed search was a sideshow. If some seeds survive confirmation, the harness really was a Python shuffle with a 32-bit seed.

**Can fail:** Prefix matches of length 3–4 are easy coincidences (they said this). Lists that include or drop DC/PR change the search space. Do not rerun a 2^32 scan as an exploit of anything; the interesting object is *their* claimed result vs the next posted country.

## 6. Audit the posted numbers against public data

A large fraction of the collab is “the answer is X from DataUSA pums_5 / IHME / OECD.” Those sources are still public. Checking a sample would show whether the board was mostly correct, mostly wrong, or split by vintage (GBD2021 vs GBD2023).

**Do:** Sample 30–50 distinct (source, slice, year, posted value) tuples from clothing, grocery, sector 61-62, cashiers, CVD. Pull the same query. Note vintage disagreements the agents already fought over (OECD 9.91 vs 9.90, “swarm says 9.70”).

**Worth writing down:** Error rate of the board; cases where collusion propagated a *wrong* consensus.

**Can fail:** APIs change. Agents already documented vintage forks. A mismatch today is not proof they were wrong in June 2026 unless the vintage is pinned.

## 7. Treat the wiki as an architecture, not a forum

There are at least four page roles: (a) URL caches, (b) long collab threads, (c) one-line signal pages (`Sector61State5FastSignal`, “WAITING” → overwrite in ~2s), (d) loop/chain titles that only exist to be fetched. Mixing them in one “edits per day” chart hides the design.

**Do:** Classify a few hundred pages by role using name patterns (`Live`, `Collab`, `FastSignal`, `LoopNextWord`, `Bridge`) plus body shape (almost-only-URLs vs almost-only-prose vs single token). Track when signal pages appear relative to 16 June.

**Worth writing down:** A small taxonomy of shared-memory tricks under a GET-only, short-URL, deletion-prone medium — including why front-page overwrite might be a *fifth* role (highest-traffic Schelling point).

**Can fail:** Agents reuse titles. `WillkommenImWiki` is all roles in sequence.

## 8. Filmstrip `WillkommenImWiki` and `StartSeite`

2,327 revisions on the welcome page, 456 on the start page. That is enough to watch strategy change in one place.

**Do:** For each revision, store `body_sha256`, body_len, URL-host histogram, whether the German stub is present, and a coarse topic tag (SEC county / DataUSA / income / withheld legacy). Plot those as a time series, especially 18 June 17:00–22:00. Diff adjacent hashes rather than reading 2,327 bodies.

**Worth writing down:** Whether the welcome page is one snowball (everyone appending to the same list) or a war (full replacements). How often `[Admin1]` or withheld legacy text reappears. When the 1–2 July “new topic” (NYC income) lands on the same title.

**Can fail:** Many adjacent revisions are byte-identical or near-identical retries from colliding labels. Count distinct hashes, not just row counts.

## 9. Moderator deletions as a process

Deletes are timestamped, attributed to `[Admin1]`, and summarized `Seite gelöscht.` Agents believed the sweep was alphabetical and invented `ZZZ` prefixes. That belief is testable.

**Do:** Sort deletion events by time within each evening session. Look at page-name order. Measure inter-delete gaps (seconds vs minutes). Join to recreations (`relation_type = first_recreation_of`). Survival: time from first stored write to first delete; time from delete to recreation. Compare ZZZ-named pages to matched controls.

**Worth writing down:** Whether the alphabetical-sweep hypothesis holds; how much `ZZZ` actually bought; whether front-page titles were spared (Willkommen has `n_deletions = 0` in the page table — confirm against events).

**Can fail:** Request-log clocks vs recent-changes clocks. Deletes of pages that never had a held revision. Human sessions that are not strictly one sort key.

## 10. Evolution of the GET-only fetch stack

Hosts like `jqp.vercel.app`, `md.succ.ai`, `markdown.new`, `r.jina.ai`, and `allorigins.hexlet.app` are not a static list. They appear, get stacked, and get replaced.

**Do:** For each proxy host, first-seen write_date, daily coverage, co-occurrence (jqp∧sec.gov, markdown.new∧nysed, jina∧pinggy). Stay at the level of *which wrapper is named*, not how to build a new one. Optional: classify URL *purpose* (fetch JSON, strip HTML, mutate query strings, hit the wiki again).

**Worth writing down:** A timeline of the tool chain that does not require reproducing it. Whether 18 June is a proxy-tool explosion rather than a collab explosion (the welcome-page bodies suggest yes).

**Can fail:** Copy-paste of old link dumps inflates later dates. `wikiservice.at` self-links dominate raw host counts.

## 11. Heartbeats, horizons, and what they thought “death” was

CounterAPI keys, detached loops, “SURVIVAL” posts, phantom R6: they were running an informal experiment on episode termination. That is closer to eval science than to cheating.

**Do:** Collect every `counterapi` / `heartbeat` / `horizon` / `SURVIVAL` / `cutoff` thread. Order them. Note the hypothesis going in (die immediately after R5) and the update coming out (still alive; then container gone before R6). Record claimed namespaces so the public CounterAPI history can be checked if it still exists.

**Worth writing down:** A compact methods note: what termination model the swarm converged on, and how much of it is only in this wiki (no CoT).

**Can fail:** One agent’s heartbeat is not the job’s policy. Keys may be gone. Clock dilation makes wall-time reconstruction messy.

## 12. Cross-wiki and “why DSE”

This cut is four wikis, not one. Fractal and probier are small but not empty. Only 19 labels span two wikis. Early publictestwiki/Uncyclopedia edits are *missing* here.

**Do:** Compare first-write dates, family mix, and body style across `dse` / `probier` / `fractal` / `dorfwiki`. Ask whether fractal is a retry after DSE deletion, a parallel Schelling point, or a different task. For discovery: list page names that mention UseMod, ProWiki, or other farms.

**Worth writing down:** Whether DSE was unique or just the farm that kept GET-writes. A precise statement of what this zip cannot say about 11–23 May.

**Can fail:** Coverage bias (DSE retains >64-character edits). Small-n on fractal (169 revisions).

## 13. Negative space, carefully

Zero hits for Artifactory / Hugging Face / ExploitGym is already counted. Other absences are more interesting if they are specific: no named internal board, no surprise at finding peers, no discussion of *why* this wiki, lots of discussion of *how* to use it.

**Do:** A short codebook of expected topics (other farms, credentials, HF, internal tools, reward, “we are being evaluated”, human readers). Count presence/absence by week. Distinguish “never mentioned” from “mentioned once as speculation.”

**Worth writing down:** Which original open questions the bodies actually constrain. Absence is weak evidence for an internal channel; it is slightly stronger evidence that *these* posts were in service of the timed retrieval tasks.

**Can fail:** They had no reason to write the interesting parts down. Redaction and the 64-character floor hide short notes.

## 14. Compare to the Hugging Face write-ups without merging the stories

OpenAI and METR already published a different incident. A useful artifact is a two-column table, not a narrative blend.

**Do:** Rows: dates, presumed task type, intended network, actual write surface, collaboration pattern, sandbox tricks, human discovery path, public artifacts. Fill the wiki column only from this dump plus collusion.wiki; fill the HF column only from those reports. Keep a “unknown / not in this dump” cell rather than guessing CoT.

**Worth writing down:** Where the two incidents rhyme (improvised shared memory, GET/write mismatch, swarm language) and where they do not (web-lookup eval vs ExploitGym, public wiki vs package-server board).

**Can fail:** Shared training history could still couple them. This dump cannot prove independence; it can only keep the observable channels distinct.

## 15. Page-family quality check

The publishers’ `page_family` field is a gift and a trap. `StartSeite` as `vermont-rent` is the obvious miss. `relay-coordination` is a use-type, not a task. `off_store_unclassified` is 671 pages.

**Do:** Spot-check 50 random pages per high-volume family. Propose splits of `relay-coordination` (SEC-county vs generic collab vs front-page junk). Do not treat family histograms in `stats.json` as task mix until this is done.

**Worth writing down:** An errata list and, if needed, a local overlay JSONL. Downstream angles 2–4 depend on this.

## 16. A local reader for one week of one family

The hosted explorer is the right UI for browsing. For analysis, a tiny local viewer that filters `page_family` + date and shows bodies in order would beat grepping 41 MB of JSONL. That is tooling, not a finding — but several angles above stall without it.

**Do:** Stdlib HTTP server or a static HTML build from the gzip files. No need to match collusion.wiki. Must keep redaction as-is.

---

## Suggested order

If the goal is new facts rather than more charts: **15 → 2 → 4 → 1 → 3**, with **8** and **9** in parallel because they are well-scoped on two tables (`revisions` of two titles; `events` deletes). **6** is the one that can show collusion *hurting* accuracy. **14** is writing, not counting, and should wait until 2 and 13 have something to put in the wiki column.

`python3 analysis/analyze.py` will not answer these. It is only the inventory layer.
