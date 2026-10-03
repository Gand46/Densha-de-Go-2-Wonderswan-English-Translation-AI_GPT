---
title: "WonderSwan Translation Projects — Universal Rules"
version: "1.1"
date: "2026-09-20"
scope: "All WonderSwan / WonderSwan Color translation and localization projects"
language: "en"
status: "MANDATORY_BASELINE"
machine_readable_sections: true
---

# WonderSwan / WonderSwan Color Translation Projects
## Universal Rules, Translation Quality and Integrated Quality Gate
### Version 1.1 — Mandatory Project Source

## 0. PURPOSE AND AUTHORITY

This document is the universal baseline for all WonderSwan and WonderSwan Color translation/localization projects.

It is intended to be consumed by:
- GPT/LLM agents;
- ChatGPT Work projects;
- coding agents;
- QA agents;
- translation agents;
- human contributors;
- automated build/verification pipelines.

Project-specific rules MAY add stricter constraints, but MUST NOT weaken, bypass, or contradict this baseline.

The quality model is:

```text
FINAL QUALITY
=
UR PASS
+
TQ PASS
+
QG PASS
```

Where:

```text
UR = Universal technical/project rules
TQ = Translation and linguistic quality rules
QG = Integrated product/release quality rules
```

The desired end result is not merely "Japanese text replaced with English".

The target is:

> A coherent English-language version that looks, reads and behaves as if it could have been an official WonderSwan/WonderSwan Color release, while preserving the original game's design, functionality, constraints and artistic identity.

---

# PART I — UR: UNIVERSAL PROJECT RULES

## UR-01 — Identify the original ROM
Every project MUST identify the original Japanese ROM using, at minimum:
- expected filename;
- exact byte size;
- SHA-256;
- WonderSwan checksum when applicable.

Never assume two ROMs with the same filename are byte-identical.

## UR-02 — Use a clean base
Official cumulative patches MUST be generated from a clean, known original ROM.

## UR-03 — Commercial ROM handling
A commercial ROM may be used privately for development and validation, but it is NOT required to be distributed with the project package.

The package MUST include sufficient metadata/hashes for the user to provide the correct base ROM.

## UR-04 — Never silently change the base
If a project changes to a different original ROM revision, that change MUST be explicitly documented and the validation chain rebuilt.

## UR-05 — Complete cumulative sources
Every formal version MUST include the complete cumulative source state needed to reproduce the current build.

Do not ship only files changed in the last phase.

## UR-06 — Mandatory cumulative BPS
Every playable formal version MUST include:

```text
Original Japanese ROM -> Current Version
```

as a cumulative BPS patch.

## UR-07 — No patch chains
Users MUST NOT need:

```text
v0.1 -> v0.2 -> v0.3 -> v0.4
```

to obtain the current version.

## UR-08 — Incremental patches are supplemental
Incremental BPS/IPS patches may be retained for:
- auditing;
- debugging;
- historical comparison;
- regression analysis.

They are NOT the primary installation method.

## UR-09 — IPS is optional/supplemental
A cumulative IPS may be included for compatibility, but it does NOT replace the mandatory cumulative BPS.

## UR-10 — Self-contained delivery
Formal packages SHOULD include, when applicable:
- full source;
- scripts;
- tables;
- dictionaries/glossaries;
- builders;
- patchers;
- verifiers;
- inventories;
- reports;
- evidence;
- documentation;
- changelog;
- hashes.

The project MUST NOT depend solely on prior chat context.

## UR-11 — Reproducible build
There MUST be a documented procedure equivalent to:

```text
Known Original ROM + Project Sources/Scripts -> Current ROM
```

## UR-12 — BPS round-trip verification
Applying the cumulative BPS to the correct original ROM SHOULD produce a ROM byte-identical to the project build.

Preferred validation:

```text
SHA256(builder_output) == SHA256(BPS_output)
```

