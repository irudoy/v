"""Lossless source-bound records of unresolved chain semantics.

An archived source statement provides provenance for an open question. It is
not arithmetic, executable evidence, a typed condition or a claim promotion.
"""

from functools import lru_cache
from copy import deepcopy
import hashlib
import json
import re
import subprocess
import tomllib

from kb import repo

COMMIT = re.compile(r'[0-9a-f]{40}')
SHA256 = re.compile(r'[0-9a-f]{64}')
CHAIN_PATH = re.compile(r'kb/chain/[a-z][a-z0-9_-]*\.toml')
KEYS = frozenset(('state','source_commit','source_path','source_sha256',
                  'order','step_sha256','original'))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def exact_step(step):
    """A deterministic encoding of every original field, including absence."""
    return json.dumps(step,ensure_ascii=True,sort_keys=True,separators=(',',':'))


def archive(step,source,commit,path,order):
    """Record a complete source step without inferring its semantics."""
    original=exact_step(step)
    return dict(state='unresolved',source_commit=commit,source_path=path,
                source_sha256=sha256(source),order=order,
                step_sha256=sha256(original.encode()),original=original)


def reference_binding(text, model, home):
    """A current or retained alias must resolve to one exact owned symbol."""
    from kb import refs
    from kb.model import MEANING_REF
    if not isinstance(text, str):
        return None
    full = refs.FULL.fullmatch(text)
    named = MEANING_REF.fullmatch(text)
    if not (full or named):
        return None
    match = full or named
    layout = full.group('layout') if full else home
    found = set()
    for symbol in model.symbols.values():
        if symbol.layout != layout or symbol.kind != match.group('kind'):
            continue
        if full and symbol.address != int(full.group('address'), 16):
            continue
        owner = symbol.meaning
        if owner is None:
            continue
        aliases = {owner.name, symbol.name, symbol.generated, *symbol.former}
        aliases.update(name for name, _, _ in owner.other_names)
        if match.group('name') in aliases:
            found.add(symbol.key)
    return next(iter(found)) if len(found) == 1 else None


def same_binding(expected, actual, model, home):
    """Only reference aliases may differ; order and all other fields remain exact."""
    if expected == actual:
        return True
    if model is None or set(expected) != set(actual):
        return False
    for key in expected:
        if expected[key] == actual[key]:
            continue
        if key not in ('from', 'to', 'via'):
            return False
        left = expected[key] if key == 'via' else [expected[key]]
        right = actual[key] if key == 'via' else [actual[key]]
        if not isinstance(left, list) or not isinstance(right, list) or len(left) != len(right):
            return False
        for old, new in zip(left, right):
            before = reference_binding(old, model, home)
            if before is None or before != reference_binding(new, model, home):
                return False
    return True


def validate(record,current,source,grammar,path,order,*,model=None,home='7mfk'):
    """Refuse lost fields, changed binding, unsupported resolution and sources."""
    if not isinstance(record,dict) or set(record)!=KEYS:
        return 'research needs exactly its declared source and original-step keys'
    if record['state']!='unresolved':
        return 'research state must remain unresolved; it provides no semantic proof'
    if not isinstance(record['source_commit'],str) or not COMMIT.fullmatch(record['source_commit']):
        return 'research source_commit must name one complete immutable commit'
    if record['source_path']!=path or not CHAIN_PATH.fullmatch(path):
        return 'research source_path must be the exact owning chain file'
    if type(record['order']) is not int or record['order']!=order or order<1:
        return 'research order must match the complete ordered step'
    for key in ('source_sha256','step_sha256'):
        if not isinstance(record[key],str) or not SHA256.fullmatch(record[key]):
            return f'research {key} must be one complete SHA-256'
    if not isinstance(record['original'],str):
        return 'research original must encode the complete original step'
    if sha256(source)!=record['source_sha256']:
        return 'research source bytes do not match the immutable source digest'
    if sha256(record['original'].encode())!=record['step_sha256']:
        return 'research original-step digest differs'
    try:
        original=json.loads(record['original'])
        historical=tomllib.loads(source.decode('utf-8'))['step'][order-1]
    except (ValueError,UnicodeDecodeError,KeyError,IndexError,TypeError) as error:
        return f'research original source is malformed: {error}'
    if not isinstance(original,dict) or exact_step(original)!=record['original']:
        return 'research original is not a canonical complete step'
    if original!=historical:
        return 'research does not preserve the exact historical source step'
    note=original.get('note')
    if not isinstance(note,str) or not grammar.validate(note):
        return 'research must retain an unresolved original prose note'
    if 'research' in original:
        return 'research archives cannot nest or restate an existing archive'
    expected={key:value for key,value in original.items() if key!='note'}
    actual={key:value for key,value in current.items() if key!='research'}
    if not same_binding(expected, actual, model, home):
        return 'research changes or loses original binding, order, conditions or metadata'
    return None


