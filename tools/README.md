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

### The other way: on a computer

```bash
pip install Pillow
sudo apt-get install -y poppler-utils     # macOS: brew install poppler

python3 tools/fetch_patent_figure.py US12570369B1 US11866114B2
python3 tools/fetch_patent_figure.py 4733881 --out /tmp/figs --candidates 6
python3 tools/fetch_patent_figure.py US9102197B2 --pdf saved.pdf   # already have the PDF
```

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

### Known limits

- **Figure choice is not automatable in any honest way.** Which drawing explains
  a mechanism to a reader is an editorial call.
- **Alt text is not automatable either.** It has to name the real reference
  numerals in the figure actually chosen, in English and French.
- **The fetch needs open egress.** Both sources (`image-ppubs.uspto.gov` and
  `patents.google.com`) are blocked by the egress proxy in some Claude Code
  sandboxes; there the script fails loudly, writes nothing, and says to use the
  workflow instead. It never emits a placeholder.
- **Design patents** have few sheets and no text columns, so every page after
  the first is offered as a candidate. That is correct, just noisier.
- **Pre-1920 patents** are scanned images with no text layer, so every page
  reads as a drawing sheet. Expect to skip the first candidate by hand.
- It **cannot confirm the number is the right patent for the entry.** That is
  what the report is for.
