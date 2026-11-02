"""Extraction recognizes the current and registered historical runtimes.

Every case starts from a current builder output with the built-in profile and
turns it into a registered earlier endpoint, an editor-edited runtime, or a
partial state.
"""

from dataclasses import replace
from functools import lru_cache
from unittest import mock

import pytest

from patches import apply_calibration
from patches import build_rom
from patches import calibration_ranges
from patches import can_telemetry
from patches import extract_calibration
from patches import preflash
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_endpoints
from patches import runtime_targets


pytestmark = pytest.mark.slow

# Exact engine bytes of the last RPM-hold endpoint, which holds through the
# fuel-cut coordinator wrapper.
SCHEMA_3_ENGINE = bytes.fromhex(
    "4f22d586e000815a6050880089058801890588028905a0db0009a0040009a03f"
    "0009a09800098454e10530128910845520088b0d8553600d20088b098554600d"
    "20088b05b0fa000920088903a0d00009a0be0009d571d47260408054d4718443"
    "8055e00081538154815bd46f6241622d60238155d46b85476303633d323ce3ff"
    "633d33228900623360238156d069400b0009d562e0012500b2420009a0a80009"
    "84546203e105321289098455e103301289058554600d20088b01a0020009a087"
    "0009b0bb0009d555d4556240845432008903e0118051a0330009d45284436203"
    "845532008903e0128051a029000984512008890dd44e604088088b03e00f8051"
    "a01e000988208b1be0078051a018000985536203622d7201622dd44285496303"
    "633d32328b06e00e80518452c9f78052a006000960238153b1f20009a0580009"
    "d536e0008154815b8452c90f8052e0022500a04d00098454e105301289388455"
    "e103301289348554600d9165611d3012892eb16b000920088921d42d60408820"
    "8b18d52685546203622d7201622dd425854a6303633d32328b08e00025008052"
    "8053805581538154a022000960238154a01e0009d519e0008154a0190009d517"
    "e0018051e000805280538154a0100009e400d016400b0009d5106153e000e206"
    "2102710442108bfbe0022500e01080514f26000b0009ffffffffffffffffffff"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff5d40"
    "ffff5d00000d3f60ffff11bc000d3660ffff2a85000d41408000ffff4f22d573"
    "e000805180528053b10000096703200889048453cb018053a0020009e0018051"
    "d46b6240622ce10532128b06845120088b17e0028051a01400092778890c6023"
    "d164021cd16484142029200889048453cb028053a0050009845120088b01e003"
    "8051d45b844163038442230b8443203b20088b048453cb048053a00500098451"
    "20088b01e004805161437104601220088b048453cb088053a005000984512008"
    "8b01e0058051d44d6040c8808b048453cb108053a0050009845120088b01e006"
    "8051d447604088028b048453cb208053a0050009845120088b01e00880512778"
    "890cd4406240622cd43b8448600c32028b048453cb408053a005000984512008"
    "8b01e00980512778890cd4376241622dd4318545600d32028b048453cb808053"
    "a0050009845120088b01e00a80512778890cd42e6241622dd4278546600d3202"
    "8b048452cb018052a0050009845120088b01e00b805127788910d4256240622c"
    "d41d8446600c32028b088447600c30228b048452cb028052a005000984512008"
    "8b01e00c8051277889028452cb0880528451600c4f26000b0009ffffffffffff"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    "ffffffffffffffffffffffffffff5d40ffff5d00000d3d18000d3f60ffff41ae"
    "ffff2a85ffff110effff11bcffff2672ffff10770102040810ffffffffffffff"
    "ffffffffffffffffffffffffd3536031600d91ab611d30108b5f843288038b5c"
    "8433e103301289588434c9e020088b54843520088b5184366203622c8437600c"
    "30228b4a8439610c2118894685356203622d2228894185376403644d2448893c"
    "34128b3a623372106024610c211889346020620c32128b303242892e8539600d"
    "2008892a9175611d30128926853a600d200889223012892064337416e2056044"
    "600ce16e30128b18e1763012891542108bf560402008891074016041600d9156"
    "611d30108b0974026041600d9150611d30108b02e001000b0009e000000b0009"
    "d51f8452cb1063038455620322288921d41c6141611d8556600d31028b03e001"
    "815ba00600098557600d31028901e000815b855b88018b04e03f815a6033cb20"
    "63036033cb406303e10232128b026033cb806303d40c6040c904200889026033"
    "cb20630360338052000b0009ffffffffffffffffffffffffffffffff000d3f60"
    "ffff5d40ffff11bcffff2497524cadb3a55a8000ffffffffffffffff"
)
# Exact ignition-adapter bytes of the schema-3 endpoints.
SCHEMA_3_ADAPTER = bytes.fromhex(
    "644cd125621372106043220072012200d3296030c8408b38601088018b358415"
    "88028b3284146303633ce0053302892cd11a6011600d923c622d30208b258412"
    "88038b22841388028b1f6033d216022c84142029200889186213721c6022d215"
    "30208b1284192008890f621372166033022c622ce06e32028b07e07632028904"
    "34228902d007402b0009d005402b0009ffffffffffffffffffff5d40000d3f60"
    "0002a892000d40c0000d3f4c0102040810ff524cadb3a55affff24c9ffffffff"
)
# Exact threshold-helper bytes, which follow every schema-3 controller in the
# speed-controller span.
THRESHOLD_HELPER = bytes.fromhex(
    "4f22d41fd51f85556203622d6143711b6010630c223e011a9038310c9037d31a"
    "430b00096203614371106010600c3202890062038411600c3022890062038556"
    "6303633d33286033815742008449610c3212890062138547610d312289006213"
    "85566303633d33288555610d331289006313603381594f26000b0009ffffffff"
    "000d3f60ffff5d4000021ce001f403e8ffffffffffffffffffffffffffffffff"
)
# Exact controller bytes of the bounded schema-3 endpoints.
BOUNDED_CONTROLLER = bytes.fromhex(
    "4f223248d1178516630d2f368519630d23388918d1146011610d31368b1360f2"
    "3102890931383038212e011ad30f430b0009340ca0010009342cd10d60432100"
    "d1087111210060f64f26d00a402b0009ffffffffffffffffffffffffffffffff"
    "ffffffffffff5d40ffff11bc00021ce0ffff20220002a892ffffffffffffffff"
)
# Exact controller bytes of the registered schema-3 guarded endpoint.
GUARDED_CONTROLLER = bytes.fromhex(
    "4f223248d1178516630d2f368519630d2338891ad1146011610d31368b1560f2"
    "3102890b313830382008890e212e011ad30e430b0009340ca0010009342cd10c"
    "60432100d1077111210060f64f26d009402b0009ffffffffffffffffffffffff"
    "ffffffffffff5d40ffff11bc00021ce0ffff20220002a892ffffffffffffffff"
)
# Exact wrapper bytes of the last RPM-hold endpoint, which clears a 24-byte
# state.
SCHEMA_3_WRAPPERS = bytes.fromhex(
    "4f22d019400b0009d018400b00094f26000b0009ffffffffffffffffffffffff"
    "d113601088008902d012402b0009d012402b0009ffffffffffffffffffffffff"
    "4f22d10ee000e2062102710442108bfbd00b400b00094f26000b0009ffffffff"
    "ffffffffffffffff000a9554000d38e4ffff5d40000d09d8000d2108ffff5d40"
    "000d22a0"
)
# Exact wrapper and engine bytes of the schema-3 endpoints that hold RPM
# through the fuel-cut shadow and clear a 20-byte state.
FUEL_SHADOW_WRAPPERS = bytes.fromhex(
    "4f22d019400b0009d018400b00094f26000b0009ffffffffffffffffffffffff"
    "d113601088008902d012402b0009d012402b0009ffffffffffffffffffffffff"
    "4f22d10ee000e2052102710442108bfbd00b400b00094f26000b0009ffffffff"
    "ffffffffffffffff000a9554000d38e4ffff5d40000d09d8000d2108ffff5d40"
    "000d22a0"
)
FUEL_SHADOW_ENGINE = bytes.fromhex(
    "4f22d5866050880089058801890588028905a0e70009a0040009a0430009a0a4"
    "00098454e10530128910845520088b0d8553600d20088b098554600d20088b05"
    "b0fc000920088903a0dc0009a0ca0009d572d47360408054d47284438055e000"
    "81538154d4706241622d60238155d46d85476303633d323ce3ff633d33228900"
    "623360238156d06b400b0009845588008901b2450009d561e0012500b2580009"
    "a0b0000984546203e105321289098455e103301289058554600d20088b01a002"
    "0009a08f0009b0b90009d554d4546240845432008903e0118051a0330009d451"
    "84436203845532008903e0128051a029000984512008890dd44d604088088b03"
    "e00f8051a01e000988208b1be0078051a018000985536203622d7201622dd441"
    "85496303633d32328b06e00e80518452c9f78052a006000960238153b2080009"
    "a0600009d53584558800890484546403d036400b0009d531e00081548452c90f"
    "8052e0022500a04d00098454e105301289388455e103301289348554600d915b"
    "611d3012892eb161000920088921d428604088208b18d52185546203622d7201"
    "622dd420854a6303633d32328b08e000250080528053805581538154a0220009"
    "60238154a01e0009d514e0008154a0190009d512e0018051e000805280538154"
    "a0100009e400d011400b0009d50b6153e000e2052102710442108bfbe0022500"
    "e01080514f26000b0009ffffffffffffffffffffffffffffffffffffffff5d40"
    "ffff5d00000d3f60ffff11bc000d3660ffff2a85000d41408000ffff4f22d573"
    "e000805180528053b10000096703200889048453cb018053a0020009e0018051"
    "d46b6240622ce10532128b06845120088b17e0028051a01400092778890c6023"
    "d164021cd16484142029200889048453cb028053a0050009845120088b01e003"
    "8051d45b844163038442230b8443203b20088b048453cb048053a00500098451"
    "20088b01e004805161437104601220088b048453cb088053a005000984512008"
    "8b01e0058051d44d6040c8808b048453cb108053a0050009845120088b01e006"
    "8051d447604088028b048453cb208053a0050009845120088b01e00880512778"
    "890cd4406240622cd43b8448600c32028b048453cb408053a005000984512008"
    "8b01e00980512778890cd4376241622dd4318545600d32028b048453cb808053"
    "a0050009845120088b01e00a80512778890cd42e6241622dd4278546600d3202"
    "8b048452cb018052a0050009845120088b01e00b805127788910d4256240622c"
    "d41d8446600c32028b088447600c30228b048452cb028052a005000984512008"
    "8b01e00c8051277889028452cb0880528451600c4f26000b0009ffffffffffff"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    "ffffffffffffffffffffffffffff5d40ffff5d00000d3d18000d3f60ffff41ae"
    "ffff2a85ffff110effff11bcffff2672ffff10770102040810ffffffffffffff"
    "ffffffffffffffffffffffffd3536031600d91ab611d30108b5f843288038b5c"
    "8433e103301289588434c9e020088b54843520088b5184366203622c8437600c"
    "30228b4a8439610c2118894685356203622d2228894185376403644d2448893c"
    "34128b3a623372106024610c211889346020620c32128b303242892e8539600d"
    "2008892a9175611d30128926853a600d200889223012892064337416e2056044"
    "600ce16e30128b18e1763012891542108bf560402008891074016041600d9156"
    "611d30108b0974026041600d9150611d30108b02e001000b0009e000000b0009"
    "07026073cbf0400ed51d85566203622d85576303633dd41b6023240174022401"
    "74026033240174022401470e000b0009d5138452cb1063038455620322288908"
    "6033cb406303e10232128b026033cb806303d40d6040c904200889026033cb20"
    "630360338052000b0009ffffffffffffffffffffffffffffffffffff000d3f60"
    "ffff5d40ffff5d10ffff2497524cadb3a55a8000ffffffffffffffff"
)
# The 32-byte schema-3 record of the RPM-hold Map 1 test profile.
SCHEMA_3_RECORD = bytes.fromhex(
    "524c0301010000ff011000a000010010040c012c0064737373737314adb3a55a"
)
# A schema-1 record that no current runtime reads.
SCHEMA_1_RECORD = bytes.fromhex(
    "524c0101050000ff010000a00001001000"
    "04012c0064737373737300adb3a55a"
)
# Exact unit bytes of the speed-hold runtime without the RPM ceiling latch,
# whose wrappers clear a 24-byte state and whose controller cuts inline.
SPEED_HOLD_WRAPPERS = bytes.fromhex(
    "4f22d019400b0009d018400b00094f26000b0009ffffffffffffffffffffffff"
    "d113601088008902d012402b0009d012402b0009ffffffffffffffffffffffff"
    "4f22d10ee000e2062102710442108bfbd00b400b00094f26000b0009ffffffff"
    "ffffffffffffffff000a9554000d38e4ffff5d40000d09d8000d2108ffff5d40"
    "000d22a0"
)
SPEED_HOLD_ENGINE = bytes.fromhex(
    "4f22d57ee000815a6050880089058801890588028905a0dc0009a0040009a03c"
    "0009a09700098454e10530128910845520088b0d8553600d20088b098554600d"
    "20088b05b0ec000920088903a0d10009a0bf0009d569d46a60408054d4698443"
    "8055e000815381548159d16760118155d1666211622d8548320c42118900e200"
    "e3ff633d3322890062336023815690c68157e0012500a04e00098454e1053012"
    "890c8455e102301289088554600d20088b048557600d91b230168b01a0890009"
    "b0ae0009d54dd44e6240845432008903e0118051a0340009d44a844362038455"
    "32008903e0128051a02a000984512008890dd448604088088b03e00f8051a01f"
    "000988208b1ce0078051a019000985536203622d7201622dd43a854f6303633d"
    "32328b06e00e80518452c9f78052a007000960238153d038400b0009a0590009"
    "d52ee00081548452c90f8052e0022500a04f00098454e1053012893a8455e102"
    "301289368554600d9158611d30128930b178000920088923d426604088208b1a"
    "d51e85546203622d7201622dd41d6143712060116303633d32328b08e0002500"
    "80528053805581538154a022000960238154a01e0009d511e0008154a0190009"
    "d50ee0018051e000805280538154a0100009e400d00e400b0009d5086153e000"
    "e2062102710442108bfbe0022500e01080514f26000b0009ffffffffffff5d40"
    "ffff5d00000d6040ffff11bcffff113c000d3660ffff2a85000d40c0800003e8"
    "4f22d583e000805180528053b11a00096703200889048453cb018053a0020009"
    "e0018051d47b6240622ce10532128b06845120088b17e0028051a01400092778"
    "890c6023d174021cd17484142029200889048453cb028053a005000984512008"
    "8b01e0038051d46b844163038442230b8443203b20088b048453cb048053a005"
    "0009845120088b01e004805161437104601220088b048453cb088053a0050009"
    "845120088b01e0058051d45d6040c8808b048453cb108053a005000984512008"
    "8b01e0068051d457604088028b048453cb208053a0050009845120088b01e008"
    "80512778890ed4516240622cd44b614371226010600c30228b048452cb048052"
    "a0050009845120088b01e00d805127788929d4456241622dd44060508801890e"
    "8544600d2008890132028b1c8545600d200889203022891ee313a01500098556"
    "600d32086143711a6010600c32078b02e314a00900098411600c600b3203890a"
    "e315a0010009e309845120088b0660338051a00300098453cb4080532778890c"
    "d42b6241622dd4258546600d32028b048453cb808053a0050009845120088b01"
    "e00a80512778890cd4226241622dd41b8547600d32028b048452cb018052a005"
    "0009845120088b01e00b805127788910d4196240622cd4118446600c32028b08"
    "8447600c30228b048452cb028052a0050009845120088b01e00c805127788902"
    "8452cb0880528451600c4f26000b0009ffff5d40ffff5d00000d3d40000d6040"
    "ffff41aeffff2a85ffff113cffff3b38ffff11bcffff2672ffff107701020408"
    "10ffffffd33f6031600d917d611d30108b74843288048b718433e1023012896d"
    "8434c9e020088b69843520088b6684366203622c8437600c30228b5f8534620d"
    "222889058535600d2008890130228b558536600d200889516433741a6044610c"
    "2118894b6040620c222889478538310c41158b43320842158b40643374126040"
    "2008893b9144853a600d2008893630168934853b40118b31853c600d3016892d"
    "853e600d200889299131611d853f600d2008892330128921643374206045600d"
    "2008891b301289196044600c20088915e1ff611c30108911604420088b0e6045"
    "600d9112611d30108b086041600d910d611d30108b02e001000b0009e000000b"
    "0009ffff000d6040524cadb3a55a800003e8ffffffffffffffffffffffffffff"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
)
SPEED_HOLD_CONTROLLER = bytes.fromhex(
    "4f22d540d440d1416211622d8556600d320860238158614371126010630c8411"
    "600c3028e60040158b0a9677303289076163210e011a6033d335430b00096603"
    "854b220f011a611b855967034021402140214021306c4015890341118907a005"
    "0009935b30338b0241158b00e100371c854c4008400837078b006703600b3703"
    "89006703607381594021402140214021306c40118900e000914030178b006013"
    "815b6203854a630385576103303c32078b006203313832138900621360238157"
    "8452cb106303845588018b0fe740237b8555610d854e600d310cd20e6021600d"
    "30168b03e03f815ae7a0237bd20a6020c8048901e720237b603380524f26000b"
    "0009ffffffff5d40000d6040ffff113c00021ce0ffff11bcffff249703e8ffff"
)
# Exact wrapper bytes of the speed-hold runtime with the RPM ceiling latch and
# without the spark-cut actuator, whose startup wrapper clears a 28-byte state.
CEILING_LATCH_WRAPPERS = bytes.fromhex(
    "4f22d019400b0009d018400b00094f26000b0009ffffffffffffffffffffffff"
    "d113601088008902d012402b0009d012402b0009ffffffffffffffffffffffff"
    "4f22d10ee000e2072102710442108bfbd00b400b00094f26000b0009ffffffff"
    "ffffffffffffffff000a9554000d38e4ffff5d40000d09d8000d2108ffff5d40"
    "000d22a0"
)
EDITED_ROMS = ("JK08A", "JK00C", "JK78C", "1ND0A", "1ME3B")


