#!/usr/bin/env python3
"""Self-test for fetch_patent_figure.py. No network. Pillow and poppler are
needed only for the image and end-to-end checks at the bottom, which are
skipped, with a message, when either is missing.

    python3 tools/test_fetch_patent_figure.py

The page-length fixtures below are not invented -- they are the real
per-page extracted-text lengths measured by live workflow runs on 2026-09-17,
and they encode three genuinely different document shapes that a patent PDF
can take. The third one broke the first version of the classifier, which
skipped page 1 unconditionally and so discarded the only drawing in a pre-1970
grant. Keep these fixtures honest: if a future run finds a fourth shape, add
its measured numbers here rather than adjusting the rule until the run looks
right.
"""

import sys
import os
import tempfile
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_patent_figure import pick_drawing_pages, parse_number  # noqa: E402
import fetch_patent_figure as F  # noqa: E402

FAILURES = []


def check(name, got, expected):
    if got == expected:
        print("PASS  %s" % name)
    else:
        print("FAIL  %s\n        got      %r\n        expected %r" % (name, got, expected))
        FAILURES.append(name)


# --- page classification, against real measured documents --------------------

# US 11,019,237 (GoPro multi-camera sync). The textbook modern grant: a
# bibliographic front page, then drawing sheets, then specification columns.
check("modern grant with a text layer",
      pick_drawing_pages(
          {1: 2400, 2: 349, 3: 705, 4: 218, 5: 474, 6: 238, 7: 6959, 8: 7201,
           9: 7667, 10: 7776, 11: 7727, 12: 7631, 13: 7622, 14: 7579,
           15: 6730, 16: 2663}, 4),
      [2, 3, 4, 5])

# US 12,016,421 (Forcite helmet electronics). A pure image scan: every page
# extracts zero characters, so text density cannot separate drawings from
# text. Only the structural assumption is left -- page 1 is the front page.
check("pure image scan, no text layer anywhere",
      pick_drawing_pages({i: 0 for i in range(1, 14)}, 4),
      [2, 3, 4, 5])

# US 3,514,091 (Park Tool clamping device, 1970). The order is INVERTED:
# the drawing is page 1 and the specification follows it. The rule must keep
# page 1 here, because it is sparse, not drop it for being page 1.
check("pre-1970 grant, drawings before the specification",
      pick_drawing_pages({1: 175, 2: 7367, 3: 8388, 4: 8211, 5: 5455}, 4),
      [1])

# Degenerate: nothing is under the absolute threshold. Rank by relative
# sparseness rather than handing back the first N pages in document order.
check("every page text-heavy falls back to the sparsest pages",
      pick_drawing_pages({1: 9000, 2: 8000, 3: 5000, 4: 7000}, 2),
      [3, 4])

check("want= is respected",
      pick_drawing_pages({1: 2400, 2: 10, 3: 20, 4: 30, 5: 9000}, 2),
      [2, 3])

# --- number parsing ----------------------------------------------------------

check("plain utility grant", parse_number("US12570369B1"), ("12570369", "US12570369B1"))
check("bare digits", parse_number("12570369"), ("12570369", "US12570369"))
check("design patent", parse_number("D1140680"), ("D1140680", "USD1140680"))
check("reissue", parse_number("RE45684"), ("RE45684", "USRE45684"))
check("commas and spaces tolerated", parse_number("US 12,570,369 B1"), ("12570369", "US12570369B1"))

# Non-US numbers need their own office prefix -- there is no sane default to
# guess for them the way a bare US number defaults to "US". These two are the
# PI ROPE GmbH spoke patents this atlas has (2026-09-26 pass), the case that
# motivated this branch: DE-numbered documents fetch_patent_figure.py could
# not previously parse at all.
check("German granted patent (B4)", parse_number("DE102017116754B4"),
      ("102017116754", "DE102017116754B4"))
check("German utility model (U1, a Gebrauchsmuster)", parse_number("DE202017104416U1"),
      ("202017104416", "DE202017104416U1"))
check("non-US number, no kind code", parse_number("EP3111109"), ("3111109", "EP3111109"))

try:
    parse_number("not-a-patent")
    check("garbage input is rejected", "no exception raised", "ValueError")
except ValueError:
    print("PASS  garbage input is rejected")

