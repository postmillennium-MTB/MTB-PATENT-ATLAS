#!/usr/bin/env node
/* Estimated US patent expiry, following docs/reference.md's expiration rule, so no
   session has to redo the GATT / design-term arithmetic by hand.

     node tools/patent_term.js --filed 1994-03-02 --granted 1996-04-23
     node tools/patent_term.js --filed 2014-07-28 --granted 2016-08-23 --pta 120
     node tools/patent_term.js --filed 2016-05-20 --granted 2019-01-01 --design
     node tools/patent_term.js --filed 2023-03-31            # pending: filed + 20

   --filed is the EARLIEST non-provisional US filing in the priority chain
   (a continuation inherits its parent's date; a provisional alone doesn't
   count). Years alone (--filed 1994) work too; the answer is then +/-1.
   Prints the expiry date and the `exp` year to store. A terminal disclaimer
   or a fee lapse can end a patent sooner; neither can be computed, so check
   the record's legal status ("Expired - Fee Related") and use that instead. */
'use strict';

const GATT = new Date('1995-06-08');
const DESIGN_14 = new Date('1982-10-01');
const DESIGN_15 = new Date('2015-05-13');

function toDate(v) {
  if (v == null || v === '') return null;
  const s = String(v);
  return new Date(/^\d{4}$/.test(s) ? `${s}-07-01` : s);
}
const addYears = (d, y) => { const r = new Date(d); r.setUTCFullYear(r.getUTCFullYear() + y); return r; };
const addDays = (d, n) => new Date(d.getTime() + n * 86400000);
const iso = d => d.toISOString().slice(0, 10);

/* Returns {exp: Date|null, rule: string}. */
function patentTerm({ filed, granted, design = false, pta = 0 }) {
  const f = toDate(filed), g = toDate(granted);
  if (!f) return { exp: null, rule: 'no filing date' };
  if (design) {
    if (!g) return { exp: null, rule: 'design application: no term until granted' };
    if (f >= DESIGN_15) return { exp: addYears(g, 15), rule: 'design filed on/after 2015-05-13: grant + 15' };
    if (f >= DESIGN_14) return { exp: addYears(g, 14), rule: 'design filed 1982-10-01 to 2015-05-12: grant + 14' };
    return { exp: null, rule: 'pre-1982 design: term was an election (3.5, 7 or 14 years); read it off the record' };
  }
  if (f >= GATT) {
    const e = addDays(addYears(f, 20), pta || 0);
    return { exp: e, rule: `utility filed on/after 1995-06-08: filed + 20${pta ? ` + ${pta} days PTA` : ''}${g ? '' : ' (pending: if granted)'}` };
  }
  if (!g) return { exp: addYears(f, 20), rule: 'pre-1995 filing, no grant: filed + 20 (estimate)' };
  const g17 = addYears(g, 17), f20 = addYears(f, 20);
  if (g17 < GATT) return { exp: g17, rule: 'utility expired before 1995-06-08: grant + 17' };
  return g17 >= f20
    ? { exp: g17, rule: 'utility in force on 1995-06-08: greater of grant + 17 and filed + 20 (grant + 17)' }
    : { exp: f20, rule: 'utility in force on 1995-06-08: greater of grant + 17 and filed + 20 (filed + 20)' };
}

module.exports = { patentTerm };

if (require.main === module) {
  const a = process.argv.slice(2);
  const opt = k => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : undefined; };
  if (!opt('--filed')) {
    console.log('usage: node tools/patent_term.js --filed YYYY[-MM-DD] [--granted YYYY[-MM-DD]] [--pta DAYS] [--design]');
    process.exit(2);
  }
  const r = patentTerm({ filed: opt('--filed'), granted: opt('--granted'), design: a.includes('--design'), pta: Number(opt('--pta') || 0) });
  console.log(r.exp ? `exp: ${r.exp.getUTCFullYear()}   (expires ${iso(r.exp)}; ${r.rule})` : `exp: null   (${r.rule})`);
}