@lru_cache(maxsize=None)
def target(rom):
    return runtime_targets.load_runtime_target(rom)


@lru_cache(maxsize=None)
def built(rom):
    return build_rom.build_image(
        target(rom).stock_image.data, source_name=f"{rom} stock"
    ).data


def closed(rom, data):
    return bytes(rom_checksums.recalculate(bytearray(data), target(rom).checksum_layout))


def extract(source, rom="JK08A"):
    return extract_calibration.extract(closed(rom, source), rom=rom)


def state(extraction):
    return dict(extraction.calibration.source[1:])


def without_telemetry(rom, data):
    return runtime_endpoints.strip_telemetry_endpoint(
        data, target(rom).telemetry_layout, "current", target(rom).checksum_layout
    )


def edited_runtime(rom, *, rolling=False, telemetry=False):
    """Return a current build whose settings an editor changed."""
    edited = bytearray(built(rom))
    if rolling:
        start = target(rom).rolling_layout.configuration.start
        # Editor fields in the current 40-byte Rolling Launch record.
        edited[start + 4] = 0x02  # Map 1 disabled, Map 2 enabled.
        edited[start + 8 : start + 10] = (0).to_bytes(2, "big")  # No speed floor.
        edited[start + 22 : start + 24] = (3).to_bytes(2, "big")  # Integral gain.
        edited[start + 30 : start + 32] = (301).to_bytes(2, "big")  # Run timeout.
    if telemetry:
        layout = target(rom).telemetry_layout
        start = layout.configuration.start
        # Editor fields in the current 16-byte telemetry record.
        edited[start + 3] = 1  # Enable sampling after reset.
        edited[start + 6] = 7  # Snapshot divisor.
        edited[start + 8 : start + 10] = (0x6E0).to_bytes(2, "big")
        configuration = can_telemetry.Configuration.from_bytes(
            edited[start : layout.configuration.end]
        )
        record = layout.mailbox_record_address
        edited[record : record + 4] = configuration.mailbox_record()
    return closed(rom, edited)


