#!/usr/bin/env node
/* Browser smoke test for index.html -- exercises real page behavior, not
   just data shape. This is what catches a render-time crash that
   verify_data.js cannot, since that script only ever inspects the D array
   and never runs the code that reads it. See CLAUDE.md's 2026-09-27
   incident note: a missing b[] field parsed fine and looked correct in
   every Node-side check, but crashed cardHTML()/passes() the moment a
   real page actually rendered an affected entry -- breaking search and
   Rabbit Holes navigation in what looked like two unrelated bugs.

   Rabbit Holes is checked BEFORE search, deliberately: typing a query
   navigates off the default home/Atlas tab, and .rh-card stops existing
   in the DOM. An earlier draft of this exact script shipped with that
   ordering backwards and silently "passed" by timing out on a selector
   that no longer existed -- fixed here, called out so it isn't
   reintroduced by a future edit.

   Needs Playwright installed (see tools/package.json) and a Chromium
   build available -- either the one this repo's dev sandbox has
   pre-installed at /opt/pw-browsers/chromium, or Playwright's own
   bundled browser (`npx playwright install --with-deps chromium`), which
   is what CI installs since that fixed sandbox path won't exist there. */
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const LOCAL_CHROMIUM = '/opt/pw-browsers/chromium';
const launchOpts = fs.existsSync(LOCAL_CHROMIUM) ? { executablePath: LOCAL_CHROMIUM } : {};

// Category-word terms: broad, common, high collision risk with ANY
// pre-existing entry regardless of what a recent change touched -- this
// is what actually found the 2026-09-27 incident, not a term specific to
// whatever was just added.
const CATEGORY_SEARCH_TERMS = ['wheel', 'frame', 'fork', 'drive', 'comp', 'emtb', 'susp', 'transport', 'tech'];
const MIN_EXPECTED_CARDS = 1; // any of these terms returning 0 is itself suspicious

(async () => {
  const browser = await chromium.launch(launchOpts);
  const page = await browser.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));

  const filePath = 'file://' + path.resolve(__dirname, '..', 'index.html');
  await page.goto(filePath);
  await page.waitForTimeout(600);

  let failed = false;

  // Rabbit Holes -- clicking one always renders the FULL unfiltered list
  // (see jumpToCard() in index.html), so this alone touches every entry
  // in D on a single click, making it a stronger whole-file check than
  // any individual search term below.
  errors.length = 0;
  await page.click('.rh-card >> nth=0');
  await page.waitForTimeout(400);
  const rhCards = await page.locator('.card').count();
  console.log(`rabbit hole click: ${rhCards} cards rendered, errors: ${JSON.stringify(errors)}`);
  if (errors.length || rhCards < 1) {
    failed = true;
    console.error('::error::Rabbit Holes click crashed or rendered nothing.');
  }

  for (const q of CATEGORY_SEARCH_TERMS) {
    errors.length = 0;
    await page.fill('#searchInput', '');
    await page.fill('#searchInput', q);
    await page.waitForTimeout(500);
    const cards = await page.locator('.card').count();
    console.log(`search "${q}": ${cards} cards, errors: ${JSON.stringify(errors)}`);
    if (errors.length || cards < MIN_EXPECTED_CARDS) {
      failed = true;
      console.error(`::error::search "${q}" crashed or returned suspiciously few cards.`);
    }
  }

  /* Every Brands / Inventors chip must return at least one card. A registered
     name that no entry's who[] uses renders a chip that filters to nothing
     (BMC and SCOR did, 2026-10-07). verify_data.js catches it from the data;
     this checks the rendered behavior. */
  errors.length = 0;
  await page.fill('#searchInput', '');
  await page.waitForTimeout(300);
  const emptyChips = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('.chip[data-fset="brand"], .chip[data-fset="inv"]').forEach(b => {
      b.click();
      if (!document.querySelectorAll('.card').length) out.push(b.dataset.fset + ':' + b.dataset.fkey);
      b.click();
    });
    return out;
  });
  console.log(`brand/inventor chips returning zero cards: ${JSON.stringify(emptyChips)}, errors: ${JSON.stringify(errors)}`);
  if (emptyChips.length || errors.length) {
    failed = true;
    console.error('::error::Filter chips that return no results: ' + emptyChips.join(', '));
  }

  /* Card cross-links ([[card:ref|text]] -> a.card-xref): from each end of the
     required pairs, open the card, click the link, and confirm the target card
     opens. Keep in step with REQUIRED_CROSSLINKS in verify_data.js. */
  const XLINK_PAIRS = [['615003', '667348'], ['667348', '615003'], ['9701361', '10088020'], ['10088020', '9701361']];
  for (const [from, to] of XLINK_PAIRS) {
    errors.length = 0;
    await page.evaluate(ref => jumpToCard(ref), from);
    await page.waitForTimeout(500);
    const link = page.locator(`#p-${from} a.card-xref[data-xref="${to}"]`).first();
    const found = await link.count();
    if (found) await link.click();
    await page.waitForTimeout(500);
    const opened = await page.locator(`#p-${to}.open`).count();
    console.log(`cross-link ${from} -> ${to}: link found ${found}, target opened ${opened}, errors: ${JSON.stringify(errors)}`);
    if (!found || !opened || errors.length) {
      failed = true;
      console.error(`::error::Cross-link ${from} -> ${to} is missing or did not open its target.`);
    }
  }

  /* Old slug deep links must still open their card (REF_ALIASES in index.html). */
  for (const [oldRef, newRef] of [['priority-stillpoint-suspension-system', '20250256807'], ['hayes-hydraulic-disc-brake', '5390771'], ['isospeed-decoupler', '10086899']]) {
    errors.length = 0;
    await page.evaluate(ref => jumpToCard(ref), oldRef);
    await page.waitForTimeout(500);
    const opened = await page.locator(`#p-${newRef}.open`).count();
    console.log(`alias ${oldRef} -> ${newRef}: opened ${opened}, errors: ${JSON.stringify(errors)}`);
    if (!opened || errors.length) { failed = true; console.error(`::error::Old deep link #p=${oldRef} no longer opens its card.`); }
  }

  await browser.close();
  if (failed) {
    console.error('\n::error::Browser smoke test FAILED.');
    process.exit(1);
  }
  console.log('\nBrowser smoke test passed.');
})().catch(e => {
  console.error('::error::Smoke test script itself threw:', e);
  process.exit(1);
});
