# Card checklist

One page to check a new or edited card against. Each line points to where the
full rule lives (`docs/reference.md` section names) for the rare case that
needs it. Rules marked **(checked)** fail `node tools/verify_data.js` when
broken, so you don't have to police them by eye.

## Facts

- [ ] Number, dates, inventors, assignee come from the record (`*.details.md`
      from the figure workflow, or the Google Patents page). Never invent one;
      an honest `num: null` + `conf: "l"` beats a guess.
- [ ] Duplicate check: `node tools/entry.js find <number> <brand> <keyword>`.
      A match on a `num: null` placeholder means fill that card, not a new one.
- [ ] `exp` from `node tools/patent_term.js --filed … --granted … [--pta N] [--design]`,
      using the **earliest non-provisional US filing** (continuations inherit
      the parent's date). A fee lapse ("Expired - Fee Related") ends it early:
      `st: "expired"`, and say so in `s`. Pre-1982 design patents: read the term
      off the record.
- [ ] `st` matches the record's legal status. `conf`: `v` verified against the
      record, `m` story solid but number unconfirmed, `l` draft. Never upgrade
      a tier to look complete.
- [ ] `num` format: plain digits, no "US", no commas. Design: bare digits +
      `pt: "design"` (inside `nums[]` it carries its own `D`). Foreign keeps its
      prefix (`EP3111109`) and sets `j`. EU RCDs and pre-1916 British patents:
      `num: null`, number in `s`.
- [ ] **No patent?** Two cases. Not located: `num: null`, no `np`. Confirmed
      none (maker, inventor, open-standard text, trademark, stated trade
      secret): `np: true|"trademark"|"standard"|"secret"`, `g/exp: null`,
      `st: "unknown"`, `y` = introduction year, no "(no patent)" in the title (the pill says it).
      "Our searches found nothing" is the first case. **(checked)**
- [ ] **Family** (README "Patent families and continuations"): every member
      looked up and run through `find`. One card per family unless a member
      is a CIP, claims a different product, was litigated/licensed/sold on its
      own, or has its own story. `num` = parent or best-matching granted
      member (not simply the newest). `nums[]` = headline first, granted and
      pending US members, one granted foreign counterpart per office; no
      pre-grant publication of a granted application, no abandoned
      applications (name those in `s`). `exp` = latest expiry of a granted
      member in force; `s` says which member ends when if they differ.
- [ ] New `who[]` names registered in `BRANDS` / `INVENTORS` first. **(checked)**
      Inventors only for recurring, notable people.

## Title

- [ ] **Brand first** when there is one brand: "Shimano Ice Tech clad disc brake
      rotor (US 9,234,553)". Skip for a lone inventor, a historical patent, a
      multi-brand technology (Horst Link, VPP) or a lawsuit. French brand-first
      too. `verify_data.js` lists titles that don't start with a `who[]` name.
- [ ] Headline number in the title: `(US 1,234,567)` / `(US 1 234 567)`.
- [ ] Renamed title or new number on an existing card changes its link: add
      `REF_ALIASES` `"old-ref":"new-ref"`. **(checked for dead targets)**

## Text (EN + FR, every field)

- [ ] Every text field is `{en, fr}`, both written now. Proper nouns, brand
      names and quoted patent titles stay untranslated in French.
- [ ] `s`: what it covers, filing/grant history, the mechanism in concrete
      terms. `w`: why a rider, mechanic or advocate should care. Jon's own
      voice in `w` only when he gives it.
- [ ] `hook`: one-line opener from this card's own `s`/`w`, EN ≤ 120, FR ≤ 140. **(checked)**
- [ ] `clever`: one sentence on how the mechanism works, EN ≤ 200, FR ≤ 240,
      no markup. Not for lawsuits, design patents or company-history cards. **(checked)**
- [ ] **No process narration.** State the fact or the gap as a fact about the
      record. Banned: "this pass", "this session", "was/were not read",
      "front page was read", "the user", "our search", "web search",
      "search snippet", "independently confirmed". **(checked)**
- [ ] **No investment language**: "moat", "investment thesis", "investors
      should". **(checked)**
- [ ] No hedge-stacking ("likely may plausibly"), no restating a caveat in
      both `s` and `w`, no comments about the Atlas itself.
- [ ] Links: `[[card:<ref>|text]]` to another card (never to a `num: null`
      card, except a confirmed no-patent `np` card by its title slug), `[[link:https://…|text]]` outside. **(checked)**

## Drawings

- [ ] `node tools/entry.js pics <number>` for **every** number on the card, after
      syncing with `main`: Jon often uploads extra sheets (`.1.png`, `.2.png`),
      and may name them after any family member.
- [ ] Family drawings: continuations share the parent's drawings, so each
      figure goes on once. Keep the file named for the document it came from
      and caption it "Fig. N from US x,xxx,xxx".
- [ ] `imgs[]` order: the most recognisable figure first (it becomes the
      thumbnail everywhere). Each has `alt` (what is drawn, with its reference
      numerals) and `caption`, both languages.
- [ ] Non-patent image: caption ends "— not a patent drawing", `"link": false`.
- [ ] `python3 tools/make_thumbs.py pictures/<file>` for each new first drawing.
- [ ] If the thumbnail shows a printed date or patent number, add the file stem
      to `GAME_HIDDEN_DRAWINGS`.

## Before the PR

- [ ] `node tools/sync_counts.js` (all hand-written counts) **(checked)**
- [ ] `node tools/verify_data.js` and `node tools/smoke_test.js`
- [ ] README "Recent updates" bullet: what was added, tier, any gap.
      `WHATS_NEW` line if readers would notice.
- [ ] PR, not a push to `main`; Jon merges.