def edited_record():
    """Return the schema-3 record with the fields that an editor changed."""
    record = bytearray(SCHEMA_3_RECORD)
    record[4] = 0x02  # Map 1 disabled, Map 2 enabled.
    record[8] = 0  # Vehicle-speed activation gate disabled.
    record[18:20] = (301).to_bytes(2, "big")
    record[22] = 114  # Map 1 target command.
    return bytes(record)


def without_spark_cut(rom, data):
    """Return ``data`` with the spark-cut unit erased and the stock vector of
    the GR11A spark handler, as in every runtime before the hold actuator."""
    layout = target(rom).rolling_layout
    source = bytearray(data)
    spark = layout.assembly_unit_by_key["spark_cut"].span
    source[spark.start : spark.end] = bytes([0xFF]) * spark.size
    hook = layout.hook_by_key["spark_handler"]
    source[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
        hook.width, layout.byte_order
    )
    return source


def schema_3_lower(rom, data, record=SCHEMA_3_RECORD, controller=BOUNDED_CONTROLLER):
    """Return ``data`` with the units and record of the last RPM-hold endpoint,
    whose record occupies the retired span while the current span, the RPM
    ceiling unit, and the spark-cut unit are erased."""
    layout = target(rom).rolling_layout
    source = without_spark_cut(rom, data)
    ceiling = layout.assembly_unit_by_key["rpm_ceiling"].span
    source[ceiling.start : ceiling.end] = bytes([0xFF]) * ceiling.size
    for key, blob in (
        ("wrappers", SCHEMA_3_WRAPPERS),
        ("engine", SCHEMA_3_ENGINE),
        ("ignition_adapter", SCHEMA_3_ADAPTER),
        ("speed_controller", controller + THRESHOLD_HELPER),
    ):
        unit = layout.assembly_unit_by_key[key]
        source[unit.span.start : unit.span.end] = blob
    current = layout.configuration
    source[current.start : current.end] = bytes([0xFF]) * current.size
    retired = layout.retired_configuration
    source[retired.start : retired.end] = record
    return source