## UR-13 — WonderSwan checksum
After ROM modification, validate and rebuild the WonderSwan checksum when required.

## UR-14 — Output hashes
At minimum record SHA-256 for:
- original ROM;
- current ROM;
- cumulative BPS.

## UR-15 — Explain binary changes
Relevant binary modifications SHOULD be attributable to intended project changes.

## UR-16 — Validate allowed ranges
For bounded modifications, compare actual changed ranges against expected ranges.

Preferred result:

```text
unexpected_changed_offsets = 0
```

## UR-17 — Preserve neighboring data
Do not arbitrarily alter:
- code;
- pointers;
- opcodes;
- padding;
- tables;
- graphics;
- icons;
- terminators;
- metadata;
- neighboring resources.

## UR-18 — No blind global replacements
Do not globally replace byte sequences merely because they decode as Japanese text.

The resource context MUST be understood first.

---

# PART II — TEXT DISCOVERY AND STRUCTURAL VALIDATION

## UR-19 — Shift-JIS/CP932 is only candidate evidence
A valid Shift-JIS/CP932 sequence is NOT proof that it is real in-game text.

## UR-20 — Prefer structural confirmation
When possible, connect candidate text to:
- consumer;
- pointer;
- descriptor;
- table;
- decoder;
- renderer;
- script;
- index;
- resource structure;
- runtime execution.

## UR-21 — No destructive candidate filtering
Do not permanently discard uncertain candidates solely because of:
- entropy;
- proximity;
- apparent noise;
- length;
- unusual characters;
- lack of obvious references.

## UR-22 — Use explicit unresolved states
Allowed states include:

```text
UNRESOLVED
UNKNOWN
NEEDS_TRACE
NEEDS_CONTEXT
NEEDS_REVIEW
SOURCE_UNCLEAR
```

## UR-23 — Negative evidence is limited
Failure to find a reference with one tool does NOT prove a resource is unused.

---

# PART III — UNIVERSAL TRANSLATION STATES

The following states MUST be treated as independent:

```text
DISCOVERED
TRANSLATED
INTEGRATED
RUNTIME_CONFIRMED
LINGUISTIC_APPROVED
DESIGN_APPROVED
VISUAL_APPROVED
FUNCTIONAL_APPROVED
FINAL_APPROVED
```

Never treat one state as automatically implying the next.

---

# PART IV — TQ: TRANSLATION / LINGUISTIC QUALITY

## TQ-01 — Preserve meaning
The translation MUST preserve the real meaning of the source.

## TQ-02 — Preserve intent
Maintain the communicative function:
- question;
- order;
- threat;
- request;
- joke;
- warning;
- explanation;
- implication;
- reaction;
- gameplay instruction.

## TQ-03 — No unsupported additions
Do not add information that is absent or not reasonably implied in the source.

## TQ-04 — No meaning loss
Do not omit meaning merely to make text fit.

Solve space pressure through better wording, layout, typography or technical changes.

## TQ-05 — Preserve logic
Maintain:
- cause;
- consequence;
- condition;
- negation;
- comparison;
- temporal relation;
- subject/object;
- direction;
- possession.

## TQ-06 — Preserve gameplay information
Never accidentally alter:
- quantities;
- stats;
- percentages;
- damage;
- items;
- conditions;
- directions;
- objectives;
- hints;
- timers;
- turns;
- commands;
- requirements.

A stylistically attractive but functionally wrong translation is a FAIL.

## TQ-07 — Natural target language
Final English MUST read naturally and should not look like raw Japanese syntax transferred word-for-word.

## TQ-08 — No unreviewed MTL
Machine/LLM output may create a draft, but it MUST NOT be considered linguistically approved without review.

## TQ-09 — Grammar
Approved text MUST use correct grammar.

## TQ-10 — Spelling
Known spelling errors are not acceptable in approved text.

