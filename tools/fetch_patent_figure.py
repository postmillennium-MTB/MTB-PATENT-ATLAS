#!/usr/bin/env python3
"""
Fetch a patent's drawing sheets and produce cropped, atlas-ready candidate PNGs.

WHAT THIS AUTOMATES (the mechanical part)
  - downloading the patent PDF
  - working out which pages are drawing sheets rather than text columns
  - cropping off the page margin and the "U.S. Patent / Sheet n of m" header band
  - downscaling and naming the file the way pictures/ expects

WHAT THIS DELIBERATELY DOES NOT DO (the judgement part)
  - pick which figure belongs on the card. It writes several candidates and a
    human chooses. The best figure is often not the first one: for the DW-Link
    family the useful drawing is the abstract kinematic diagram, not the bike.
  - write imgAlt text. Alt text has to describe what is actually in the figure,
    with the real reference numerals, in both languages. That means a person
    looking at the image.
  - touch index.html. It only writes into an output directory.
  - invent anything. If the download fails it says so and exits non-zero. It
    never emits a placeholder image, and it never guesses a patent number.

It also dumps the PDF's own front-page text to report.txt, so the title,
inventor, assignee and filing/grant dates can be read off the primary document
instead of being taken from secondhand coverage. That is the part that decides
an entry's `conf` tier, so it is worth reading before wiring a figure up.

REQUIREMENTS
  poppler-utils (pdftoppm, pdftotext) and Pillow.
  On the GitHub Actions runner both are installed by the workflow.

USAGE
  python3 tools/fetch_patent_figure.py US12570369B1 US11866114B2
  python3 tools/fetch_patent_figure.py 4733881 --out /tmp/figs --candidates 6
  python3 tools/fetch_patent_figure.py US12570369B1 --url <pdf link>  # lookup blocked
  python3 tools/fetch_patent_figure.py US12570369B1 --pdf saved.pdf   # already have it

  Accepts "US12570369B1", "12570369", "D1140680", "RE45684".
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

# --- tuning knobs, all in one place ------------------------------------------

RENDER_DPI = 200          # pdftoppm resolution. 200 is legible at card size
                          # without producing 4MB files.
DRAWING_TEXT_MAX = 900    # chars of extracted text below which a page is taken
                          # to be a drawing sheet. Text columns run into the
                          # thousands; a drawing sheet yields only the header
                          # line plus scattered reference numerals.
INK_THRESHOLD = 200       # grey level at or below which a pixel counts as ink.
CROP_PAD = 24             # white margin re-added after autocropping, in px.
HEADER_MAX_FRAC = 0.09    # a top band shorter than this fraction of the sheet
                          # can be the "U.S. Patent ... Sheet n of m" header.
HEADER_GAP_FRAC = 0.012   # ...but only if this much blank space separates it
                          # from whatever is below, so a tall figure that
                          # happens to start near the top is never truncated.
MAX_WIDTH = 1600          # downscale wider output than this. Cards never
                          # display larger, and the repo has no CDN.
HTTP_TIMEOUT = 60
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) MTB-Patent-Atlas-figure-fetcher"

# USPTO's public print endpoint takes the bare digits and needs no page scrape,
# so it is tried first. Google Patents is the fallback and does need a scrape:
# the PDF lives on patentimages, linked from the patent page.
USPTO_PDF = "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/{digits}"
GOOGLE_PATENT_PAGE = "https://patents.google.com/patent/{full}/en"
PATENTIMAGES_RE = re.compile(r'https://patentimages\.storage\.googleapis\.com/[^\s"\'<>]+?\.pdf')


def parse_number(raw):
    """Split a patent identifier into (digits, canonical_name).

    digits          what USPTO's print endpoint wants (no country, no kind code)
    canonical_name  what the file should be called, matching pictures/'s
                    dominant US<number><kind>.png convention
    """
    s = raw.strip().upper().replace(",", "").replace(" ", "")
    s = re.sub(r"^US", "", s)
    m = re.match(r"^(RE|D|PP|H|T)?(\d+)([AB]\d?)?$", s)
    if not m:
        raise ValueError(
            "cannot parse %r as a US patent number. Expected forms: "
            "US12570369B1, 12570369, D1140680, RE45684." % raw
        )
    prefix, digits, kind = m.group(1) or "", m.group(2), m.group(3) or ""
    return prefix + digits, "US%s%s%s" % (prefix, digits, kind)


def _get(url, referer=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    if referer:
        req.add_header("Referer", referer)
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return r.read()


def download_pdf(digits, canonical, dest, direct_url=None):
    """Try the direct URL if given, then USPTO, then Google Patents.

    Three sources rather than two because the automatic ones can both fail for
    reasons that have nothing to do with the patent: an egress policy blocking
    the host, or Google refusing a scrape from a datacenter IP. The direct URL
    is the escape hatch -- on the Google Patents page for any patent, the PDF
    link is right there under the title, and pasting it here skips both
    automatic lookups entirely.
    """
    attempts = []

    if direct_url:
        try:
            blob = _get(direct_url)
            if blob[:5] == b"%PDF-":
                open(dest, "wb").write(blob)
                return direct_url
            attempts.append("%s -> not a PDF (%d bytes). If this is a Google "
                            "Patents *page* URL rather than the PDF link on it, "
                            "use the PDF link." % (direct_url, len(blob)))
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            attempts.append("%s -> %s" % (direct_url, e))

    url = USPTO_PDF.format(digits=digits)
    try:
        blob = _get(url)
        if blob[:5] == b"%PDF-":
            open(dest, "wb").write(blob)
            return url
        attempts.append("%s -> not a PDF (%d bytes)" % (url, len(blob)))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        attempts.append("%s -> %s" % (url, e))

    page_url = GOOGLE_PATENT_PAGE.format(full=canonical)
    try:
        html = _get(page_url).decode("utf-8", "replace")
        found = PATENTIMAGES_RE.search(html)
        if not found:
            attempts.append("%s -> page fetched but no patentimages PDF link" % page_url)
        else:
            pdf_url = found.group(0)
            blob = _get(pdf_url, referer=page_url)
            if blob[:5] == b"%PDF-":
                open(dest, "wb").write(blob)
                return pdf_url
            attempts.append("%s -> not a PDF (%d bytes)" % (pdf_url, len(blob)))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        attempts.append("%s -> %s" % (page_url, e))

    raise RuntimeError(
        "could not download a PDF for %s. Tried:\n  %s\n\n"
        "No image was written -- this tool never emits a placeholder.\n"
        "If every attempt is a 403: the network this is running on blocks "
        "patent hosts. Two ways forward, both of which still skip the manual "
        "cropping:\n"
        "  1. run it on the GitHub Actions runner "
        "(.github/workflows/patent-figure.yml), where egress is open;\n"
        "  2. open the patent on Google Patents, copy the PDF link under the "
        "title, and pass it with --url (or the pdf_url input in the workflow)."
        % (canonical, "\n  ".join(attempts))
    )


def require_tool(name):
    if shutil.which(name) is None:
        sys.exit(
            "error: %s not found. Install poppler-utils "
            "(apt-get install -y poppler-utils / brew install poppler)." % name
        )


def page_text_lengths(pdf, workdir):
    """Extracted-text length per page, 1-indexed, used to spot drawing sheets."""
    lengths = {}
    page = 1
    while True:
        out = os.path.join(workdir, "p%d.txt" % page)
        rc = subprocess.run(
            ["pdftotext", "-f", str(page), "-l", str(page), pdf, out],
            capture_output=True,
        ).returncode
        if rc != 0 or not os.path.exists(out):
            break
        txt = open(out, encoding="utf-8", errors="replace").read()
        lengths[page] = len(txt.strip())
        page += 1
        if page > 400:  # a runaway guard; no patent in this atlas is near this
            break
    return lengths


def pick_drawing_pages(lengths, want):
    """Pick the drawing sheets by text density. Three real document shapes:

      modern grant, text layer  p1 bibliographic (thousands of chars), then
                                drawing sheets (hundreds), then spec columns
                                (thousands). US 11,019,237 measured
                                p1=2400, p2-6=218..705, p7-16=~7500.
      pure image scan           every page extracts 0 chars, so density says
                                nothing. US 12,016,421 measured 0 across all
                                13 pages.
      pre-~1970s grant          THE ORDER IS INVERTED: drawings come first and
                                the spec follows. US 3,514,091 measured
                                p1=175 (the drawing) and p2-5=5455..8388.

    An earlier version skipped page 1 unconditionally, which is right for the
    first two shapes and exactly wrong for the third -- on US 3,514,091 it
    discarded the only drawing in the document and then, finding nothing under
    the threshold, fell back to "every page after the first" and offered four
    pages of specification text as drawing candidates. Worse than no output,
    because the candidates looked plausible in a file listing.

    So: page 1 is dropped because it is text-heavy, never because it is page 1.
    """
    low = [p for p in sorted(lengths) if lengths[p] <= DRAWING_TEXT_MAX]

    if len(low) == len(lengths):
        # Nothing distinguishes any page -- no text layer anywhere. Density is
        # useless here, so fall back to the one structural fact that still
        # holds for a modern grant: page 1 is the bibliographic front page.
        return [p for p in sorted(lengths) if p > 1][:want]

    if low:
        # Some pages are text-heavy and some are not, so the split is real.
        # Keep page 1 if it landed on the sparse side: that means it is a
        # drawing (the inverted old-patent shape), not a front page.
        return low[:want]

    # Every page is text-heavy. Rank by relative sparseness instead of an
    # absolute threshold, so the least text-like pages still surface rather
    # than handing back the first N pages in document order.
    return sorted(sorted(lengths), key=lambda p: lengths[p])[:want]


def render_page(pdf, page, workdir):
    prefix = os.path.join(workdir, "render%d" % page)
    subprocess.run(
        ["pdftoppm", "-f", str(page), "-l", str(page),
         "-r", str(RENDER_DPI), "-png", "-gray", pdf, prefix],
        check=True, capture_output=True,
    )
    hits = sorted(f for f in os.listdir(workdir)
                  if f.startswith("render%d-" % page) and f.endswith(".png"))
    if not hits:
        raise RuntimeError("pdftoppm produced no image for page %d" % page)
    return os.path.join(workdir, hits[0])


def ink_row_bands(img):
    """Row ranges containing ink, as [(top, bottom), ...] top-to-bottom."""
    w, h = img.size
    px = img.load()
    # Subsample columns: a header line or a figure spans many columns, and
    # checking every pixel on a 200dpi sheet is needlessly slow.
    step = max(1, w // 400)
    rows = []
    for y in range(h):
        for x in range(0, w, step):
            if px[x, y] <= INK_THRESHOLD:
                rows.append(y)
                break
    if not rows:
        return []
    bands, start, prev = [], rows[0], rows[0]
    gap = max(2, int(h * HEADER_GAP_FRAC))
    for y in rows[1:]:
        if y - prev > gap:
            bands.append((start, prev))
            start = y
        prev = y
    bands.append((start, prev))
    return bands


def crop_sheet(path, strip_header=True):
    from PIL import Image, ImageChops, ImageOps

    img = Image.open(path).convert("L")

    # Patent PDFs render light-on-dark essentially never, but screenshots taken
    # from a dark-mode viewer do, and one such file was already in pictures/.
    # Normalising here means a hand-added file can be run through this same
    # tool to match the rest.
    w, h = img.size
    edge, px = [], img.load()
    for x in range(0, w, max(1, w // 120)):
        edge += [px[x, 0], px[x, h - 1]]
    for y in range(0, h, max(1, h // 120)):
        edge += [px[0, y], px[w - 1, y]]
    if edge and sum(edge) / len(edge) < 128:
        img = ImageOps.invert(img)

    # Trim the page margin.
    bg = Image.new("L", img.size, 255)
    mask = ImageChops.difference(img, bg).point(lambda v: 255 if v > 18 else 0)
    box = mask.getbbox()
    if box:
        img = img.crop(box)

    # Drop the "U.S. Patent   <date>   Sheet n of m   <number>" band. It is
    # redundant on a card that already shows the number, and it costs vertical
    # space the figure could use. Only dropped when it really is a thin band
    # clearly separated from the drawing -- otherwise the figure is left whole.
    if strip_header:
        bands = ink_row_bands(img)
        if len(bands) >= 2:
            top, bottom = bands[0]
            band_h = bottom - top + 1
            gap = bands[1][0] - bottom
            if (band_h <= img.size[1] * HEADER_MAX_FRAC
                    and gap >= img.size[1] * HEADER_GAP_FRAC):
                img = img.crop((0, bands[1][0], img.size[0], img.size[1]))
                box2 = ImageChops.difference(
                    img, Image.new("L", img.size, 255)
                ).point(lambda v: 255 if v > 18 else 0).getbbox()
                if box2:
                    img = img.crop(box2)

    if img.size[0] > MAX_WIDTH:
        ratio = MAX_WIDTH / img.size[0]
        img = img.resize(
            (MAX_WIDTH, max(1, int(img.size[1] * ratio))), Image.LANCZOS
        )

    from PIL import ImageOps as _IO
    return _IO.expand(img, border=CROP_PAD, fill=255)


def process(raw, outdir, want, strip_header, local_pdf=None, direct_url=None):
    digits, canonical = parse_number(raw)
    os.makedirs(outdir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="patfig-")
    try:
        pdf = os.path.join(work, "%s.pdf" % canonical)
        if local_pdf:
            # --pdf: skip the download and crop a PDF already on disk. Useful
            # when the fetch is blocked but the document was saved by hand, and
            # as the way to test the cropping stage without network access.
            shutil.copyfile(local_pdf, pdf)
            source = "local file %s" % local_pdf
            print("  using %s" % source)
        else:
            source = download_pdf(digits, canonical, pdf, direct_url)
            print("  downloaded %s from %s" % (canonical, source))

        lengths = page_text_lengths(pdf, work)
        if not lengths:
            raise RuntimeError("pdftotext read no pages from the PDF")
        pages = pick_drawing_pages(lengths, want)
        print("  %d pages; drawing-sheet candidates: %s"
              % (len(lengths), pages or "none"))

        # Front-page text is the primary-source record. Write it out so the
        # number, title, inventor and dates can be checked against the entry.
        front = os.path.join(work, "p1.txt")
        report = os.path.join(outdir, "%s.report.txt" % canonical)
        with open(report, "w", encoding="utf-8") as fh:
            fh.write("patent: %s\nsource: %s\npages: %d\n" % (canonical, source, len(lengths)))
            fh.write("per-page extracted text length: %s\n\n" % lengths)
            fh.write("=== FRONT PAGE TEXT (primary source -- check the entry against this) ===\n")
            front_text = ""
            if os.path.exists(front):
                front_text = open(front, encoding="utf-8", errors="replace").read()
            if front_text.strip():
                fh.write(front_text)
            else:
                # An empty report reads as "nothing to check" rather than
                # "nothing could be extracted", which are very different things
                # when the report exists to verify an entry's conf tier.
                fh.write(
                    "(NO TEXT LAYER -- this PDF is a pure image scan, so no "
                    "bibliographic text could be extracted.)\n\n"
                    "The front page cannot be checked automatically here. Read "
                    "the first rendered page by eye, or open the patent on "
                    "Google Patents, before setting this entry's conf tier. Do "
                    "not treat the absence of a contradiction as confirmation.\n"
                )
                print("  NOTE: no text layer -- the report has no front-page "
                      "text to verify the entry against.")
        print("  wrote %s" % report)

        made = []
        for i, page in enumerate(pages, 1):
            rendered = render_page(pdf, page, work)
            img = crop_sheet(rendered, strip_header=strip_header)
            name = "%s__cand%d_p%d.png" % (canonical, i, page)
            dest = os.path.join(outdir, name)
            img.save(dest, optimize=True)
            made.append(dest)
            print("  candidate %d: %s  (page %d, %dx%d, %.0fKB)"
                  % (i, name, page, img.size[0], img.size[1],
                     os.path.getsize(dest) / 1024))
        return canonical, made
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("numbers", nargs="+", help="patent numbers, e.g. US12570369B1")
    ap.add_argument("--out", default="figures-out",
                    help="output directory (default: figures-out). Candidates land "
                         "here for review; nothing is written into pictures/ "
                         "automatically.")
    ap.add_argument("--candidates", type=int, default=4,
                    help="how many drawing sheets to emit per patent (default 4)")
    ap.add_argument("--keep-header", action="store_true",
                    help="keep the 'U.S. Patent / Sheet n of m' band")
    ap.add_argument("--pdf",
                    help="crop this already-downloaded PDF instead of fetching. "
                         "Only valid with a single patent number, which is used "
                         "for naming. Lets the cropping half run where the patent "
                         "hosts are unreachable.")
    ap.add_argument("--url",
                    help="download the PDF from this exact URL instead of looking "
                         "it up. Use the PDF link shown under the title on the "
                         "Google Patents page. Only valid with a single patent "
                         "number, which is used for naming.")
    args = ap.parse_args()
    if args.pdf and len(args.numbers) != 1:
        sys.exit("error: --pdf takes exactly one patent number, for naming.")
    if args.url and len(args.numbers) != 1:
        sys.exit("error: --url takes exactly one patent number, for naming.")
    if args.pdf and args.url:
        sys.exit("error: --pdf and --url are alternatives; pass one or neither.")

    require_tool("pdftoppm")
    require_tool("pdftotext")
    try:
        import PIL  # noqa: F401
    except ImportError:
        sys.exit("error: Pillow not installed. pip install Pillow")

    failures = []
    for raw in args.numbers:
        print("\n%s" % raw)
        try:
            process(raw, args.out, args.candidates, not args.keep_header,
                    args.pdf, args.url)
        except Exception as e:                      # noqa: BLE001
            print("  FAILED: %s" % e)
            failures.append((raw, str(e)))

    print("\n" + "=" * 66)
    print("Candidates are in %s/ -- nothing has been added to pictures/." % args.out)
    print("To finish a figure:")
    print("  1. look at the candidates and pick the one that shows the mechanism")
    print("  2. rename it to US<number><kind>.png and move it into pictures/")
    print("  3. read <patent>.report.txt and check the entry's number, title,")
    print("     inventor and dates against the PDF's own front page")
    print("  4. write img + bilingual imgAlt on the entry, describing the actual")
    print("     reference numerals in the figure you chose")
    print("  5. delete the candidates you did not use")
    if failures:
        print("\n%d of %d failed:" % (len(failures), len(args.numbers)))
        for raw, msg in failures:
            print("  %s: %s" % (raw, msg.splitlines()[0]))
        sys.exit(1)


if __name__ == "__main__":
    main()
