# MTB Patent Atlas

**45 years of mountain bike invention — who patented it, who fought over it, and when it became free for everyone to use.**

An interactive timeline of mountain bike intellectual property: 214 patents and applications spanning 1890 to 2026, organized into eight categories, with dedicated views for the industry's major litigation, a live stats dashboard, four distinct visual themes, and zero build tooling required. A single HTML file that opens in any browser.

🔗 **Live:** [postmillennium-mtb.github.io/MTB-PATENT-ATLAS](https://postmillennium-mtb.github.io/MTB-PATENT-ATLAS/)
📁 **Repo:** [github.com/postmillennium-MTB/MTB-PATENT-ATLAS](https://github.com/postmillennium-MTB/MTB-PATENT-ATLAS)
✍️ A RedFoxRun / PostMillennium MTB project.

---

## At a glance

| | |
|---|---|
| **Total entries** | 214 |
| **Year range** | 1890 – 2026 |
| **Active patents** | 107 |
| **Expired patents** | 69 |
| **Pending applications** | 34 |
| **Litigated entries** | 19 |
| **Patent Fights (named rivalries)** | 7 |
| **Brands** | 74 |
| **Named inventors** | 21 |
| **Non-US jurisdictions** | 14 (AU, BE, CH, CN, DE, EP, ES, FR, GB, IS, IT, PL, SE, ZA) |
| **Verified entries** | 101 |
| **Medium confidence** | 61 |
| **Draft / in progress** | 52 |

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

### 🔗 Shareable deep links
Every filter combination, search term, active tab, and individual card now has its own URL. The **Share view** button (next to the result count) copies a link that reproduces the exact view it was copied from — filters, search, and all. Individual cards resolve by patent number (or a title slug for unverified entries), so a link can point at one specific patent. Handy for citing a specific view or card from a Pinkbike article instead of telling readers "search for it yourself."

### 🎲 Surprise me
Jumps to a random card from whatever's currently visible (respects active filters), opens it, and scrolls it into view. A low-effort way to surface entries from deep in a 214-item catalogue that most visitors would otherwise never scroll to. The button also gives itself a subtle shimmer at a random interval (roughly every 20–90 seconds) as a passive hint that it's interactive — it never interrupts a click and turns itself off for anyone with reduced-motion preferences set.

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

Canfield (Lance & Chris) · Dave Weagle · Horst Leitner · Joe Breeze · Paul Turner · Jo Klieber · David Earle · Wayne Lumpkin · Gavin Vos · Cal Phillips · Richard Bryne · Brian Scura · Charles Curnutt · Damon Madsen · Scot Breithaupt · Sam Garrett · Adam Krefting · Benedikt Skulason · Owen Pemberton · Mic Williams · Bill Shook

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

**Deep links inside an iframe:** the Share button copies the standalone `github.io` URL, not an iframe-wrapped one — that's intentional, since it's the only URL that resolves correctly on its own. If the browser blocks URL rewriting inside a sandboxed iframe (some embed contexts do), the tool degrades gracefully: filtering and browsing still work, only the "URL reflects current view" behavior is skipped.

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

---

## License

No license file is currently included. MIT is a reasonable default for a reference/data project of this type.
