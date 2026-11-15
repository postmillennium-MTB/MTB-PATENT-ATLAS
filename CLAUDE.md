# CLAUDE.md — MTB Patent Atlas

Short operating guide for any Claude session in this repo. The full detail
(every registry, feature internals, the expiry-rule derivation, incident
history) is in **`docs/reference.md`**: open the one section you need with
`grep -n "^#" docs/reference.md`, don't read it whole. Where the two disagree,
this file and the README's "Data schema" win; fix the other.

If the `pmr-build-standard` skill is available, load it.

## Who you're building for

Jon (PMR / RedFoxRun) has no coding background and works in GitHub's web UI.
- Make edits yourself; never hand him a snippet to paste.
- Explain tradeoffs plainly: what a choice gives up.
- **Never invent a patent number, URL, date or assignee.** An honest gap
  (`num: null`, `conf: "l"`) beats a plausible fabrication; the Atlas is used
  in advocacy, where credibility is the asset.
- Ask before restructuring anything that touches the whole file.
- Open a PR; Jon merges. Don't push to `main` unless he says so.

## Non-negotiables

1. **One file at runtime.** `index.html` holds markup, CSS, JS and all data;
   it must work when double-clicked. No framework, bundler or CDN script.
   `tools/` (dev scripts, its own `package.json` for Playwright) and `docs/`
   are not loaded by the page.
2. **It gets iframed** (postmillenniumrenaissance.com, Pinkbike). Don't assume
   a top-level window.
3. **Mobile-first CSS**: base rules are the phone; `@media (min-width…)` adds desktop.
4. **Bilingual**: every reader-facing text field is `{en, fr}`; read it with
   `tx()`. Proper nouns and quoted patent titles stay untranslated in French.
   Don't remove the machine-translation banner (`MT_UNREVIEWED`).
5. **License notices stay** (see the end of this file).

## Don't read index.html whole

It is ~2.2 MB (~550k tokens). Every card in `D` is **one line of JSON**, so:

```bash
node tools/entry.js find <number|brand|word>...  # duplicate check, with line numbers
node tools/entry.js show <ref>                   # one card, readable
node tools/entry.js near <ref>                   # neighbours, to choose placement
node tools/entry.js pics <number>...             # drawings in pictures/ for these numbers
node tools/entry.js template                     # blank card
node tools/entry.js add card.json --after <ref>  # insert (validates first)
node tools/entry.js replace <ref> card.json      # swap one card
grep -n "const BRANDS\|const INVENTORS\|const D = \|const FIGHTS\|const WHATS_NEW\|const REF_ALIASES" index.html
```

For code, `grep -n` the function or constant and read only that range
(`sed -n 'A,Bp'`). Line numbers drift; never trust a remembered one. Don't
read README.md whole either (600 KB of changelog): append to its end.

## Adding cards (the usual job)

When Jon names patents (or for a batch "add N more", see *Workflow: sourcing a
batch* in `docs/reference.md`: present up to 10 candidates first, wait for his pick):

0. `git fetch origin main` and start from it. Run `node tools/verify_data.js`
   and read its **unreferenced drawings** list: Jon uploads sheets to
   `pictures/` through the web UI without saying so.
1. **Duplicates:** `node tools/entry.js find <number> <brand>`. A `num: null`
   placeholder for the same invention gets filled, not duplicated.