## TQ-11 — Punctuation consistency
Use project-wide conventions for:
- periods;
- commas;
- question/exclamation marks;
- apostrophes;
- quotes;
- dashes;
- ellipses.

## TQ-12 — Capitalization consistency
Define and preserve conventions for:
- names;
- titles;
- items;
- skills;
- menus;
- headings;
- places;
- commands.

## TQ-13 — Mandatory terminology memory/glossary
Large projects SHOULD maintain a central glossary covering, where relevant:
- characters;
- places;
- items;
- weapons;
- armor;
- spells;
- skills;
- statuses;
- enemies;
- factions;
- organizations;
- UI commands;
- system terminology;
- proper nouns.

## TQ-14 — One entity, one approved name
The same entity SHOULD NOT receive different translations without a documented reason.

## TQ-15 — Document required abbreviations
When a technical limit requires a shorter variant, document it.

Example:

```text
Full: Restoration Potion
Menu: Restore Pot.
```

## TQ-16 — Preserve character voice
When applicable preserve:
- formality;
- rudeness;
- timidity;
- authority;
- age impression;
- humor;
- sarcasm;
- arrogance;
- innocence;
- military style;
- technical register.

## TQ-17 — Do not approve ambiguous text without context
When context materially affects meaning, identify:
- speaker;
- listener;
- scene;
- location;
- previous line;
- next line;
- game state.

Otherwise use:

```text
NEEDS_CONTEXT
```

## TQ-18 — Dialogue must work as dialogue
Review conversations as connected exchanges, not isolated strings.

## TQ-19 — UI wording must be functional
Menu labels and commands MUST prioritize clear function while preserving meaning.

## TQ-20 — Abbreviate only when necessary
When space is limited, prioritize:

```text
meaning
> clarity
> consistency
> naturalness
> compactness
```

## TQ-21 — Reference translations are semantic aids
Translations from SNES/PS1/other versions may guide:
- meaning;
- official terminology;
- names;
- intent.

They MUST NOT be assumed structurally identical to the WonderSwan version.

## TQ-22 — Do not invent context
If the correct interpretation cannot be supported, mark it unresolved instead of guessing.

---

# PART V — QG: INTEGRATED PRODUCT / RELEASE QUALITY

## QG-01 — Quality is multidimensional
Release quality requires all applicable dimensions:

```text
LINGUISTIC QUALITY
+
TECHNICAL INTEGRATION
+
VISUAL DESIGN
+
TYPOGRAPHY
+
LAYOUT
+
UI/UX QUALITY
+
GAMEPLAY INTEGRITY
+
ARTISTIC CONSISTENCY
+
RUNTIME STABILITY
+
REGRESSION CONTROL
+
CONTENT COVERAGE
+
REPRODUCIBILITY
```

## QG-02 — Translation must look native to the game
Localized content MUST feel integrated into the original game systems, not pasted on top.

## QG-03 — Respect the original architecture
Do not solve presentation problems with arbitrary hacks that damage:
- pointers;
- tables;
- code;
- memory;
- save behavior;
- control codes;
- nearby resources.

## QG-04 — No integration side effects
A valid change MUST NOT introduce:
- missing text;
- graphical corruption;
- new misalignment;
- crashes;
- gameplay changes;
- save failures;
- regressions in previously approved scenes.

---

# PART VI — DESIGN QUALITY

## QG-10 — Preserve composition
Maintain the original visual logic:
- hierarchy;
- margins;
- alignment;
- centering;
- distribution;
- grouping;
- relationship between text and icons.

## QG-11 — "It fits" is not enough
A string is not design-approved merely because it remains inside a box.

Evaluate:
- breathing room;
- balance;
- optical centering;
- distance from borders;
- relation to neighboring elements.

## QG-12 — Optical centering
Centered:
- titles;
- names;
- item labels;
- buttons;
- headers

MUST be evaluated visually, not only by character count.

