#!/usr/bin/env python3
"""Make card thumbnails from the first drawing of every atlas entry.

The atlas shows the first drawing of each entry as a small picture on its card
(grid / plate / tinted views). The full drawings are 150 KB on average and up
to 2.8 MB, so a list of 300 cards cannot load them directly; this writes a
small copy of each into pictures/thumbs/.

    python3 tools/make_thumbs.py            # make any thumbnail that is missing or out of date
    python3 tools/make_thumbs.py --force    # remake every thumbnail
    python3 tools/make_thumbs.py pictures/US5509679A.png ...   # just these sources

Naming (index.html's thumbSrc() must agree with this, byte for byte):
    pictures/<name>.<ext>  ->  pictures/thumbs/<name>.webp
where <name> is the percent-decoded file name without its extension.

What it does to each drawing:
  1. Flattens transparency onto white.
  2. Removes the "U.S. Patent / Sheet n of m / patent number" header band when
     one is detected (see find_header_band for the exact rule). Older sheets
     carry it and it is unreadable noise at 100 px.
  3. Trims the white margin, so the drawing fills the thumbnail instead of
     sitting in a sea of paper.
  4. Pads a little, scales to fit THUMB_MAX px on the long side, saves WebP.

Not handled on purpose: choosing a better sheet. If an entry's first drawing
is a poor thumbnail (a whole-page scan, say), the fix is editorial -- reorder
the entry's imgs[] -- not a crop rule here.

Requires Pillow and Node (Node only to read which images are first drawings,
via tools/first_images.js).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

from PIL import Image, ImageChops

REPO = Path(__file__).resolve().parent.parent
THUMB_DIR = REPO / "pictures" / "thumbs"

# Long side of a thumbnail, px. The largest slot is a grid tile ~200 CSS px
# wide, and 2x covers retina screens. Raise it only together with the slot
# sizes in index.html's CSS; a bigger thumbnail costs every list view.
THUMB_MAX = 400
WEBP_QUALITY = 80

# Pixels at or above this grey level count as paper. Patent scans are not
# pure white, so this is lower than 255.
PAPER_LEVEL = 228
# Ignore rows/columns whose ink share is below this: scanner specks, edge
# shadows.
INK_NOISE = 0.002
# Share of the long side kept as margin around the trimmed drawing.
PAD_FRACTION = 0.05

# --- header band detection (see find_header_band) ---
HEADER_SEARCH = 0.16      # the band must start within this share of the height
HEADER_MAX_HEIGHT = 0.07  # ...and be no taller than this share
HEADER_GAP = 0.010        # blank rows (share of height) that end the band
HEADER_MIN_WIDTH = 0.55   # band must span this share of the drawing's width
HEADER_MIN_CLUSTERS = 3   # left / centre / right text blocks, as on a real header
CLUSTER_GAP = 0.03        # blank columns (share of width) that split text blocks


def ink_profile(img, axis):
    """Share of dark pixels per row (axis 0) or per column (axis 1)."""
    bw = img.convert("L").point(lambda p: 255 if p < PAPER_LEVEL else 0)
    w, h = bw.size
    small = bw.resize((1, h) if axis == 0 else (w, 1), Image.BOX)
    return [v / 255 for v in small.tobytes()]


def runs(flags):
    """[(start, end_exclusive)] for each run of True in flags."""
    out, start = [], None
    for i, f in enumerate(flags):
        if f and start is None:
            start = i
        elif not f and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(flags)))
    return out


def find_header_band(img):
    """Return the y where real drawing content starts if a patent header band
    sits above it, else 0.

    A header is a thin strip of small text at the very top, spanning most of the
    sheet's width in several separate blocks ("U.S. Patent" at left, the date and
    "Sheet 1 of 3" in the middle, the patent number at right), followed by a clear
    gap and then the drawing. A "FIG. 1" label above a drawing is one narrow
    block, so it fails the width and cluster tests and is left alone.
    """
    w, h = img.size
    rows = ink_profile(img, 0)
    inked = [r > INK_NOISE for r in rows]
    ink_runs = runs(inked)
    if len(ink_runs) < 2:
        return 0
    first = ink_runs[0]
    # The band is the first inked run; the next inked run is the drawing.
    if first[0] > h * HEADER_SEARCH or (first[1] - first[0]) > h * HEADER_MAX_HEIGHT:
        return 0
    nxt = ink_runs[1]
    if (nxt[0] - first[1]) < h * HEADER_GAP:
        return 0
    band = img.crop((0, first[0], w, first[1]))
    cols = ink_profile(band, 1)
    col_inked = [c > INK_NOISE for c in cols]
    spans = runs(col_inked)
    if not spans:
        return 0
    # Merge blocks closer together than CLUSTER_GAP (letters in one phrase).
    merged = [list(spans[0])]
    for s, e in spans[1:]:
        if s - merged[-1][1] < w * CLUSTER_GAP:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    # Width is measured against the sheet's own drawn width, not the file's.
    full_cols = ink_profile(img, 1)
    full_spans = runs([c > INK_NOISE for c in full_cols])
    content_w = (full_spans[-1][1] - full_spans[0][0]) if full_spans else w
    band_w = merged[-1][1] - merged[0][0]
    if len(merged) >= HEADER_MIN_CLUSTERS and band_w >= content_w * HEADER_MIN_WIDTH:
        return nxt[0]
    return 0


def trim(img):
    """Crop to the inked area, then pad."""
    mask = img.convert("L").point(lambda p: 255 if p < PAPER_LEVEL else 0)
    box = mask.getbbox()
    if box:
        img = img.crop(box)
    w, h = img.size
    m = int(max(w, h) * PAD_FRACTION)
    out = Image.new("RGB", (w + 2 * m, h + 2 * m), (255, 255, 255))
    out.paste(img, (m, m))
    return out


def flatten(img):
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        bg.alpha_composite(img)
        img = bg
    return img.convert("RGB")


def thumb_path(src):
    """pictures/<name>.<ext> (possibly percent-encoded) -> pictures/thumbs/<name>.webp"""
    name = unquote(src).split("/")[-1]
    stem = name.rsplit(".", 1)[0]
    return THUMB_DIR / (stem + ".webp")


def make(src, force):
    source = REPO / unquote(src)
    dest = thumb_path(src)
    if not source.exists():
        return "missing", None
    if dest.exists() and not force and dest.stat().st_mtime >= source.stat().st_mtime:
        return "current", None
    img = flatten(Image.open(source))
    y = find_header_band(img)
    note = None
    if y:
        img = img.crop((0, y, img.size[0], img.size[1]))
        note = "header cropped"
    img = trim(img)
    img.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "WEBP", quality=WEBP_QUALITY, method=6)
    return "made", note


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sources", nargs="*", help="pictures/... paths; default: every entry's first drawing")
    ap.add_argument("--force", action="store_true", help="remake thumbnails that are already current")
    args = ap.parse_args()

    if args.sources:
        sources = args.sources
    else:
        res = subprocess.run(["node", str(REPO / "tools" / "first_images.js")],
                             capture_output=True, text=True, check=True)
        sources = json.loads(res.stdout)

    # Two sources must never map to one thumbnail: the later would silently
    # overwrite the earlier and a card would show another patent's drawing.
    seen = {}
    for s in sources:
        p = thumb_path(s)
        if p in seen and seen[p] != s:
            sys.exit(f"::error::{seen[p]} and {s} both map to {p.name}")
        seen[p] = s

    counts = {"made": 0, "current": 0, "missing": 0}
    for s in sources:
        status, note = make(s, args.force)
        counts[status] += 1
        if status == "missing":
            print(f"::warning::{s} is referenced by an entry but not in the repo")
        elif note:
            print(f"{s}: {note}")
    print(f"thumbnails: {counts['made']} made, {counts['current']} already current, "
          f"{counts['missing']} source file(s) missing")


if __name__ == "__main__":
    main()
