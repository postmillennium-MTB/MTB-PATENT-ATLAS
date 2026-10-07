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

Alongside the candidates it writes <patent>__contact.png, a labelled thumbnail
grid of every drawing sheet, so the right figure can be chosen from one image
instead of guessing how many candidates to ask for. Sheets labelled "prior art"
are ranked last for the default candidates (they stay on the contact sheet).

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
  python3 tools/fetch_patent_figure.py DE102017116754B4               # non-US number
  python3 tools/fetch_patent_figure.py US2011227312A1 --pages 10-13   # exact sheets
  python3 tools/fetch_patent_figure.py US2011227312A1 --pages 12 --rotate 12:cw

  Accepts "US12570369B1", "12570369", "D1140680", "RE45684", or a non-US
  number with its own office prefix, e.g. "DE102017116754B4", "EP3111109" --
  the USPTO print endpoint is skipped for those (US-only) and there is no
  kind-code guessing (each office's scheme differs; the given kind code is
  trusted as given rather than guessed at).
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
SPECK_INK_PX = 150        # an isolated edge mark with this few ink pixels or fewer
                          # is scan dust, not drawing, and must not stretch the
                          # crop box. A real drawing element (a label, even a
                          # long thin line) carries far more than this.
SPECK_GAP_FRAC = 0.01     # blank run, as a fraction of the sheet's height or
                          # width, that separates one cluster of ink from the next.
CONTACT_DPI = 70          # thumbnails need far less resolution than candidates.
CONTACT_MAX_SHEETS = 24   # a 56-sheet patent would make an unreadable grid;
                          # the report says how many were left off.
