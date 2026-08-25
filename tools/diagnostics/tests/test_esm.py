from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DIAGNOSTICS = ROOT / "refs" / "diagnostics" / "nissan-esm-2007-g35-sedan"
VQ37_DIAGNOSTICS = ROOT / "refs" / "diagnostics" / "nissan-esm-2013-g37-sedan"
sys.path.insert(0, str(ROOT / "tools" / "diagnostics"))

import extract_esm  # noqa: E402


def read_csv(name: str, root: Path = DIAGNOSTICS) -> list[dict[str, str]]:
    with (root / name).open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def read_fragment(fragment_id: str) -> dict[str, object]:
    with (DIAGNOSTICS / "fragments.jsonl").open(encoding="utf-8") as source:
        for line in source:
            fragment = json.loads(line)
            if fragment["id"] == fragment_id:
                return fragment
    raise AssertionError(f"missing fixture fragment: {fragment_id}")


class EsmCatalogTest(unittest.TestCase):
    def test_tracked_corpus_counts(self) -> None:
        documents = read_csv("documents.csv")
        definitions = read_csv("dtc_definitions.csv")
        parameters = read_csv("diagnostic_parameters.csv")
        operations = read_csv("diagnostic_operations.csv")
        signals = read_csv("can_signals.csv")
        ecm_codes = {
            row["code"] for row in definitions if row["ecu_id"].endswith(":ecm")
        }
        self.assertEqual(29, len(documents))
        self.assertEqual(1635, len(definitions))
        self.assertEqual(169, len(ecm_codes))
        self.assertNotIn("P0000", ecm_codes)
        self.assertEqual(1120, len(parameters))
        self.assertEqual(316, len(operations))
        self.assertEqual(106, len(signals))
        p0605 = next(
            row
            for row in definitions
            if row["code"] == "P0605" and row["ecu_id"].endswith(":ecm")
        )
        self.assertEqual("ECM", p0605["title"])

    def test_vq37_corpus_counts_and_bank_labels(self) -> None:
        documents = read_csv("documents.csv", VQ37_DIAGNOSTICS)
        definitions = read_csv("dtc_definitions.csv", VQ37_DIAGNOSTICS)
        parameters = read_csv("diagnostic_parameters.csv", VQ37_DIAGNOSTICS)
        self.assertEqual(31, len(documents))
        self.assertEqual(842, len(definitions))
        self.assertEqual(1165, len(parameters))
        ecm = {
            row["code"]: row["title"]
            for row in definitions
            if row["ecu_id"].endswith(":ecm")
        }
        self.assertEqual(202, len(ecm))
        self.assertEqual(
            {
                "P100A": "VVEL SYSTEM-B1",
                "P100B": "VVEL SYSTEM-B2",
                "P1087": "VVEL SYSTEM-B1",
                "P1088": "VVEL SYSTEM-B2",
                "P1089": "VVEL POS SEN/CIRC-B1",
                "P1090": "VVEL ACTR MOT-B1",
                "P1091": "VVEL ACTR MOT PWR",
                "P1092": "VVEL POS SEN/CIRC-B2",
                "P1093": "VVEL ACTR MOT-B2",
                "P1608": "VVEL SENSOR POWER/CIRC",
            },
            {
                code: title
                for code, title in ecm.items()
                if code
                in {
                    "P100A",
                    "P100B",
                    "P1087",
                    "P1088",
                    "P1089",
                    "P1090",
                    "P1091",
                    "P1092",
                    "P1093",
                    "P1608",
                }
            },
        )
        self.assertNotIn("P1422", ecm)
        monitors = {
            row["name"]: (row["unit"], row["description"])
            for row in parameters
            if row["name"].startswith("VVEL")
        }
        self.assertEqual(
            ("deg", "\u2022 Indicates [deg] of VVEL control shaft angle."),
            monitors["VVEL TIM-B1"],
        )
        self.assertEqual(monitors["VVEL TIM-B1"], monitors["VVEL TIM-B2"])
        self.assertEqual("V", monitors["VVEL POSITION SEN-B1"][0])
        self.assertEqual("V", monitors["VVEL POSITION SEN-B2"][0])

    def test_ecm_manual_codes_are_in_jk08a(self) -> None:
        manual = {
            row["code"]
            for row in read_csv("dtc_definitions.csv")
            if row["ecu_id"].endswith(":ecm")
        }
        rom_path = (
            ROOT
            / "refs"
            / "diagnostics"
            / "rom-dtc"
            / "rom_dtc_descriptors.csv"
        )
        with rom_path.open(newline="", encoding="utf-8") as source:
            rom = {
                row["code"]
                for row in csv.DictReader(source)
                if row["rom"] == "JK08A"
            }
        self.assertEqual(set(), manual - rom)

    def test_operations_are_definitions_only(self) -> None:
        operations = read_csv("diagnostic_operations.csv")
        self.assertGreater(len(operations), 0)
        self.assertEqual({"false"}, {row["executable"] for row in operations})
        self.assertEqual({"factory_defined"}, {row["verification_status"] for row in operations})

    def test_fixed_width_tables_preserve_names_and_units(self) -> None:
        rows = extract_esm.first_column_names(
            "\n".join(
                (
                    " VEH SPEED 1                     Value of vehicle speed signal",
                    " [Km/h]                          received over CAN.",
                    " POWER BAL-                      Engine at idle",
                    " ANCE                            Cut each injector signal.",
                )
            ),
            34,
        )
        self.assertEqual(
            [("VEH SPEED 1", "Km/h"), ("POWER BALANCE", "")],
            rows,
        )

    def test_page_start_table_kind_ignores_application_tables(self) -> None:
        self.assertEqual(
            "active_test",
            extract_esm.leading_table_kind(
                "\n".join(
                    (
                        "DIAGNOSIS SYSTEM (BCM)",
                        " Test item                         Description",
                        " REAR DEFOGGER                    Check operation.",
                        "DATA MONITOR",
                    )
                ),
                "data_monitor",
            ),
        )
        self.assertEqual(
            "work_support",
            extract_esm.leading_table_kind(
                "\n".join(
                    (
                        "DIAGNOSIS SYSTEM (BCM)",
                        " Monitor item                     Description",
                        " TRUNK OPEN DELAY                 Select delay.",
                        "DATA MONITOR",
                    )
                ),
                "work_support",
            ),
        )
        self.assertEqual(
            "",
            extract_esm.leading_table_kind(
                "\n".join(
                    (
                        "DIAGNOSIS SYSTEM (BCM)",
                        " Test item     Diagnosis mode     Description",
                        " BUZZER        Active Test        Check loads.",
                        "DATA MONITOR",
                    )
                ),
                "active_test",
            ),
        )

    def test_page_start_and_later_mode_tables_are_combined(self) -> None:
        fragment = {
            "id": "fixture:p0001:data_monitor",
            "dataset_id": extract_esm.DATASET_ID,
            "kind": "data_monitor",
            "ecu_id": f"{extract_esm.VEHICLE_ID}:bcm",
            "vehicle_id": extract_esm.VEHICLE_ID,
            "page_start_kind": "data_monitor",
            "text": "\n".join(
                (
                    "DIAGNOSIS SYSTEM (BCM)",
                    f" {'Monitor item':<33}Description",
                    f" {'EARLY SWITCH':<33}Early description.",
                    "ACTIVE TEST",
                    f" {'Test item':<33}Description",
                    f" {'LAMP':<33}Check lamp.",
                    "DATA MONITOR",
                    f" {'Monitor item':<33}Description",
                    f" {'LATE SWITCH':<33}Late description.",
                )
            ),
        }
        rows = extract_esm.diagnostic_parameters(fragment)
        self.assertEqual(
            {"EARLY SWITCH", "LATE SWITCH"},
            {row["name"] for row in rows},
        )

    def test_service_setting_rows_keep_each_mode_with_its_item(self) -> None:
        rows = extract_esm.service_setting_rows(
            "\n".join(
                (
                    " Service item                 Setting item       Setting",
                    "                              MODE 1*            45 sec.",
                    " FIRST ITEM",
                    "                              MODE 2             30 sec.",
                    "                              MODE 1*            Normal",
                    " SECOND ITEM                  MODE 2             Sensitive",
                    "DATA MONITOR",
                )
            )
        )
        self.assertEqual(["FIRST ITEM", "SECOND ITEM"], [row["name"] for row in rows])
        self.assertIn("MODE 2 30 sec.", rows[0]["description"])
        self.assertNotIn("Normal", rows[0]["description"])
        self.assertIn("MODE 1* Normal", rows[1]["description"])

    def test_hyphenated_semantic_text_ignores_footnote_marker(self) -> None:
        self.assertEqual(
            "the swivel position sensor",
            extract_esm.join_table_text(
                ("the swiv-", " * el position sensor")
            ),
        )

    def test_semantic_table_rows_extracts_active_test_columns(self) -> None:
        rows = extract_esm.semantic_table_rows(
            "\n".join(
                (
                    "    TEST ITEM                      CONDITION                           JUDGEMENT                       CHECK ITEM (REMEDY)",
                    f" {'POWER BALANCE':<20}{'Engine at idle':<36}"
                    f"{'Engine runs rough.':<40}Fuel injector",
                )
            ),
            "active_test",
            20,
        )
        self.assertEqual(1, len(rows))
        self.assertEqual("POWER BALANCE", rows[0]["name"])
        self.assertIn("Engine at idle", rows[0]["conditions"])
        self.assertIn("Engine runs rough", rows[0]["description"])
        self.assertIn("Fuel injector", rows[0]["usage"])

    def test_combined_monitor_item_unit_header_preserves_remarks(self) -> None:
        rows = extract_esm.semantic_table_rows(
            "\n".join(
                (
                    "           Monitor item (Unit)                         Remarks",
                    " ENGINE SPEED [rpm]                         "
                    "The engine speed signal from ECM is indicated with CAN "
                    "communication line.",
                )
            ),
            "data_monitor",
            34,
        )
        self.assertEqual(1, len(rows))
        self.assertEqual("ENGINE SPEED", rows[0]["name"])
        self.assertEqual("rpm", rows[0]["unit"])
        self.assertEqual(
            "The engine speed signal from ECM is indicated with CAN "
            "communication line.",
            rows[0]["remarks"],
        )

    def test_paired_monitor_rows_share_complete_semantics_and_unit(self) -> None:
        rows = extract_esm.semantic_table_rows(
            "\n".join(
                (
                    f" {'Monitored item':<25}{'Unit':<14}"
                    f"{'Description':<50}Remarks",
                    f" {'PAIR SEN-B1':<39}"
                    f"{'• Shared sensor description is dis-':<50}"
                    "• Shared remark.",
                    f" {'':<25}{'V':<14}",
                    f" {'PAIR SEN-B2':<39}played.",
                )
            ),
            "data_monitor",
            34,
        )
        self.assertEqual(["PAIR SEN-B1", "PAIR SEN-B2"], [row["name"] for row in rows])
        self.assertEqual({"V"}, {row["unit"] for row in rows})
        self.assertEqual(
            {"• Shared sensor description is displayed."},
            {row["description"] for row in rows},
        )
        self.assertEqual(
            {"• Shared remark."},
            {row["remarks"] for row in rows},
        )

    def test_explicit_kinds_follow_page_order_and_carry_monitor_tables(self) -> None:
        text = "\n".join(
            (
                "Freeze Frame Data",
                "DATA MONITOR MODE",
                "Monitored item Unit Description",
            )
        )
        self.assertEqual(
            ["freeze_frame", "data_monitor"],
            extract_esm.explicit_kinds(text),
        )
        self.assertEqual(
            "data_monitor",
            extract_esm.carry_kind(
                "data_monitor",
                "Monitored item Unit Description",
                1,
            ),
        )

    def test_table_of_contents_is_not_a_dtc_detail(self) -> None:
        text = "\n".join(
            (
                "CONTENTS",
                "P0455 Diagnosis Procedure ............ 297",
                "P0605 Diagnosis Procedure ............ 401",
                "P1610 Diagnosis Procedure ............ 525",
            )
        )
        self.assertTrue(extract_esm.table_of_contents_page(text))
        self.assertNotIn("dtc_detail", extract_esm.explicit_kinds(text))

    def test_tracked_esm_rows_do_not_contain_wrapped_fragments(self) -> None:
        parameters = read_csv("diagnostic_parameters.csv")
        operations = read_csv("diagnostic_operations.csv")
        speed = next(
            row
            for row in parameters
            if row["source_fragment_id"].endswith(
                "body-control-system:p0015:data_monitor"
            )
            and row["name"] == "VEH SPEED 1"
        )
        self.assertEqual("Km/h", speed["unit"])
        described_parameters = [
            row
            for row in parameters
            if row["description"] or row["conditions"] or row["remarks"]
        ]
        described_operations = [
            row
            for row in operations
            if row["description"] or row["conditions"] or row["usage"]
        ]
        self.assertGreaterEqual(len(described_parameters), 940)
        self.assertGreaterEqual(len(described_operations), 295)
        self.assertFalse(
            any(row["name"] == "TRUNK/GLASS HATCH" for row in parameters)
        )
        names = {row["name"] for row in operations}
        self.assertIn("POWER BALANCE", names)
        self.assertIn("FUEL INJECTION", names)
        self.assertNotIn("ANCE", names)
        self.assertNotIn("ING", names)
        self.assertNotIn("LAY", names)
        power_balance = next(
            row for row in operations if row["name"] == "POWER BALANCE"
        )
        self.assertEqual(
            "Engine runs rough or dies.",
            power_balance["description"],
        )
        self.assertIn("Engine: After warming up", power_balance["conditions"])
        self.assertIn("Fuel injector", power_balance["usage"])
        alpha_rows = [
            row
            for row in parameters
            if row["name"] in {"A/F ALPHA-B1", "A/F ALPHA-B2"}
            and row["source_fragment_id"].endswith(
                "engine-control-system:p0117:data_monitor"
            )
        ]
        self.assertEqual(2, len(alpha_rows))
        self.assertEqual({"%"}, {row["unit"] for row in alpha_rows})
        self.assertEqual(
            {
                "• The mean value of the air-fuel ratio feedback correction "
                "factor per cycle is indicated."
            },
            {row["description"] for row in alpha_rows},
        )
        ignition_timing = next(
            row
            for row in parameters
            if row["name"] == "IGN TIMING"
            and row["source_fragment_id"].endswith(
                "engine-control-system:p0118:data_monitor"
            )
        )
        self.assertEqual("BTDC", ignition_timing["unit"])
        self.assertIn(
            "ignition timing computed by ECM",
            ignition_timing["description"],
        )
        door_lock = next(
            row
            for row in operations
            if row["source_fragment_id"].endswith(
                "body-control-system:p0014:work_support"
            )
            and row["name"] == "DOOR LOCK-UNLOCK SET"
        )
        self.assertIn("Selective unlock function", door_lock["description"])

    def test_mode_boundaries_and_dtc_work_support(self) -> None:
        operations = read_csv("diagnostic_operations.csv")
        body_work = {
            row["name"]
            for row in operations
            if row["source_fragment_id"].endswith(
                "body-control-system:p0014:work_support"
            )
        }
        transmission_work = {
            row["name"]
            for row in operations
            if row["source_fragment_id"].endswith(
                "transaxle-transmission:p0119:work_support"
            )
        }
        self.assertEqual(
            {"D/LOCK VHCL SPD AJT", "DOOR LOCK-UNLOCK SET"},
            body_work,
        )
        self.assertEqual(
            {
                "1ST GR FUNCTN P0731",
                "2ND GR FUNCTN P0732",
                "3RD GR FUNCTN P0733",
                "4TH GR FUNCTN P0734",
                "5TH GR FUNCTN P0735",
            },
            transmission_work,
        )

    def test_multiline_dtc_title_keeps_qualifier(self) -> None:
        definitions = read_csv("dtc_definitions.csv")
        c1928 = next(row for row in definitions if row["code"] == "C1928")
        self.assertEqual("CONTROL UNIT [ABNORMAL9]", c1928["title"])
        steering = {
            row["code"]: row["title"]
            for page in ("p0166", "p0167")
            for row in extract_esm.dtc_definitions(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    f"steering-control-system:{page}:dtc_index"
                )
            )
        }
        self.assertEqual("ENG REV SIGNAL", steering["C1921"])
        self.assertEqual("4WAS FRONT ECU", steering["C1930"])
        self.assertEqual("CAN COMM", steering["U1000"])
        self.assertEqual("CONTROL UNIT (CAN)", steering["U1010"])

    def test_ecu_attribution_uses_the_page_heading(self) -> None:
        shared_bcm = read_fragment(
            "nissan-esm-2007-g35-sedan-v1:"
            "automatic-drive-positioner:p0210:dtc_index"
        )
        engine = read_fragment(
            "nissan-esm-2007-g35-sedan-v1:"
            "engine-control-system:p0325:dtc_detail"
        )
        steering = read_fragment(
            "nissan-esm-2007-g35-sedan-v1:"
            "steering-control-system:p0078:dtc_detail"
        )
        self.assertEqual(
            f"{extract_esm.VEHICLE_ID}:bcm",
            extract_esm.infer_ecu_id(
                "AUTOMATIC DRIVE POSITIONER",
                str(shared_bcm["text"]),
            ),
        )
        self.assertEqual(
            f"{extract_esm.VEHICLE_ID}:ecm",
            extract_esm.infer_ecu_id(
                "ENGINE CONTROL SYSTEM",
                str(engine["text"]),
            ),
        )
        self.assertEqual(
            f"{extract_esm.VEHICLE_ID}:steering-control-system",
            extract_esm.infer_ecu_id(
                "STEERING CONTROL SYSTEM",
                str(steering["text"]),
            ),
        )

    def test_title_first_av_dtc_lists_are_complete(self) -> None:
        expectations = {
            "p0077": (9, "U1000", "CAN COMM CIRCUIT"),
            "p0210": (10, "U1010", "CONTROL UNIT (CAN)"),
            "p0430": (28, "U124C", "CD CHANGER [N-BUS]"),
        }
        for page, (count, code, title) in expectations.items():
            with self.subTest(page=page):
                rows = extract_esm.dtc_definitions(
                    read_fragment(
                        "nissan-esm-2007-g35-sedan-v1:"
                        f"audio-visual-navigation-system:{page}:dtc_index"
                    )
                )
                by_code = {row["code"]: row for row in rows}
                self.assertEqual(count, len(rows))
                self.assertEqual(title, by_code[code]["title"])
        rear_camera = extract_esm.dtc_definitions(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "audio-visual-navigation-system:p0430:dtc_index"
            )
        )
        self.assertEqual(
            "REAR CAMERA LAN CONN",
            next(
                row["title"]
                for row in rear_camera
                if row["code"] == "U1252"
            ),
        )

    def test_srs_range_and_qualifier_titles_are_reconstructed(self) -> None:
        preceding_page = {
            row["code"]: row["title"]
            for row in extract_esm.dtc_definitions(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "srs-airbag-control-system:p0182:dtc_index"
                )
            )
        }
        first_page = {
            row["code"]: row["title"]
            for row in extract_esm.dtc_definitions(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "srs-airbag-control-system:p0184:dtc_index"
                )
            )
        }
        second_page = {
            row["code"]: row["title"]
            for row in extract_esm.dtc_definitions(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "srs-airbag-control-system:p0185:dtc_index"
                )
            )
        }
        self.assertEqual("CONTROL UNIT", first_page["B1106"])
        self.assertEqual("CONTROL UNIT", first_page["B1111"])
        self.assertEqual(
            "CURTAIN MODULE RH [OPEN]",
            first_page["B1145"],
        )
        self.assertEqual(
            "OCCUPANT SENS C/U [UNIT FAIL]",
            second_page["B1017"],
        )
        self.assertEqual(
            "FRONTAL COLLISION DETECTION",
            second_page["B1209"],
        )
        self.assertEqual(
            "SIDE COLLISION DETECTION",
            second_page["B1210"],
        )
        self.assertEqual(
            "CRASH ZONE SEN [COMM FAIL]",
            preceding_page["B1035"],
        )
        for code, qualifier in (
            ("B1054", "OPEN"),
            ("B1055", "VB-SHORT"),
            ("B1056", "GND-SHORT"),
            ("B1057", "SHORT"),
        ):
            with self.subTest(code=code):
                self.assertEqual(
                    f"DRIVER AIRBAG MODULE [{qualifier}]",
                    preceding_page[code],
                )
        self.assertFalse(
            any(
                title.startswith(("[", "("))
                or title.startswith("ULE ")
                for title in preceding_page.values()
            )
        )

    def test_sensor_number_pairs_share_complete_monitor_semantics(self) -> None:
        first_page = {
            row["name"]: row
            for row in extract_esm.diagnostic_parameters(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "engine-control-system:p0117:data_monitor"
                )
            )
        }
        second_page = {
            row["name"]: row
            for row in extract_esm.diagnostic_parameters(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "engine-control-system:p0119:data_monitor"
                )
            )
        }
        for names, rows in (
            (("ACCEL SEN 1", "ACCEL SEN 2"), first_page),
            (("TP SEN 1-B1", "TP SEN 2-B1"), first_page),
            (("TP SEN 1-B2", "TP SEN 2-B2"), second_page),
        ):
            with self.subTest(names=names):
                pair = [rows[name] for name in names]
                self.assertEqual({"V"}, {row["unit"] for row in pair})
                self.assertEqual(
                    1,
                    len({row["description"] for row in pair}),
                )
                self.assertEqual(
                    1,
                    len({row["remarks"] for row in pair}),
                )
                self.assertTrue(pair[0]["description"])
                self.assertTrue(pair[0]["remarks"])

    def test_monitor_columns_do_not_include_neighboring_text(self) -> None:
        av = {
            row["name"]: row
            for row in extract_esm.diagnostic_parameters(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "audio-visual-navigation-system:p0349:data_monitor"
                )
            )
        }
        self.assertEqual(
            "Vehicle speed >0 km/h (0 MPH) "
            "Vehicle speed =0 km/h (0 MPH)",
            av["VHCL SPD SIG"]["description"],
        )
        self.assertEqual(
            "Changes in indication may be delayed. This is normal.",
            av["VHCL SPD SIG"]["remarks"],
        )
        self.assertNotIn("Selector lever", av["IGN SIG"]["description"])
        self.assertEqual(
            "Selector lever in R position "
            "Selector lever in any position other than R",
            av["REV SIG"]["description"],
        )

        afs = {
            row["name"]: row
            for row in extract_esm.diagnostic_parameters(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "exterior-lighting-system:p0040:data_monitor"
                )
            )
        }
        self.assertFalse(
            afs["STR ANGLS SIG"]["description"].startswith("[Unit]")
        )

        body = {
            row["name"]: row
            for row in extract_esm.diagnostic_parameters(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "body-control-system:p0015:data_monitor"
                )
            )
        }
        self.assertEqual(
            "Status of front fog lamp switch judged by BCM.",
            body["FR FOG SW"]["description"],
        )
        self.assertEqual(
            "Status of driver side door switch judged by BCM.",
            body["DOOR SW-DR"]["description"],
        )

        abs_rows = {
            row["name"]: row
            for row in extract_esm.diagnostic_parameters(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "brake-control-system:p0077:data_monitor"
                )
            )
        }
        self.assertEqual(
            "VDC OFF switch ON (When VDC OFF indicator lamp is ON) "
            "VDC OFF switch OFF (When VDC OFF indicator lamp is OFF)",
            abs_rows["OFF SW"]["conditions"],
        )
        self.assertEqual("ON OFF", abs_rows["OFF SW"]["remarks"])
        self.assertNotIn(
            "VDC OFF",
            abs_rows["YAW RATE SEN"]["conditions"],
        )
        self.assertNotIn(
            "VDC OFF",
            abs_rows["YAW RATE SEN"]["remarks"],
        )

        steering = {
            row["name"]: row
            for row in extract_esm.diagnostic_parameters(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "steering-control-system:p0041:data_monitor"
                )
            )
        }
        for name in (
            "ACT PRTCT FLG",
            "ECU PRTCT FLG",
            "DRV TMPO FLG",
            "MTR PW TMP FL",
            "LOW VOLT FLG",
            "HIGH VOLT FLG",
        ):
            with self.subTest(name=name):
                remarks = steering[name]["remarks"]
                self.assertEqual(
                    1,
                    remarks.count("4WAS system protection function mode"),
                )
                self.assertTrue(
                    remarks.endswith(
                        "• 4WAS system protection function mode"
                    )
                )

    def test_standalone_work_support_items_are_extracted(self) -> None:
        for fragment_id in (
            "nissan-esm-2007-g35-sedan-v1:"
            "body-control-system:p0031:work_support",
            "nissan-esm-2007-g35-sedan-v1:"
            "road-wheels-tires:p0012:work_support",
        ):
            with self.subTest(fragment_id=fragment_id):
                rows = extract_esm.diagnostic_operations(
                    read_fragment(fragment_id)
                )
                self.assertEqual(
                    {
                        "ID Read":
                            "The registered ID number is displayed.",
                        "ID Regist":
                            "Refer to WT-5, \"ID REGISTRATION PROCEDURE : "
                            "Special Repair Requirement\".",
                    },
                    {
                        row["name"]: row["description"]
                        for row in rows
                    },
                )

    def test_can_matrix_starts_after_its_header(self) -> None:
        signals = read_csv("can_signals.csv")
        first = next(
            row
            for row in signals
            if row["source_fragment_id"].endswith(
                "lan-system:p0028:can_signal_matrix"
            )
            and row["name"] == "A/C compressor request signal"
        )
        self.assertEqual("ECM", first["transmitters"])
        self.assertEqual("IPDM-E", first["receivers"])
        self.assertFalse(
            any(row["name"].startswith("CAN Communication Signal Chart") for row in signals)
        )

    def test_dtc_index_parser_excludes_no_fault_code(self) -> None:
        fragment = {
            "id": "fixture:p1:dtc-index",
            "dataset_id": extract_esm.DATASET_ID,
            "kind": "dtc_index",
            "text": "DTC Index INFOID:1\nP0000 NO DTC\nP0605 ECM\n",
            "ecu_id": "fixture:ecm",
            "vehicle_id": extract_esm.VEHICLE_ID,
        }
        rows = extract_esm.dtc_definitions(fragment)
        self.assertEqual(["P0605"], [row["code"] for row in rows])

    def test_dtc_titles_keep_semantic_brackets(self) -> None:
        rows = {
            row["code"]: row["title"]
            for row in extract_esm.dtc_definitions(
                read_fragment(
                    "nissan-esm-2007-g35-sedan-v1:"
                    "exterior-lighting-system:p0174:dtc_index"
                )
            )
        }
        self.assertEqual(
            "SWIVEL ACTUATOR [RH, LH]",
            rows["B2503"],
        )
        self.assertEqual(
            "SWIVEL ACTUATOR [RH, LH]",
            rows["B2504"],
        )
        self.assertEqual("HI SEN UNUSUAL [RR]", rows["B2514"])
        self.assertEqual("SHIFT SIG [P, R]", rows["B2516"])
        self.assertFalse(
            any(title.count("[") != title.count("]") for title in rows.values())
        )

    def test_real_monitor_tables_preserve_units_and_columns(self) -> None:
        tcm = extract_esm.diagnostic_parameters(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "transaxle-transmission:p0116:data_monitor"
            )
        )
        tcm_by_name = {row["name"]: row for row in tcm}
        self.assertEqual(28, len(tcm))
        self.assertEqual("km/h", tcm_by_name["VHCL/S SE-A/T"]["unit"])
        self.assertEqual("0.0/8", tcm_by_name["ACCELE POSI"]["unit"])
        self.assertIn(
            "updated after gear-shifting",
            tcm_by_name["GEAR"]["remarks"],
        )

        probes = extract_esm.diagnostic_parameters(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "transaxle-transmission:p0119:data_monitor"
            )
        )
        self.assertEqual(
            {
                "VEHICLE SPEED": "km/h",
                "Voltage": "V",
                "Frequency": "Hz",
                "DUTY-HI": "%",
                "DUTY-LOW": "%",
                "PLS WIDTH-HI": "ms",
                "PLS WIDTH-LOW": "ms",
            },
            {row["name"]: row["unit"] for row in probes},
        )

        abs_rows = extract_esm.diagnostic_parameters(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "brake-control-system:p0077:data_monitor"
            )
        )
        abs_by_name = {row["name"]: row for row in abs_rows}
        for name in (
            "FR LH SENSOR",
            "FR RH SENSOR",
            "RR LH SENSOR",
            "RR RH SENSOR",
        ):
            self.assertEqual("Wheel speed", abs_by_name[name]["description"])
            self.assertIn(
                "Nearly matches the speed meter display",
                abs_by_name[name]["conditions"],
            )
            self.assertEqual(
                "Vehicle stopped Vehicle running (Note 1)",
                abs_by_name[name]["remarks"],
            )
        self.assertEqual(
            "P R N D",
            abs_by_name["SLCT LVR POSI"]["remarks"],
        )

        meter = extract_esm.diagnostic_parameters(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "meter-warning-lamp-indicator:p0037:data_monitor"
            )
        )
        meter_by_name = {row["name"]: row for row in meter}
        self.assertEqual("lit.", meter_by_name["FUEL METER"]["unit"])
        self.assertEqual(
            "Fuel level indicated on combination meter.",
            meter_by_name["FUEL METER"]["description"],
        )
        self.assertNotIn("X ", meter_by_name["FUEL METER"]["description"])
        self.assertNotIn(
            "door warning",
            meter_by_name["BRAKE W/L"]["description"].lower(),
        )

        continued = extract_esm.diagnostic_parameters(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "body-control-system:p0019:data_monitor"
            )
        )
        continued_by_name = {row["name"]: row for row in continued}
        self.assertEqual(
            "ON/OFF",
            continued_by_name["DOOR SW-RR"]["unit"],
        )
        self.assertEqual(
            "The value of exterior brightness voltage input from the "
            "optical sensor",
            continued_by_name["OPTICAL SENSOR"]["description"],
        )

        repeated = extract_esm.diagnostic_parameters(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "body-control-system:p0020:data_monitor"
            )
        )
        repeated_by_name = {row["name"]: row for row in repeated}
        self.assertEqual("ON/OFF", repeated_by_name["PUSH SW"]["unit"])
        self.assertIn("engine switch", repeated_by_name["PUSH SW"]["description"])

    def test_real_operation_tables_keep_row_boundaries(self) -> None:
        engine = extract_esm.diagnostic_operations(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "engine-control-system:p0122:active_test"
            )
        )
        engine_by_name = {row["name"]: row for row in engine}
        self.assertEqual(
            {
                "INT V/T ANGLE",
                "EXT V/T ANGLE",
                "FAN DUTY CONTROL*",
                "ALTERNATOR DUTY",
            },
            set(engine_by_name),
        )
        self.assertEqual(
            "• Harness and connectors • Cooling fan motor "
            "• Cooling fan relay • Cooling fan control module • IPDM E/R",
            engine_by_name["FAN DUTY CONTROL*"]["usage"],
        )
        self.assertEqual(
            "• Harness and connectors • IPDM E/R • Alternator",
            engine_by_name["ALTERNATOR DUTY"]["usage"],
        )

        door = extract_esm.diagnostic_operations(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "door-lock:p0052:work_support"
            )
        )
        door_by_name = {row["name"]: row for row in door}
        self.assertIn(
            "Hazard reminder function mode",
            door_by_name["HAZARD ANSWER BACK"]["description"],
        )
        self.assertIn(
            "• OFF: Non operation",
            door_by_name["HAZARD ANSWER BACK"]["description"],
        )
        self.assertNotIn(
            "Trunk button",
            door_by_name["HORN WITH KEYLESS LOCK"]["description"],
        )
        self.assertIn(
            "• 200 msec",
            door_by_name["SHORT CRANKING OUTPUT"]["description"],
        )

        lighting = extract_esm.diagnostic_operations(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "exterior-lighting-system:p0039:active_test"
            )
        )
        lighting_by_name = {row["name"]: row for row in lighting}
        self.assertEqual(
            "Off Lo Hi",
            lighting_by_name["FRONT WIPER"]["conditions"],
        )
        self.assertEqual(
            "1 2 3 4",
            lighting_by_name["MOTOR FAN"]["conditions"],
        )
        self.assertEqual(
            "On Off",
            lighting_by_name["HEAD LAMP WASHER"]["conditions"],
        )
        self.assertEqual(
            "TAIL Lo Hi Fog",
            lighting_by_name["EXTERNAL LAMPS"]["conditions"],
        )

        continued_active = extract_esm.diagnostic_operations(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "body-control-system:p0015:active_test"
            )
        )
        self.assertIn(
            "REAR DEFOGGER",
            {row["name"] for row in continued_active},
        )

        continued_work = extract_esm.diagnostic_operations(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "body-control-system:p0018:work_support"
            )
        )
        continued_work_by_name = {
            row["name"]: row for row in continued_work
        }
        self.assertIn(
            "MODE 8 180 sec.",
            continued_work_by_name["ILL DELAY SET"]["description"],
        )
        self.assertNotIn(
            "MODE 8",
            continued_work_by_name["CUSTOM A/LIGHT SETTING"]["description"],
        )

        intelligent_key = extract_esm.diagnostic_operations(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "body-control-system:p0022:work_support"
            )
        )
        self.assertEqual(9, len(intelligent_key))
        self.assertIn(
            "This function allows inside key antenna self-diagnosis.",
            {
                row["description"]
                for row in intelligent_key
                if row["name"] == "INSIDE ANT DIAGNOSIS"
            },
        )

    def test_real_tables_do_not_mix_neighboring_columns(self) -> None:
        injection = extract_esm.diagnostic_parameters(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "engine-control-system:p0118:data_monitor"
            )
        )
        injection_by_name = {row["name"]: row for row in injection}
        pulse = injection_by_name["INJ PULSE-B1"]
        self.assertEqual(
            "• Indicates the actual fuel injection pulse width compensated "
            "by ECM according to the input signals.",
            pulse["description"],
        )
        self.assertEqual(
            "• When the engine is stopped, a certain computed value is "
            "indicated.",
            pulse["remarks"],
        )

        steering = extract_esm.diagnostic_parameters(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "steering-control-system:p0045:data_monitor"
            )
        )
        steering_by_name = {row["name"]: row for row in steering}
        self.assertEqual(
            "The steering angle sensor signal from the steering angle "
            "sensor is indicated with CAN communication line.",
            steering_by_name["STEERING ANG"]["remarks"],
        )
        self.assertEqual(
            "The front wheel angle value transmitted from 4WAS main "
            "control unit to 4WAS front control unit is indicated.",
            steering_by_name["FR ANGLE OPE"]["remarks"],
        )

    def test_active_test_sections_exclude_following_reference_tables(self) -> None:
        steering = extract_esm.diagnostic_operations(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "steering-control-system:p0046:active_test"
            )
        )
        self.assertEqual(
            ["SELF DIAGNOSTIC MODE"],
            [row["name"] for row in steering],
        )
        self.assertIn(
            "4WAS rear actuator assembly activates",
            steering[0]["description"],
        )

        cruise = extract_esm.diagnostic_operations(
            read_fragment(
                "nissan-esm-2007-g35-sedan-v1:"
                "cruise-control-system:p0027:active_test"
            )
        )
        self.assertNotIn(
            "ECU IDENTIFICATION",
            {row["name"] for row in cruise},
        )


if __name__ == "__main__":
    unittest.main()
