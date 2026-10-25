"""Exact proof applicability and missing obligations for saved source groups.

The report selects source work. Existing guarded consumers alone admit evidence.
Function membership, a shared callee and source preparation supply no coverage.
"""

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import tomllib

from kb import ordinary_access_registry as registry, proof_adapter, proof_sources, test_contract

SOURCE = 'tools/kb/src/kb/proof_reuse.py'
OBLIGATIONS = ('original', 'datum', 'site', 'width', 'direction', 'function',
    'entry', 'phase', 'premises', 'call-premises', 'image', 'analysis',
    'source-closure', 'independent-state', 'independent-numerical', 'physical-carrier',
    'branch-call-return', 'fixed-other-causal', 'full-native-types-TEST-scopes', 'same-primary')
LOCATION = re.compile(r'([0-9a-z]+)-([0-9a-f]{8})/(?:ram|const|tbl|reg|fn|axis)')


def sha(data):return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode())


def _literal_names(root, path):
    values = {}
    for node in ast.parse((Path(root)/path).read_text(), filename=path).body:
        if not isinstance(node, ast.Assign):continue
        for name in node.targets:
            if not isinstance(name, ast.Name):continue
            try:values[name.id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                value = node.value
                if (isinstance(value, ast.Call) and isinstance(value.func, ast.Name)
                        and value.func.id == 'Path' and len(value.args) == 1 and not value.keywords
                        and isinstance(value.args[0], ast.Constant) and type(value.args[0].value) is str):
                    values[name.id] = value.args[0].value
    return values


def _producer_contract(root, producer):
    path = 'tools/sh-elf-run/'+producer+'.py'
    tree = ast.parse((Path(root)/path).read_text(), filename=path)
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == 'kb':
            for item in node.names:
                if item.asname == 'contract':
                    return 'tools/kb/src/kb/'+item.name+'.py'
    return None


def _component(root, identity, producer, sources):
    producer_path = 'tools/sh-elf-run/'+producer+'.py'
    values = _literal_names(root, producer_path)
    contract_path = _producer_contract(root, producer)
    contract = _literal_names(root, contract_path) if contract_path else {}
    descriptor = contract.get('DESCRIPTOR')
    declared = tomllib.loads((Path(root)/descriptor).read_text()) if descriptor else {}
    adapter = declared.get('adapter')
    entries = adapter['entries'] if adapter else ([contract['ENTRY']] if type(contract.get('ENTRY')) is int else [])
    windows = contract.get('WINDOWS', ())
    if type(windows) not in (list,tuple):windows=()
    scope = dict(id=identity, producer=producer_path, contract=contract_path,
        descriptor=descriptor, entries=entries, windows=list(windows),
        scope=declared.get('scope'), case_kinds=adapter['kind'] if adapter else None,
        stock_image=declared.get('image_sha256'), source_prepared=True, accepted=False,
        accepted_status='not-evaluated', semantic_admission=False)
    scope['premises_binding'] = digest(dict(descriptor=declared,
        producer_sha256=sha((Path(root)/producer_path).read_bytes()),
        contract_sha256=sha((Path(root)/contract_path).read_bytes()) if contract_path else None))
    seeds = set(sources) | {producer_path, SOURCE, proof_sources.SOURCE}
    if contract_path:seeds.add(contract_path)
    if descriptor:seeds.add(descriptor)
    if adapter:seeds.update(proof_adapter.source_files(root, descriptor))
    for name in ('HARNESS', 'OBSERVER', 'RETURN', 'SOURCE', 'HEADER_SOURCE'):
        value = values.get(name)
        if type(value) is str and Path(value).suffix in {'.c', '.s', '.h', '.py'}:
            path = value if value.startswith(('tools/', 'defs/')) else 'tools/sh-elf-run/'+value
            seeds.add(path)
    for name in ('ASSEMBLY', 'OBSERVER'):
        value = contract.get(name)
        if type(value) is str and value.startswith('tools/'):seeds.add(value)
    unit = contract.get('UNIT')
    if type(unit) is dict and type(unit.get('assembly')) is str:seeds.add(unit['assembly'])
    scope['source_seeds'] = sorted(seeds)
    scope['generated_headers'] = ['tools/sh-elf-run/'+values['HEADER']] if 'HEADER' in values else []
    return scope


def _reference(row, descriptor, component, *, family=None):
    original = json.loads(row['original_claim_json'])
    if digest(original) != row['original_claim_sha256']:
        raise ValueError('a reusable reference changes its exact original identity')
    site = row.get('sites') or ([row['source_read']] if 'source_read' in row else [])
    function = row.get('function')
    if type(function) is str:
        located=re.fullmatch(r'7mfk:([0-9a-fA-F]{8})',function)
        function=int(located[1],16) if located else None
    entries = []
    if function in component['entries']:entries = [function]
    for window in component['windows']:
        if type(window) is dict and window.get('parent') == function:entries.append(window['start'])
    calls = []
    if 'callsite' in row:
        calls.append({key:row[key] for key in ('caller','target','source_read','callsite','delay_slot','register') if key in row})
    return dict(id=row['id'], component=component['id'], descriptor=descriptor, family=family,
        original=row['original_claim_sha256'], owner=row['owner'], datum=row['address'],
        sites=site, width=row.get('width_bytes'), direction=original['type'],
        disposition=row.get('direction', json.loads(row.get('proposed_claim_json','{}')).get('type')),
        function=function, entry=entries[0] if len(set(entries)) == 1 else None,
        phase='function:'+format(function,'08x') if type(function) is int else None,
        premises=component['premises_binding'], call_premises=calls or None,
        image=component['stock_image'], analysis=None, source_prepared=True,
        accepted=False, accepted_status='not-evaluated',
        full_native_preimage=row.get('original_native_sha256'),
        full_native_postimage=row.get('proposed_native_sha256'),
        native_types=dict(width=row.get('declared_width'), signed=row.get('declared_signed')),
        evidence=json.loads(row['evidence_json']) if 'evidence_json' in row else None)


def index(root):
    """Read existing exact registrations; build neither matrices nor evidence."""
    from kb import calculation_dependency_contract as calculations
    root = Path(root).resolve();components, references = {}, []
    for family in registry.families():
        for identity, producer in family.captures:
            components[identity] = _component(root, identity, producer, family.source_files)
        declared = family.contract.descriptor(root)
        for row in declared['reference']:
            references.append(_reference(row, family.contract.DESCRIPTOR, components[row['component']], family=family.mode))
    # Calculation dispositions retain their own guarded operation and consumers.
    for row in calculations.rows(root):
        identity = row.get('component')
        if identity not in components:
            identity = 'calculation:'+row['family']
            components.setdefault(identity, dict(id=identity, producer=None, contract=None,
                descriptor=row['descriptor'], entries=[], windows=[], scope=row['family'],
                case_kinds=None, stock_image=calculations.IMAGE_SHA256,
                premises_binding=digest(dict(descriptor=row['descriptor'], family=row['family'])),
                source_prepared=True, accepted=False, accepted_status='not-evaluated', semantic_admission=False,
                source_seeds=[row['descriptor'], 'tools/kb/src/kb/'+row['module']+'.py',
                    'tools/kb/src/kb/'+row['consumer']+'.py', 'tools/kb/src/kb/calculation_dependency_contract.py'],
                generated_headers=[]))
        references.append(_reference(row, row['descriptor'], components[identity], family='calculation-dependency'))
    # The existing coherent tuple owns lane/transfer distinctions and caller parents.
    path = 'tools/kb/src/kb/coherent_copy_members.py';values = _literal_names(root, path)
    component = dict(id='coherent', producer='tools/sh-elf-run/coherent_snapshot_copy.py',
        contract=None, descriptor=values['DESCRIPTOR'], entries=[], windows=[], scope=values['KEY'],
        case_kinds=None, stock_image=values['IMAGE_SHA256'], premises_binding=sha((root/path).read_bytes()),
        source_prepared=True, accepted=False, accepted_status='not-evaluated', semantic_admission=False,
        source_seeds=[path, values['DESCRIPTOR'], 'tools/kb/src/kb/coherent_copy_evidence.py',
            'tools/sh-elf-run/coherent_snapshot_copy.py'], generated_headers=[])
    components['coherent'] = component
    for datum, direction, owner, bits, signed, original, call, mechanism, site, lane, transfer in values['MEMBERS']:
        parent = values['CALLERS'].get(call, (0x20DFE, 'coherent_snapshot/fn'))[0]
        references.append(dict(id=original, component='coherent', descriptor=path, family='coherent-copy',
            original=original, owner=owner, datum=datum, sites=[site], width=transfer//8,
            direction=direction, disposition=direction, function=parent, entry=None,
            phase='function:'+format(parent,'08x'), premises=component['premises_binding'],
            call_premises=[dict(callsite=call, mechanism=mechanism, lane_offset=lane)],
            image=values['IMAGE_SHA256'], analysis=None, source_prepared=True, accepted=False,
            accepted_status='not-evaluated', native_types=dict(width=bits, signed=signed),
            full_native_preimage=None, full_native_postimage=None, evidence=None))
    return dict(schema=1, components=components, references=references, semantic_admission=False)


def loader_declarations(root):
    """Finite targets of existing registry, projection and private tool loaders.

    The source boundary includes all existing private SH Python tools, matching
    the complete primary's current provenance. It makes no minimality claim.
    """
    from kb import calculation_dependency_contract as calculations, value_flow
    root = Path(root).resolve()
    hooks = sorted({path for family in registry.families() for path in family.source_files})
    calculation_hooks = sorted({'tools/kb/src/kb/'+name+'.py' for family, module, consumer in calculations.FAMILIES
        for name in (module, consumer)})
    private = sorted(path.relative_to(root).as_posix() for path in (root/'tools/sh-elf-run').glob('*.py'))
    projections = tomllib.loads((root/'tools/kb/projections.toml').read_text())
    generators = {'tools/check_projection_contract.py'}
    for row in projections['projection']:
        generator = row['generator']
        if re.fullmatch(r'kb\.[a-zA-Z_][a-zA-Z0-9_.]*:[a-zA-Z_]\w*', generator):
            generators.add('tools/kb/src/'+generator.split(':')[0].replace('.', '/')+'.py')
    result = {
        'tools/kb/src/kb/ordinary_access_registry.py':hooks,
        'tools/kb/src/kb/calculation_dependency_contract.py':calculation_hooks,
        'tools/kb/src/kb/calculation_dependency_evidence.py':calculation_hooks,
        'tools/kb/src/kb/test_stock_capture.py':private,
        'tools/kb/src/kb/project.py':sorted(generators),
        'tools/kb/src/kb/value_flow.py':sorted({'tools/kb/src/kb/'+name+'.py'
            for names in value_flow.COMPONENTS.values() for name in names}),
    }
    for module, key in (('ledgers','DTC_DECODER'),('dids','DECODER')):
        path='tools/kb/src/kb/adapters/'+module+'.py'
        declared=_literal_names(root,path)
        if type(declared.get(key)) is str:result[path]=[declared[key]]
    # Two existing domain loaders select exact declared numerical source names.
    for evidence, contract, key in (
            ('phase_normalization_capture_evidence','phase_normalization_contract','NUMERIC'),
            ('bank_pulse_stage_capture_evidence','bank_pulse_stage_semantics','PRECURSOR_NUMERIC')):
        path='tools/kb/src/kb/'+contract+'.py'
        if not (root/path).is_file():continue
        declared=_literal_names(root,path)
        if type(declared.get(key)) is str:
            result['tools/kb/src/kb/'+evidence+'.py']=[declared[key]]
    return result


def adapter_closures(root):
    """Complete declared reference-adapter dependencies for the existing gates."""
    loaders = loader_declarations(root)
    result = {}
    for descriptor in proof_adapter.DESCRIPTORS:
        adapter = proof_adapter.descriptor(root, descriptor)
        result[descriptor] = proof_sources.closure(root,
            proof_adapter.source_files(root, descriptor), declared_edges=loaders,
            generated_headers=['tools/sh-elf-run/'+adapter['header']])
    return result


def generated_input_headers(root):
    """Existing capture-owned private headers, distinct from persistent includes."""
    root=Path(root).resolve();result=set()
    for path in (root/'tools/sh-elf-run').glob('*_capture.py'):
        declared=_literal_names(root,path.relative_to(root).as_posix())
        header=declared.get('HEADER')
        if type(header) is str and re.fullmatch(r'[a-z0-9-]+\.h',header):
            result.add('tools/sh-elf-run/'+header)
    return result


def compare(request, candidate):
    """Exact known fields cover only their own source obligations."""
    covered, missing, conflicts = [], [], []
    fields = {'original':'original', 'datum':'datum', 'site':'sites', 'width':'width',
        'direction':'direction', 'function':'function', 'entry':'entry', 'phase':'phase',
        'premises':'premises', 'call-premises':'call_premises', 'image':'image', 'analysis':'analysis'}
    for obligation, field in fields.items():
        expected, actual = request.get(field), candidate.get(field)
        if expected is None or actual is None or field == 'sites' and (expected == [] or actual == []):
            missing.append(dict(obligation=obligation, reason='unknown-required-binding',
                requested=expected, component=actual))
        elif not test_contract.exact(expected, actual):
            conflicts.append(dict(obligation=obligation, reason='incompatible-'+obligation,
                requested=expected, component=actual))
        else:covered.append(obligation)
    return dict(component=candidate['component'], reference=candidate['id'], covered=covered,
        missing=missing, incompatible=conflicts, source_compatible=not missing and not conflicts,
        accepted=False, accepted_status='not-evaluated', semantic_admission=False)


def _claims(group):
    return [*group.get('source_prepared_originals', []), *group.get('remaining_originals', [])]


def _request(row, requirement):
    match = LOCATION.fullmatch(row['subject'])
    function = LOCATION.fullmatch(row['function'])
    if match is None or function is None:
        raise ValueError('a saved group changes its exact datum or function identity')
    original = row['original_canonical_claim']
    if (not row['function'].endswith('/fn') or match[1] != function[1]
            or original.get('layout') != match[1] or original.get('owner') != row['meaning']
            or digest(original) != row['original_claim_sha256']):
        raise ValueError('a saved group changes its exact original canonical claim')
    result = dict(original=row['original_claim_sha256'], owner=row['meaning'],
        datum=int(match[2],16), function=int(function[2],16), direction=original['type'],
        sites=None, width=None, entry=None, phase=None, premises=None, call_premises=None,
        image=None, analysis=None)
    if requirement is not None:
        allowed = {'original','datum','function','direction','sites','width','entry','phase','premises','call_premises','image','analysis'}
        if type(requirement) is not dict or set(requirement)-allowed:
            raise ValueError('a group requirement changes its exact bounded schema')
        for key in ('original','datum','function','direction'):
            if key in requirement and not test_contract.exact(requirement[key], result[key]):
                raise ValueError('a group requirement changes its original datum, function or direction')
        result.update(requirement)
    return result


def _prepared(value, references):
    if (type(value) is not dict or value.get('source_preparation_is_qualification') is not False
            or type(value.get('source_prepared_originals')) is not dict):
        raise ValueError('the prepared-original manifest grants no qualification or inferred completion')
    result = set();unresolved = []
    for original, declarations in value['source_prepared_originals'].items():
        known = [row for row in references if row['original'] == original]
        if (type(original) is not str or not re.fullmatch('[0-9a-f]{64}', original)
                or type(declarations) is not list or not declarations
                or any(type(item) is not dict for item in declarations)
                or not any(any(row['descriptor'] == item.get('source') and row['component'] == item.get('component')
                    and ('id' not in item or row['id'] == item['id'])
                    and ('call' not in item or any(call.get('callsite') == item['call']
                        for call in row['call_premises'] or [])) for row in known)
                    for item in declarations)):
            unresolved.append(dict(original=original, reason='prepared-original-has-no-current-exact-reference'))
        else:result.add(original)
    return result, unresolved


def flow_binding(root, candidate, component, flows):
    """Use current flow structure only; it cannot supply independent evidence."""
    from kb import derive,value_flow
    matching = [flow for flow in flows if flow.get('component') == candidate['component']
        and flow.get('request',{}).get('datum') == candidate['datum']
        and flow.get('request',{}).get('load_site') in candidate['sites']]
    if not matching:return candidate, []
    if len(matching) != 1:
        return candidate, [dict(reason='ambiguous-exact-datum-flow-binding')]
    if candidate['component'] not in value_flow.COMPONENTS:
        return candidate,[dict(reason='unsupported-bounded-flow-component')]
    flow = matching[0];binding = flow.get('binding',{});premises = flow.get('premises',{})
    if (flow.get('schema') != 1 or type(flow.get('schema')) is not int
            or flow.get('kind') != 'bounded-concrete-value-flow'
            or flow.get('status') != 'resolved-concrete-path' or flow.get('unresolved_edges')
            or flow.get('source_prepared') is not True or flow['request'].get('layout')!='7mfk'
            or any(flow.get(name) is not False for name in
                ('accepted','executable_evidence','causal_evidence','semantic_admission'))
            or flow['request'].get('width_bytes') != candidate['width']
            or type(flow['request'].get('width_bytes')) is not int
            or digest(binding) != flow.get('analysis_sha256')
            or binding.get('image_sha256') != candidate['image']
            or binding.get('descriptor_sha256') != sha((Path(root)/component['descriptor']).read_bytes())
            or digest(premises.get('case')) != binding.get('input_sha256')
            or type(binding.get('sources')) is not dict
            or not binding['sources']):
        return candidate, [dict(reason='incompatible-or-unresolved-flow-structure')]
    path=flow.get('path');expected_address=(0x01000000+(candidate['datum']&65535)
        if candidate['datum']>=0xFFFF0000 else candidate['datum'])
    if (type(path) is not dict or type(path.get('nodes')) is not list
            or type(path.get('source_definitions')) is not list or not path['source_definitions']
            or type(path.get('outputs')) is not list or not path['outputs']
            or any(type(node) is not dict or type(node.get('id')) is not int or node['id']<0 for node in path['nodes'])
            or any(type(identity) is not int for identity in (*path['source_definitions'],*path['outputs']))):
        return candidate,[dict(reason='incomplete-exact-datum-flow-path')]
    nodes={node['id']:node for node in path['nodes']}
    if len(nodes)!=len(path['nodes']):return candidate,[dict(reason='conflicting-flow-definitions')]
    for identity in path['source_definitions']:
        node=nodes.get(identity,{})
        if (node.get('operation')!='memory-read'
                or not test_contract.exact((node.get('address'),node.get('site'),node.get('width_bytes')),
                    (expected_address,flow['request']['load_site'],candidate['width']))):
            return candidate,[dict(reason='wrong-exact-datum-flow-root')]
    for node in nodes.values():
        for key in ('data_inputs','address_inputs','control_inputs'):
            if (type(node.get(key)) is not list or any(type(item) is not int
                    or item not in nodes or item>=node['id'] for item in node[key])):
                return candidate,[dict(reason='unknown-or-conflicting-flow-edge')]
    if any(identity not in nodes for identity in path['outputs']):
        return candidate,[dict(reason='missing-exact-datum-flow-result')]
    origins={}
    for identity,node in sorted(nodes.items()):
        parents=(*node['data_inputs'],*node['address_inputs'],*node['control_inputs'])
        origins[identity]=({identity} if identity in path['source_definitions'] else set())|set().union(
            *(origins[parent] for parent in parents))
    if any(not origins[identity] for identity in path['outputs']):
        return candidate,[dict(reason='result-has-no-exact-datum-flow-carrier')]
    for path, identity in binding['sources'].items():
        path = proof_sources.safe_path(path)
        if not (Path(root)/path).is_file() or sha((Path(root)/path).read_bytes()) != identity:
            return candidate, [dict(reason='stale-flow-source-binding', source=path)]
    if derive._pair_digest('7mfk',Path(root)) != binding.get('L0_analysis_sha256'):
        return candidate, [dict(reason='stale-flow-L0-analysis-binding')]
    entry = premises.get('case',{}).get('entry')
    if type(entry) is not int or component['entries'] and entry not in component['entries']:
        return candidate, [dict(reason='incompatible-flow-entry-phase')]
    value = dict(candidate, analysis=flow['analysis_sha256'], entry=entry,
        call_premises=candidate['call_premises'] if candidate['call_premises'] is not None else flow.get('calls'))
    return value, []


def report(root, groups, function, prepared, *, requirements=None, inputs=None, anchors=None, model=None, flows=()):
    """Select one coherent saved group, preserving separate source/accepted states."""
    if (type(groups) is not dict or type(groups.get('groups')) is not list
            or requirements is not None and type(requirements) is not dict
            or type(flows) not in (list,tuple) or any(type(flow) is not dict for flow in flows)):
        raise ValueError('proof preparation requires typed saved groups, requirements and flow responses')
    root = Path(root).resolve();catalog = index(root);requirements = {} if requirements is None else requirements
    matches = [row for row in groups['groups'] if row['function'] == function]
    if len(matches) != 1:raise ValueError('the saved source descriptions do not name one exact coherent group')
    group = matches[0];claims = _claims(group)
    if len({row['original_claim_sha256'] for row in claims}) != len(claims):
        raise ValueError('a coherent source group repeats an exact original')
    prepared_set, unresolved_prepared = _prepared(prepared, catalog['references'])
    unknown_requirements = set(requirements)-{row['original_claim_sha256'] for row in claims}
    if unknown_requirements:raise ValueError('a group requirement names another original')
    results, selected_components = [], set()
    for claim in claims:
        request = _request(claim, requirements.get(claim['original_claim_sha256']))
        candidates = [row for row in catalog['references'] if row['original'] == request['original']
            or row['datum'] == request['datum'] or row['function'] == request['function']]
        bound = [flow_binding(root, row, catalog['components'][row['component']], flows) for row in candidates]
        comparisons = [dict(compare(request,row), flow_unresolved=unresolved) for row,unresolved in bound]
        for comparison in comparisons:
            if comparison['flow_unresolved']:comparison['source_compatible']=False
        for candidate, comparison in zip(candidates, comparisons):
            selected_components.add(candidate['component'])
            if (model is not None and candidate['original'] == request['original']
                    and not comparison['incompatible'] and candidate['family'] in registry.MODES
                    and candidate['evidence'] is not None):
                family = next(item for item in registry.families() if item.mode == candidate['family'])
                accepted = bool(family.evidence.accepted(model, candidate['evidence']))
                comparison.update(existing_exact_proof_accepted=accepted,
                    accepted=False,
                    accepted_status='accepted-exact-original-scope' if accepted else 'refused')
            comparison['missing'].extend(dict(obligation=name, reason='independent-guarded-evidence-required')
                for name in OBLIGATIONS if name not in comparison['covered']
                and name not in {item['obligation'] for item in comparison['missing']}
                and name not in {item['obligation'] for item in comparison['incompatible']})
        source_prepared = request['original'] in prepared_set
        results.append(dict(original=request['original'], request=request, source_prepared=source_prepared,
            accepted=any(row.get('existing_exact_proof_accepted', False) for row in comparisons),
            accepted_status='evaluated' if model is not None else 'not-evaluated',
            remaining_source=not source_prepared, candidates=comparisons,
            missing_if_no_candidate=list(OBLIGATIONS) if not candidates else []))
    dependencies = {};loaders = loader_declarations(root)
    for identity in sorted(selected_components):
        component = catalog['components'][identity]
        value = proof_sources.closure(root, component['source_seeds'],
            declared_edges=loaders,
            generated_headers=component['generated_headers'])
        if inputs is not None:
            try:proof_sources.require_manifest(value, inputs, anchors=anchors)
            except ValueError as error:value['manifest_failure'] = str(error)
        dependencies[identity] = value
    for result in results:
        for candidate in result['candidates']:
            closure = dependencies[candidate['component']]
            complete = closure['complete_declared_closure'] and 'manifest_failure' not in closure
            if complete:
                candidate['covered'].append('source-closure')
                candidate['missing'] = [item for item in candidate['missing'] if item['obligation'] != 'source-closure']
            else:
                for item in candidate['missing']:
                    if item['obligation'] == 'source-closure':
                        item.update(reason='incomplete-or-unbound-declared-source-closure',
                            unresolved=closure['unresolved_edges'], manifest_failure=closure.get('manifest_failure'))
    return dict(schema=1, kind='bounded-proof-group-preparation', function=function,
        claims=results, prepared_originals=sorted(row['original'] for row in results if row['source_prepared']),
        remaining_originals=sorted(row['original'] for row in results if row['remaining_source']),
        accepted_originals=sorted(row['original'] for row in results if row['accepted']),
        prepared_manifest_unresolved=unresolved_prepared, source_dependencies=dependencies,
        structural_candidates=deepcopy(group.get('shared_code_candidates', [])),
        structural_candidates_are_evidence=False, source_preparation_is_qualification=False,
        canonical_publication=False, receipt_publication=False, semantic_admission=False,
        scale_admission=False,units_admission=False,native_geometry_inference=False,
        reverse_identity_donation=False,hardware_qualification=False)


def saved_report(root, group_path, function, prepared_path, *, requirement_path=None,
        flow_paths=(), input_path=None, model=None):
    """Read exact saved artifacts and current sources through the normal KB API."""
    from kb import ignition_literal_evidence
    root=Path(root).resolve();loaded={}
    def objects(pairs):
        value={}
        for key,item in pairs:
            if key in value:raise ValueError('a saved proof preparation artifact repeats a JSON key')
            value[key]=item
        return value
    def read(path):
        value=Path(path)
        if value.is_absolute():
            try:value=value.relative_to(root)
            except ValueError as error:raise ValueError('proof preparation inputs must belong to this checkout') from error
        if not value.parts or '..' in value.parts or value.parts[0] not in {'tmp','.kb'}:
            raise ValueError('proof preparation reads saved local artifacts under tmp/ or .kb/')
        name=value.as_posix();raw=(root/value).read_bytes();loaded[name]=sha(raw)
        return json.loads(raw,object_pairs_hook=objects)
    groups=read(group_path);prepared=read(prepared_path)
    requirements=read(requirement_path) if requirement_path is not None else None
    flows=[read(path) for path in flow_paths]
    original=read(input_path) if input_path is not None else None
    if original is None:inputs=ignition_literal_evidence.execution_inputs(root)
    elif 'source_inputs_sha256' in original:inputs=original['source_inputs_sha256']
    elif 'candidate' in original:inputs=original['candidate']['producer_inputs']
    else:raise ValueError('the saved execution input manifest has no complete current source map')
    document=tomllib.loads((root/'tools/sh-elf-run/acceptance.toml').read_text())
    anchors={path for group in document['group'] for path in group['source_anchors']}
    for value in adapter_closures(root).values():
        if value['complete_declared_closure']:anchors.update(value['files'])
    result=report(root,groups,function,prepared,requirements=requirements,flows=flows,
        inputs=inputs,anchors=anchors,model=model)
    for path,identity in loaded.items():
        if sha((root/path).read_bytes())!=identity:
            raise ValueError('a saved proof preparation input changes during the read')
    return dict(result,input_artifacts=loaded,
        acceptance_anchor_policy='Explicit anchors and the existing pipeline integration declared dependency closure.')
