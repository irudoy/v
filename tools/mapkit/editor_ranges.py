"""Bind editor writes and immutable axis labels to the builder contract."""

from functools import lru_cache
import math
import xml.etree.ElementTree as ET

from patches import calibration_ranges, runtime_targets


STORAGE_BYTES = {"uint8": 1, "uint16": 2, "uint32": 4}


@lru_cache(maxsize=None)
def writable_ranges(rom):
    """Return calibration storage and the records transferred in a profile."""
    target = runtime_targets.load_runtime_target(rom)
    records = [target.telemetry_layout.configuration]
    if target.rolling_layout is not None:
        records.append(target.rolling_layout.configuration)
    return tuple((item.start, item.end) for item in (
        *calibration_ranges.load(rom).ranges, *records
    ))


def contains(ranges, address, size):
    return size > 0 and any(start <= address and address + size <= end
                            for start, end in ranges)


def axis_labels(image, axis):
    """Convert exact stock points through the validated axis expression."""
    expression = axis.get("scale_expr") or "x"
    labels = []
    for raw in image.values(axis["addr"], axis["len"], axis["storagetype"]):
        value = eval(expression, {"__builtins__": {}}, {"x": raw})
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{image.rom}: invalid axis label at {axis['addr']}")
        labels.append(format(value, ".15g"))
    return labels


def bind_axes(rom, image, axes, addresses):
    """Keep protected ROM axes as stock labels without writable addresses."""
    ranges = writable_ranges(rom)
    result = dict(axes)
    for address in addresses:
        axis = axes[address]
        size = axis["len"] * STORAGE_BYTES[axis["storagetype"]]
        if not contains(ranges, int(address, 16), size):
            result[address] = dict(axis, read_only_values=axis_labels(image, axis))
    return result


def require_coverage(rom, xml, xdf, ranges=None):
    """Check every complete writable extent in both rendered formats."""
    ranges = writable_ranges(rom) if ranges is None else ranges

    def require(address, size, name):
        if not contains(ranges, address, size):
            raise ValueError(
                f"{rom}: editable {name} at {address:#x} ({size} bytes) "
                "is outside builder calibration and profile ranges"
            )

    for table in ET.fromstring(xml).iter("table"):
        if "storageaddress" not in table.attrib:
            continue
        address = int(table.get("storageaddress"), 16)
        if table.get("type") == "Switch":
            size = max(len(bytes.fromhex(state.get("data")))
                       for state in table.findall("state"))
        else:
            size = (STORAGE_BYTES[table.get("storagetype")]
                    * int(table.get("sizex", "1")) * int(table.get("sizey", "1")))
        require(address, size, f"RomRaider {table.get('name')}")
    root = ET.fromstring(xdf)
    for data in root.iter("EMBEDDEDDATA"):
        if "mmedaddress" not in data.attrib:
            continue
        size = ((int(data.get("mmedelementsizebits")) + 7) // 8
                * int(data.get("mmedrowcount", "1"))
                * int(data.get("mmedcolcount", "1")))
        require(int(data.get("mmedaddress"), 16), size, "TunerPro data")
    for entry in root.iter("XDFPATCHENTRY"):
        require(int(entry.get("address"), 16), int(entry.get("datasize"), 16),
                "TunerPro patch")
