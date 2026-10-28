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
CAN_DASHBOARD_NAME := $(shell sed -n 's/^PRODUCT_NAME = "\([^"]*\)"/\1/p' tools/can_dashboard/__init__.py)
CAN_DASHBOARD_SLUG := $(shell sed -n 's/^PRODUCT_SLUG = "\([^"]*\)"/\1/p' tools/can_dashboard/__init__.py)
CAN_DASHBOARD_VERSION := $(shell sed -n 's/^__version__ = "\([^"]*\)"/\1/p' tools/can_dashboard/__init__.py)
CAN_DASHBOARD_OUTPUT ?= tmp/$(CAN_DASHBOARD_SLUG)-v$(CAN_DASHBOARD_VERSION)-windows.zip
CAN_DASHBOARD_MACOS_OUTPUT ?= tmp/$(CAN_DASHBOARD_SLUG)-v$(CAN_DASHBOARD_VERSION)-macos-arm64.zip
CAN_DASHBOARD_MACOS_APP_OUTPUT ?= tmp/$(CAN_DASHBOARD_NAME).app
CAN_DASHBOARD_MACOS_BUILD_ENV ?= tmp/$(CAN_DASHBOARD_SLUG)-macos-build-env
INPUT ?=
OUTPUT ?=
PROFILE ?=
CALIBRATION ?=
REPLACE_SETTINGS ?=
CORRESPONDENCE_SOURCE_EXPORT ?=
CORRESPONDENCE_TARGET_EXPORT ?=
CORRESPONDENCE_OUTPUT ?=
CORRESPONDENCE_ARGS ?=

PROFILE_OPTION = $(if $(strip $(PROFILE)),--profile "$(PROFILE)",)
CALIBRATION_OPTION = $(if $(strip $(CALIBRATION)),--calibration "$(CALIBRATION)",)

.PHONY: help setup check test-python test-js test verify-firmware verify-npkern verify vendor-catalog
.PHONY: test-python-fast test-full test-changed
.PHONY: romviz dashboard-package dashboard-package-macos defs-generate runtime-targets-generate telemetry-update rom-correspondence census-homology rom-verify rom-build rom-extract rom-calibrate preflash