CONTACT_COLS = 4
CONTACT_CELL = (340, 390) # width, height of one thumbnail cell, label included.
CONTACT_LABEL_H = 30
CONTACT_PAD = 6           # white border kept around each thumbnail's drawing.
# Figures a patent labels as background art. They are rarely the figure a card
# wants, but they come first in the PDF often enough (US 2011/0227312 opens with
# eight of them) that the default candidates were all prior art.
BACKGROUND_ART_RE = re.compile(r"(PRIOR|RELATED|CONVENTIONAL|BACKGROUND)\s+ART", re.I)
ROTATIONS = {"cw": -90, "ccw": 90, "180": 180}  # PIL rotates counter-clockwise
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

    digits          what USPTO's print endpoint wants (no country, no kind
                    code) -- only meaningful when canonical_name starts with
                    "US"; for a non-US number it's the same digits, unused
                    by the (US-only) USPTO endpoint.
    canonical_name  what the file should be called, matching pictures/'s
                    dominant <COUNTRY><number><kind>.png convention. A bare
                    number or one already prefixed "US" defaults to the US
                    office, covering the vast majority of numbers in this
                    atlas. A non-US number must carry its own office prefix
                    explicitly (DE102017116754B4, EP3111109) -- there is no
                    sane default to guess for it.
    """
    s = raw.strip().upper().replace(",", "").replace(" ", "")
    us = re.sub(r"^US", "", s)
    m = re.match(r"^(RE|D|PP|H|T)?(\d+)([AB]\d?)?$", us)
    if m:
        prefix, digits, kind = m.group(1) or "", m.group(2), m.group(3) or ""
        return prefix + digits, "US%s%s%s" % (prefix, digits, kind)

    # Not a bare/US-prefixed number -- try a non-US office prefix instead.
    # Other offices don't share USPTO's RE/D/PP/H/T design-and-reissue
    # sub-prefixes, so this branch stays deliberately simpler: office code,
    # digits, kind code. Kind-code shapes vary by office (DE's "B4"/"U1" vs.
    # USPTO's "B1"/"A1"), so this accepts any short letter+digit suffix
    # rather than the US-specific [AB]\d? pattern above.
    m2 = re.match(r"^([A-Z]{2,3})(\d+)([A-Z]\d{0,2})?$", s)
    if m2:
        country, digits, kind = m2.group(1), m2.group(2), m2.group(3) or ""
        return digits, country + digits + kind

    raise ValueError(
        "cannot parse %r as a patent number. Expected forms: "
        "US12570369B1, 12570369, D1140680, RE45684, or a non-US number with "
        "its own office prefix, e.g. DE102017116754B4, EP3111109." % raw
    )


# Every live run so far -- Forcite, GoPro, Park Tool, the DRCV shock below --
# has gone through this fallback. The USPTO print endpoint has returned 403
# on every attempt from a GitHub-hosted runner, whatever the reason (rate
# limiting, a UA check, geographic policy). It is kept as the first attempt
# because it costs nothing to try and may start working, but in practice
# Google Patents is not a fallback here, it is the path.
#
# That makes the exact kind code load-bearing in a way a caller often can't
# get right from secondhand sourcing: a news article about a patent almost
# never prints "B1" vs "B2" vs "A1", and guessing wrong doesn't 403 (blocked)
# but 404s (wrong specific document) -- a different failure that is worth
# recovering from automatically rather than making the caller re-run with a
# guess-and-check loop of their own. US 6,203,042 (guessed as "...A", the
# generic fallback when no kind code is known) is the case that exposed this:
# the real kind code is B1, and Google's own page for a bare "...A" 404s
# outright rather than redirecting.
KIND_CODE_FALLBACKS = ["B1", "B2", "A1", "A2", "B", "A"]


def _get(url, referer=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    if referer:
        req.add_header("Referer", referer)
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
        return r.read()


def _http_status(exc):
    return exc.code if isinstance(exc, urllib.error.HTTPError) else None


def download_pdf(digits, canonical, dest, direct_url=None):
    """Try the direct URL if given, then USPTO, then Google Patents.

    Three sources rather than two because the automatic ones can both fail for
    reasons that have nothing to do with the patent: an egress policy blocking
    the host, or Google refusing a scrape from a datacenter IP. The direct URL
    is the escape hatch -- on the Google Patents page for any patent, the PDF
    link is right there under the title, and pasting it here skips both
    automatic lookups entirely.

    USPTO's print endpoint only exists for US numbers, so a non-US canonical
    (a "canonical" not starting with "US" -- see parse_number) skips straight
    to Google Patents, which mirrors most national offices' own PDFs.
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

    is_us = canonical.startswith("US")

    # The USPTO print endpoint only serves US numbers -- skip it entirely for
    # a non-US canonical rather than firing a request that can only 404/403.
    if is_us:
        url = USPTO_PDF.format(digits=digits)
        try:
            blob = _get(url)
            if blob[:5] == b"%PDF-":
                open(dest, "wb").write(blob)
                return url
            attempts.append("%s -> not a PDF (%d bytes)" % (url, len(blob)))
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            attempts.append("%s -> %s" % (url, e))

    # Try the caller's own canonical id first, then -- only on a 404, meaning
    # the *page itself* doesn't exist rather than the whole site being blocked
    # -- retry the same digits under each common kind code. re-guessing after
    # a 403 would be pointless (every kind code would fail the same way) and
    # is deliberately not attempted. KIND_CODE_FALLBACKS is a USPTO kind-code
    # list (B1/B2/A1/...) so this guessing only applies to a US canonical --
    # for a non-US number the caller's own kind code is trusted as given
    # rather than guessed against a scheme (DE's B4/U1/C1/...) this tool
    # doesn't model.
    candidates = [canonical]
    if is_us:
        m = re.match(r"^(RE|D|PP|H|T)?(\d+)", canonical.removeprefix("US"))
        prefix, num = (m.group(1) or "", m.group(2)) if m else ("", "")
        for kc in KIND_CODE_FALLBACKS:
            alt = "US%s%s%s" % (prefix, num, kc)
            if alt not in candidates:
                candidates.append(alt)

    for i, cand in enumerate(candidates):
        page_url = GOOGLE_PATENT_PAGE.format(full=cand)
        try:
            html = _get(page_url).decode("utf-8", "replace")
            found = PATENTIMAGES_RE.search(html)
            if not found:
                attempts.append("%s -> page fetched but no patentimages PDF link" % page_url)
                break  # page exists, so the id was right; a different fault, don't guess further
            pdf_url = found.group(0)
            blob = _get(pdf_url, referer=page_url)
            if blob[:5] == b"%PDF-":
                open(dest, "wb").write(blob)
                if i > 0:
                    print("  note: %s 404'd; %s is the real kind code for this "
                          "number" % (canonical, cand))
                return pdf_url
            attempts.append("%s -> not a PDF (%d bytes)" % (pdf_url, len(blob)))
            break  # got a page and a PDF link, just not a real PDF -- not a kind-code problem
        except urllib.error.HTTPError as e:
            attempts.append("%s -> %s" % (page_url, e))
            if _http_status(e) != 404:
                break  # not a "wrong id" failure (403/5xx/etc) -- retrying other kind codes won't help
            continue  # 404: plausibly just the wrong kind code, try the next one
        except (urllib.error.URLError, OSError) as e:
            attempts.append("%s -> %s" % (page_url, e))
            break

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
    return read_pages(pdf, workdir)[0]


