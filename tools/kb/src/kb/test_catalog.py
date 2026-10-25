"""Explicit semantic profiles required by the common native TEST producer.

The complete-current-origin gate is mandatory. An incomplete component list
cannot qualify a smaller package or supply legacy unqualified TEST grounding.
"""

from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import weakref

from kb import test_cases, test_copy_facts, test_execution, test_image_scan, test_origins, test_registry
from kb import test_sid22_facts, test_stock_accumulator

COMPONENTS = (test_image_scan, test_stock_accumulator, test_copy_facts, test_sid22_facts)
PREPARATIONS = ContextVar('native_test_catalog_preparations', default=None)
PREPARATION_LIMIT = 4


@contextmanager
def preparing(root):
    """Retain immutable registration instructions within one primitive-output pass."""
    root = Path(root).resolve()
    previous = PREPARATIONS.get()
    if previous is not None and previous[0] == root:
        yield
        return
    token = PREPARATIONS.set((root, OrderedDict()))
    try:
        yield
    finally:
        PREPARATIONS.reset(token)


def prepared(model):
    """Reuse declarations, never a verdict, model, live context or proof result."""
    bound = PREPARATIONS.get()
    if bound is None or bound[0] != Path(model.root).resolve():
        return build(model)
    if (build is not STANDARD_BUILD or build.__code__ is not STANDARD_BUILD_CODE
            or COMPONENTS is not STANDARD_COMPONENTS
            or any(component.profile is not profile or component.adapter is not adapter
                   or component.profile.__code__ is not profile_code
                   or component.adapter.__code__ is not adapter_code
                   for component, profile, adapter, profile_code, adapter_code in STANDARD_METHODS)):
        return build(model)
    methods = tuple((id(component), id(component.profile), id(component.adapter))
                    for component in COMPONENTS)
    key = id(model), methods
    cache = bound[1]
    held = cache.get(key)
    if held is not None and held[0]() is model:
        cache.move_to_end(key)
        return held[1]
    engine = build(model)
    try:
        reference = weakref.ref(model)
    except TypeError:
        return engine
    cache[key] = reference, engine
    cache.move_to_end(key)
    while len(cache) > PREPARATION_LIMIT:
        cache.popitem(last=False)
    return engine


def build(model):
    origins = test_origins.index(model)
    profiles = tuple(component.profile(model, origins) for component in COMPONENTS)
    wanted = {case.nodeid for profile in profiles for case in profile.contract.cases}
    case_order = tuple(case.nodeid for case in test_cases.ordered() if case.nodeid in wanted)
    registry = test_registry.Registry(profiles, case_order=case_order)
    engine = test_execution.Engine(registry,
        tuple(component.adapter(model.root) for component in COMPONENTS),
        raw_declarations=capture_declarations())
    engine.require_coverage(model)
    return engine


def capture_declarations():
    """Additional raw views coexist with the existing full witness protocols."""
    return (test_stock_accumulator.capture_spec(),)


STANDARD_BUILD = build
STANDARD_BUILD_CODE = build.__code__
STANDARD_COMPONENTS = COMPONENTS
STANDARD_METHODS = tuple((component, component.profile, component.adapter,
                          component.profile.__code__, component.adapter.__code__)
                         for component in COMPONENTS)
