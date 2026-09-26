#!/usr/bin/env python3
"""Self-test for fetch_patent_figure.py. No dependencies, no network.

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

print()
if FAILURES:
    print("%d FAILURE(S): %s" % (len(FAILURES), ", ".join(FAILURES)))
    sys.exit(1)
print("all checks passed")
