#!/usr/bin/env node
/* Verifies index.html's D/BRANDS/INVENTORS block: confirms it still parses
   as valid JS, reports the counts README's At-a-glance table needs, and
   checks two classes of gap a parse check alone can't catch, since both
   only ever look at fields that are *present*:

     - required array fields on every D entry (b[], who[])
     - every who[] value actually registered in BRANDS or INVENTORS

   These are hard failures (non-zero exit). See CLAUDE.md's 2026-09-27
   incident note for why the b[]/who[] check exists: four pre-existing
   entries shipped with no `b` field at all, which parsed fine and looked
   correct in every check that existed at the time, then crashed
   cardHTML()/passes() the moment a real page rendered one of them --
   breaking search and Rabbit Holes navigation in what looked like two
   unrelated bugs. A missing field doesn't break parsing, only rendering,
   so this script exists specifically to catch what parsing alone can't.

   Bilingual completeness (t/s/w/long still a plain string somewhere) is
   reported but does NOT fail the run -- CLAUDE.md documents "English now,
   French later" as an acceptable, deliberate interim state, not an error.

   Run standalone: `node tools/verify_data.js` from the repo root, or
   `node verify_data.js` from inside tools/ -- both resolve index.html
   relative to this file, not the working directory. */
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const htmlPath = path.join(repoRoot, 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');

function extract(re, label) {
  const m = html.match(re);
  if (!m) {
    console.error(`::error::Could not locate ${label} in index.html -- has its shape changed?`);
    process.exit(1);
  }
  return m[1];
}

let D, BRANDS, INVENTORS;
try {
  D = eval('let D=[' + extract(/const D = \[([\s\S]*?)\n\];/, 'the D array') + '\n];D');
  BRANDS = eval('[' + extract(/const BRANDS = \[([\s\S]*?)\];/, 'the BRANDS array') + ']');
  INVENTORS = eval('[' + extract(/const INVENTORS = \[([\s\S]*?)\n\];/, 'the INVENTORS array') + ']');
} catch (e) {
  console.error("::error::Parse failure -- index.html's D/BRANDS/INVENTORS block is not valid JS.");
  console.error(e.stack || e.message);
  process.exit(1);
}

const count = (pred) => D.filter(pred).length;
console.log('Total:', D.length);
console.log('active:', count(d => d.st === 'active'));
console.log('expired:', count(d => d.st === 'expired'));
console.log('pending:', count(d => d.st === 'pending'));
console.log('unknown:', count(d => d.st === 'unknown'));
console.log('litigated:', count(d => (d.b || []).includes('litigated')));
console.log('conf v:', count(d => d.conf === 'v'));
console.log('conf m:', count(d => d.conf === 'm'));
console.log('conf l:', count(d => d.conf === 'l'));
console.log('brands:', BRANDS.length);
console.log('inventors:', INVENTORS.length);

const hardFailures = [];

// Schema-integrity: required array fields.
D.forEach(d => {
  const id = d.num || (d.t && (d.t.en || d.t)) || '(untitled)';
  if (!Array.isArray(d.b)) hardFailures.push(`${id}: b is missing or not an array`);
  if (!Array.isArray(d.who)) hardFailures.push(`${id}: who is missing or not an array`);
});

// who[] registration: every value must exist in BRANDS or as an INVENTORS key.
D.forEach(d => {
  const id = d.num || (d.t && (d.t.en || d.t)) || '(untitled)';
  (d.who || []).forEach(w => {
    if (!BRANDS.includes(w) && !INVENTORS.some(i => i.key === w)) {
      hardFailures.push(`${id}: who[] value "${w}" is not registered in BRANDS or INVENTORS`);
    }
  });
});

console.log('\nschema-integrity issues:', hardFailures.length ? hardFailures : 'none');

// Bilingual completeness -- informational only, does not fail the run.
const notBilingual = [];
D.forEach(d => ['t', 's', 'w', 'long'].forEach(f => {
  if (d[f] != null && typeof d[f] !== 'object') notBilingual.push([d.num || d.t, f]);
}));
console.log('still-plain-string fields (informational, not blocking):',
  notBilingual.length ? notBilingual : 'none');

if (hardFailures.length) {
  console.error(`\n::error::${hardFailures.length} schema-integrity issue(s) found -- see list above.`);
  process.exit(1);
}
console.log('\nData checks passed.');
