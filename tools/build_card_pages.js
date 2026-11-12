#!/usr/bin/env node
/* Builds one small link-preview page per Atlas card, at p/<ref>/index.html.

   Why: a shared card link used to be .../atlas/#p=<ref>. Link-preview bots
   (Pinkbike, iMessage, Slack, Facebook, X, Google) never send the part after
   "#" to the server, so every shared card unfurled as the same generic
   "MTB Patent Atlas" title and picture. Each page here carries its own card's
   title, a one-line description and its first drawing in the og:/twitter:
   tags, then forwards a human visitor to the Atlas on that card
   (postmillenniumrenaissance.com/atlas/#p=<ref>), so the reader lands in the
   real tool exactly as an old #p= link did.

   index.html stays one file: nothing here is loaded by it, and the Share
   button only builds the URL (CARD_PAGE_BASE_URL in index.html). The pages
   are generated, never hand-edited: .github/workflows/card-pages.yml runs
   this after a change to index.html reaches main and opens a pull request
   with whatever changed. Until that is merged a new card's link still works,
   because 404.html at the repo root sends any unknown /p/<ref>/ to the Atlas
   with #p=<ref> (only the preview is generic).

   Old refs in REF_ALIASES get a page too, built from the card they now point
   at, so a /p/ link survives the same renames a #p= link does.

   Usage (repo root or tools/):
     node tools/build_card_pages.js           write p/ (removes pages for refs that no longer exist)
     node tools/build_card_pages.js --check   exit 1 if p/ is out of date, write nothing
     node tools/build_card_pages.js --refs    print every card ref as JSON (smoke_test.js
                                              compares this with the page's own cardRef()) */
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(repoRoot, 'index.html'), 'utf8');

// Where the pages are served (GitHub Pages for this repo) and where a visitor
// is sent. ATLAS_URL matches SHARE_BASE_URL in index.html.
const SITE_URL = 'https://postmillennium-mtb.github.io/MTB-PATENT-ATLAS/';
const ATLAS_URL = 'https://postmillenniumrenaissance.com/atlas/';
const DEFAULT_IMG = { url: SITE_URL + 'social-preview.png', w: 1000, h: 852 };
const DESC_MAX = 200;  // characters; previews cut off around here anyway
const OUT_DIR = path.join(repoRoot, 'p');

function grab(re, label) {
  const m = html.match(re);
  if (!m) {
    console.error(`::error::Could not locate ${label} in index.html -- has its shape changed?`);
    process.exit(1);
  }
  return m[1];
}
const D = eval('let D=[' + grab(/const D = \[([\s\S]*?)\n\];/, 'the D array') + '\n];D');
const REF_ALIASES = eval('(' + grab(/const REF_ALIASES = (\{[\s\S]*?\n\});/, 'REF_ALIASES') + ')');

const txEN = f => (f == null ? '' : typeof f === 'object' ? (f.en || '') : String(f));

/* Same rule as the _REF block next to cardRef() in index.html: the patent
   number, "num-N" when several entries share one, else a slug of the English
   title. smoke_test.js fails if the two ever disagree. */
function computeRefs() {
  const counts = {}, seen = {}, refs = [];
  D.forEach(d => { if (d.num) counts[d.num] = (counts[d.num] || 0) + 1; });
  D.forEach(d => {
    if (d.num) {
      seen[d.num] = (seen[d.num] || 0) + 1;
      refs.push(counts[d.num] > 1 ? `${d.num}-${seen[d.num]}` : d.num);
    } else {
      refs.push(txEN(d.t).toLowerCase().replace(/\(.*?\)/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 40));
    }
  });
  return refs;
}

if (process.argv.includes('--refs')) {
  console.log(JSON.stringify(computeRefs()));
  process.exit(0);
}

// ---- text -------------------------------------------------------------
const CARD_LINK_RE = /\[\[card:([^|\]]+)\|([^\]]+)\]\]/g;
const EXT_LINK_RE = /\[\[link:(https:\/\/[^|\]]+)\|([^\]]+)\]\]/g;
/* Research-process wording never goes into a preview (CLAUDE.md, "Prose
   style": no "this pass", no "was/were not read", no "verified against").
   A sentence that contains any of these is dropped from the description. */
const NARRATION_RE = /\b(this pass|this session|front page|(?:was|were|is|are|not|never|un)\s*read\b|read directly|fetched|verified against|(?:independently|not yet) (?:located|verified|confirmed)|confirmed (?:from|against)|not seen|the user)\b/i;
/* A summary that opens with its docket history ("US 5,784,931 was filed July
   8, 1996 and granted ...") makes a poor preview line; such leading sentences
   are skipped when something else is left to say. */
