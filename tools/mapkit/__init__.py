# mapkit - calibration-annotation tools described in
# tools/map-analysis-pipeline.md.
#
# Before this package, image reads lived in session scratchpads. Every session
# recreated its own hexadecimal dump and element unpacking, leaving no common
# way to verify results. This package places the same operations in Git with one
# element declaration and one map geometry.
#
#   rom.py       - image registry, array reads, and measurement;
#   show.py      - map or axis in physical units from graph plus image;
#   ptrscan.py   - address candidate scan without Ghidra;
#   emit_def.py  - shared RomRaider/XDF definition projection from graph, DTC,
#                  and overrides (Stage 8, section 9);
#   presentation.py - shared functional-category presentation policy;
#   tunerpro.py  - TunerPro XDF rendering, patches, and masked conversions.
#
# Run modules as files (`python tools/mapkit/show.py ...`). Import with
# `from mapkit import rom` while `tools/` is on sys.path, as load_maps.py and the
# package scripts do.