def read_pages(pdf, workdir):
    """(lengths, texts): extracted text length and the text itself, per page,
    1-indexed. The text is kept so sheets labelled "prior art" can be spotted."""
    lengths, texts = {}, {}
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
        texts[page] = txt
        page += 1
        if page > 400:  # a runaway guard; no patent in this atlas is near this
            break
    return lengths, texts


def background_art_pages(lengths, texts):
    """Drawing-density pages whose text says PRIOR ART / RELATED ART / etc.

    Only sparse pages are considered: a specification column mentions "prior
    art" constantly and is not a candidate in the first place. This is a
    heuristic over a text layer, so it finds nothing on an image-only scan, and
    it can flag a sheet that mixes a prior-art figure with the invention's own.
    That is why such sheets are ranked last, never dropped."""
    return {p for p, txt in texts.items()
            if lengths.get(p, 0) <= DRAWING_TEXT_MAX and BACKGROUND_ART_RE.search(txt)}


def pick_drawing_pages(lengths, want, avoid=()):
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
        ordered = [p for p in sorted(lengths) if p > 1]
    elif low:
        # Some pages are text-heavy and some are not, so the split is real.
        # Keep page 1 if it landed on the sparse side: that means it is a
        # drawing (the inverted old-patent shape), not a front page.
        ordered = low
    else:
        # Every page is text-heavy. Rank by relative sparseness instead of an
        # absolute threshold, so the least text-like pages still surface rather
        # than handing back the first N pages in document order.
        ordered = sorted(sorted(lengths), key=lambda p: lengths[p])

    # Sheets labelled as background art go last, not away: still reachable by
    # asking for more candidates, and always visible on the contact sheet.
    if avoid:
        ordered = ([p for p in ordered if p not in avoid]
                   + [p for p in ordered if p in avoid])
    return ordered[:want]


def render_page(pdf, page, workdir, dpi=RENDER_DPI):
    stem = "render%d_%d" % (dpi, page)
    prefix = os.path.join(workdir, stem)
    subprocess.run(
        ["pdftoppm", "-f", str(page), "-l", str(page),
         "-r", str(dpi), "-png", "-gray", pdf, prefix],
        check=True, capture_output=True,
    )
    hits = sorted(f for f in os.listdir(workdir)
                  if f.startswith(stem + "-") and f.endswith(".png"))
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


def _ink_counts(mask):
    """Ink pixels in each row of a 0/255 'L' mask. bytes.count runs in C, so
    this stays fast on a 200dpi sheet without needing numpy."""
    w, h = mask.size
    data = mask.tobytes()
    return [data.count(255, y * w, (y + 1) * w) for y in range(h)]


def _content_span(counts):
    """(first, last) index of real content in a per-row (or per-column) ink
    count list, ignoring specks at either end. None if there is no real ink.

    Ink is grouped into clusters separated by blank runs; a cluster with no
    more than SPECK_INK_PX ink pixels in total is scan dust. Dust at the edge
    is what used to stretch the crop box: a plain bounding box treats one stray
    dot in a margin as drawing. Counting pixels (rather than rows) is what keeps
    a long thin line, such as a dimension line reaching beyond the rest of the
    figure, from being mistaken for dust."""
    gap = max(8, int(len(counts) * SPECK_GAP_FRAC))
    clusters, start, last, ink = [], None, None, 0
    for i, c in enumerate(counts):
        if not c:
            continue
        if start is not None and i - last > gap:
            clusters.append((start, last, ink))
            start, ink = None, 0
        if start is None:
            start = i
        last = i
        ink += c
    if start is not None:
        clusters.append((start, last, ink))
    real = [c for c in clusters if c[2] > SPECK_INK_PX]
    if not real:
        return None
    return real[0][0], real[-1][1]


def content_box(img):
    """Bounding box of the drawing on a white-background sheet, ignoring
    scan specks. Falls back to the plain bounding box if nothing survives."""
    from PIL import Image, ImageChops

    mask = ImageChops.difference(img, Image.new("L", img.size, 255)).point(
        lambda v: 255 if v > 18 else 0)
    rows = _content_span(_ink_counts(mask))
    if rows is None:
        return mask.getbbox()
    top, bottom = rows
    transpose = getattr(Image, "Transpose", Image).TRANSPOSE
    band = mask.crop((0, top, mask.size[0], bottom + 1))
    cols = _content_span(_ink_counts(band.transpose(transpose)))
    if cols is None:
        return mask.getbbox()
    return (cols[0], top, cols[1] + 1, bottom + 1)