def speed_hold_unlatched(rom, data, part):
    """Return ``data`` with the speed-hold units that precede the RPM ceiling
    latch over an erased ceiling span. ``runtime`` also restores the wrappers
    and the hold-mode record with a zero hysteresis byte."""
    layout = target(rom).rolling_layout
    source = without_spark_cut(rom, data)
    ceiling = layout.assembly_unit_by_key["rpm_ceiling"].span
    source[ceiling.start : ceiling.end] = bytes([0xFF]) * ceiling.size
    units = [
        ("engine", SPEED_HOLD_ENGINE),
        ("speed_controller", SPEED_HOLD_CONTROLLER),
    ]
    if part == "runtime":
        units.append(("wrappers", SPEED_HOLD_WRAPPERS))
        start = layout.configuration.start
        source[start + 3] = rolling_launch.Mode.HOLD
        source[start + 0x23] = 0
    for key, blob in units:
        unit = layout.assembly_unit_by_key[key]
        source[unit.span.start : unit.span.end] = blob
    return source


def fuel_shadow_lower(rom, data, record=SCHEMA_3_RECORD, controller=BOUNDED_CONTROLLER):
    """Return ``data`` with the wrappers, engine, and stock fuel-cut hook of the
    endpoints that hold RPM through the fuel-cut shadow."""
    layout = target(rom).rolling_layout
    source = schema_3_lower(rom, data, record, controller)
    for key, blob in (
        ("wrappers", FUEL_SHADOW_WRAPPERS),
        ("engine", FUEL_SHADOW_ENGINE),
        ("fuel_cut_wrapper", bytes([0xFF]) * 64),
    ):
        unit = layout.assembly_unit_by_key[key]
        source[unit.span.start : unit.span.end] = blob
    hook = layout.hook_by_key["fuel_cut_coordinator"]
    source[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
        hook.width, layout.byte_order
    )
    return source


