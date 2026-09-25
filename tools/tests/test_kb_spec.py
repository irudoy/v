from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "tools" / "kb" / "SPEC.md"
HOMOLOGY = ROOT / "rom-images" / "homology.toml"
LAYOUT_HEADING = "## 3. Layouts and families"
KINDS_HEADING = "## 6. Kinds"
TOKENS_HEADING = "### 20.7 Evidence tokens"


def layout_rows():
    """Return the rows of the layout table that the specification publishes."""

    text = SPEC.read_text(encoding="utf-8")
    section = text.split(LAYOUT_HEADING, 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        if not line.startswith("| `"):
            continue
        layout, family, kind, images, l0_image = (
            cell.strip() for cell in line.strip().strip("|").split("|")
        )
        rows.append(
            {
                "layout": layout.strip("`"),
                "family": family.strip("`"),
                "kind": kind,
                "images": [image.strip() for image in images.split(",")],
                "l0_image": l0_image,
            }
        )
    return rows


def kind_names():
    """Return the kind names of the kind table that the specification publishes."""

    text = SPEC.read_text(encoding="utf-8")
    section = text.split(KINDS_HEADING, 1)[1].split("\n## ", 1)[0]
    return [
        line.strip().strip("|").split("|")[0].strip().strip("`")
        for line in section.splitlines()
        if line.startswith("| `")
    ]


def resolution_orders():
    """Return {role: kinds} of the target resolution table of section 20.7."""

    text = SPEC.read_text(encoding="utf-8")
    section = text.split(TOKENS_HEADING, 1)[1].split("\n## ", 1)[0]
    table = section.split("| Role | Resolution order |", 1)[1].split("\n\n", 1)[0]
    orders = {}
    for line in table.splitlines():
        if not line.startswith("| `"):
            continue
        roles, kinds = (cell.strip() for cell in line.strip().strip("|").split("|"))
        for role in roles.split(","):
            orders[role.strip().strip("`")] = tuple(
                kind.strip().strip("`") for kind in kinds.split(",")
            )
    return orders


class KbSpecTokenTableTest(unittest.TestCase):
    def test_the_resolution_orders_are_those_the_adapters_run(self):
        from kb import tokens

        self.assertEqual(resolution_orders(), tokens.TARGET_KINDS)


class KbSpecLayoutTableTest(unittest.TestCase):
    def setUp(self):
        self.rows = layout_rows()
        self.families = tomllib.loads(HOMOLOGY.read_text(encoding="utf-8"))[
            "family"
        ]

    def test_every_family_member_belongs_to_one_layout(self):
        self.assertTrue(self.rows)
        for name, family in self.families.items():
            with self.subTest(family=name):
                rows = [row for row in self.rows if row["family"] == name]
                images = sorted(image for row in rows for image in row["images"])
                self.assertEqual(images, sorted(family["members"]))
                expected = (
                    1
                    if family["same_address_inheritance"]
                    else len(family["members"])
                )
                self.assertEqual(len(rows), expected)

    def test_rows_follow_family_kind_and_l0_image_rules(self):
        for row in self.rows:
            with self.subTest(layout=row["layout"]):
                self.assertIn(row["family"], self.families)
                family = self.families[row["family"]]
                self.assertEqual(row["kind"], family["kind"])
                if family["same_address_inheritance"]:
                    self.assertEqual(row["l0_image"], family["canonical"])
                else:
                    self.assertEqual(row["images"], [row["l0_image"]])

    def test_rows_equal_the_layouts_the_families_declare(self):
        declared = {
            layout: (name, image)
            for name, family in self.families.items()
            for layout, image in family["layouts"].items()
        }
        published = {
            row["layout"]: (row["family"], row["l0_image"]) for row in self.rows
        }
        self.assertEqual(published, declared)

    def test_layout_ids_and_kind_names_are_disjoint(self):
        kinds = kind_names()
        self.assertIn("fn", kinds)
        self.assertFalse(set(kinds) & {row["layout"] for row in self.rows})

    def test_layout_ids_are_unique_and_well_formed(self):
        ids = [row["layout"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        for layout in ids:
            with self.subTest(layout=layout):
                self.assertRegex(layout, r"^[0-9a-z]{2,8}$")


if __name__ == "__main__":
    unittest.main()