@lru_cache(maxsize=256)
def historical_source(root,commit,path):
    """Read a validated immutable Git source through the primary knowledge API."""
    if not COMMIT.fullmatch(commit) or not CHAIN_PATH.fullmatch(path):
        raise repo.KbError('invalid research historical source',code=3)
    result=subprocess.run(['git','show',f'{commit}:{path}'],cwd=root,capture_output=True)
    if result.returncode:
        raise repo.KbError(f'research source {commit}:{path} is unavailable',code=3)
    return result.stdout


def preservation(before,after):
    """Existing unresolved records cannot disappear or change in a batch."""
    failures=[]
    for key,entity in before.entities.items():
        if entity.kind!='chain':
            continue
        replacement=after.entities.get(key)
        for index,step in enumerate(entity.steps):
            held=step.get('research')
            if held is None:
                continue
            current=replacement.steps[index].get('research') if replacement and index<len(replacement.steps) else None
            if current!=held:
                failures.append(f'{entity.key} step {index+1}: an unresolved source record cannot be removed or changed')
                continue
            original_binding = step_binding(before, step, getattr(entity, 'props', {}).get('home', '7mfk'))
            replacement_binding = step_binding(after, replacement.steps[index],
                getattr(replacement, 'props', {}).get('home', '7mfk'))
            if original_binding is None or original_binding != replacement_binding:
                failures.append(f'{entity.key} step {index+1}: an unresolved source record cannot change its owned SymbolKey bindings')
    return failures


def step_binding(model, step, home):
    """Exact before/after symbol identities, including unchanged named references."""
    from kb.model import SymbolKey
    def binding(value):
        if isinstance(value, SymbolKey):
            return value if value in model.symbols else None
        return reference_binding(value, model, home)
    source, target = binding(step.get('from')), binding(step.get('to'))
    calls = tuple(binding(value) for value in step.get('via', ()))
    if source is None or target is None or any(value is None for value in calls):
        return None
    return source, target, calls


def restore(document):
    """The complete original document represented by unresolved records."""
    original = deepcopy(document)
    for index, step in enumerate(original.get('step', ())):
        if 'research' in step:
            try:
                original['step'][index] = json.loads(step['research']['original'])
            except (ValueError, TypeError, KeyError) as error:
                raise repo.KbError(f'cannot restore the original step {index+1}: {error}', code=3) from error
    return original


def transfer(document, source, grammar, commit, path):
    """Prepare lossless note transfer without changing any other source fact."""
    historical = tomllib.loads(source.decode('utf-8'))
    if restore(document) != historical:
        raise repo.KbError(f'{path}: current facts differ from the immutable transfer source', code=3)
    result = deepcopy(document)
    count = 0
    for order, step in enumerate(result.get('step', ()), 1):
        if 'research' in step:
            failure = validate(step['research'], step, source, grammar, path, order)
            if failure:
                raise repo.KbError(f'{path} step {order}: {failure}', code=3)
            continue
        note = step.get('note')
        if note is not None and not isinstance(note, str):
            raise repo.KbError(f'{path} step {order}: note must be a string', code=3)
        if note is None or grammar.validate(note) is None:
            continue
        step['research'] = archive(step, source, commit, path, order)
        del step['note']
        failure = validate(step['research'], step, source, grammar, path, order)
        if failure:
            raise repo.KbError(f'{path} step {order}: {failure}', code=3)
        count += 1
    if restore(result) != historical:
        raise repo.KbError(f'{path}: transfer loses original source facts', code=3)
    return result, count


def operations(model, commit, root=repo.ROOT):
    """One primary writer batch for all unresolved chain statements."""
    from kb import store
    from kb.arithmetic import Grammar

    if not COMMIT.fullmatch(commit):
        raise repo.KbError('transfer source must be a complete immutable commit', code=2)
    grammar = Grammar(model.config)
    ops, inventory = [], []
    for (kind, slug), entity in sorted(model.entities.items()):
        if kind != 'chain':
            continue
        path = store.path_of(kind, slug)
        document = store.load(root, path, model.overlay)
        source = historical_source(root, commit, path.as_posix())
        prepared, count = transfer(document, source, grammar, commit, path.as_posix())
        if count:
            ops.append({'cmd': 'set', 'ref': entity.key, 'keys': {'step': prepared['step']}})
            inventory.append({'path': path.as_posix(), 'statements': count,
                              'source_sha256': sha256(source)})
    return ops, inventory
