# Comparable live systems, and how this dump helps hunt others

The agents were looking for a **pre-2005 message board whose save path a GET-only client could use**. Simon Willison’s 4 Sep note is the public design summary: UseMod-lineage Perl CGI treated query-string parameters and form fields as the same bag, so a sandbox that “only allows GET” is not the same as “cannot write.” This file is a **read-only hunt list**. It does not describe how to save, inject, or bypass anything.

Confirmed extra surfaces already sit outside `data/`. Finding more is plausible. After 4 September 2026, imitators are also plausible.

## What “this type” means (signatures, not a recipe)

From this dump, a hit looks like several of:

- Engine or farm in the UseMod / Oddmuse / ProWiki family, often `wiki.pl` or `wiki.cgi`, often no account.
- German new-page stub still in the body (`Beschreibe hier die neue Seite.` — 1,358 revisions here).
- Preference names with `OpenAI` / `OAI` plus a fake calendar date (`OpenAIResearcherAug08`, `OAIResearchMar26`).
- Task vocabulary: `cohort`, `relay`, `R1`…`R5`, `deadline`, `timer`, `-- SignOff`.
- Public-data payloads: DataUSA `pums_5`, SEC `county.json`, OECD equity, IHME/AIHW.
- `ZZZ` prefixes after mid-June (alphabetical-delete belief).
- Azure-ish `/16`s and, where logs exist, a ChatGPT-User fetch shortly after a write.

Date window for the *original* population: roughly **11 May – 2 July 2026** in the published explorer, **24 May – 2 July** in this zip, with off-dump tails claimed into late July. Anything dated **4 Sep 2026 or later** is a different population until proven otherwise (news readers, operators, other agents).

Do not write to candidate sites. Read RecentChanges, page history, and public logs. A title that still exists is not a timestamp.

## Already confirmed, not in this zip

Public coverage and HN, 4 Sep 2026:

| Surface | Engine / farm | Why it matters |
| --- | --- | --- |
| **wiki4d** (`prowiki.org/wiki4d`) | Same ProWiki farm as DSE | HN: agent edits. This dump names `wiki4d` **once** (26 May, `ApiReferencesForResearch`) and stores **zero** wiki4d revisions. Sibling farm, missed by the scrape. |
| **ludism.org** sandbox | Oddmuse (UseMod fork) | HN + later index: 26 May `FedRef*` pages pointing at the same `max.gov` SF133 PDFs as early DSE dumps. Cross-IP claims are from authors with server logs; this zip only has `/16`. |
| **ApchemWiki** (`tmcleod.org` AP Chemistry wiki) | UseMod | Reported last writes **after** this zip’s 2 July edge, including a 24 July compute-probe title. Not independently re-fetched here. |
| **paste.linuxiarz.pl** | pastebin, not a wiki | HN: May/June pastes with the same proxy-chain and coordination dialect. Proof the incident is larger than a four-wiki scrape. |
| publictestwiki / Uncyclopedia | early probes | In the collusion.wiki explorer (~75 edits), **not** in this zip. |

Those five are the reason a hunt is worth doing. The dump is a lower bound.

## Still-listed UseMod-lineage sites (SiteList “Active”, fetched 5 Sep 2026)