def fuel_shadow_hold_image(rom="JK08A", *, telemetry=True, custom=False):
    source = (
        edited_runtime(rom, telemetry=True) if custom else built(rom)
    )
    if not telemetry:
        source = without_telemetry(rom, source)
    record = edited_record() if custom else SCHEMA_3_RECORD
    return closed(rom, fuel_shadow_lower(rom, source, record))


def previous_current_image(*, telemetry=True, custom=False):
    source = (
        edited_runtime("JK08A", telemetry=True) if custom else built("JK08A")
    )
    if not telemetry:
        source = without_telemetry("JK08A", source)
    record = edited_record() if custom else SCHEMA_3_RECORD
    return closed(
        "JK08A", fuel_shadow_lower("JK08A", source, record, GUARDED_CONTROLLER)
    )


def state_6_7_arbiter_image():
    layout = target("JK08A").rolling_layout
    unit = layout.assembly_unit_by_key["feedback_arbiter"]
    active_immediate = unit.span.start + 0x2D
    failed_immediate = unit.span.start + 0x41
    historical = fuel_shadow_lower(
        "JK08A", built("JK08A"), controller=GUARDED_CONTROLLER
    )
    assert historical[active_immediate] == 0x40
    assert historical[failed_immediate] == 0x50
    historical[active_immediate] = 0x70
    historical[failed_immediate] = 0x60
    endpoint = next(
        item for item in runtime_endpoints.HISTORICAL_ROLLING_ENDPOINTS
        if item.key == "schema-3-state-6-7-indicators"
    )
    assert dict(endpoint.unit_sha256)["feedback_arbiter"] == build_rom.sha256(
        historical[unit.span.start : unit.span.end]
    )
    return closed("JK08A", historical)


def unexpressed_fields(extraction, key):
    """Return the reported settings of the one historical record."""
    assert extraction.rolling is None
    assert not extraction.has_profile
    ((component, record, schema_version, fields),) = extraction.unexpressed
    assert (component, record, schema_version) == ("rolling_launch", key, 3)
    return fields


def test_current_builder_output_is_the_current_runtime():
    extraction = extract(built("JK08A"))
    assert state(extraction) == {
        "map_switching": "current",
        "rolling_launch": "current",
        "can_telemetry": "current",
    }
    assert extraction.calibration.elements == ()
    assert extraction.rolling == build_rom.builtin_profile().calibration


def test_last_rpm_hold_endpoint_reports_its_record():
    extraction = extract(closed("JK08A", schema_3_lower("JK08A", built("JK08A"))))
    assert state(extraction) == {
        "map_switching": "current",
        "rolling_launch": "schema-3-fuel-cut-wrapper",
        "can_telemetry": "current",
    }
    fields = unexpressed_fields(extraction, "schema-3-fuel-cut-wrapper")
    assert fields["mode"] == "rpm_hold" and fields["enable_mask"] == 0x01
    assert extraction.calibration.elements == ()


