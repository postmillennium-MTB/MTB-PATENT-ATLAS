"""Rewrite the `const CITE_MAP = {...};` line in ../../index.html from data.json.

That line is the snapshot the Atlas's citation tab (renderCite()) draws. Run it
after build_data.py, from this folder:  python3 update_atlas_tab.py
It changes that one line and nothing else; titles, categories and years are
read live from D by card ref, so only refs, links and outside patents live here.
"""
import json, os, re
here = os.path.dirname(os.path.abspath(__file__))
page = os.path.join(here, '..', '..', 'index.html')
d = json.load(open(os.path.join(here, 'data.json')))
m = d['meta']
cm = dict(read=m['date'], fetched=m['fetched'], numbers=m['numbers'], nocit=m['nocit'], extMin=m['extMin'],
          nodes=[n['ref'] for n in d['nodes']], edges=d['edges'],
          ext=[dict(pn=x['pn'], t=x['t'], a=x['a'], y=x['y'], k=x['k'], c=x['c']) for x in d['ext']])
line = 'const CITE_MAP = ' + json.dumps(cm, ensure_ascii=False, separators=(',', ':')) + ';'
s = open(page, encoding='utf-8').read()
found = re.findall(r'^const CITE_MAP = .*;$', s, flags=re.M)
assert len(found) == 1, 'expected exactly one CITE_MAP line, found %d' % len(found)
s = s.replace(found[0], line)
open(page, 'w', encoding='utf-8').write(s)
print('CITE_MAP: %d cards, %d links, %d outside patents, read %s' % (len(cm['nodes']), len(cm['edges']), len(cm['ext']), cm['read']))