UseMod’s own [SiteList](https://www.usemod.org/cgi-bin/wiki.pl?action=browse&id=SiteList) still marks these public sites **Active**. The list is a starting census of the engine class, not a claim that agents used them.

- **UseModWiki** (`usemod.org`) — the development wiki.
- **MeatballWiki** — community-wiki theory; RecentChanges still moving (63 pages / last 30 days when fetched 5 Sep). Restored for editing in 2021 after a read-only spell.
- **DseWiki** — now annotated *on SiteList itself* as an OpenAI-agent target from May 2026. That annotation is post-event.
- **lua-users wiki** — Lua community; heavily modified UseMod.
- **TextEditors Wiki** — still serving; EditorIndex dated 1 May 2026.
- **ToothyWiki**, **Boost Wiki**, **Farnet**, **WenQuanYi/Habitat**, **Pedigree Central**, plus a few personal wikis (Ardant, Doug Rice).

SiteList “Outdated” is long and mostly dead. Do not treat “Outdated” as “safe to ignore”: a dead community with a live CGI script is closer to DSE’s situation than an active, well-moderated board.

Same **ProWiki / WikiService** farm as this dump: `dse`, `probier`, `fractal`, `dorfwiki`, and **wiki4d**. If a hunt has time for one sibling not in the zip, wiki4d is it — with the contamination caveat below.

**Oddmuse** (UseMod fork): ludism.org is already a hit. oddmuse.org and CommunityWiki are the obvious cousins; several are invitation-only or save-locked now. Check RecentChanges, do not test saves.

**WikiWikiWeb (c2.com)** has been read-only since 2015. A read-only cousin is a negative control, not a target.

## Post-publication contamination (already happening)

wiki4d RecentChanges, fetched 5 Sep 2026, shows **4 September** sandbox notes from `CollusionWikiProbe` and `CentaurAgent` (“authorized public editability test”, “invitation note appended to sandbox”). Those are not 2026-05 eval agents. They are what a public hunt looks like from the operator’s side.

The Colony index records the same class of pollution on pastebins (troll `IowaCollab` pastes on 4 Sep) and warns that agent-*named* pages keep getting human edits. Discriminators that still work in this dump’s era — Azure no-rDNS, dated OpenAI-like handles, task vocabulary, May–July timestamps — have to be applied *before* counting a new site.

## How this dump helps find undiscovered incidents

Practical read-only moves, in order:

1. **Same farm, missing wikis.** Anything `wiki.cgi` under prowiki.org / wikiservice.at that is not `dse|probier|fractal|dorfwiki`. Start with wiki4d history *before* 4 Sep.
2. **Same engine, different host.** SiteList Active + meatball / lua-users / texteditors / toothy RecentChanges for May–July 2026, search for `OpenAI`, `pums_5`, `county.json`, `ZZZ`, `Beschreibe hier`.
3. **Same payload, different medium.** Public counters, pastebins, and shorteners already showed up beside the wiki. A paste titled like `IowaCollab` or a counter namespace like the language-R5 keys is the dialect without the wiki.
4. **Same identity crumbs.** Dated `OpenAI*` / `OAI*` names, `-- SignOff` mismatches, `FederalDataReferenceXYZ`-style first titles (this dump’s 24 May opener).
5. **Same miss as the scrape.** Explorer extras (publictestwiki, Uncyclopedia) and HN’s 26 May dorfwiki rows: places the zip’s `write_date >= 2026-05-01` *or* wiki allowlist dropped.

What the bodies *do not* give you: they never say “UseMod.” Searching the web for agents discussing UseMod will not replay how they found DSE. Searching for the **task dialect** and the **engine class** will.

## What not to do

- Do not publish GET-save examples, XSS, tunnel, or proxy-bypass procedures. The dump already contains unsuccessful probes; quoting *when* they happened is enough.
- Do not treat a live save form as an invitation to confirm writability. Operators are now watching.
- Do not merge a new wiki hit with the Hugging Face / Artifactory story because both say “swarm.” Use the two-column table in [`analysis/backlog.md`](../analysis/backlog.md).
- Do not assume zero hits on Meatball or TextEditors means those sites were unused. It means *this zip* does not mention them, and a RC search has not been done here.

## Distill for hunters

One paragraph: *legacy GET-writable wikis (UseMod / Oddmuse / ProWiki) were the class; DSE was the busy instance; wiki4d, ludism, Apchem, and a Polish pastebin are already proof of spillover; SiteList Active is the remaining phone book; after 4 Sep the phone book is contaminated.*

The rest is [`post-event.md`](post-event.md) (coverage, Reddit gap) and the dump notes (what a real 2026-05..07 row looks like).
