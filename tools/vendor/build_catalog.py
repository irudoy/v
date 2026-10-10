#!/usr/bin/env python3
# Combines two vendor-dictionary transcriptions, refs/vendor/proecu-maps.csv (ProECU/EcuTek)
# and refs/vendor/uprev-maps.csv (UpRev), into refs/vendor/catalog.csv, the input to
# load_vendor.py as described in tools/map-analysis-pipeline.md. See
# refs/vendor/README.md for the
# transcription and annotation method.
#
# The catalog is generated and the transcriptions are handwritten. Edit the transcriptions,
# not the catalog: catalog.csv contains derived columns (origin, concept), and editing it
# would silently diverge from the dictionaries.
#
# Names are neither normalized nor rewritten. Source capitalization and typos are preserved,
# including ProECU's own uncertainty markers (`Idle Target #1a - ??`, `Sensor Multiplier Unk`).
# A name is the only information available from a ProECU tree screenshot, so it is a quotation.
# All analysis goes into separate columns and no entry is discarded.
#
# Run: uv run python tools/vendor/build_catalog.py
import argparse
import csv
import io
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "refs" / "vendor"

# --- origin: ProECU ---
# The entire racerom-supplement documents RaceROM features. In tuning-guide, only the explicit
# RaceROM tree branch is patched; the remainder is factory content.
# origin is normalized as factory | patch | unknown. The vendor column identifies the patch
# owner (ecutek -> RaceROM, uprev -> ARC).
#
# This column is required for Stage 5: a patch entry describes vendor code absent from stock,
# so matching a stock map to it would be wrong rather than merely weak. Group labels are not
# part of the rule because they are unreliable: `Rev Limit Per Gear Mode1-4` are RaceROM maps
# placed under `Limiters` beside factory maps. The source document and explicit tree root decide.
def proecu_origin(r):
    if r['doc'] == 'racerom-supplement':
        return 'patch'
    if r['group'].startswith('EcuTek RaceROM Maps//'):
        return 'patch'
    return 'factory'