const DOCKET_RE = /\b(?:filed|granted|published|issued)\b[^.]*\b(?:1[89]|20)\d\d\b/i;
const DOCKET_START_RE = /^(?:filed|granted|published|issued|(?:US|EP|WO|DE|GB|FR|JP|TW|CN)\b|U\.S\.|an? (?:international|PCT|U\.S\.|US) )/i;

function plain(str) {
  return str.replace(CARD_LINK_RE, '$2').replace(EXT_LINK_RE, '$2')
    .replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
}
/* Split at a full stop followed by a capital, but not after an abbreviation
   ("Shimano Inc.", "No.", "Fig.", "U.S.") or a lone initial ("Joseph T."). */
const ABBREV_RE = /(?:\b(?:Inc|Co|Corp|Ltd|No|Nos|Fig|Figs|Pat|Ser|St|Mr|Mrs|Dr|Jr|Sr|vs|approx|e\.g|i\.e|U\.S|ca)|\b[A-Z])\.$/;
function sentences(str) {
  const out = [];
  let start = 0;
  const re = /[.!?]+(?=\s+["“(]?[A-Z0-9])/g;
  let m;
  while ((m = re.exec(str))) {
    const end = m.index + m[0].length;
    if (ABBREV_RE.test(str.slice(Math.max(0, end - 8), end))) continue;
    out.push(str.slice(start, end).trim());
    start = end;
  }
  out.push(str.slice(start).trim());
  return out.filter(Boolean);
}
function clip(str, max) {
  if (str.length <= max) return str;
  const cut = str.slice(0, max - 1);
  const sp = cut.lastIndexOf(' ');
  return (sp > max * 0.6 ? cut.slice(0, sp) : cut).replace(/[\s,;:–—-]+$/, '') + '…';
}
/* The entry's one-line hook when it has one, else its summary (s), else its
   "why it matters" (w), minus any narration sentence, cut to DESC_MAX. */
function description(d) {
  for (const f of [d.hook, d.s, d.w]) {
    const text = plain(txEN(f));
    if (!text) continue;
    const kept = sentences(text).filter(s => !NARRATION_RE.test(s));
    while (kept.length > 1 && DOCKET_RE.test(kept[0]) && DOCKET_START_RE.test(kept[0])) kept.shift();
    if (kept.length) return clip(kept.join(' '), DESC_MAX);
  }
  return 'A patent in the MTB Patent Atlas: the patents behind the modern mountain bike.';
}

// ---- image ------------------------------------------------------------
/* Pixel size from the file header, so previews can reserve the right box
   (Facebook and LinkedIn ignore an image on first share without it). */
function imageSize(file) {
  let b;
  try { b = fs.readFileSync(file); } catch (e) { return null; }
  if (b.length > 24 && b.readUInt32BE(0) === 0x89504e47) return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  if (b.length > 10 && b.toString('ascii', 0, 3) === 'GIF') return { w: b.readUInt16LE(6), h: b.readUInt16LE(8) };
  if (b.length > 30 && b.toString('ascii', 0, 4) === 'RIFF' && b.toString('ascii', 8, 12) === 'WEBP') {
    const k = b.toString('ascii', 12, 16);
    if (k === 'VP8X') return { w: 1 + b.readUIntLE(24, 3), h: 1 + b.readUIntLE(27, 3) };
    if (k === 'VP8 ') return { w: b.readUInt16LE(26) & 0x3fff, h: b.readUInt16LE(28) & 0x3fff };
    if (k === 'VP8L') { const n = b.readUInt32LE(21); return { w: 1 + (n & 0x3fff), h: 1 + ((n >> 14) & 0x3fff) }; }
  }
  if (b[0] === 0xff && b[1] === 0xd8) {
    let i = 2;
    while (i + 9 < b.length) {
      if (b[i] !== 0xff) { i++; continue; }
      const mk = b[i + 1];
      if (mk >= 0xc0 && mk <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(mk)) return { w: b.readUInt16BE(i + 7), h: b.readUInt16BE(i + 5) };
      i += 2 + b.readUInt16BE(i + 2);
    }
  }
  return null;
}
function image(d) {
  const first = d.imgs && d.imgs.length ? d.imgs[0] : (d.img ? { src: d.img, alt: d.imgAlt } : null);
  if (!first || !first.src) return { ...DEFAULT_IMG, alt: 'MTB Patent Atlas' };
  const size = imageSize(path.join(repoRoot, decodeURI(first.src)));
  return { url: SITE_URL + first.src, w: size && size.w, h: size && size.h, alt: plain(txEN(first.alt)) || plain(txEN(d.t)) };
}

// ---- page -------------------------------------------------------------
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function page(ref, d, linkRef) {
  const title = plain(txEN(d.t));
  const desc = description(d);
  const img = image(d);
  const self = `${SITE_URL}p/${encodeURIComponent(ref)}/`;
  const dest = `${ATLAS_URL}#p=${encodeURIComponent(linkRef)}`;
  const dims = img.w && img.h ? `\n<meta property="og:image:width" content="${img.w}">\n<meta property="og:image:height" content="${img.h}">` : '';
  return `<!DOCTYPE html>
<!-- (c) 2026 Post Millennium Renaissance (https://www.postmillenniumrenaissance.com/). SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0. See LICENSE. -->
<!-- Generated by tools/build_card_pages.js from index.html. Do not edit by hand. -->
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} — MTB Patent Atlas</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${esc(self)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="MTB Patent Atlas">
<meta property="og:url" content="${esc(self)}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:image" content="${esc(img.url)}">${dims}
<meta property="og:image:alt" content="${esc(img.alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(desc)}">
<meta name="twitter:image" content="${esc(img.url)}">
<meta name="twitter:image:alt" content="${esc(img.alt)}">
<link rel="icon" href="../../favicon.ico">
<script>
/* Send the reader into the Atlas on this card. ?lang=fr (added by the Share
   button when the reader is browsing in French) carries over. */
(function(){
  var lang=null;
  try{ lang=new URLSearchParams(location.search).get("lang"); }catch(e){}
  location.replace(${JSON.stringify(dest)}+(lang&&/^[a-z]{2}$/.test(lang)&&lang!=="en"?"&lang="+lang:""));
})();
</script>
<style>body{font-family:system-ui,sans-serif;max-width:640px;margin:0 auto;padding:24px 16px;background:#f6f3ea;color:#1c1a14;line-height:1.5}img{max-width:100%;height:auto}a{color:inherit}.pmr-license{margin-top:32px;font-size:12px;text-align:center;border-top:1px solid rgba(128,128,128,.35);padding-top:10px}</style>
</head>
<body>
<p><a href="${esc(dest)}">Open this card in the MTB Patent Atlas</a></p>
<h1>${esc(title)}</h1>
<p>${esc(desc)}</p>
<div class="pmr-license"><p>&copy; 2026 Post Millennium Renaissance &middot; <a href="https://www.postmillenniumrenaissance.com/">postmillenniumrenaissance.com</a> &middot; Free for noncommercial use under <a href="https://polyformproject.org/licenses/noncommercial/1.0.0/">PolyForm Noncommercial 1.0.0</a>. Source studies remain the property of their authors.</p></div>
</body>
</html>
`;
}

// ---- build ------------------------------------------------------------
const refs = computeRefs();
const pages = new Map();   // ref -> html
const bad = [];
const SAFE_REF = /^[A-Za-z0-9][A-Za-z0-9-]*$/;
refs.forEach((ref, i) => {
  if (!SAFE_REF.test(ref)) { bad.push(ref); return; }
  pages.set(ref, page(ref, D[i], ref));
});
Object.entries(REF_ALIASES).forEach(([from, to]) => {
  const i = refs.indexOf(to);
  if (i < 0 || !SAFE_REF.test(from) || pages.has(from)) return;  // verify_data.js reports dead aliases
  pages.set(from, page(from, D[i], to));
});
if (bad.length) console.warn(`::warning::No page for refs that are not URL-safe: ${bad.join(', ')}`);

const existing = fs.existsSync(OUT_DIR) ? fs.readdirSync(OUT_DIR).filter(n => fs.statSync(path.join(OUT_DIR, n)).isDirectory()) : [];
const stale = existing.filter(n => !pages.has(n));
const changed = [...pages].filter(([ref, h]) => {
  const f = path.join(OUT_DIR, ref, 'index.html');
  return !fs.existsSync(f) || fs.readFileSync(f, 'utf8') !== h;
}).map(([ref]) => ref);

if (process.argv.includes('--check')) {
  if (stale.length || changed.length) {
    console.log(`card pages out of date: ${changed.length} to write, ${stale.length} to remove. Run node tools/build_card_pages.js`);
    process.exit(1);
  }
  console.log(`card pages up to date (${pages.size}).`);
  process.exit(0);
}

stale.forEach(n => fs.rmSync(path.join(OUT_DIR, n), { recursive: true, force: true }));
changed.forEach(ref => {
  fs.mkdirSync(path.join(OUT_DIR, ref), { recursive: true });
  fs.writeFileSync(path.join(OUT_DIR, ref, 'index.html'), pages.get(ref));
});
console.log(`card pages: ${pages.size} total, ${changed.length} written, ${stale.length} removed.`);
