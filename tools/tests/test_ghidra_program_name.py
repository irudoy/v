import pytest

from tools.ghidra import program_name

INDEX = """VERSION=1
/
  00000004:1JK00C-20260803-stock.bin:c0a81d6d0f31056504642729333
  00000002:1JK00D_8MFK36N15-20260726-013734.bin:c0a81d6e815207621045059166
  00000003:1JK08A-20260726-stock.bin:c0a81d6ffcf11355277967416
  00000000:1ND0A_Stock.bin:c0a815acd3e140141876060333
  00000001:as7058.bin:c0a81d6ce3d189887248927958
/experiments
  00000007:1JK08A-20260726-stock.bin:c0a81d6ffcf11355277967417
  00000008:1ND3B_copy.bin:c0a81d6ffcf11355277967418
NEXT-ID:9
MD5:d41d8cd98f00b204e9800998ecf8427e
"""


def test_root_programs_lists_only_the_root_folder():
    assert program_name.root_programs(INDEX) == [
        "1JK00C-20260803-stock.bin",
        "1JK00D_8MFK36N15-20260726-013734.bin",
        "1JK08A-20260726-stock.bin",
        "1ND0A_Stock.bin",
        "as7058.bin",
    ]


def test_registered_image_name_wins():
    programs = program_name.root_programs(INDEX) + ["JK08A-scratch.bin"]
    assert program_name.resolve(
        "JK08A", "1JK08A-20260726-stock.bin", programs,
    ) == "1JK08A-20260726-stock.bin"


@pytest.mark.parametrize("rom, image, expected", [
    ("JK00D", "1JK00D-20260726-stock.bin", "1JK00D_8MFK36N15-20260726-013734.bin"),
    ("1ND0A", "11ND0A-20260715-stock.bin", "1ND0A_Stock.bin"),
])
def test_single_program_with_the_rom_key_is_taken(rom, image, expected):
    assert program_name.resolve(rom, image, program_name.root_programs(INDEX)) == expected


def test_missing_program_is_reported_with_the_stored_names():
    with pytest.raises(LookupError) as error:
        program_name.resolve(
            "1ND3B", "11ND3B-20260715-stock.bin", program_name.root_programs(INDEX))
    assert "no program matches ROM 1ND3B" in str(error.value)
    assert "1ND0A_Stock.bin" in str(error.value)
    assert "-p" in str(error.value)


def test_ambiguous_rom_key_is_rejected():
    programs = ["1JK00D_a.bin", "1JK00D_b.bin"]
    with pytest.raises(LookupError) as error:
        program_name.resolve("JK00D", "1JK00D-20260726-stock.bin", programs)
    assert "several programs match ROM JK00D" in str(error.value)


def test_unreadable_index_keeps_the_image_name(tmp_path):
    assert program_name.read_index(tmp_path, "absent") is None
    assert program_name.resolve(
        "JK00D", "1JK00D-20260726-stock.bin", None,
    ) == "1JK00D-20260726-stock.bin"


def test_index_is_read_from_the_project_repository(tmp_path):
    idata = tmp_path / "vq-hr.rep" / "idata"
    idata.mkdir(parents=True)
    (idata / "~index.dat").write_text(INDEX)
    assert "1ND0A_Stock.bin" in program_name.read_index(tmp_path, "vq-hr")


def synthetic_root(base):
    """A root with layout t1 of image T1, the Ghidra pin, the L0 manifest of
    t1, and the function-name registry of t1."""
    from kb import repo

    (base / "rom-images").mkdir(parents=True)
    (base / repo.HOMOLOGY).write_text(
        '[family.test]\nkind = "exact-code"\nmembers = ["T1"]\ncanonical = "T1"\n'
        'mcu = "SH7058"\nsame_address_inheritance = false\nlayouts = { t1 = "T1" }\n')
    (base / repo.GHIDRA_PIN).parent.mkdir(parents=True)
    (base / repo.GHIDRA_PIN).write_text("#!/bin/sh\nGHIDRA_VERSION=12.1.4\n")
    (base / repo.L0 / "t1").mkdir(parents=True)
    (base / repo.L0 / "t1" / "manifest.toml").write_text('layout = "t1"\n')
    (base / "tools/ghidra/symbols").mkdir(parents=True)
    (base / "tools/ghidra/symbols/t1.csv").write_text("addr,name,note\n")
    return base


def test_cache_key_follows_the_pin_the_l0_manifest_and_the_names(tmp_path):
    from kb import repo

    root = synthetic_root(tmp_path)
    key = program_name.cache_key("T1", "T1.bin", "ab" * 32, root)
    manifest = repo.sha256_file(root / repo.L0 / "t1" / "manifest.toml")[:16]
    names = repo.sha256_file(root / "tools/ghidra/symbols/t1.csv")[:16]
    assert key == (f"ghidra=12.1.4 program=T1.bin image={'ab' * 8} "
                   f"l0=t1:{manifest} names={names}")
    (root / repo.L0 / "t1" / "manifest.toml").write_text('layout = "t1"\nghidra = "x"\n')
    assert program_name.cache_key("T1", "T1.bin", "ab" * 32, root) != key
    (root / repo.L0 / "t1" / "manifest.toml").unlink()
    assert "l0=t1:- " in program_name.cache_key("T1", "T1.bin", "ab" * 32, root)
    assert program_name.cache_key("T2", "T2.bin", "cd" * 32, root) == (
        f"ghidra=12.1.4 program=T2.bin image={'cd' * 8}")