## QG-13 — Preserve hierarchy
Maintain clear distinction between:
- titles;
- subtitles;
- body text;
- values;
- commands;
- names;
- secondary information.

## QG-14 — Localized redesign is allowed when necessary
The English version may require a layout/design adaptation, but it MUST look intentional and coherent with the original game.

---

# PART VII — TYPOGRAPHY QUALITY

## QG-20 — Respect typographic style
Modified text SHOULD preserve the game's typographic identity.

## QG-21 — Evaluate glyph width
Character count alone does not determine whether text fits.

## QG-22 — Validate spacing
Check:
- letter spacing;
- word spacing;
- icon/text spacing;
- number/symbol spacing;
- accidental double spaces;
- missing spaces.

## QG-23 — Baseline and height
Do not accept:
- vertically floating glyphs;
- clipped glyphs;
- inconsistent baseline;
- malformed glyph height.

## QG-24 — Font changes require global regression testing
If the font or glyph mapping changes, revalidate other surfaces affected by the same font.

---

# PART VIII — LAYOUT QUALITY

## QG-30 — No clipping
No approved text may be cut off.

## QG-31 — No overflow
Text MUST NOT invade:
- frames;
- portraits;
- icons;
- numbers;
- other fields;
- reserved regions.

## QG-32 — Good line breaks
Line breaks SHOULD preserve semantic and visual units.

Avoid unnecessary separation of:
- article + noun;
- auxiliary + verb;
- proper names;
- number + unit;
- inseparable expressions.

## QG-33 — Window modifications must remain coherent
If a window is resized or altered, preserve:
- visual style;
- borders;
- symmetry;
- tile consistency;
- reuse compatibility.

## QG-34 — Avoid destructive one-off fixes
Do not fix one string by changing a reusable component in a way that breaks other strings/screens.

---

# PART IX — ARTISTIC QUALITY

## QG-40 — Preserve platform/game identity
Localization assets SHOULD remain consistent with:
- WonderSwan-era resolution;
- platform palette;
- original artistic direction;
- original pixel-art language.

## QG-41 — Pixel-art discipline
Localized graphics MUST respect:
- original resolution;
- pixel grid;
- tile size;
- color limits;
- pixel-art style;
- platform-appropriate anti-aliasing behavior.

## QG-42 — Logo localization
A localized logo SHOULD preserve:
- personality;
- proportions;
- visual weight;
- composition;
- intent.

Do not replace a distinctive logo with generic typography.

## QG-43 — Preserve iconography
Do not alter original icons unless localization requires it.

## QG-44 — Avoid visually foreign assets
Avoid modern-looking fonts, smoothing, Unicode glyphs or graphic elements that visibly clash with the original game.

---

# PART X — UI / UX QUALITY

## QG-50 — Immediate comprehension
The player SHOULD understand:
- what is selected;
- what action will occur;
- what value is shown;
- how navigation works.

## QG-51 — Command consistency
The same action SHOULD keep the same name across interfaces unless a documented constraint requires otherwise.

## QG-52 — Preserve UI states
Validate:
- selected;
- unselected;
- active;
- inactive;
- disabled;
- highlighted.

## QG-53 — Navigation integrity
Localization MUST NOT accidentally alter:
- cursor positions;
- hitboxes;
- menu order;
- selection coordinates;
- navigation logic.

## QG-54 — Functional clarity beats decorative wording
A visually elegant but functionally ambiguous label is a quality failure.

---

# PART XI — GAMEPLAY INTEGRITY

## QG-60 — Localization must not alter gameplay
Do not accidentally change:
- damage;
- statistics;
- AI;
- collision;
- timers;
- spawn behavior;
- progression;
- flags;
- scripts;
- win/loss conditions.

## QG-61 — Save/load validation
When applicable validate:
- New Game;
- Save;
- Load;
- Continue;
- cold boot;
- existing save compatibility.

---

# PART XII — RUNTIME AND VISUAL QA

