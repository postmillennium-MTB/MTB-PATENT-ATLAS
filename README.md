# MTB Patent Atlas

**45 years of mountain bike invention — who patented it, who fought over it, and when it became free for everyone to use.**

An interactive timeline of mountain bike intellectual property: 223 patents and applications spanning 1890 to 2026, organized into eight categories, with dedicated views for the industry's major litigation, a live stats dashboard, four distinct visual themes, and zero build tooling required. A single HTML file that opens in any browser.

🔗 **Live:** [postmillennium-mtb.github.io/MTB-PATENT-ATLAS](https://postmillennium-mtb.github.io/MTB-PATENT-ATLAS/)
📁 **Repo:** [github.com/postmillennium-MTB/MTB-PATENT-ATLAS](https://github.com/postmillennium-MTB/MTB-PATENT-ATLAS)
✍️ A RedFoxRun / PostMillennium MTB project.

---

## At a glance

| | |
|---|---|
| **Total entries** | 223 |
| **Year range** | 1890 – 2026 |
| **Active patents** | 110 |
| **Expired patents** | 74 |
| **Pending applications** | 35 |
| **Litigated entries** | 20 |
| **Patent Fights (named rivalries)** | 7 |
| **Brands** | 117 |
| **Named inventors** | 33 |
| **Non-US jurisdictions** | 14 (AU, BE, CH, CN, DE, EP, ES, FR, GB, IS, IT, PL, SE, ZA) |
| **Verified entries** | 109 |
| **Medium confidence** | 61 |
| **Draft / in progress** | 53 |

This table is a snapshot. For live, always-current numbers — plus a category breakdown and a most-patented-names leaderboard — see the **📊 Stats** tab in the tool itself, which recomputes from the data on every load.

---

## What's in it

### Eight categories
Rear Suspension · Forks & Damping · Drivetrain · Wheels & Tires · Components · E-MTB & Electronics · Frame & Standards · Bike Transport

### 📈 Patents-per-era bar chart
A scrubber above the filter bar renders the full dataset as a tappable bar chart, bracketed by year. Three bracket sizes are available via the toggle in the top-right of the scrubber:

- **2yr** (default) — the balance point between too dense to read and too coarse to be useful
- **1yr** — every year gets its own bar
- **5yr** — half-decade buckets (e.g. 1995–1999, 2000–2004 are each a single bar), for a zoomed-out view of eras

Tapping any bar jumps straight to that era's section in the timeline. Bars carry a tooltip with the exact count; a subset get a visible year label underneath, thinned automatically on narrow screens so labels never collide. Where the dataset has a real multi-decade silence (e.g. between the earliest 1890 entry and the next one in the mid-1970s), a dashed gap marker breaks the axis rather than drawing the two eras as if they were adjacent.

### ⚔ Patent Fights view
A dedicated tab frames the industry's seven major disputes as named rivalries — not just a filtered list, but head-to-head case cards showing the combatants, what the fight was actually about, how it ended, and tappable chips that jump directly to the affected patent cards in the timeline:

1. **Weagle v. Trek** — the concentric-pivot war (Split Pivot vs. ABP)
2. **Fox v. SRAM** — bleed-valve and damper fight, transferred to Colorado District Court
3. **SRAM v. the Industry** — narrow-wide chainring claims against Race Face, Fox, Praxis, Wolf Tooth
4. **Stan's v. Specialized** — Bead Socket Technology tubeless rim patent
5. **Speedplay v. Bebop** — founder-license pedal case, Federal Circuit (2000)
6. **Spot v. Gates** — belt-drive Drop-Out dropout royalty suit, currently active in Denver District Court
7. **Knolly v. Intense** — seat-tube geometry patent, resolved May 2021 on prior art

### 📊 Stats view
A dedicated tab that turns the raw dataset into a live dashboard: total/active/expired/litigated counts, a status-split bar, entries-by-category, and a most-patented-names leaderboard (brands and inventors combined, top 12). Every bar is tappable — clicking a category or a name jumps straight into the filtered timeline. Nothing here is hand-maintained; it's all computed from `D` at render time, so it can't drift out of sync the way a written-out stats table can.

### ⏳ Going free soon
A dedicated Status filter surfaces active patents estimated to expire within the next two years — the atlas's forward-looking answer to its own tagline about technology "becoming free for everyone to use." Qualifying cards carry an amber "⏳ free by [year]" pill. The same list appears at the top of the Stats tab as a tap-to-jump watchlist.

### 🔗 URL reflects the current view
Every filter combination, search term, active tab, and individual card has its own URL — the browser's address bar updates automatically as you filter and browse, and reloading or bookmarking a page returns to the same view. Individual cards resolve by patent number (or a title slug for unverified entries), so a URL can point at one specific patent. There's no dedicated "copy link" button for this at the moment — pulled deliberately, see *Recent updates* below — so sharing a specific view currently means copying the address bar URL directly.

### 🎲 Surprise me
Jumps to a random card from whatever's currently visible (respects active filters), opens it, and scrolls it into view. A low-effort way to surface entries from deep in a 217-item catalogue that most visitors would otherwise never scroll to. The button also gives itself a subtle shimmer at a random interval (roughly every 20–90 seconds) as a passive hint that it's interactive — it never interrupts a click and turns itself off for anyone with reduced-motion preferences set.

### 📍 Colorado MTB Innovation panel
A slide-in explainer auto-linked from cards involving Colorado-connected brands (Spot, Gates, MRP, Revel, Reeb). Covers the CBF/Revel licensing story, the Spot v. Gates suit, and the Fox v. SRAM jurisdictional transfer to Colorado. Minimizes to a persistent tab; reopens with one tap. Esc key or overlay-click also minimizes.

### Four distinct visual themes
Each theme has its own structural personality — not just a different color, but different corner radii, node shapes, card borders, typography weight, and header treatment. The theme switcher lives at the top of the header, directly under the PMR link, so it's the first thing available on both desktop and mobile before scrolling into the rest of the tool:

| Theme | Club | Personality |
|---|---|---|
| **WMBC** | Wisconsin Mountain Bike Coalition | Clean trail / topographic — soft 14px rounded corners, round nodes, green gradient header |
| **COMBA** | Colorado Off-Road Mountain Bicyclists | Vintage editorial print — warm cream, sharp 3px corners, square nodes, flat earthy header |
| **CAMBA** | California Mountain Bike Association | Bold racing / high-contrast — 0px sharp corners, hard offset shadows, square pills, red left-edge accent on litigated cards |
| **CAMBR** | Chicago Area Mountain Bike Riders | Technical blueprint — navy structure, orange accents, 6px corners, mono-forward |

### Scrollable filter tabs
Eight tabs across the top of the filter bar: Category · Status · Story · Inventors · Brands · All · 📊 Stats · ⚔ Fights. The Inventors and Brands rows (the long ones) have left/right scroll arrows that appear only when content overflows, soft fade-edge cues, and a "Show all" button that wraps everything onto multiple lines for full at-a-glance access.

### International patent office links
Entries with non-US filings carry a jurisdiction tag and link out to the relevant national patent office (DPMA, UK IPO, INPI, PRV, EPO/Espacenet, IP Australia, CIPO, UPRP) or to the direct Google Patents record when available. Taiwan's 3-letter TWI prefix and US reissue patents (RE-prefix) are handled automatically by the link-building logic.

### PMR link
A "PMR ↗" button in the header top-right returns to [postmillenniumrenaissance.com](https://www.postmillenniumrenaissance.com), the parent site for this and the rest of the PMR tool suite.

---

## Named inventors

Canfield (Lance & Chris) · Dave Weagle · Horst Leitner · Joe Breeze · Paul Turner · Jo Klieber · David Earle · Wayne Lumpkin · Gavin Vos · Cal Phillips · Richard Bryne · Brian Scura · Charles Curnutt · Damon Madsen · Scot Breithaupt · Sam Garrett · Adam Krefting · Benedikt Skulason · Owen Pemberton · Mic Williams · Bill Shook · Frank W. Schwinn · Frank P. Brilando · McKay H. Davis · Jim Busby · Mert Lawwill · Tony Ellsworth · Gary Ewing · Doug Bradbury · Cedric Eveleigh · Wayne Sicz · John Rader · John Castellano

---

## Tech stack

Single HTML file. No build step, no package manager, no framework, no dependencies beyond two Google Fonts loaded via CDN (Barlow and Barlow Condensed). Opens directly in a browser or deploys as-is to GitHub Pages. Tested against a jsdom harness covering filtering, theme token application, era-bracket aggregation at all three bar-chart granularities, Patent Fights rendering, Stats view rendering and click-through, going-free-soon matching, deep-link read/write (including graceful fallback when the browser blocks URL rewriting), surprise-me from every tab, Colorado panel visibility, scroll-arrow behavior, `who[]` registration integrity against `BRANDS`/`INVENTORS`, and regression across all major features after each build.

---

## Embedding in Pinkbike or similar platforms

The page works as a standalone link or an `[IFRAME]` embed. Pinkbike's embed syntax:

```
[IFRAME width=text height=1100 mobileHeight=1800 src="https://postmillennium-mtb.github.io/MTB-PATENT-ATLAS/"]
```

**Known limitation:** `position: sticky` (filter bar) and `position: fixed` (Colorado panel) resolve against the *iframe's* own viewport, not the host page. Inside a fixed-height iframe, the sticky filter bar scrolls away when the reader scrolls the article page and doesn't return without manually scrolling inside the iframe. On mobile this is the most noticeable friction point. A `?embed=1` mode that wraps the atlas in its own internal scroll container would fix this cleanly and is a planned improvement. Test in an actual iframe before publishing.

**Deep links inside an iframe:** the address bar always reflects the standalone `github.io` URL, not an iframe-wrapped one — that's a consequence of how the hash-routing is written, and it's actually the right behavior, since it's the only URL that resolves correctly on its own. If the browser blocks URL rewriting inside a sandboxed iframe (some embed contexts do), the tool degrades gracefully: filtering and browsing still work, only the "URL reflects current view" behavior is skipped.

---

## Data schema

All content lives in the `D` array near the top of the `<script>` block. Each entry is a plain JavaScript object:

```js
{
  y: 1996,                    // year filed (required)
  g: 1997,                    // year granted, or null if pending
  t: "Title (US 1,234,567)",  // put the headline patent number in the title when there is one
  a: "Assignee / inventor",   // free text, shown on the card
  num: "1234567",             // primary patent number — plain digits, no commas, no prefix
  nums: ["1234567","7654321"],// OPTIONAL: only when a real portfolio needs multiple links
  cat: "susp",                // susp | fork | drive | wheel | comp | emtb | frame | transport
  st: "active",               // active | expired | pending | unknown
  exp: 2017,                  // estimated expiry (filing year + 20), or null
  j: "DE",                    // OPTIONAL: omit entirely for US filings
  b: ["litigated"],           // licensor | acquired | givenaway | litigated | priorart
  who: ["Trek"],              // brand/inventor filter tags — must exist in BRANDS or INVENTORS
  conf: "v",                  // v = verified | m = unverified number | l = draft / in progress
  s: "Factual summary...",    // 1–3 sentences, what the patent covers and its history
  w: "Why it matters..."      // editorial payoff — what changed because of this patent
}
```

`exp` also drives the **Going free soon** filter and Stats watchlist automatically — active entries with `exp` within two years of the current year surface there with no extra tagging needed.

A single entry can also stand in for a whole product family rather than one specific filing — several GoPro entries do this deliberately (see *Bundled entries*, below) rather than adding a card per patent in a 1,600+ patent portfolio.

### Patent number formatting

Store numbers as plain digit strings with no commas, spaces, or `US` prefix. The `numLink` / `patentUrl` functions detect prefixes and format display labels automatically:

| Type | Store as | Displays as | Example |
|---|---|---|---|
| Standard US grant | `"7334846"` | US 7,334,846 | Stan's BST |
| US design patent | `"D896132"` | US D 896,132 | — |
| US reissue patent | `"RE45684"` | US RE 45,684 | Manitou |
| 2-letter country prefix | `"EP3111109"` | EP 3,111,109 | MRP Wave Ring |
| 3-letter country prefix | `"TWI386342"` | TWI 386,342 | Manitou Taiwan |
| WO publication | `"WO2025003104"` | WO 2025/003,104 | KOM Xeno Hub |
| US application | `"20190136918"` | US 20190136918 | Bill Shook ratchet ring |

### Confidence tiers

The `conf` field is an honesty mechanism, not cosmetic metadata:

- **`"v"`** — verified: patent number independently confirmed against a primary source (USPTO, Google Patents, a manufacturer's own virtual-marking page, or court filings)
- **`"m"`** — medium: the technology and story are confirmed but the specific number wasn't independently re-verified this pass
- **`"l"`** — draft: existence confirmed, number not yet located, or research still in progress

Several entries (WRP, EXT, Forbidden, Lauf's original Grit fork, Antidote, OPEN BAR, and the bundled GoPro category entries) are intentionally tagged `"m"` or `"l"` because the underlying companies operate on a deliberate patent-pending or trade-secret strategy, the entry stands in for an entire portfolio rather than one filing — not because of incomplete research. When adding entries, prefer an honest `"m"`/`"l"` over inflating to `"v"`.

### Bundled entries

A handful of entries represent a *category* of patents rather than a single filing — currently GoPro's action-camera portfolio (image processing/FOV, stabilization, hardware/acoustics, telemetry), grouped into four cards instead of one per patent. Use this pattern when a company's IP position matters to the story but individually cataloguing a 1,000+ patent portfolio would swamp the rest of the dataset. Bundled entries cite one representative patent number where a specific filing is genuinely the best example, and are tagged `conf: "l"` since no single number fully verifies the bundle.

### Adding a new brand or inventor

Every value used in an entry's `who[]` array must already exist in `BRANDS` (companies) or `INVENTORS` (named individuals, `{label, key}` pairs) near the top of the script. If a chip doesn't appear in the filter row, the missing registration here is the first place to check.

### Adding a new Patent Fight

Add an object to the `FIGHTS` array with: `key`, `title`, `sub`, `combatants[]`, `era`, `stakes`, `outcome`, and `cards[]`. The `cards[]` array takes patent number strings or distinctive title substrings; `fightCardMatches()` scans all `D[]` entries and auto-generates tap-to-jump chips for every match.

### A note on card identity

Each rendered card gets an HTML `id` of `p-<patent number>` (or a slugified title if there's no number), used by both the deep-link and surprise-me features to jump to a specific entry. Adding a new patent doesn't require touching this — the id is generated automatically from existing fields at render time.

---

## Methodology and sourcing

Compiled from USPTO and Google Patents records, manufacturer virtual-marking pages (Fox, Wolf Tooth, Hayes Bicycle Group, MRP, Shimano, Manitou, and others), court filings, and industry reporting (Pinkbike, BikeRadar, Bicycle Retailer, Singletracks, MTBR, Singletrack World, Vital MTB, Escape Collective).

Primary-source verification is preferred throughout. Where verification wasn't possible, entries carry an honest confidence label rather than inflated certainty. This includes checking third-party product claims against the primary patent record rather than taking them at face value — a product marketed under a "chin mount" name, for instance, doesn't necessarily mean the seller holds a patent on the mechanism, or that a patent with a similar-sounding title is actually the same invention.

Expiration dates are estimated as filing year + 20 years and do not account for terminal disclaimers, maintenance fee lapses, or patent term adjustments. **Nothing here is legal advice.**

For patents that issued before June 8, 1995 (when US law switched to a 20-years-from-filing term), `exp` is instead estimated as **grant year + 17 years** for utility patents or **grant year + 14 years** for design patents, matching the actual pre-GATT statutory term. The atlas's three Schwinn entries (1938–1966) are the only current cases old enough for this to matter, but it's the correct rule for any pre-1995 filing added later.

Corrections, additional patents, and better sourcing are welcome — open an issue or PR.

---

## Recent updates (July 2026)

- **Fixed the 5-year bar chart bug.** The bar chart's "5yr" bracket wasn't aggregating into five-year buckets — it was silently falling back to one bar per year, making it the *most* granular view rather than the least. It now genuinely buckets by half-decade (1995–1999, 2000–2004, etc.), aligned to the calendar rather than to the dataset's earliest entry, so the buckets stay stable as more patents are added. The chart also gained a dashed gap marker for real multi-decade silences in the data (there's an 84-year gap between the 1890 entry and the next), and its final bucket's label no longer advertises years that haven't happened yet.
- **Default bar bracket changed from 5yr to 2yr.**
- **Bar chart date labels are now legible on all four themes** — full white with a text shadow rather than a low-opacity gray that got lost against colored headers — and thin out automatically on narrow screens instead of just shrinking to an unreadable size.
- **Theme switcher moved** to the top of the header, directly under the PMR link, ahead of the title — visible immediately on both desktop and mobile.
- **Surprise Me now shimmers** at a random 20–90 second interval as a passive discoverability hint. Subtle by design, respects `prefers-reduced-motion`, and never blocks the click target.
- **New entries:** the Yeti Sixfinity entry now covers the July 2026 Yeti LT, which moves off the Switch Infinity platform onto the six-bar layout — the first time that migration has shown up on a non-assist bike. Added a verified action-camera chin-mount patent (US 10,021,931, Sopro Mounts Inc.) and four bundled GoPro entries covering image processing/FOV, stabilization, hardware/design, and telemetry, rather than attempting to catalogue a 1,600+ patent portfolio one filing at a time.
- **Corrected a mismatched patent reference:** an earlier candidate for the camera chin-mount category (US 7,735,160) turned out to be an unrelated football helmet chin-guard patent with no camera-mount claims. Replaced with the correct filing.
- **Added Schwinn** as a registered brand, with three verified entries spanning the company's two most historically significant filings: the 1938 cantilever frame (US 2,151,533) and Knee-Action Spring Fork (US 2,160,034) — filed the same day by Frank W. Schwinn — and the 1965 Sting-Ray banana seat design patent (US D204,121) by Frank P. Brilando, which was itself invalidated on appeal in 1970 after Schwinn's own prior advertising became prior art against its own patent. All three predate the atlas's existing entries by decades and fill in real ground between the 1890s bicycle-mechanics patents and the 1970s mountain-bike-specific ones. Corrected `exp` for all three using the pre-1995 statutory term (grant + 17/14 years) rather than the atlas's usual filing + 20 shorthand, which would have been wrong by nearly a decade for patents this old.
- **Open question, not yet decided:** whether GoPro-type entries (currently split across `comp` and `emtb`) warrant a ninth category — tentatively "Tech" or similar — rather than being absorbed into the existing eight. See *A note on the "Tech" category question*, below, for the tradeoffs as they stand today.

**Later in July 2026:**

- **Fixed state/region search coverage.** Searching "Colorado," "California," "Wisconsin," or "Utah" previously only matched entries whose prose happened to mention the state (litigation venues, mostly) — so "California," the state where mountain biking itself was invented, returned exactly one result, and "Utah" returned zero. Search now also checks each entry's brands against a new `BRAND_HQ` lookup table of company/inventor headquarters, so a state search surfaces every entry for brands based there, not just the ones that spell it out. Colorado: 6 → 12 results. California: 1 → 29. Wisconsin: 3 → 12. Utah: 0 → 2. The existing Colorado MTB Innovation panel now reads from this same table instead of a separate hardcoded brand list, so the two features can't drift out of sync with each other. `BRAND_HQ` is intentionally partial — only brands and inventors verified so far are tagged, not all 78 in `BRANDS` — and documented in the source as straightforward to extend.
- **Added Rocky Mountain** (Vancouver-area, BC) as a registered brand: their foundational 2002 rear-suspension patent (US 6,843,494, Duhane Lam), and the Dyname e-bike propulsion system (US 9,643,683) — which turns out to be a genuine licensor story rather than in-house IP. Dyname is built by a separate company, Propulsion PowerCycle Inc., under an exclusivity deal with Rocky Mountain that ran 2017 through a 2024–25 ownership change at Rocky Mountain, after which Dyname became free to supply other brands.
- **Added VelociRAX** (Lehi, UT) as a registered brand: the C-hoop vertical hitch rack portfolio (US 11,554,724 and four related patents), filed by founders Blake and Bryce Owen. A third rack architecture in the Bike Transport category, alongside the existing tray-rack (Cal Phillips/1UP) and hook-rack coverage — and the entry that makes "Utah" search return something.
- **Added a verified Utah patent from the historical record:** McKay H. Davis's 1994 water-bottle-cage battery light system (US 5,426,570, Salt Lake City) — a 1994 solution to mounting a heavy light battery on a bike by force-fitting it into a standard bottle cage, cross-checked against a contemporary Deseret News patent listing.
- **Added Yoshimura Cycling** (Chino, CA) as a registered brand: the Chilao SS pedal's "Static Spring" axle preload system, tagged honestly as patent-pending (`conf: "l"`) since no application number has surfaced in any 2024–2025 coverage.
- **Added the Specialized/Dave Weagle linkage fork** (US 11,345,432): a sixth atlas entry under Weagle's name, and a different IP story than his suspension-linkage work — Weagle's own startup Trvstper Inc. (maker of the Trust Shout and Message forks) filed it in 2018, folded, and the patent migrated to Specialized in 2021. Badged `acquired`, cross-referencing the existing Fox v. SRAM and Horst Link acquisition entries.
- **Removed the Share view button.** The URL still updates automatically to reflect the current filter/search/card state (that underlying mechanism wasn't touched), but the one-click "copy a shareable link" button and its confirmation flash are gone — a deliberate step back on the sharing concept, revisited at a later date.
- **Fixed a systemic search/filter gap: 47 of 223 entries had no brand or inventor tags at all.** The Supre Drive entry (Cedric Eveleigh / Lal Bikes) was one of them — the name was right there in the card's own text, but `who: []` was empty, so it never showed up under the Brands or Inventors filter tabs, and would have stayed invisible to anyone browsing rather than free-text searching. An audit of every entry with an empty `who[]` found 47 more of the same pattern — Cannondale, Marzocchi, Crankbrothers, Magura, Pinion, Atherton, and 40 others, all real, identifiable brands or inventors sitting unloaded. All 47 are now correctly tagged, adding 38 new brands and 9 new named inventors to the registries. The 8 entries still showing an empty `who[]` are genuinely anonymous (unnamed 19th-century inventors, "independent inventors," a still-unverified assignee) — that's accurate, not a bug.
- **Closed the underlying reason this class of bug is easy to introduce: search text didn't cover everything a card actually displays.** Free-text search previously only scanned title, assignee, summary, editorial text, and patent number — not the category pill, status pill, badge pill text, jurisdiction, or filing/grant/expiry years, even though all of those are printed right on the card. Searching a word the person could literally see and not finding it is worse than the word not existing at all. Search now also indexes the category label ("Drivetrain," "Rear Suspension," …), badge text ("Litigated," "Patent acquired," …), jurisdiction code and full patent-office name, and the filing/grant/expiry years — so any visible text on a card is now findable by typing it.

---

## A note on the "Tech" category question

Every current entry fits the existing eight categories (`susp fork drive wheel comp emtb frame transport`), including the new GoPro entries, which are split across `comp` (image processing, stabilization, hardware/acoustics) and `emtb` (telemetry). Whether that's the right long-term home, or whether a ninth category — "Tech," "Camera & Electronics," something similar — would serve better, is an open call rather than a settled one. The tradeoffs as of this update:

**For a new category:** GoPro doesn't cleanly fit "Components" (a physical bike part) or "E-MTB & Electronics" (motor/battery systems specifically) — it's neither. Future camera-and-sensor entries (action cameras, ride computers, the suspension-AI telemetry entries already in the atlas) would have a clearer home, and the Stats view's category breakdown would more accurately reflect where the dataset's weight sits as this area grows.

**Against, for now:** only 5 entries currently fall in this space (4 GoPro bundles + the chin mount) — thin enough that a dedicated filter tab risks reading as a single-brand category rather than a genuine cluster. Adding a ninth category is also a real identity change: the README, meta description, and site tagline all currently describe "eight categories," and the filter-tab row would need to accommodate the addition without crowding on mobile.

**Implementation note, if it happens:** category rendering is fully data-driven from the `CATS` object near the top of the script (filter chips, card pills, and the Stats breakdown all read from it directly) — adding a key there is a small, low-risk change with no hardcoded per-category styling to update elsewhere. The harder part is deciding the boundary and migrating the 5 existing `comp`/`emtb` entries, not the code.

No action taken on this yet — flagging it here so the decision and its tradeoffs are on record rather than made silently in a future update.

---

## License

No license file is currently included. MIT is a reasonable default for a reference/data project of this type.
