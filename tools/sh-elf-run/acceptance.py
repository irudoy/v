"""Check verification boundaries and emit the existing protocol input manifests.

Source anchors identify mechanisms. The protocol manifests preserve their full
current input closures, which can exceed a group's semantic repeat boundary.
Neither metadata nor timings authorize dropping a required execution gate.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
for path in (TOOL_DIR, ROOT, ROOT / 'tools/kb/src'):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

PRIMARY_STAGES = ('toolchain', 'reconstruction_fixture', 'map_switching',
                  'delay_slot_probe', 'rolling_launch', 'can_telemetry',
                  'relocated_runtime_targets')
CATEGORIES = {'pipeline', 'stock', 'evidence_and_acceptance'}
STOCK_GROUPS = ('upstream_fuel', 'airflow_bfs', 'interpolation', 'crank_rpm',
                'injection_calculation', 'injection_scheduler', 'knock',
                'closed_loop', 'cut_control', 'can_copy', 'sid22_pointer')
EVIDENCE_GROUPS = ('pipeline_integration', 'qualified_receipt_protocol',
                   'registered_python_test_evidence', 'native_publication_and_reuse',
                   'generated_projection_contracts')


def declared():
    return tomllib.loads((TOOL_DIR / 'acceptance.toml').read_text())


def registered():
    import verify_stock_code
    return verify_stock_code.REGIONS


def check(document, regions, root=ROOT):
    if type(document['schema']) is not int or document['schema'] != 1:
        raise ValueError('unknown verification-boundary schema')
    if (document['full_matrix_minimality'] != 'unproved'
            or document['qualification_policy'] !=
            'Required repository gates and exact current receipt protocols apply.'):
        raise ValueError('metadata cannot weaken the qualification boundary')
    groups = document['group']
    identities = [group['id'] for group in groups]
    if len(identities) != len(set(identities)):
        raise ValueError('duplicate verification group')
    expected = set(PRIMARY_STAGES) | {'elf_storage'} | set(STOCK_GROUPS) | set(EVIDENCE_GROUPS)
    if set(identities) != expected:
        raise ValueError('verification groups differ from the reviewed contract vocabulary')
    assigned = []
    for group in groups:
        if group['category'] not in CATEGORIES:
            raise ValueError('unknown verification category')
        expected_category = ('stock' if group['id'] in STOCK_GROUPS else
                             'evidence_and_acceptance' if group['id'] in EVIDENCE_GROUPS else 'pipeline')
        if group['category'] != expected_category:
            raise ValueError('verification group has a different category')
        for key in ('property', 'overlap', 'minimum_boundary', 'minimality'):
            if type(group[key]) is not str or not group[key]:
                raise ValueError('each verification group requires its evidence boundary')
        for key in ('repeat_triggers', 'source_anchors', 'limits'):
            if not group[key] or any(type(value) is not str or not value for value in group[key]):
                raise ValueError('each group requires explicit inputs, repeat triggers and limits')
        for value in group['source_anchors']:
            path = Path(value)
            if (path.is_absolute() or '..' in path.parts or path.parts[0] in ('kb', 'l0')
                    or not (root / path).is_file()):
                raise ValueError(f'unknown verification source anchor: {value}')
        if group['category'] == 'stock':
            if group['minimality'] != 'unproved' or not group['regions']:
                raise ValueError('stock matrix minimality requires independent evidence')
            assigned.extend(group['regions'])
        elif group['regions']:
            raise ValueError('only stock groups own region registrations')
    actual = [region.key for region in regions]
    if len(actual) != len(set(actual)) or Counter(assigned) != Counter(actual):
        raise ValueError('stock group partition differs from the executed registry')
    if not set(PRIMARY_STAGES) <= set(identities) or 'elf_storage' not in identities:
        raise ValueError('a primary verification stage lacks a group boundary')
    for group in groups:
        direct_sources(group, regions, root)
    return {'groups': len(groups), 'categories': dict(Counter(g['category'] for g in groups)),
            'stock_regions': len(regions), 'stock_cases': sum(region.cases for region in regions)}


def direct_sources(group, regions, root=ROOT):
    """Explicit anchors and transitive local C/assembly includes, not all provenance."""
    paths = set(group['source_anchors'])
    paths.update('tools/sh-elf-run/' + value for region in regions
                 if region.key in group['regions'] for value in (region.source, region.harness))
    pending = list(paths)
    include = re.compile(r'^\s*(?:#\s*include|\.include)\s+"([^"]+)"', re.MULTILINE)
    while pending:
        path = pending.pop()
        if Path(path).suffix not in ('.c', '.h', '.s'):
            continue
        for name in include.findall((root / path).read_text()):
            target = (Path(path).parent / name).as_posix()
            if '..' in Path(target).parts or not (root / target).is_file():
                raise ValueError(f'unresolved local execution include: {target}')
            if target not in paths:
                paths.add(target)
                pending.append(target)
    return {path: hashlib.sha256((root / path).read_bytes()).hexdigest() for path in sorted(paths)}


def manifests(document, regions):
    """Use the same tracked producers that govern current receipt freshness."""
    from kb import copy_evidence, copy_witness, sid22_evidence, test_evidence
    inventory = check(document, regions)
    return {'inventory': inventory,
            'contract_inputs': {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                                for path in ('tools/sh-elf-run/acceptance.py',
                                             'tools/sh-elf-run/acceptance.toml',
                                             'tools/sh-elf-run/execution_report.py', 'Makefile')},
            'direct_group_sources': {group['id']: direct_sources(group, regions)
                                     for group in document['group']},
            'protocol_inputs': {'CAN': copy_evidence.inputs(ROOT),
                                'SID22': sid22_evidence.inputs(ROOT),
                                'TEST': test_evidence.inputs(ROOT)},
            'GNU_source_producer_provenance': copy_witness.provenance(ROOT),
            'runtime_artifact_boundary': [
                'The actual ELF, reconstructed code/pools, fixture, aliases and ordered cases belong to execution.',
                'CAN/SID22 packets bind actual ELF/fixture/toolchain hashes and observations.',
                'Other region timings do not independently bind every physical execution artifact.',
                'Unchanged source anchors do not prove unchanged binaries, runtime libraries or environment.'],
            'qualification_policy': document['qualification_policy']}


def check_stages(text, regions):
    from execution_report import read
    rows = read(text, require_complete=True)
    expected = [('pipeline', name) for name in PRIMARY_STAGES]
    expected += [('stock', region.key) for region in regions]
    if [(row['start']['kind'], row['start']['name']) for row in rows] != expected:
        raise ValueError('actual timing stages differ from the complete primary registry order')
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--manifest', action='store_true')
    mode.add_argument('--stages', type=Path)
    args = parser.parse_args(argv)
    document, regions = declared(), registered()
    inventory = check(document, regions)
    if args.manifest:
        print(json.dumps(manifests(document, regions), sort_keys=True))
    elif args.stages:
        rows = check_stages(args.stages.read_text(), regions)
        print(json.dumps({'stage_count': len(rows), 'inventory': inventory}))
    else:
        print(json.dumps(inventory, sort_keys=True))


if __name__ == '__main__':
    main()
