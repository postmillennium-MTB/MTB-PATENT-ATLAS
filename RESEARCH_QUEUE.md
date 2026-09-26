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

7. ~~**Tioga Disk Drive wheel**~~ — **Resolved 2026-09-26, no change needed.**
   US 5,064,249 is a real patent, but it's a completely unrelated automotive
   part: "Disc wheel cover" (a hubcap), inventor Hung Chun Mao, filed
   April 9, 1990, granted November 12, 1991 — same era, adjacent number,
   nothing to do with bicycles. Confirms the atlas's existing entry, US
   5,064,250 (Tadashi Yashiro & Takafumi Nishimoto, Sugino/Nippon Steel
   Chemical, "Wheel for light vehicle and disc used therefor," filed
   June 13, 1989, granted November 12, 1991 — same issue date as the
   unrelated 5,064,249, which is presumably why the two got confused
   upstream of this atlas), is correct as-is and needs no change.

## New candidates — nothing currently in the atlas

All 13 "new candidate" entries from this section (Spinergy Rev-X, Kestrel
monocoque, Browning Automatic Transmission, Rolf paired-spoke wheel, Giro
vented EPS helmet, Boone Lennon/Scott DH aero bar, Mantis elevated
chainstays, Mavic Zap, Look clipless pedal, Shimano V-Brake, Biopace,
Mountain Cycle Pro-Stop, and Magic Motorcycle hollow crank) were added to
`index.html` on 2026-09-26 — see the README changelog entry "Added 13
entries from a 26-candidate list..." for what was actually confirmed.

**Most of the originally-submitted patent numbers turned out to be
wrong** — independent web-search verification found several named a
completely different, unrelated invention (details in the README
changelog entry). Corrected real numbers were used where one could be
confirmed; where none could be, the entry shipped honestly with
`num:null` and a low/medium confidence tier rather than guessing. Two
follow-ups worth a future session with working patent-database access:

- The Kestrel entry (now US 4,982,975, Brent J. Trimble) flags a real risk
  of confusion with US 4,513,986, a different, similarly-named "James L.
  Trimble" patent from the same few years — worth confirming neither
  number got swapped.
- The Shimano V-Brake entry (US 5,636,716) credits inventor "M. Sugimoto"
  from a single source, not the "Masanao Ose" name originally submitted —
  needs a second source before that inventor credit is treated as settled.

CamelBak remains out of scope as a new entry — see the duplicates section
above; that submission's detail was folded into the existing entry's own
sourcing note rather than creating a second entry.

- **Bicycle with integrated anti-theft system** — Bassem Ghaly, assignee
  12226448 Canada Inc., US 20230312034A1 (a *published application*, not
  yet a granted patent — WO/US/EP family, worldwide filing 2020). A
  spindle-blocking mechanism built into a bicycle sub-assembly (bore that
  receives a wheel/BB/headset-type spindle) with a locked/unlocked state
  toggled by an authorized user — an integrated, non-retrofit anti-theft
  approach rather than a bolt-on lock. Nothing in the atlas today covers
  integrated/frame-level anti-theft (only conventional add-on locks would
  be adjacent, and none of those are in `D` either) — this would be a
  genuinely new angle, not just a new company. Notes for whoever
  researches it: confirm current prosecution status (published ≠ granted,
  so `st` would likely be `"pending"` and `exp` should stay `null` until a
  grant date exists, per the schema's own pending-patent handling);
  identify what product/brand this maps to, if any, since the assignee
  name here is a numbered holding company rather than a recognizable
  brand; and check whether "spindle" in the claims covers a wheel axle,
  a bottom bracket spindle, or both, since the entry's `cat` depends on
  that (likely `comp`, possibly `wheel`).

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