help:
	@printf '%s\n' \
		'Usage: make <target> [VARIABLE=value]' \
		'' \
		'Targets:' \
		'  help              Show this help.' \
		'  setup             Install dependencies, initialize pinned references, and build the graph.' \
		'  check             Validate versions, tracked sources, L0 exports, projections, and the' \
		'                    firmware architecture model, and rebuild the ROM atlas from them.' \
		'  test-python       Run the complete Python test contract.' \
		'  test-python-fast  Run Python tests without the slow marker.' \
		'  test-js           Run the pin-tracer test contract.' \
		'  test              Run fast Python tests and the JavaScript contract.' \
		'  test-full         Run the complete Python and JavaScript contracts.' \
		'  test-changed      Run the fast tests that tools/test-map.toml selects for the paths' \
		'                    changed against origin/master; an unmapped path runs make test.' \
		'  verify-firmware   Run the repository-contained GNU SH-2E executable gate.' \
		'  verify-npkern     Run the optional exact-revision external npkern gate.' \
		'  verify            Qualify firmware evidence, then run check and test-full.' \
		'  vendor-catalog    Rebuild the machine-readable vendor catalog.' \
		'  romviz            Rebuild the self-contained ROM atlas HTML.' \
		'  dashboard-package Build the portable Windows PCAN dashboard ZIP.' \
		'  dashboard-package-macos Build the native macOS PCAN dashboard app and ZIP.' \
		'  defs-generate     Regenerate XML, XDF, and the map ledger from Memgraph.' \
		'  runtime-targets-generate Rebuild GNU SH-2E payload locks for relocated ROMs.' \
		'  telemetry-update  Derive the JK08A CAN telemetry layout locks and payload manifest' \
		'                    from the telemetry sources, then rebuild the relocated payloads.' \
		'  rom-correspondence Compare the function-signature exports of two layouts.' \
		'  census-homology   Regenerate the 1ND0A-1ME3B table-level census correspondence from L0.' \
		'  rom-verify        Verify the unified ROM build in memory; requires INPUT.' \
		'  rom-build         Build the unified modified ROM; requires INPUT and OUTPUT.' \
		'  rom-extract       Extract the calibration and build profile of a ROM; requires INPUT.' \
		'  rom-calibrate     Apply a calibration file over a fresh build; requires INPUT, CALIBRATION, and OUTPUT.' \
		'  preflash          Qualify a built image of one ROM for flashing; requires INPUT and an exact ROM.' \
		'' \
		'Variables:' \
		'  ROM               Exact ROM or auto detection for ROM builds (default: auto); exact for preflash.' \
		'  DEFS_ROM          Definition target or all (default: all).' \
		'  ROMS              ROM models or all for romviz (default: all).' \
		'  ROMVIZ_OUTPUT     ROM atlas output path.' \
		'  CAN_DASHBOARD_OUTPUT  Windows dashboard ZIP path.' \
		'  CAN_DASHBOARD_MACOS_OUTPUT  macOS arm64 app ZIP path.' \
		'  CAN_DASHBOARD_MACOS_APP_OUTPUT  Unarchived macOS app path.' \
		'  CAN_DASHBOARD_MACOS_BUILD_ENV  macOS build environment created from the build lock.' \
		'  INPUT             Input ROM path for rom-verify, rom-build, rom-extract, rom-calibrate, and preflash.' \
		'  OUTPUT            Output ROM path for rom-build and rom-calibrate.' \
		'  PROFILE           Local unified-builder profile: optional rom-build input, rom-extract output.' \
		'  UPGRADE           Set for rom-build to preserve calibration and settings from an existing complete image.' \
		'  CALIBRATION       Local calibration file: rom-extract output, rom-calibrate input.' \
		'  REPLACE_SETTINGS  Non-empty to let rom-calibrate replace the extracted settings.' \
		'  CORRESPONDENCE_SOURCE_EXPORT  Source export directory, such as l0/<layout>.' \
		'  CORRESPONDENCE_TARGET_EXPORT  Target export directory, such as l0/<layout>.' \
		'  CORRESPONDENCE_OUTPUT  Optional function-correspondence CSV path.' \
		'  CORRESPONDENCE_ARGS  Optional additional correspondence arguments.' \
		'  UV, PYTHON, PYTEST  Python entry points (default: uv, uv run python, uv run pytest).' \
		'  NODE, NPM         JavaScript entry points (default: node, npm).' \
		'  GHIDRA_HOME, GHIDRA_JAVA_HOME  Ghidra and JDK >= 21 roots; unset paths use Homebrew.' \
		'  VQ_SH_ELF_IMAGE   Local GNU gate image tag in the default Docker context.' \
		'  VQ_SH_ELF_SKIP_BUILD  Set to 1 to reuse the image after its input-label check.' \
		'  VQ_SH_ELF_STOCK_TIMEOUT_SECONDS  Bounded ignition-consumer timeout; validated by run.sh.' \
		'  VQ_NPKERN_SOURCE  External npkern checkout for verify-npkern.'

setup:
	$(UV) sync --frozen
	git submodule update --init --recursive
	$(UV) run kb instance up
	$(UV) run kb sync

