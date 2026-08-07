# 23710-JK03A package evidence

The forum package was imported on 2026-07-15 and contains two related source
artifacts:

- `1JK03A-20260715-stock.bin`, the SH7058 flash ROM;
- `ST95320-20260715-nats-sync.bin`, the external SPI EEPROM containing NATS
  synchronization/adaptation data.

The EEPROM is not MCU flash ROM and has no graph label. Its package association
with the ROM is the reason both source artifacts remain in this directory.

Identity, provenance, and stock hashes are authoritative in `../roms.csv` and
`../README.md`.
