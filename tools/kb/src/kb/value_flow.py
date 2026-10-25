"""Concrete bounded value paths over exact instruction and analysis inputs.

The existing state equations supply the path, not executable or causal evidence.
SSA-like definitions retain data, address and path-control edges separately.
"""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from kb import byte_surface_equations as state, derive, fingerprint, proof_adapter, repo, sh2

COMPONENTS = {
    'closed_loop_coolant_paths': ('closed_loop_coolant_access_contract', 'closed_loop_coolant_matrix'),
    'maf_record_paths': ('maf_record_contract', 'maf_record_matrix'),
}
SOURCE_FILES = ('tools/kb/src/kb/value_flow.py', 'tools/kb/src/kb/byte_surface_equations.py',
    'tools/kb/src/kb/cli.py', 'tools/kb/src/kb/mcp.py',
    'tools/kb/src/kb/sh2.py', 'tools/kb/src/kb/derive.py', 'tools/kb/src/kb/repo.py',
    'tools/kb/src/kb/fingerprint.py', 'tools/kb/projections.toml',
    'tools/ghidra/TraceRamAccesses.java', 'tools/ghidra/InventoryPointerArgs.java')
STACK = 0x02010000
CONTINUATION = 0x02020000


def sha(data):
    return hashlib.sha256(data).hexdigest()


def _plain(value):
    return json.loads(json.dumps(value, sort_keys=True))


