# Densha de Go! 2 — English translation

**v0.4.17-test · playable test prerelease · not a complete-translation RC.**

An English translation project for the monochrome WonderSwan version of Densha de Go! 2. This repository reproduces the verified v0.4.17 ROM and provides the source, resource inventory and QA scripts needed to continue the translation.

The current ROM passes the documented structural checks, reproducible-build checks and selected Mesen tests. Environmental signage, terminology and some rare-event contexts remain under review. See [known issues](docs/KNOWN_ISSUES.md), [continuation guide](docs/CONTINUING.md) and [QA scope](qa/README.md).

The targeted [synthetic QA addendum](docs/SYNTHETIC_QA_V0417.md) records 16 scoped `PASS_SYNTHETIC` consumer results and two scripted natural notice results. Coupling, an additional warning descriptor, and the full language/visual audit remain open. The ROM and cumulative BPS are unchanged.

## Apply the test release

Use `patches/Densha_de_Go_2_EN_v0.4.17_CUMULATIVE.bps` with an unmodified Japanese ROM:

- Size: **4,194,304 bytes**
- Original SHA-256: `3ec68e02fa964383d6a0792aca7e53ab005e17a768a8546eb6dc5ed482db7c29`
- Patched SHA-256: `bf9db9f19abca263c7d90076037e41c8e27625da34ea9eba101762f777758513`
- Patched WonderSwan checksum: `0x5C91`

The incremental patch requires the exact v0.4.16 ROM, SHA-256 `643363ab9f8d5c466a0e01ca14b22a4c8e65d76c7a5bb927139ec8e755a45f3b`.

## Build

Requires **Python 3.10+**, standard library only. Put your own original ROM at `roms/original.ws`, or provide its path explicitly. ROMs and emulator executables are not bundled in the public repository.

Windows:

```bat
BUILD_WINDOWS.bat "C:\My ROMs\Densha de Go 2 Japan.ws"
```

Linux/macOS:

```sh
python3 tools/build.py "/path/to/original.ws"
```

Outputs go to `build/`: translated ROM, four BPS/IPS patches and a JSON build report. The original ROM is read without being modified. The normal build verifies the exact release SHA-256 before writing output. Validation remains active under Python `-O`.

The clean constructor was tested on Linux, including a directory containing spaces and `ñ`. The Windows BAT is included; execution on Windows/macOS has not been verified.

## Project layout

| Path | Purpose |
|---|---|
| `tools/build.py`, `tools/codec.py` | Active portable constructor and graphics codec |
| `assets/baseline_v0416_cumulative.ips` | Hash-checked cumulative historical translation baseline |
| `translations/headings.json` | Editable v0.4.17 result headings |
| `translations/resource_overrides.json` | Additional compressed-resource overrides for DEV builds |
| `translations/GLOBAL_RESOURCE_INVENTORY.json` | Complete table-reference inventory, including aliases |
| `translations/TRANSLATION_LEDGER.json` | Recent corrections and their distinct approval stages |
| `translations/PENDING_REVIEW.json` | Unresolved context/terminology records |
| `qa/scripts/`, `qa/reports/`, `qa/evidence/` | Bounded emulator tests and selected evidence |
| `archive/builders/` | Recovered historical builders, retained for reference |
| `patches/` | Frozen v0.4.17 release patches |

The build is cumulative and needs no intermediate ROM. Historical translations are represented by the baseline patch; **not every historical text has a recovered editable text record or builder**. The archived builders contain legacy paths/dependencies and are not the active build chain. The resource override workflow allows continued work on those inherited graphics.

## Verify without writing a ROM

```sh
python3 tools/check_release.py "/path/to/original.ws"
```

Windows: `VERIFY_WINDOWS.bat "C:\My ROMs\Densha de Go 2 Japan.ws"`.

To apply the cumulative BPS with the bundled Python applicator:

