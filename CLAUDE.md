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
2. **Zero runtime dependencies beyond two Google Fonts** (Barlow, Barlow
   Condensed), loaded via a `<link>` in `<head>`. Don't add a framework, a
   CDN script, or a new external dependency without calling it out explicitly
   and saying what breaks without it.
3. **It will be iframed.** Every release is embedded on
   postmillenniumrenaissance.com and often in a Pinkbike article (see
   README's "Embedding in Pinkbike" section for the known `position: sticky`
   /`position: fixed` iframe quirk). Don't design a feature that assumes a
   top-level browsing context.
4. **Mobile-first CSS.** Base rules are the phone layout; `@media
   (min-width: …)` adds desktop. Never the reverse.
5. **No committed test suite.** The README's "Tech stack" line describing a
   jsdom harness documents a verification *method* used during development
   sessions, not a checked-in test file — there is no `package.json`, no
   `node_modules`, no test directory in this repo. Don't assume `npm test`
   exists. See **Verifying a change**, below, for what actually exists.

## File map

| Path | Contents |
|---|---|
| `index.html` | Everything: `<head>` meta/SEO tags (lines ~1–20), `<style>` (~21–400), body markup (~402–503), `<script>` (~504–end) — which itself opens with the data registries (`CATS`, `BRAND_HQ`, `BADGES`, `BADGE_TIPS`, `INVENTORS`, `BRANDS`, then the `D` array of patent entries, then `FIGHTS`) before the rendering/filtering logic. **Line numbers drift with every edit — `grep -n` for the constant name rather than trusting a remembered line number.** |
| `README.md` | Full public documentation: at-a-glance stats table, feature tour, data schema reference, confidence-tier and sourcing rules, methodology, and a chronological "Recent updates" changelog that's the closest thing this repo has to commit history in prose. |
| `pictures/` | Patent drawing images referenced by individual entries' `img` field. Two naming patterns coexist: `US<number><kindcode>.png` (e.g. `US7665929B2.png` — the majority pattern) and a few bare-number files from an earlier pass (`9102378.png`). Prefer the full `US<number><kind>.png` form for anything new. |
| `favicon.ico`, `favicon-32x32.png`, `apple-touch-icon.png` | Site favicons. No reason to touch these for a data addition. |
| `social-preview.png` | The `og:image`/`twitter:image` social-card asset (1000×852), referenced by absolute URL in `index.html`'s `<head>`. Not a runtime dependency of the page itself — only fetched by link-preview bots — so it doesn't violate the zero-dependency rule above. |

## The data model

Everything a reader sees comes from four things defined near the top of the
`<script>` block, in this order: `CATS`, `BRAND_HQ`, `BADGES`/`BADGE_TIPS`,
`INVENTORS`, `BRANDS`, the `D` array, and `FIGHTS`. `grep -n "const CATS\|const D = \|const FIGHTS"`
to relocate them — they move as the file grows.

### `D` — the patent entries (this is what you'll edit most)

```js
{
  y: 1996,                    // year filed (required)
  g: 1997,                    // year granted, or null if still pending
  t: "Title (US 1,234,567)",  // put the headline patent number in the title when one exists
  a: "Assignee / inventor",   // free text, shown on the card
  num: "1234567",             // primary patent number — plain digits, no commas, no "US" prefix
  nums: ["1234567","7654321"],// OPTIONAL — only when a real portfolio needs multiple linked numbers
  pt: "design",               // OPTIONAL — omit for utility patents; "design" changes the exp-term math
  cat: "susp",                // susp | fork | drive | wheel | comp | emtb | frame | transport
  st: "active",               // active | expired | pending | unknown
  exp: 2017,                  // estimated expiry year, or null — see the expiration rule below
  j: "DE",                    // OPTIONAL — omit entirely for US filings
  b: ["litigated"],           // zero or more of: licensor | acquired | givenaway | litigated | priorart
  who: ["Trek"],              // filter tags — every value MUST already exist in BRANDS or INVENTORS
  conf: "v",                  // v = verified | m = story confirmed, number unverified | l = draft
  s: "Factual summary...",    // 1–3 sentences: what the patent covers and its concrete history
  w: "Why it matters..."      // editorial payoff — what changed in the market because of this patent
  // img: "pictures/US1234567A.png",   // OPTIONAL — only if a drawing was actually sourced and viewed
  // imgAlt: "…"                       // required alongside img — describe what figure/number is shown
}
```

**Expiration rule (`exp`):**
- Filed **on or after June 8, 1995** (the post-GATT rule, which covers nearly
  everything in this dataset): `exp = filing year + 20`.
- Filed **before June 8, 1995**: `exp = grant year + 17` (utility) or `+ 14`
  (design, `pt:"design"`). This has mattered exactly three times so far (the
  Schwinn entries), but apply it correctly to any old filing added later —
  filing+20 would understate the real term by years.
- `exp` isn't decorative: it drives the **Going free soon** filter and the
  Stats-view watchlist automatically for any `active` entry expiring within
  two years. Getting it wrong misfires a real feature, not just a label.

**`num` formatting** — plain digits, no punctuation, no country/type prefix
baked in except where the prefix *is* the number's identity:

