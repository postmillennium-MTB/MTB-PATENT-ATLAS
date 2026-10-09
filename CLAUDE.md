# CLAUDE.md — MTB Patent Atlas

Operating instructions for any Claude Code session working in this repo. Read
this before touching `index.html`. It complements `README.md` — the README is
the reader-facing documentation and the living changelog; this file is the
contributor-facing "how to actually make a change without breaking something"
guide. Where the two disagree, trust the README's "Data schema" and "Recent
updates" sections as ground truth and treat this file as due for a fix.

If the `pmr-build-standard` skill is available in your session, load it — it
covers the conventions shared across every Post Millennium Renaissance tool
(not just this one). This file is the same standard applied specifically to
the Patent Atlas's actual schema, registries, and history.

## Who you're building for

Jon (PMR / RedFoxRun) has no coding background and edits through GitHub's web
UI, not a local git client. That has concrete consequences:

- **Deliver complete files, not diffs or snippets.** He pastes whole files
  into GitHub's editor. If a change is large, say what changed and why, then
  hand over the full file (or, in this session, commit and push it directly).
- **Never say "add this line to your CSS/JS."** Make the edit yourself.
- **Explain tradeoffs, not just the answer.** He thinks in costs and
  benefits, not right-answer/wrong-answer. Say what a choice gives up.
- **Never invent a patent number, URL, date, or assignee.** An honest gap
  (`num: null`, `conf: "l"`) beats a plausible-looking fabrication — this
  dataset gets used in advocacy contexts where credibility is the asset.
- **Ask before restructuring.** A refactor that touches the whole file means
  a full re-review on his end. Worth it sometimes; always flag it first.

## The non-negotiables

1. **One file.** `index.html` contains everything — markup, CSS, JS, and the
   entire dataset. No build step, no bundler, no npm, no `package.json`. It
   must keep working when someone just double-clicks it.
2. **It will be iframed.** Every release is embedded on
   postmillenniumrenaissance.com and often in a Pinkbike article (see
   README's "Embedding in Pinkbike" section for the known `position: sticky`
   /`position: fixed` iframe quirk). Don't design a feature that assumes a
   top-level browsing context.
3. **Mobile-first CSS.** Base rules are the phone layout; `@media
   (min-width: …)` adds desktop. Never the reverse.
4. **No committed test suite.** The README's "Tech stack" line describing a
   jsdom harness documents a verification *method* used during development
   sessions, not a checked-in test file — there is no `package.json`, no
   `node_modules`, no test directory in this repo. Don't assume `npm test`
   exists. See **Verifying a change**, below, for what actually exists.

The former non-negotiable #2 capped this project at two Google Fonts total
(Barlow, Barlow Condensed) to keep font-loading weight down for the iframed/
mobile embed case. Removed 2026-09-20 at the user's explicit request — no
longer a hard constraint. Still weigh load weight before adding an external
dependency (this stays a single-file, no-framework, no-CDN-script project
per rule 1 above), but a new Google Font is no longer something that needs
special justification. The four visual themes each now carry their own
display font (Nunito/WMBC, Bitter/COMBA, Anton/CAMBA, IBM Plex Mono/CAMBR)
loaded via the same `<link>` in `<head>`, layered onto `--font-display`
per theme rather than replacing Barlow/Barlow Condensed, which remain the
shared body font and the `:root` fallback.

## File map

