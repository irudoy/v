from tools.mapkit import presentation_audit


def test_canonical_presentation_is_clean_and_explicit():
    report = presentation_audit.audit()
    assert report.canonical_table_count == 210
    assert report.visible_table_count == 42
    assert report.hidden_table_count == 168
    assert report.masked_view_count == 3
    assert report.switchable_family_count == 12


def test_non_tuning_tables_remain_in_the_catalog_but_hidden():
    report = presentation_audit.audit()
    assert report.hidden_non_tuning == {
        "0000abba": "diagnostic-only surface with unknown verdict direction",
        "0000abfa": "diagnostic-only surface with unknown verdict direction",
        "000120f6": "stock-inactive DFCO branch",
        "0001491a": "diagnostic calculated-load publication only",
    }


def test_visible_taxonomy_separates_control_domains():
    report = presentation_audit.audit()
    assert report.categories["Torque Model / Engine Torque"] == 3
    assert report.categories[
        "Electronic Throttle Control / Requested Torque"
    ] == 2
    assert report.categories[
        "Electronic Throttle Control / Throttle Geometry"
    ] == 2
    assert report.categories["Ignition Timing / State Surfaces"] == 3
