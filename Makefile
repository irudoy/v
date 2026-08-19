SHELL := /bin/sh
.DEFAULT_GOAL := help

UV ?= uv
PYTHON ?= $(UV) run python
PYTEST ?= $(UV) run pytest
NODE ?= node
NPM ?= npm

ROM ?= JK08A
ROMS ?= JK08A
ROMVIZ_OUTPUT ?= tmp/romviz/jk08a-rom-atlas.html
CAN_DASHBOARD_VERSION := $(shell sed -n 's/^__version__ = "\([^"]*\)"/\1/p' tools/can_dashboard/__init__.py)
CAN_DASHBOARD_OUTPUT ?= tmp/vq-can-telemetry-v$(CAN_DASHBOARD_VERSION)-windows.zip
CAN_DASHBOARD_MACOS_OUTPUT ?= tmp/vq-can-telemetry-v$(CAN_DASHBOARD_VERSION)-macos-arm64.zip
CAN_DASHBOARD_MACOS_APP_OUTPUT ?= tmp/VQ CAN Telemetry.app
INPUT ?=
OUTPUT ?=
PROFILE ?=

PROFILE_OPTION = $(if $(strip $(PROFILE)),--profile "$(PROFILE)",)

.PHONY: help setup check test-python test-js test verify-firmware verify
.PHONY: romviz dashboard-package dashboard-package-macos defs-generate rom-verify rom-build

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
		'  rom-verify        Verify the unified ROM build in memory; requires INPUT.' \
		'  rom-build         Build the unified modified ROM; requires INPUT and OUTPUT.' \
		'' \
		'Variables:' \
		'  ROM               ROM series for definitions and ROM builds (default: JK08A).' \
		'  ROMS              Space-separated ROM models embedded in romviz (default: JK08A).' \
		'  ROMVIZ_OUTPUT     ROM atlas output path.' \
		'  CAN_DASHBOARD_OUTPUT  Windows dashboard ZIP path.' \
		'  CAN_DASHBOARD_MACOS_OUTPUT  macOS arm64 app ZIP path.' \
		'  CAN_DASHBOARD_MACOS_APP_OUTPUT  Unarchived macOS app path.' \
		'  INPUT             Input ROM path for rom-verify and rom-build.' \
		'  OUTPUT            Output ROM path for rom-build.' \
		'  PROFILE           Optional local unified-builder profile.'

setup:
	$(UV) sync --frozen

check:
	$(PYTHON) patches/can_telemetry_profile.py --check
	$(PYTHON) tools/mapkit/validate_map_switching.py
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
	@test -n "$(strip $(ROMS))" || { printf '%s\n' 'ROMS is required' >&2; exit 2; }
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
	$(PYTHON) tools/mapkit/emit_def.py "$(ROM)"
	$(PYTHON) tools/maps/build_tracker.py "$(ROM)"
	$(PYTHON) tools/mapkit/validate_map_switching.py

rom-verify:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	$(PYTHON) patches/build_rom.py "$(INPUT)" --rom "$(ROM)" $(PROFILE_OPTION) --verify-only

rom-build:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	@test -n "$(strip $(OUTPUT))" || { printf '%s\n' 'OUTPUT is required' >&2; exit 2; }
	$(PYTHON) patches/build_rom.py "$(INPUT)" --rom "$(ROM)" $(PROFILE_OPTION) --output "$(OUTPUT)"
