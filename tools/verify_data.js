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

// No empty filter chips: every BRANDS entry and INVENTORS key must be used by at
// least one entry's who[]. A registered name nothing is tagged with renders a
// Brands/Inventors chip that returns zero results (BMC and SCOR did, because
// they were only ever named in prose, which typed search matches but the chip
// filter does not). Tag an entry or remove the registration.
BRANDS.forEach(b => {
  if (!D.some(d => (d.who || []).includes(b))) hardFailures.push(`BRANDS "${b}" is used by no entry's who[] (would render an empty filter chip)`);
});
INVENTORS.forEach(i => {
  if (!D.some(d => (d.who || []).includes(i.key))) hardFailures.push(`INVENTORS "${i.key}" is used by no entry's who[] (would render an empty filter chip)`);
});

/* Card cross-links: [[card:<ref>|text]] inside s/w/long (see CARD_LINK_RE in
   index.html). <ref> must be a real card's #p= deep-link ref, computed here the
   same way index.html's _REF map does (the patent number, or number-N when a
   number is shared; num:null entries use a title slug and are not linkable).
   Hard failure on any dead target, so a renumbered or deleted card can't leave
   a link that opens nothing. */
const refOf = new Map();
(() => {
  const counts = {}, seen = {};
  D.forEach(d => { if (d.num) counts[d.num] = (counts[d.num] || 0) + 1; });
  D.forEach(d => {
    if (!d.num) return;
    seen[d.num] = (seen[d.num] || 0) + 1;
    refOf.set(d, counts[d.num] > 1 ? `${d.num}-${seen[d.num]}` : d.num);
  });
})();
const validRefs = new Set(refOf.values());
const xrefs = [];   // {from: ref|title, to: ref}
D.forEach(d => ['s', 'w', 'long'].forEach(f => {
  const langs = d[f] && typeof d[f] === 'object' ? Object.entries(d[f]) : [];
  langs.forEach(([lang, text]) => {
    for (const m of String(text).matchAll(/\[\[card:([^|\]]+)\|([^\]]+)\]\]/g)) {
      const from = refOf.get(d) || (d.t && d.t.en);
      xrefs.push({ from, to: m[1], where: `${from}.${f}.${lang}` });
      if (!validRefs.has(m[1])) hardFailures.push(`${from}.${f}.${lang}: card link target "${m[1]}" matches no entry`);
    }
  });
}));
/* Cross-links that must exist in BOTH directions and in BOTH languages. Add a
   pair here whenever two cards are deliberately wired to each other, so a later
   edit that drops one side fails CI instead of silently orphaning the other. */
const REQUIRED_CROSSLINKS = [
  ['615003', '667348'],    // Crampon design patents D615,003 <-> D667,348
  ['9701361', '10088020'], // Spot Brand Living Link <-> Gates CenterTrack / Drop-Out
];
REQUIRED_CROSSLINKS.forEach(([a, b]) => [[a, b], [b, a]].forEach(([from, to]) => {
  ['en', 'fr'].forEach(lang => {
    if (!xrefs.some(x => x.to === to && x.where.startsWith(from + '.') && x.where.endsWith('.' + lang))) {
      hardFailures.push(`required cross-link missing: card ${from} must link to card ${to} (${lang})`);
    }
  });
}));
/* REF_ALIASES (old #p= refs kept alive after an entry's ref changed): every
   target must be a real card, and no alias may shadow a ref that is live. */