# --- concept: curated annotation only where the link is justified ---
# Dictionary join key: entries sharing a concept describe the same entity. Names remain
# verbatim, and the two dictionaries use different terms for the same item
# (`BFS Multiplier (K-Factor)` versus `K - Fuel Multiplier`). An exact-name join would fail,
# while a similarity join would merge different items. The manual dictionary is therefore
# intentional: a link is a claim, not a string operation.
# An empty concept means "link not established", not "no link exists".
# exact: exact name -> concept; prefix: name starts with -> concept
PROECU_EXACT = {
    'BFS Multiplier (K-Factor)': 'bfs-multiplier',
    'MAF Sensor Scale (% to g/s) for Load': 'maf-gps-scalar',
    'MAF Sensor Scale Bank #1 (V to %)': 'maf-curve',
    'MAF Sensor Scale Bank #2 (V to %)': 'maf-curve',
    'MAF Voltage Min Allowed': 'maf-volts-min',
    'MAP Sensor Multiplier': 'map-sensor-scaling',
    'MAP Sensor Offset': 'map-sensor-scaling',
    'Sensor Multiplier Unk': 'map-sensor-scaling',
    'Sensor Offset Unk': 'map-sensor-scaling',
    'Coolant & AIT Sensor Scale': 'temp-sensor-scale',
    'Eng Oil Temp Scale': 'temp-sensor-scale',
    'Fuel Map': 'fuel-target',
    'Fuel Enrichment - Cold': 'fuel-comp',
    'Fuel Enrichment - Hot': 'fuel-comp',
    'Fuel Trim Per Cyl': 'cylinder-trim',
    'Injector Flow Scaling': 'injector-size',
    'Injector Lag Time Multiplier': 'injector-latency',
    'Injector Lag Time Offset': 'injector-latency',
    'Injector Minimum Open Time': 'injector-minimum',
    'Knock Sensitivity': 'knock-threshold',
    'Rev Limit - Fuel Cut': 'rev-limit-fuel',
    'Rev Limit - Fuel Cut Restore': 'rev-limit-restore',
    'Rev Limit - Fuel Cut Maximum': 'rev-limit-max',
    'Rev Limit - Throttle Cut': 'rev-limit-throttle',
    'Torque Actual': 'torque-actual',
    'Torque Demand': 'torque-demand',
    'Torque Demand - Trustful': 'torque-demand',
    'Idle Target #1 - Drive': 'idle-target-drive',
    'Idle Target #2 - Neutral': 'idle-target-neutral',
    'Idle Target #1a - ??': 'idle-target-load',
    'VVEL Control Shaft Angle to Duration': 'vvel-cs-angle',
    'VVEL Control Shaft Angle Trustful': 'vvel-cs-angle',
    'VVEL Control Shaft Max': 'vvel-cs-limit',
    'DoNotAdjust: VTC Max Advance by VVEL CS Angle': 'vvel-interference-vtc',
    'DoNotAdjust: VVEL Control Shaft Max by VTC Angle': 'vvel-interference-cs',
    'Accel Map Slow/Fast Switch': 'accel-map-switch',
    'Accel Map Slow/Fast Switch Trustful': 'accel-map-switch',
    'Accel To Throttle Lo/Hi Switch': 'accel-throttle-switch',
}
PROECU_PREFIX = [
    ('Cranking Fuel Injector Pulsewidth Initial', 'cranking-initial'),
    ('Cranking Fuel Injector Pulsewidth step',    'cranking-decay'),
    ('Cranking Fuel RPM Compensation',            'cranking-rpm-comp'),
    ('Overrun Fuel Cut',                          'overrun-fuel-cut'),
    ('Idle - target airflow rate',                'idle-airflow'),
    ('Idle Ignition Timing',                      'idle-ignition'),
    ('Ignition Timing Mode A1 Adj',               'ignition-trim'),
    ('Ignition Timing Mode B1',                   'ignition-mode-b'),
    ('Knock Control Enable A1',                   'knock-enable'),
    ('Knock Retard Multiplier',                   'knock-multiplier'),
    ('Speed Limit -',                             'speed-limit'),
    ('VTC Valve Advance',                         'vtc-advance'),
    ('VVEL Valve Duration',                       'vvel-duration'),
    ('VVEL Control Shaft Min',                    'vvel-cs-limit'),
    ('Accel to Throttle',                         'accel-throttle'),
    ('Accel To Throttle Lo',                      'accel-throttle'),
    ('Accel Map',                                 'accel-pedal'),
    ('Torque Filtering WOT',                      'torque-filtering-wot'),
]
UPREV_EXACT = {
    'K - Fuel Multiplier': 'bfs-multiplier',
    'Calculated Load': 'load-100pct',
    'Load Point Scaler': 'load-point-scaler',
    'Mass Air Flow Sensor': 'maf-curve',
    'Fuel Targets': 'fuel-target',
    'Fuel Compensation Main': 'fuel-comp',
    'Fuel Compensation Cold': 'fuel-comp',
    'Cylinder Trim': 'cylinder-trim',
    'Injector Minimum': 'injector-minimum',
    'Cranking Enrichment Initial Value': 'cranking-initial',
    'Ignition Timing Knock Windows': 'knock-enable',
    'Knock Listening Threshold': 'knock-threshold',
    'Cam Phasing': 'vtc-advance',
    'Rev Limit': 'rev-limit-fuel',
    'Throttle Cut Rev Limit': 'rev-limit-throttle',
    'Speed Limit': 'speed-limit',
    'Estimated Torque Delivered': 'torque-actual',
    # The same map as EcuTek 'Torque Demand' and A2L 'QH0/ Torque Conversion Map': axes,
    # output scale, section, and presence of a check copy match. Vendor interpretations differ
    # (torque request versus delivered-torque estimate); the structural link is recorded and
    # analyzed in facts.csv.
    'Throttle A': 'torque-demand',
    'Radiator Fan Speed by Temp': 'rad-fan-duty',
    'Idle Target': 'idle-target-neutral',
    'Idle Target Gear': 'idle-target-drive',
    'Idle Target Low': 'idle-target-load',
    'VVEL Angle': 'vvel-cs-angle',
    'VVEL Angle Alt': 'vvel-cs-angle',
    'VVEL Intake Phasing': 'vvel-interference-vtc',
    'VVEL Limit': 'vvel-interference-cs',
    'VVEL Max': 'vvel-cs-limit',
    'VVEL Min': 'vvel-cs-limit',
    'VVEL Decel': 'vvel-duration',
    'VVEL Duration WOT': 'vvel-duration',
    'ETC Control': 'etc-control',
    'NATS': 'nats',
}
UPREV_PREFIX = [
    ('Injector Priming Pulse Mode',   'cranking-decay'),
    ('Injector Priming Pulse by RPM', 'cranking-rpm-comp'),
    ('Ignition Timing Trim',          'ignition-trim'),
    ('Acc. Throttle Request',         'accel-throttle'),
    ('VVEL Main Drivability',         'vvel-duration'),
]