def crop_sheet(path, strip_header=True, rotate=0, pad=CROP_PAD):
    from PIL import Image, ImageOps

    img = Image.open(path).convert("L")

    # Some sheets are laid out sideways in the PDF (a landscape figure on a
    # portrait page). pdftoppm renders them as stored, so the caller says which
    # pages need turning; see --rotate. Done before cropping so the header
    # logic below still sees the header at the top.
    if rotate:
        img = img.rotate(rotate, expand=True, fillcolor=255)

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

    # Trim the page margin (and any scan specks in it).
    box = content_box(img)
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
                box2 = content_box(img)
                if box2:
                    img = img.crop(box2)

    if img.size[0] > MAX_WIDTH:
        ratio = MAX_WIDTH / img.size[0]
        img = img.resize(
            (MAX_WIDTH, max(1, int(img.size[1] * ratio))), Image.LANCZOS
        )

    return ImageOps.expand(img, border=pad, fill=255)


def parse_pages(spec):
    """"6,10-12" -> [6, 10, 11, 12]. Order kept, duplicates dropped."""
    pages = []
    for part in spec.replace(" ", "").split(","):
        m = re.match(r"^(\d+)(?:-(\d+))?$", part)
        if not m:
            raise ValueError("cannot parse %r in --pages; expected e.g. 6,10-12" % part)
        lo = int(m.group(1))
        hi = int(m.group(2) or lo)
        if lo < 1 or hi < lo:
            raise ValueError("bad page range %r in --pages" % part)
        pages += [p for p in range(lo, hi + 1) if p not in pages]
    return pages


def parse_rotate(spec):
    """"12:cw,13:ccw" -> {12: -90, 13: 90}. cw/ccw/180 say which way to turn
    the rendered sheet; words rather than degrees because the sign convention
    of image libraries (counter-clockwise positive) is easy to get backwards,
    and was, by hand, the first time this was needed."""
    out = {}
    for part in spec.replace(" ", "").split(","):
        m = re.match(r"^(\d+):(cw|ccw|180)$", part, re.I)
        if not m:
            raise ValueError("cannot parse %r in --rotate; expected e.g. 12:cw,13:ccw "
                             "(cw, ccw or 180)" % part)
        out[int(m.group(1))] = ROTATIONS[m.group(2).lower()]
    return out


def _label_font(size):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=size)   # Pillow >= 10.1
    except TypeError:
        return ImageFont.load_default()


