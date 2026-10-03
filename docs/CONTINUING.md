# Continuation guide

1. Build the frozen test version and verify its hash before editing.
2. Consult `translations/PENDING_REVIEW.json` and the complete resource inventory. Preserve aliases and undecoded formats; do not destructively filter candidates.
3. Review original Japanese/context before modifying a graphic. A compressed stream is not necessarily text.
4. For a result heading, edit `translations/headings.json`. Use only supported font glyphs and the existing field size.
5. For another compressed resource, export it from the current built ROM:

```sh
python3 tools/export_resource.py build/Densha_de_Go_2_EN_v0.4.17.ws 0x3D9BA4 translations/resources/example.raw
```

Edit the raw tile data with an appropriate 2bpp graphics workflow, preserving its byte length. Add an entry to `translations/resource_overrides.json`:

```json
[
  {
    "offset": "0x3D9BA4",
    "file": "translations/resources/example.raw",
    "reason": "Document the source, replacement and consumer here"
  }
]
```

Then build with `--development`. The importer checks known stream identity, original raw size, compression roundtrip and original compressed capacity. Duplicate overrides, including an override of a configured heading, are rejected. Resources requiring relocation or other formats need a separate researched implementation.

6. Test the actual consumer and neighboring shared tiles. Static atlas legibility alone is insufficient. Distinguish button input, timer freeze and explicit state injection in the ledger.
7. Use the short scripts first. After a bounded attempt fails to reach a screen, use documented tracing or minimal assisted state; do not repeat long runs indefinitely.
8. For a new release, update `project.json`, expected target hash, version, release notes, known issues, ledgers and evidence together. Rebuild from the original and verify cumulative plus incremental patches. Do not merely rename DEV output as a release.

## Priorities

- Visual review by environmental families and reliable transcription of signs/photos.
- Consolidate the historical translation ledger and review names/abbreviations.
- Directed tests of bonus/coupling, rare notices and ending branches.
- Close the release gates in `docs/TRANSLATION_RULES.md` before using an RC label.

The full private checkpoint contains the original/reference ROMs, complete runtime dumps and the 2,915-image environmental gallery. This public project retains inventories, scripts and representative evidence; original game resources can be exported locally from the user's ROM.
