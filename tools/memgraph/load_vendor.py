#!/usr/bin/env python3
# Load the vendor vocabularies described in tools/map-analysis-pipeline.md into
# Memgraph. :VendorEntry (name catalog) and :VendorFact (anchor facts) nodes form a
# ROM-independent HR-family layer alongside :A2LEntry.
#
# Sources are refs/vendor/catalog.csv and refs/vendor/facts.csv, consolidated ProECU
# (EcuTek) and UpRev vocabularies. refs/vendor/README.md defines the method and annotation
# rules. Like A2L, they contain no addresses: the vocabularies define classes rather than
# placement.
#
# Why a second catalog exists alongside A2L. A2L knows table form (geometry, storagetype,
# scaling) but not meaning: it provides names without their mechanics. Vendor documentation
# supplies exactly what is missing: calibration meaning, axes in ROM terms, and documented
# defaults. K-Factor demonstrates the value: prose names its default as 26806, a value search
# locates it in a dump, and a homolog join finds it across six ROMs before any trace.
#
# Catalog node key: (vendor, family, name). A name is unique per vendor. Names remain
# verbatim, and the two vocabularies use different terms for the same entity
# (`BFS Multiplier (K-Factor)` versus `K - Fuel Multiplier`). A global name key would
# therefore merge different entries and separate equivalent ones.
#
# The concept column links vocabularies instead of name. It is set only where evidence
# supports a link (170 of 371 entries; 27 concepts covered by both vocabularies); empty means
# "link not established". The loader does not materialize concept relationships because a
# property join takes one Cypher line, while a relationship would duplicate the property and
# create the kind of second source of truth that P5 prevents.
#
# As in load_a2l.py, this loader creates no :MATCHES relationships. Section 7 match keys are
# (dims, scale family, axis semantics). ProECU has none of the three because tree screenshots
# contain only names. UpRev has prose axis semantics (`Base Fuel Schedule`, `coolant temp`);
# reconciling them with :Axis semantics belongs to Stage 5 after Stage 4, not to the loader.
# Blind name matching is exactly the failure P6 prevents.
#
# The origin=factory filter is mandatory when annotating stock ROM. Of 371 entries, 128 are
# not factory: 126 describe vendor patches (EcuTek RaceROM or UpRev ARC), which are external
# code absent from stock, and two remain unresolved. Matching a stock map to a patch entry
# would be wrong rather than merely weak evidence.
#
# Invocation: uv run python tools/memgraph/load_vendor.py [family]
# Default family: HR.
import csv
import os
import sys



ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CATALOG = os.path.join(ROOT, "refs", "vendor", "catalog.csv")
FACTS = os.path.join(ROOT, "refs", "vendor", "facts.csv")

ORIGINS = {"factory", "patch", "unknown"}
KINDS = {"const", "unit", "axis", "geometry", "mechanics", "hardware", "gap", "hypothesis"}


def read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(s):
    """Parse dims as an axis count, matching :A2LEntry and :Map; empty means unspecified."""
    return int(s) if s and s.isdigit() else None


def build_entries(family, catalog=CATALOG):
    rows = []
    for r in read(catalog):
        rows.append(
            {
                "vendor": r["vendor"],
                "family": family,
                "name": r["name"],
                "doc": r["doc"],
                "section": r["section"],
                "group": r["group"],
                "dims": num(r["dims"]),
                "axis_x": r["axis_x"],
                "axis_y": r["axis_y"],
                "output": r["output"],
                "origin": r["origin"],
                "level": r["level"],
                "concept": r["concept"],
                "source": r["source"],
                "note": r["note"],
            }
        )
    return rows


def build_facts(family, facts=FACTS):
    rows = []
    for r in read(facts):
        rows.append(
            {
                "vendor": r["vendor"],
                "family": family,
                "subject": r["subject"],
                "doc": r["doc"],
                "kind": r["kind"],
                "concept": r["concept"],
                "statement": r["statement"],
                "value": r["value"],
                "units": r["units"],
                "applies_to": r["applies_to"],
                "anchor": r["anchor"],
                "note": r["note"],
            }
        )
    return rows


def check(entries, facts):
    """Reject failures before loading when the graph could not distinguish them from facts."""
    bad = sorted({e["origin"] for e in entries} - ORIGINS)
    if bad:
        sys.exit(f"catalog.csv: unknown origin: {bad}")
    bad = sorted({f["kind"] for f in facts} - KINDS)
    if bad:
        sys.exit(f"facts.csv: unknown kind: {bad}")

    # Node key is (vendor, name); a collision would silently merge two catalog entries.
    seen = {}
    for e in entries:
        seen.setdefault((e["vendor"], e["name"]), 0)
        seen[(e["vendor"], e["name"])] += 1
    dup = sorted(k for k, n in seen.items() if n > 1)
    if dup:
        sys.exit(f"catalog.csv: nonunique (vendor, name), {len(dup)}: {dup[:5]}")

    seen = {}
    for f in facts:
        seen.setdefault((f["vendor"], f["subject"]), 0)
        seen[(f["vendor"], f["subject"])] += 1
    dup = sorted(k for k, n in seen.items() if n > 1)
    if dup:
        sys.exit(f"facts.csv: nonunique (vendor, subject), {len(dup)}: {dup[:5]}")


