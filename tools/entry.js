#!/usr/bin/env node
/* Work on one card without opening index.html (2 MB, ~550k tokens).
   Every D entry is one line of strict JSON, so cards can be found, shown,
   added and replaced by line.

     node tools/entry.js find <text>...      duplicate check: matches num, nums, title, assignee, who
     node tools/entry.js show <ref>          one card as readable JSON (ref = number, num-N, or line:<n>)
     node tools/entry.js near <ref> [n]      the cards just before/after it (one line each), to pick placement
     node tools/entry.js pics <num>...       drawings in pictures/ for these numbers (and whether a thumbnail exists)
     node tools/entry.js template            a blank card to fill in
     node tools/entry.js add <file.json> --after <ref>
                                             insert the card(s) in the file (one object or an array) after <ref>
     node tools/entry.js replace <ref> <file.json>
                                             swap one card for the object in the file

   add/replace check the new card's shape first (required fields, {en,fr}
   text, who[] registered, num formatting) and refuse to write if it fails.
   They then print the next steps: sync_counts.js, verify_data.js, thumbs. */
'use strict';
const fs = require('fs');
const path = require('path');
const { loadAtlas, refs, HTML_PATH } = require('./atlas_data');

const ROOT = path.join(__dirname, '..');
const [cmd, ...args] = process.argv.slice(2);
const A = loadAtlas();
const REFS = refs(A.D);

const oneLine = (d, i) =>
  `${String(A.dLines[i] + 1).padStart(5)}  ${(REFS[i] || '(no num)').padEnd(14)} ${d.cat.padEnd(9)} ${d.y}  ${(d.t && d.t.en) || d.t}`;

function locate(ref) {
  if (!ref) die('give a ref: a patent number, num-N, or line:<n>');
  if (ref.startsWith('line:')) {
    const k = A.dLines.indexOf(Number(ref.slice(5)) - 1);
    if (k < 0) die(`no card on ${ref}`);
    return k;
  }
  const clean = ref.replace(/^US/i, '').replace(/[ ,]/g, '');
  let k = REFS.indexOf(clean);
  if (k < 0) k = A.D.findIndex(d => (d.nums || []).includes(clean));
  if (k < 0) die(`no card with ref ${ref} (try: node tools/entry.js find ${ref})`);
  return k;
}
function die(msg) { console.error(msg); process.exit(1); }
const norm = s => String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '');

function validate(d) {
  const p = [];
  const need = ['y', 'g', 't', 'a', 'num', 'cat', 'st', 'exp', 'b', 'who', 'conf', 's', 'w'];
  need.forEach(k => { if (!(k in d)) p.push(`missing ${k}`); });
  ['t', 's', 'w', 'hook', 'clever', 'imgAlt', 'long'].forEach(k => {
    if (k in d && !(d[k] && typeof d[k] === 'object' && d[k].en && d[k].fr)) p.push(`${k} must be {en, fr}, both filled`);
  });
  if (!['susp', 'fork', 'drive', 'wheel', 'comp', 'emtb', 'frame', 'transport', 'tech'].includes(d.cat)) p.push(`unknown cat ${d.cat}`);
  if (!['active', 'expired', 'pending', 'unknown'].includes(d.st)) p.push(`unknown st ${d.st}`);
  if (!['v', 'm', 'l'].includes(d.conf)) p.push(`unknown conf ${d.conf}`);
  if (!Array.isArray(d.b)) p.push('b must be an array');
  if (!Array.isArray(d.who)) p.push('who must be an array');
  (d.who || []).forEach(w => {
    if (!A.BRANDS.includes(w) && !A.INVENTORS.some(i => i.key === w)) p.push(`who "${w}" is not in BRANDS or INVENTORS: register it first`);
  });
  if (d.num != null && /[ ,]|^US/.test(d.num)) p.push(`num "${d.num}": plain digits, no "US", spaces or commas`);
  if (d.pt === 'design' && /^D/.test(d.num || '')) p.push('design num holds bare digits; the page adds the D');
  if (d.img && !d.imgAlt) p.push('img needs imgAlt');
  (d.imgs || []).forEach((x, i) => ['alt', 'caption'].forEach(f => {
    if (!(x[f] && x[f].en && x[f].fr)) p.push(`imgs[${i}].${f} must be {en, fr}`);
  }));
  [d.img, ...(d.imgs || []).map(x => x.src)].filter(Boolean).forEach(src => {
    if (!fs.existsSync(path.join(ROOT, src))) p.push(`image not found: ${src}`);
  });
  if (d.num && REFS.includes(d.num)) p.push(`num ${d.num} is already on a card (${d.num}); a second card is allowed but check it is not a duplicate`);
  return p;
}

function writeLines(lines) {
  fs.writeFileSync(HTML_PATH, lines.join('\n'));
}
function readCards(file) {
  if (!file) die('give a .json file');
  const v = JSON.parse(fs.readFileSync(file, 'utf8'));
  return Array.isArray(v) ? v : [v];
}
function checkOrDie(cards, allowDupNum) {
  let bad = 0;
  cards.forEach(d => {
    const probs = validate(d).filter(x => !(allowDupNum && x.startsWith('num ')));
    if (probs.length) { bad++; console.error(`${(d.t && d.t.en) || '(untitled)'}:\n  - ${probs.join('\n  - ')}`); }
  });
  const hard = cards.some(d => validate(d).some(x => !x.startsWith('num ')));
  if (hard) die('nothing written.');
  if (bad) console.error('(warnings only; written anyway)');
}
const NEXT = `next: node tools/sync_counts.js && node tools/verify_data.js
      new drawings: python3 tools/make_thumbs.py pictures/<file>
      before the PR: node tools/smoke_test.js; add a README "Recent updates" bullet and a WHATS_NEW line (required when cards are added)`;