# --- kind-code fallback on a Google Patents 404 (mocked, no network) --------
#
# US 6,203,042 is the real case this locks in: guessed at "US6203042A" (the
# generic fallback when a news article doesn't print the exact kind code),
# it 404'd. The real kind code is B1. This replays that exact sequence
# against a fake _get() so the recovery is pinned without touching the
# network -- and so a future change can't silently regress it back to
# failing loudly on a wrong guess instead of trying the obvious next one.


def _install_fake_get(responses):
    """responses: url -> bytes on success, or url -> an HTTPError to raise.
    Any url not listed 404s, matching a real unlisted document."""
    calls = []

    def fake_get(url, referer=None):
        calls.append(url)
        r = responses.get(url)
        if r is None:
            raise urllib.error.HTTPError(url, 404, "Not Found", None, None)
        if isinstance(r, Exception):
            raise r
        return r

    orig = F._get
    F._get = fake_get
    return calls, orig


def test_kind_code_fallback_recovers_from_a_wrong_guess():
    pdf_bytes = b"%PDF-1.4 fake"
    pdf_url = "https://patentimages.storage.googleapis.com/xx/US6203042B1.pdf"
    uspto_url = F.USPTO_PDF.format(digits="6203042")
    bad_page = F.GOOGLE_PATENT_PAGE.format(full="US6203042A")
    good_page = F.GOOGLE_PATENT_PAGE.format(full="US6203042B1")

    calls, orig = _install_fake_get({
        uspto_url: urllib.error.HTTPError(uspto_url, 403, "Forbidden", None, None),
        bad_page: urllib.error.HTTPError(bad_page, 404, "Not Found", None, None),
        good_page: ('<a href="%s">pdf</a>' % pdf_url).encode(),
        pdf_url: pdf_bytes,
    })
    try:
        with tempfile.TemporaryDirectory() as td:
            dest = os.path.join(td, "out.pdf")
            source = F.download_pdf("6203042", "US6203042A", dest)
            ok = (source == pdf_url
                  and open(dest, "rb").read() == pdf_bytes
                  and bad_page in calls and good_page in calls)
            check("kind-code fallback recovers from a wrong guess (404)",
                  ok, True)
    finally:
        F._get = orig


def test_403_does_not_trigger_kind_code_guessing():
    uspto_url = F.USPTO_PDF.format(digits="9999999")
    first_page = F.GOOGLE_PATENT_PAGE.format(full="US9999999A")

    calls, orig = _install_fake_get({
        uspto_url: urllib.error.HTTPError(uspto_url, 403, "Forbidden", None, None),
        first_page: urllib.error.HTTPError(first_page, 403, "Forbidden", None, None),
    })
    try:
        with tempfile.TemporaryDirectory() as td:
            dest = os.path.join(td, "out.pdf")
            try:
                F.download_pdf("9999999", "US9999999A", dest)
                ok = False
            except RuntimeError:
                # A 403 means blocked, not "wrong id" -- every kind code would
                # fail identically, so exactly one Google Patents URL should
                # have been tried, not all six fallbacks.
                ok = calls == [uspto_url, first_page]
            check("a 403 does not trigger kind-code guessing (would be pointless)",
                  ok, True)
    finally:
        F._get = orig


def test_non_us_canonical_skips_uspto_and_kind_code_guessing():
    """A non-US canonical (DE102017116754B4) has no USPTO print endpoint and
    no modeled kind-code scheme to guess against -- download_pdf should go
    straight to the one Google Patents URL for the given kind code, never
    touching USPTO_PDF or trying alternates."""
    pdf_bytes = b"%PDF-1.4 fake"
    pdf_url = "https://patentimages.storage.googleapis.com/xx/DE102017116754B4.pdf"
    page_url = F.GOOGLE_PATENT_PAGE.format(full="DE102017116754B4")
    uspto_url = F.USPTO_PDF.format(digits="102017116754")

    calls, orig = _install_fake_get({
        page_url: ('<a href="%s">pdf</a>' % pdf_url).encode(),
        pdf_url: pdf_bytes,
    })
    try:
        with tempfile.TemporaryDirectory() as td:
            dest = os.path.join(td, "out.pdf")
            source = F.download_pdf("102017116754", "DE102017116754B4", dest)
            ok = (source == pdf_url
                  and open(dest, "rb").read() == pdf_bytes
                  and uspto_url not in calls
                  and calls == [page_url, pdf_url])
            check("non-US canonical skips USPTO and kind-code guessing", ok, True)
    finally:
        F._get = orig


test_kind_code_fallback_recovers_from_a_wrong_guess()
test_403_does_not_trigger_kind_code_guessing()
test_non_us_canonical_skips_uspto_and_kind_code_guessing()