```bat
APPLY_WINDOWS.bat "C:\My ROMs\Densha de Go 2 Japan.ws" "C:\My ROMs\Densha English.ws"
```

The applicator rejects incorrect source hashes and existing output files.

## Continue development

Follow [CONTRIBUTING.md](CONTRIBUTING.md). Intentional edits use:

```sh
python3 tools/build.py "/path/to/original.ws" --development
```

Development outputs have `_DEV` in their filenames; this bypasses only the final frozen-release SHA check. Source-ROM identification, baseline validation, size/capacity checks and patch roundtrips remain enforced.

See [docs/CONTINUING.md](docs/CONTINUING.md) for graphics export and override instructions. Do not infer translated-text counts from graphical resource counts.

## Short emulator tests

The optional runner currently supports Linux. Supply an existing Mesen executable:

```sh
python3 tools/run_mesen.py --mesen "/path/to/Mesen" --name options_check --mode options
python3 tools/run_mesen.py --mesen "/path/to/Mesen" --name pause_check --frames 6200 --lua qa/scripts/pause_resume.lua
```

The runner uses 85-second internal and 90-second supervisory limits. Results go to ignored `qa/generated/`. Supply a new output name for each run. Some scripts intentionally inject state; [qa/README.md](qa/README.md) distinguishes them from button-only tests.

## GitHub release

Suggested tag: **`v0.4.17-test`**, marked **pre-release**. The prepared release text is [docs/RELEASE_NOTES.md](docs/RELEASE_NOTES.md). Attach the cumulative BPS, optionally the incremental BPS/IPS and checksums. See [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md).

No remote repository or release has been published by this package. See [NOTICE.md](NOTICE.md) for licensing scope and third-party notices.

## Technical architecture and findings index

The active constructor applies a hash-checked historical v0.4.16 IPS baseline directly to the identified Japanese ROM, then redraws two compressed 2bpp heading atlases. It checks the original decoded lengths and allocation capacities, changes only the two known streams and checksum, and verifies the frozen target SHA-256. The historical baseline preserves translation work for which individual editable strings have not all been recovered. No game-code modification or relocation is part of the v0.4.17 heading fix.

The [technical findings and consumer map](docs/TECHNICAL_FINDINGS.md) records each confirmed address in its proper ROM, segmented execution, WRAM or tilemap address space, with evidence and unresolved consumers. The full [resource inventory](translations/GLOBAL_RESOURCE_INVENTORY.json) covers 60 tables and 3,731 references with aliases, including 3,121 unique compressed streams. These are resource counts rather than a translation denominator. The relevant consumer paths include `F000:33DD` → `E000:C186` for RUN ABORTED, `F000:3A53` for RUN ENDED, `F000:794C` for BONUS and `F000:660B` → `F000:6636` for PENALTY!. Eight rare notices were shown through the actual notice consumer by guarded WRAM descriptor substitution; their normal gameplay triggers remain unproven.

The [organization and verification record](docs/PACKAGING_MANIFEST.md) identifies retained files, excluded materials and this packaging session's checks. Original Spanish engineering reports are retained as primary evidence; the English technical index consolidates their release-relevant findings. Vendored patch tools retain their MIT notice; no repository-wide license is asserted.

## Current packaging verification

The separately supplied cumulative BPS has SHA-256 `c74d4d4dd1f72a23a791c0320e456b3d3a8b2aa0ce5a95d01c6a0385c0229c21`, matches the source archive's BPS byte for byte, and passes its internal patch CRC (`0xE0EBC4DD`). It declares source and target sizes of 4,194,304 bytes; its embedded source/target CRC32 values are `0xAF9D8F42` / `0xD58F0E5B`. The SHA-256 values above are documented in `project.json` and prior reports, not recalculated from ROM bytes in this packaging session: the private original ROM was not supplied. Rebuild from source, BPS application to that ROM, output byte comparison and emulator execution in this packaging session are **NOT_RUN**. The prior results are retained with their evidence and scope.
