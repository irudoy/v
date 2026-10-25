"""Bounded exact-datum paths preserve concrete premises and unresolved edges."""

import pytest

from kb import byte_surface_equations as state, cli, mcp, repo, value_flow
from kb import closed_loop_coolant_access_contract as contract, closed_loop_coolant_matrix as matrix


@pytest.fixture(scope='module')
def coolant_flow():
    source = contract.descriptor(repo.ROOT);image = repo.images()['JK08A'].path.read_bytes()
    cases = matrix.cases(source, image, root=repo.ROOT)
    index = next(row['index'] for row in cases if row['kind'] == 'controlled'
        and row['load'] == row['rpm_select'] == 0 and row['coefficients'][0] == 64
        and row['previous_coolant'] == 240 and row['coolant_offset'] == 0xFF40)
    return value_flow.explain(repo.ROOT, 'closed_loop_coolant_paths', index, 0xFFFF106F, 0x5532C, 1)


def test_exact_source_reaches_actual_post_delay_curve_arguments_and_result(coolant_flow):
    result = coolant_flow
    assert result['status'] == 'resolved-concrete-path'
    assert result['accepted'] is result['causal_evidence'] is result['executable_evidence'] is False
    path = result['path'];nodes = {row['id']: row for row in path['nodes']}
    assert path['source_definitions'] and path['outputs']
    for identity in path['source_definitions']:
        row = nodes[identity]
        assert (row['site'], row['address'], row['width_bytes'], row['transform']) == (
            0x5532C, state.RAM_BASE+0x106F, 1, 'sign-extend-8')
    calls = [row for row in nodes.values() if row['operation'] == 'post-delay-call' and row['site'] == 0x55392]
    assert len(calls) == 1
    call = calls[0]
    assert (call['target'], call['return_address'], call['delay_site']) == (0x26370, 0x55396, 0x55394)
    assert call['registers'][4] == 0x12422 and 0 <= call['registers'][5] <= 255
    assert any(row['operation'] == 'extu' and row['site'] == call['delay_site'] for row in nodes.values())
    assert any(row['operation'] == 'branch-premise' for row in nodes.values())
    assert any(row['operation'] == 'memory-store' and row['site'] == 0x5539E for row in nodes.values())
    assert any(row['operation'] == 'natural-return' and row['target'] == 0x55396 for row in nodes.values())
    for row in nodes.values():
        assert set((*row['data_inputs'], *row['address_inputs'], *row['control_inputs'])) <= set(nodes)
    assert result['premises']['single_concrete_path'] is True
    assert result['binding']['image_sha256'] == contract.IMAGE_SHA256
    assert result['binding']['L0_analysis_sha256'] and result['analysis_sha256']


def test_trace_disabled_retains_the_complete_original_engine_result(coolant_flow):
    prepared = value_flow._prepared(repo.ROOT, 'closed_loop_coolant_paths', coolant_flow['case'])
    owner, inputs, source, layout, image, fixture, aliases, case, context, memory, frame = prepared
    args = (source, fixture, context, memory, frame, value_flow.STACK, value_flow.CONTINUATION,
        case['entry'], context[18])
    plain = state.execute(*args)
    traced = state.execute(*args, trace=True)
    events = traced.pop('trace')
    assert traced == plain and len(events) == plain['steps']
    assert events[0]['site'] == case['entry'] and events[-1]['next'] == value_flow.CONTINUATION
    for event in events:
        assert event['bytes'] == fixture[event['site']:event['site']+2].hex()


def test_conditional_clamp_paths_keep_distinct_concrete_premises():
    source = contract.descriptor(repo.ROOT);image = repo.images()['JK08A'].path.read_bytes()
    cases = matrix.cases(source, image, root=repo.ROOT)
    results = []
    for offset in (0x8000, 0x7FFF):
        index = next(row['index'] for row in cases if row['kind'] == 'controlled'
            and row['previous_coolant'] == 240 and row['coolant_offset'] == offset
            and row['coefficients'] == [64]*16)
        results.append(value_flow.explain(repo.ROOT, 'closed_loop_coolant_paths', index,
            0xFFFF106F, 0x5532C, 1))
    assert all(result['status'] == 'resolved-concrete-path' for result in results)
    assert results[0]['analysis_sha256'] != results[1]['analysis_sha256']
    branches = [{row['site']: row['kind'] for row in result['branches']} for result in results]
    assert any(branches[0][site] != branches[1][site] for site in branches[0].keys() & branches[1].keys())
    for result in results:
        assert result['premises']['single_concrete_path'] is True
        assert result['semantic_admission'] is result['causal_evidence'] is False


@pytest.mark.parametrize('datum,site,width', ((0xFFFF1350,0x5532C,1),
    (0xFFFF106F,0x5532A,1), (0xFFFF106F,0x5532C,2)))
def test_wrong_datum_site_or_width_cannot_supply_the_exact_path(coolant_flow, datum, site, width):
    result = value_flow.explain(repo.ROOT, 'closed_loop_coolant_paths', coolant_flow['case'], datum, site, width)
    assert result['status'] == 'partially-unresolved'
    assert not result['path']['source_definitions']
    assert any(row['reason'] == 'exact-datum-load-site-width-not-observed' for row in result['unresolved_edges'])


def test_stale_analysis_refuses_before_instruction_analysis(monkeypatch, coolant_flow):
    monkeypatch.setattr(state, 'execute', lambda *args, **kwargs: pytest.fail('stale analysis executes no instructions'))
    result = value_flow.explain(repo.ROOT, 'closed_loop_coolant_paths', coolant_flow['case'],
        0xFFFF106F, 0x5532C, 1, expected_analysis='0'*64)
    assert result['status'] == 'unresolved' and result['path'] is None
    assert result['unresolved_edges'] == [dict(reason='stale-or-conflicting-analysis-binding')]


def test_unsupported_closure_retains_explicit_unresolved_call_clobbers(monkeypatch, coolant_flow):
    def unavailable(*args, **kwargs):raise ValueError('outside declared callee closure')
    monkeypatch.setattr(state, 'execute', unavailable)
    result = value_flow.explain(repo.ROOT, 'closed_loop_coolant_paths', coolant_flow['case'], 0xFFFF106F, 0x5532C, 1)
    assert result['status'] == 'unresolved' and result['path'] is None
    assert result['unresolved_edges'][0]['outside_call_clobbers'] == list(range(8))
    assert result['semantic_admission'] is False


def test_cli_and_mcp_expose_the_same_bounded_read_only_request():
    parser = cli.build_parser()
    arguments = dict(ref='7mfk:ffff106f', component='closed_loop_coolant_paths',
        case=14261, site='7mfk:0005532c', width=1, json=True)
    argv = mcp.argv('flow', arguments, parser)
    args = parser.parse_args(argv)
    assert args.handler == cli.command_flow and args.component == arguments['component']
    assert args.width == 1 and args.case == 14261 and args.json is True
    tool = next(row for row in mcp.tools(parser) if row['name'] == 'kb_flow')
    assert set(tool['inputSchema']['required']) == {'ref','component','case','site','width'}
