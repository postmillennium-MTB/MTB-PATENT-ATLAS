# tools/

Repo tooling. Nothing here is loaded by `index.html` at runtime — the atlas is
still one self-contained file with no build step, and deleting this whole
directory would not change what a reader sees.

## `fetch_patent_figure.py` — patent drawings, semi-automated

Replaces the mechanical half of adding a drawing: find the PDF, work out which
pages are drawing sheets, crop the margin and the `U.S. Patent / Sheet n of m`
header, downscale, and name the file the way `pictures/` expects.

It deliberately stops short of the half that needs judgement. It does not pick
which figure goes on the card, does not write `imgAlt`, and never touches
`index.html`. It writes candidates to an output directory and a report, and a
person finishes the job.

### The easy way: from the GitHub web UI

**Actions → Fetch patent figure → Run workflow.** Type one or more patent
numbers, click Run. A few minutes later it opens a pull request with the
candidate images and the report. Review, keep the one you want, merge.

No local setup, nothing to install, and it works from a phone.

**Two prerequisites:**

1. GitHub only shows a `workflow_dispatch` workflow once the file is on the
   **default branch**.
2. To have it open the PR for you, tick **Settings → Actions → General →
   Workflow permissions → "Allow GitHub Actions to create and approve pull
   requests."** Without it the run logs `GitHub Actions is not permitted to
   create or approve pull requests` — the candidates are still produced and
   still reachable (see below), it just cannot open the PR itself.

**If the PR does not appear**, nothing is lost. Every run uploads the
candidates to its **Artifacts** section, which needs no permissions at all, and
the branch `patent-figures/<run id>` is pushed before the PR is attempted — the
run log prints a one-click compare link for it.

**If the automatic lookup fails**, the run log says which URLs it tried. Open
the patent on Google Patents, copy the PDF link under the title, and put it in
the optional **pdf_url** box with a single patent number. That skips both
lookups and still does all the cropping, sizing and naming — which is the part
that actually takes time by hand.

### The other way: on a computer

```bash
pip install Pillow
sudo apt-get install -y poppler-utils     # macOS: brew install poppler

python3 tools/fetch_patent_figure.py US12570369B1 US11866114B2
python3 tools/fetch_patent_figure.py 4733881 --out /tmp/figs --candidates 6
python3 tools/fetch_patent_figure.py US12570369B1 --url <pdf link>  # lookup blocked
python3 tools/fetch_patent_figure.py US9102197B2 --pdf saved.pdf   # already have the PDF
```

Those last two matter more than they look. Downloading a PDF is the one step
that is easy by hand and hard to automate reliably; cropping, sizing and naming
is the reverse. `--url` and `--pdf` let you do the easy half yourself and still
skip the tedious half.

Accepts `US12570369B1`, `12570369`, `D1140680`, `RE45684`.

### After it runs

1. Look at the candidates. Pick the figure that shows the mechanism — the first
   drawing sheet is frequently a generic whole-bike view, and the useful one is
   further in. The DW-Link entry uses the abstract kinematic diagram from sheet
   1 of 56 precisely because the geometry is the point.
2. Rename to `US<number><kind>.png`, move into `pictures/`.
3. Read `<patent>.report.txt`. It holds the PDF's own front page — the title,
   inventor, assignee, application number and dates. **Check the atlas entry
   against it.** This is the primary source that decides the entry's `conf`
   tier, and it is how a wrong entry gets caught: US 4,733,881 sat at `conf:"v"`
   for a long time describing the wrong invention and the wrong assignee, and
   reading the drawing sheet is what exposed it.
4. Add `img` and bilingual `imgAlt` to the entry.
5. Delete the candidates you did not use.

### Self-test

```bash
python3 tools/test_fetch_patent_figure.py
```

No network, no dependencies. It pins the page-classification rule against the
real measured page-length profiles of three patents, plus number parsing. The
workflow runs it before every fetch. The fixtures are measurements, not
inventions — if a run turns up a fourth document shape, add its real numbers
rather than tuning the rule until the output looks plausible.

### Known limits

- **Figure choice is not automatable in any honest way.** Which drawing explains
  a mechanism to a reader is an editorial call.
- **Alt text is not automatable either.** It has to name the real reference
  numerals in the figure actually chosen, in English and French.
- **Google Patents is not really a fallback, it is the path.** Every live run
  so far -- Forcite, GoPro, the Park Tool clamp, the Trek DRCV shock below --
  went through it. The USPTO print endpoint has returned 403 on every attempt
  from a GitHub-hosted runner. Given that, the exact kind code (`B1` vs `B2`
  vs `A1`...) is load-bearing, and it's exactly the detail a news article or
  a forum post never states. Getting it wrong doesn't 403, it 404s -- a
  different failure, and one the tool now recovers from automatically: on a
  404 (not a 403 -- that means genuinely blocked, and retrying other kind
  codes would fail identically) it retries the same digits under B1, B2, A1,
  A2, B, A in turn. US 6,203,042, guessed at a bare `A` because that was the
  only kind code known, is the case that found this: the real code is B1,
  and it now resolves without a second run. Locked in as a mocked test
  (`test_fetch_patent_figure.py`) that replays exactly this sequence, since
  the fallback can't be tested against the real network from most sandboxes.
- **The fetch needs open egress, and is the least proven part.** Both automatic
  sources (`image-ppubs.uspto.gov` and `patents.google.com`) are blocked by the
  egress proxy in the Claude Code sandbox, so the download path has never been
  run against a live patent — it is written but unverified, unlike the crop and
  page-classification stages, which were tested. Two specific things that could
  still bite on a GitHub runner: the USPTO print endpoint could want headers or
  a session this does not send, and Google may refuse a scrape from a datacenter
  IP even though it serves a home connection fine. `--url` / `pdf_url` exists
  precisely so neither is a dead end. Whatever happens, the script fails loudly
  and writes nothing; it never emits a placeholder.
- **Figure selection is density-based, and patent PDFs come in three shapes.**
  Measured on real documents:
  - *Modern grant with a text layer* — bibliographic page 1, then drawing
    sheets, then specification columns. Cleanly separated; this is the easy case.
  - *Pure image scan* — every page extracts zero characters, so density says
    nothing. The tool falls back to "page 1 is the front page, offer the rest",
    which is usually right but unverified. The report will say **NO TEXT LAYER**
    rather than sitting there empty, because an empty report reads as "nothing
    to check" when it means "nothing could be extracted."
  - *Pre-1970s grant* — **the order is inverted**: the drawing comes first and
    the specification follows. The first version of this tool skipped page 1
    unconditionally and so threw away the only drawing in US 3,514,091, then
    offered four pages of specification text as candidates. Page 1 is now
    dropped for being text-heavy, never for being page 1. All three shapes are
    pinned as fixtures in `test_fetch_patent_figure.py`.
- **Design patents** have few sheets and no text columns, so every page after
  the first is offered as a candidate. That is correct, just noisier.
- It **cannot confirm the number is the right patent for the entry.** That is
  what the report is for.