## QG-70 — Boot is only a minimum check
A successful boot is NOT equivalent to full QA.

## QG-71 — Representative runtime validation
Every modified family SHOULD receive representative runtime validation.

## QG-72 — Cover late-game states
QA SHOULD include, when applicable:
- title;
- menus;
- options;
- gameplay;
- dialogue;
- inventory;
- equipment;
- battle UI;
- shops;
- tutorials;
- transitions;
- Stage Clear;
- Game Over;
- Continue;
- Save/Load;
- late-game areas;
- ending;
- credits.

## QG-73 — Visual review criteria
Check:
- clipping;
- overflow;
- overlap;
- spacing;
- centering;
- alignment;
- width;
- line breaks;
- corrupted glyphs;
- damaged icons;
- wrong tiles;
- legibility.

## QG-74 — Evidence
Important visual validation SHOULD preserve evidence such as:
- screenshot;
- GIF;
- video;
- log;
- save state/checkpoint;
- reproducible route.

---

# PART XIII — NATURAL VS SYNTHETIC QA

## UR-30 — Label access method
When relevant, distinguish:

```text
NATURAL
SCRIPTED_NATURAL
SAVESTATE
CHEAT
WRAM_POKE
FREEZE
SYNTHETIC_STATE
POINTER_INJECTION
STATIC_ONLY
NOT_VALIDATED
```

## UR-31 — Synthetic proof has limited scope
Synthetic validation may prove:
- resource existence;
- decoder behavior;
- renderer compatibility;
- consumer behavior.

It does NOT prove that the scene was naturally reached in normal gameplay.

## UR-32 — Never misrepresent synthetic coverage
Do not report synthetic access as if it were a normal playthrough.

---

# PART XIV — UNIVERSAL ANTI-BLOCKING POLICY

## UR-40 — No test may block the project indefinitely
A hard-to-reach state MUST NOT stop development indefinitely.

## UR-41 — Bounded natural attempt
Natural/manual/automated navigation SHOULD have a defined time/frame/attempt limit.

## UR-42 — Escalate methods
If natural access fails, progressively consider:
1. savestate/checkpoint;
2. scripted input;
3. cheats/flags;
4. WRAM poke/freeze;
5. breakpoints/watchpoints;
6. consumer tracing;
7. minimal pointer substitution;
8. controlled state injection;
9. static analysis.

## UR-43 — Do not repeat equivalent failures indefinitely
After repeated equivalent failures, change methodology.

## UR-44 — Use safeguards
Long-running tasks SHOULD use:
- timeout;
- watchdog;
- frame limit;
- log limit;
- checkpointing;
- partial-result persistence.

## UR-45 — Tool failure does not stop unrelated work
Document the failure, preserve evidence, switch to alternatives, and continue independent work.

---

# PART XV — METRICS AND COMPLETION PERCENTAGES

## UR-50 — No percentage without a defensible denominator
Never report a global completion percentage without a known total universe.

## UR-51 — Label the metric
Examples:

```text
inventory_coverage
confirmed_text_coverage
script_coverage
family_coverage
runtime_coverage
visual_coverage
global_coverage
```

## UR-52 — Inventory is not automatically global scope
`X translated / Y discovered candidates` is only an inventory percentage unless exhaustiveness is proven.

## UR-53 — Shift-JIS candidates are not a global denominator
Raw candidate counts MUST NOT automatically define project completion.

---

# PART XVI — REGRESSION CONTROL

## QG-80 — Validate against previous stable version
Each significant version SHOULD compare current behavior/output with the previous approved version.

## QG-81 — A fix may not create an equal-or-worse defect
A new correction is not accepted if it introduces an equivalent or more severe regression.

## QG-82 — Revalidate globally affected surfaces
Global changes to:
- font;
- renderer;
- common UI;
- shared tables;
- allocators;
- text engine

require revalidation of previously approved surfaces they may affect.

