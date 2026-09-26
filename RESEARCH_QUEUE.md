# Research Queue — Candidate Patent Entries

Not yet added to `index.html`. This is a holding pen for candidates Jon
supplied on 2026-09-26, pending verification per CLAUDE.md's sourcing
discipline (web-search confirmation, primary-source check, resolvable
links, honest `conf` tiering) before any of them become real `D` entries.
No code or dataset changes have been made — this file is notes only.

Every patent number below is **as submitted, unverified**. Do not treat any
of them as confirmed — cross-check against Google Patents / USPTO (subject
to this environment's known egress blocks on those hosts — see CLAUDE.md's
"known environment constraint" section) before drafting an entry.

## Likely duplicates of existing atlas entries — reconcile, don't just add

These candidates describe technology already in `D`, but the submitted
patent number and/or credited inventor **doesn't match** what's currently
in the atlas. Each needs a real research pass to figure out whether the
submitted number is a related family member, a plain error in the source
list, or evidence the existing entry needs a correction — not an assumption
either way.

1. **Shimano SPD** — submitted as Satoshi Naito, US 5,125,288 (1992).
   Atlas already has SPD at `num:"5115692"`, inventor **Masashi Nagano**
   (same inventor credited on the submitted Biopace patent, below — worth
   checking that's not a mix-up in the source list). Check whether
   5,125,288 is a real related Shimano pedal patent (a continuation, a
   different claim set) or whether "Naito" is misattributed.

2. **CamelBak hydration pack** — submitted as Michael Eidson, US 5,060,833
   (1991). **Exact number match** to the atlas's existing entry, which
   already names the patent's inventors as James M. Edison & Arthur D.
   Henderson (Fastrak Systems) and notes CamelBak's own founding story
   credits paramedic Michael Eidson, flagging the "Edison"/"Eidson"
   spelling question as unconfirmed. The submitted text is useful
   supporting color for that existing unconfirmed note (the IV-bag/tube-sock
   prototype detail, the specific race) — fold into the existing entry's
   sourcing rather than creating a second entry.

3. **Hyperglide shifting** — submitted as Nobuo Ozaki, US 4,889,521 (1989).
   Atlas has a Hyperglide entry already but with `num:null`, `conf:"m"`,
   crediting Shimano generally with no named inventor or number. If
   4,889,521 checks out, this is a strong candidate to **upgrade** the
   existing entry rather than add a new one — would take it from `"m"` to
   `"v"` with a real number.

4. **Trek Y-bike / URT frame** — submitted as James P. Cole et al., US
   5,611,557 (1997). Atlas's existing Y-bike entry uses US 5,685,553. Check
   whether 5,611,557 is a related Trek filing in the same family (the atlas
   already documents a Castellano URT patent + Trek's design-around, so a
   third related number wouldn't be surprising) before assuming an error.

5. **Cannondale Lefty (single-sided strut)** — submitted as James F. Turner,
   US 5,957,473 (1999). **This number is already in the atlas — but
   attached to a completely different entry**: the Lawwill four-bar
   suspension family (Gary Fisher RS-1), where it's cited as "Rear
   suspension bicycle." That's a direct conflict worth resolving carefully:
   either the submitted list has the wrong number for the Lefty, or there
   are two unrelated patents that happen to share this number in the
   submitted source (unlikely — verify), or the Lawwill citation is the one
   that's wrong. Don't touch the existing Lawwill entry without confirming
   which is correct.

6. **Mavic UST tubeless** — submitted as Jean-Pierre Mercat, US 6,102,485
   (2000). Atlas's existing UST entry uses US 6,257,676 (filed 1998,
   granted 2001, credited to Jean-Pierre Lacombe and Jean-Pierre Mercat) as
   the primary number, with 6,443,533 and 6,641,227 as continuations. A
   2000-filed 6,102,485 doesn't fit that continuation family's dates as
   described (continuations of a 1998 filing don't usually issue with an
   earlier-appearing number) — check whether this is a distinct related
   Mavic filing or a mismatch in the submitted list.

7. **Tioga Disk Drive wheel** — submitted as Oscar Yamanami/Sugino, US
   5,064,249 (1991). Atlas's existing entry is US **5,064,250** (Tadashi
   Yashiro & Takafumi Nishimoto, Sugino/Nippon Steel Chemical, filed 1989,
   granted 1991) — one digit off, and a different inventor name.
   5,064,249 and 5,064,250 being adjacent numbers from the same era is
   plausible (a companion filing granted the same day), but needs an actual
   lookup rather than assuming it's a typo for the existing entry.

