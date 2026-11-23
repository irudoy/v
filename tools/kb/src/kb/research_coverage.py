"""A Markdown snapshot of ROM research coverage in the compiled KB."""

from collections import Counter, defaultdict

from kb import compile, repo


CONFIRMED = ('code', 'silicon')
STATES = ('confirmed', 'review', 'unrecorded', 'absent', 'excluded')


def report(root=repo.ROOT):
    return render(compile.cached(root))


def applicable(symbol, image):
    images = symbol.props.get('images')
    return not images or image in images


def state(meaning, layout, image):
    symbol = meaning.symbols.get(layout)
    if symbol is not None:
        if not applicable(symbol, image):
            return 'excluded'
        return 'confirmed' if symbol.value('level') in CONFIRMED else 'review'
    status = meaning.statuses.get(layout)
    if status is None:
        return 'unrecorded'
    return 'absent' if status.state == 'absent' else 'review'


def architecture_counts(model, layout, image):
    """Count anchored endpoints and fully bound chains on the exact image."""
    def bound(ref):
        meaning = model.meaning_of(ref)
        symbol = meaning.symbols.get(layout) if meaning is not None else None
        return symbol is not None and applicable(symbol, image)

    endpoints, chains = Counter(), 0
    for entity in model.entities.values():
        if layout not in entity.props.get('layouts', (layout,)):
            continue
        if entity.kind == 'endpoint':
            refs = (*entity.refs.get('registers', ()), *entity.refs.get('functions', ()))
            if any(map(bound, refs)):
                endpoints[entity.props['direction']] += 1
        if entity.kind == 'chain':
            refs = [*entity.refs['output']]
            for step in entity.steps:
                refs.extend((step['from'], step['to'], *step.get('via', ())))
            if all(map(bound, refs)):
                chains += 1
    return endpoints, chains


def table_row(cells):
    return '| ' + ' | '.join(str(cell).replace('|', '\\|') for cell in cells) + ' |'


def render(model):
    def order(entity):
        return entity.props.get('order', 0), entity.slug

    images = sorted((image, layout.id) for layout in model.layouts.values()
                    for image in layout.images)
    stages = sorted((item for item in model.entities.values() if item.kind == 'stage'), key=order)
    blocks = defaultdict(list)
    for block in model.entities.values():
        if block.kind == 'block':
            blocks[block.refs['stage'][0]].append(block)
    placements = defaultdict(list)
    for meaning in model.meanings:
        if block := meaning.props.get('block'):
            placements[block].append(meaning)

    matrix, totals = [], defaultdict(Counter)
    for stage in stages:
        for block in sorted(blocks['stage', stage.slug], key=order):
            cells = []
            for image, layout in images:
                counts = Counter(state(item, layout, image) for item in placements[block.key])
                totals[image].update(counts)
                cells.append(' / '.join(str(counts[key]) for key in STATES) if counts else '-')
            matrix.append(table_row([stage.props['title'], block.props['title'], *cells]))

    lines = [
        '### Coverage by image', '',
        '**Functions** shows image-applicable bindings at `code` or `silicon` level',
        "against the layout's function exports. **Endpoints** shows input / output /",
        'bidirectional endpoints with at least one bound anchor. **Chains** shows applicable',
        'chains with every step reference and the output bound on the image.', '',
        table_row(('Image', 'Layout', 'Functions', 'Endpoints', 'Chains',
                   'Confirmed', 'To verify', 'Unrecorded', 'Absent', 'Image-excluded')),
        table_row(['---'] * 10),
    ]
    for image, layout in images:
        functions = model.functions[layout]
        reviewed = sum(symbol.kind == 'fn' and symbol.address in functions
                       and applicable(symbol, image) and symbol.value('level') in CONFIRMED
                       for meaning in model.meanings if (symbol := meaning.symbols.get(layout)))
        endpoints, chains = architecture_counts(model, layout, image)
        endpoint_counts = ' / '.join(str(endpoints[key]) for key in ('input', 'output', 'bidirectional'))
        lines.append(table_row((image, f'`{layout}`', f'{reviewed} / {len(functions)}', endpoint_counts,
                                chains, *(totals[image][key] for key in STATES))))

    lines.extend([
        '', '<details>', '<summary>Coverage by subsystem</summary>', '',
        'Cells show **confirmed / to verify / unrecorded / absent / image-excluded**.',
        'Counts cover meanings assigned to a block. The inventory grows as new',
        'meanings are recorded. A dash marks a block with no assigned meanings.', '',
        '- **Confirmed** has an applicable binding at `code` or `silicon` level.',
        '- **To verify** has a lower-confidence binding or an unresolved search.',
        '- **Unrecorded** has neither a binding nor a status on the layout.',
        '- **Absent** has an explicit absence record.',
        '- **Image-excluded** has a layout binding restricted to other images.', '',
        table_row(['Stage', 'Block', *(image for image, _ in images)]),
        table_row(['---'] * (2 + len(images))),
        *matrix, '', '</details>', '',
    ])
    return '\n'.join(lines)