---

# PART XVII — TOOL AND EVIDENCE PROVENANCE

## UR-60 — Do not claim tools that were not used
Only attribute evidence to tools actually executed.

## UR-61 — Record methodology
Important results SHOULD record:
- tool;
- version;
- command;
- input;
- output;
- result.

## UR-62 — Tools are evidence sources, not unquestionable authorities
Automated output MUST be reconciled with structural/runtime evidence.

---

# PART XVIII — EVIDENCE PRESERVATION

## UR-70 — Preserve useful project history
When reasonable retain:
- CSV inventories;
- logs;
- rejected candidates;
- screenshots;
- save states;
- hashes;
- analyses;
- negative results;
- prior versions.

## UR-71 — Trace reclassification
If a candidate changes status, preserve:
- previous state;
- new state;
- reason;
- evidence;
- version.

## UR-72 — Negative results matter
Record disproven hypotheses to prevent future repetition.

---

# PART XIX — VERSIONING AND HANDOFF

## UR-80 — Versions must represent real changes
Do not increment versions without meaningful change in:
- ROM;
- sources;
- translation;
- tooling;
- QA;
- evidence.

## UR-81 — Changelog required
A formal version SHOULD state:
- what changed;
- what was fixed;
- what was validated;
- what remains pending.

## UR-82 — Explicit project state
Handoffs SHOULD identify:
- current version;
- original ROM;
- hashes;
- current phase;
- completed work;
- pending work;
- blockers;
- evidence;
- build instructions;
- patch instructions;
- recommended next step.

## UR-83 — Migration-ready project
Important work SHOULD be resumable in another chat/Work environment without relying exclusively on hidden prior context.

---

# PART XX — QUALITY GATE PER ELEMENT

An element may be considered FINAL_APPROVED only when all applicable checks pass:

```text
SOURCE_UNDERSTOOD       = PASS
SEMANTIC_ACCURACY       = PASS
TRANSLATION             = PASS
TERMINOLOGY             = PASS
LINGUISTIC_QUALITY      = PASS
INTEGRATION             = PASS
TYPOGRAPHY              = PASS
LAYOUT                  = PASS
DESIGN                  = PASS
VISUAL                  = PASS
FUNCTIONAL              = PASS
RUNTIME                 = PASS or JUSTIFIED_N/A
REGRESSION              = PASS
```

If an applicable mandatory field fails:

```text
FINAL_APPROVED = false
```

---

# PART XXI — RELEASE QUALITY GATE

Before declaring a release candidate or final translation:

```text
ROM_INTEGRITY           = PASS
CHECKSUM                = PASS
BUILD                   = PASS
BPS_ROUNDTRIP           = PASS

LANGUAGE                = PASS
TERMINOLOGY             = PASS
DESIGN                  = PASS
TYPOGRAPHY              = PASS
LAYOUT                  = PASS
UI_UX                   = PASS
GRAPHICS                = PASS
GAMEPLAY                = PASS
RUNTIME                 = PASS
REGRESSION              = PASS

CONFIRMED_JP_PENDING    = 0
BLOCKER_ISSUES          = 0
MAJOR_ISSUES            = 0
```

MINOR/POLISH issues MAY remain only when explicitly documented and the build is not misrepresented as defect-free.

---

# PART XXII — ISSUE SEVERITY

## BLOCKER
Examples:
- ROM does not boot;
- crash;
- broken save/load;
- blocked progression;
- severe corruption;
- functionally wrong text that prevents correct play.

## MAJOR
Examples:
- mistranslation;
- important omission;
- significant clipping;
- broken layout;
- missing UI element;
- wrong proper name;
- substantially degraded screen.

## MINOR
Examples:
- small centering issue;
- spacing defect;
- punctuation;
- minor alignment;
- non-functional consistency issue.