# --- prior-art ranking, option parsing (no image libraries needed) ----------

# US 2011/0227312 is the real case: sheets 2-9 are labelled PRIOR ART and the
# application's own drawings start on sheet 10, so the default four candidates
# were all background art. Densities are the measured ones.
lengths_227312 = {1: 1309, 2: 79, 3: 97, 4: 110, 5: 79, 6: 97, 7: 97, 8: 98,
                  9: 16, 10: 79, 11: 89, 12: 80, 13: 93, 14: 6444, 15: 7231, 16: 5278}
check("prior-art sheets are ranked last, not dropped",
      pick_drawing_pages(lengths_227312, 4, avoid={2, 3, 4, 5, 6, 7, 8, 9}),
      [10, 11, 12, 13])
check("asking for more than the invention's own sheets reaches the prior art",
      pick_drawing_pages(lengths_227312, 6, avoid={2, 3, 4, 5, 6, 7, 8, 9}),
      [10, 11, 12, 13, 2, 3])
check("no avoid set leaves the ranking unchanged",
      pick_drawing_pages(lengths_227312, 4), [2, 3, 4, 5])
check("background art is detected on sparse pages only",
      F.background_art_pages({1: 5000, 2: 80, 3: 90},
                             {1: "the prior art teaches", 2: "FIG. 1\nPRIOR ART", 3: "FIG. 2"}),
      {2})
check("related-art wording is detected too",
      F.background_art_pages({2: 80}, {2: "FIG. 1 Related Art"}), {2})

check("page list and ranges", F.parse_pages("6,10-12"), [6, 10, 11, 12])
check("page list drops duplicates", F.parse_pages("3, 3-4"), [3, 4])
check("rotation words map to PIL's counter-clockwise degrees",
      F.parse_rotate("12:cw,13:ccw,14:180"), {12: -90, 13: 90, 14: 180})
for bad, fn in (("0", F.parse_pages), ("5-2", F.parse_pages), ("x", F.parse_pages),
                ("12", F.parse_rotate), ("12:90", F.parse_rotate)):
    try:
        fn(bad)
        check("rejects malformed %r" % bad, "no exception raised", "ValueError")
    except ValueError:
        print("PASS  rejects malformed %r" % bad)

# --- image handling and an end-to-end run on generated PDFs ------------------
#
# The PDFs are generated here, not downloaded, so this runs offline. A
# PIL-saved PDF has no text layer (the "pure image scan" shape); a hand-written
# one has real text, which is what the prior-art detection needs.

import shutil  # noqa: E402

try:
    from PIL import Image, ImageDraw  # noqa: E402
    HAVE_IMAGING = shutil.which("pdftoppm") and shutil.which("pdftotext")
except ImportError:
    HAVE_IMAGING = False

if not HAVE_IMAGING:
    print("SKIP  image and end-to-end checks (Pillow and poppler-utils needed)")
