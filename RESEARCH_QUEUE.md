# Research Queue — Candidate Patent Entries

Not yet added to `index.html`. This is a holding pen for candidates Jon
supplied on 2026-09-26, pending verification per CLAUDE.md's sourcing
discipline (web-search confirmation, primary-source check, resolvable
links, honest `conf` tiering) before any of them become real `D` entries.
Items struck through below have since been resolved — see each one's own
note for what was found and whether the atlas changed as a result.

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

1. ~~**Shimano SPD**~~ — **Resolved 2026-10-06, dead end.** Per Jon's own
   lookup, US 5,125,288 is not bicycle-related at all, so the "Satoshi
   Naito" attribution has nothing behind it and there is no related
   Shimano pedal filing to reconcile. The atlas's existing SPD entry
   (US 5,115,692, Shimano, `conf:"v"`) stands unchanged. Combined with
   item 3 below, the pattern in that submitted list is now clear: its
   patent numbers are unreliable and its inventor names more so.

2. **CamelBak hydration pack** — submitted as Michael Eidson, US 5,060,833
   (1991). **Exact number match** to the atlas's existing entry, which
   already names the patent's inventors as James M. Edison & Arthur D.
   Henderson (Fastrak Systems) and notes CamelBak's own founding story
   credits paramedic Michael Eidson, flagging the "Edison"/"Eidson"
   spelling question as unconfirmed. The submitted text is useful
   supporting color for that existing unconfirmed note (the IV-bag/tube-sock
   prototype detail, the specific race) — fold into the existing entry's
   sourcing rather than creating a second entry.

3. ~~**Hyperglide shifting**~~ — **Resolved 2026-10-06, entry upgraded.**
   The submitted number was right and the submitted inventor was wrong.
   US 4,889,521 is "Multistage sprocket assembly for a bicycle," inventor
   **Masashi Nagano** (not "Nobuo Ozaki"), filed October 24, 1988, granted
   December 26, 1989, assigned to Shimano Industrial Co. Cross-confirmed
   via the EPO family member EP 0313345 (same title) and the Background
   sections of three later Shimano sprocket patents (US 6,923,741,
   US 8,177,670, US 9,376,165), each citing 4,889,521 by number as the
   Hyper Glide assembly. The atlas entry is now `conf:"v"` with that
   number, a corrected grant year (`g:1990` → 1989) and a corrected
   `exp` (2010 → 2008). Google Patents itself was blocked from the
   session that did this, so the primary page was never opened directly —
   a future session with working access should re-check the exact dates.

4. ~~**Trek Y-bike / URT frame**~~ — **Resolved 2026-10-06, dead end.**
   Per Jon's own lookup, US 5,611,557 is not bicycle-related, so it is not
   a third Trek filing in the Y-bike family and there is nothing to
   reconcile. The atlas's existing Y-bike entry (US 5,685,553) stands
   unchanged. **Note for whoever reads this later:** a web-search snippet
   during the 2026-10-06 pass described 5,611,557 as "issued March 18,
   1997 for a bicycle suspension system." That snippet was wrong. It is
   exactly the kind of unsourced secondary summary CLAUDE.md's sourcing
   discipline warns about, and it should not be used to reopen this
   item.

5. ~~**Cannondale Lefty (single-sided strut)**~~ — **Resolved 2026-10-06,
   no change needed.** US 5,957,473 is "Rear suspension bicycle," inventor
   **Mert Lawwill**, granted September 28, 1999, assigned to Schwinn
   Cycling & Fitness — exactly what the atlas already says, and it stays
   in the Lawwill entry's `nums[]` where it is. The submitted attribution
   to Cannondale's Lefty and inventor "James F. Turner" is simply wrong;
   the atlas's existing Lefty entry (US 5,308,099 + 5,509,674) is
   unaffected. Nothing to change in either entry.

6. ~~**Mavic UST tubeless**~~ — **Resolved 2026-10-06, no change needed.**
   US 6,102,485 is not a Mavic patent at all: per Jon's own lookup it is
   assigned to Casio Computer Co. Ltd., which fits the original suspicion
   that the submitted list carried a typo rather than a real second Mavic
   filing. (Search could not independently surface this number's record
   from this environment, so the Casio attribution rests on that lookup
   rather than on a source read here — but it does not change the
   outcome.) The atlas's existing UST entry (US 6,257,676, with 6,443,533
   and 6,641,227 as continuations, Lacombe and Mercat) is correct as it
   stands and needs no edit.

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

