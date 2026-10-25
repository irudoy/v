# Packed-field transfer boundary

`packed-field-transfers.toml` binds retained width questions to exact stock
transfer sites. It distinguishes a declared byte field, the physical width of
an instruction, and the width of a diagnostic or telemetry publication.
Neither a word nor a longword copy establishes a wider semantic field.

The declaration preserves each native field owner, layout, declared width,
original width-claim digest and normalized code-source identity. Each transfer
names the exact source/destination bytes, load/store sites and data register.
The SH-2E sources under `tools/sh-elf-run/stock_*_packed_transfers.s` independently
reconstruct the bounded instructions and pools. Gaps contain no tested code.

The fuel-mask windows include the literal load of R10, the actual JSR and its
length-setting delay slot, the natural copy helper and the subsequent wider
field access. Their explicit bounded entry supplies R1/R2/R7. A post-call R10
assumption cannot replace execution of that callee. The helper's real lower
stack saves, return delay slot, GPR effects, T result and full RAM footprint
belong to the observation boundary.

`kb.packed_transfer_matrix` declares input patterns, individual container bits,
independent caller registers, flags, source-field bytes, neighboring bytes and
full RAM. `kb.packed_transfer_evidence` supplies separate instruction and state
equations, including word sign extension. Full actual GPR/SR/SP/PR, caller ABI,
seeded stack and RAM must agree with those equations. The copied first byte and
every neighboring byte remain distinct physical observations.

These declarations and equations grant no qualified width exception alone.
Admission requires the exact complete original GNU and TEST execution,
independent source/fixture bindings, each retained native width question and
its controlled refusals. Natural scheduler reachability, semantic storage
width, publication width and hardware behavior require their own evidence.

`tools/sh-elf-run/packed_transfer_capture.py` executes the windows inside the
same relocated-runtime phase of the full primary. Its C driver emits actual
raw contexts, complete observations and full RAM views; it supplies no semantic
expected-output columns. The raw captures occupy `packed_transfers` in the
existing COPY packet and create no separate producer or receipt.

`kb.packed_transfer_capture_evidence` independently binds exact native questions,
source snapshots, generated inputs, GNU reconstruction, RAM aliases, observation
boundaries, fixture/ELF identities, simulator streams and invocation order.
The existing TEST primary requires the same original complete successful
terminal before applying the independent input and full-state equations.

`kb.packed_width` accepts only the exact retained width question through that
live original proof. It supplies no symbol-identity grounding and changes no
declared width. The normal writer's batch-only `reconcile-width` operation
names the symbol, layout and original claim digest explicitly. It removes only
the matching source-bound unresolved review when the current qualified
compatibility contract holds. Missing or stale execution makes the raw width
question visible. Unregistered fields and other wider sites retain their
independent questions.
