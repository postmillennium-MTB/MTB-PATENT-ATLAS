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

  /* [[link:https://…|text]] in prose renders as a new-tab anchor (Boost 148 card). */
  errors.length = 0;
  await page.evaluate(() => jumpToCard('boost-148-spacing-the-un-patent'));
  await page.waitForTimeout(500);
  const ext = await page.locator('#p-boost-148-spacing-the-un-patent a.card-xref[target="_blank"][href^="https://www.pinkbike.com/"]').count();
  console.log(`external prose link on Boost 148 card: ${ext}, errors: ${JSON.stringify(errors)}`);
  if (!ext || errors.length) { failed = true; console.error('::error::External [[link:]] did not render on the Boost 148 card.'); }

  /* Old slug deep links must still open their card (REF_ALIASES in index.html). */
  for (const [oldRef, newRef] of [['priority-stillpoint-suspension-system', '20250256807'], ['hayes-hydraulic-disc-brake', '5390771'], ['isospeed-decoupler', '10086899']]) {
    errors.length = 0;
    await page.evaluate(ref => jumpToCard(ref), oldRef);
    await page.waitForTimeout(500);
    const opened = await page.locator(`#p-${newRef}.open`).count();
    console.log(`alias ${oldRef} -> ${newRef}: opened ${opened}, errors: ${JSON.stringify(errors)}`);
    if (!opened || errors.length) { failed = true; console.error(`::error::Old deep link #p=${oldRef} no longer opens its card.`); }
  }

  /* Card views (grid / plate / tint / text -- VIEW_MODES in index.html).
     Each is a different layout of the same cards, so what can break is: the
     default for the viewport, switching rendering nothing or throwing, the text
     view quietly loading images, a thumbnail path that does not resolve, the
     grid's open-card reordering losing a card, the saved choice, and the
     toggle's French label. */
  const VIEW_KEYS = ['grid', 'plate', 'tint', 'text'];
  const showAll = () => page.evaluate(() => { activeTab = 'all'; renderTabs(); render(); });

  // Defaults by width, from a clean slate (no saved choice).
  for (const [w, h, want] of [[1280, 800, 'grid'], [390, 844, 'plate']]) {
    const ctx = await browser.newContext({ viewport: { width: w, height: h } });
    const p = await ctx.newPage();
    const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    await p.goto(filePath + '#tab=all');
    await p.waitForTimeout(600);
    const got = await p.getAttribute('#timeline', 'data-view');
    console.log(`default view at ${w}px: ${got} (want ${want}), errors: ${JSON.stringify(errs)}`);
    if (got !== want || errs.length) { failed = true; console.error(`::error::Default card view at ${w}px is ${got}, expected ${want}.`); }
    await ctx.close();
  }

  // Every view renders every card, without errors.
  await showAll();
  const expectedCards = await page.evaluate(() => D.length);
  for (const v of VIEW_KEYS) {
    errors.length = 0;
    await page.click(`.view-btn[data-view="${v}"]`);
    await page.waitForTimeout(400);
    const attr = await page.getAttribute('#timeline', 'data-view');
    const cards = await page.locator('#timeline .card').count();
    const thumbs = await page.locator('#timeline .thumb').count();
    const wantThumbs = v === 'text' ? 0 : expectedCards;
    console.log(`view ${v}: data-view=${attr}, ${cards} cards, ${thumbs} thumbnails, errors: ${JSON.stringify(errors)}`);
    if (attr !== v || cards !== expectedCards || thumbs !== wantThumbs || errors.length) {
      failed = true;
      console.error(`::error::Card view "${v}" rendered ${cards}/${expectedCards} cards and ${thumbs} thumbnails (want ${wantThumbs}) or threw.`);
    }
  }

  // Thumbnail files: every card's first-drawing thumbnail must load as itself,
  // not through the full-size fallback. (A fallback is correct behaviour for a
  // thumbnail not generated yet, but CI should say so: run tools/make_thumbs.py.)
  await page.click('.view-btn[data-view="grid"]');
  await page.waitForTimeout(300);
  const thumbReport = await page.evaluate(async () => {
    const imgs = [...document.querySelectorAll('#timeline .thumb img[data-full]')];
    imgs.forEach(i => { i.loading = 'eager'; });
    await Promise.all(imgs.map(i => i.complete ? 0 : new Promise(r => { i.addEventListener('load', r); i.addEventListener('error', r); setTimeout(r, 8000); })));
    await new Promise(r => setTimeout(r, 400));
    const bad = imgs.filter(i => !(i.complete && i.naturalWidth > 0 && /\/pictures\/thumbs\//.test(decodeURIComponent(i.currentSrc || i.src)))).map(i => i.dataset.full);
    return { total: imgs.length, bad };
  });
  console.log(`thumbnails: ${thumbReport.total - thumbReport.bad.length}/${thumbReport.total} load from pictures/thumbs/${thumbReport.bad.length ? ', not: ' + thumbReport.bad.slice(0, 8).join(', ') : ''}`);
  if (!thumbReport.total || thumbReport.bad.length) {
    failed = true;
    console.error('::error::Some card thumbnails are missing or broken. Run: python3 tools/make_thumbs.py');
  }

  // Grid: opening a card promotes it to the front of its row; closing puts it back.
  errors.length = 0;
  const order = () => page.evaluate(() => [...document.querySelectorAll('#timeline .tl > .card')].map(c => c.id).join(','));
  const before = await order();
  const target = await page.evaluate(() => { const c = document.querySelectorAll('#timeline .tl > .card')[6]; return c.id; });
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.click(`#${target} .chead`);
  await page.waitForTimeout(300);
  const openState = await page.evaluate(id => {
    const list = [...document.querySelectorAll('#timeline .tl > .card')];
    const c = document.getElementById(id);
    const i = list.indexOf(c);
    return { open: c.classList.contains('open'), rowMateBefore: list.slice(0, i).some(x => !x.classList.contains('open') && x.offsetTop === c.offsetTop), same: list.length };
  }, target);
  await page.click(`#${target} .chead`);
  await page.waitForTimeout(300);
  const after = await order();
  console.log(`grid open/close: open ${openState.open}, tile left of it on its row ${openState.rowMateBefore}, order restored ${before === after}, errors: ${JSON.stringify(errors)}`);
  if (!openState.open || openState.rowMateBefore || before !== after || errors.length) {
    failed = true;
    console.error('::error::Grid view open/close left a hole, lost a card or changed the order.');
  }

  // The choice is remembered, and the toggle is labelled in French.
  await page.click('.view-btn[data-view="tint"]');
  await page.waitForTimeout(300);
  const saved = await page.evaluate(() => localStorage.getItem('pmr-patent-atlas-view'));
  await page.reload();
  await page.waitForTimeout(600);
  const restored = await page.getAttribute('#timeline', 'data-view');
  await page.click('.langbtn[data-lang="fr"]');
  await page.waitForTimeout(300);
  const frTip = await page.getAttribute('.view-btn[data-view="grid"]', 'title');
  await page.click('.langbtn[data-lang="en"]');
  console.log(`view saved "${saved}", restored "${restored}", French tooltip: ${frTip}`);
  if (saved !== 'tint' || restored !== 'tint' || !/Grille/.test(frTip || '')) {
    failed = true;
    console.error('::error::The chosen card view is not remembered, or the toggle is not translated.');
  }
  await page.evaluate(() => { try { localStorage.removeItem('pmr-patent-atlas-view'); } catch (e) {} });

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
