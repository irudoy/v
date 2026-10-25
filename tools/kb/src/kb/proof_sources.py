"""Declared local proof-source closure without importing or executing its code.

Static Python imports, explicit local loader operands and C/assembly includes
extend the declared seeds. Unknown local edges remain obligations.
"""

import ast
import hashlib
from pathlib import Path
import re
import sys

SOURCE = 'tools/kb/src/kb/proof_sources.py'
PACKAGE_ROOTS = ('tools/kb/src', '.', 'tools/sh-elf-run')
FORBIDDEN_ROOTS = {'kb', 'l0', '.git', '.agents', '.codex'}
ROOT_FILES = {'pyproject.toml', 'uv.lock', 'Makefile'}
EXTERNAL_MODULES = {'neo4j', 'tomlkit', 'coolname', 'rapidfuzz', 'pytest'}
INCLUDE = re.compile(r'^\s*(?:#\s*include|\.include)\s+"([^"]+)"', re.MULTILINE)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value):
    if type(value) is not str:
        raise ValueError('a proof dependency requires an exact local source path')
    path = Path(value)
    if (not path.parts or path.is_absolute()
            or '..' in path.parts or path.parts[0] in FORBIDDEN_ROOTS
            or path.parts[0] not in {'tools', 'defs', 'patches', 'rom-images'}
                and path.as_posix() not in ROOT_FILES):
        raise ValueError('a proof dependency is outside its declared local source boundary')
    return path.as_posix()


def _module(root, name, parent):
    """Resolve only explicit project roots; never search environments or sys.path."""
    relative = Path(*name.split('.'))
    found = []
    bases = (parent, *(Path(value) for value in PACKAGE_ROOTS))
    for base in bases:
        for suffix in (relative.with_suffix('.py'), relative/'__init__.py'):
            path = (base/suffix).as_posix()
            try:safe_path(path)
            except ValueError:continue
            if (root/path).is_file() and path not in found:found.append(path)
    if found:
        # The source directory has ordinary Python import priority.
        local = [path for path in found if Path(path).parent == parent]
        if len(local) == 1:return local[0], None
        if len(found) == 1:return found[0], None
        return None, dict(reason='ambiguous-local-import', module=name, candidates=found)
    first = name.split('.')[0]
    if first in sys.stdlib_module_names or first in EXTERNAL_MODULES:
        return None, None
    # Namespace packages have no executable initializer. Their children resolve separately.
    for base in bases:
        path = (base/relative).as_posix()
        try:safe_path(path)
        except ValueError:continue
        if (root/path).is_dir():return None, None
    return None, dict(reason='missing-local-import', module=name)


def _python_edges(root, path, data):
    tree = ast.parse(data.decode(), filename=path)
    edges, unknown, generated = set(), [], set()
    parent = Path(path).parent
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):names = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = parent
                for step in range(node.level-1):base = base.parent
                name = (base/Path(*(node.module or '').split('.'))).as_posix().replace('/', '.')
                names = [name, *(name+'.'+item.name for item in node.names if item.name != '*')]
            else:
                names = [node.module] if node.module else []
                for item in node.names:
                    if item.name == '*':continue
                    # A from-import can name a Python object instead of a module.
                    full = (node.module+'.' if node.module else '')+item.name
                    resolved, error = _module(root, full, parent)
                    if resolved:names.append(full)
        for name in names:
            target, error = _module(root, name, parent)
            if target:edges.add(target)
            if error:unknown.append(dict(error, source=path, line=node.lineno))
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            value = node.value
            if (any(isinstance(target, ast.Name) and target.id == 'HEADER' for target in targets)
                    and isinstance(value, ast.Constant) and type(value.value) is str
                    and value.value.endswith('.h') and path.startswith('tools/sh-elf-run/')
                    and path.endswith('_capture.py')):
                generated.add((parent/value.value).as_posix())
            declarations = {'SOURCE_FILES', 'SOURCES', 'SOURCE', 'EXECUTION_FILES', 'EXECUTION_INPUTS', 'INPUT_SOURCE',
                'ASSEMBLY', 'HARNESS', 'OBSERVER', 'RETURN', 'DESCRIPTOR', 'NUMERIC',
                'PRECURSOR_NUMERIC', 'DTC_DECODER', 'DECODER', 'UNIT', 'UNITS'}
            if any(isinstance(target, ast.Name) and target.id in declarations for target in targets):
                if value is None:
                    unknown.append(dict(reason='declared-source-needs-initializer',source=path,line=node.lineno))
                    continue
                for item in ast.walk(value):
                    if (isinstance(item, ast.Constant) and type(item.value) is str
                            and (item.value.startswith(('tools/', 'defs/', 'patches/', 'rom-images/'))
                                or item.value in ROOT_FILES)
                            and (Path(item.value).suffix or Path(item.value).name in {'Dockerfile','Makefile'})):
                        edges.add(safe_path(item.value))
                    elif (isinstance(item, ast.Constant) and type(item.value) is str
                            and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_.-]*\.(?:py|c|h|s|inc)',item.value)):
                        options={(parent/item.value).as_posix(),'tools/sh-elf-run/'+item.value}
                        found=sorted(target for target in options if (root/target).is_file())
                        if len(found)==1:edges.add(safe_path(found[0]))
                        else:unknown.append(dict(reason='unresolved-declared-relative-source',source=path,
                            line=node.lineno,operand=item.value,candidates=found))
        if isinstance(node, ast.Call):
            name = node.func.attr if isinstance(node.func, ast.Attribute) else (
                node.func.id if isinstance(node.func, ast.Name) else '')
            if name not in {'tool', 'spec_from_file_location', 'import_module'}:continue
            position = 0 if name == 'import_module' else 1
            operand = node.args[position] if len(node.args) > position else None
            literals = [operand.value] if isinstance(operand, ast.Constant) and type(operand.value) is str else []
            resolved_operand = False
            for value in literals:
                if value.endswith('.py'):
                    choices = [(parent/value).as_posix(), 'tools/sh-elf-run/'+value]
                    if value.startswith(('tools/', 'patches/')):choices = [value]
                    found = list(dict.fromkeys(target for target in choices if (root/target).is_file()))
                    if len(found) == 1:edges.add(found[0]);resolved_operand = True
                    else:unknown.append(dict(reason='unresolved-declared-loader', source=path,
                        line=node.lineno, operand=value, candidates=found))
                elif name == 'import_module' and re.fullmatch(r'[a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*', value):
                    target, error = _module(root, value, parent)
                    if target:edges.add(target)
                    if error:unknown.append(dict(error, source=path, line=node.lineno))
                    resolved_operand = error is None
            if not resolved_operand and not literals:
                unknown.append(dict(reason='dynamic-loader-needs-declaration', source=path, line=node.lineno))
            elif not resolved_operand and not any(row.get('line')==node.lineno for row in unknown):
                unknown.append(dict(reason='unsupported-declared-loader-operand',source=path,
                    line=node.lineno,operand=literals))
    return edges, unknown, generated


