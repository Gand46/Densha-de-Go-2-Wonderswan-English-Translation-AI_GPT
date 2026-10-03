# v0.4.17-test — English translation test prerelease

**Status: playable test build. Not a complete-translation release candidate.**

This release repairs malformed RUN ABORTED and RUN ENDED headings. The GAME OVER artwork and gameplay code are unchanged from v0.4.16. All six courses are accessible through normal left/right course-selector pages; no unlock patch is required.

## Validation

- Reproducible build from the original Japanese ROM; exact cumulative and incremental BPS/IPS roundtrips.
- 60 coherent resource tables and 3,121 compressed streams checked, with no detected allocation overflow or decompressed-size change.
- 74 screenshots compared with v0.4.16: 69 identical; five changed only within the repaired headings.
- Additional short Mesen tests cover options, pause/resume, ending a run and continuing after a loss.
- RUN ABORTED tested through natural button input. RUN ENDED tested in its actual consumer via assisted substate injection; natural full completion remains unverified for that screen.

## Known limitations

Environmental signs/photos, inherited terminology/abbreviations, rare events and performance-dependent ending contexts remain under review. The project does not claim zero remaining Japanese or 100% translation completion. Windows/macOS execution and physical hardware have not been tested for this source packaging.

## Patch

Apply `Densha_de_Go_2_EN_v0.4.17_CUMULATIVE.bps` to the original Japanese 4,194,304-byte ROM:

- Original SHA-256: `3ec68e02fa964383d6a0792aca7e53ab005e17a768a8546eb6dc5ed482db7c29`
- Output SHA-256: `bf9db9f19abca263c7d90076037e41c8e27625da34ea9eba101762f777758513`
- Output checksum: `0x5C91`
- Cumulative BPS SHA-256: `c74d4d4dd1f72a23a791c0320e456b3d3a8b2aa0ce5a95d01c6a0385c0229c21`

Use the incremental patch only with exact v0.4.16. Original/translated ROMs and emulator binaries are not release assets.

When publishing on GitHub, mark this release as a **pre-release**, with tag `v0.4.17-test`.

The later targeted QA addendum records 16 scoped synthetic consumer passes and two scripted natural notice passes on this same ROM/BPS, with six scoped points not approved. See `docs/SYNTHETIC_QA_V0417.md`. This documentation update does not promote the build to RC. The accompanying publication package was prepared without a supplied original ROM, so rebuild and patch-to-ROM equivalence were not rerun during packaging.