@pytest.mark.parametrize("part", ("current-record", "retired-record"))
def test_records_in_both_spans_are_refused(part):
    layout = target("JK08A").rolling_layout
    source = bytearray(schema_3_lower("JK08A", built("JK08A")))
    if part == "current-record":
        current = layout.configuration
        source[current.start : current.end] = built("JK08A")[current.start : current.end]
    else:
        source = bytearray(built("JK08A"))
        retired = layout.retired_configuration
        source[retired.start : retired.end] = SCHEMA_3_RECORD
    with pytest.raises(
        extract_calibration.ExtractionError,
        match="partial or unknown Rolling Launch state",
    ):
        extract(source)


def test_map_switching_endpoint_carries_no_settings():
    layout = target("JK08A").rolling_layout
    map_only = bytearray(without_telemetry("JK08A", built("JK08A")))
    for span in layout.claimed_rom_ranges:
        map_only[span.start : span.end] = bytes([0xFF]) * span.size
    for hook in layout.hooks:
        map_only[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
            hook.width, layout.byte_order
        )
    for diagnostic in layout.diagnostics:
        map_only[diagnostic.pointer_address : diagnostic.pointer_address + 4] = (
            diagnostic.stock.to_bytes(4, layout.byte_order)
        )
    extraction = extract(map_only)
    assert state(extraction) == {
        "map_switching": "current",
        "rolling_launch": "absent",
        "can_telemetry": "absent",
    }
    assert extraction.calibration.settings == ()
    assert extraction.calibration.elements == ()
    assert not extraction.has_profile


@pytest.mark.parametrize("status_mask", (0x8F, 0x9F))
def test_state_6_feedback_engines_are_registered_map_endpoints(status_mask):
    map_layout = target("JK08A").map_layout
    engine = map_layout.assembly_unit_by_key["cruise_feedback_engine"]
    status_mask_immediate = engine.span.start + 0x41
    lamp_on_immediate = engine.span.start + 0x4B
    phase_counts = map_layout.feedback.phase_counts_address
    historical = bytearray(built("JK08A"))
    assert historical[status_mask_immediate] == 0x8F
    assert historical[lamp_on_immediate] == 0x40
    assert historical[phase_counts : phase_counts + 2] == bytes((20, 20))
    historical[status_mask_immediate] = status_mask
    historical[lamp_on_immediate] = 0x60
    historical[phase_counts : phase_counts + 2] = bytes((30, 30))
    assert build_rom.sha256(
        historical[engine.span.start : engine.span.end]
    ) in runtime_endpoints.HISTORICAL_FEEDBACK_ENGINE_SHA256
    extraction = extract(historical)
    assert state(extraction)["map_switching"] == "current"
    assert extraction.calibration.elements == ()


def test_unregistered_feedback_engine_is_rejected():
    engine = target("JK08A").map_layout.assembly_unit_by_key["cruise_feedback_engine"]
    historical = bytearray(built("JK08A"))
    historical[engine.span.start + 0x4B] = 0x50
    with pytest.raises(
        extract_calibration.ExtractionError, match="cruise_feedback_engine differs"
    ):
        extract(historical)


def test_state_6_7_arbiter_endpoint_is_recognized_under_telemetry():
    extraction = extract(state_6_7_arbiter_image())
    assert state(extraction) == {
        "map_switching": "current",
        "rolling_launch": "schema-3-state-6-7-indicators",
        "can_telemetry": "current",
    }
    unexpressed_fields(extraction, "schema-3-state-6-7-indicators")


def test_telemetry_over_an_unflagged_historical_endpoint_is_rejected():
    with mock.patch.object(
        runtime_endpoints, "TELEMETRY_LOWER_ROLLING_STATES", frozenset({"current"})
    ):
        with pytest.raises(extract_calibration.ExtractionError, match="not layered"):
            extract(state_6_7_arbiter_image())


def test_pre_feedback_indicator_endpoint_is_recognized():
    layout = target("JK08A").rolling_layout
    historical = fuel_shadow_lower(
        "JK08A",
        without_telemetry("JK08A", built("JK08A")),
        controller=GUARDED_CONTROLLER,
    )
    unit = layout.assembly_unit_by_key["feedback_arbiter"]
    historical[unit.span.start : unit.span.end] = bytes([0xFF]) * unit.span.size
    hook = layout.hook_by_key["feedback_arbitration"]
    assert int.from_bytes(
        historical[hook.address : hook.address + hook.width], layout.byte_order
    ) == hook.replacement
    historical[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
        hook.width, layout.byte_order
    )
    extraction = extract(historical)
    assert state(extraction)["rolling_launch"] == "schema-3-pre-feedback-indicators"
    assert state(extraction)["can_telemetry"] == "absent"
    unexpressed_fields(extraction, "schema-3-pre-feedback-indicators")
    assert extraction.telemetry is None


@pytest.mark.parametrize("telemetry", (False, True))
@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_fuel_shadow_hold_endpoint_is_recognized(rom, telemetry):
    extraction = extract(fuel_shadow_hold_image(rom, telemetry=telemetry), rom)
    assert state(extraction) == {
        "map_switching": "current",
        "rolling_launch": "schema-3-fuel-shadow-hold",
        "can_telemetry": "current" if telemetry else "absent",
    }
    assert extraction.calibration.elements == ()
    fields = unexpressed_fields(extraction, "schema-3-fuel-shadow-hold")
    assert fields["mode"] == "rpm_hold" and fields["enable_mask"] == 0x01