else:
    def drawing_sheet(size=(800, 1000), specks=True, sideways=False):
        """A white page with a drawing, optional scan dust in the margins."""
        im = Image.new("L", size, 255)
        d = ImageDraw.Draw(im)
        d.rectangle((200, 300, 600, 600), outline=0, width=3)
        d.line((400, 100, 400, 800), fill=0, width=2)      # long thin line
        d.text((350, 850), "FIG. 1", fill=0)
        if specks:
            for x, y in ((20, 20), (780, 15), (30, 980), (770, 990), (15, 500)):
                d.ellipse((x, y, x + 4, y + 4), fill=0)
        return im.rotate(90, expand=True) if sideways else im

    # Specks must not stretch the crop box; the long thin line must survive.
    with tempfile.TemporaryDirectory() as td:
        clean_path = os.path.join(td, "clean.png")
        dusty_path = os.path.join(td, "dusty.png")
        drawing_sheet(specks=False).save(clean_path)
        drawing_sheet(specks=True).save(dusty_path)
        clean = F.crop_sheet(clean_path, strip_header=False)
        dusty = F.crop_sheet(dusty_path, strip_header=False)
        check("scan specks do not change the crop", dusty.size, clean.size)
        check("the long thin line is not mistaken for dust (height kept)",
              dusty.size[1] > 700, True)
        turned = F.crop_sheet(clean_path, strip_header=False, rotate=F.ROTATIONS["cw"])
        check("rotate turns the sheet (width and height swap)",
              (turned.size[0] > turned.size[1]), True)

    def write_text_pdf(path, pages):
        """Minimal PDF, one text string per page, with a rectangle so the
        page renders to something. Offsets are computed, so poppler reads it
        without repair."""
        objs = ["<< /Type /Catalog /Pages 2 0 R >>", None]
        kids = []
        for text in pages:
            page_id = len(objs) + 1
            kids.append("%d 0 R" % page_id)
            lines = text if isinstance(text, list) else [text]
            stream = "BT /F1 12 Tf 50 750 Td 14 TL " + " ".join(
                "(%s) Tj T*" % ln for ln in lines) + " ET 100 300 300 200 re S"
            objs.append("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                        "/Contents %d 0 R /Resources << /Font << /F1 << /Type /Font "
                        "/Subtype /Type1 /BaseFont /Helvetica >> >> >> >>" % (page_id + 1))
            objs.append("<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream))
        objs[1] = "<< /Type /Pages /Kids [%s] /Count %d >>" % (" ".join(kids), len(pages))
        out, offsets = b"%PDF-1.4\n", []
        for i, body in enumerate(objs, 1):
            offsets.append(len(out))
            out += ("%d 0 obj\n%s\nendobj\n" % (i, body)).encode()
        xref = len(out)
        out += ("xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)).encode()
        out += b"".join(("%010d 00000 n \n" % o).encode() for o in offsets)
        out += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(objs) + 1, xref)).encode()
        open(path, "wb").write(out)

    front = ["Front page line %d of the bibliographic page" % i for i in range(60)]
    with tempfile.TemporaryDirectory() as td:
        pdf = os.path.join(td, "doc.pdf")
        write_text_pdf(pdf, [front, "FIG. 1 PRIOR ART", "FIG. 2 PRIOR ART",
                             "FIG. 3", "FIG. 4"])
        out = os.path.join(td, "out")
        canonical, made = F.process("US9999999B2", out, 2, True, local_pdf=pdf)
        names = sorted(os.listdir(out))
        check("end to end: prior-art sheets 2-3 are skipped; candidates are 4 and 5",
              [n for n in names if "__cand" in n],
              ["US9999999B2__cand1_p4.png", "US9999999B2__cand2_p5.png"])
        check("end to end: a contact sheet and report are written",
              ("US9999999B2__contact.png" in names, "US9999999B2.report.txt" in names),
              (True, True))
        report = open(os.path.join(out, "US9999999B2.report.txt")).read()
        check("report names the prior-art sheets", "prior art / background art" in report
              and "[2, 3]" in report, True)

        out2 = os.path.join(td, "out2")
        F.process("US9999999B2", out2, 2, True, local_pdf=pdf, pages=[3],
                  rotations={3: F.ROTATIONS["cw"]})
        check("--pages picks exactly the named sheet",
              [n for n in os.listdir(out2) if "__cand" in n], ["US9999999B2__cand1_p3.png"])
        try:
            F.process("US9999999B2", os.path.join(td, "out3"), 2, True,
                      local_pdf=pdf, pages=[99])
            check("--pages beyond the PDF is rejected", "no exception raised", "RuntimeError")
        except RuntimeError:
            print("PASS  --pages beyond the PDF is rejected")

        # An image-only scan: every page extracts 0 chars. Specks everywhere.
        scan = os.path.join(td, "scan.pdf")
        sheets = [drawing_sheet(specks=True) for _ in range(6)]
        sheets[0].save(scan, save_all=True, append_images=sheets[1:])
        out4 = os.path.join(td, "out4")
        F.process("US8888888A", out4, 3, True, local_pdf=scan)
        check("image-only scan: page 1 skipped, pages in order",
              [n for n in sorted(os.listdir(out4)) if "__cand" in n],
              ["US8888888A__cand1_p2.png", "US8888888A__cand2_p3.png",
               "US8888888A__cand3_p4.png"])
        report = open(os.path.join(out4, "US8888888A.report.txt")).read()
        check("image-only scan: report says the ranking is a guess",
              "NO TEXT LAYER: sheets are listed in page order only" in report, True)
        contact = Image.open(os.path.join(out4, "US8888888A__contact.png"))
        check("contact sheet covers every drawing sheet (5 sheets, 4 columns, 2 rows)",
              contact.size, (F.CONTACT_CELL[0] * F.CONTACT_COLS, F.CONTACT_CELL[1] * 2))

print()
if FAILURES:
    print("%d FAILURE(S): %s" % (len(FAILURES), ", ".join(FAILURES)))
    sys.exit(1)
print("all checks passed")
