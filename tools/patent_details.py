#!/usr/bin/env python3
"""
Collect the facts a new Atlas card needs from each patent's Google Patents
page, so a session doesn't have to web-search for them or read the 2 MB
index.html to check for duplicates.

For each number it writes, into --out (default figures-out/):
  <canonical>.details.md    readable summary: title, inventors, assignees,
                            application number, priority / filing / publication
                            / grant dates, legal status, Google's expiry date,
                            the PTA days from the front page (when the figure
                            fetch left a report.txt beside it), the expiry the
                            Atlas rule gives (tools/patent_term.js), family
                            members, and which cited / citing patents are
                            already Atlas cards
  <canonical>.details.json  the same, for scripts
  <canonical>.card.json     a draft card with only the record's facts filled
                            in (y, g, a, num, st, exp, pt, j). Prose, cat, who,
                            conf, hook, clever and images are left as TODO:
                            those are editorial.

Runs in the "Fetch patent figure" workflow (GitHub's runners can reach
patents.google.com; the cloud sandbox can't). It never fails that run: a page
it can't fetch or parse is reported in the summary, not guessed at.

USAGE
  python3 tools/patent_details.py US9422993B2 4733881 --out figures-out
  python3 tools/patent_details.py US9422993B2 --html saved_page.html   # offline / tests
"""
import argparse
import html as H
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_patent_figure import parse_number, KIND_CODE_FALLBACKS, USER_AGENT  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = "https://patents.google.com/patent/{full}/en"


def clean(s):
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def fetch_page(canonical):
    tries = [canonical]
    if not re.search(r"[A-Z]\d?$", canonical[2:]):
        tries += [canonical + k for k in KIND_CODE_FALLBACKS]
    for full in tries:
        try:
            req = urllib.request.Request(PAGE.format(full=full), headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = r.read().decode("utf-8", "replace")
            if len(body) > 20000:
                return full, body
        except Exception:
            pass
        time.sleep(0.5)
    return None, None


def metas(h, name, scheme=None):
    out = []
    for m in re.finditer(r"<meta\s+name=\"%s\"([^>]*)>" % re.escape(name), h):
        attrs = m.group(1)
        c = re.search(r'content="([^"]*)"', attrs)
        s = re.search(r'scheme="([^"]*)"', attrs)
        if c and (scheme is None or (s and s.group(1) == scheme)):
            out.append(clean(c.group(1)))
    return out


def props(h, name):
    return [clean(m.group(1)) for m in re.finditer(r'itemprop="%s"[^>]*>(.*?)</(?:dd|span|td|time|div)>' % name, h, re.S)]


def first(xs):
    return xs[0] if xs else ""


def rows(h, prop):
    out = []
    for m in re.finditer(r'<tr itemprop="%s" itemscope repeat>(.*?)</tr>' % prop, h, re.S):
        r = m.group(1)
        pn = re.search(r'itemprop="(?:publicationNumber|representativePublication)">([^<]+)<', r)
        if pn:
            t = re.search(r'itemprop="title"[^>]*>(.*?)</', r, re.S)
            out.append({"pn": pn.group(1).strip(), "title": clean(t.group(1)) if t else ""})
    return out


def events(h):
    out = []
    for m in re.finditer(r'<dd itemprop="events" itemscope repeat>(.*?)</dd>', h, re.S):
        e = m.group(1)
        d = re.search(r'datetime="([^"]+)"', e)
        t = re.search(r'itemprop="title"[^>]*>(.*?)</', e, re.S)
        ty = re.search(r'itemprop="type"[^>]*>(.*?)</', e, re.S)
        out.append({"date": d.group(1) if d else "", "type": clean(ty.group(1)) if ty else "",
                    "title": clean(t.group(1)) if t else ""})
    return out


def atlas_index():
    """num -> card title, from D (one JSON object per line in index.html)."""
    idx = {}
    try:
        lines = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read().split("\n")
        s = lines.index("const D = [")
    except Exception:
        return idx
    for line in lines[s + 1:]:
        if line == "];":
            break
        try:
            d = json.loads(line.strip().rstrip(","))
        except Exception:
            continue
        title = (d.get("t") or {}).get("en", "") if isinstance(d.get("t"), dict) else d.get("t", "")
        nums = [("D" + d["num"]) if d.get("pt") == "design" and d.get("num") else d.get("num")]
        for n in nums + (d.get("nums") or []):
            if n:
                idx[str(n)] = title
    return idx


def atlas_key(pn):
    """US9422993B2 -> 9422993; USD236609S -> D236609; EP1234567B1 -> EP1234567."""
    p = pn.replace(" ", "").upper()
    m = re.match(r"^US(RE|D|PP)?(\d+)[A-Z]?\d?$", p)
    if m:
        pre, digits = m.group(1) or "", m.group(2)
        if not pre and len(digits) == 11:   # published application, 20190136918
            return digits
        return pre + digits.lstrip("0")
    m = re.match(r"^([A-Z]{2,3}\d+)", p)
    return m.group(1) if m else p


def pta_days(outdir, canonical):
    for f in os.listdir(outdir) if os.path.isdir(outdir) else []:
        if f.startswith(canonical[:-2] if re.search(r"[A-Z]\d$", canonical) else canonical) and f.endswith(".report.txt"):
            t = open(os.path.join(outdir, f), encoding="utf-8", errors="replace").read()
            m = re.search(r"(?:extended|adjusted)\s+under\s+35\s+U\.?S\.?C\.?\s*154\s*\(b\)\s*by\s*(\d+)\s*days", t, re.I | re.S)
            if m:
                return int(m.group(1))
            if re.search(r"154\s*\(b\)\s*by\s*0\s*days", t):
                return 0
    return None


def term(filed, granted, design, pta):
    args = ["node", os.path.join(ROOT, "tools", "patent_term.js"), "--filed", filed]
    if granted:
        args += ["--granted", granted]
    if design:
        args.append("--design")
    if pta:
        args += ["--pta", str(pta)]
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=30).stdout.strip()
    except Exception as e:
        return "(patent_term.js not run: %s)" % e


