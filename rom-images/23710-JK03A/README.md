# 23710-JK03A package evidence

The forum package was imported on 2026-07-15 and contains two related source
artifacts:

- `1JK03A-20260715-stock.bin`, the SH7058 flash ROM;
- `ST95320-20260715-nats-sync.bin`, the external SPI EEPROM containing NATS
  synchronization/adaptation data.

The EEPROM is not MCU flash ROM and has no graph label. Its package association
with the ROM is the reason both source artifacts remain in this directory.

The package carries no ECU label transcription. A dismantler listing for the
exact part number records Hitachi hardware `MEC100-190` on a `DBA-V36`
registered 2007/2 with the `VQ25-HRTM` engine, 5AT `RE5R05A`, and FR drive,
which repeats the 2WD 5AT VQ25HR application the source post states and adds
the hardware identifier at marketplace-grade confidence.

Application source:

- https://autoparts.beforward.jp/detail/Computers---Sensors/Computers-Engine---ECU/PA33205361/

Identity, provenance, and stock hashes are authoritative in `../roms.csv` and
`../README.md`.