def test_fuel_shadow_hold_endpoint_reports_its_editor_settings():
    extraction = extract(fuel_shadow_hold_image(custom=True))
    fields = unexpressed_fields(extraction, "schema-3-fuel-shadow-hold")
    assert fields["mode"] == "rpm_hold"
    assert fields["enable_mask"] == 0x02
    assert fields["min_speed"] == 0
    assert fields["run_timeout_ticks"] == 301
    assert fields["target_commands"][0] == 114


@pytest.mark.parametrize("part", ("wrappers", "fuel_cut_wrapper", "hook"))
def test_fuel_shadow_hold_hybrid_with_the_fuel_cut_wrapper_is_refused(part):
    layout = target("JK08A").rolling_layout
    current = built("JK08A")
    source = bytearray(fuel_shadow_hold_image())
    if part == "hook":
        hook = layout.hook_by_key["fuel_cut_coordinator"]
        span = (hook.address, hook.address + hook.width)
    else:
        unit = layout.assembly_unit_by_key[part]
        span = (unit.span.start, unit.span.end)
    source[span[0] : span[1]] = current[span[0] : span[1]]
    with pytest.raises(
        extract_calibration.ExtractionError,
        match="partial or unknown Rolling Launch state",
    ):
        extract(source)


@pytest.mark.parametrize("telemetry", (False, True))
def test_previous_guarded_controller_is_recognized_with_or_without_telemetry(telemetry):
    extraction = extract(previous_current_image(telemetry=telemetry))
    assert state(extraction)["rolling_launch"] == "schema-3-guarded-controller"
    assert state(extraction)["can_telemetry"] == ("current" if telemetry else "absent")


@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_previous_guarded_controller_is_recognized_on_every_exact_rom(rom):
    source = fuel_shadow_lower(rom, built(rom), controller=GUARDED_CONTROLLER)
    extraction = extract(source, rom)
    assert state(extraction)["rolling_launch"] == "schema-3-guarded-controller"
    assert extraction.calibration.elements == ()


@pytest.mark.parametrize("part", ("speed_controller", "engine", "configuration"))
def test_previous_guarded_controller_hybrid_and_malformed_endpoint_are_refused(part):
    layout = target("JK08A").rolling_layout
    address = (
        layout.retired_configuration.start if part == "configuration"
        else layout.assembly_unit_by_key[part].span.start
    )
    source = bytearray(previous_current_image())
    source[address] ^= 1
    with pytest.raises(
        extract_calibration.ExtractionError, match="partial or unknown Rolling Launch"
    ):
        extract(source)


def test_previous_endpoint_reports_its_editor_settings_and_transfers_telemetry():
    extraction = extract(previous_current_image(custom=True))
    fields = unexpressed_fields(extraction, "schema-3-guarded-controller")
    assert fields["enable_mask"] == 0x02
    assert fields["min_speed"] == 0
    assert extraction.telemetry == can_telemetry.Configuration(True, 0x6E0, "tuning", 7)


@pytest.mark.parametrize(
    ("component", "rom"),
    (("rolling_launch", "JK08A"), *(("can_telemetry", rom) for rom in EDITED_ROMS)),
)
def test_editor_settings_need_their_profile_or_an_explicit_replacement(rom, component):
    source = edited_runtime(
        rom,
        rolling=component == "rolling_launch",
        telemetry=component == "can_telemetry",
    )
    extraction = extract_calibration.extract(source, rom=rom)
    profile = build_rom.builtin_profile(target(rom).family)
    if component == "rolling_launch":
        assert extraction.rolling.enable_mask == 0x02
        assert extraction.rolling.min_speed == 0
        assert extraction.rolling.integral_gain == 3
        assert extraction.rolling.run_timeout_ticks == 301
        assert extraction.telemetry == profile.telemetry
    else:
        assert extraction.rolling == profile.calibration
        assert extraction.telemetry == can_telemetry.Configuration(
            True, 0x6E0, "tuning", 7
        )
    assert extraction.calibration.elements == ()
    with pytest.raises(
        apply_calibration.ApplicationError,
        match=f"differ from the extracted settings: {component};",
    ):
        apply_calibration.apply(built(rom), extraction.calibration)


@pytest.mark.parametrize("rom", ("JK08A", "JK00A"))
def test_editor_disabling_only_map_1_travels_in_the_profile(rom):
    start = target(rom).rolling_layout.configuration.start
    edited = bytearray(built(rom))
    assert edited[start + 3] == rolling_launch.Mode.HOLD
    assert edited[start + 4] & 1 == 1
    edited[start + 4] &= ~1
    extraction = extract(edited, rom)
    assert extraction.rolling == replace(
        build_rom.builtin_profile(target(rom).family).calibration, enable_mask=0
    )
    with pytest.raises(apply_calibration.ApplicationError, match="rolling_launch"):
        apply_calibration.apply(built(rom), extraction.calibration)


@pytest.mark.parametrize("part", ("runtime", "controller-engine"))
def test_speed_hold_runtime_without_the_ceiling_latch_is_refused(part):
    data = closed("JK08A", speed_hold_unlatched("JK08A", built("JK08A"), part))
    with pytest.raises(
        runtime_endpoints.EndpointError,
        match="partial or unknown Rolling Launch state",
    ):
        runtime_endpoints.classify_runtime(data, target("JK08A"), "image")
    with pytest.raises(
        preflash.PreflashError,
        match="partial or unknown Rolling Launch state",
    ):
        preflash.check_image(data, "JK08A")