def parse(h, full):
    ev = events(h)
    grant = first(metas(h, "DC.date", "issued")) or next((e["date"] for e in ev if "granted" in e["title"].lower() or e["type"] == "granted"), "")
    exp_ev = [e for e in ev if "expiration" in e["title"].lower() or "expir" in e["type"].lower() or "lapsed" in e["title"].lower()]
    return {
        "number": full,
        "title": first(metas(h, "DC.title")),
        "inventors": metas(h, "DC.contributor", "inventor") or props(h, "inventor"),
        "assignee_original": props(h, "assigneeOriginal") or metas(h, "DC.contributor", "assignee"),
        "assignee_current": props(h, "assigneeCurrent"),
        "application": first(props(h, "applicationNumber")),
        "priority_date": first(props(h, "priorityDate")),
        "filing_date": first(props(h, "filingDate")) or first(metas(h, "DC.date", "dateSubmitted")),
        "publication_date": first(props(h, "publicationDate")),
        "grant_date": grant,
        "status": first(props(h, "status")),
        "expiry_events": exp_ev,
        "abstract": first(metas(h, "description"))[:1200],
        "family": sorted({r["pn"] for r in rows(h, "docdbFamily")} | {r["pn"] for r in rows(h, "applications")}),
        "cites": rows(h, "backwardReferencesOrig") or rows(h, "backwardReferences"),
        "cited_by": rows(h, "forwardReferencesOrig") or rows(h, "forwardReferences"),
        "events": ev,
    }