- ~~**Bicycle with integrated anti-theft system**~~ — **Added 2026-09-30;
  this note is retained only as provenance.** Shipped as a real `D` entry
  (`num:"20230312034"`, `cat:"wheel"`, `st:"unknown"`, `conf:"m"`, with a
  drawing) — Bassem Ghaly, assignor to 12226448 Canada Inc. The research
  notes below were answered in the entry itself: `y` follows the confirmed
  2020 priority year, `g`/`exp` are left unset rather than guessed because
  the examination status could not be confirmed, and the claimed mechanism
  sits at a wheel spindle, which settled `cat` as `wheel`. The assignee is
  still a numbered holding company with no identified consumer product —
  that gap is stated in the entry's own `w` text.

## From issue #103 — research leads (triaged 2026-10-06)

Moved here from GitHub issue #103 so the leads live with the rest of the
queue. Each was worked as far as this session's blocked-egress constraint
allowed; **none produced a `D` entry**, and the reason is recorded per item
rather than left implied.

1. ~~**Scott Sports SA portfolio**~~ — **Resolved 2026-10-06 as a Patent
   Fight, not a portfolio scan.** The lead was framed as "scan the Justia
   assignee listing," which is a blocked host and looked like a batch job.
   It wasn't. US litigation names patents by their last three digits, and
   the "'679"/"'837" patents in contemporary coverage of the Specialized
   suit are **US 5,509,679 and US 5,678,837** — both already in the atlas
   as the Horst Link entries. Confirmed against the docket Jon supplied:
   **Case 3:04-cv-01496, N.D. Cal., filed April 16, 2004**, both patents
   titled "Rear suspension for bicycles," inventor Horst Leitner; the case
   number corroborates against govinfo's own record
   (`USCOURTS-cand-3_04-cv-01496`). Shipped as a ninth `FIGHTS` entry,
   `specialized-scott`, and US 5,678,837 picked up the `litigated` badge
   it had been missing. **Still genuinely open:** the rest of the Scott
   Sports portfolio was never screened — that part still needs the
   assignee listing, which no source reachable from here provides.



2. ~~**US 11,318,049 B2**~~ — **Added 2026-10-06.** Resolved once Jon
   supplied the bibliographic data the blocked databases would not give up:
   it is "Goggle," inventor Gavin Michael Vos, assigned to VOG — Image
   Police Inc. of Taichung, Taiwan. Confirmed against the patent's own
   front page, pulled via the `Fetch patent figure` workflow: filed
   October 23, 2018 as PCT/CN2018/111340 (published WO 2020/082222), US
   national phase March 26, 2020, granted May 3, 2022 with zero term
   adjustment. It is a roll-off goggle — two reels with a film sheet
   across the lens — whose point of novelty is that the control assembly
   mounts to either reel, so one goggle sets up left- or right-handed.
   Filed under `cat:"tech"`, following the 100% Speedlab protective-eyewear
   entry's precedent for rider-worn eyewear, `conf:"v"`, with Figs. 1 and 2
   wired in (both rotated 90° clockwise from the source sheets). `who` is
   left empty: the assignee is a Taichung company with no identified
   consumer brand, the same handling the Ghaly anti-theft entry got.

3. ~~**TQ Systems — EP 2,582,571 B1**~~ — **Resolved 2026-10-06, entry
   added.** The single blocker was the proprietor, which no reachable
   source confirmed — it had come only from the submitted link's query
   string. Settled by running the patent through the `Fetch patent figure`
   workflow, which reaches the EPO document server from GitHub's runners
   where this sandbox cannot: the B1 front page reads **"(73) Proprietor:
   TQ-Systems GmbH, 82229 Seefeld (DE)"**, inventor **Jürgen Jäkel**. Also
   confirmed there: application 11795288.7, filed June 17, 2011 as
   PCT/IB2011/052659 (WO 2011/158220), priorities DE 10 2010 017 412 and
   DE 10 2010 036 833, grant published October 19, 2016, IPC in B62M 6/xx
   (electric bicycles). Added as its own `emtb` entry at `conf:"v"` rather
   than folded into the pin-ring gearbox entry, since it claims control
   logic (cut motor torque for the duration of a shift) rather than
   mechanism. **Generalisable lesson:** the figure workflow is not just for
   drawings — its front-page report is the way to read bibliographic data
   off any patent this environment's egress policy blocks.

4–5. **Starley background reading, and the Hadland & Lessing *Bicycle Design*
   piece** — no action needed or taken. Both are secondary-source background,
   useful for enriching the existing 1870 Starley & Hillman entry or for
   sourcing early entries, and neither is a primary source to cite directly in
   an `s` field. Left as reading, which is what the issue already called them.