| Type | Store as | Renders as |
|---|---|---|
| Standard US grant | `"7334846"` | US 7,334,846 |
| US design patent | `"D896132"` | US D 896,132 |
| US reissue | `"RE45684"` | US RE 45,684 |
| Foreign, 2-letter prefix | `"EP3111109"` | EP 3,111,109 |
| Foreign, 3-letter prefix | `"TWI386342"` | TWI 386,342 |
| WO (PCT) publication | `"WO2025003104"` | WO 2025/003,104 |
| US published application (no grant yet) | `"20190136918"` | US 20190136918 |

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
| `BRAND_HQ` | Maps a `BRANDS`/`INVENTORS` key to a state/country, purely so state/region search and the Colorado panel work without the entry's own prose spelling out the location | Deliberately partial — only add when you've actually confirmed the HQ location. |
| `CATS` | The eight category labels (`susp fork drive wheel comp emtb frame transport`) | Don't add a ninth without reading "A note on the 'Tech' category question" in the README first — it's an open, deliberately undecided call, not a settled gap. |
| `BADGES` / `BADGE_TIPS` | The five entry badges (`licensor acquired givenaway litigated priorart`) and their tooltip text | Adding a sixth badge is a bigger structural change — it touches the Stats view and the filter-tab row. Flag it as a design decision rather than doing it inline with a data addition. |
| `FIGHTS` | Named rivalry groupings shown in the Patent Fights view | Add `{key, title, sub, combatants[], era, stakes, outcome, cards[]}`. `cards[]` takes patent-number strings or distinctive title substrings — `fightCardMatches()` scans `D[]` and auto-generates the tap-to-jump chips, so you don't hand-wire card references. |

If a brand/inventor chip you expect doesn't show up in the filter row after
an edit, the most likely cause is a `who[]` value that doesn't exactly match
a `BRANDS` string or an `INVENTORS` `key` — check for a typo or a missing
registration before assuming something else broke.

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

### A known environment constraint: blocked patent-site fetches

Sessions in this environment run behind a network egress proxy that has, in
practice, blocked direct fetches to `patents.google.com`, `www.google.com`,
`www.freepatentsonline.com`, `patents.justia.com`, and `uspto.report`. Don't
assume this is fixed by the time you're reading this — check first — but
plan for it:

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

## Workflow: adding one or more new patent entries

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
   should care, what it changed, how it connects to other entries).
4. **Register any new brand/inventor** in `BRANDS`/`INVENTORS` (and
   `BRAND_HQ` if the location is confirmed) *before* referencing it in
   `who[]` — see the registries table above.
5. **Run the verification script** (below) to confirm the file still parses
   and to get the real updated counts — don't hand-compute them.
6. **Sync every place a total/count is hardcoded** (all of these must move
   together — this exact class of drift has bitten this repo twice before):
   - `README.md` → the "At a glance" table (total, active, expired, pending,
     litigated, verified, medium, draft, brands, inventors, jurisdictions —
     whichever your change actually affected) and the intro-paragraph patent
     count.
   - `index.html` → four hardcoded strings that do **not** derive from
     `D.length` at render time: the `<meta name="description">` tag, the
     `<meta property="og:description">` tag, the `<meta name="twitter:description">`
     tag, and the `SHARE_TEXT` JS constant used by the Share menu.
7. **Add a changelog bullet** to README's "Recent updates" section (append
   at the end — it's chronological, oldest-to-newest, and the section header
   date doesn't need to be bumped for every entry; that's established
   practice in this file already). State plainly what was added, the
   confidence tier and why, and anything that couldn't be verified.
8. **Commit and push** per the git conventions below.

## Verifying a change

There's no committed test suite, so the actual repeatable check is a Node
one-liner that `eval`s the `D` array out of the raw HTML text and confirms
it still parses as valid JS, then recomputes the counts the README table
needs — run this after any edit to `D`, `BRANDS`, or `INVENTORS`:

```bash
node -e "
const fs = require('fs');
const html = fs.readFileSync('index.html','utf8');
const m = html.match(/const D = \[([\s\S]*?)\n\];/);
const D = eval('let D=[' + m[1] + '\n];D');
console.log('Total:', D.length);
const count = (pred) => D.filter(pred).length;
console.log('active:', count(d=>d.st==='active'));
console.log('expired:', count(d=>d.st==='expired'));
console.log('pending:', count(d=>d.st==='pending'));
console.log('unknown:', count(d=>d.st==='unknown'));
console.log('litigated:', count(d=>(d.b||[]).includes('litigated')));
console.log('conf v:', count(d=>d.conf==='v'));
console.log('conf m:', count(d=>d.conf==='m'));
console.log('conf l:', count(d=>d.conf==='l'));
"
```

A thrown error here means a syntax mistake in the edit (a missing comma, an
unclosed string, a stray brace) — fix it before committing; a parse failure
in `D` breaks the entire page, not just one card. For a `BRANDS`/`INVENTORS`
change, the same pattern works against `const BRANDS = \[([\s\S]*?)\];` /
`const INVENTORS = \[([\s\S]*?)\n\];`.

There's no visual/rendering check available without a browser — if a change
touches layout, CSS, or interactive behavior rather than just `D`, say
plainly that it's unverified visually rather than implying it was tested.

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

When asked to review or clean up rather than just add an entry, run all six:

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
