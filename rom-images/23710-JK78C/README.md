# 23710-JK78C source evidence

The image was imported on 2026-07-15. No RomRaider thread for this part number
was found, so the application comes from part-number catalogs, where the
`23710-JK7xC` series denotes a 2008 Infiniti G37 3.7L and the replacement list
for the original `23710-JK78B` names `JK78C`. That identification is
catalog-grade. The package carries the flash image alone: no ECU label
transcription, no PCMFlash identification record, and no external EEPROM read.

ROM strings give the calibration `1JK78C00000` and the SH7058 type, which the
PCMFlash module 18 USDM listing `EFI SH70582xN (Hitachi SH7058/1MB)`
independently covers. The image is one of the three that populate both identity
blocks, and the two blocks carry different software strings. No PCMFlash read of
a `23710-JK78C` ECU exists to establish which one the tool reports, so the
target identity in `../../defs/rom-identities.toml` keeps `caseid = "Unknown"`
rather than selecting one by analogy. Both strings are in
`../README.md#identity-strings`.

No second image in the collection reaches exact-code or near-code similarity
with `JK78C`, so it carries its own reviewed address layout. The family
boundary and its byte evidence are in `../homology.toml`, and the source links
are in `../README.md#sources`.

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`.
