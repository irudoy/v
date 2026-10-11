"""Test-local reuse of successful TOML parses, with separate returned objects.

Original readers select and read every source, including overlays. Original
compilers construct every model and original checks inspect every result.
The cache holds only immutable serialization of a parse of exact input text;
root and effective adapter order partition the source preparation.
"""

from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
import pickle
from types import SimpleNamespace
import tomllib
from weakref import WeakKeyDictionary

from kb import adapters, compile, repo, store, write


@dataclass
class _Source:
    text: str
    packed: bytes
    size: int
    owners: int = 0


class SourceParseCache:
    # Scoped references consume the same budget as their shared contents.
    REFERENCE_BYTES = 32

    def __init__(self, capacity=64 << 20):
        self.capacity = capacity
        self.entries = OrderedDict()
        self.sources = {}
        self.bytes = 0
        self.hits = self.misses = self.evictions = 0
        self.scope_entries = 0
        self.context = ContextVar('kb_test_source_context', default=None)
        self.orders = WeakKeyDictionary()

    @contextmanager
    def scope(self, root, order):
        path = Path(root)
        self.scope_entries += 1
        token = self.context.set((str(path.resolve()), tuple(order), path))
        try:
            yield
        finally:
            self.context.reset(token)

    def loads(self, text, *, parse_float=float):
        context = self.context.get()
        if context is None or parse_float is not float:
            return tomllib.loads(text, parse_float=parse_float)
        key = context[:2], text
        if key in self.entries:
            self.hits += 1
            source = self.entries[key]
            self.entries.move_to_end(key)
            return pickle.loads(source.packed)
        self.misses += 1
        document = tomllib.loads(text)
        packed = pickle.dumps(document, protocol=pickle.HIGHEST_PROTOCOL)
        size = len(text.encode('utf-8')) + len(packed)
        # Each new root/order still parses its own first request. Only exact
        # immutable text/serialization pairs share retained storage.
        content = (text, packed)
        if size + self.REFERENCE_BYTES <= self.capacity:
            while self.entries and self.bytes + self.REFERENCE_BYTES \
                    + (0 if content in self.sources else size) > self.capacity:
                _, removed = self.entries.popitem(last=False)
                self.bytes -= self.REFERENCE_BYTES
                removed.owners -= 1
                if removed.owners == 0:
                    del self.sources[removed.text, removed.packed]
                    self.bytes -= removed.size
                self.evictions += 1
            source = self.sources.get(content)
            if source is None:
                source = self.sources[content] = _Source(text, packed, size)
                self.bytes += size
            source.owners += 1
            self.entries[context[:2], source.text] = source
            self.bytes += self.REFERENCE_BYTES
        return document

    def stats(self):
        return dict(hits=self.hits, misses=self.misses, evictions=self.evictions,
                    entries=len(self.entries), bytes=self.bytes, capacity=self.capacity,
                    scope_entries=self.scope_entries)

    def install(self, monkeypatch):
        parser = SimpleNamespace(loads=self.loads, TOMLDecodeError=tomllib.TOMLDecodeError)
        for module in dict.fromkeys((compile, repo, store, *adapters.ORDER)):
            if getattr(module, 'tomllib', None) is tomllib:
                monkeypatch.setattr(module, 'tomllib', parser)

        original_build, original_issues = compile.build, write._issues

        @wraps(original_build)
        def build(*args, **kwargs):
            root = args[0] if args else kwargs.get('root', repo.ROOT)
            order = args[2] if len(args) > 2 else kwargs.get('order')
            effective_order = tuple(adapters.ADAPTERS if order is None else order)
            with self.scope(root, effective_order):
                model = original_build(*args, **kwargs)
            self.orders[model] = effective_order
            return model

        @wraps(original_issues)
        def issues(model):
            # Models constructed outside this fixture use a separate context.
            order = self.orders.get(model, ('outside-test-cache',))
            with self.scope(model.root, order):
                return original_issues(model)

        def rooted(original):
            @wraps(original)
            def read(root, *args, **kwargs):
                context = self.context.get()
                if context and context[2] == root:
                    return original(root, *args, **kwargs)
                order = context[1] if context and context[0] == str(Path(root).resolve()) \
                    else tuple(adapters.ADAPTERS)
                with self.scope(root, order):
                    return original(root, *args, **kwargs)
            return read

        monkeypatch.setattr(compile, 'build', build)
        monkeypatch.setattr(write, '_issues', issues)
        for name in ('load', 'canonical'):
            monkeypatch.setattr(store, name, rooted(getattr(store, name)))
        original_config = rooted(repo.config)

        @wraps(repo.config)
        def configuration(root=repo.ROOT, overlay=None):
            return original_config(root, overlay)

        monkeypatch.setattr(repo, 'config', configuration)
