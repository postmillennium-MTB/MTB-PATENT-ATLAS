#!/usr/bin/env node
/* Keeps every hand-written count in step with the data in index.html.

   The entry total and the README "At a glance" numbers are written out as
   plain text in eleven places (README intro + table, three <meta> tags,
   EN/FR shareText, EN/FR mtBannerText). This script recomputes them from D,
   BRANDS, INVENTORS and FIGHTS and rewrites them.

     node tools/sync_counts.js           # rewrite README.md and index.html
     node tools/sync_counts.js --check   # change nothing; exit 1 if any spot is stale

   verify_data.js runs the --check form, so CI fails when a count drifts.
   If a pattern below stops matching (someone reworded the sentence), the
   script says which one; fix the pattern here rather than the count by hand. */
'use strict';
const fs = require('fs');
const path = require('path');
const { loadAtlas } = require('./atlas_data');

const ROOT = path.join(__dirname, '..');
const check = process.argv.includes('--check');
const { D, BRANDS, INVENTORS, FIGHTS } = loadAtlas();

const n = pred => D.filter(pred).length;
const years = D.map(d => d.y).filter(y => typeof y === 'number');
const juris = [...new Set(D.map(d => d.j).filter(Boolean))].sort();
const c = {
  total: D.length,
  yMin: Math.min(...years),
  yMax: Math.max(...years),
  active: n(d => d.st === 'active'),
  expired: n(d => d.st === 'expired'),
  pending: n(d => d.st === 'pending'),
  np: n(d => d.np),
  litigated: n(d => (d.b || []).includes('litigated')),
  fights: FIGHTS.length,
  brands: BRANDS.length,
  inventors: INVENTORS.length,
  juris: `${juris.length} (${juris.join(', ')})`,
  v: n(d => d.conf === 'v'),
  m: n(d => d.conf === 'm'),
  l: n(d => d.conf === 'l'),
};

const row = (label, key) => [new RegExp(`(\\| \\*\\*${label}\\*\\* \\| )[^|]*?( \\|)`), key];
const README_RULES = [
  [/(An interactive timeline of mountain bike intellectual property: )\d+( patents and applications spanning )\d{4}( to )\d{4}/,
    m => `${m[1]}${c.total}${m[2]}${c.yMin}${m[3]}${c.yMax}`],
  row('Total entries', 'total'),
  [/(\| \*\*Year range\*\* \| )[^|]*?( \|)/, m => `${m[1]}${c.yMin} – ${c.yMax}${m[2]}`],
  row('Active patents', 'active'),
  row('Expired patents', 'expired'),
  row('Pending applications', 'pending'),
  row('Confirmed no patent', 'np'),
  row('Litigated entries', 'litigated'),
  row('Patent Fights \\(named rivalries\\)', 'fights'),
  row('Brands', 'brands'),
  row('Named inventors', 'inventors'),
  row('Non-US jurisdictions', 'juris'),
  row('Verified entries', 'v'),
  row('Medium confidence', 'm'),
  row('Draft / in progress', 'l'),
];
const HTML_RULES = [
  [/(<meta name="description" content="An interactive timeline of )\d+/, 'total'],
  [/(<meta property="og:description" content="An interactive timeline of )\d+/, 'total'],
  [/(<meta name="twitter:description" content="An interactive timeline of )\d+/, 'total'],
  [/(shareText:"MTB Patent Atlas — )\d+( mountain bike)/, 'total'],
  [/(shareText:"MTB Patent Atlas — )\d+( brevets)/, 'total'],
  [/(French content \(all )\d+( patent entries\))/, 'total'],
  [/(\(les )\d+( fiches de brevets\))/, 'total'],
];

let stale = 0, broken = 0;
function apply(file, rules) {
  const p = path.join(ROOT, file);
  let text = fs.readFileSync(p, 'utf8');
  for (const [re, how] of rules) {
    const m = text.match(re);
    if (!m) { console.error(`::error::sync_counts: pattern not found in ${file}: ${re}`); broken++; continue; }
    const repl = typeof how === 'function' ? how(m)
      : m.length > 2 ? `${m[1]}${c[how]}${m[2]}` : `${m[1]}${c[how]}`;
    if (repl !== m[0]) {
      stale++;
      console.log(`${check ? 'stale' : 'updated'} ${file}: "${m[0].slice(-60)}" -> "${repl.slice(-60)}"`);
      text = text.replace(re, repl);
    }
  }
  if (!check) fs.writeFileSync(p, text);
}
apply('README.md', README_RULES);
apply('index.html', HTML_RULES);

if (broken) process.exit(1);
if (check && stale) {
  console.error(`::error::${stale} count(s) out of date. Run: node tools/sync_counts.js`);
  process.exit(1);
}
console.log(stale ? `sync_counts: ${stale} spot(s) ${check ? 'stale' : 'updated'}.` : 'sync_counts: all counts current.');