class Definitions:
    def __init__(self, source, site, width):
        self.source, self.site, self.width = source, site, width
        self.nodes, self.by_id, self.memory = [], {}, {}
        self.controls, self.roots, self.outputs, self.unknown = [], [], [], []
        self.pending_returns = {}
        self.registers = [self.add('entry-register', register=index) for index in range(16)]
        self.special = {name: self.add('entry-special', register=name)
            for name in ('gbr', 'mach', 'macl', 'sr', 'pr')}

    def add(self, operation, inputs=(), *, address_inputs=(), controls=None, source=False, **values):
        controls = tuple(self.controls) if controls is None else tuple(controls)
        identity = len(self.nodes)
        dependencies = tuple(dict.fromkeys((*inputs, *address_inputs, *controls)))
        roots = set().union(*(set(self.by_id[item]['source_roots']) for item in dependencies))
        if source:
            roots.add(identity);self.roots.append(identity)
        row = dict(id=identity, operation=operation, data_inputs=list(dict.fromkeys(inputs)),
            address_inputs=list(dict.fromkeys(address_inputs)), control_inputs=list(dict.fromkeys(controls)),
            source_roots=sorted(roots), **values)
        self.nodes.append(row);self.by_id[identity] = row
        return identity

    def memory_read(self, event, access, insn, before):
        at, width = access['address'], access['width_bytes']
        dependencies = tuple(dict.fromkeys(self.memory[(access['domain'], byte)]
            for byte in range(at, at+width) if (access['domain'], byte) in self.memory))
        address_inputs = []
        if insn.access is not None:
            base = insn.access.base
            address_inputs.append(self.special['gbr'] if base == 'gbr' else before[base])
            if insn.access.indexed:address_inputs.append(before[0])
        exact = at == self.source and event['site'] == self.site and width == self.width
        if event['site'] == self.site and at == self.source and width != self.width:
            self.unknown.append(dict(site=event['site'], reason='source-width-mismatch',
                expected=self.width, actual=width))
        return self.add('memory-read', dependencies, address_inputs=address_inputs, source=exact,
            site=event['site'], instruction=event['bytes'], address=at, width_bytes=width,
            domain=access['domain'], bytes=access['bytes'], register=access['register'],
            transform='sign-extend-'+str(width*8) if width < 4 else 'word32',
            value=(sh2.sext(int(access['bytes'], 16), width*8)&sh2.MASK if width < 4
                else int(access['bytes'], 16)))

    def instruction(self, event, call_entries):
        word, site = event['word'], event['site']
        insn = sh2.decode(word, site)
        n, m, low = word >> 8 & 15, word >> 4 & 15, word & 15
        before, old_special = list(self.registers), dict(self.special)
        reads = [self.memory_read(event, row, insn, before)
            for row in event['accesses'] if row['mode'] == 'read']
        loaded = {}
        for access, node in zip((row for row in event['accesses'] if row['mode'] == 'read'), reads):
            if access['register'] is not None:loaded[access['register']] = node
        for access in event['accesses']:
            if access['mode'] != 'write':continue
            register = access['register']
            if register is not None:
                inputs = (before[register],)
            elif word & 0xF0FF == 0x4022:
                inputs = (old_special['pr'],)
            elif word & 0xF0FF == 0x4012:
                inputs = (old_special['macl'],)
            elif word & 0xF0FF == 0x4013:
                inputs = (old_special['gbr'],)
            elif word >> 8 in (0xCD, 0xCF):
                inputs = tuple(reads)
            else:
                inputs = tuple(before)+tuple(old_special.values())
                self.unknown.append(dict(site=site, reason='unresolved-store-value-carrier'))
            address_inputs = []
            if insn.access is not None:
                base = insn.access.base
                address_inputs.append(old_special['gbr'] if base == 'gbr' else before[base])
                if insn.access.indexed:address_inputs.append(before[0])
            node = self.add('memory-store', inputs, address_inputs=address_inputs,
                site=site, instruction=event['bytes'], **{key: access[key]
                    for key in ('address', 'width_bytes', 'domain', 'bytes', 'register')})
            for byte in range(access['address'], access['address']+access['width_bytes']):
                self.memory[(access['domain'], byte)] = node
            self.outputs.append(node)
        for register in insn.writes:
            if register in loaded:
                self.registers[register] = loaded[register];continue
            operation, inputs = None, ()
            if insn.dest == register and insn.value is not None:
                operation = insn.value[0]
                if operation in ('copy', 'extu', 'exts'):
                    inputs = (before[insn.value[-1]],)
                elif operation in ('addi', 'shl', 'shr', 'sar'):
                    inputs = (before[register],)
                elif operation in ('add', 'sub'):
                    inputs = (before[register], before[insn.value[1]])
                elif operation == 'gbr':inputs = (old_special['gbr'],)
                elif operation not in ('const', 'pool', 'mova'):operation = None
            elif word & 0xF0FF == 0x001A:
                operation, inputs = 'copy-macl', (old_special['macl'],)
            elif word & 0xF0FF == 0x0029:
                operation, inputs = 'copy-T-bit', (old_special['sr'],)
            elif word & 0xF00F in (0x6007, 0x6009, 0x600B):
                operation, inputs = 'unary-register', (before[m],)
            elif word & 0xF00F in (0x2009, 0x200A, 0x200B, 0x200D, 0x300A, 0x300E):
                operation, inputs = 'binary-register', (before[n], before[m])
                if word & 0xF00F in (0x300A, 0x300E):inputs += (old_special['sr'],)
            elif word >> 8 in (0xC9, 0xCA, 0xCB):
                operation, inputs = 'immediate-bitwise', (before[0],)
            elif word & 0xF0FF in (0x4024, 0x4025):
                operation, inputs = 'rotate-through-T', (before[n], old_special['sr'])
            elif word & 0xF00F == 0x3004:
                operation, inputs = 'division-step', (before[n], before[m], old_special['sr'])
            elif insn.access is not None and register == insn.access.base:
                operation, inputs = 'address-update', (before[register],)
            if operation is None:
                operation, inputs = 'unresolved-register-transfer', tuple(before)+tuple(old_special.values())
                self.unknown.append(dict(site=site, register=register, reason=operation))
            self.registers[register] = self.add(operation, inputs, site=site, instruction=event['bytes'],
                register=register, before=event['before']['registers'][register],
                value=event['after']['registers'][register],
                decoded_transform=list(insn.value) if insn.value is not None else None)
        # Special registers and condition bits use the same exact instruction events.
        if word & 0xF00F in (0x0007, 0x200E):
            self.special['macl'] = self.add('multiply-to-macl', (before[n], before[m]),
                site=site, instruction=event['bytes'], value=event['after']['macl'])
        if word & 0xF0FF == 0x401E:
            self.special['gbr'] = self.add('copy-to-gbr', (before[n],), site=site, value=event['after']['gbr'])
        if word & 0xF0FF == 0x401A:
            self.special['macl'] = self.add('copy-to-macl', (before[n],), site=site, value=event['after']['macl'])
        if word & 0xF0FF == 0x402A:
            self.special['pr'] = self.add('copy-to-pr', (before[n],), site=site, value=event['after']['pr'])
        for mask, name in ((0x4026, 'pr'), (0x4016, 'macl'), (0x4017, 'gbr')):
            if word & 0xF0FF == mask:
                self.special[name] = self.add('memory-to-'+name, reads, site=site, value=event['after'][name])
        condition = None
        if word & 0xF00F in (0x3000, 0x3002, 0x3003, 0x3006, 0x3007, 0x2008, 0x2007):
            condition = (before[n], before[m])
        elif word >> 8 in (0x88, 0xC8):condition = (before[0],)
        elif word >> 8 == 0xCC:condition = tuple(reads)
        elif word & 0xF0FF in (0x4011, 0x4015, 0x4000, 0x4020, 0x4001, 0x4021):
            condition = (before[n],)
        elif word & 0xF0FF in (0x4024, 0x4025):condition = (before[n], old_special['sr'])
        elif word & 0xF00F in (0x3004, 0x300A, 0x300E):
            condition = (before[n], before[m], old_special['sr'])
        elif word == 0x0019:condition = ()
        if condition is not None:
            self.special['sr'] = self.add('condition-bits', condition, site=site,
                instruction=event['bytes'], before=event['before']['sr'], value=event['after']['sr'])
        for branch in event['branches']:
            if branch['kind'] in ('taken', 'fallthrough'):
                node = self.add('branch-premise', (self.special['sr'],), site=site,
                    instruction=event['bytes'], taken=branch['kind']=='taken',
                    target=branch['target'], delayed=branch['delay'],
                    sr=event['before']['sr'], T=event['before']['sr']&1)
                self.controls.append(node)
            elif branch['kind'] == 'call':
                self.special['pr'] = self.add('call-return-address', controls=(), site=site, value=site+4)
            elif branch['kind'] == 'return':
                self.pending_returns[site] = dict(target=branch['target'], pr=self.special['pr'])
        if event['delay_slot'] and event['site']-2 in call_entries:
            candidates = call_entries[event['site']-2]
            if not candidates:
                self.unknown.append(dict(site=site-2, reason='missing-ordered-call-entry'))
                return
            call = candidates.pop(0)
            entry = call['entry']
            self.add('post-delay-call', self.registers[:15], site=call['site'],
                target=call['target'], return_address=call['return_address'],
                delay_site=site, delay_instruction=event['bytes'],
                registers=list(entry['registers']), register_definitions=self.registers[:15],
                sp=entry['sp'], gbr=entry['gbr'], pr=entry['pr'], sr=entry['sr'],
                caller_saved_policy='Exact bounded callee instructions define all subsequent carriers; an outside call is unresolved.')
        if event['delay_slot'] and site-2 in self.pending_returns:
            returned = self.pending_returns.pop(site-2)
            node = self.add('natural-return', (self.registers[0], returned['pr']),
                site=site-2, delay_site=site, delay_instruction=event['bytes'],
                target=returned['target'], value=event['after']['registers'][0])
            self.outputs.append(node)

    def result(self):
        selected = [identity for identity in self.outputs if self.by_id[identity]['source_roots']]
        related = set()
        checkpoints = [row['id'] for row in self.nodes
            if row['operation'] == 'post-delay-call' and row['source_roots']]
        pending = [*self.roots, *selected, *checkpoints]
        while pending:
            identity = pending.pop()
            if identity in related:continue
            related.add(identity);row = self.by_id[identity]
            pending.extend((*row['data_inputs'], *row['address_inputs'], *row['control_inputs']))
        return dict(source_definitions=self.roots, outputs=selected,
            nodes=[row for row in self.nodes if row['id'] in related], unresolved_edges=self.unknown)


