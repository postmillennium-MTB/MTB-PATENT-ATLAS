#!/usr/bin/env node
/* Rebuilds MATCH_DATA in match/index.html from index.html's D array.

   match/index.html (the matching game) holds a static snapshot of every D
   entry that has a drawing -- not a live link -- so it goes stale whenever a
   data session adds or edits an entry's image. Run this after one:

     node tools/regen_match_data.js            # rewrite match/index.html in place
     node tools/regen_match_data.js --check    # report drift, change nothing

   `node tools/verify_data.js` calls the same builder and reports drift, so a
   forgotten regeneration shows up there (and in CI) instead of on the live page.

   Everything but `teaser` is copied verbatim from D. `teaser` is the first
   ~200 characters of the entry's summary, cut at a word boundary: algorithmic,
   not hand-written (see the comment above MATCH_DATA in match/index.html).

   This replaces a Node snippet that used to live in a comment at the bottom of
   match/index.html. One copy of the logic, here, so the two cannot drift. */
const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const MAX = 200;

function teaser(text) {
  if (!text) return '';
  if (text.length <= MAX) return text;
  const cut = text.lastIndexOf(' ', MAX);
  return text.slice(0, cut > 40 ? cut : MAX) + '…';
}

function parseD(html) {
  const m = html.match(/const D = \[([\s\S]*?)\n\];/);
  if (!m) throw new Error("could not locate the D array in index.html");
  return eval('let D=[' + m[1] + '\n];D');
}

/* The MATCH_DATA array for a given index.html source string. */
function buildMatchData(html) {
  const D = parseD(html);
  return D.filter(d => d.img || (d.imgs && d.imgs.length)).map(d => {
    const imgSrc = d.img || d.imgs[0].src;
    const imgAltObj = d.img ? d.imgAlt : d.imgs[0].alt;
    // Entries with no s fall back to w (one case: Cool Tool, US 4,967,435).
    const descSrc = d.s || d.w;
    return {
      num: d.num, cat: d.cat,
      title: { en: d.t.en, fr: d.t.fr },
      assignee: d.a,
      img: '../pictures/' + path.basename(decodeURIComponent(imgSrc)),
      alt: { en: (imgAltObj && imgAltObj.en) || d.t.en,
             fr: (imgAltObj && imgAltObj.fr) || d.t.fr },
      teaser: { en: teaser(descSrc.en), fr: teaser(descSrc.fr) },
      full: { en: descSrc.en, fr: descSrc.fr },
    };
  });
}

/* Where MATCH_DATA sits in match/index.html: [start, end) of the declaration. */
function locateDeclaration(matchHtml) {
  const start = matchHtml.indexOf('const MATCH_DATA = ');
  if (start < 0) throw new Error('could not locate MATCH_DATA in match/index.html');
  const end = matchHtml.indexOf('];', start) + 2;
  return [start, end];
}

function currentMatchData(matchHtml) {
  const [start, end] = locateDeclaration(matchHtml);
  return eval('(' + matchHtml.slice(start + 'const MATCH_DATA = '.length, end - 1) + ')');
}

module.exports = { buildMatchData, currentMatchData, locateDeclaration };

if (require.main === module) {
  const htmlPath = path.join(repoRoot, 'index.html');
  const matchPath = path.join(repoRoot, 'match', 'index.html');
  const out = buildMatchData(fs.readFileSync(htmlPath, 'utf8'));
  const matchHtml = fs.readFileSync(matchPath, 'utf8');
  const [start, end] = locateDeclaration(matchHtml);
  const next = matchHtml.slice(0, start) + 'const MATCH_DATA = ' + JSON.stringify(out) + ';' + matchHtml.slice(end);
  if (process.argv.includes('--check')) {
    if (next === matchHtml) { console.log('MATCH_DATA is current (' + out.length + ' entries).'); }
    else { console.error('MATCH_DATA is out of date. Run: node tools/regen_match_data.js'); process.exit(1); }
  } else {
    fs.writeFileSync(matchPath, next);
    console.log('MATCH_DATA written: ' + out.length + ' entries.');
    console.log('If the entry count changed, update the "N entries" figure in the');
    console.log('comment above MATCH_DATA in match/index.html.');
  }
}
