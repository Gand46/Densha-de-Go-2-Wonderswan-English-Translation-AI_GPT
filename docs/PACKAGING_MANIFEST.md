# Packaging manifest — v0.4.17-test

Source input: `Densha_de_Go_2_EN_v0.4.17_TEST_SYNTHETIC_QA_SOURCE.zip` (the more complete of the two supplied source checkpoints). The older `Densha_de_Go_2_EN_v0.4.17_TEST_GitHub_Source.zip` lacks the later synthetic evidence; it is not stacked onto the newer version. The separate supplied BPS was compared byte for byte with `patches/Densha_de_Go_2_EN_v0.4.17_CUMULATIVE.bps`. The release assets input was used as a cross-check and not copied wholesale, because it contains supplemental incremental and IPS patches.

The full per-file disposition appears in [`SOURCE_DISPOSITION.csv`](SOURCE_DISPOSITION.csv). The existing project root is maintained to preserve build and QA paths.

| Source path or class | Final location / decision | Reason |
|---|---|---|
| `tools/`, `vendor/ws_patch_tools/`, `project.json` | Same paths | Active constructor, patch codecs and exact ROM hashes; vendor license retained. |
| `assets/baseline_v0416_cumulative.ips`, `assets/font5x7.json`, `translations/` | Same paths | Required cumulative baseline, glyph source and active edits/inventory. The baseline patch is a necessary historical dependency; the original ROM remains external. |
| `archive/builders/` | Same paths, historical only | Source of unique earlier engineering findings; older builders are not the active build and may refer to absent prior ROMs. |
| `qa/`, `docs/`, project Markdown | Same paths, plus this manifest and `TECHNICAL_FINDINGS.md` | Recorded evidence, QA scripts, continuity and English technical index. Existing Spanish reports retain primary provenance. Some historical paths point to private evidence omitted from this public package. |
| `patches/` | Same paths in source | Frozen cumulative build outputs and supplemental patch history used by existing verification/docs. The separate release ZIP distributes only the cumulative BPS. |
| Original and patched ROMs, BIOS, firmware, savestates, SRAM, EEPROM, emulator executables, private galleries | Excluded / never present in the selected public source input | User supplies the exact original ROM outside this repository. |
| `SOURCE_SHA256SUMS.txt` | Regenerated at the same path | Previous manifest preceded the added documentation. It lists source-tree files except itself. |

## Checks in this packaging session

- Both supplied source ZIPs and the release ZIP had readable member directories; the selected source archive was extracted. No nested archive members or 4 MiB ROM-like member were found in the selected public tree. Files were also scanned by signature, size and extension; all public files are code, JSON/text, screenshots, license or patch data. An automated scan does not establish licensing of every derived pixel asset.
- Supplied standalone cumulative BPS and selected source BPS are byte-identical, SHA-256 `c74d4d4dd1f72a23a791c0320e456b3d3a8b2aa0ce5a95d01c6a0385c0229c21`. Embedded BPS patch CRC recomputed successfully; source and target each declare 4,194,304 bytes. Source CRC32 `0xAF9D8F42`, target CRC32 `0xD58F0E5B` are internal BPS metadata, not substitutes for SHA-256.
- Build scripts were inspected for active dependencies and paths. Python syntax, JSON syntax, ZIP integrity, documented relative links and source manifest are checked for this package. The original Japanese ROM is not among the supplied files, so **source rebuild, BPS application to original, byte-exact equivalence and a new runtime test are NOT_RUN here**. Historical `qa/reports/BUILD_VALIDATION.json` and `qa/reports/CLEAN_REPRODUCTION.json` report those prior checks; they are not claimed as fresh execution.
- `project.json` documents original SHA-256 `3ec68e02fa964383d6a0792aca7e53ab005e17a768a8546eb6dc5ed482db7c29` and target SHA-256 `bf9db9f19abca263c7d90076037e41c8e27625da34ea9eba101762f777758513`. Those hashes were not recalculated from ROM bytes in this session.

No GitHub repository, tag or release was created. Publish this checkpoint as a prerelease only. Outstanding linguistic, visual and contextual work remains in `docs/KNOWN_ISSUES.md` and `docs/TECHNICAL_FINDINGS.md`.