def _prepared(root, component, index):
    from importlib import import_module
    if component not in COMPONENTS:raise ValueError('the value-flow component has no bounded source adapter')
    contract, matrix = (import_module('kb.'+name) for name in COMPONENTS[component])
    declared = contract.descriptor(root);layout = repo.layout('7mfk', root)
    image = derive.image_bytes(layout, root);contract.require_image(declared, image)
    if component == 'closed_loop_coolant_paths':
        cases = matrix.cases(declared, image, root=root)
    else:cases = matrix.cases(declared, image)
    if type(index) is not int or not 0 <= index < len(cases):
        raise ValueError('the value-flow input case is outside its explicit bounded domain')
    case = cases[index]
    if component == 'closed_loop_coolant_paths':
        fixture, aliases = contract.fixture_for_case(declared, image, case)
    else:
        fixture, aliases = contract.independent_fixture(declared, image)
        declared = dict(declared, entry=[*declared['entry'], dict(start=contract.BOUNDARY['address'],
            end=contract.BOUNDARY['address']+8)])
    context = matrix.context(declared, case);memory = matrix.memory(case)
    frame = bytearray(b''.join((0xA3B4C5D6+item*17).to_bytes(4, 'big') for item in range(48)))
    for offset, value in ((160, context[19]), (164, context[7]), (184, CONTINUATION)):
        frame[offset:offset+4] = value.to_bytes(4, 'big')
    return contract, matrix, declared, layout, image, fixture, aliases, case, context, memory, bytes(frame)


