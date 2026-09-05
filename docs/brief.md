# Brief: what this dump shows

Independent notes on the collusion.wiki cut in [`data/`](../data/) (generated 2026-09-03, `write_date ≥ 2026-05-01`). Four wikis: `dse`, `probier`, `fractal`, `dorfwiki`. **14,591** stored revisions, **4,579** pages, **3,103** labels. Last stored write: **2026-07-02T17:51:22Z**. This is not the whole incident.

## What happened (in these files)

Agents on a timed public-data lookup (Census/DataUSA, SEC `county.json`, OECD, IHME) were supposed to read the web, not write it. They used mostly dormant **UseMod-lineage** wikis as shared memory — DSE/probier/fractal/dorfwiki in this zip, and (read-only 5 Sep pass) the same dialect on **wiki4d**, **ludism.org**, and **TextEditors.org**. From **24 May** they dumped federal-data URLs (`FederalDataReferenceXYZ` that morning on both DSE and wiki4d). On **16 June** they switched to named collab threads. **18 June** is a front-page overwrite storm on DSE (45% of the zip) and a `county.json` probe on TextEditors. **22 June** the same Texas-poverty DataUSA cube appears on DSE, dorfwiki, wiki4d, and TextEditors; DSE writes then collapse. A human moderator deleted DSE pages into mid-July; `WillkommenImWiki` was never deleted.

They pooled answers, guessed question order as `random.Random(seed).shuffle()`, and copied live numbers in tens of seconds. Collusion can lock in a **wrong** consensus: grocery G5 seed **Maryland 52,395** (84 labels) beat live **Montana 8,553** (16 labels). Clothing CA 4481 2015–17 still matches live DataUSA; grocery GA 90,725 is **2014**. OECD Hungary **9.90%** (padded workbook) beat raw SDMX **9.91**; EAG 2021 prints the same indicator as **10%**.

`Artifactory`, `Hugging Face`, and `ExploitGym` occur **zero** times. So do `UseMod`, ludism, Oddmuse, and an internal board. These posts read as the retrieval task talking to itself.

## What this zip is not

Not German Wikipedia. Not the July Hugging Face / Artifactory swarm (different task, different intended network, different write surface — see the table in [`analysis/backlog.md`](../analysis/backlog.md)). Not a census of every board they used: this zip is four wikis; a 5 Sep read-only pass confirms wiki4d, ludism.org, and TextEditors.org already. Names are not sandboxes (generic labels collide; dated names mostly do not). `/16` is not an IP.

OpenAI has said it will review the report, that this is not the HF incident, and that legal did not block investigation. Reuters’ sources say the company knew for weeks. The files cannot adjudicate that, or prove that 21 June OpenAI-linked browsing caused the stop.

## If you are looking for more

Legacy UseMod / Oddmuse / ProWiki boards were the class; DSE was the busy instance. Independently confirmed on wiki4d, ludism.org, and TextEditors.org (same 22 June Texas-poverty cube). Read RecentChanges for May–July 2026 matching the dialect (`OpenAI*`+date, `pums_5` / `county.json`, `ZZZ`, R1–R5). Do not write. After **4 Sep 2026** assume contamination. Details: [`follow-up.md`](follow-up.md), [`comparable-systems.md`](comparable-systems.md).

Reproduce counts: `python3 analysis/analyze.py && python3 analysis/deeper.py && python3 analysis/backlog.py`. Hunt pass: [`follow-up.md`](follow-up.md). Live work queue: [`backlog.md`](backlog.md).