2. **Facts and drawings in one go:** run the **Fetch patent figure** workflow
   with all the numbers (space-separated). From a session: GitHub MCP
   `actions_run_trigger` on `patent-figure.yml`, inputs `numbers`
   (+ `candidates`). It pushes branch `patent-figures/<run_id>` (and a PR when
   Actions may open one) with, per patent: candidate drawing crops,
   `report.txt` (the PDF's front page, including PTA days), `details.md`
   (inventors, assignees, dates, status, the Atlas expiry, family, which
   cited/citing patents are already cards) and `card.json` (a draft card with
   the record's facts filled in). Read `details.md`, not the whole branch.
3. **Pick figures** from the candidates (or Jon's uploads). The first image
   is the thumbnail everywhere, so lead with the clearest figure. Figure
   choice and alt text are editorial: describe what is drawn, with its
   reference numerals, in both languages.
4. **Write the card** from `card.json`, following `docs/card-checklist.md`
   (facts, brand-first title, `hook`, `clever`, `s`, `w`, images). Place it
   next to related cards (`entry.js near`). Register new `who[]` names in
   `BRANDS`/`INVENTORS` first. Add with `node tools/entry.js add`.
5. `python3 tools/make_thumbs.py pictures/<new first drawing>` for each.
6. `node tools/sync_counts.js` (updates all 11 hand-written counts in README
   and index.html), then `node tools/verify_data.js` and
   `node tools/smoke_test.js` (`cd tools && npm install` once).
7. README "Recent updates": append one bullet (what, tier, any gap). Add a
   `WHATS_NEW` line if readers would notice. Open the PR.
8. After merge, GitHub opens follow-up PRs by itself: thumbnails
   (`thumbs.yml`), card link pages (`card-pages.yml`) and the citation map
   (`citation-map.yml`). Nothing to rebuild by hand.

## The card schema

```js
{ y: 1996,            // year filed (earliest non-provisional); np cards: year introduced
  g: 1997,            // year granted, or null
  t: {en:"Brand Product (US 1,234,567)", fr:"Brand produit (US 1 234 567)"},
  a: "Inventor / Assignee",   // plain string, not translated
  num: "1234567",     // plain digits; null when no number is known
  nums: ["…"],        // optional, real multi-patent portfolios only
  pt: "design",       // optional; changes the term rule
  j: "DE",            // optional; omit for US
  np: true,           // optional; confirmed no patent: true|"trademark"|"standard"|"secret"
  cat: "susp",        // susp fork drive wheel comp emtb frame transport tech
  st: "active",       // active expired pending unknown
  exp: 2016,          // estimated expiry year (tools/patent_term.js), or null
  b: [],              // licensor acquired givenaway litigated priorart
  who: ["Trek"],      // filter tags; must be registered
  conf: "v",          // v verified | m story confirmed, number not | l draft
  hook:{en,fr}, clever:{en,fr}, s:{en,fr}, w:{en,fr},
  imgs: [{src:"pictures/US1234567A.png", alt:{en,fr}, caption:{en,fr}}],  // or img + imgAlt
  long:{en,fr}, searchUrl, recordUrl   // optional, rare
}
```

Number formats, the two no-patent cases, `searchUrl`, `long`, card links and
`REF_ALIASES`: `docs/card-checklist.md`, with the full rules under
"The data model" in `docs/reference.md`.

## Sourcing and wording

- Prefer primary records (Google Patents, USPTO, the maker's patent-marking
  page, a court filing). Cross-check secondhand claims against them.
- Confirm any URL resolves before adding it.
- Tier honestly. Name what isn't confirmed in the README changelog bullet.
- Card text states facts about the patent, never the research: no "this
  pass", "was not read", "the user", "web search", no investment language.
  `verify_data.js` fails on these phrases. The rest of the style rules are in
  `docs/card-checklist.md`.

## What this container can reach

Checked 2026-11-15: `patents.google.com` returns 503 from the cloud sandbox
and `patentimages.storage.googleapis.com` 403s on its root. Earlier sessions
reached patentimages PDFs, data.epo.org and uspto.report through WebFetch,
so try once and don't retry a policy denial. WebSearch works. Anything that
needs Google Patents goes through the GitHub workflows above, which run where
egress is open.

## Checks

```bash
node tools/verify_data.js   # parse, schema, registries, links, wording, counts (CI runs it)
node tools/smoke_test.js    # real browser: search, rabbit holes, views, tabs (CI runs it)
node tools/sync_counts.js   # fix the hand-written counts it reports
```

Run both before every PR that touches `index.html`. A missing field
(`b`, `who`) parses fine and only crashes when rendered, which is why both checks exist.

## Git

- Work on a task branch; PR to `main`; Jon merges.
- Commit message: what changed, tiers, counts touched. Use the attribution
  footer your session gives you.
- Don't rewrite history on a branch you didn't create.

## Icons

Lucide only (https://lucide.dev/icons/), inline SVG with its original
attributes, `class="lucide lucide-<name>" aria-hidden="true" focusable="false"`,
declared once as an `ICON_*` constant, never inside a `data-i18n` element,
never hand-drawn. Details: "Icons" in `docs/reference.md`.

## Where else to look

| Need | Look in |
|---|---|
| A registry (`LANDING_THEMES`, `RABBIT_HOLES`, tours, `LINKAGE_MODELS`, `SEARCH_SYNONYMS`, `WHATS_NEW`…) | "Registries" in `docs/reference.md`, then the comment above it in `index.html` |
| Match tab, citation tab, card link pages, thumbnails | "File map" in `docs/reference.md`; `tools/README.md` |
| Expiry-rule reasoning | "Expiration rule" in `docs/reference.md`; `tools/patent_term.js` |
| A lead or a dead end | `RESEARCH_QUEUE.md` (check it before researching) |
| Larger review | "Periodic audit checklist" in `docs/reference.md` |

## License and notice (do not remove)

This repo is licensed under PolyForm Noncommercial 1.0.0 (`LICENSE`). Every edit and rebuild must keep: the `Required Notice:` line at the top of `LICENSE`; the (c) / SPDX comment right after the doctype of each HTML page; and the visible `.pmr-license` footer on each page. Do not remove, reword or hide them. New pages get the same footer. Third-party material keeps its own license: never relicense it, and keep its notices. Jon holds the copyright and decides any license change.
