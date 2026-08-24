SHELL := /bin/sh
.DEFAULT_GOAL := help

UV ?= uv
PYTHON ?= $(UV) run python
PYTEST ?= $(UV) run pytest
NODE ?= node
NPM ?= npm

ROM ?= auto
ROMS ?= all
DEFS_ROM ?= all
ROMVIZ_OUTPUT ?= tmp/romviz/rom-atlas.html
CAN_DASHBOARD_VERSION := $(shell sed -n 's/^__version__ = "\([^"]*\)"/\1/p' tools/can_dashboard/__init__.py)
CAN_DASHBOARD_OUTPUT ?= tmp/vq-can-telemetry-v$(CAN_DASHBOARD_VERSION)-windows.zip
CAN_DASHBOARD_MACOS_OUTPUT ?= tmp/vq-can-telemetry-v$(CAN_DASHBOARD_VERSION)-macos-arm64.zip
CAN_DASHBOARD_MACOS_APP_OUTPUT ?= tmp/VQ CAN Telemetry.app
INPUT ?=
OUTPUT ?=
PROFILE ?=
CORRESPONDENCE_SOURCE_EXPORT ?=
CORRESPONDENCE_TARGET_EXPORT ?=
CORRESPONDENCE_OUTPUT ?=
CORRESPONDENCE_ARGS ?=

PROFILE_OPTION = $(if $(strip $(PROFILE)),--profile "$(PROFILE)",)

.PHONY: help setup check test-python test-js test verify-firmware verify
.PHONY: romviz dashboard-package dashboard-package-macos defs-generate runtime-targets-generate rom-correspondence rom-verify rom-build

help:
	@printf '%s\n' \
		'Usage: make <target> [VARIABLE=value]' \
		'' \
		'Targets:' \
		'  help              Show this help.' \
		'  setup             Synchronize the locked Python environment.' \
		'  check             Validate generated sources, definitions, and ROM atlas JavaScript.' \
		'  test-python       Run the complete Python test contract.' \
		'  test-js           Run pin-tracer tests and check ROM atlas JavaScript.' \
		'  test              Run the Python and JavaScript test contracts.' \
		'  verify-firmware   Run the repository-contained GNU SH-2E executable gate.' \
		'  verify            Run check, test, and verify-firmware in sequence.' \
		'  romviz            Rebuild the self-contained ROM atlas HTML.' \
		'  dashboard-package Build the portable Windows PCAN dashboard ZIP.' \
		'  dashboard-package-macos Build the native macOS PCAN dashboard app and ZIP.' \
		'  defs-generate     Regenerate XML, XDF, and the map ledger from Memgraph.' \
		'  runtime-targets-generate Rebuild GNU SH-2E payload locks for relocated ROMs.' \
		'  rom-correspondence Compare two Ghidra function-signature exports.' \
		'  rom-verify        Verify the unified ROM build in memory; requires INPUT.' \
		'  rom-build         Build the unified modified ROM; requires INPUT and OUTPUT.' \
		'' \
		'Variables:' \
		'  ROM               Exact ROM or auto detection for ROM builds (default: auto).' \
		'  DEFS_ROM          Definition target or all (default: all).' \
		'  ROMS              ROM models or all for romviz (default: all).' \
		'  ROMVIZ_OUTPUT     ROM atlas output path.' \
		'  CAN_DASHBOARD_OUTPUT  Windows dashboard ZIP path.' \
		'  CAN_DASHBOARD_MACOS_OUTPUT  macOS arm64 app ZIP path.' \
		'  CAN_DASHBOARD_MACOS_APP_OUTPUT  Unarchived macOS app path.' \
		'  INPUT             Input ROM path for rom-verify and rom-build.' \
		'  OUTPUT            Output ROM path for rom-build.' \
		'  PROFILE           Optional local unified-builder profile.' \
		'  CORRESPONDENCE_SOURCE_EXPORT  Source Ghidra export directory.' \
		'  CORRESPONDENCE_TARGET_EXPORT  Target Ghidra export directory.' \
		'  CORRESPONDENCE_OUTPUT  Optional function-correspondence CSV path.' \
		'  CORRESPONDENCE_ARGS  Optional additional correspondence arguments.'