def explain(root, component, index, datum, site, width, *, expected_analysis=None):
    """Analyze one declared software input; do not produce or publish evidence."""
    if (any(type(value) is not int for value in (datum, site, width))
            or not 0 <= datum <= sh2.MASK or not 0 <= site < sh2.MASK or site&1
            or width not in (1, 2, 4)):
        raise ValueError('the value-flow query requires an exact typed datum, instruction site and byte width')
    root = Path(root).resolve()
    contract, matrix, declared, layout, image, fixture, aliases, case, context, memory, frame = _prepared(root, component, index)
    sources = {path: sha((root/path).read_bytes()) for path in
        sorted(set(SOURCE_FILES) | set(proof_adapter.source_files(root, contract.DESCRIPTOR)))}
    body = derive.bodies('7mfk', root)
    functions = getattr(contract, 'FUNCTIONS', tuple(row['parent'] for row in getattr(contract, 'WINDOWS', ())))
    pairs = [asdict(row) for function in functions
        for row in derive.function_pairs(function, body.get(function, ()), image)]
    binding = dict(image_sha256=sha(image), fixture_sha256=sha(fixture),
        descriptor_sha256=sha((root/contract.DESCRIPTOR).read_bytes()),
        L0_analysis_sha256=derive._pair_digest('7mfk', root),
        ghidra_version=repo.ghidra_version(root), sources=sources,
        code=[dict(start=row['start'], end=row['end'], simulator_only=
            component == 'maf_record_paths' and row['start'] == contract.BOUNDARY['address'],
            stock_sha256=sha(image[row['start']:row['end']]),
            fixture_sha256=sha(fixture[row['start']:row['end']])) for row in declared['entry']],
        input_sha256=sha(json.dumps(_plain(case), sort_keys=True, separators=(',', ':')).encode()))
    analysis = sha(json.dumps(binding, sort_keys=True, separators=(',', ':')).encode())
    answer = dict(schema=1, kind='bounded-concrete-value-flow', component=component, case=index,
        request=dict(layout='7mfk', datum=datum, load_site=site, width_bytes=width),
        analysis_sha256=analysis, binding=binding, source_prepared=True, accepted=False,
        executable_evidence=False, causal_evidence=False, semantic_admission=False,
        premises=dict(case=_plain(case), context=list(context), RAM_sha256=sha(memory),
            frame_sha256=sha(frame), sp=STACK, continuation=CONTINUATION, sr_before=context[18],
            aliases=aliases, single_concrete_path=True, natural_caller_reachability=False),
        structural_candidates=pairs, structural_candidates_are_evidence=False)
    if expected_analysis is not None and expected_analysis != analysis:
        return dict(answer, status='unresolved', path=None,
            unresolved_edges=[dict(reason='stale-or-conflicting-analysis-binding')])
    source = state.RAM_BASE+(datum&65535) if 0xFFFF0000 <= datum <= sh2.MASK else datum
    definitions = Definitions(source, site, width)
    try:
        result = state.execute(declared, fixture, context, memory, frame, STACK,
            CONTINUATION, case['entry'], context[18], trace=True)
    except ValueError as error:
        return dict(answer, status='unresolved', path=None, unresolved_edges=[dict(
            reason='unsupported-bounded-instruction-state', detail=str(error),
            outside_call_clobbers=sorted(sh2.CALLER_SAVED))])
    call_entries = {}
    for row in result['calls']:call_entries.setdefault(row['site'], []).append(row)
    for event in result['trace']:definitions.instruction(event, call_entries)
    path = definitions.result()
    unresolved = list(path['unresolved_edges'])
    if not path['source_definitions']:unresolved.append(dict(reason='exact-datum-load-site-width-not-observed'))
    if not path['outputs']:unresolved.append(dict(reason='no-result-carrier-on-this-concrete-path'))
    if {path:sha((root/path).read_bytes()) for path in sources} != sources:
        raise ValueError('the value-flow analysis sources change during the bounded query')
    if derive._pair_digest('7mfk', root) != binding['L0_analysis_sha256']:
        raise ValueError('the value-flow L0/image analysis changes during the bounded query')
    return dict(answer, status='resolved-concrete-path' if not unresolved else 'partially-unresolved',
        path=path, unresolved_edges=unresolved,
        calls=_plain(result['calls']), branches=_plain(result['branches']),
        terminal=dict(registers=list(result['registers']), gbr=result['gbr'], sr=result['sr'],
            pr=result['pr'], sp=result['sp'], RAM_sha256=sha(result['ram']), frame_sha256=sha(result['frame'])))
