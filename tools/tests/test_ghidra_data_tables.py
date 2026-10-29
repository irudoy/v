"""Exact-image data-table classification and executable-data export refusals."""

import hashlib
import json

import pytest

from kb import ghidra_preparation as prep, repo
from kb.repo import KbError
from tools.tests.test_ghidra_preparation import prepared_root


def register_table(root, row):
    path = root / prep.SEEDS / "t1.toml"
    head = path.read_text().split("\n[[data_table]]", 1)[0]
    path.write_text(head + "\n[[data_table]]\n" + "".join(
        f"{key} = {json.dumps(value)}\n" for key, value in row.items()))


@pytest.fixture
def data_table_root(prepared_root):
    root, original = prepared_root
    data = bytearray(original)
    data[0x80:0x90] = bytes.fromhex("ff0eff0cfff20000000a001600240034")
    image = bytes(data)
    digest = hashlib.sha256(image).hexdigest()
    old = hashlib.sha256(original).hexdigest()
    (root / "rom-images/T1/T1.bin").write_bytes(image)
    for path in (root / repo.CATALOG, root / prep.SEEDS / "t1.toml"):
        path.write_text(path.read_text().replace(old, digest))
    row = dict(start="00000080", end="00000090", element="s16",
               sha256=hashlib.sha256(image[0x80:0x90]).hexdigest(),
               former_entry="00000088", former_end="00000090",
               former_instruction_sha256=hashlib.sha256(image[0x88:0x90]).hexdigest())
    register_table(root, row)
    return root, image, row


def test_data_table_binds_exact_bytes_and_the_contained_former_body(data_table_root, tmp_path):
    root, image, row = data_table_root
    plan = prep.plan("t1", root)
    [table] = plan.data_tables
    assert (table.start, table.end, table.element) == (0x80, 0x90, "s16")
    assert table.sha256 == hashlib.sha256(image[0x80:0x90]).hexdigest()
    assert (table.former_entry, table.former_end) == (0x88, 0x90)
    wire = tmp_path / "table.tsv"
    prep.write_plan(plan, wire, root)
    assert ("data_table\t00000080\t00000090\ts16\t" + row["sha256"]
            + "\t00000088\t00000090\t" + row["former_instruction_sha256"]) in wire.read_text()


@pytest.mark.parametrize("key,value", [
    ("element", "u16"), ("start", "00000081"), ("end", "00000202"),
    ("former_entry", "0000007e"), ("former_entry", "00000090"),
    ("former_end", "00000092"), ("former_end", "00000089"),
    ("sha256", "0" * 64), ("former_instruction_sha256", "0" * 64),
])
def test_data_table_refuses_unbound_bytes_wrong_types_and_uncontained_bodies(data_table_root, key, value):
    root, _, row = data_table_root
    register_table(root, {**row, key: value})
    with pytest.raises(KbError):
        prep.plan("t1", root)


def test_data_table_refuses_overlap_with_another_table_or_reviewed_code(data_table_root):
    root, image, row = data_table_root
    path = root / prep.SEEDS / "t1.toml"
    declaration = path.read_text().split("\n[[data_table]]", 1)[1]
    path.write_text(path.read_text() + "\n[[data_table]]" + declaration)
    with pytest.raises(KbError, match="data tables overlap"):
        prep.plan("t1", root)
    register_table(root, {**row, "start": "000000f0", "end": "00000110",
                         "former_entry": "00000100", "former_end": "00000108",
                         "sha256": hashlib.sha256(image[0xf0:0x110]).hexdigest(),
                         "former_instruction_sha256": hashlib.sha256(image[0x100:0x108]).hexdigest()})
    with pytest.raises(KbError, match="conflicts with another preparation"):
        prep.plan("t1", root)


@pytest.mark.parametrize("mutation", ["former-entry", "another-entry", "instruction", "odd-instruction"])
def test_export_refuses_any_function_or_instruction_in_the_data_table(data_table_root, tmp_path, mutation):
    root, _, _ = data_table_root
    plan = prep.plan("t1", root)
    seed = plan.seeds[0]
    output = tmp_path / "export"
    output.mkdir()
    (output / "funcs.csv").write_text("addr\n00000100\n")
    (output / "function_signatures.csv").write_text(
        "addr,size,instructions,exact_sha256\n"
        f"00000100,8,4,{seed.instruction_sha256}\n")
    (output / "function_tokens.csv").write_text("func_addr,ins_addr\n" + "".join(
        f"00000100,{site:08x}\n" for site in range(0x100, 0x108, 2)))
    (output / "function_references.csv").write_text(
        "func_addr,ins_addr,ref_addr,ref_type\n00000100,00000104,ffff1000,write\n")
    prep.check_exports(plan, output, root)
    if mutation.endswith("entry"):
        path = output / "funcs.csv"
        extra = "00000088\n" if mutation == "former-entry" else "00000082\n"
    else:
        path = output / "function_tokens.csv"
        extra = "00000200,00000081\n" if mutation == "odd-instruction" else "00000200,00000080\n"
    path.write_text(path.read_text() + extra)
    with pytest.raises(KbError, match="retains executable data table"):
        prep.check_exports(plan, output, root)
