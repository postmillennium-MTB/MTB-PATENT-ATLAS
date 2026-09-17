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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_patent_figure import pick_drawing_pages, parse_number  # noqa: E402

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

try:
    parse_number("not-a-patent")
    check("garbage input is rejected", "no exception raised", "ValueError")
except ValueError:
    print("PASS  garbage input is rejected")

print()
if FAILURES:
    print("%d FAILURE(S): %s" % (len(FAILURES), ", ".join(FAILURES)))
    sys.exit(1)
print("all checks passed")
