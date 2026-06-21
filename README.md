# MTB Patent Atlas

**45 years of mountain bike invention — who patented it, who fought over it, and when it became free for everyone to use.**

A single-file, interactive timeline of mountain bike intellectual property: 206 patents and applications spanning 1890 to the present, with four distinct visual themes, a dedicated view for the industry's major litigation, and zero build tooling required.

🔗 **Live:** [postmillennium-mtb.github.io/MTB-PATENT-ATLAS](https://postmillennium-mtb.github.io/MTB-PATENT-ATLAS/) · **Repo:** [github.com/postmillennium-MTB/MTB-PATENT-ATLAS](https://github.com/postmillennium-MTB/MTB-PATENT-ATLAS)

A RedFoxRun / PostMillennium MTB project.

---

## What's in it

- **206 entries** spanning Rear Suspension, Forks & Damping, Drivetrain, Wheels & Tires, Components, E-MTB & Electronics, Frame & Standards, and Bike Transport
- **70 brands** and **20 named inventors**, each filterable
- **⚔ Patent Fights** — 7 major rivalries (Weagle v. Trek, Fox v. SRAM, SRAM v. the Industry, Stan's v. Specialized, Speedplay v. Bebop, Spot v. Gates, Knolly v. Intense) presented as head-to-head dispute cards with stakes, outcome, and tap-to-jump links into the affected patents
- **4 color themes**, each with its own structural personality rather than just a different hue:
  - **WMBC** — clean trail/topographic: soft rounded corners, round timeline nodes
  - **COMBA** — vintage editorial print: warm cream, squared corners, flat header
  - **CAMBA** — bold racing/high-contrast: sharp corners, hard offset shadows, red accent stripe on litigated cards
  - **CAMBR** — technical blueprint: navy structure, orange accents, mono-forward
- **📍 Colorado MTB Innovation panel** — a slide-in explainer auto-linked from any card involving a Colorado-connected brand (Spot, Gates, MRP, Revel, Reeb), minimizable to a small persistent tab
- International coverage beyond the US: patents/applications tagged for Germany, UK, France, Sweden, Australia, EPO, Canada, Poland, Taiwan, Belgium, Switzerland, Italy, Iceland, Spain, and China, with links out to the relevant national patent office or Espacenet when no US filing exists
- A timeline scrubber with selectable grouping (5yr / 2yr / 1yr buckets), full-text search, and tabbed filters (Category, Status, Story, Inventors, Brands, All, Fights) with overflow-aware scroll arrows + a "Show all" expand on the long rows

## Tech stack

Single HTML file. No build step, no package manager, no framework. Vanilla JS, CSS custom properties for theming, Google Fonts (Barlow / Barlow Condensed) loaded via CDN. Opens directly in a browser or deploys as-is to GitHub Pages.

## Embedding (e.g. in a Pinkbike article)

The page works as a standalone link or an `<iframe>` embed. **Known limitation:** `position: sticky` (the filter bar) and `position: fixed` (the Colorado panel) resolve against the iframe's own viewport, not the host page — inside a short iframe on an article page, the sticky filter bar will scroll out of reach. A fixed-height embed mode (own internal scroll container, toggled via a `?embed=1` query param) would fix this and has not yet been built. Test in an actual iframe before publishing, not just standalone.

## Data schema

All content lives in the `D` array near the top of the `<script>` block. Each entry:

```js
{
  y: 1996,            // year filed (required)
  g: 1997,             // year granted, or null if pending
  t: "Title (US 1,234,567)",   // include the headline patent number in the title when there is one
  a: "Assignee / inventor text",
  num: "1234567",       // primary patent number, no commas/prefix — or null
  nums: ["1234567","7654321"], // OPTIONAL — only when num alone isn't enough (a real portfolio)
  cat: "susp",          // one of: susp, fork, drive, wheel, comp, emtb, frame, transport
  st: "active",         // active | expired | pending | unknown
  exp: 2017,            // expiration year estimate (filed + 20), or null
  j: "DE",              // OPTIONAL — jurisdiction code if not a US filing; omit for US
  b: ["litigated"],     // badges: licensor, acquired, givenaway, litigated, priorart
  who: ["Trek"],        // brand/inventor tags — MUST already exist in BRANDS or INVENTORS
  conf: "v",            // v = verified, m = number unverified, l = draft / research in progress
  s: "...",             // factual summary, 1–3 sentences
  w: "..."              // "why it matters" — the editorial payoff line
}
```

**Patent number formatting:** plain digits only (`"1234567"`, not `"1,234,567"`). Design patents use a leading `D` (`"D896132"`). Reissue patents use `RE` (`"RE45684"`). Non-US numbers carry their country prefix (`"EP3111109"`, `"WO2025003104"`, `"TWI386342"` — 2-or-3-letter prefixes are both handled). The link-building logic (`numLink` / `patentUrl`) detects these prefixes automatically; don't hand-format URLs.

**Confidence tiers (`conf`)** are not cosmetic — they're an honesty mechanism:
- `"v"` — patent number independently verified against a primary source (USPTO, Google Patents, the company's own marking page, court filings)
- `"m"` — the technology/story is confirmed but the specific number wasn't independently re-verified
- `"l"` — draft: existence confirmed, number not located, or research still in progress

When adding entries, prefer `"m"`/`"l"` honestly over inflating to `"v"` — several existing entries (WRP, EXT, Forbidden, Lauf's original fork) are intentionally tagged this way because the underlying companies themselves operate on patent-pending/trade-secret strategies, not because of incomplete research.

### Adding a new brand or inventor

Add to `BRANDS` (companies) or `INVENTORS` (named individuals, `{label, key}` pairs) near the top of the script — every value used in an entry's `who[]` must already exist in one of these two lists, or that filter chip won't render.

### Adding a new Patent Fight

Add an object to the `FIGHTS` array: `key`, `title`, `sub`, `combatants[]`, `era`, `stakes`, `outcome`, and `cards[]` — the last referencing existing `D[]` entries by exact patent number or a distinctive title substring (matched via `fightCardMatches()`). The fight card auto-generates tap-to-jump chips for every matched card.

## Methodology / sourcing

Compiled from USPTO and Google Patents records, manufacturer virtual-marking pages, court filings, and industry reporting (Pinkbike, BikeRadar, Bicycle Retailer, Singletracks, MTBR, and others). Expiration dates are estimated as filing date + 20 years and don't account for terminal disclaimers, fee lapses, or patent term adjustments. **Nothing here is legal advice.**

Corrections, missing patents, and better sourcing are welcome — open an issue or a PR.

## License

No license file yet — add one (MIT is a reasonable default for a reference/data project like this) before treating this as open for reuse.