const aliasBlock = html.match(/const REF_ALIASES = (\{[\s\S]*?\n\});/);
if (!aliasBlock) hardFailures.push('REF_ALIASES not found in index.html');
else {
  const aliases = eval('(' + aliasBlock[1] + ')');
  Object.entries(aliases).forEach(([from, to]) => {
    if (!validRefs.has(to)) hardFailures.push(`REF_ALIASES "${from}" -> "${to}": target matches no entry`);
    if (validRefs.has(from)) hardFailures.push(`REF_ALIASES "${from}" is a live card ref; remove the alias`);
  });
  console.log('ref aliases:', Object.keys(aliases).length, '(all targets resolve)');
}
// External links in prose: [[link:URL|text]] must be https (anything else, or a
// malformed token, would render as a broken or unsafe link).
D.forEach(d => ['s', 'w', 'long'].forEach(f => {
  const o = d[f] && typeof d[f] === 'object' ? d[f] : {};
  Object.entries(o).forEach(([lang, text]) => {
    for (const m of String(text).matchAll(/\[\[link:([^|\]]*)\|([^\]]*)\]\]/g)) {
      if (!/^https:\/\/[^\s"<>]+$/.test(m[1]) || !m[2].trim()) {
        hardFailures.push(`${d.num || d.t.en}.${f}.${lang}: bad [[link:…]] token "${m[0]}" (needs an https URL and link text)`);
      }
    }
  });
}));
console.log('card cross-links:', xrefs.length, '(all targets resolve)');

console.log('\nschema-integrity issues:', hardFailures.length ? hardFailures : 'none');

// Bilingual completeness -- informational only, does not fail the run.
const notBilingual = [];
D.forEach(d => ['t', 's', 'w', 'long'].forEach(f => {
  if (d[f] != null && typeof d[f] !== 'object') notBilingual.push([d.num || d.t, f]);
}));
console.log('still-plain-string fields (informational, not blocking):',
  notBilingual.length ? notBilingual : 'none');

/* Patent-term check -- informational only, like the bilingual check above, and
   for the same reason: a mismatch can be a documented exception rather than an
   error, so hard-failing would just train people to ignore the run.

   Scope is deliberately narrow: single-number, non-design, PRE-1995 filings.
   That is exactly the set CLAUDE.md's "Expiration rule (exp)" section got wrong
   until 2026-10-06. The old one-line rule said flatly "filed before June 8,
   1995 -> grant + 17" and omitted the other half of 35 U.S.C. 154(c): a patent
   still in force on June 8, 1995 gets the GREATER of grant+17 and filing+20
   (MPEP 2701). Reaching for grant+17 alone understates every patent that issued
   less than three years after filing -- which was ~21 entries.

   Deliberately NOT checked, because a mismatch there is usually legitimate and
   the noise would drown the signal:
     - post-1995 filings. Continuations inherit the PARENT application's filing
       date (see CLAUDE.md), so exp != y+20 is normal and expected for them, and
       they're common enough after 1995 to make the check useless there.
     - design patents, spotted by pt:"design" OR a D-prefixed num. They sit
       outside 154(c), and a pre-1982 design term was ELECTED by the applicant
       at 3.5/7/14 years, so it cannot be derived from the grant year at all.
     - num:null era/estimate entries ("Freehub cassette hub"), where exp is an
       editorial estimate for a technology rather than one patent's real term.
     - multi-patent bundles (nums[] > 1), whose exp tracks the newest member. */
const preGattExp = d => {
  const fromGrant = d.g + 17;
  // 154(c) reaches it only if it was still alive on 1995-06-08 (or issued later).
  return (fromGrant >= 1995 || d.g >= 1995) ? Math.max(fromGrant, d.y + 20) : fromGrant;
};
const expIssues = [];
D.forEach(d => {
  if (!d.num) return;
  if (d.pt === 'design' || /^D/.test(String(d.num))) return;
  if ((d.nums || []).length > 1) return;
  if (typeof d.y !== 'number' || typeof d.g !== 'number' || typeof d.exp !== 'number') return;
  if (d.y >= 1995) return;
  const want = preGattExp(d);
  if (d.exp !== want) expIssues.push(`${d.num}: exp ${d.exp}, rule gives ${want} (y:${d.y} g:${d.g})`);
});
console.log('\npre-1995 patent-term mismatches (informational, not blocking):',
  expIssues.length ? expIssues : 'none');

if (hardFailures.length) {
  console.error(`\n::error::${hardFailures.length} schema-integrity issue(s) found -- see list above.`);
  process.exit(1);
}
console.log('\nData checks passed.');