| Path | Contents |
|---|---|
| `index.html` | Everything: `<head>` meta/SEO tags (lines ~1–20), `<style>` (~21–400), body markup (~402–503), `<script>` (~504–end) — which itself opens with the data registries (`CATS`, `BRAND_HQ`, `BADGES`, `BADGE_TIPS`, `INVENTORS`, `BRANDS`, then the `D` array of patent entries, then `FIGHTS`) before the rendering/filtering logic. **Line numbers drift with every edit — `grep -n` for the constant name rather than trusting a remembered line number.** |
| `README.md` | Full public documentation: at-a-glance stats table, feature tour, data schema reference, confidence-tier and sourcing rules, methodology, and a chronological "Recent updates" changelog that's the closest thing this repo has to commit history in prose. |
| `RESEARCH_QUEUE.md` | **The repo's system of record for leads not yet in `D`.** Candidate patents, submitted numbers that conflict with existing entries, and research leads triaged out of GitHub issues. Resolved items are struck through in place with a note on what was found and whether the atlas changed, rather than deleted — the dead ends are the point, since the same wrong number tends to get resubmitted. Jon files leads as GitHub issues (that's what's convenient from the web UI); a session's job is to triage the issue into this file and close it, so there is one durable home and not two that drift apart. Check this file before starting a research pass — a lead you're about to chase may already be recorded here as resolved or as a known dead end. |
| `tools/` | Repo tooling, not runtime: `fetch_patent_figure.py` (downloads a patent PDF, picks out the drawing sheets, crops the margin and the "U.S. Patent / Sheet n of m" header, emits candidate PNGs plus a report of the PDF's own front page), `verify_data.js`/`smoke_test.js` (the parse/schema/bilingual check and the real-browser smoke test — see **Verifying a change** below), `package.json` (Playwright as a dev dependency for the smoke test only — `tools/node_modules` is gitignored), and `tools/README.md` documenting all of it. Paired with two `workflow_dispatch`/automatic GitHub Actions jobs: `.github/workflows/patent-figure.yml` (figure fetching, manual) and `.github/workflows/verify-data.yml` (the two checks above, automatic on every PR and push to `main`). Deliberately stops short of choosing which figure to use or writing `imgAlt` — both are editorial. Nothing here is loaded by `index.html`; deleting the directory changes nothing a reader sees, so it does not breach the single-file rule. |
| `pictures/` | Patent drawing images referenced by individual entries' `img` field. Two naming patterns coexist: `US<number><kindcode>.png` (e.g. `US7665929B2.png` — the majority pattern) and a few bare-number files from an earlier pass (`9102378.png`). Prefer the full `US<number><kind>.png` form for anything new. |
| `favicon.ico`, `favicon-32x32.png`, `apple-touch-icon.png` | Site favicons. No reason to touch these for a data addition. |
| `social-preview.png` | The `og:image`/`twitter:image` social-card asset (1000×852), referenced by absolute URL in `index.html`'s `<head>`. Not loaded by the page's own runtime code — only fetched by link-preview bots. |
| `match/index.html` | **Added as a prototype 2026-09-30; wired live 2026-10-01 at `postmillenniumrenaissance.com/atlas/match`** (Jon asked for it explicitly) via a wrapper page in the `pmr-website` repo (`atlas/match/index.html`, same pattern as the main Atlas's own `/atlas/` wrapper — iframes this repo's GitHub Pages URL) plus a `sitemap.xml` entry there. A matching game: pair a real patent drawing with its description. Its own single file, own `<style>`/`<script>`. `MATCH_DATA` is every `D` entry with a drawing (252 as of this writing, any confidence tier, all nine categories — regenerated 2026-10-01 to pick up 6 entries added since the page first went live) — not a live link to `index.html`'s `D` array, but a full snapshot of it, regenerated with the Node script kept as a comment in the file's own `<script>` block; re-run that snippet after a data session adds or edits entries with images rather than hand-editing `MATCH_DATA`. The Rabbit Holes section (`index.html`'s own home tab) has no equivalent drift: its auto-fill reads `D` live on every render (`D.filter(d=>(d.img||d.imgs) && d.w && !used.has(d))`, same image-presence rule, no snapshot step), so it never needs a manual resync the way `MATCH_DATA` does. `title`/`assignee`/`img`/`imgAlt`/the full summary are all copied verbatim; `teaser` is the one field this page invents, and it's algorithmic, not hand-written — the first ~200 characters of the entry's own summary, cut at a word boundary. That's a real quality trade against the original 27-entry demo's hand-written, mechanism-first one-liners: an algorithmic cut often leads with filing/citation boilerplate instead of the mechanism. Bilingual (EN/FR toggle, `localStorage`-persisted preference, same `tx()`/`t()` pattern as the main Atlas) — the entry data was already fully bilingual in `D`, so this was free; the game's own chrome strings live in a `T` object in this file, not shared with the main Atlas's `T`. `../pictures/` references into the shared image folder. The `noindex,nofollow` robots meta and the red "Prototype" badge are both removed now that the page is intentionally public; the badge was replaced with a neutral "Beta — descriptions are auto-generated for now" pill (same honest-gap pattern as the main Atlas's `MT_UNREVIEWED` banner) rather than dropped outright, since the teaser-quality gap below is real and still worth flagging to a player. **Still open, by Jon's own explicit call to launch now and improve after:** hand-written teasers to replace the algorithmic ones (at least for the entries where the auto-cut reads worst) — once that pass happens, consider whether the beta pill should come off too. **Also still open, not yet asked for:** a link to the game from this repo's own `index.html` nav/chrome — the game is reachable today only by URL (direct, via the wrapper, or via `pmr-website`'s sitemap), not by clicking anything inside the main Atlas. |

## The data model

Everything a reader sees comes from four things defined near the top of the
`<script>` block, in this order: `CATS`, `BRAND_HQ`, `BADGES`/`BADGE_TIPS`,
`INVENTORS`, `BRANDS`, the `D` array, and `FIGHTS`. `grep -n "const CATS\|const D = \|const FIGHTS"`
to relocate them — they move as the file grows.

### The atlas is bilingual (English/French) — every text field is `{en, fr}`

As of a language-switcher feature merged 2026-09-10, every reader-facing text
field — `t`, `s`, `w`, `imgAlt` on `D` entries; `title`, `sub`, `stakes`,
`outcome` on `FIGHTS`; the `CATS`/`BADGES`/`BADGE_TIPS`/`STATUS_WORD`/
`NATOFFICE.full`/`JUR_LANG` registries — is stored as `{en: "...", fr: "..."}`,
not a plain string:

```js
t: {en:"Title (US 1,234,567)", fr:"Titre (US 1 234 567)"},
```

Fields that are **not** translated and stay plain strings: `a` (assignee,
mostly proper nouns), `num`/`nums`/`j`/`pt`/`cat`/`st`/`exp`/`b`/`who`/`conf`/
`img` (all codes or file paths, not prose), and on `FIGHTS`, `combatants`/
`era` (same reasoning).

**By design, proper nouns and assignee names are left untranslated in the
French text too.** Company, brand, product, person, and place names, and the
names of cited documents (a patent's own title, an article title), stay in
their original form inside `fr` strings exactly as they appear in `en` — "Trek,"
"Horst Link," "Split Pivot," "Spoke & Blossom's *Gear Profile*." This is a
deliberate rule, not a gap a translation pass should "fix": a patent's quoted
title is its identity on the record, and translating a brand or an assignee
would break search and make the entry harder to match against the USPTO or
Google Patents. A common noun *around* a proper name is still translated ("the
Rocky Mountain rear-suspension patent" → "le brevet de suspension arrière
Rocky Mountain"). When reviewing French text, don't flag an untranslated proper
noun as an omission.

**Read a field with `tx(field)`**, never `field` directly or `field.en`
directly — `tx()` returns the current-language string, falls back to English
if the current language's translation is missing, and — critically —
**returns the value unchanged if it's still a plain string**, so an entry
added before this feature (or before you've written its French) renders
correctly rather than breaking:

```js
function tx(field){
  if(field==null) return field;
  if(typeof field==="object") return field[state.lang] ?? field.en ?? "";
  return field; // not yet converted to {en,fr} — render the plain string as-is
}
```

Use `txEN(field)` instead of `tx()` only for the handful of places that must
stay stable across a language switch: the deep-link/DOM-id slug (`_REF`) and
the literal English substrings `FIGHTS[].cards` matches titles against
(`fightCardMatches`). `catLabel()`/`badgeLabel()`/`badgeTip()`/`statusWord()`/
`natOfficeFull()`/`jurLangName()` are the equivalent accessors for those
registries. Chrome strings (buttons, labels, tooltips — not entry data) live
in a separate `T = {en:{...}, fr:{...}}` object read via `t(key, ...args)`.

**A page-level banner** (`MT_UNREVIEWED = true`, shown via `#mtBanner`) tells
readers the French entry text is AI-drafted and hasn't been checked by a
French speaker against the English original — this is the atlas's own
"never inflate certainty" discipline applied to itself, and it says so in
both languages. **Do not remove the banner or flip `MT_UNREVIEWED` to
`false`** without an actual review pass confirming the French is accurate.
The banner text (`mtBannerText`, in both `T.en` and `T.fr`) hardcodes the
current entry count ("all N patent entries") — it's a hardcoded count string
like the four described in **Keeping counts in sync** below, and needs to
move in step with them.

**When adding a new entry:** write both `en` and `fr` from the start —
that's the current convention, decided explicitly when this note was last
updated (ask the user again if it's been a while and the codebase's own
practice looks like it's drifted). Writing English-only and leaving French
to a later pass is not an error — `tx()`'s fallback renders it correctly —
but it reopens the exact gap a full translation pass just closed, so treat
it as a deliberate exception to flag in the changelog, not a shortcut to
take by default.

### `D` — the patent entries (this is what you'll edit most)

```js
{
  y: 1996,                    // year filed (required)
  g: 1997,                    // year granted, or null if still pending
  t: {en:"Title (US 1,234,567)", fr:"Titre (US 1 234 567)"}, // headline patent number in the title when one exists
  a: "Assignee / inventor",   // free text, shown on the card — NOT translated (see above)
  num: "1234567",             // primary patent number — plain digits, no commas, no "US" prefix
  nums: ["1234567","7654321"],// OPTIONAL — only when a real portfolio needs multiple linked numbers
  pt: "design",               // OPTIONAL — omit for utility patents; "design" changes the exp-term math
  cat: "susp",                // susp | fork | drive | wheel | comp | emtb | frame | transport
  st: "active",               // active | expired | pending | unknown
  exp: 2017,                  // estimated expiry year, or null — see the expiration rule below
  j: "DE",                    // OPTIONAL — omit entirely for US filings; see the jurisdiction table below
  b: ["litigated"],           // zero or more of: licensor | acquired | givenaway | litigated | priorart
  who: ["Trek"],              // filter tags — every value MUST already exist in BRANDS or INVENTORS
  conf: "v",                  // v = verified | m = story confirmed, number unverified | l = draft
  s: {en:"Factual summary...", fr:"Résumé factuel..."},   // 1–3 sentences: what the patent covers and its history
  w: {en:"Why it matters...", fr:"Pourquoi c'est important..."} // editorial payoff — what changed because of this patent
  // img: "pictures/US1234567A.png",   // OPTIONAL — only if a drawing was actually sourced and viewed — NOT translated
  // imgAlt: {en:"…", fr:"…"},         // required alongside img — describe what figure/number is shown, both languages
  // searchUrl: "https://patents.google.com/?inventor=Jane+Doe", // OPTIONAL — see below — NOT translated
  // recordUrl: "https://euipo.europa.eu/eSearch/#details/designs/015091656-0001", // OPTIONAL — direct link to an official record Google Patents doesn't index (EU RCDs); wins over searchUrl — NOT translated
  // long: {en:"…", fr:"…"},           // OPTIONAL — see below — a deeper narrative, rendered as an inline <details> disclosure below w
}
```

**`searchUrl`** overrides the card's auto-built "Search related patents on
Google Patents" link with a specific URL you supply. The auto-built version
(no `num`, US jurisdiction) constructs a query from the assignee name and
title — a reasonable default, but sometimes a hand-picked query finds the
right person or company far better than that guess can, most obviously an
inventor-name search (`?inventor=First+M.+Last`) for a `num:null` entry
where the actual patent hasn't been identified yet but the *inventor* is
known — added first for Joe Breeze's JBX1 entry, whose real name (Joseph T.
Breeze) differs from how he's credited (`a: "Joe Breeze"`), so the
auto-built query would never have found it. `searchUrl` wins over every
other branch of that link's logic, including a numbered/`nums` entry — set
it deliberately, and update or remove it if a real patent number gets added
to the same entry later, since nothing checks the two stay in sync
automatically.

**Before finalizing `img`/`imgs` on any entry, check `pictures/` for every
number in that entry's `num` and `nums[]`, not just the one you were pointed
at.** Jon sometimes uploads several sheets for a single patent directly
through GitHub's web UI ahead of a data session, without saying so in the
request — the base file (`<NUM><KIND>.png`) plus numbered variants
(`.1.png`, `.2.png`, `.3.png`, ...). A session that only looks up the sheet
it was explicitly told about will miss the rest. Run
`ls pictures/ | grep -i <NUM>` for each number the entry touches (the
2026-09-30 session that added Lauf's foundational patent found one used
sheet and missed three more sitting in `pictures/` under the same number —
caught a session later only because Jon asked directly). This applies on
every entry that touches a patent number, new or existing — an entry can
gain a newly-uploaded sheet between sessions with no other signal that it
happened. If multiple sheets show genuinely different embodiments (e.g. a
patent's own drawings covering both a front and a rear application), that's
itself evidence for how broadly the patent's claims reach — worth reflecting
in `s`, not just in which sheets get wired into `imgs[]`.

**`long`** is a second, deeper layer of narrative for the rare entry that has
more well-sourced substance than `s`/`w` should carry on their own — added
2026-09-26 for cases like a patent's own Background section naming an
earlier, unpatented product as prior art, or a company history documented
across multiple independent articles. It renders as a native `<details>`
disclosure at the bottom of the card body (same zero-JS-to-open pattern as
the multi-number `.gp-list` block and the share menu — see the comment above
`.share-menu` in `index.html`), so it costs nothing on cards that don't use
it and needs no new JavaScript to open/close. Write multiple paragraphs by
separating them with a literal `\n\n` in the string; single-paragraph is
fine too.

**This is an escape valve, not a new default.** The **Prose style: avoid AI
tells** rules below — especially "say it once," don't pad a gap, don't
restate a caveat — apply to `long` exactly as they apply to `s`/`w`; a
`long` field is not permission to relax them because there's now more room.
Most entries should never have one. Reach for it only when there's genuine
additional substance (a documented legal/technical angle, a company history
worth telling in the founders' own words) that would otherwise force `s`/`w`
to either omit something worth keeping or bloat the default card view for
every reader — not as a place to dump biographical color that doesn't
actually serve the entry's point just because a source happened to include it.

**Linking one card to another:** write `[[card:<ref>|link text]]` inside `s`, `w`
or `long` (both languages). `<ref>` is the target's `cardRef()` — its `num`, or
`num-N` if two entries share a number — i.e. the `#p=` deep-link string. The
card renders an in-page link (`a.card-xref`, handled by one delegated click
listener that calls `jumpToCard`); search, the Rabbit Holes blurb and Patent
Match see only the link text (`stripCardLinks`). Do not link to `num:null`
entries (slug refs are fragile), and don't hand-write `<a href="#p=…">` — it
bypasses both the dead-link check and the click handler. `verify_data.js`
hard-fails on any token whose target doesn't exist and on any pair in its
`REQUIRED_CROSSLINKS` list missing a direction or a language; `smoke_test.js`
clicks those pairs in a real browser (keep its `XLINK_PAIRS` in step). When you
wire a new pair on purpose, add it to both lists.

**Linking to an outside page:** `[[link:https://…|link text]]` in `s`/`w`/`long`,
same rules as the card token (stripped to plain text in search, Rabbit Holes and
Patent Match). `https` only, hard-checked by `verify_data.js`. It does not check
that the URL resolves; confirm that yourself before adding one.

**Changing an entry's `num` changes its deep link.** A `num:null` entry's `#p=`
ref is a title slug; once it gets a number the ref becomes the number (and a
renamed title or a merged entry changes it too). Every old ref people have
shared would then open nothing. Add `"old-ref":"new-ref"` to `REF_ALIASES` in
`index.html` (next to `cardRef`) in the same edit; `jumpToCard()` resolves it,
and `verify_data.js` fails on a dead alias target or one shadowing a live ref.

**Expiration rule (`exp`):**
- Filed **on or after June 8, 1995** (the post-GATT rule, which covers nearly
  everything in this dataset): `exp = filing year + 20`.
- Filed **before June 8, 1995** — this is the sub-case this note itself got
  wrong until 2026-10-06, so read it properly. It is not one rule, it is
  three, and it applies to far more of this dataset than the old text
  claimed (it said "exactly three times so far (the Schwinn entries)";
  the real figure is 57 single-patent entries):
  - **Utility patent still in force on June 8, 1995** — i.e. grant year + 17
    lands in 1995 or later. This covers essentially everything in the atlas
    filed from the late 1970s on. Under 35 U.S.C. §154(c) the term is the
    **greater** of `grant year + 17` and `filing year + 20` (see
    [MPEP 2701](https://www.uspto.gov/web/offices/pac/mpep/s2701.html)).
    Take the later of the two. GATT gave these patents whichever term was
    longer, so reaching for `grant + 17` by reflex *understates* any patent
    that issued less than three years after it was filed — which is most of
    them. The old one-line version of this rule is exactly why ~21 entries
    shipped with an `exp` that was off by two years or more.
  - **Utility patent that had already expired before June 8, 1995** — grant
    year + 17 lands in 1994 or earlier. Every 19th- and early-20th-century
    entry in the atlas is here. §154(c) never reached these patents, so the
    term is simply `grant year + 17`, the law of their own day. Do **not**
    apply the "greater of" test to them; it hands a patent years it never
    actually had, which is the same class of error in the opposite
    direction.
  - **Design patents (`pt:"design"`) sit outside §154(c) entirely**, and
    before October 1, 1982 there was no single design term to compute: the
    applicant *elected* 3½, 7, or 14 years at filing and paid a fee to
    match. A pre-1982 design patent's `exp` therefore **cannot be derived
    from the grant year at all** — read it off the record, or leave the best
    available estimate and say in the entry that the term was an election.
    The Schwinn Sting-Ray banana seat (`US D204,121`, granted 1966,
    `exp: 1970`) is a 3½-year election, not a miscalculation — don't
    "correct" it to grant + 14. Design patents from applications filed
    between October 1, 1982 and May 12, 2015 run a flat 14 years from grant;
    filed on or after May 13, 2015, 15 years from grant.
  - Because the atlas stores *years*, not dates, all of the above is
    year-level arithmetic and carries an inherent ±1 ambiguity against the
    real docket dates. That's accepted and consistent across the dataset —
    `tools/verify_data.js` reports entries that don't match the formula so
    the inconsistency stays visible, but it does **not** hard-fail, because
    a documented exception (a design-term election, a bundled portfolio
    whose `exp` tracks its newest member) is legitimate.
- **Continuations inherit their parent application's filing date**, not their
  own later one — the 20-year clock runs from the earliest non-provisional
  U.S. filing in the priority chain (a provisional alone doesn't count). Two
  WickWerks/RampWerks chainring patents share a title and inventor but sit in
  *separate* continuation lineages rooted in 2006 and 2011 respectively —
  computing `exp` from each one's own later filing year (2017/2014) would
  have overstated both terms by roughly a decade. When a continuation's
  ancestry is documented in its own text (a "Ser. No." trail, a stated
  priority date), use the earliest one for `exp`, not the specific document's
  own filing date, and say so in the entry's own `s`/`w` text — this is
  exactly the kind of thing a reader has no way to sanity-check themselves.
- `exp` isn't decorative: it drives the **Going free soon** filter and the
  Stats-view watchlist automatically for any `active` entry expiring within
  two years. Getting it wrong misfires a real feature, not just a label.

**`num` formatting** — plain digits, no punctuation, no country/type prefix
baked in except where the prefix *is* the number's identity:

| Type | Store as | Renders as |
|---|---|---|
| Standard US grant | `"7334846"` | US 7,334,846 |
| US design patent (single `num`) | `"1140680"` + `pt:"design"` | US D1,140,680 |
| US design patent (inside `nums[]`) | `"D896132"` | US D 896,132 |
| US reissue | `"RE45684"` | US RE 45,684 |
| Foreign, 2-letter prefix | `"EP3111109"` | EP 3,111,109 |
| Foreign, 3-letter prefix | `"TWI386342"` | TWI 386,342 |
| WO (PCT) publication | `"WO2025003104"` | WO 2025/003,104 |
| US published application (no grant yet) | `"20190136918"` | US 20190136918 |
| **EU Registered Community Design (RCD)** | **`num: null`, always** | cite the RCD number(s) in `s` prose instead |
| **Pre-1916 British patent** | **`num: null`, always** | cite the number ("No. NNNN of YYYY") in `s` prose instead |

**Pre-1916 British patents are a second exception, same shape as the EU RCD
one.** Before the Patents and Designs Act 1907 took effect (1916 in
practice), UK patents were numbered sequentially *within each calendar
year*, restarting at 1 every January — "No. 2236 of 1870" and a modern
"No. 2236" (this atlas's `numLink()`/`patentUrl()` only handle the
post-1915 forever-incrementing scheme) are two completely different
patents. Storing the bare number would auto-generate a Google Patents link
to a real but *wrong* 20th/21st-century GB patent — worse than no link,
since a wrong link reads as confirmed when it isn't. Keep `j:"GB"` (still
correct for search/filter purposes) and `num: null`, and cite the
year-qualified number in prose ("British patent No. 2236, taken out August
11, 1870") the same way an EU RCD's number lives in `s` rather than `num`.
The 1870 Starley & Hillman wheel entry is the first case of this in the
dataset — if EPO/Espacenet ever exposes a working per-record deep link for
this pre-1916 numbering scheme, wiring it in would be a genuine code
change, same call as the EU RCD deep-link idea above.

**EU RCDs are a real exception to "always fill `num` when you have a real
number."** An EUIPO Registered Community Design (format `NNNNNNNNN-NNNN`) is
an industrial-design registration, not a utility or design *patent* — a
different legal instrument, administered by EUIPO rather than a patent
office, and not indexed by Google Patents at all. `numLink()`/`patentUrl()`
are Google-Patents-only and have no branch for this format; forcing the raw
number into `num` produces a wrong, dead link rather than a merely
oddly-formatted one. Use `j:"EU"` (distinct from `j:"EP"`, which is the EPO —
*patents*) to get a generic "search EUIPO" link via `NATOFFICE.EU`, keep
`num: null`, and cite the actual RCD number(s) in the entry's own `s` text. A
real per-record EUIPO deep link (parsing the `NNNNNNNNN-NNNN` format into a
proper eSearch URL) would be a genuine, worthwhile code change — flag it as
a design decision rather than doing it inline with a data addition.

**Design patents are stored differently depending on which field they live in,
and getting it backwards produces a broken link both ways.** A single `num` on a
`pt:"design"` entry holds *bare digits* — the rendering code prepends the `D`
itself, for the display label and for the Google Patents URL (which needs
`USD1140680`, not `US1140680`). Writing `num:"D1140680"` alongside `pt:"design"`
doubles it into `DD1140680`; that has been caught twice. Inside a `nums[]` array
the opposite holds: `numLink()` format-sniffs each entry independently and has no
per-entry `pt`, so a design patent there carries its own `D` (see OneUp's
`"D896132"`). All three consumers of the single-`num` form — the Google Patents
button, the "cite this entry" string, and the figure caption's "view full patent"
link — now read one hoisted `numForUrl`/`numPretty` pair rather than recomputing
the prefix; the figure-caption link was the copy that got forgotten, and pointed
design entries at the wrong patent until 2026-09-17.

The `numLink`/`patentUrl` functions in the script detect these prefixes and
build both the display label and the outbound Google Patents / national
patent office link automatically — don't hand-format a number in `t` or `s`
beyond the human-readable version in prose; the stored `num` is what the UI
actually uses.

### Confidence tiers (`conf`) — an honesty mechanism, not decoration

- **`"v"`** — verified against a primary source: USPTO, Google Patents, a
  manufacturer's own virtual patent-marking page, or a court filing.
- **`"m"`** — the technology/story is solid but the specific number wasn't
  independently re-verified this pass, OR the entry deliberately stands in
  for a trade-secret/patent-pending strategy rather than incomplete research
  (WRP, EXT, Forbidden, the GoPro bundles, etc. are `"m"`/`"l"` for that
  reason, not because nobody looked).
- **`"l"`** — draft: existence confirmed, number not yet located, or the
  research pass didn't get far enough to firm anything up.

**Never upgrade a tier to make the dataset look more complete than the
verification actually was.** If a pass didn't re-check a number, it stays
`"m"` even if it happens to be correct. An honest `num: null` beats a
plausible but unconfirmed number.

### Registries — must be updated *before* an entry can reference them

| Registry | What it's for | Rule |
|---|---|---|
| `BRANDS` | Company names for `who[]` and the Brands filter tab | Every company named in a new entry's `who[]` must already be a string in this array, or add it there first. |
| `INVENTORS` | Named individuals for `who[]` and the Inventors filter tab, as `{label, key}` | Only add a person here if they're a recurring, notable figure worth a standalone filter chip — a one-off corporate engineer credited in `a` doesn't need an `INVENTORS` entry (see e.g. `Duhane Lam`, credited in the Rocky Mountain entry's `a` field but not filter-tagged). When in doubt, look for precedent among similar existing entries before adding a name here. |
| `BRAND_HQ` | Maps a `BRANDS`/`INVENTORS` key to a state/country, purely so state/region search and the Colorado panel work without the entry's own prose spelling out the location | Deliberately partial — only add when you've actually confirmed the HQ location. The Colorado panel link also fires on prose: `isColorado` in `cardHTML` matches "Colorado" and a few Colorado town names in an entry's `a`/`s`/`w`, so an out-of-state invention with a Colorado moment (a world title won at Durango) should name the town, not the state. |
| `CATS` | The nine category labels (`susp fork drive wheel comp emtb frame transport tech`) | The "Tech" question (README's own note on it) resolved 2026-09-12: `tech` ("Cameras & Wearables") holds rider-worn camera/data-capture accessories genuinely orthogonal to the bike's own systems — action cams, smart-helmet electronics, ride telemetry. It does NOT mean "anything electronic": a system that controls how the bike itself functions (Di2, AXS, Flight Attendant, a drive-unit motor) stays in its functional category even though it's electronic. Don't add a tenth category without the same scrutiny the README's note gives the ninth — it touches `CAT_COLORS` (below) and the filter-tab row. |
| `CAT_COLORS` | Maps each `CATS` key to a hex color, used only by the Stats tab's "Patents by category, over time" chart | An 8-hue colorblind-safety-validated categorical palette (fixed hue order, checked with a Delta-E/contrast validator against this tool's actual light chart surfaces) for the 8 original categories, plus a 9th entry for `tech` that is deliberately NOT a competing hue — it's a neutral gray, the dataviz method's own prescribed handling for an overflow/thin category rather than stretching an 8-hue-capped palette to 9. If a 10th category is ever added, it also gets the gray-"Other" treatment, not a re-validated 9- or 10-hue palette — re-tier only the original 8 if you ever swap two of *their* colors, and re-run the validator if you ever restyle this chart. |
| `BADGES` / `BADGE_TIPS` | The five entry badges (`licensor acquired givenaway litigated priorart`) and their tooltip text | Adding a sixth badge is a bigger structural change — it touches the Stats view and the filter-tab row. Flag it as a design decision rather than doing it inline with a data addition. |
| `FIGHTS` | Named rivalry groupings shown in the Patent Fights view | Add `{key, title, sub, combatants[], era, stakes, outcome, cards[]}`. `cards[]` takes patent-number strings or distinctive title substrings — `fightCardMatches()` scans `D[]` and auto-generates the tap-to-jump chips, so you don't hand-wire card references. |
| `SEARCH_SYNONYMS` | Search-only synonym groups (added 2026-09-21) — see the dedicated section below | Extends what the search box matches; never changes a card's own text or what a category filter chip means. |
| `RABBIT_HOLES` | Hand-written story cards for the top of the Atlas (home) tab — `{title, blurb, go, img?, imgAlt?, kicker?, pin?}`, schema documented in the comment above it in `index.html` | Jon's to curate. Title/blurb are reader-facing prose and follow the same sourcing and prose-style rules as `s`/`w`. `go` must point at something real (a `card` matcher is resolved with `fightCardMatches()`, same as `FIGHTS[].cards`). Empty is valid — slots then fill automatically from verified entries with drawings. |
| `HOME_SEARCH_SUGGESTIONS` / `HOME_SEARCH_ROTATING` | The "Popular" one-tap search chips under the Atlas tab's big search box, `{label:{en,fr}, q}` — the second list feeds the single rotating chip at the front of that row | Each chip shows a live count from the real `passes()` predicate, so check a new `q` doesn't balloon through a `SEARCH_SYNONYMS` group before adding it (that's how the "post" false positive was found). |

If a brand/inventor chip you expect doesn't show up in the filter row after
an edit, the most likely cause is a `who[]` value that doesn't exactly match
a `BRANDS` string or an `INVENTORS` `key` — check for a typo or a missing
registration before assuming something else broke.

### `SEARCH_SYNONYMS` — widening the search box without touching entry text

`passes()` (the search/filter predicate) splits a typed query into words and
requires each word to be found somewhere on the card — see the comment on
that function for why it works per-word rather than as one glued phrase.
`SEARCH_SYNONYMS` sits on top of that: a flat array of small word groups,
e.g. `["wheel","hub","spoke","freehub","rim","driver body"]`. When a query
word belongs to a group, the search also accepts any *other* word in that
same group appearing on the card, so the relationship works **in either
direction** — searching "spoke" matches a card that only says "wheel," and
searching "wheel" matches a card that only says "spoke," because both
queries expand against the same group rather than one word pointing at
another. This is why the structure is a list of groups, not a `word ->
word[]` map: a directional map would need two entries (one each way) to get
the symmetric behavior a reader actually expects, and would silently drift
out of sync the moment someone added one side without the other.

**This registry only affects what the search box matches.** It never adds a
word to any card's own `t`/`s`/`w`/displayed text, and it has nothing to do
with `CATS`/category filter chips — a `wheel`-category filter still means
exactly what `CATS.wheel` says, synonym groups don't touch it.

**When to add a group or a word to one:**
- The words have to be genuinely the same real-world thing or tightly
  coupled to it in this dataset — a freehub *is* part of a wheel, a
  derailleur *is* part of a drivetrain. Don't add a group for two things
  that are merely often mentioned near each other.
- A word can legitimately belong to more than one group (`damper` is real
  fork vocabulary and real rear-shock vocabulary) — put it in both rather
  than forcing one group to cover two different concepts.
- Keep groups small and specific. A group is doing more harm than good the
  moment a search using it starts surfacing a card that isn't actually
  about the thing being searched for — that's a false positive this
  registry exists to avoid creating, not to introduce.
- This is a search convenience, not a data-integrity mechanism — it doesn't
  need the same sourcing rigor as a `D` entry, but a bad group still
  degrades a reader's trust in search results, so treat a new group as
  worth a second look before committing, the same as any other registry
  change.

## Sourcing discipline

This dataset gets used in advocacy and public writing, where a fabricated
detail is a credibility loss, not just a data error. In order of priority
when adding or touching an entry:

1. **Web-search the invention/company/patent to confirm it's real.**
2. **Confirm any URL actually resolves** before it goes in prose or a link.
   Never carry a link forward from a list without checking it yourself.
3. **Prefer primary sources**: USPTO, Google Patents, a manufacturer's own
   virtual patent-marking page, or a court filing, over secondhand coverage.
4. **Check third-party marketing claims against the primary record.** A
   product marketed as solving a problem doesn't mean the seller holds a
   patent on the mechanism they claim; a similar-sounding patent title isn't
   necessarily the same invention.
5. **When you can't verify something, say so** — tier it honestly (`"m"` or
   `"l"`), or leave it out and name the gap rather than guessing.
6. **Report what you couldn't confirm**, in the changelog entry you write for
   the change, so an unverified claim is a visible, known gap rather than
   something that quietly reads as settled fact.

### Prose style: avoid AI tells

Every honesty requirement above (name the gap, state the tier, say what
wasn't confirmed) has to be met in **plain, professional, concise prose** —
being honest about a gap is not license to write three sentences about it.
This applies to `s`/`w` on `D` entries and to changelog bullets alike; it
does not apply to this file's own contributor-facing voice.

- **Don't narrate the research process.** "This pass," "this session," "this
  session's WebSearch access," "independently confirmed this pass" — none of
  that belongs in reader-facing text. A reader doesn't care which session did
  the work; they care what's confirmed and what isn't. Write the *state* of
  the fact ("confirmed against the manufacturer's marking page" / "unconfirmed
  — no primary source located"), not the *story* of how you got there.
- **Don't refer to "the user."** Jon is not a third party to this dataset —
  he's its author. If a fact came from him directly rather than a document,
  say what kind of source it is ("per the founder's own account," "per the
  assignee's public statement," or just fold it into the sentence as a plain
  claim) rather than narrating "the user confirmed X." If it matters *that a
  person* said it (as opposed to a document), name Jon or the actual person,
  not a generic role label.
- **Don't over-explain a gap.** State the unconfirmed fact, state why it's
  unconfirmed in a half-sentence if that's useful context (a blocked source,
  a name collision), and stop. A gap worth flagging is worth one clean
  sentence, not a paragraph defending the tier assignment.
- **Cut hedge-stacking and meta-commentary about the atlas itself.** Sentences
  like "distinguishing them is part of what this atlas exists to do" or "a
  useful teaching point" editorialize about the *project* rather than the
  *patent*. `w` is allowed real editorial voice — see below — but it should
  land on the invention, the company, or the technology, not on this
  dataset's own epistemics.
- **Watch for compounding qualifiers.** "Likely," "plausibly," "may," "could
  reasonably be assumed to," stacked two or three to a sentence, is a
  speculative-sounding tell even when each individual hedge is accurate. Pick
  the one hedge the sentence needs and cut the rest, or restructure as a
  flat statement of what's known plus one flat statement of what isn't.
- **Say it once.** Don't restate the same caveat in both `s` and `w`, or
  re-explain a conclusion the previous sentence already reached.

**`w` is where Jon's own voice belongs — but only when he actually has
something to add.** A personal aside, a domain judgment call, a "this is the
detail that actually matters to a rider/mechanic/advocate" — that's the
right kind of injected personality, and it's welcome. Don't manufacture it
by default on every entry; a factual `w` with no personal angle is a
perfectly normal `w`. When Jon does add a personal take in a session, keep
it in his voice (direct, technical, opinionated where warranted) rather than
smoothing it into the same neutral-AI register as `s`.

Before shipping a new or edited `s`/`w`, do one pass specifically hunting for
these tells — it's a distinct check from fact-verification, and a factually
correct entry can still read as generated rather than written.

### A known environment constraint: blocked patent-site fetches

Sessions in this environment run behind a network egress proxy that has, in
practice, blocked direct fetches to `patents.google.com`, `www.google.com`,
`www.freepatentsonline.com`, `patents.justia.com`, and `uspto.report`. Don't
assume this is fixed by the time you're reading this — check first — but
plan for it.

A 2026-09-17 session probed this properly and found it wider than the list
above: `image-ppubs.uspto.gov`, `patentsgazette.uspto.gov`, `api.patentsview.org`
and `search.patentsview.org`, `worldwide.espacenet.com`, `register.epo.org`,
`patentscope.wipo.int`, `dockets.justia.com`, `www.patsnap.com`, and even
`singletracks.com` (which mirrors some eGrant PDFs) all returned **403 at
CONNECT** — an organization egress-policy denial, not a transient failure.
Two things worth knowing before you spend a session's budget on this:

- **`WebFetch` is blocked on the same hosts as `curl`.** It is not a way around
  the proxy; it returns `EGRESS_BLOCKED`. `WebSearch` is the only external
  source that works, because it does not egress from the sandbox at all.
- **Don't try to route around a 403.** `/root/.ccr/README.md` says to report a
  policy denial rather than retry it. The right move is to say plainly that the
  primary source was unreachable, tier accordingly, and — for figures — use the
  `Fetch patent figure` GitHub Actions workflow (see `tools/README.md`), which
  runs on GitHub's runners where egress is open.

Given that:

- **`WebSearch` still works and its result snippets often quote the blocked
  page's own content directly** (title, filing/grant dates, inventor names,
  patent number). Cross-confirm a fact across two or more independent search
  queries before trusting it, since a single snippet can be wrong or stale.
- If a fact only comes from search-snippet cross-confirmation rather than a
  page you actually opened and read, that's a real constraint on
  verification depth — tier the entry accordingly (usually still `"v"` if
  multiple independent snippets agree on the specific number/date/inventor,
  but say in the changelog that the primary-source page itself was blocked
  and couldn't be directly read, so a future session with working access
  should double-check it).
- Try alternate hosts if one primary source is blocked (a manufacturer's own
  patent/marking page is sometimes reachable when the aggregator isn't).
- Never silently fall back to guessing when a fetch is blocked — say so.

## Workflow: sourcing a batch of new entries (Jon hasn't named specific patents)

This is the process for a request like "add 10 more entries" — as opposed to
Jon handing over a specific patent number or Google Patents link, which skips
straight to *Workflow: adding one or more new patent entries* below. Follow
these steps in order every time; don't improvise a different shape for this
request from one session to the next.

1. **Source candidates, screening for duplicates as you go.** Search for
   real inventions/patents against category gaps, assignees not yet in
   `BRANDS`, and general MTB-patent research — not just whatever surfaces
   first. For every candidate, check it against the existing `D` array by
   `num` *and* by title/assignee (a fuzzy match, not just an exact string),
   because a continuation or reissue can share a title/inventor with an
   entry already in the atlas while being a legally distinct filing (see
   the WickWerks/RampWerks continuation-lineage note above) — and because a
   "new" patent can turn out to be the same invention already covered under
   a different number. Drop anything that doesn't hold up as a genuinely
   real, distinct, unlisted patent per *Sourcing discipline* above — don't
   pad the list with a guess to hit a round number.
2. **Present a numbered list of up to 10 candidates before writing anything.**
   For each: title, patent number, assignee, filing/grant year, proposed
   `cat`, proposed `conf` tier (call it honestly — a first-pass find is
   usually `m` or `l`, not `v`, until sourced further), and whether a usable
   drawing/figure sheet is realistically available (most utility and design
   patents have one; some process/software patents don't). Note briefly why
   anything considered got rejected as a duplicate or unverifiable, so the
   screening in step 1 is visible rather than invisible. If honest sourcing
   only turns up fewer than 10 clean candidates, present fewer — a short
   list of real entries beats a full list padded with weak ones.
3. **Wait for Jon's direction on which candidates to proceed with**, and on
   images. For each entry he selects for a figure, fetch it via the
   `Fetch patent figure` GitHub Actions workflow (`tools/fetch_patent_figure.py`
   — direct fetches to patent sites are blocked in-session, see *A known
   environment constraint* above), then present the candidate sheets/crops
   from its report and propose a specific sheet, crop, and `imgAlt` — don't
   pick and commit a figure unilaterally, since sheet selection and `imgAlt`
   wording are editorial calls that belong to Jon per `tools/README.md`. The
   `D` schema has one `img` field per entry; if a case genuinely seems to
   need two images, flag that as a schema question rather than inventing a
   workaround (e.g. don't silently repurpose `long` as an image slot).
4. **Write, verify, and changelog each approved entry** by following
   *Workflow: adding one or more new patent entries* below in full, starting
   at its step 1 (candidates are already verified for existence in step 1
   above, but still confirm the number/date/inventor precisely before
   writing the object) — including the count-sync step, which is easy to
   forget when several entries land in one batch.
5. **Run the browser smoke test** (see *Verifying a change* below) before
   opening the PR — not just the Node parse/schema/bilingual checks. A batch
   add is exactly the change most likely to exercise a part of the file a
   narrower edit wouldn't have touched, and it's also the moment a
   pre-existing latent bug elsewhere in `D` is most likely to surface and
   get (wrongly) blamed on the new entries — as happened 2026-09-27, where
   four *pre-existing* entries missing `b:[]` were surfaced by, but not
   caused by, a batch add, and were initially reported as two seemingly
   unrelated bugs (search, then Rabbit Holes) before the shared root cause
   was found. Running the smoke test once, right before opening the PR,
   catches this class of issue regardless of which entries actually
   introduced it.
6. **Open a pull request; do not push to `main`.** State in the PR
   description: which entries were added, the tier assigned to each and why,
   any gaps that couldn't be verified, which count-sync locations were
   touched, and that the browser smoke test was run (or, if it genuinely
   couldn't be — no Playwright/Chromium available in that session's
   environment — say so explicitly rather than letting the omission read as
   an oversight). Push to `main` only when Jon explicitly asks for that
   separately.

## Workflow: adding one or more new patent entries

0. **`git fetch origin main` and diff against it before touching anything** —
   don't assume your local checkout (or this file's schema description) is
   current. This repo is edited by multiple concurrent sessions and directly
   through GitHub's web UI; a 12-commit gap containing a full schema change
   (see the bilingual section above) landed on `main` once already without
   this session noticing until it went looking. A stale local file doesn't
   just risk a bad merge — it risks writing an entry against a schema that's
   no longer accurate.
1. **Verify** per *Sourcing discipline* above: real invention, real
   number/date/inventor, resolvable link.
2. **Decide placement in `D`.** Entries are *not* strictly chronological —
   they're grouped thematically within each `cat`, often clustered next to
   related entries from the same company or the same underlying story (see
   e.g. the Shimano brake cluster around the Servo Wave / Ice Tech entries).
   Find the most relevant existing entry and insert near it; check the
   surrounding `/* ---- Section Name ---- */` comment banners for the
   category's rough grouping.
3. **Write the object** following the schema above. Match the existing prose
   style: `s` is factual (what it covers, filing/grant history, the
   mechanism in concrete terms); `w` is the editorial payoff (why a reader
   should care, what it changed, how it connects to other entries). See
   **Prose style: avoid AI tells**, below — it applies to every `s`/`w`
   you write, not just new entries.
4. **Register any new brand/inventor** in `BRANDS`/`INVENTORS` (and
   `BRAND_HQ` if the location is confirmed) *before* referencing it in
   `who[]` — see the registries table above.
5. **Run the verification script** (below) to confirm the file still parses
   and to get the real updated counts — don't hand-compute them. Also run
   the **schema-integrity check** (same section) — it catches a field your
   new entry forgot (`b`, `who`) that the parse check alone won't, since a
   *missing* field doesn't break parsing, only rendering. For anything
   beyond a single entry — and always for a batch add — also run the
   **browser smoke test** in that same section before committing; it's the
   only check that actually executes `cardHTML()`/`passes()` against your
   edit rather than just inspecting the data shape.
6. **Sync every place a total/count is hardcoded** (all of these must move
   together — this exact class of drift has bitten this repo twice before):
   - `README.md` → the "At a glance" table (total, active, expired, pending,
     litigated, verified, medium, draft, brands, inventors, jurisdictions —
     whichever your change actually affected) and the intro-paragraph patent
     count.
   - `index.html` → six hardcoded strings that do **not** derive from
     `D.length` at render time: the `<meta name="description">` tag, the
     `<meta property="og:description">` tag, the `<meta name="twitter:description">`
     tag, `T.en.shareText` and `T.fr.shareText` (the Share menu text, one per
     language since the bilingual conversion — it used to be a single
     `SHARE_TEXT` constant), and `T.en.mtBannerText`/`T.fr.mtBannerText` (the
     French-translation-disclosure banner, which also states the entry count
     — easy to miss since it reads as a disclaimer, not a counter).
7. **Add a changelog bullet** to README's "Recent updates" section (append
   at the end — it's chronological, oldest-to-newest, and the section header
   date doesn't need to be bumped for every entry; that's established
   practice in this file already). State plainly what was added, the
   confidence tier and why, and anything that couldn't be verified.
8. **Commit and push** per the git conventions below.

## Verifying a change

There's no committed test suite, but there are two real, runnable checks in
`tools/` — `tools/verify_data.js` (parses `D`/`BRANDS`/`INVENTORS`, recomputes
the README table's counts, and checks data-integrity rules the parse alone
can't) and `tools/smoke_test.js` (a real headless-browser check that actually
exercises search and Rabbit Holes navigation). Both are also documented in
`tools/README.md`, and both now run **automatically** via
`.github/workflows/verify-data.yml` on every PR and every push to `main` — but
still run them yourself before committing, rather than waiting to find out
from CI, since by then the bad state is already pushed.

```bash
node tools/verify_data.js
```

prints the README-table counts (total, active/expired/pending/unknown,
litigated, confidence tiers, brands, inventors), then runs two hard-failing
checks (non-zero exit) plus one informational one:

- **Parses `D`/`BRANDS`/`INVENTORS` as valid JS.** A thrown error means a
  syntax mistake in the edit (a missing comma, an unclosed string, a stray
  brace) — a parse failure in `D` breaks the entire page, not just one card.
- **Schema-integrity: every entry has `b[]` and `who[]` as real arrays**, and
  every `who[]` value is actually registered in `BRANDS` or `INVENTORS`.
- **Bilingual completeness** (`t`/`s`/`w`/`long` still a plain string
  somewhere) — reported, not a hard failure, since "English now, French
  later" is a documented, deliberate, acceptable interim state, not an error.

**Why the schema-integrity check exists (2026-09-27 incident, don't remove
without re-reading this):** four pre-existing entries (Spinergy Rev-X, Giro
vented helmet shell, Look clipless pedal, Trimble X-Frame) had shipped with
no `b` field at all — not even `b:[]`. `cardHTML()` rendered badge pills
with an unguarded `d.b.map(...)`, and `passes()`'s badge-filter check did an
unguarded `d.b.includes(...)`. Neither the parse check nor the bilingual
check catches a *missing* field — both only look at fields that are
present. The result: any render that included one of those four entries
threw `TypeError: Cannot read properties of undefined (reading 'map')`
**mid-render**, silently truncating or blanking the results with no visible
error to the reader. This broke two features that looked unrelated and were
reported as two separate bugs before the shared root cause was found: (1)
search — any query matching one of the four (`wheel`, `spoke`, `helmet`,
`pedal`, `frame` — all common words) returned a truncated list; (2) Rabbit
Holes — *every single click* failed, because tapping one calls
`jumpToCard()`, which switches to the unfiltered "All" tab, and the
unfiltered list always contains all four broken entries. Fixed by adding
`b:[]` to all four entries, and by hardening the two unguarded reads to
`d.b||[]` (matching a defensive pattern the search hay-building code
already used one function over) so a future entry missing `b[]` degrades
gracefully instead of crashing the whole page — confirmed directly:
re-introducing a missing `b[]` after that fix still gets caught by
`verify_data.js` as a data gap, but no longer crashes `smoke_test.js`,
because the render-level fallback now holds. **The lesson for schema
changes generally:** when adding a new array field to the `D` schema (or
auditing an old one), grep for every place that reads it and confirm each
site tolerates the field being absent — a `||[]` fallback is cheap; a
silent full-page crash from one bad entry touching every reader who
searches or browses is not.

```bash
cd tools && npm install && cd ..   # once per checkout — installs Playwright
node tools/smoke_test.js
```

This is a **real browser**, not static analysis — Chromium pre-installed at
`/opt/pw-browsers/chromium` in this repo's usual dev sandbox, or Playwright's
own bundled browser otherwise (what CI installs). It loads the actual file,
clicks the first Rabbit Hole (which always renders the full, unfiltered
`D` list — the single strongest whole-file check available, since it
touches every entry on one click), then searches a batch of broad
category-word terms chosen for *collision risk with any pre-existing
entry*, not just words a recent change happens to contain — that's what
actually found the incident above; a Node-only check that only ever
inspects `D` and never executes the code that reads it cannot. Any
non-empty error array, or a suspiciously low card count, means something
crashed mid-render — treat it the same as a thrown error from
`verify_data.js`, not as a cosmetic issue.

Run `smoke_test.js` at least once per session that touches `D`,
`cardHTML()`, `passes()`, or any render/navigation code — and always before
opening a PR for a batch add, per that workflow's own step above.

## Git conventions for this repo

- Work on the task-specific branch you were given (or create one) — never
  push data changes straight to `main`.
- Commit messages: describe what entry/entries were added or changed, the
  tier assigned and why, and any count/registry files touched as a
  consequence. Follow whatever attribution footer your current session's
  instructions specify — that's session-scoped, not a fixed convention to
  hardcode here.
- Don't rewrite history on a branch you didn't create, and don't force-push
  over someone else's commits.

## Periodic audit checklist (for larger reviews, not every small addition)

When asked to review or clean up rather than just add an entry, run all seven:

1. **Data separation** — is every fact above the `D`/registries block and
   every rendering decision below it? Watch for a label or threshold that
   leaked into a render function instead of living in the data.
2. **Repetition** — is a brand/patent-number/title typed more than twice in
   ways that could drift apart? Derive from one field where possible.
3. **Hard-coded values** — a magic number buried in a function (a pixel
   breakpoint, a debounce delay, a color) should be a named constant near
   its use with a comment saying what it controls.
4. **Comment coverage** — does every non-obvious block explain *why*, not
   just *what*? (`STATUS_COLOR_VAR`'s comment, for instance, explains it
   exists only because one inline-styled bar needs a raw color string —
   that's the bar to clear.)
5. **Naming** — do constant and field names say what they're for without
   requiring a trace-through?
6. **Extensibility** — can the next obvious addition (one more patent, one
   more brand, one more Patent Fight) be made as a single, localized edit?
   If not, that's a signal the relevant registry needs widening, not that
   the next contributor should hand-roll around it.
7. **Schema completeness** — run the schema-integrity check in *Verifying a
   change* against every entry in `D`, not just the ones a recent session
   touched (it caught four entries missing `b[]` entirely — see that
   section's incident note — that had sat undetected for an unknown number
   of prior sessions because nothing had ever checked for a field's
   *absence*, only for wrong values in fields that were present). While
   here, grep for every read site of any array field (`b`, `who`, `nums`,
   `imgs`) and confirm each one tolerates the field being missing (`||[]`
   or an equivalent guard) — a bare `d.field.map(...)`/`.includes(...)` is
   a latent full-page crash waiting for one old entry to trigger it.

## What not to do

- Don't add a framework, bundler, or `package.json` — the single file is the
  point, not an accident of history.
- Don't split CSS/JS into separate files.
- Don't invent a patent number, filing date, inventor name, or URL under any
  circumstance — an honest gap is always the correct fallback.
- Don't upgrade a `conf` tier to make a pass look more thorough than it was.
- Don't add a ninth category, a sixth badge, or restructure the `D` schema
  without flagging it as a design decision first — these ripple into the
  Stats view, filter-tab row, and every existing entry's assumptions.
- Don't silently skip the count-sync step (README table + the four
  `index.html` strings) — this is the single most common way this repo's
  data and its own self-description drift apart.
