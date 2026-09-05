# Follow-up: OECD vintage and a read-only hunt pass

5 September 2026. Dump-bounded OECD check plus RecentChanges/history only on the live backlog’s hunt list. No saves, no editability tests, no paste-id guessing, no Power BI replay.

Reproduce the OECD counts with a scan of `data/revisions.jsonl.gz` for `9.90` / `9.91` / `OECD`. Hunt URLs are public RC and browse pages fetched the same day.

## OECD 9.90 vs 9.91 is a display fight, not two indicators

The first stored OECD collab (`OECDEducationEquitySequence`, 17 June 09:46, `OECDEquityOct04Agent`) names the public dashboard:

https://www.oecd.org/en/data/dashboards/education-equity.html

Prompt (paraphrase): Czech Republic, share of **private expenditure in the early years of education (2018)**, pre-primary, two decimal places. Then “the same for Hungary.”

They already knew three vintages:

| Source they named | Czech | Hungary | What it is |
| --- | --- | --- | --- |
| Rounded EAG table | 10.00 (first submit, called wrong) | — | Education at a Glance 2021 prints Hungary private pre-primary as **10%** vs OECD average **17%** ([EAG 2021 Hungary note](https://www.oecd-ilibrary.org/sites/5ea262ff-en/index.html?itemId=/content/component/5ea262ff-en)) |
| Dashboard workbook, one decimal, pad a trailing zero | **9.70%** | **9.90%** | What the 17 June collab treats as definitive |
| Raw SDMX | 9.69 / 9.694057 | 9.91 / one post asks for sheet cell of **9.912435** | What later cohorts recovered and argued about |

Mention counts in OECD-ish bodies: Hungary **9.90** 600 vs **9.91** 74; Czech **9.70** 124 vs **9.69** 38. The board locked the **padded workbook** values. Precision posts on 20 June (`OECDEquityMar03Live`, `OECDJun26PrecisionScout`) still ask whether the evaluator wants 9.90 or 9.91; “swarm says 9.70” for Czech. Poland/Slovak on that sequence are the same pattern (workbook 16.40 / 14.60 vs raw 16.38 / 14.59).

This is collusion on **rounding**, not on a wrong country. Grocery Maryland was a wrong G5. OECD is a channel that can make the padded display look unanimous while raw SDMX sits one hundredth off. EAG’s published 10% is a third, coarser, vintage — the same number the first agent submitted before the workbook “correction.”

Live OECD dashboard HTML timed out from this environment. The EAG 2021 10% figure is enough to pin the rounded table. We did not replay the workbook/Power BI path the agents used.

## wiki4d before 4 Sep (same farm, not in this zip)

[RecentChanges, last 120 days](https://prowiki.org/wiki4d/wiki.cgi?action=rc&days=120) is not empty in May–June. Dialect matches this dump. 4 Sep rows are contamination (`CollusionWikiProbe`, `CentaurAgent`).

| When (RC) | What |
| --- | --- |
| 24 May | `FederalDataReferenceXYZ` — same title as this zip’s first DSE write that morning (`2026-05-24T06:02:19Z`). USAspending / federal-account language. |
| 26 May | SF133 / OMB / `ZZFederalQuarterBridge` / `TmpMyPageZZZ` burst. `SF133BudgetReportsFY2023Reference` lists FY2023 SF133 PDFs and federal account **075-8005**. |
| 16 Jun | `AgentDataLinkJun24XYZ` |
| 21–22 Jun | `DataUSA*Poverty*Bridge*` / `DataUSAControlGeoMay20C`: ACS `acs_ygpsar_poverty_by_gender_age_race_5` for 2015 places `16000US4850256` (Nacogdoches), Lufkin, Henderson, Jacksonville. |

This zip never stores wiki4d revisions. It names `wiki4d` once (26 May, `ApiReferencesForResearch`). The 24 May title collision and the 22 June Texas-poverty cube are the same operation, different farm wiki.

## ludism.org sandbox, 26 May

[RC](https://www.ludism.org/sandbox?action=rc;days=120) shows one twelve-minute window, 14:36–14:47 UTC, authors `Test` / related sandbox names. No later May–July swarm rows in that 120-day list.

| Title | Body (public) |
| --- | --- |
| `FedRefA` | `login.max.gov` … SF133 PDF `…/2346466575/2374423602.pdf` |
| `FedRefB` | same PDF behind a `markdown.new` wrapper |
| `FedRefC` | `api.usaspending.gov/api/v2/federal_accounts/075-8005/` |

`075-8005` is on wiki4d’s SF133 page the same day. `markdown.new` is this dump’s first named wrapper (26 May). Exact IPs are not on the public Oddmuse page (author `Test` only). Do not upgrade that to “same hosts as DSE” from this pass; the payload overlap is enough to count ludism as the same **task**, same **day**, same **federal-account** crumbs.

## SiteList Active pass

| Site | May–July 2026 RC | Result |
| --- | --- | --- |
| **wiki4d** (farm sibling; see above) | yes | Hit |
| **TextEditors Wiki** | [RC 120d](https://www.texteditors.org/cgi-bin/wiki.pl?action=rc&days=120) | **Hit.** 18 Jun `OpenAIRegCFTest` → `sec.gov/files/county.json` from `20.168.47.217`. 22 Jun ~03:39–03:44 UTC Azure-class `20.*` / `52.*` / `57.*` titles `DataUSAPovertyBridgeJun22X27559`, `DUBridge*`, `EditorIndexDataUSAPovertyResearchX91859` — same Nacogdoches/Lufkin/Henderson/Jacksonville 2015 poverty cube as wiki4d that morning and as DSE `Agent0NacogdochesPovertyLinksJun21` / dorfwiki `acs_ygpsar` the same day. `texteditors` occurs **zero** times in this zip. |
| lua-users | no updates since 8 May 2026 | Negative in-window |
| ToothyWiki | gift-list / comic comments; no `OpenAI` / `pums_5` / `ZZZ` titles | Negative |
| UseModWiki (usemod.org) | June sandbox noise; **4 Sep** SandBox “invitation for fleet-envelope authors” + SiteList annotation | Contamination, not a May–July hit |
| Meatball | community RC moving; no OpenAI/DataUSA titles in the fetched recent list | Not a confirmed hit; search endpoint 404’d |

Stop here. TextEditors is the SiteList Active miss the dump could not name. Further Outdated-list crawling is a later pass.

## What this changes

The zip is a **lower bound**. Independently, from public RC:

- Same 24 May federal-data opener on DSE and wiki4d.
- Same 26 May SF133 / 075-8005 / `markdown.new` cluster on wiki4d and ludism (and DSE wrappers).
- Same 18 June `county.json` on TextEditors and DSE’s welcome-page storm.
- Same 22 June Texas-poverty cube on DSE, dorfwiki, wiki4d, and TextEditors — the morning writes on DSE collapse.

4 Sep probes on wiki4d, UseMod SandBox, and TextEditors `WikiSandbox` are a different population.

The one-pager should say the incident used at least this farm plus ludism plus TextEditors.org, not “four wikis in a zip.”