check:
	$(PYTHON) tools/check_projection_contract.py
	$(PYTHON) tools/version_index.py --check
	$(PYTHON) tools/can_dashboard/package_locks.py --check
	$(PYTHON) tools/vendor/build_catalog.py --check
	$(PYTHON) tools/diagnostics/extract_rom_dtc.py --check
	$(PYTHON) tools/diagnostics/import_370z_logger.py --check
	$(PYTHON) tools/diagnostics/import_ecudocs.py --check
	$(PYTHON) tools/single_source.py --check
	$(PYTHON) patches/rom_address_profiles.py --check
	$(PYTHON) patches/runtime_targets.py --check
	$(PYTHON) tools/mapkit/dtc_projection.py --check
	$(PYTHON) tools/mapkit/definition_projections.py --check
	$(PYTHON) tools/mapkit/presentation_audit.py --check
	$(PYTHON) tools/census_homology.py --check
	$(PYTHON) tools/rom_homology.py --check
	$(UV) run kb check
	$(PYTHON) tools/mapkit/emit_def.py all --check
	$(PYTHON) tools/maps/build_tracker.py all --check
	$(PYTHON) patches/can_telemetry_profile.py --check
	$(PYTHON) tools/can_dashboard/feed_table.py --check
	tools/sh-elf-run/generate-targets.sh --rolling --check
	tools/sh-elf-run/generate-targets.sh --telemetry --check
	tools/sh-elf-run/generate-targets.sh --check
	$(PYTHON) tools/mapkit/validate_map_switching.py
	$(PYTHON) tools/romviz/architecture.py check
	$(PYTHON) tools/romviz/build.py all --output "$(ROMVIZ_OUTPUT)"
	$(NODE) --check tools/romviz/architecture.js
	$(NODE) --check tools/romviz/app.js

test-python:
	$(PYTEST) -q

test-python-fast:
	$(PYTEST) -q -m "not slow"

test-js:
	$(NPM) --prefix tools/pin-tracer test

test: test-python-fast test-js

test-full: test-python test-js

test-changed:
	$(PYTHON) tools/changed_tests.py --pytest "$(PYTEST)" --npm "$(NPM)" --make "$(MAKE)"

verify-firmware:
	tools/sh-elf-run/run.sh --verbose

verify-npkern:
	tools/sh-elf-run/run-npkern.sh --verbose

vendor-catalog:
	$(PYTHON) tools/vendor/build_catalog.py

verify:
	+$(MAKE) verify-firmware
	+$(MAKE) check
	+$(MAKE) test-full

romviz:
	@test -n "$(strip $(ROMVIZ_OUTPUT))" || { printf '%s\n' 'ROMVIZ_OUTPUT is required' >&2; exit 2; }
	$(PYTHON) tools/romviz/build.py $(ROMS) --output "$(ROMVIZ_OUTPUT)"

dashboard-package:
	@test -n "$(strip $(CAN_DASHBOARD_OUTPUT))" || { printf '%s\n' 'CAN_DASHBOARD_OUTPUT is required' >&2; exit 2; }
	$(PYTHON) tools/can_dashboard/package_windows.py --force --output "$(CAN_DASHBOARD_OUTPUT)"

dashboard-package-macos:
	@test -n "$(strip $(CAN_DASHBOARD_MACOS_OUTPUT))" || { printf '%s\n' 'CAN_DASHBOARD_MACOS_OUTPUT is required' >&2; exit 2; }
	@test -n "$(strip $(CAN_DASHBOARD_MACOS_APP_OUTPUT))" || { printf '%s\n' 'CAN_DASHBOARD_MACOS_APP_OUTPUT is required' >&2; exit 2; }
	@test -n "$(strip $(CAN_DASHBOARD_MACOS_BUILD_ENV))" || { printf '%s\n' 'CAN_DASHBOARD_MACOS_BUILD_ENV is required' >&2; exit 2; }
	$(PYTHON) tools/can_dashboard/package_macos.py --prepare-environment "$(CAN_DASHBOARD_MACOS_BUILD_ENV)"
	"$(CAN_DASHBOARD_MACOS_BUILD_ENV)/bin/python" tools/can_dashboard/package_macos.py --force \
		--output "$(CAN_DASHBOARD_MACOS_OUTPUT)" \
		--app-output "$(CAN_DASHBOARD_MACOS_APP_OUTPUT)"