## New candidates — nothing currently in the atlas

No existing `D` entry found for these. Standard verification still applies
before any of them get written up (real invention, real number, resolvable
link, honest tier) — none are pre-approved just because no duplicate exists.

- **Spinergy Rev-X carbon wheels** — Raphael Schlanger, US 5,184,874 (1993).
  Note for research: the UCI-ban/injury angle needs its own sourcing check
  before it goes in `w` — that's a strong claim.
- **Kestrel monocoque carbon frame** — Brent Trimble, US 4,828,781 (1989).
- **Browning Automatic Transmission** — Bruce Browning, US 4,867,733 (1989).
  Genealogy claim (grandson of John Moses Browning) needs independent
  confirmation before repeating it.
- **Rolf paired-spoke wheel lacing** — Rolf Dietrich, US 5,931,544 (1999).
  Note the Trek/Bontrager licensing claim for `w`.
- **Giro vented EPS helmet** — Jim Gentes, US 5,088,130 (1992).
- **Boone Lennon aero bar (Scott DH)** — US 4,750,378 (1988). The 1989 Tour
  de France / Greg LeMond connection is well-documented territory generally
  but still needs its own check against a primary source, not just the
  submitted summary.
- **Elevated chainstays (Mantis)** — Richard Cunningham, US 4,986,558
  (1991). Note: the atlas already has a *different* Cunningham patent
  (Charles B. Cunningham's roller-cam brake, US 4,765,443) under `who:
  ["Charlie Cunningham", ...]` — confirm whether Richard Cunningham
  (Mantis) and Charles "Charlie" Cunningham (WTB) are two different people
  before adding a second `who[]` tag, since a collision here would
  misattribute credit between two real, distinct mountain bike builders.
- **Mavic Zap electronic shifting** — Jean-Pierre Mercat, US 5,358,451
  (1994). Distinct from the UST/ISM/X-Tend Mercat patents already in the
  atlas — same named inventor, different invention; worth a cross-reference
  note if added, given how many other Mercat/Mavic entries already exist.
- **Look clipless pedal** — Jean Beyl, US 4,686,867 (1987).
- **Shimano V-Brake (linear-pull)** — Masanao Ose, US 5,636,716 (1997).
- **Biopace non-circular chainrings** — submitted as Masashi Nagano, US
  4,406,643 (1983). Same inventor name as the atlas's existing SPD entry
  (also credited to Masashi Nagano) — plausible (both Shimano), but confirm
  independently rather than assuming consistency proves accuracy.
- **CamelBak** — see duplicates section above, not a new candidate.
- **Mountain Cycle Pro-Stop hydraulic disc brake** — Robert Reisinger, US
  5,251,727 (1993).
- **Magic Motorcycle hollow crank** — Alex Pong, US 5,456,134 (1995).
  Cannondale/CODA acquisition claim needs its own check.

## Process reminder for whoever picks this up

Follow CLAUDE.md's full workflow, not just this list — in particular:
web-search each invention/number/inventor combination independently (don't
trust the submitted summaries as pre-verified), confirm links resolve,
decide `conf` tier honestly based on what was actually confirmed, register
any new `BRANDS`/`INVENTORS` entries before referencing them, source or
skip images per the "pictures in each entry when possible" preference (two
where a good second figure exists), write both `en`/`fr` from the start,
and run the count-sync step (README + the six hardcoded `index.html`
strings) once anything is actually added.