const TEMPLATE = {
  y: 2020, g: 2022,
  t: { en: 'Brand Product name (US 1,234,567)', fr: 'Brand nom du produit (US 1 234 567)' },
  a: 'Assignee / inventor', num: '1234567', cat: 'susp', st: 'active', exp: 2040,
  b: [], who: ['Brand'], conf: 'v',
  hook: { en: 'One-line opener, EN <=120 chars', fr: 'FR <=140' },
  clever: { en: 'How the mechanism works, one sentence, EN <=200', fr: 'FR <=240' },
  s: { en: 'What it covers, filing/grant history, the mechanism.', fr: '…' },
  w: { en: 'Why it matters.', fr: '…' },
  imgs: [{
    src: 'pictures/US1234567B2.png',
    alt: { en: 'Fig. 1 of US 1,234,567: what the drawing shows, with its reference numerals', fr: 'Fig. 1 de l\'US 1 234 567 : …' },
    caption: { en: 'Fig. 1 (US 1,234,567) — short label', fr: 'Fig. 1 (US 1 234 567) — légende courte' },
  }],
};

switch (cmd) {
  case 'find': {
    const qs = args.map(norm).filter(Boolean);
    if (!qs.length) die('usage: find <text>...');
    let hits = 0;
    A.D.forEach((d, i) => {
      const hay = norm([d.num, ...(d.nums || []), d.t && d.t.en, d.t && d.t.fr, d.a, ...(d.who || [])].join(' '));
      if (qs.some(q => hay.includes(q))) { hits++; console.log(oneLine(d, i)); }
    });
    console.log(hits ? `${hits} match(es)` : 'no match');
    break;
  }
  case 'show': console.log(JSON.stringify(A.D[locate(args[0])], null, 2)); break;
  case 'near': {
    const k = locate(args[0]), n = Number(args[1] || 4);
    for (let i = Math.max(0, k - n); i <= Math.min(A.D.length - 1, k + n); i++) console.log((i === k ? '>' : ' ') + oneLine(A.D[i], i));
    break;
  }
  case 'pics': {
    const files = fs.readdirSync(path.join(ROOT, 'pictures'));
    args.forEach(num => {
      const key = norm(num.replace(/^US/i, ''));
      /* A family card answers for all its numbers: drawings Jon uploads under
         any member's number belong to the same card. */
      const fam = A.D.find(d => norm(String(d.num || '')) === key || (d.nums || []).some(n => norm(n) === key));
      const keys = [...new Set([key, ...(fam ? [fam.num, ...(fam.nums || [])].filter(Boolean).map(n => norm(String(n).replace(/^US/i, ''))) : [])])];
      const m = files.filter(f => keys.some(k => norm(f).includes(k)));
      console.log(`${num}: ${m.length ? '' : 'none'}${fam && keys.length > 1 ? `  (family card: ${keys.join(', ')})` : ''}`);
      m.forEach(f => {
        const thumb = fs.existsSync(path.join(ROOT, 'pictures', 'thumbs', f.replace(/\.[^.]+$/, '.webp')));
        const used = A.D.some(d => d.img === `pictures/${f}` || (d.imgs || []).some(x => x.src === `pictures/${f}`));
        console.log(`  pictures/${f}${used ? '  (used)' : '  (not on any card)'}${thumb ? '  thumb ok' : ''}`);
      });
    });
    break;
  }
  case 'template': console.log(JSON.stringify(TEMPLATE, null, 2)); break;
  case 'add': {
    const ai = args.indexOf('--after');
    if (ai < 0) die('usage: add <file.json> --after <ref>');
    const k = locate(args[ai + 1]);
    const cards = readCards(args.find((x, i) => i !== ai && i !== ai + 1));
    checkOrDie(cards, false);
    const lines = A.lines.slice();
    lines.splice(A.dLines[k] + 1, 0, ...cards.map(d => '  ' + JSON.stringify(d) + ','));
    writeLines(lines);
    console.log(`added ${cards.length} card(s) after line ${A.dLines[k] + 1}. Atlas now has ${A.D.length + cards.length} cards.\n${NEXT}`);
    break;
  }
  case 'replace': {
    const k = locate(args[0]);
    const cards = readCards(args[1]);
    if (cards.length !== 1) die('replace takes exactly one object');
    checkOrDie(cards, true);
    const old = A.D[k];
    if (old.num !== cards[0].num || (old.t && old.t.en) !== (cards[0].t && cards[0].t.en))
      console.log('note: num or English title changed, so the card\'s link may change; add a REF_ALIASES entry if so.');
    const lines = A.lines.slice();
    lines[A.dLines[k]] = '  ' + JSON.stringify(cards[0]) + ',';
    writeLines(lines);
    console.log(`replaced line ${A.dLines[k] + 1}.\n${NEXT}`);
    break;
  }
  default:
    console.log(fs.readFileSync(__filename, 'utf8').match(/\/\*([\s\S]*?)\*\//)[1]);
}
