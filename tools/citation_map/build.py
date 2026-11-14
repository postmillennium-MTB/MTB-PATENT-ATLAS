"""Fill src.html's /*DATA*/ slot with data.json and write the standalone page
to citations/index.html (two folders up). Run from this folder after
build_data.py."""
import os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'src.html')).read().replace('/*DATA*/', open('data.json').read())
head, body = src.split('<!--BODY-->')
head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
full = ('<!DOCTYPE html>\n<!-- (c) 2026 Post Millennium Renaissance (https://www.postmillenniumrenaissance.com/). '
        'SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0. See LICENSE. -->\n<html lang="en">\n<head>\n'
        '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        + head + '</head>\n<body>\n' + body + '</body>\n</html>\n')
out = os.path.join(here, '..', '..', 'citations', 'index.html')
open(out, 'w').write(full)
print('wrote', os.path.normpath(out))
