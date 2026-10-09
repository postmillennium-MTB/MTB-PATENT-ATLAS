#!/usr/bin/env node
/* Prints, as JSON, the first drawing of every D entry that has one -- the
   image the card thumbnail is made from (index.html's thumbSrc() makes the
   same choice: imgs[0].src when imgs exists, otherwise img).

   Used by make_thumbs.py so the "which images need a thumbnail" rule lives
   in one place and the Python side never has to parse index.html itself.
   Parses D the same way verify_data.js does.

   Output: ["pictures/US5509679A.png", "pictures/Priority%20Outdoor%20Products%20LLC.png", ...]
   -- paths exactly as written in the entry, still percent-encoded, deduplicated,
   in D order. */
const fs = require('fs');
const path = require('path');

const html = fs.readFileSync(path.resolve(__dirname, '..', 'index.html'), 'utf8');
const m = html.match(/const D = \[([\s\S]*?)\n\];/);
if (!m) {
  console.error("::error::Could not locate the D array in index.html -- has its shape changed?");
  process.exit(1);
}
const D = eval('let D=[' + m[1] + '\n];D');
const firsts = D.map(d => (d.imgs && d.imgs.length ? d.imgs[0].src : d.img)).filter(Boolean);
console.log(JSON.stringify([...new Set(firsts)]));