setup:
	$(UV) sync --frozen

check:
	$(PYTHON) patches/rom_address_profiles.py --check
	$(PYTHON) patches/runtime_targets.py --check
	$(PYTHON) tools/mapkit/definition_projections.py --check
	$(PYTHON) patches/can_telemetry_profile.py --check
	$(PYTHON) tools/mapkit/validate_map_switching.py
	$(PYTHON) tools/romviz/build.py --check
	$(NODE) --check tools/romviz/app.js

test-python:
	$(PYTEST) -q

test-js:
	$(NODE) --check tools/romviz/app.js
	$(NPM) --prefix tools/pin-tracer test

test: test-python test-js

verify-firmware:
	tools/sh-elf-run/run.sh --verbose

verify:
	+$(MAKE) check
	+$(MAKE) test
	+$(MAKE) verify-firmware

romviz:
	@test -n "$(strip $(ROMVIZ_OUTPUT))" || { printf '%s\n' 'ROMVIZ_OUTPUT is required' >&2; exit 2; }
	$(PYTHON) tools/romviz/build.py $(ROMS) --output "$(ROMVIZ_OUTPUT)"

dashboard-package:
	@test -n "$(strip $(CAN_DASHBOARD_OUTPUT))" || { printf '%s\n' 'CAN_DASHBOARD_OUTPUT is required' >&2; exit 2; }
	$(PYTHON) tools/can_dashboard/package_windows.py --force --output "$(CAN_DASHBOARD_OUTPUT)"

dashboard-package-macos:
	@test -n "$(strip $(CAN_DASHBOARD_MACOS_OUTPUT))" || { printf '%s\n' 'CAN_DASHBOARD_MACOS_OUTPUT is required' >&2; exit 2; }
	@test -n "$(strip $(CAN_DASHBOARD_MACOS_APP_OUTPUT))" || { printf '%s\n' 'CAN_DASHBOARD_MACOS_APP_OUTPUT is required' >&2; exit 2; }
	$(UV) run --with-requirements tools/can_dashboard/requirements-macos-build.txt \
		python tools/can_dashboard/package_macos.py --force \
		--output "$(CAN_DASHBOARD_MACOS_OUTPUT)" \
		--app-output "$(CAN_DASHBOARD_MACOS_APP_OUTPUT)"

defs-generate:
	@test -n "$(strip $(DEFS_ROM))" || { printf '%s\n' 'DEFS_ROM is required' >&2; exit 2; }
	$(PYTHON) tools/mapkit/emit_def.py "$(DEFS_ROM)"
	$(PYTHON) tools/maps/build_tracker.py all
	$(PYTHON) tools/mapkit/validate_map_switching.py

runtime-targets-generate:
	tools/sh-elf-run/generate-targets.sh

rom-correspondence:
	@test -n "$(strip $(CORRESPONDENCE_SOURCE_EXPORT))" || { printf '%s\n' 'CORRESPONDENCE_SOURCE_EXPORT is required' >&2; exit 2; }
	@test -n "$(strip $(CORRESPONDENCE_TARGET_EXPORT))" || { printf '%s\n' 'CORRESPONDENCE_TARGET_EXPORT is required' >&2; exit 2; }
	$(PYTHON) tools/rom_correspondence.py \
		"$(CORRESPONDENCE_SOURCE_EXPORT)" \
		"$(CORRESPONDENCE_TARGET_EXPORT)" $(if $(strip $(CORRESPONDENCE_OUTPUT)),--output "$(CORRESPONDENCE_OUTPUT)",) $(CORRESPONDENCE_ARGS)

rom-verify:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	$(PYTHON) patches/build_rom.py "$(INPUT)" --rom "$(ROM)" $(PROFILE_OPTION) --verify-only

rom-build:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	@test -n "$(strip $(OUTPUT))" || { printf '%s\n' 'OUTPUT is required' >&2; exit 2; }
	$(PYTHON) patches/build_rom.py "$(INPUT)" --rom "$(ROM)" $(PROFILE_OPTION) --output "$(OUTPUT)"
