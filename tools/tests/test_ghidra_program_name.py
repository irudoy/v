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
