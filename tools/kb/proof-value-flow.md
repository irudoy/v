# Bounded exact-datum paths

`kb flow` reports one concrete path through an existing bounded proof component.
The input case index, datum, load instruction and width are explicit:

```sh
uv run kb flow 7mfk:ffff106f --component closed_loop_coolant_paths \
  --case 14261 --site 7mfk:0005532c --width 1 --json
```

The query uses the current descriptor, owned stock image and declared input-only
matrix. `closed_loop_coolant_paths` and `maf_record_paths` use their existing
context, RAM, calibration, pointer-alias and fixture rules. The fixed analysis
stack and continuation are explicit software premises, separate from any
observed GNU stack address. One case answers one bounded path. It establishes
neither natural scheduling nor a property over all firmware states.

## Instruction and structural layers

The existing `byte_surface_equations.execute` has an optional `trace=True`
mode. Ordinary consumers retain its unchanged result shape with tracing off.
Trace events retain exact instruction bytes, complete register/special state
before and after each instruction, memory transfers, actual branch outcomes
and delayed control transfers. The query constructs SSA-like definitions from
those events using `sh2.decode`. Data, effective-address and branch-control
edges remain separate. Loads retain byte width and signed extension; later
explicit unsigned/signed transformations retain their own definitions.

Calls report the real target, return address, delay instruction and actual
post-delay register carriers of this concrete instruction path. Natural callee
instructions define the subsequent values and stores. A call outside the
declared executable closure remains unresolved with its caller-saved clobbers.
The query supplies no replacement numerical return. Unsupported register or
store transformations also remain explicit unresolved edges.

The existing `derive.function_pairs` control-flow resolver supplies a separate
set of L0/Ghidra structural candidates for the declared functions. Those
candidates preserve conservative joins and caller-saved clobbers. They do not
establish an exact-datum path or independent executable/causal evidence.

## Binding and result

The response binds the complete image, descriptor, controlled input fixture,
exact code spans, declared sources and current L0 analysis digest. A simulator
observing return is labelled separately from stock instructions. Case, context,
complete initial RAM/frame hashes, SR, SP, continuation and pointer aliases are
explicit premises. `--analysis <digest>` requires that complete current binding;
a stale or conflicting digest returns an unresolved result before instruction
analysis. Source and L0 bindings are checked again after analysis.

`path.nodes` contains exact definitions and their data/address/control inputs.
`source_definitions` names only loads matching datum, site and width together.
`outputs` identifies related stores and natural returns. Post-delay calls are
retained as explanatory checkpoints. Calls and branches also retain their full
ordered concrete records. Missing exact source loads or result carriers remain
explicitly unresolved. `resolved-concrete-path` describes analysis closure for
the stated inputs; `accepted`, `executable_evidence`, `causal_evidence` and
`semantic_admission` remain false.

The coolant reference follows `FFFF106F`, read at `0005532C`, through signed
offset and conditional coordinate handling to the real `00055392 -> 00026370`
call. The `EXTU.B` delay slot at `00055394` supplies the actual byte coordinate.
The helper's natural return feeds the lookup store at `0005539E`. Further
coefficient, limiter and publication transfers remain within the same exact
fixture. Independent domain numerical equations, actual GNU observations,
fixed-other causal alternatives and native/TEST/scopes guards retain their
existing acceptance responsibilities.

[`proof-reuse.md`](proof-reuse.md) describes saved flow consumption by
`kb proof-group`. Matching rejects stale source/L0 bindings, wrong datum/site/
width, conflicting definition edges and incompatible entries. Flow structure
cannot replace any independent domain or publication obligation.