def closure(root, seeds, *, declared_edges=None, generated_headers=()):
    """Return exact declared closure and unresolved edges, without loading modules."""
    root = Path(root).resolve()
    declared_edges = declared_edges or {}
    supplied = {safe_path(path): tuple(safe_path(item) for item in targets)
        for path, targets in declared_edges.items()}
    if any(not targets for targets in supplied.values()):
        raise ValueError('a dynamic proof loader requires a nonempty finite source declaration')
    pending = sorted({safe_path(path) for path in seeds} | {SOURCE,'tools/kb/pyproject.toml'} | ROOT_FILES)
    files, edges, unresolved = {}, {}, []
    private_headers = {safe_path(path) for path in generated_headers}
    include_pending = []
    while pending:
        path = pending.pop()
        if path in files:continue
        target = root/path
        if not target.is_file():
            unresolved.append(dict(reason='missing-declared-source', source=path));continue
        data = target.read_bytes();files[path] = sha(data);children = set(supplied.get(path, ()))
        if target.suffix == '.py':
            found, unknown, generated = _python_edges(root, path, data)
            children.update(found);private_headers.update(generated)
            # A finite explicit loader declaration resolves only this source's loader edge.
            unresolved.extend(row for row in unknown
                if row['reason'] != 'dynamic-loader-needs-declaration' or path not in supplied)
        elif target.suffix in {'.c', '.h', '.s', '.inc'}:
            for name in INCLUDE.findall(data.decode()):
                include_pending.append((path, safe_path((Path(path).parent/name).as_posix())))
        edges[path] = sorted(children)
        for child in children:
            safe_path(child)
            if child not in files:pending.append(child)
        if not pending and include_pending:
            for parent, child in include_pending:
                if child in private_headers and not (root/child).is_file():continue
                edges[parent] = sorted(set(edges[parent]) | {child})
                if child not in files:pending.append(child)
            include_pending = []
    for source, identity in files.items():
        if sha((root/source).read_bytes()) != identity:
            raise ValueError('a declared proof source changes during closure preparation')
    return dict(schema=1, files=dict(sorted(files.items())), edges=dict(sorted(edges.items())),
        generated_input_headers=sorted(private_headers), unresolved_edges=unresolved,
        complete_declared_closure=not unresolved, semantic_admission=False)


def require_manifest(value, inputs, *, anchors=None):
    """Reject a missing/stale declared dependency in the existing execution boundary."""
    if type(inputs) is not dict or not value['complete_declared_closure']:
        raise ValueError('the declared proof dependency closure is incomplete')
    for path, identity in value['files'].items():
        if inputs.get(path) != identity:
            raise ValueError('a declared proof dependency is missing or stale in execution inputs: '+path)
        if anchors is not None and path not in anchors:
            raise ValueError('a declared proof dependency is absent from acceptance anchors: '+path)