## Mavic leads (added 2026-10-06, from Jon)

The **X-Tend e-bike motor platform is already in the atlas** — US 12,434,786
plus US 12,325,488 in `nums[]`, `conf:"v"`, catalogued as a 15-patent family
and crediting Jean-Pierre Mercat. No new entry needed. Two things that would
still improve it: it currently has **no figure**, and the
[BicycleRetailer piece on Mavic's motor patent trail](https://www.bicycleretailer.com/product-tech/2024/02/14/industry-patent-watch-mavics-minimalist-motor-has-long-patent-trail)
is a usable secondary source for the entry's history that nothing in the
entry cites yet.

Three further Mavic candidates, none screened against `D` yet and none
verified — these need the batch-sourcing workflow (candidate list, Jon
picks, then write):

- **R2R spoke lacing** — continuous carbon-fibre spokes running from one
  side of the rim straight through the hub to the other, per
  [Bike Europe](https://www.bike-eu.com/3274/mavic-patents-spoke-lacing-technology).
  Would be a `wheel` entry. Note the atlas already holds Mavic wheel
  entries (UST, ISM/FORE) plus other continuous/composite-spoke art, so
  screen against those for overlap before treating it as distinct.
- **iTgMax** — a laser treatment of the braking surface on carbon rims.
  `wheel`. No patent number in hand.
- **Mektronic (1999) wireless group** — would pair with the atlas's
  existing Mavic Zap entry, which is still `num:null`/`conf:"m"` with no
  US number located. [Disraeligears' Mavic page](https://www.disraeligears.co.uk/site/documents_-_mavic.html)
  is the suggested starting point. Finding a real number for either Zap or
  Mektronic would let that existing entry move off `"m"`, which is the
  higher-value outcome of the three.

## Scott Sports portfolio — screening material (2026-10-06)

The one part of issue #103 still genuinely open. The assignee listings are
on blocked hosts, so no session here can enumerate the portfolio; this is
what could be established from outside them.

**Pull the listing from two pages, not one** — older filings sit under the
US entity:

- `patents.justia.com/assignee/scott-sports-sa`
- `patents.justia.com/assignee/scott-usa-inc`

**Candidates, verified 2026-10-06 against the records Jon pulled.** Neither
is in `D`; both screened by number and by title/assignee. Two corrections to
the first pass are folded in — the fork shaft had *granted* since the
publication that first surfaced, and the two helmet numbers turned out to be
one family, not two candidates:

1. **Eccentric bicycle fork shaft — US 10,926,827 B2.** Inventor Ricco
   Süsse, assignee Scott Sports SA. DE priority 2017; US application
   16/133,886 filed September 18, 2018; published as US 2019/0092417 A1 on
   March 28, 2019; **granted February 23, 2021**. Status active, adjusted
   expiration **2039-08-03**. The claim: a fork shaft whose cylindrical
   segment sits eccentric to the steering axis, the eccentricity pointing
   opposite the direction of travel — offset, and therefore trail, set by
   where that eccentric sits rather than by the fork crown. Ready to write;
   note the `exp` is **2039, not 2038** — a filing+20 of 2038-09-18 plus
   patent term adjustment. State the PTA in the entry explicitly rather than
   landing on 2039 by coincidence, the same handling the Star Ratchet EXP
   entry got.

2. **Protective helmet with a shell and a movable visor — US 2023/0136136 A1
   (= EP 4 125 480 A1).** Inventors Anatole Dehéselle and Mathilde Lamaud,
   assignee Scott Sports SA. One invention, two family members: US
   application 17/914,517 and EP application 21700933.1, both filed
   January 19, 2021; US publication May 4, 2023, EP publication February 8,
   2023. **Both still pending** — so `st:"pending"`, `g:null` and `exp:null`
   per the schema's pending handling, and the US publication number is the
   one to put in `num`. The visor detaches and re-seats via fastening
   elements on the shell, holding either over the face opening or parked on
   the shell outside it, with flexible elements on each side keeping it
   captive.

**Excluded: US 11,083,239.** Surfaced in a Scott helmet search and flagged
then as unconfirmed; it is **Bauer Hockey LLC**, a hockey visor system, not
Scott and not mountain biking. Not a portfolio item at all — recorded here
so the same search result doesn't resurface it as one.

US 9,039,026 also surfaced once as a possible "bicycle suspension system"
hit and could not be verified at all on re-search. It is recorded here only
so a future session does not spend budget rediscovering it; do not treat it
as a Scott number.

**Subject areas reported for the portfolio** (useful for screening the real
listing): protective helmets with movable visors, handlebar stems with
integrated cable guidance, cycling power meters, shock absorbers, eccentric
fork shafts, bicycle wheels, and frame components.

**Pre-exclude when screening** — already in `D`: US 10,071,786 (Scott/Bold
integrated hidden-shock frame) and US 4,750,754 (Boone Lennon aero bar /
Scott DH bar). Also note US 5,509,679 and US 5,678,837 are Scott-adjacent
through the `specialized-scott` fight but are Specialized's patents, not
Scott's.

**Highest-value target in the whole portfolio:** the atlas's **TwinLoc
simultaneous lockout** entry is `num:null`, `conf:"l"`, crediting Scott
generally with no number. Finding its patent upgrades an existing draft-tier
entry rather than adding a new one — the same reasoning that makes Mektronic
the pick among the Mavic leads.

## Trek IsoSpeed (resolved 2026-10-07)

1. ~~**US 8,210,554 as "the key IsoSpeed patent" (inventor "Mark Cole")**~~ —
   **Resolved 2026-10-07, dead end.** A WheelBased summary gives this number,
   title "Decoupled Seat Tube" and inventor Mark Cole. Google Patents' record
   for US 8,210,554 B2 is "Bicycle frame having a multiple step and lap joint"
   (David Guzik, Christopher Pomering; Trek; filed 2009-07-09, granted
   2012-07-03), a frame-joint patent unrelated to IsoSpeed. Do not resubmit.
   The IsoSpeed entry now cites US 10,086,899 / 10,351,192 / 10,676,145
   ("Adjustable compliance bicycle", Hartung and Moechnig).
2. **Open lead: the original 2012 Domane decoupler patent.** The family above
   dates from 2015 provisionals and 2016 filing, after the 2012 launch, and
   covers the adjustable version. A pre-2016 Trek filing may exist; not found.
   Also unchecked: US 11,242,111 (same "Adjustable compliance bicycle" family
   per search results) and US 10,150,530 ("Rigid frame with high-compliance
   seat tube and internal cable routing", Trek, per a Golden.com listing).

## Continental MTB patents (added 2026-10-13, from Jon)

Source was an unattributed summary of Continental's MTB tire patent base,
submitted alongside the atlas's existing "Continental MTB construction
patents" entry (`conf:"l"`). One number held up; the rest did not.

- **US 7,968,635** — confirmed (Continental AG, "Tire compositions and
  components containing free-flowing filler compositions", filed 2006-12-28,
  granted 2011-06-28, from a joint research agreement with GE's silicones
  unit). General tire-compound patent. Cited in the Continental entry's `s`
  with the caveat that nothing ties it to the Kryptotal/Argotal/Xynotal/
  Hydrotal compounds. Promote to a numbered entry only if that link is found.
- ~~**US 12,397,590 B2**~~ — **Resolved 2026-10-13.** Jon supplied the Google
  Patents record: "Pneumatic tyre for a two-wheeled vehicle", Continental Reifen
  Deutschland GmbH, granted 2025-08-26. The Continental entry is now numbered
  on it. Its link to MTB tires is still unconfirmed.
- **DE 20 2020 104 281 U1**, **EP 3,174,738 A1** — submitted in the same
  line. No search turned up a record for either (EP 3,174,738 returns unrelated
  results). Unverified.
- **DE 20 2015 000 366 U1 / EP 0,484,831** — submitted as bead-reinforcement and
  tubeless-interface patents. Not found; an EP 0,484,xxx number would date from
  about 1991, which doesn't fit a 2015 German utility model, so the pairing looks
  malformed. Unverified.
- The summary's claims about ply layouts, TPI and the SuperSoft/Soft/Endurance
  compounds being trade secrets have no cited source. Treat as unsourced.

## Niner leads (added 2026-10-13, from Jon)

- MCR 9 RDO discontinuation (submitted as November 2023) — not confirmed.
- ~~United Wheels pause (2026)~~ — **Resolved 2026-10-13.** Reported May 19–20, 2026 by Bicycle Retailer, Pinkbike, BikeRadar and others; now in the CVA entry.
- Assignment of US 7,934,739 itself to UWHK not yet seen; only 8,590,914's
  record was checked.

## Shimano V-Brake patent (added 2026-10-16)

- The atlas's former "V-Brake" entry (US 5,636,716) turned out to describe a four-bar link driven by a cantilever brake; its text never uses the name V-Brake. The patent that actually covers the single-cable linear-pull V-Brake (introduced c. 1991) is not yet identified. Search Shimano filings of 1989–1991 by title ("Bicycle brake device", "Brake assembly") and confirm the claim language before adding an entry.

## Citation-map leads (added 2026-11-13, picked by Jon)

Found by counting which patents with no Atlas card are cited by, or cite, the
most Atlas cards (`tools/citation_map/`, Google Patents citation tables read
2026-11-13). Jon chose these 17 from that ranking. Numbers, titles, assignees
and priority dates are as Google Patents' citation tables list them; none has
had its own front page verified, a drawing chosen, or its bike relevance
confirmed beyond the title. "Cards" is how many Atlas cards the patent links to.

### New cards (14)

Rear suspension
1. **US 5,791,674** — "Bicycle suspension system", Cannondale Corporation, priority 1997-03-13. Cited by 27 cards.
2. **US 5,226,674 + US 5,205,572** — "Cycle rear suspension system", Schwinn Bicycle Company, priority 1991-08-27. Cited by 21 cards. One card for the pair unless the two turn out to cover different designs.
3. **US 7,100,930** (published as US 2005/0057018 A1) — "Bicycle rear suspension system", Neal Tate Saiki, priority 2003-09-15. Cited by 21 cards.
4. **US 5,217,241** — "Bicycle suspension system", Ocean State International Inc., priority 1990-09-18. Cited by 19 cards.

Forks & damping
5. **US 5,186,481** — "Bicycle with improved front fork wheel suspension", RockShox, priority 1991-04-03. Cited by 8 cards.
6. **US 5,456,480** — "Fork suspension with variable hydraulic damping", RockShox, priority 1994-06-06. Cited by 8 cards.
7. **US 5,580,075** — "Bicycle fork suspension with exchangeable spring unit", RockShox, priority 1994-06-06. Cited by 8 cards.
8. **US 6,105,988** — "Adjustable suspension system having positive and negative springs", RockShox, priority 1997-07-16. Cited by 7 cards.
9. **US 5,996,746** — "Adjustable twin tube shock absorber", RockShox, priority 1997-07-03. Cited by 6 cards.
10. **US 6,260,832** — "Shock absorber with adjustable compression and rebound", Marzocchi S.p.A., priority 1997-12-17. Cited by 6 cards.

Check 5 to 10 against the existing RockShox and Marzocchi cards first (RS-1 fork US 4,971,344; "Marzocchi damping & hub portfolio"); some may belong on a card that already exists.

Drivetrain
11. **US 3,969,947** — "Tapered tooth sprocket", Gehl Company, priority 1975-05-22. Cited by 6 cards. Companion to the existing Gehl alternating-width sprocket card (US 4,174,642); cross-link the two.
12. **US 9,033,833 + US 9,327,792 + US 10,207,772** — "Gear transmission and derailleur system", Paha Designs, LLC, priority 2011-01-28. The family cites 9 cards.

Bike transport
13. **US 5,526,971** — "Bicycle rack", Steven S. Despain, priority 1994-05-06. Cited by 5 cards.

Rear suspension, recent
14. **US 12,617,488** — "Two-wheeled vehicle with configurable idler", Yeti Cycling, LLC, priority 2021-09-09. Cites 28 cards. Check against the existing Yeti 6-bar idler card (US 2025/0376238) before adding: same 2021 family is possible.

### Numbers that probably belong on existing cards (3)

15. **US 5,628,524 + reissue US RE39,159** — "Bicycle wheel travel path for selectively applying chainstay lengthening effect and apparatus for providing same", Outland Design Technologies (the reissue is listed to Santa Cruz Bicycles), priority 1995-01-25. Cited by 25 cards. Likely belongs with the Outland Virtual Pivot Point card (US 5,553,881). Confirm the relationship before adding it to `nums[]`; the card's `exp` and text may need to follow.
16. **US 5,409,249 + US 5,441,292** — "Bicycle rear suspension system", GT Bicycles, priority 1993-09-15. Cited by 25 cards. Likely belongs with "GT RTS / LTS suspension era" (US 5,259,637 + 5,306,036 + 6,056,307 + EP 0,825,098).
17. **US 5,244,224** — "Rocker arm rear suspension bicycle", GT Bicycles, priority 1992-05-14. Cited by 21 cards. Same GT card as 16.

The full ranking (501 patents linked to four or more cards) was delivered to
Jon as a spreadsheet, not committed; rebuild it from `graph.py`'s output if
needed. The three Yeti patents already on hold (US 10,766,563, 12,077,241,
12,145,684) rank at the top of the "cites the most Atlas cards" side.

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
