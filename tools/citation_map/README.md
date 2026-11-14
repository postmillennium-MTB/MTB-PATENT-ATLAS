# Citation map tooling

Rebuilds `citations/index.html`, the Patent Citation Map: Atlas cards joined
by the citations listed on each patent's Google Patents page. Nothing here is
loaded by `index.html`.

The page's data block is a snapshot. Rebuild it after a batch of new cards if
the map should show them. Run every step from this folder; the steps write
their working files (`atlas.json`, `raw/`, `pages.json`, `graph.json`,
`data.json`) next to the scripts, and `.gitignore` keeps them out of the repo.

```bash
cd tools/citation_map
node extract.js        # reads D from ../../index.html -> atlas.json (cards, refs, Google Patents ids)
python3 fetch.py       # downloads each patent's Google Patents page into raw/ (2 at a time; reruns skip what it has)
python3 parse.py       # reads the "Patent citations" and "Cited by" tables -> pages.json
python3 graph.py       # card-to-card links + outside patents -> graph.json (prints the rankings)
python3 build_data.py  # -> data.json, the block the page embeds
python3 build.py       # fills src.html -> ../../citations/index.html
```

Notes

- `fetch.py` needs `patents.google.com` to be reachable. It was from a cloud
  session on 2026-11-13; if it is blocked, run the steps on a machine where it
  is not. Never fill a gap by hand.
- A link is "exact" when the cited publication is the card's own patent (or
  another publication of the same application), and "family" when it is a
  relative in the same patent family. The page draws family links dashed.
- `parse.py` holds two number fixes for the PI ROPE cards, whose German
  numbers are stored as bare digits (`FIX`). Add to it if another card's
  number does not resolve on Google Patents.
- Edit the page in `src.html`, not in `citations/index.html`, then run
  `build.py`. `build_data.py` sets the "read on" date by hand (`date=`).
