/* Shared loader for the data block in index.html, used by sync_counts.js and
   entry.js so neither has to re-implement the parsing.

   Every D entry sits on exactly one line of index.html as strict JSON plus a
   trailing comma. loadAtlas() relies on that: entry.js can then find, show,
   insert or replace one card by line without anyone reading the 2 MB file.
   verify_data.js hard-fails if a line in D stops being one JSON object, so
   the rule can't quietly break. */
'use strict';
const fs = require('fs');
const path = require('path');

const HTML_PATH = path.join(__dirname, '..', 'index.html');

function block(html, re, label) {
  const m = html.match(re);
  if (!m) throw new Error(`Could not locate ${label} in index.html`);
  return m[1];
}

function loadAtlas(htmlPath = HTML_PATH) {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const lines = html.split('\n');
  const start = lines.indexOf('const D = [');
  if (start < 0) throw new Error('Could not locate "const D = [" in index.html');
  let end = start + 1;
  while (end < lines.length && lines[end] !== '];') end++;
  const D = [], dLines = [];
  for (let i = start + 1; i < end; i++) {
    const t = lines[i].trim().replace(/,$/, '');
    if (!t) continue;
    D.push(JSON.parse(t));
    dLines.push(i);
  }
  const BRANDS = eval('[' + block(html, /const BRANDS = \[([\s\S]*?)\];/, 'BRANDS') + ']');
  const INVENTORS = eval('[' + block(html, /const INVENTORS = \[([\s\S]*?)\n\];/, 'INVENTORS') + ']');
  const FIGHTS = eval('[' + block(html, /const FIGHTS = \[([\s\S]*?)\n\];/, 'FIGHTS') + ']');
  return { html, lines, D, dLines, dStart: start, dEnd: end, BRANDS, INVENTORS, FIGHTS };
}

/* Same rule as cardRef() in index.html for numbered cards: the num, or
   num-N when several entries share it. Slug refs (num:null) come from
   build_card_pages.js --refs, which copies the page's own rule. */
function refs(D) {
  const counts = {}, seen = {};
  D.forEach(d => { if (d.num) counts[d.num] = (counts[d.num] || 0) + 1; });
  return D.map(d => {
    if (!d.num) return null;
    seen[d.num] = (seen[d.num] || 0) + 1;
    return counts[d.num] > 1 ? `${d.num}-${seen[d.num]}` : d.num;
  });
}

module.exports = { loadAtlas, refs, HTML_PATH };