## POLISH
Optional refinement:
- optical centering;
- improved phrasing;
- minor pixel-art refinement;
- fine spacing adjustment.

---

# PART XXIII — GPT / AGENT OPERATING RULES

A GPT/agent working on these projects MUST treat quality as integrated product quality, not text replacement.

Before approving a change, evaluate:

```text
1. Is the meaning correct?
2. Is the terminology consistent?
3. Is it technically integrated correctly?
4. Does it preserve the original design intent?
5. Is typography correct?
6. Is layout balanced and readable?
7. Is it visually professional?
8. Is UI behavior intact?
9. Is gameplay intact?
10. Was it actually tested?
11. Did it introduce regressions?
12. Is the evidence sufficient for the claimed status?
```

Additional agent rules:

- Do NOT invent missing context.
- Do NOT mark doubtful text as approved.
- Do NOT prefer shorter wording solely because it fits.
- Do NOT modify placeholders/control codes blindly.
- Do NOT equate "no Japanese found" with "translation complete".
- Do NOT equate "build succeeds" with "quality approved".
- Do NOT equate "boots" with "runtime QA complete".
- Do NOT equate "inside box" with "good design".
- Do NOT equate mathematical centering with optical centering.
- Do NOT report synthetic validation as natural playthrough.
- Do NOT claim use of a tool that was not actually run.
- Preserve intermediate evidence and unresolved candidates.
- When blocked, change method instead of repeating indefinitely.

---

# PART XXIV — RECOMMENDED RECORD FORMAT

When practical, translation records SHOULD support:

```yaml
id:
offset:
resource:
consumer:
speaker:
context:

source_jp:
literal_gloss:
translation_en:

terminology_refs:
character_voice:

status:
confidence:

translated:
integrated:
runtime_confirmed:
linguistic_approved:
design_approved:
visual_approved:
functional_approved:
final_approved:

access_method:
issues:
notes:
evidence:
version:
```

---

# PART XXV — FINAL COMPLETION CRITERIA

A project MUST NOT be called 100% complete merely because no obvious Japanese remains.

A final-quality release SHOULD satisfy:

```text
structural census reasonably closed
+
confirmed Japanese pending = 0
+
ambiguous candidates classified/documented
+
linguistic review complete
+
terminology review complete
+
design review complete
+
typography/layout review complete
+
representative runtime QA complete
+
late-game/ending/credits reviewed
+
save/load tested when applicable
+
critical regressions = 0
+
checksum valid
+
build reproducible
+
cumulative BPS verified
+
complete cumulative sources present
+
handoff/documentation complete
```

---

# PART XXVI — RULE HIERARCHY

```text
Universal Rules (this file)
        ↓
Project-specific technical rules
        ↓
Phase-specific instructions
        ↓
Individual implementation decisions
```

Project-specific rules MAY be stricter.

They MUST NOT weaken this file.

If old documentation conflicts with reproducible evidence, investigate, document the discrepancy, and update the project knowledge explicitly.

---

# FINAL OPERATING PRINCIPLE

Every project SHOULD follow this sequence:

```text
KNOWN BASE
→ STRUCTURAL ANALYSIS
→ SOURCE UNDERSTANDING
→ NATURAL LOCALIZATION
→ SAFE INTEGRATION
→ DESIGN/TYPOGRAPHY REVIEW
→ RUNTIME QA
→ VISUAL QA
→ REGRESSION CONTROL
→ REPRODUCIBLE CUMULATIVE PATCH
→ PRESERVED EVIDENCE
→ RELEASE QUALITY GATE
```

Three non-negotiable principles:

```text
1. Integrated text is not automatically approved text.
2. Synthetic validation is not automatically a real playthrough.
3. Failure to find something is not proof that it does not exist.
```

And the final quality target is:

```text
NOT:
"Japanese game with English text inserted"

TARGET:
"A coherent English WonderSwan release that preserves the original game's
design, function, artistic identity and platform constraints."
```