def load(driver, family, catalog, facts_path):
    """Load the tracked external vocabulary without creating a connection."""
    entries = build_entries(family, catalog)
    facts = build_facts(family, facts_path)
    check(entries, facts)

    vendors = sorted({e["vendor"] for e in entries})
    factory = sum(1 for e in entries if e["origin"] == "factory")
    print(f"Vendor vocabularies: {len(entries)} catalog entries, {len(facts)} facts; "
          f"family={family}")
    print(f"Vocabularies: {', '.join(vendors)}")
    print(f"origin=factory (usable for stock ROM): {factory} of {len(entries)}")

    with driver.session() as s:
        s.run("MATCH (n:VendorEntry {family:$f}) DETACH DELETE n", f=family)
        s.run("MATCH (n:VendorFact {family:$f}) DETACH DELETE n", f=family)
        for label, props in (
            ("VendorEntry", ("family", "vendor", "name", "concept", "origin")),
            ("VendorFact", ("family", "vendor", "subject", "concept", "kind")),
        ):
            for prop in props:
                try:
                    s.run(f"CREATE INDEX ON :{label}({prop})")
                except Exception:
                    pass

        s.run(
            """
            UNWIND $rows AS r
            MERGE (e:VendorEntry {vendor:r.vendor, family:r.family, name:r.name})
            SET e.doc = r.doc, e.section = r.section, e.group = r.group,
                e.dims = r.dims, e.axis_x = r.axis_x, e.axis_y = r.axis_y,
                e.output = r.output, e.origin = r.origin, e.level = r.level,
                e.concept = r.concept, e.source = r.source, e.note = r.note
            """,
            rows=entries,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (f:VendorFact {vendor:r.vendor, family:r.family, subject:r.subject})
            SET f.doc = r.doc, f.kind = r.kind, f.concept = r.concept,
                f.statement = r.statement, f.value = r.value, f.units = r.units,
                f.applies_to = r.applies_to, f.anchor = r.anchor, f.note = r.note
            """,
            rows=facts,
        )
        n = s.run(
            "MATCH (e:VendorEntry {family:$f}) RETURN count(e) AS n", f=family
        ).single()["n"]
        m = s.run(
            "MATCH (f:VendorFact {family:$f}) RETURN count(f) AS n", f=family
        ).single()["n"]
        print(f"Memgraph: {n} :VendorEntry, {m} :VendorFact")

        print("Factory names by vocabulary (Stage 5 matching input):")
        for r in s.run(
            """
            MATCH (e:VendorEntry {family:$f, origin:'factory'})
            RETURN e.vendor AS vendor, count(*) AS n ORDER BY n DESC
            """,
            f=family,
        ):
            print(f"  {r['vendor']:<8} {r['n']:>3}")

        print("Vocabulary convergence (concepts covered by both):")
        rows = list(
            s.run(
                """
                MATCH (e:VendorEntry {family:$f}) WHERE e.concept <> ''
                WITH e.concept AS c, collect(DISTINCT e.vendor) AS vs, count(*) AS n
                WHERE size(vs) > 1
                RETURN c, n ORDER BY c
                """,
                f=family,
            )
        )
        for r in rows:
            print(f"  {r['c']:<24} entries {r['n']:>2}")
        print(f"  total: {len(rows)}")

        print("Documented defaults (anchors to search for in the dump):")
        for r in s.run(
            """
            MATCH (f:VendorFact {family:$f, kind:'const'}) WHERE f.value <> ''
            RETURN f.value AS value, f.units AS units, f.subject AS subject,
                   f.applies_to AS scope ORDER BY f.concept, f.subject
            """,
            f=family,
        ):
            print(f"  {r['value']:>10} {r['units']:<22} {r['scope']:<9} {r['subject']}")

        print("Open work (vendor gaps and reconciliation hypotheses):")
        for r in s.run(
            """
            MATCH (f:VendorFact {family:$f}) WHERE f.kind IN ['gap','hypothesis']
            RETURN f.kind AS kind, f.vendor AS vendor, f.subject AS subject
            ORDER BY f.kind, f.vendor, f.subject
            """,
            f=family,
        ):
            print(f"  {r['kind']:<11} {r['vendor']:<8} {r['subject']}")



def main():
    raise SystemExit("This layer belongs to the kb compiler; use `uv run kb sync`.")


if __name__ == "__main__":
    main()