defs-generate:
	@test -n "$(strip $(DEFS_ROM))" || { printf '%s\n' 'DEFS_ROM is required' >&2; exit 2; }
	$(PYTHON) tools/mapkit/dtc_projection.py --write
	$(PYTHON) tools/mapkit/emit_def.py "$(DEFS_ROM)"
	$(PYTHON) tools/maps/build_tracker.py all
	$(PYTHON) tools/mapkit/validate_map_switching.py

runtime-targets-generate:
	tools/sh-elf-run/generate-targets.sh

telemetry-update:
	@$(UV) run kb project --check patches/can-telemetry-profile.toml || { printf '%s\n' 'regenerate it with uv run kb project patches/can-telemetry-profile.toml' >&2; exit 1; }
	$(PYTHON) patches/can_telemetry_profile.py --check
	tools/sh-elf-run/generate-targets.sh --telemetry --update
	tools/sh-elf-run/generate-targets.sh

rom-correspondence:
	@test -n "$(strip $(CORRESPONDENCE_SOURCE_EXPORT))" || { printf '%s\n' 'CORRESPONDENCE_SOURCE_EXPORT is required' >&2; exit 2; }
	@test -n "$(strip $(CORRESPONDENCE_TARGET_EXPORT))" || { printf '%s\n' 'CORRESPONDENCE_TARGET_EXPORT is required' >&2; exit 2; }
	$(PYTHON) tools/rom_correspondence.py \
		"$(CORRESPONDENCE_SOURCE_EXPORT)" \
		"$(CORRESPONDENCE_TARGET_EXPORT)" $(if $(strip $(CORRESPONDENCE_OUTPUT)),--output "$(CORRESPONDENCE_OUTPUT)",) $(CORRESPONDENCE_ARGS)

census-homology:
	$(PYTHON) tools/census_homology.py$(if $(strip $(CORRESPONDENCE_SOURCE_EXPORT)), --source-export "$(CORRESPONDENCE_SOURCE_EXPORT)",)$(if $(strip $(CORRESPONDENCE_TARGET_EXPORT)), --target-export "$(CORRESPONDENCE_TARGET_EXPORT)",)

rom-verify:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	$(PYTHON) patches/build_rom.py "$(INPUT)" --rom "$(ROM)" $(PROFILE_OPTION) --verify-only

rom-build:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	@test -n "$(strip $(OUTPUT))" || { printf '%s\n' 'OUTPUT is required' >&2; exit 2; }
	$(PYTHON) patches/build_rom.py "$(INPUT)" --rom "$(ROM)" $(PROFILE_OPTION) --output "$(OUTPUT)"$(if $(strip $(UPGRADE)), --upgrade,)

rom-extract:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	$(PYTHON) patches/extract_calibration.py "$(INPUT)" --rom "$(ROM)" $(CALIBRATION_OPTION) $(PROFILE_OPTION)

rom-calibrate:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	@test -n "$(strip $(CALIBRATION))" || { printf '%s\n' 'CALIBRATION is required' >&2; exit 2; }
	@test -n "$(strip $(OUTPUT))" || { printf '%s\n' 'OUTPUT is required' >&2; exit 2; }
	$(PYTHON) patches/apply_calibration.py "$(INPUT)" --calibration "$(CALIBRATION)" --output "$(OUTPUT)"$(if $(strip $(REPLACE_SETTINGS)), --replace-settings,)

preflash:
	@test -n "$(strip $(INPUT))" || { printf '%s\n' 'INPUT is required' >&2; exit 2; }
	@test "$(ROM)" != auto || { printf '%s\n' 'ROM must name the exact ROM of the image' >&2; exit 2; }
	$(PYTHON) patches/preflash.py "$(INPUT)" --rom "$(ROM)" --pytest "$(PYTEST)"
