#!/usr/bin/env python3
"""Rotate a drawing in pictures/ and rebuild its thumbnail.

    python3 tools/rotate_picture.py pictures/US1234567A.png          # 90 degrees clockwise
    python3 tools/rotate_picture.py pictures/US1234567A.png --ccw    # 90 degrees counter-clockwise
    python3 tools/rotate_picture.py pictures/US1234567A.png --180

Patent sheets often arrive sideways: the printed header ("Patented ... Sheet 1")
runs up or down the edge instead of across the top. Look at every new drawing
before it goes on a card; if the figure lies on its side, run this. The usual
fix is clockwise. The file is overwritten in place, so check the result by eye.
Pillow only; thumbnails come from tools/make_thumbs.py.
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

REPO = Path(__file__).resolve().parent.parent


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if not args or flags - {"--ccw", "--180"}:
        print(__doc__)
        return 2
    angle = -90 if not flags else (90 if "--ccw" in flags else 180)  # PIL: positive = counter-clockwise
    for name in args:
        path = Path(name)
        img = ImageOps.exif_transpose(Image.open(path))
        img.load()
        out = img.rotate(angle, expand=True)
        out.save(path)
        print(f"rotated {path} ({img.size[0]}x{img.size[1]} -> {out.size[0]}x{out.size[1]})")
        subprocess.run([sys.executable, str(REPO / "tools" / "make_thumbs.py"), str(path)], check=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
