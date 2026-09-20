# 23710-1ND3B source evidence

The image was imported on 2026-07-15 from the RomRaider forum thread t=22328,
"Does anyone have the CKV36 file? (237101ND3B)". The package carries the flash
image alone: no ECU label transcription, no PCMFlash identification record, and
no external EEPROM read.

ROM strings identify the image directly and are tabulated in
`../README.md#identity-strings`. The software identifier is shared with
`1ND0A`, so it does not separate the two images; the calibration string
does.

The part-number-to-CKV36 association and the model year come from the thread
and remain forum-grade. The delta between `1ND0A` and `1ND3B` - model year,
trim, and revision - is unknown, and neither exact model year is established.

The two `1ND` images form an exact-code family and share one reviewed address
layout while retaining independent identities and stock calibration values.
The family boundary and its byte evidence are in `../homology.toml`, and the
source links are in `../README.md#sources`.

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`.