def summarize(d, idx, pta):
    design = d["number"].upper().startswith("USD")
    us = d["number"].upper().startswith("US")
    y = lambda s: int(s[:4]) if s and s[:4].isdigit() else None
    rule = term(d["filing_date"], d["grant_date"], design, pta) if us and d["filing_date"] else "(non-US or no filing date: check the national rule)"
    m = re.match(r"exp: (\d{4})", rule)
    exp = int(m.group(1)) if m else None
    status = d["status"].lower()
    st = "pending" if "pending" in status else "expired" if ("expired" in status or "lapsed" in status or "ceased" in status) else "active" if "active" in status else "unknown"
    key = atlas_key(d["number"])
    in_atlas = lambda rs: [dict(r, card=idx[atlas_key(r["pn"])]) for r in rs if atlas_key(r["pn"]) in idx]
    card = {
        "y": y(d["filing_date"]), "g": y(d["grant_date"]),
        "t": {"en": "TODO Brand-first title (%s)" % d["number"], "fr": "TODO"},
        "a": " / ".join(filter(None, [", ".join(d["inventors"]), ", ".join(d["assignee_current"] or d["assignee_original"])])),
        "num": key.lstrip("D") if design else key, "cat": "TODO", "st": st, "exp": exp,
        "b": [], "who": [], "conf": "v",
        "hook": {"en": "TODO", "fr": "TODO"}, "clever": {"en": "TODO", "fr": "TODO"},
        "s": {"en": "TODO", "fr": "TODO"}, "w": {"en": "TODO", "fr": "TODO"},
    }
    if design:
        card["pt"] = "design"
    if not us:
        card["j"] = re.match(r"^[A-Z]{2}", d["number"]).group(0)
    lines = [
        "# %s — %s" % (d["number"], d["title"]),
        "",
        "Already in the Atlas: **%s**" % (idx[key] if key in idx else "no"),
        "",
        "| | |", "|---|---|",
        "| Inventors | %s |" % ", ".join(d["inventors"]),
        "| Assignee (original) | %s |" % ", ".join(d["assignee_original"]),
        "| Assignee (current) | %s |" % ", ".join(d["assignee_current"]),
        "| Application | %s |" % d["application"],
        "| Priority date | %s |" % d["priority_date"],
        "| Filed | %s |" % d["filing_date"],
        "| Published | %s |" % d["publication_date"],
        "| Granted | %s |" % (d["grant_date"] or "not granted"),
        "| Legal status | %s |" % d["status"],
        "| Google's expiry line | %s |" % "; ".join("%s %s" % (e["date"], e["title"]) for e in d["expiry_events"]),
        "| PTA (front page) | %s |" % ("%d days" % pta if pta is not None else "not found (no report.txt, or none printed)"),
        "| Atlas rule | %s |" % rule,
        "",
    ] + ([
        "**Check:** the record says expired, but the full term runs to %d, so it lapsed early (usually unpaid fees). The card's `st` is expired; keep `exp` as the term or set it to the lapse year, and say which in `s`." % exp,
        "",
    ] if st == "expired" and exp and exp > time.gmtime().tm_year else []) + [
        "If this is a continuation or divisional, the clock runs from the parent's filing date:",
        "rerun `node tools/patent_term.js --filed <parent date> --granted %s`." % (d["grant_date"] or "<date>"),
        "",
        "**Abstract:** %s" % d["abstract"],
        "",
        "**Family:** %s" % (", ".join(d["family"]) or "none listed"),
        "",
        "**Cites, already Atlas cards:** %s" % ("; ".join("%s (%s)" % (r["pn"], r["card"]) for r in in_atlas(d["cites"])) or "none"),
        "",
        "**Cited by, already Atlas cards:** %s" % ("; ".join("%s (%s)" % (r["pn"], r["card"]) for r in in_atlas(d["cited_by"])) or "none"),
        "",
        "Counts: cites %d, cited by %d." % (len(d["cites"]), len(d["cited_by"])),
    ]
    return "\n".join(lines) + "\n", card


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("numbers", nargs="+")
    ap.add_argument("--out", default="figures-out")
    ap.add_argument("--html", help="parse this saved page instead of fetching (one number only)")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    idx = atlas_index()
    failed = []
    for raw in a.numbers:
        try:
            _, canonical = parse_number(raw)
        except ValueError as e:
            print("  %s: %s" % (raw, e)); failed.append(raw); continue
        if a.html:
            full, h = canonical, open(a.html, encoding="utf-8", errors="replace").read()
        else:
            full, h = fetch_page(canonical)
        if not h:
            print("  %s: Google Patents page not reachable; no details written" % canonical)
            failed.append(raw); continue
        d = parse(h, full)
        md, card = summarize(d, idx, pta_days(a.out, canonical))
        base = os.path.join(a.out, full)
        open(base + ".details.md", "w", encoding="utf-8").write(md)
        json.dump(d, open(base + ".details.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        json.dump(card, open(base + ".card.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print("  wrote %s.details.md, .details.json, .card.json" % base)
    if failed:
        print("details missing for: %s" % " ".join(failed))
    return 0  # never fail the figure run over details


if __name__ == "__main__":
    sys.exit(main())