def concept(name, exact, prefixes):
    if name in exact:
        return exact[name]
    for p, c in prefixes:
        if name.startswith(p):
            return c
    return ''

def read(name, vendor=VENDOR):
    with (vendor / name).open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def build(vendor=VENDOR):
    out = []
    for r in read('proecu-maps.csv', vendor):
        out.append(dict(
            vendor='ecutek', doc=r['doc'], section=r['section'], group=r['group'],
            name=r['name'], dims='', axis_x='', axis_y='', output='',
            origin=proecu_origin(r), level=r['level'],
            concept=concept(r['name'], PROECU_EXACT, PROECU_PREFIX),
            source=r['source_image'], note=r['note']))
    for r in read('uprev-maps.csv', vendor):
        out.append(dict(
            vendor='uprev', doc=r['doc'], section=r['section'], group='',
            name=r['name'], dims=r['dims'], axis_x=r['axis_x'], axis_y=r['axis_y'],
            output=r['output'], origin=r['origin'], level='',
            concept=concept(r['name'], UPREV_EXACT, UPREV_PREFIX),
            source=r['anchor'], note=r['note']))

    # Unmatched annotations would silently omit dictionary links.
    named = {r['name'] for r in out}
    stale = sorted((set(PROECU_EXACT) | set(UPREV_EXACT)) - named)
    if stale:
        raise ValueError(f"concept refers to names absent from the dictionaries: {stale}")
    return out


def render(rows):
    cols = ['vendor','doc','section','group','name','dims','axis_x','axis_y','output',
            'origin','level','concept','source','note']
    output = io.StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=cols, quoting=csv.QUOTE_MINIMAL,
                            lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode('utf-8')


def generate(vendor=VENDOR, *, check=False):
    rows = build(vendor)
    expected = render(rows)
    path = vendor / 'catalog.csv'
    if check:
        if not path.is_file():
            raise ValueError(f"{path}: missing (fix: make vendor-catalog)")
        if path.read_bytes() != expected:
            raise ValueError(f"{path}: differs from its rendering (fix: make vendor-catalog)")
    else:
        path.write_bytes(expected)
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true',
                        help='compare the catalog without writing')
    args = parser.parse_args(argv)
    try:
        rows = generate(check=args.check)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    origins = {o: sum(r['origin'] == o for r in rows)
               for o in ('factory', 'patch', 'unknown')}
    concepts = {r['concept'] for r in rows if r['concept']}
    both = sum(len({r['vendor'] for r in rows if r['concept'] == c}) > 1
               for c in concepts)
    print(f"catalog.csv: {len(rows)} entries "
          f"({sum(r['vendor'] == 'ecutek' for r in rows)} ecutek, "
          f"{sum(r['vendor'] == 'uprev' for r in rows)} uprev)")
    print(f"origin: factory {origins['factory']}, patch {origins['patch']}, "
          f"unknown {origins['unknown']} (Stage 5 matches only factory)")
    print(f"concept: {sum(bool(r['concept']) for r in rows)} entries, "
          f"{len(concepts)} values, {both} covered by both dictionaries")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