def build_contact_sheet(pdf, sheets, chosen, prior, rotations, work, dest):
    """One labelled thumbnail grid of the drawing sheets, saved to dest.

    sheets   page numbers to show, in page order
    chosen   {page: candidate number} for the sheets also written as candidates
    prior    pages flagged as background art

    Returns (sheets_shown, sheets_left_off). Looking at this one image is how
    the right figure is picked; the alternative was re-running with a bigger
    --candidates until it appeared."""
    from PIL import Image, ImageDraw

    shown = sheets[:CONTACT_MAX_SHEETS]
    cw, ch = CONTACT_CELL
    rows = (len(shown) + CONTACT_COLS - 1) // CONTACT_COLS
    grid = Image.new("L", (cw * CONTACT_COLS, ch * max(rows, 1)), 255)
    draw = ImageDraw.Draw(grid)
    font = _label_font(18)
    for i, page in enumerate(shown):
        x, y = (i % CONTACT_COLS) * cw, (i // CONTACT_COLS) * ch
        rendered = render_page(pdf, page, work, dpi=CONTACT_DPI)
        thumb = crop_sheet(rendered, strip_header=True,
                           rotate=rotations.get(page, 0), pad=CONTACT_PAD)
        thumb.thumbnail((cw - 10, ch - CONTACT_LABEL_H - 8))
        grid.paste(thumb, (x + (cw - thumb.width) // 2,
                           y + CONTACT_LABEL_H + 2))
        label = "p%d" % page
        if page in chosen:
            label += "  = cand %d" % chosen[page]
        if page in prior:
            label += "  PRIOR ART"
        draw.text((x + 8, y + 5), label, fill=0, font=font)
        draw.rectangle((x, y, x + cw - 1, y + ch - 1), outline=170)
    grid.save(dest, optimize=True)
    return shown, sheets[CONTACT_MAX_SHEETS:]


def process(raw, outdir, want, strip_header, local_pdf=None, direct_url=None,
            pages=None, rotations=None):
    rotations = rotations or {}
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

        lengths, texts = read_pages(pdf, work)
        if not lengths:
            raise RuntimeError("pdftotext read no pages from the PDF")
        prior = background_art_pages(lengths, texts)
        # Every drawing sheet in rank order, for the contact sheet; the first
        # `want` of them are the candidates unless --pages named them outright.
        ranked = pick_drawing_pages(lengths, len(lengths), avoid=prior)
        if pages:
            bad = [p for p in pages if p not in lengths]
            if bad:
                raise RuntimeError("--pages %s: the PDF has only %d pages"
                                   % (bad, len(lengths)))
            chosen_pages = pages
        else:
            chosen_pages = ranked[:want]
        for p in rotations:
            if p not in lengths:
                raise RuntimeError("--rotate names page %d but the PDF has only "
                                   "%d pages" % (p, len(lengths)))
        print("  %d pages; drawing-sheet candidates: %s"
              % (len(lengths), chosen_pages or "none"))
        if prior:
            print("  sheets labelled prior art, ranked last: %s" % sorted(prior))

        # Front-page text is the primary-source record. Write it out so the
        # number, title, inventor and dates can be checked against the entry.
        front = os.path.join(work, "p1.txt")
        report = os.path.join(outdir, "%s.report.txt" % canonical)
        with open(report, "w", encoding="utf-8") as fh:
            fh.write("patent: %s\nsource: %s\npages: %d\n" % (canonical, source, len(lengths)))
            fh.write("per-page extracted text length: %s\n" % lengths)
            fh.write("drawing sheets, best first: %s\n" % ranked)
            if prior:
                fh.write("labelled prior art / background art (ranked last): %s\n"
                         % sorted(prior))
            if all(v == 0 for v in lengths.values()):
                fh.write("NO TEXT LAYER: sheets are listed in page order only; the "
                         "ranking above is a guess, not a classification. Check "
                         "the contact sheet.\n")
            fh.write("contact sheet: %s__contact.png\n\n" % canonical)
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
        for i, page in enumerate(chosen_pages, 1):
            rendered = render_page(pdf, page, work)
            img = crop_sheet(rendered, strip_header=strip_header,
                             rotate=rotations.get(page, 0))
            name = "%s__cand%d_p%d.png" % (canonical, i, page)
            dest = os.path.join(outdir, name)
            img.save(dest, optimize=True)
            made.append(dest)
            print("  candidate %d: %s  (page %d, %dx%d, %.0fKB)"
                  % (i, name, page, img.size[0], img.size[1],
                     os.path.getsize(dest) / 1024))

        sheets = sorted(ranked)
        if sheets:
            contact = os.path.join(outdir, "%s__contact.png" % canonical)
            shown, left_off = build_contact_sheet(
                pdf, sheets, {p: i for i, p in enumerate(chosen_pages, 1)},
                prior, rotations, work, contact)
            print("  contact sheet: %s (%d sheets%s)" % (
                os.path.basename(contact), len(shown),
                "; %d more not shown: pages %s" % (len(left_off), left_off)
                if left_off else ""))
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
    ap.add_argument("--pages",
                    help="emit exactly these PDF pages as candidates, e.g. 6,10-12, "
                         "instead of the first --candidates drawing sheets. Page "
                         "numbers are the ones printed on the contact sheet. Only "
                         "valid with a single patent number.")
    ap.add_argument("--rotate",
                    help="turn sideways sheets upright, e.g. 12:cw,13:ccw (cw, ccw "
                         "or 180, keyed by PDF page). Only valid with a single "
                         "patent number.")
    args = ap.parse_args()
    for flag in ("pages", "rotate"):
        if getattr(args, flag) and len(args.numbers) != 1:
            sys.exit("error: --%s names pages of one PDF, so it takes exactly "
                     "one patent number." % flag)
    try:
        pages = parse_pages(args.pages) if args.pages else None
        rotations = parse_rotate(args.rotate) if args.rotate else {}
    except ValueError as e:
        sys.exit("error: %s" % e)
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
                    args.pdf, args.url, pages, rotations)
        except Exception as e:                      # noqa: BLE001
            print("  FAILED: %s" % e)
            failures.append((raw, str(e)))

    print("\n" + "=" * 66)
    print("Candidates are in %s/ -- nothing has been added to pictures/." % args.out)
    print("To finish a figure:")
    print("  1. open <patent>__contact.png to see every drawing sheet at once, then")
    print("     pick the one that shows the mechanism (re-run with --pages N to get")
    print("     a sheet that is not among the candidates; --rotate N:cw if sideways)")
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