def test_ceiling_latch_runtime_without_the_spark_cut_is_refused():
    layout = target("JK08A").rolling_layout
    data = without_spark_cut("JK08A", built("JK08A"))
    wrappers = layout.assembly_unit_by_key["wrappers"].span
    data[wrappers.start : wrappers.end] = CEILING_LATCH_WRAPPERS
    # The built-in profile of that runtime observes on Map 1.
    data[layout.configuration.start + 3] = rolling_launch.Mode.OBSERVE
    data = closed("JK08A", data)
    with pytest.raises(
        runtime_endpoints.EndpointError,
        match="partial or unknown Rolling Launch state",
    ):
        runtime_endpoints.classify_runtime(data, target("JK08A"), "image")
    with pytest.raises(
        preflash.PreflashError,
        match="partial or unknown Rolling Launch state",
    ):
        preflash.check_image(data, "JK08A")


def _rolling_cases():
    layout = target("JK08A").rolling_layout
    base = built("JK08A")
    unknown_payload = bytearray(base)
    unknown_payload[0xD3900] ^= 0x01
    partial_hook = bytearray(base)
    hook = layout.hooks[0]
    partial_hook[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
        hook.width, layout.byte_order
    )
    partial_did = bytearray(base)
    diagnostic = layout.diagnostics[0]
    partial_did[diagnostic.pointer_address : diagnostic.pointer_address + 4] = (
        diagnostic.stock.to_bytes(4, layout.byte_order)
    )
    invalid_configuration = bytearray(base)
    # A zero speed-window width is outside the record contract.
    invalid_configuration[layout.configuration.start + 18] = 0
    mixed_schema = bytearray(base)
    retired = layout.retired_configuration
    mixed_schema[retired.start : retired.end] = SCHEMA_1_RECORD
    return {
        "unknown-payload": unknown_payload,
        "partial-hook": partial_hook,
        "partial-did": partial_did,
        "framed-invalid-configuration": invalid_configuration,
        "current-payload-schema-1": mixed_schema,
    }


@pytest.mark.parametrize(
    "case",
    (
        "unknown-payload",
        "partial-hook",
        "partial-did",
        "framed-invalid-configuration",
        "current-payload-schema-1",
    ),
)
def test_partial_and_unknown_rolling_states_are_rejected(case):
    with pytest.raises(
        extract_calibration.ExtractionError,
        match="partial or unknown Rolling Launch state",
    ):
        extract(_rolling_cases()[case])


def test_partial_map_pointer_state_is_rejected():
    partial = bytearray(built("JK08A"))
    partial[target("JK08A").map_layout.families[0].pointer_table] ^= 1
    with pytest.raises(extract_calibration.ExtractionError, match="pointer table"):
        extract(partial)


@pytest.mark.parametrize(
    "case", ("damaged-unit", "damaged-hook", "damaged-configuration")
)
def test_partial_can_telemetry_states_are_rejected(case):
    layout = target("JK08A").telemetry_layout
    source = bytearray(built("JK08A"))
    if case == "damaged-unit":
        source[layout.assembly_units[0].span.start] ^= 1
    elif case == "damaged-hook":
        hook = layout.hooks[0]
        source[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
            hook.width, layout.byte_order
        )
    else:
        source[layout.configuration.start] ^= 1
    with pytest.raises(
        extract_calibration.ExtractionError,
        match="partial or unknown CAN telemetry state",
    ):
        extract(source)


def test_occupied_telemetry_reserve_is_rejected_by_address():
    reserve = target("JK08A").telemetry_layout.reserved_rom.start
    source = bytearray(built("JK08A"))
    source[reserve] = 0
    with pytest.raises(
        extract_calibration.ExtractionError,
        match=f"change at {reserve:#x} is outside the calibration ranges",
    ):
        extract(source)


@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_historical_endpoint_calibration_transfers_with_replaced_settings(rom):
    families = target(rom).map_layout.families
    source = fuel_shadow_lower(
        rom,
        edited_runtime(rom, telemetry=True),
        edited_record(),
        GUARDED_CONTROLLER,
    )
    for index, family in enumerate(families):
        source[family.canonical_address] ^= 1 + index
        source[family.copies[-1] + family.byte_length - 1] ^= 1 + index
    source = closed(rom, source)
    extraction = extract_calibration.extract(source, rom=rom)
    assert state(extraction)["rolling_launch"] == "schema-3-guarded-controller"
    profile = replace(
        build_rom.builtin_profile(target(rom).family),
        telemetry=extraction.telemetry,
    )
    fresh = build_rom.build_image(
        target(rom).stock_image.data, rom=rom, profile=profile
    ).data
    with pytest.raises(
        apply_calibration.ApplicationError,
        match="differ from the extracted settings: rolling_launch;",
    ):
        apply_calibration.apply(fresh, extraction.calibration)
    result = apply_calibration.apply(
        fresh, extraction.calibration, replace_settings=True
    )
    assert dict(result.settings) == {
        "rolling_launch": "replaced",
        "can_telemetry": "matched",
    }
    ranges = calibration_ranges.load(rom)
    differences = {
        offset for offset, (before, after) in enumerate(zip(fresh, result.data))
        if before != after
    }
    assert differences
    assert differences <= ranges.offsets() | ranges.checksum_offsets
    rolling = target(rom).rolling_layout.configuration
    assert result.data[rolling.start : rolling.end] == fresh[rolling.start : rolling.end]
    telemetry = target(rom).telemetry_layout.configuration
    assert result.data[telemetry.start : telemetry.end] == (
        source[telemetry.start : telemetry.end]
    )
