# GNU SH-ELF firmware instruction verification

This directory is the mandatory independent executable gate for every firmware
patch that changes instruction bytes. It uses the GNU SH-2E assembler, linker,
and instruction-set simulator in a pinned Debian container rather than Ghidra
p-code.

The default gate is fully repository-contained. Verification of the separate
npkern project is optional, external, and revision-locked.

## Bounded adapter sources

The coolant and MAF record raw adapters use the input-only descriptor generator
in `generate_proof_adapters.py`. Its generated C drivers retain the existing
80/572 observer, complete frames/RAM/CPU state and exact fixture lifecycle.
`make check` compares generated sources. Both independent domain consumers also
require the complete declared source dependency graph in their actual execution
input map, including imported numerical helpers. Private generated headers retain
their exact producer/consumer byte checks. Numerical equations, physical/call
interpretation, causal alternatives and native/TEST/scopes guards remain separate.

`tools/kb/proof-adapters.md`, `proof-value-flow.md` and `proof-reuse.md` describe
generation, the bounded read-only value path and exact group preparation. These
source and structural reports retain the shared executable acceptance boundary.

## Primary container lifecycle

`run.sh` uses the local `default` Docker context through `docker_lifecycle.py`.
The host bookkeeping uses Python 3's standard library and a POSIX file lock.
The host lock, persistent owner, attempt records and CID files live under
`tmp/local-results/sh-elf-run/`. The container has a unique attempt label, a stable
owner name and the checkout label, and mounts the checkout read-only at
`/workspace`. Both registered witness input manifests include the lifecycle
source.

`tmp/local-results` may be a symbolic link to a physical directory on another
disk. A root-level `local-results` directory or link is not required. The runner
exposes that linked directory read-only at its absolute host path inside the container, so links from
`/workspace` remain reachable. Process and stream names in qualified records
remain checkout-relative. A missing results target or a nested link escaping
that target refuses execution; the rest of the checkout keeps its existing
storage boundary.

Before building and before creating a container, the runner reads actual Docker
state. A running matching child refuses a repeat with `kind=live`; an unavailable,
incomplete or ambiguous state refuses it with `kind=unknown`. Matching also
includes an old unlabeled container with the same checkout mounted at
`/workspace`, so loss of the client before CID publication or deletion of a local
owner record cannot hide that child. A host lock serializes primary runs of one
checkout. Containers of other checkouts are retained.

The configured image is resolved to its immutable Docker image ID after build.
The container starts that ID with `--pull=never`; an absent or ambiguous image
identity refuses execution. The original stream's `VQ_SH_ELF_CONTAINER` record
binds the image, exact attempt/CID, checkout, arguments, client exit and observed
absent/stopped state. It includes no container environment variables.

The normal terminal binds the original client exit and the exact CID to confirmed
`absent` or `stopped` state. A zero exit without a valid identity or with a live
child refuses lifecycle completion. Interrupted attempts retain their last
record; TERM or SIGKILL can leave a Docker child running. The next primary start
detects it before another gate executes. Inspect the reported exact identity in
the same context and resolve its state before retrying. Removing a record does
not resolve a running container. The runner performs no broad container cleanup.

Lifecycle completion is distinct from GNU instruction/observation acceptance.
Original failed or interrupted process terminals remain unsuccessful; their
logs cannot supply a qualified witness. A repeat needs its own complete terminal
and independent finalization under the evidence contract.

## Shared required gate and qualification

`make verify-firmware` runs `qualified_gate.py`. It records one bounded original
`run.sh --can-copy-witness --sid22-witness` child and its exact stdout/stderr,
checks the complete stage order and runtime binding, and executes the registered
Python TEST witness once. Each independent CAN, SID22 and TEST validator runs in
its own bounded `uv run python -m kb.prepare_evidence` process. Native models and
caches retain their validator-process ownership; the coordinator holds records
and source maps rather than shared compiled models. No GC or sleep policy changes.

The job directory under `tmp/local-results/sh-elf-run/qualification-*` retains
started/terminal records, live streams, source inputs, runtime identity, prepared
record hashes and prior receipt bytes. Missing, failing, timed-out or interrupted
children do not qualify. An outer zero exit, a feedback subset, or successful
timing pairs cannot replace the exact original successful GNU terminal. Prepared
outputs require their independent original terminal and exact hash marker.

All records validate before native publication. The native source lock, exact
source comparisons and prior-receipt CAS fence publication and readback. Each
receipt replacement is atomic; a per-file I/O failure can leave independently
validated replacements, which the job journals without claiming a complete pass.
Prior bytes remain archived. A source change during publication also prevents a
completed gate. Jobs serialize without removing another job's lock or container.

The explicit `--native-test-profiles --native-publication-batch <batch>` mode
prepares CAN and SID22 records from the same original GNU child, runs the full
registered native TEST cohort against those prepared records, and independently
prepares TEST before changing native metadata. All three records name the same
original native snapshot. The ordinary writer consumes sealed prepared bytes
through its validators while the prior receipt files remain intact. Its
metadata-only mode admits registered reader/writer proof appends, exact
`reconcile-width` operations and the complete registered four-claim
`reconcile-diagnostic-output` transition. The latter requires independent
ROM-to-RAM execution, complete exhaust RAM continuity and SID22 source proof
from the same original process. It permits only the exact reader replacements,
absent per-layout geometry and the registered alias-note phrase replacement.
It withdraws only the exact legacy ledger selectors of those physical readers;
the conditional dependencies remain native facts. Every other ledger value and
evidence index retains its complete value and order.
Every original TEST context, status, executable binding and other semantic
property remains fixed. The job archives
native preimages, their hashes and the writer diff. Its source fence changes
only to the exact existing input files and bytes returned by that writer;
unrequested native or executable changes refuse final receipt publication.
The complete original producer provenance remains in each prepared record.

The registered `reconcile-timing-argument` transition replaces the exact
`0000C50E`, `00011F02`, `00011EFA` and `000147CA` physical-reader
assertions with conditional value arguments of the natural timing
compositor and explicit accumulator tail. It consumes the caller's
complete observation, bounded tail and direct division contract from the same
original primary. R1 is bound to the callee-entry state after the real delay slot;
independent table changes must alter the dividend and bounded output.
Every other native value and original ledger selector remains fixed. The
existing COPY and SID22 scope digests must remain equal across these exact
replacements; this transition adds no scope normalization or receipt.

The registered `reconcile-calculation-dependency` batch binds the remaining
exact arithmetic arguments, arithmetic outputs, conditional publication,
comparison output and owning dimensionless factor to their independent
same-primary components. Complete physical inputs, raw state, separate
equations, actual post-delay operands and positive value/output variation
remain required. The writer retains every other native property, ledger
selector, evidence position and TEST context. Existing physical scopes stay
equal without an additional normalization rule. AAFA alone retains its exact
owned `ratio`, `x/10`, `x*10`, `code` scale proof; other dependencies grant
identity only. No new producer, receipt, scheduling or hardware admission
follows from these transitions.

The one exact FFFF4524 argument disposition reuses
`closed_loop_coordinate_paths`. The caller's read0003EE72 and delay
slot0003EE7C bind R6 at real call0003EE7A to natural conditioner0003EF74.
Independent complete-input alternatives vary only that sample word and
must change the actual output pair. The pinned reverse-only original is
replaced by its owning arithmetic-argument dependency through the existing
calculation batch. Every other native relation, unset semantic type,
ledger and TEST context remains exact. The same raw component retains
its existing observer, native workspace and complete physical consumers.

The shared primary also captures `jk08a-io-access-paths` through four
bounded stock windows. The harness observes three exact native flat
storage banks separately from relocated RAM, plus complete frame,
register, SR, ABI and descriptor state. The monitor word window takes its
R4 and GBR from the actual descriptor-prefix exit and preserves complete
memory continuity. Independent state and numeric consumers bind the
DC40 mailbox writes, F430 uint32 read and packed operand, and F754
selected pointer/mask read. Four separately assembled observing returns
leave stock instruction bytes intact. `reconcile-io-access` admits only
the exact three existing-owner metadata transitions documented in
`defs/JK08A.io-accesses.md`. The proof grants no peripheral behavior,
natural scheduling, configured-disabled monitor reachability, units,
scale or hardware qualification.

`jk08a-maf-copy-filter-paths` retains the existing stock copy/filter
assembly, natural returns and the shared complete observer ABI. It adds
raw bank/word/mode/coefficient observations consumed independently of the
conventional MAF harness verdict. Exact instruction-state and separate
copy/filter/anti-stall equations bind the four existing bank-1 access
claims, preserve sibling and neighbor RAM, and require positive value
alternatives with other inputs fixed. `defs/JK08A.maf-copy-filter.md`
defines the source and exact grouped-owner publication boundary. The
transition uses ordinary `link` operations and the existing shared receipt.

`jk08a-maf-extended-paths` reuses the compensation, contribution and
scaling assembly units plus bank-publication and diagnostic-copy units
with their natural returns and callees. A sixth assembly unit binds two
bounded dual-bank caller windows with explicit incoming registers and
separately assembled SP+24 observing returns outside tested stock spans.
Complete state and separate integer equations bind 26 accesses, the exact
interior helper entry at 000224FA, real post-delay call arguments and
fixed-other input/output alternatives. `defs/JK08A.maf-extended.md`
defines this source and its joint 34-access batch with copy/filter,
the bounded two-curve lookup and existing record-member readers.
The complete natural battery publisher00039A9E uses the same scaling
assembly and real guard/scaler, three additional exact RAM pointer aliases
and its natural return. Separate word/byte-wrap/guard/scale/cap equations,
ordered physical transfers, post-delay R4/R5 and helper/caller returns
bind its one coefficient-reader claim. Both guard and final byte-cap
outcomes belong to the explicit battery input domain. Coefficient-only
alternatives must change the actual output byte with complete other input
state fixed. Native unsigned16, TEST, ledger and both coefficient-owner
appends remain exact; no physical voltage scale or live bypass state follows.
`jk08a-maf-transfer-paths` reuses the existing
MAF transfer assembly at0003A922..0003A94C with the real implicit word
wrapper and interpolation helpers, explicit ADC16/R14 premises and a
separate SP+24/R7 observing return outside tested bytes. Both exact curve
roots require fixed-other positive alternatives. Full state and separate
word/register equations preserve upper-clamp sign extension. The native
batch removes only two unsupported reader0003B27E relations and appends
evidence to the already-existing reader0003A904 relations. No universal
absence-of-read, complete coordinator or correction publisher is admitted.
Shared owners retain one complete postimage. The existing writer requires
all reserved owning items together and preserves TEST origins, semantic
types and existing physical namespaces.

`jk08a-maf-record-paths` binds natural predicate00025E20 and bounded
coordinator0003C3C6..0003C3DA to exact stock bytes and the unchanged80/572
observer. Byte1 atFFFF5A94 belongs to the existing three-byte FFFF5A93
record0129. Explicit R4 low-word index, sentinelFFFF and incoming caller
GBR premises remain separate inputs. The consumer binds the real call,
natural return, conditional byte RMW, both branch outcomes and a separately
assembled outside return. Full state and separate scalar equations retain
siblings, all RAM, status bits0..6 and fixed-other positive alternatives.
The shared owner postimage preserves unset semantic types, ledger, eleven
symbol evidence items and other three relations. No record producer,
RPM contributor, complete coordinator, new geometry or hardware behavior
is admitted. `defs/JK08A.maf-extended.md` defines this component.

`jk08a-closed-loop-admission-paths` reuses the unchanged complete adjustment
assembly for two bounded raw-mask windows, with separate executable spans
around the literal gap at000A101C..000A102C. Explicit GBR/register premises
and independent mask bytes feed the existing complete80/572 observer.
One base alias and two independently assembled outside SP+24/R7 returns
preserve every tested stock instruction. Separate full-state, bit, exact
physical, branch and fixed-other positive consumers bind four unsigned-byte
bank-2 writers while retaining both bank outputs and all other RAM.
Four exact ordinary owning appends share the complete original COPY primary
and preserve native readers, types, TEST positions and physical scopes.
The full legacy adjustment matrix and harness remain unchanged.
`defs/JK08A.closed-loop-admission-accesses.md` defines the boundary without
full coordinator, integrator, physical permission or hardware admission.

`jk08a-closed-loop-coordinate-paths` binds the bounded real3EE7A call to
the complete natural conditioner and five existing helpers. The stock
native GBR word8560 remains unchanged. A narrowly guarded20-byte native
workspace, complete256-byte native snapshots, unchanged canaries and
separate raw RAM reuse the existing observation protocol and80/572 observer.
Only those20 bytes overlay logical RAM. The existing4338 literal inputs
retain their first16 input columns; expected outputs are not consumed.
Separate scalar/full-state/physical/post-delay/branch/return/positive
consumers bind six exact owning relations and preserve unset native types,
all original TEST/evidence positions and existing physical scopes.
`defs/JK08A.closed-loop-coordinate-accesses.md` defines the complete boundary.

`jk08a-closed-loop-feedback-paths` reuses the whole 5CBEC closure and its
3067 instructions/63998 bound bytes, 43 long/17 word aliases, 76-byte input
context, 892-byte result and 352-byte frame observer. The 302-byte shared
workspace and 64 native canary bytes retain the existing translation; ordinary
RAM stays separate. Only the first three input columns and byte changes of
the 1829 legacy contexts feed the raw driver. Three source arguments and two
active-state stores require exact physical carriers, full signed post-delay
registers, the partial fifth byte/full fifth word, sixth pointer, natural
return, independent whole state/memory/frame/terminal and fixed-other effects.
The unsigned transition-counter reader/writer at FFFF88BA uses the actual
transition phase and real 5D66C/5CA8C packet/callee sequence, exact delay
store, pointer carriers, returns and original TEST/spec positions. Separate
counter/flag, threshold and inclusive-band equations remain mandatory.
All 27 active-state/transition conditional sites require both outcomes.
The separate 5CB84 saturation guard requires taken under the preceding
byte-product bound and rejects entry into its excluded saturation span.
Controlled 18-byte
ascending/descending/threshold profiles grant no stock reachability claim.
The existing coordinate/publication family has twelve owning appends with
ten retained full references; the calculation registry has 38 dispositions
with all 37 identities pinned.
`defs/JK08A.closed-loop-feedback-accesses.md` defines the complete boundary.

`jk08a-closed-loop-coolant-paths` reuses the complete natural5525A assembly
and existing numerical/frame/terminal equations with the same80/572 observer.
The source binds322 stock instructions/770 bound bytes, seven long pointer
aliases,42 controlled calibration bytes, complete64KiB RAM and14261 legacy
input rows. Only17 scalar inputs and five calibration arrays feed the driver.
The selected coefficient index/address/byte and signed offset have exact
physical transfers, real calls/delay slots/returns and fixed-other derived-word
positives. All25 feasible conditional sites require both outcomes; the byte-only
26A9A guard retains its bounded taken premise. Twelve owning appends retain
all ten prior references,37 calculations and original reader/type/TEST/spec
contexts. One normal binding reuses the ordinary registry with no
new mode, dispatcher or memory domain.
`defs/JK08A.closed-loop-coolant-accesses.md` defines this boundary.

`jk08a-exhaust-cvtc-transition-paths` reconstructs natural bank2 roots
`000C1DEC`/`000C2040` and the real byte-curve/fractional-division/unsigned-
quotient/remainder closure. Explicit bank-index and nonzero battery inputs,
complete raw RAM/CPU/ABI/frame/calibration/bound-code observations and
separate transition/product/curve/duty equations bind eleven exact RAM
relations. Ordered physical operands, actual post-delay calls, natural RTS
paths, feasible branch outcomes and fixed-other actual-output variation are
mandatory. The standard input-only driver retains the existing 80/572
observer. Exact ordinary appends preserve six complete native owners, TEST,
types, ledger and physical scopes. The source grants no sensor, scheduler,
units, scale or hardware claim. `defs/JK08A.exhaust-cvtc-accesses.md` defines
the complete domain and refusal boundary.
The registry contains 42 families and 88 captures.

The `scalar-ram-leaf-withdrawal` registration binds 136 exact original access
relations through complete natural arithmetic, state, indexed, interpolation,
division, producer and caller paths. Thirty-five independent components require
one complete original COPY primary. There are 125 readers and eleven individually
pinned writers. Complete actual instruction CPU/SR/frame/RAM, separate equations,
ordered physical operands, post-delay calls and natural returns remain mandatory.
Fixed-other alternatives require changed actual R0 or common computed publication
bytes outside controlled inputs. Every previous full family/helper/native/TEST
original remains mandatory from the identical primary.

The 136 normal unlinks and 128 matching ledger selectors preserve 101 full datum
owners and 76 complete functions. The selector total contains 120 datum-end and
8 function-end removals. Five complete function transitions retain eight exact
function-end selectors. Full preceding reference, function and source boundaries
retain complete prefix reconstruction and separate current full-image pins.
The map-bias caller changes only three proposed-image fields in four preceding
records of its shared table owner. Its exact inverse restores their complete
preceding images before the earlier prefix consumers run. Every other native,
type, TEST, ledger and scope fact remains bound. The gated assembly retains its
bounded two-site spelling exception and complete current/legacy hashes.
No owning replacement or reverse donation is created.
The complete byte-ratio producer additionally retains variable unsigned
word/large and short/long division, the ratio65536 split, real signed shift10,
its exact actual saved post-DIV1 R1 carrier and full known frame overwrite.
The complete118-record/62-function prefix retains exact reconstruction and its bounded current shared-owner transitions.
The complete state-surface caller retains three raw state modes, the real
four-byte local carrier, full four-row surface and implicit-byte helpers.
Only the additional exact row99 reader/owner-selector delta changes one
preceding current postimage; all119 core records and63 functions remain exact.
The complete byte-factor caller retains unsigned/signed word promotion,
two real byte-curve calls,distinct partial products and percentage delay-slot
publication. Its exact reverse writer adds one complete function transition;
all121 preceding full records/current images and64 functions remain exact.
The complete byte-sum caller retains the clipped raw coordinate,real byte
curve,unsigned minimum,separate three-byte sum and two full-word saturations.
Its exact reverse writer adds one full function transition and retains the
new owner's absent ledger;all122 prior full records/current images and65
functions remain exact.
The narrow caller and helper specifications define these boundaries.


The `register-only-withdrawal` family binds twelve exact unsupported readers
to six complete natural helper entries through `register_only_helper_paths`.
Separate full-register/scalar/stack/ordered-physical/branch/RTS-delay consumers
require executable absence of datum access and fixed-other actual R0 changes.
Its withdrawal-only policy admits exactly twelve normal `unlink` operations
and fourteen matching ledger-selector removals across eleven complete native
owners, with original TEST/type/context/scope preservation. It creates no
replacement relation or evidence and grants no identity, scale, units, caller
semantics or hardware admission. The existing observer, COPY primary, normal
writer and standard source generator are reused.
`defs/JK08A.register-only-helpers.md` defines this exact boundary.


The same CVTC capture also binds the conditional FFFF143A result of real26474.
Independent returned R0/extended R6/actual byte-store checks and fixed-other
coordinate/controlled-curve positives supply a distinct output guard. The
existing calculation-dependency batch preserves the complete native owner,
types, TEST, other ledger selectors and physical namespaces. Fixture, matrix,
observer, producer and generated driver remain exact.
`defs/JK08A.cvtc-gain-output.md` defines this result boundary.

`jk08a-rpm-inhibit-paths` binds the eight-byte real caller sequence at0004EDBE,
both MOV/OR delay slots, the unchanged vehicle-speed/main RPM state-machine
assembly and separate MAF-summary/shared-status/composite-status windows
at0004EDD2/0004EDF8/0004EDEA.
Their OR R0/R14 and OR R2/R14 delay states use distinct complete incoming words.
Fifteen pointer aliases and four separate outside SP+24/R7 returns reuse
the existing complete80/572 observer and64KiB RAM domain. Explicit full caller
state and27 calibration bytes feed independent instruction-state, scalar,
ordered physical, post-delay call, branch, return and fixed-other positive
consumers. All33 conditional branch sites require both outcomes. Four exact
one-sided sites bind the real minus-one diagnostic sentinel calls and byte
curve route, without stock seed lifecycle reachability. The existing curve
assembly and numeric consumer are reused with natural returns and MACL
save/restore. Fourteen exact ordinary owning appends preserve full native documents, unset
semantic types, TEST origins and existing physical scopes. The conditioned
status read requires an explicit controlled configuration bit7; sharedbit1 is
an explicit controlled input without stock lifecycle reachability. Both summary
leaves preserve complete RAM and return through their natural RTS delay slots.
`defs/JK08A.rpm-inhibit-accesses.md` defines the boundary without full
coordinator, stock conditioned-branch reachability, scale or hardware admission.

`jk08a-rpm-remaining-inhibit-paths` observes five conditional reader relations
in a separate exact fixture with entries0004EDC6/0004EDE4/0004EE00. Stationary,
thermal, sustained and CAN ceiling leaves execute with their real byte16
helper, post-delay inputs, natural returns and separate outside observers.
The thermal consumer requires FFFF4184=C0 and unsigned FFFF571E>=40; the
0007D8B8 dispatch is excluded only under those exact premises. Independent
state, scalar, physical, call/return, branch and fixed-other output consumers
are mandatory. The existing80/572 observer and192-byte frames remain exact;
the old nine full reference records and fixture retain their complete pins.
`defs/JK08A.rpm-remaining-inhibit.md` defines the conditional boundary without
diagnostic-producer, complete-coordinator, scale or hardware admission.

The ordinary access captures are registered once in
`tools/kb/src/kb/ordinary_access_registry.py`. The existing stock verifier derives
their execution order, duplicate-key guard and original candidate attachment
from those entries; their independent domain consumers remain mandatory.
Controlled pipeline tests derive per-component execution, exact candidate
identity and failure coverage from the same source. The registration and
coherent source-group contract is in `tools/kb/ordinary-access.md`.

`jk08a-phase-normalization-paths` reuses the exact natural APC normalizer and splitter
from the existing injection-tooth assembly, its real RTS delay slots and
the existing independent scalar equations. Two explicit native word/byte
pointer pairs feed the shared complete observer. Actual raw state, physical
reads/stores, phase/word/byte boundaries and positive alternatives bind ten
normalizer/splitter owning relations. `jk08a-phase-programmer-paths`
binds the existing offset multiply and real helper through actual
post-delay arguments with explicit post-guard period/remainder inputs.
Its separate observing return uses the existing SP+24/R7 source outside
tested bytes; the complete programmer, count guard and following MMIO
remain separate. Both components share the original complete COPY primary
and jointly bind twelve owning relations in six complete native owners.
No separate receipt, observer, numeric framework or natural scheduling
inference is introduced. The source and native
publication boundary are in `defs/JK08A.phase-normalization.md`.

`jk08a-bank-pulse-paths` reuses the complete natural base-pulse body and
its three declared pointer aliases. The shared complete observer and an
input-only legacy matrix retain every RAM, register, frame, ABI and literal
input. Separate state, scalar and physical consumers require both LTFT
sites, the precursor bypass, low32 arithmetic, all conditional outcomes
and positive fixed-other reader alternatives. The base component contributes
six original relations to the complete owning publication batch.
`defs/JK08A.bank-pulse-transfers.md` states the software-only boundary.

`jk08a-bank-pulse-stages` adds the complete existing precursor and channel
units with their real division, fixed-point, shift and affine helpers.
Input-only literal prefixes and explicit bounded alternatives feed the
same observer. Separate full-state, scalar, physical and post-delay-call
consumers bind the bank1 multiplier, actual loop delay-slot publication
and channel1 result. The owning family requires both raw components and
one exact nine-link batch preserving eight complete native documents.
The channel result retains unset semantic width and signedness. Existing
full legacy regions and their matrices retain their declared contracts.

`jk08a-knock-accesses` captures four separate existing stock units:
normalization, metric, threshold and comparison. Adjacent fragment
boundaries use separate fixtures and the existing SP+24/R7 observing
return outside tested instructions. The common complete observer and
input-only literal prefixes retain full explicit state and calibration
premises. Independent state/scalar/physical/post-delay-call/branch/positive
consumers support one exact eight-link batch in seven complete native
documents. No helper stub, observer ABI or receipt is added. The existing
full legacy regions and matrices retain their contracts. The source and
native boundary are in `defs/JK08A.knock-accesses.md`.

`jk08a-learning-transfer-paths` reuses the complete grid-selection and
grid-learning and LTFT publication assembly units and observes natural entries 0005796C,
00057D1E, 000580E8 and 00057B26 with the common complete observer. The raw driver
records input-only legacy columns, explicit bank/cell premises and
single-value RAM/calibration alternatives. Independent full-state,
scalar, physical and post-delay call consumers bind 21 owning relations.
No stock-function stub, observing return, observer ABI or receipt is added.
The source and exact native boundary are in `defs/JK08A.learning-transfers.md`.

`jk08a-ram-initialization-paths` observes five exact stock longword clear
paths with the existing complete observer. Exact ROM-range descriptors and
independent instruction/state and whole-range equations cover the 43 owning
writer relations. The final store preserves its full width above each
unaligned exclusive limit. The fixture documents its six pointer aliases
and four observation returns outside the tested instructions. Natural26F30
retains its stock RTS/NOP, complete frame and ordered pointer/limit reloads.
Its fixed nonempty range includes FFFF5B2C; no boot/reset reachability follows.
Its finite state
budget derives from the stock range lengths and exact loop bodies, with no
change to other families. `defs/JK08A.ram-initialization.md` describes the
bounded incoming contexts, complete native publication and refusal boundary.

`jk08a-counter-array-paths` shares the bounded-memory C driver and complete
observer with RAM initialization. Separate stream identities and explicit
input macros retain initialization's byte seeds while supplying declared
word-array patterns to the counter windows. Exact physical read/repeated-read/store
sequences and independent unsigned saturation equations cover nine original
writer claims. The complete intermediate word array remains part of the
first window's state continuity. The common finite instruction bound is
unchanged. `defs/JK08A.counter-arrays.md` describes the native publication,
preserved unknown types and absence of cadence or interrupt-entry inference.

The third bounded window2093E..20962 binds the holdoff byte atFFFF25FF,
offset four in the exact seven-byte array. Isolated input-byte alternatives
retain every other RAM/context/calibration input and require the actual
saturating output. All eight earlier full reference records, old eighteen
counter inputs and word patterns remain exact. The holdoff L0/TEST positions,
via/note and complete native/scopes guards remain mandatory; the bounded
entry grants no producer-call reachability.

The `reconcile-snapshot-output` transition binds the conditional
`0001202E` cached publication to the `FFFF106A` snapshot byte. Its raw
source component observes both natural producer invocations and the
bounded stock snapshot window with complete RAM continuity. The positive
consumer requires calibration-dependent cache and snapshot alternatives.
COPY, injection-copy and coherent-copy scopes admit only the exact
original/replacement representation of this one relation; a changed
claim retains its scope effect. All existing physical namespaces, TEST
contexts and other native facts remain fixed. No additional receipt or
natural scheduling or hardware admission follows.

`make verify` runs this qualified firmware gate before `make check` and `make test`.
Consumers can require current receipts after execution inputs change; no second
full GNU invocation follows those checks. The native validators still require
their complete existing byte/fixture/observation and claim contracts. Other TEST
attachment qualification remains tracked separately under issue #53. Full current
repository acceptance, physical validation requirements and open gate questions
are not satisfied by the controlled orchestration tests.

## Verification boundaries, inputs and diagnostics

`acceptance.toml` owns the reviewed group properties, repeat triggers, overlap
and evidence limits. `acceptance.py --check`, included in `make check`, checks
the group vocabulary, exact stock-region partition and local source/includes
against the registry the verifier executes. Counts come from that registry.

`uv run python tools/sh-elf-run/acceptance.py --manifest` emits exact direct
group source hashes and the input maps of the existing CAN, SID22 and TEST
protocols. Direct source anchors are not a complete physical execution closure.
The GNU source provenance also binds feature Python, assembly, headers and
configuration under `patches/` and shared Python tools. Native model inputs
remain part of that provenance. Runtime binaries/libraries, actual linked ELF,
prepared fixtures, aliases and ordered cases remain separate execution inputs;
CAN/SID22 packets bind their declared artifact identities and observations.
Timing records for other regions do not establish all those artifact identities.

The stock, SID22 and feature harness runners inspect the actual linked ELF before
simulator entry with declared test RAM. Allocated sections and both virtual and
physical LOAD extents, including BSS, must remain disjoint from that RAM window.
Missing or malformed ELF and storage intersections refuse execution. Exact
adjacency is allowed. This inspection preserves the linked instruction bytes;
ordinary feature execution and semantic assertions remain required independently.

A semantic reason to repeat execution is a changed consumed instruction,
calibration, address/width binding, real callee, fixture, oracle, matrix,
execution environment, or a concrete regression/non-determinism hypothesis.
Protocol freshness can bind a wider shared source set. Unchanged source anchors
do not establish unchanged ELF or toolchain/runtime behavior. Neither the group
metadata nor timing output authorizes selective qualification or removal of a
required gate. Complete matrix minimality remains unproved for the stock groups.
The current full-PASS finalizers and repository acceptance commands apply.

The primary verifier flushes `VQ_SH_ELF_STAGE` JSON start/finish records for its
preparation/feature stages and each registered stock region. Each pair has a
unique identity, exact stage name, terminal status and elapsed counter duration.
An exception emits a failed terminal and propagates; the primary entrypoint
prints its ordinary complete traceback. Abrupt process loss leaves a flushed
start without a successful terminal. The last started region identifies the
observed boundary, not an inferred missing stack or a successful execution.

`uv run python tools/sh-elf-run/acceptance.py --stages <stdout-path>` checks
successful complete timing pairs in the primary registry order. This is a
diagnostic structure check. Qualification still needs the exact original
successful process, stream hashes, candidate and independent fact validation.
Stage durations are not per-numeric-case durations. Case counts are not cost,
and nested/overlapping evidence boundaries must not be summed as new work.

Ordinary pytest diagnostics use verbose node IDs, complete traceback, JUnit and
per-case durations, for example:

```bash
uv run pytest -vv --tb=long --durations=0 \
  --junitxml=tmp/local-results/verification/pytest.xml \
  --basetemp=tmp/local-results/verification/pytest-work \
  patches/tests/test_sh_elf_execution_report.py
```

Keep the original bounded process and streams beside these reports. JUnit's
testsuite outcome count can include passing subtests beyond its testcase
elements; report both accurately. A hard timeout can leave JUnit unfinished.
Missing terminal output is not a pass. Historical truncated timer/SIGINT stack
diagnostics supply no acceptance; the supported route uses ordinary traceback,
flushed progress, original terminal and the exact-child lifecycle check. No
extra stack timer or altered sleep/GC policy is required by this route.

## Bounded CAN latch-copy witness

The registered `jk08a-can-latch-copy` region executes the exact JK08A caller
at `00021094`, its JSR and length-setting delay slot, and the natural helper
at `00022558`. `defs/JK08A.can-latch-copy.toml` owns the mechanism, entry
assumptions and simulation boundary; `kb.copy_matrix` owns its ordered cases.
The generated `can-latch-copy-cases.h` is regenerated with:

```bash
uv run python tools/sh-elf-run/can_latch_copy.py --write-cases
```

The source gate compares the header and region count with the executed matrix.
The observer captures every live GPR before scratch use, SR/PR/GBR/MACH/MACL,
natural SP/return effects, the helper's lower frame, and all RAM outside the
destination. Only the source pointer pool uses a RAM alias; R1/R11 are explicit
bounded-entry inputs. Whole-scheduler reachability and hardware behavior are
separate claims.

The fixed feedback command uses the primary container and a non-production
subset. It emits `kb-copy-subset` with the exact consumed private source bytes
and ordered actual observations, and `VQ_SH_ELF_CAN_COPY_SUBSET production=false`.
It emits no full-pipeline PASS or qualified candidate:

```bash
tools/sh-elf-run/run.sh --can-copy-early
```

`tools/sh-elf-run/run.sh --can-copy-witness` runs the complete primary pipeline
and full matrix. Only after success does it emit `kb-copy-candidate`, binding
actual private compilation inputs, image/reconstruction/fixture/ELF/toolchain,
observations, native model and complete producer provenance. The mount remains
read-only. Save the original bounded process receipt and streams under
`tmp/local-results/`, then independently finalize them:

```bash
uv run python -m kb.copy_evidence finalize \
  --process tmp/local-results/<run>-process.json \
  --stdout tmp/local-results/<run>.stdout --stderr tmp/local-results/<run>.stderr
```

The local `.kb/copy-receipts/jk08a-latch-12.json` is not committed. Failed,
partial, skipped, stale or subset runs cannot publish it; failed finalization
preserves an earlier receipt. The independent 1ME3B TEST protocol is separate.

## SID22 pointer-read witness

`defs/JK08A.sid22-pointer-read.toml` fixes the JK08A publisher at `0003235c`,
its five disjoint body ranges, all PC-relative pools and the three pointer
tables. The sum of instruction bytes is 1256; the complete contiguous backing
is `[0003235c,000328c0)`. The natural epilogue, RTS and delay slot remain under
test. The descriptor pins 50 original RAM reader claims and 55 SOURCE bindings
at 53 selected DIDs. Offsets 0 and 1 select independent pointer slots. DID
`130d` reads `ffff2a83` before `ffff2a81`.

`kb.sid22_matrix` defines 1700 ordered cases, including independent source
values, request lengths, signed starting indices, response wrap and actual
error paths. Families `11` and `12` have no general upper-index check. Family
`13` loads its first pointer before the `low <= 0x14` check. Selection of the
registered proof scope does not add firmware bounds checks. The source gate
compares the generated header, descriptor and registered region with this
matrix. Regenerate the header with:

```bash
uv run python tools/sh-elf-run/sid22_pointer_read.py --write-cases
```

The simulator relocates RAM pointers and signed-word RAM aliases, and replaces
only the external transport/error callees with explicit observing stubs. All
tested publisher instruction bytes match independent SH-2E assembly and remain
unchanged in the complete fixture. The real helper arguments, actual source
bytes and complete response ring are observed. The observer checks the complete
RAM footprint, natural SP/PR return, saved frame and independent C caller ABI.
Its exact register oracle covers R0 and R8..R14, GBR/MACH/MACL and SR outside T.
R1..R7 and T are captured without a final-value equivalence claim. This boundary
supports the selected RAM reader identities through source-byte publication;
it does not establish complete processor-state equivalence, scale or hardware
behavior. The four separate DID ROM access claims, dynamic DID `120b`, other
families and all declared-width reviews retain their independent scope.

The fixed non-production feedback command emits nine ordered observations and
no qualified full candidate:

```bash
tools/sh-elf-run/run.sh --sid22-early
```

One combined full invocation runs the complete primary pipeline and emits the
independent CAN and SID22 candidates only after success:

```bash
tools/sh-elf-run/run.sh --can-copy-witness --sid22-witness
uv run python -m kb.sid22_witness finalize \
  --process tmp/local-results/<run>-process.json \
  --stdout tmp/local-results/<run>.stdout --stderr tmp/local-results/<run>.stderr
```

The CAN finalizer consumes the same original full process and streams using its
separate protocol. The SID22 receipt at
`.kb/sid22-receipts/jk08a-pointer-read.json` is a local generated output.
Independent finalization verifies complete ordered observations, private
consumed source bytes, exact reconstruction, fixture/ELF/toolchain identity,
native facts, source provenance and the original bounded process streams.
Refusal preserves the preceding receipt. Ordinary reads, checks and sync never
execute a producer implicitly.

## Repository-contained gate

Run the complete current runtime gate from the repository root:

```bash
make verify-firmware
```

The first run builds the image defined by `Dockerfile`; later runs reuse Docker
layers. The runner selects the `default` Docker context without changing
the caller's configured context.

`VQ_SH_ELF_IMAGE` selects another compatible local image name.
`VQ_SH_ELF_SKIP_BUILD=1` skips the image build only when that image was already
built from the current Dockerfile.

`VQ_SH_ELF_STOCK_TIMEOUT_SECONDS` declares the stock simulator's execution
limit: `120` seconds by default, or an explicit `240`. The runner forwards the
value to the same container and rejects every other value before invoking
Docker. Assembly and compilation keep their existing limits; compilation
remains limited to 120 seconds. The extended limit changes no image,
instruction bytes, fixture, case, observation, or required PASS marker.

```bash
VQ_SH_ELF_STOCK_TIMEOUT_SECONDS=240 make verify
```

The gate performs these checks:

1. Assemble every current Map Switching, Rolling Launch, and CAN telemetry
   source unit with GNU `sh-elf-as --isa=sh2e`. This covers the canonical JK08A
   units and every rendered JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B
   target unit. A unit that includes a generated header of `patches/`, as the
   telemetry capture and control units include the profile identity
   `can-telemetry-identity.h`, reaches the assembler with the integer symbols
   of the header written as numbers; the telemetry harness compiles with
   `patches/` on its include path and installs the configuration record
   `TELEMETRY_CONFIGURATION` of the same header.
   Targets without a declared capability have no synthetic stage or payload.
2. Reconstruct each fill-aware ROM envelope and require byte identity with the
   corresponding SHA-locked payload in the tracked manifest.
3. Independently compose the current non-flashable capability-specific
   fixtures for JK08A, JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B and
   enforce their declared write sets, entries, hooks, pointers, mailbox record,
   stock-image identity, and stage hashes. The SH7058 images are one MiB; the
   SH7059 1ND and 1ME3B images are 1.5 MiB.
4. Execute every declared Map Switching selector, adapter, limiter, startup,
   feedback, Rolling Launch behavior, telemetry HCAN1 initialization, control
   polling, runtime enable overrides, capture, bank publication, page request,
   ACK, abort, preemption, corruption, and ISR path with distinct fixture
   values that expose wrong slots or addresses. The 8MFK cases include both
   CVTC target families, the two-byte-aligned throttle limiter container,
   mailbox 26, and the stock-ISR tail chain. The 1ND cases include both fuel
   banks, both warm-idle banks, the shared cold-idle family, native fuel-cut
   caps and curves, the exact stock fuel-cut state machine, the throttle
   scalar, Rolling Launch final-mask coordination, mailbox 26, and the stock-ISR
   tail chain. JK78C executes the same VQ37 capability cases through its
   independent SH7058 addresses, stock hooks, RAM sources, and checksums.
   1ME3B executes them through its own SH7059 addresses with the target bit
   layout: the native fuel-cut state byte keeps the active and armed flags in
   bits 3 and 2. The ASCD cases of every target set the MAIN switch bit of the
   ASCD flag byte at the position of its layout: bit 7 on JK08A, JK00C, and
   JK00D, bit 4 on JK78C, bit 5 on 1ND, and bit 1 on 1ME3B. One selector case
   and one Rolling Launch gate case set every other bit of the byte, which
   neither aborts the selector nor fails the gate. The Rolling Launch
   fuel-cut flag cases set the active cut bit of the stock RPM fuel-cut state
   of each target: bit 2 on JK08A, bit 6 on JK00C and JK00D, and the active
   bit of the native rev-limit state byte on the VQ37 targets, bit 4 on
   JK78C, bit 5 on 1ND, and bit 3 on 1ME3B. One case sets every other bit of
   the byte, and on the VQ37 targets a final mask that inhibits all six
   cylinders, and requires the flag clear; the VQ37 fuel coordinator cases
   require the state byte unchanged. The VQ37 Rolling Launch hold cases run
   the engine and then the coordinator wrapper at engine speeds below, at, and
   above cut and at and below restore in both hold modes and in observe mode,
   and require the request, its latch, and the final mask of each pass: the
   request latches at cut, holds down to restore, releases below it, stays
   released between the thresholds, and latches again at cut; a latch other
   than 1 publishes no request; an abort clears the latch; and activation
   clears a latch left in IDLE at a saturated capture, whose captured speed
   lies between restore and cut. The telemetry knock surface cases set
   the high-detonation bit of the knock surface byte of each target, bit 6 on
   every target except 1ME3B and bit 7 on 1ME3B, whose capture moves it into
   wire bit 6 and clears the other bits of the wire byte; one case sets every
   other bit of the byte and requires wire bit 6 clear. The
   VQ37 ignition cases select all five slots of the two executed 16x16
   surfaces. The 1ND and JK78C cases pass the three equal-byte surfaces of the
   gated coordinator half, which the 1ME3B coordinator does not carry, through
   the adapter while a non-default slot is active. The harness
   names those three bases by the placeholders `0x0000991a`, `0x0000e91a`, and
   `0x0000ea1a`, which the target renderer rewrites to the profile symbols
   `ignition_gated_surface_1` to `ignition_gated_surface_3`. The 1ND and 1ME3B
   targets add the adapter of the four 8x8 state-code ignition surfaces: every slot and
   both invalid selector values of each family, plus one unknown base that must
   reach the stock 8x8 lookup unchanged. The harness names the four bases by
   the placeholders `0x0000f610`, `0x0000f710`, `0x0000f690`, and `0x0000f6d0`,
   and the stock 8x8 lookup is a return stub of the dynamic fixture. The three
   targets differ in adapter count and entry count; each
   marker carries its own values, and the verifier sums the case counts the
   markers report.

   The 1ME3B runtime phase also executes every declared ignition-literal call
   window through the actual composed adapter pointers. The independent
   `stock_1me3b_ignition_consumers.s` reconstruction binds the stock loads,
   JSR operands, delay slots, axes, tables and intervening argument stores.
   `stock_ignition_consumer_invoke.s` supplies independent R7 and fifth stack
   arguments and records complete entry/exit state, caller ABI and stack.
   `ignition_consumer_callee.s` replaces the unchanged lookup body solely to
   observe its complete real entry and return path. All declared slot values
   and both invalid selector values execute for each bounded window.

   `ignition_literal_capture.py` retains the private consumed sources,
   reconstruction, composition, fixture, ELF/object identities, actual GNU
   streams and complete raw observations in the existing shared COPY packet.
   `kb.ignition_literal_evidence` checks the original complete primary,
   current sources and physical bindings, reconstructs the observing stub
   independently, and checks actual state with separate Python equations.
   The evidence grants no scheduler-reachability, arbitrary-computed-consumer,
   stock-interpolation-arithmetic or hardware claim. The region scan does
   not exempt a literal from coverage.

   Original finalization binds the complete native producer provenance.
   Consumption checks the declared executable-source closure and independently
   rebinds the current native runtime declaration, complete composition and
   prepared fixture. Exact original native provenance remains in the original
   record. Review publication metadata supplies no instruction or ABI value;
   it cannot replace any current runtime, source, ROM or fixture check.

   The canonical JK78C, 1ND0A and 1ME3B phases capture the packed-field
   transfer windows declared by `defs/packed-field-transfers.toml`, including
   the natural copy calls that separate the mask-window base load from the
   wider access. The independent mnemonic fixtures retain the tested stock
   bytes. The raw C driver records const input contexts, full exit state,
   caller ABI, seeded stack and all declared RAM. Its observations remain in
   the existing COPY packet. `kb.packed_transfer_capture_evidence` binds the
   same complete original primary, exact native width questions, consumed
   sources, fixture and actual streams before independent input/state/lane
   equations apply. A wider transfer does not infer a wider semantic field
   or publication, scheduler reachability, or hardware behavior.
5. Apply only the documented simulator transformations after exact byte
   identity succeeds: high-RAM data-literal relocation and explicit stubs for
   unchanged stock callees outside the implementation under test. The Rolling
   Launch fixture uses a deterministic, PC-relative-alignment-aware stock
   serializer stub to seed the CAN payload before executing both feedback
   layers. The VQ37 fixture stubs the stock final-mask fuel coordinator with a
   deterministic routine that publishes a distinct base mask to the aliased
   final-mask byte and returns that byte zero-extended, so the wrapper return
   path is executed against an exact expected value. The telemetry fixture
   replaces the stock knock slice evaluator of every target with a stub that
   stores a staged 32-bit value at a staged address, counts the call, and
   overwrites `r0..r7`. The harness stages the offset-binary metric of the
   evaluated channel through the block at `0x0100ff00` of the test window, so
   a knock margin wrapper that reads its operands before the stock call, or
   that relies on a register across it, fails the case. The telemetry fixture
   also installs a simulator-only TRAPA vector after byte identity is proven.
   The pinned GNU simulator's TRAPA/RTE uses SPC/SSR and leaves SP unchanged; it does not
   establish the SH-2E PC/SR exception stack. Equivalent exception-stack
   coverage is required before hardware eligibility. The canonical combined
   SLE1 ISR returns through its unchanged `RTE` instruction. Each 8MFK wrapper
   restores all interrupted registers, including `r0` in the `JMP` delay slot,
   and tail-chains to an explicit simulator-only `RTE` stub for the unchanged
   stock ISR. The same tail-chain boundary is executed for the VQ37 mailbox-26
   wrappers.
6. Execute the exact unsafe delayed-branch incident words at their ROM addresses
   and require an illegal-instruction stop, while a control fixture that changes
   only the delay-slot word returns normally.
7. Execute the stock instruction regions whose behavior the entity files state
   (`verify_stock_code.py`). The JK08A MAF ADC slice reconstructs both unsigned
   word reads, the six-bit logical shifts, and the two word stores, including
   the return delay slot. The immediate MMIO-base prologue stays byte-bound
   outside the slice; the harness supplies its mapped R4 context and relocates
   only the declared output-window pool word. Independent bank values, signed
   word boundaries, discarded low bits, maximum counts, read-only MMIO, and
   neighboring output bytes have literal expectations.
   The MAF scaling fixture reconstructs the complete bank-selected publisher,
   coefficient guard, and unsigned Q1.15 scaler at their stock addresses.
   Cases execute both banks, bit3 guard bypass, inclusive coefficient bounds,
   reset to the stock ROM word, the raw-full-scale increment after scaling,
   unsigned product truncation, word saturation, and MACL preservation in the
   scaler's return delay slot. Only five declared RAM pool words are aliased;
   the bounds, reset word, call targets, and tested instructions stay stock.
   The publisher's final signed cap comparison follows EXTU.W, so its taken
   branch is unreachable from the function entry. Explicit direct entry supplies
   a wide R5 and the producer's saved return frame to execute both outcomes
   without changing tested instructions. These branch cases establish no
   reachable ADC state or physical meaning for the coefficient bypass mode.
   A separate battery fixture reconstructs its complete publisher and the
   same guard and scaler. Literal cases distinguish the raw word copy, input
   byte truncation after the two-bit shift, and final byte cap from the MAF
   word contract. They exercise both coefficient modes, all bound edges,
   input byte wrap, signed-word boundaries, and byte saturation without a
   full-scale increment. Six declared RAM literals alone are aliased. The
   stock publisher restores GBR and PR, and the harness also checks MACL,
   mode and source preservation, and every neighboring output byte.
   The MAF compensation fixture reconstructs the complete bank-indexed
   preprocessor and unsigned divider. First-call cases bind masks 1 and 2 to
   bit0 and bit1 and preserve the sibling bank and other flag bits. Initialized
   cases check the unsigned 32-bit numerator's split products, the saturated
   previous-word denominator, quotient truncation, and modulo-65536 output.
   Five successive calls per bank retain the literal sequence 200, 172, 169,
   168, 168 for K=0x00180000. The stock bias 80 prevents a zero denominator
   from the function entry; explicit entry at its zero test supplies the full
   saved frame and checks the raw+1 word alternative. Direct divider cases
   cover the short quotient, wide divisors, and zero-divisor fault record.
   Four declared RAM literals alone are aliased. Every tested instruction,
   natural return, calibration word, mode byte, and read-only input remains
   stock; MACL, GBR, and saved R12/R13/R14 are checked after execution.
   The MAF transfer fixture reconstructs both lookups and word publications,
   including bank 2's store in the BSR delay slot. The complete implicit
   64-point word wrapper, its eight-shift body, and unsigned linear finisher
   retain their stock addresses and returns. Literal cases check both curves,
   low-12-bit input truncation, 16-count cells, fractional truncation, unsigned
   cells, both interpolation directions, argument wrap, and the sign-extended
   last-cell return whose caller stores only the word. Direct body cases
   execute the byte-cell alternative with explicit format context. The
   unchanged following callee 0x0003b320 executes only its stock zero-selection
   path and natural return; its other calibration-selected paths gain no
   execution claim. Four declared RAM literals alone are aliased. After both
   word stores and that callee, the boundary at 0x0003a950 restores PR from
   stack offset zero outside all tested instructions. Cases check MACL, GBR,
   the input base, both input words, stock tables, and neighboring RAM.
   The MAF filter fixture reconstructs the complete bank-indexed working copy
   and first-order filter. It executes both unsigned word copies and outputs,
   byte argument truncation, bit5 copy/weighted selection, stock coefficient
   26/256, floor rounding, and the one-count rising correction. Five successive
   filtered calls per bank retain the literal sequence 101, 192, 274, 347, 413
   for input 1000 from zero. The copy's cap and negative-value branches are
   unreachable after EXTU.W; direct entry supplies wide R2 values. With stock
   coefficient 26, a lower input makes the weighted result strictly below the
   previous word, so the downward anti-stall branch is also unreachable from
   the function entry. Direct post-arithmetic entry supplies input, previous,
   and weighted words plus the saved GBR/MACL frame to execute both corrections
   and both skip paths. These cases establish no live calibration or physical
   time constant. Three declared RAM pool words alone are aliased. All stock
   instructions, coefficient data, natural returns, input words, flag bits,
   sibling-bank values, MACL, GBR, saved registers, and neighbors are checked.
   The per-bank contribution fixture reconstructs 345 instructions across
   the complete MAF producer and its six-shift signed division helper.
   Both banks execute active correction and fallback modes, byte-truncated
   bank arguments, all inhibitor combinations, nonzero latches, unsigned
   word inputs, signed correction histories, word clamps, and residual signs.
   Literal cases distinguish truncation toward zero at /8, /512, and /256
   from floor at the final /64. Fallback cases distinguish low-32-bit
   multiplication before logical shifts from an unbounded weighted sum.
   Wide reference inputs and fixture-only weight variants cover software
   boundaries without asserting live reachability. Explicit post-base entry
   at `0x0003b042` supplies a complete saved stock frame and local state to
   execute otherwise unreachable signed 24-bit residual bounds and the
   active output cap; all tested instructions and natural returns stay stock.
   Repeated calls keep external references fixed and exercise producer-owned
   correction state; they establish no scheduler cadence or physical scale.
   Five declared RAM pool words alone are aliased. MACL, GBR, saved registers,
   inputs, sibling state, mode bytes, calibration, and neighbors are checked.
   The combined-MAF fixture reconstructs the complete 22-instruction sum.
   It executes signed bank contributions, sign-extended correction words,
   unsigned auxiliary words, 32-bit wrap at every addition, and the signed
   zero clamp after the final sum. Literal cases cover the largest positive
   longword, the smallest negative longword, positive and negative overflow,
   and cancellation of signed and unsigned words. Both RAM pool words alone
   are aliased; natural return and GBR restoration execute unchanged. Cases
   check the returned and stored longword, preserved registers, all input
   bytes, and output neighbors. They establish no live overflow or physical
   identity of the auxiliary term.
   The primary BFS fixture reconstructs 378 instructions across speed
   selection, split-product arithmetic, Q7 compensation, and the complete
   unsigned divide and remainder helpers. Positive signed aggregate selects
   the primary calculation; zero or negative values publish zero. Normal
   mode selects either unsigned speed word by bit5; alternate incoming mode
   uses eight times its cached speed byte. Each count is clamped to at least
   64. The product after /256 retains 40 bits, and a zero denominator selects
   the fixed cap without recording a helper fault. Literal cases cover stock
   coherent aggregate bounds, explicit wide-product wrap, unsigned division
   boundaries, final factor 9163/65536, Q7 coefficient extremes, output
   saturation, and mismatched cached quarter BFS. Those explicit contexts
   establish no full-entry reachability or live calibration claim.
   Seven declared RAM pool words alone are aliased. Independent GNU assembly
   binds 828 bytes; the decoded static test additionally binds pre-entry
   context for 930 bytes in total. The boundary at `0x0003b908` restores PR
   from SP+24 outside tested instructions, before the rate stage. Cases
   check the stock cache/register result, source words, coefficient, flags,
   neighboring RAM, and ROM coefficients. The helper restores the external
   C frame after recording the stock slice's register and MACL changes.
   The fallback lookup and final BFS publication remain outside this proof.
   The BFS limiting fixture reconstructs 163 instructions across the bit7
   selector, both corrected working-word paths, implicit byte lookup, direct
   diagnostic grid, and exact word publication. All 256 coordinate bytes
   execute for the stock limit curve and explicit rising/descending patterns.
   Cases retain directional floor increments, signed correction truncation,
   the zero clamp, below/equal/above cap, natural last-cell signed return,
   byte argument wrap, diagnostic row and throttle-column boundaries, and
   zero above the grid's speed range. Explicit word-format body entry covers
   the shared cell-width branch without claiming that the byte wrapper uses
   word cells. The pre-entry ROM mode mask and correction cache association
   are statically bound; the preceding producers do not execute here.
   Six declared RAM pool words alone are aliased. Independent GNU assembly
   binds 400 bytes; the decoded static test binds 509 bytes. The boundary at
   `0x0003bc80` restores PR from SP+0 after the tested BFS word store. Cases
   check MACL, GBR, the publication pointer, all source bytes, the normal cap
   byte's preservation in diagnostic mode, tables, and neighboring RAM.
   The Q7 load fixture reconstructs the 32-instruction normalization slice
   and its unsigned divider. Entry R5 contains the preceding unsigned BFS
   word; a separate byte proof binds its stock load and preservation. Cases
   execute the cached saturation check, explicit word reread, both division
   delay slots, byte publication, stock reference 27226, word/reference
   boundaries, and the zero-reference fault record. Artificial mismatched
   cache/RAM inputs distinguish the cached cap from the second quotient's
   low-byte store; they establish no reachable race. Direct divider cases
   execute the wide-divisor path outside the word-only normalization entry.
   Only three declared RAM pointers are aliased. The boundary at 0x0003bd5c
   restores PR from SP+0 outside all tested instructions. Cases check saved
   registers, MACL, GBR, R11, the reference word, inputs, and neighboring RAM.
   The load-snapshot fixture reconstructs the scheduler's two BFS history
   stores and complete 28-byte copy call. The unchanged length dispatcher
   selects 0x0002213a through its stock table entry; its JMP delay slot loads
   the last source longword before the seven descending longword stores.
   Cases cover all source bytes, word and byte sign boundaries, independent
   patterns, unchanged source and guards, and three successive snapshots.
   Five declared RAM pool words alone are aliased. The copier returns through
   its natural RTS and R3-pop delay slot; the boundary at 0x00020f1c restores
   PR from SP+0 outside tested instructions. The helper frame is shared with
   the normalization fixture. This proof covers the length-28 selection and
   byte-zero view, without a complete scheduler, other copy lengths, or
   hardware atomicity claim.
   The JK08A axis-search fixtures reconstruct the
   byte and word kernels and their unsigned fraction divider. Cases use the
   stock fuel, ignition, and torque row axes and independent literal offsets
   and fractions. They check clamping, exact points, unequal intervals,
   quarter-count coordinates of the byte kernel, unsigned word boundaries,
   both divider outcomes, output guards, and read-only axis data. The byte
   kernel multiplies each stored point by four; the word kernel compares
   the stored unsigned word directly. Both return through stock instructions.
   A separate direct-byte fixture searches both main CVTC axes without a
   point multiplier, including the forced maximum load coordinate. The
   implicit eight-point fixture uses the stock injection and cold-timing
   curves and checks byte argument truncation, flat and fractional results,
   and the sign-extended last-cell return that callers convert to unsigned.
   Synthetic ascending and descending byte and word arrays exercise both
   cell-width branches and both linear interpolation directions. The direct
   shared-body calls remain below the wrapper's last-cell boundary. These
   fixtures preserve all tested instructions, original pools, and stock
   returns, with no RAM-literal relocations or stock-function stubs.
   The JK08A crank-capture fixture reconstructs
   the word read of OSBR1, capture-history update, initialization branches,
   and both period stores. The earlier MMIO-base load and its signed pool
   word stay bound outside the executable slice; the harness supplies the
   mapped base in R11. Cases check the first-sample sentinel, preserved flag
   bits, zero intervals, unsigned word wrap, both signed-word transitions,
   the read-only MMIO window, and neighboring RAM.
   The JK08A tooth-period fixtures reconstruct
   the conditional normalization and ordinary copy as separate instruction
   spans, with their original pool data between them. The harness supplies
   the base registers, current interval, and masked synchronization snapshot
   from the prologue's entry state. It checks the fixed-point approximation
   on positive multiples of three, unsigned word boundaries, independent
   reference and tooth intervals, and unchanged input windows.
   The fallback quotient fixture reconstructs the stock caller and unsigned
   divider, checks the newly published interval rather than the preceding
   interval, and checks both word stores across quotient overflow. Its
   simulator boundary restores PR from a prepared stack slot after the
   stock JSR replaces it; the restoration and return lie outside all tested
   instructions. The boundary refuses misaligned or unsupported stack
   offsets, overlap with pool data, and use with a natural stock return.
   The JK08A event-interval slice
   `0x00028afa..0x00028b41` retains the producer's mode, holdoff,
   subtraction, unsigned wrap adjustment, divide-by-32 publication, marker,
   previous-capture refresh, and returns. Its harness supplies the mapped
   previous-capture pointer in R1; the preceding MOV.W pointer load at
   `0x00028af8` lies outside the executable slice. Its original pointer word
   remains in the reconstruction. The fixture changes only declared
   high-RAM longword pools and preserves all instruction bytes in the slice.
   Expected cases cover both sides of each selector, wrapping and
   nonwrapping differences, equal captures, count boundaries, input and
   window preservation, marker bits, and both stock return paths.
   The JK08A median producer
   `0x0003df2c..0x0003dfc5` and its signed divider
   `0x00021bbc..0x00021cd5` share an independent reconstruction at their
   stock addresses. The harness checks every strict order and ties of
   three unsigned samples, history shifting, quotient truncation and byte
   saturation, a zero period with a nonzero retained median, and diagnostic
   copying without a history update. Direct divider entries cover positive
   and negative operands, short and long divisors, and zero recording.
   Only declared RAM pool words are aliased; both functions retain their
   stock returns. The history and output windows retain all other bytes,
   and the mode, source, and period inputs remain unchanged.
   The JK08A primary RPM producer
   `0x00038272..0x0003829d` and its unsigned divider
   `0x00021ce0..0x00021dc5` share an independent reconstruction at their
   stock addresses. The harness takes the mode flags, event interval,
   output word, and divider entry from the meaning files. It executes
   inhibit selection, zero-divisor recording, quotient truncation,
   saturation, and the unsigned word/longword divisor boundary. Direct
   divider entries also exercise the short-quotient branch, its boundary,
   and the maximum unsigned return value. Only the declared high-RAM
   pool words change in the simulator; both functions return through their
   stock instructions. The output window and mode flags retain all other
   bytes, and zero division writes the stock diagnostic record.
   The JK08A region `0x0003e1fe..0x0003e26b`
   contains the enabled non-fault arithmetic of the RPM-drop producer.
   Its GNU reconstruction links on `0x0003e1fc`, with two padding bytes
   outside the region, to preserve PC-relative longword alignment.
   `stock_invoke_gbr` supplies the aliased `satisfied-macaque/ram` address
   as GBR. The harness takes current speed, four-sample-old speed, and the
   preceding filter snapshot from the meaning addresses. Reviewed expected
   literals distinguish rising speed with nonzero history, equal speed,
   falling speed, truncation, and saturation; every neighboring byte stays
   unchanged. The only simulator changes are the high-RAM pool word and the
   RTS/NOP boundary at `0x0003e26c`; the arithmetic instructions stay stock.
   Mode selection, history shifting, and publication are outside this slice.
   The JK78C region `0x000fcbb0..0x000fcbed` of the
   ASCD task `0x000fb9c0` holds the coolant flag and the MAIN switch block.
   The verifier links its GNU reconstruction `stock_jk78c_ascd_main.s` at the
   region start and requires byte identity with the stock image for the region
   and the four pool words that it loads. The fixture aliases the two high-RAM
   pool words, places an RTS/NOP pair at `0x000fcbee` directly after the
   region, and keeps the region bytes stock. `stock_invoke.s` calls the region
   with R12 set to the stock pool literal that `0x000fc9ca` loads and with GBR
   0, as the stock firmware runs. The harness takes the address of
   `ascd_state/ram`, the mask of its named bit `main`, and the address of
   `button_state/ram` on the layout from the entity files and executes every
   branch outcome: the button source, the alternative source that bit 7 of the
   calibration byte `0x0000894f` selects, which the harness sets in the fixture
   for two cases and then restores, and both outcomes of the coolant threshold.
   Each case requires the MAIN bit to follow its source, the other bits of the
   flag byte to keep their values, and every other byte of the flag window to
   stay unchanged. The JK00C function `0x00050bf8..0x00050c99` and the JK00D
   function `0x00050bf4..0x00050c95` are the main RPM fuel-cut state machines
   of the two relocated 8MFK layouts. The reconstructions
   `stock_jk00c_rpm_fuel_cut.s` and `stock_jk00d_rpm_fuel_cut.s` hold each
   function and the five pool words that it loads; the fixture aliases the two
   high-RAM pool words, and the function returns through its own RTS, whose
   delay slot restores the GBR that it saves. The shared harness
   `stock_rpm_fuel_cut_harness.c` takes the address of `fuel_inhibit/ram`,
   the masks of its named bits `armed` and `active`, the engine speed word
   `rpm/ram`, and the threshold table `rev_limit_fuel_cut/tbl` from the entity
   files, and the delay counter, the pair selector, and the configuration and
   delay bytes, which no entity file names, from the region. It requires the
   stock configuration to select the pair by bit 4 of the selector, reads the
   thresholds from the fixture, and executes both pairs: speed below, at, and
   above the cut-on word with the arm clear and set, a zero and a nonzero cut
   delay counter, a nonzero delay byte that the harness sets in the fixture for
   one case and then restores, and speed at, above, and below the release word
   with the cut active. Each case requires both named bits, the delay counter,
   and the return value, the other bits of the state byte to keep their
   values, the engine speed word, and every other byte of the window around
   GBR to stay unchanged.

A successful run prints `VQ_SH_ELF_MAP_SWITCHING`,
`VQ_SH_ELF_ROLLING_LAUNCH`, `VQ_SH_ELF_ROLLING_VERIFY`,
`VQ_SH_ELF_CAN_TELEMETRY`, `VQ_SH_ELF_CAN_TELEMETRY_VERIFY`,
`VQ_SH_ELF_RUNTIME_TARGET`, `VQ_SH_ELF_RUNTIME_TARGETS`,
`VQ_SH_ELF_STOCK_CODE`, and `VQ_SH_ELF_VERIFY` markers with `status=PASS`. The markers calculate current
instruction, case, branch, relocation, and composition values at runtime; this
document does not duplicate them.

The target payload registry is a tracked product of the same pinned GNU
toolchain. Rebuild it after an intentional target-source or address-profile
change with:

```bash
make runtime-targets-generate
```

The same entry point reconstructs the canonical JK08A telemetry manifest with
`tools/sh-elf-run/generate-targets.sh --telemetry`. It assembles every unit with
the existing fill-aware GNU assembler, applies the static instruction audit,
and requires the existing unit and composition digests before rendering.
Changing those byte locks remains a separate update operation.

`make check` runs both payload families with `--check`. This mode reconstructs
the complete manifest and compares its UTF-8 bytes without writing it; missing
files, changed values, and different line endings fail the gate.

## Main fuel compensation

The JK08A main-compensation region reconstructs 301 instructions and 962 bound
bytes at their stock addresses. Its 3494 cases cover the full surface/bypass
selector, all column bytes, every row-axis breakpoint and adjacent coordinates,
endpoint clamps, four distinct surfaces, directional rounding, column-first
interpolation, the three bounded bypass sources, and exact byte publication.
Direct wrapper calls cover word/byte argument truncation and sign-extended
exact-cell returns; direct unsigned-divider calls include a zero denominator.
The static contract additionally binds the preceding input-base and cached-RPM
loads, for 996 bytes whose individual corruptions are rejected.

The tested slice begins at `0003c1c0`, joins the surface at `0003c284`, and ends
after the `ffff1160` byte store at `0003c29c`. Byte row-axis points are multiplied
by four; column-axis points are direct bytes. The two axis kernels return a cell
and truncated Q0.16 fraction. The byte finisher interpolates columns in each
active row before rows, with separately truncated ascending and descending
increments. Both zero fractions permit a sign-extended exact-cell return; the
coordinator publishes its unsigned low byte.

The simulator aliases only the three declared RAM pool words after exact byte
comparison. An external return continuation at SP+4 leaves the column argument
byte at SP+3 intact and restores PR beyond the tested instructions. The table,
axes, control bytes, source RAM, neighboring bytes, cached RPM, input base, MACL,
and GBR are checked for preservation. Explicit surface/control patterns are
simulator input contexts. Preceding writers and physical mode identities are
outside the executable slice; engineering scales retain their existing levels.

## External npkern gate

Run the external gate separately:

```bash
make verify-npkern
```

Or request it after the repository-contained gate:

```bash
tools/sh-elf-run/run.sh --with-npkern --verbose
```

The default checkout is `../../oss/npkern` relative to this repository.
`VQ_NPKERN_SOURCE` may point to another checkout, but `run-npkern.sh` requires
that path to be the Git root, at the exact revision embedded in the script, and
completely clean. It does not fetch, clone, select a mirror, or modify the
external project.

If the checkout is absent, the external command reports `status=SKIP` and
`hardware_ready=NO`. A wrong revision, nested Git root, or dirty tree is a hard
failure. The repository-contained gate remains independent of npkern
availability.

The npkern verifier builds exact-address SH7058 and SH7059 CAN targets in
read-only and explicitly write-enabled configurations, executes parser,
ISO-TP, and flash-boundary fixtures, checks production-to-simulator byte
identity outside declared relocation literals, and verifies the unchanged
legacy SH7058 K-line target.

### Factory loader ABI

The CAN targets load through the factory reprogramming services `0x27`,
`0x34`, `0x36`, `0x37`, and `0xBF` of the stock diagnostic dispatcher, in that
order. The dispatcher selects each service handler with a PC-relative `mov.l`
from its literal pool:

| ROM | Dispatcher | SID | Literal-pool entry | Handler |
| --- | --- | --- | --- | --- |
| JK08A | `0x0002F928` | `0x27` | `0x0002FB44` | `0x00033578` |
| JK08A | `0x0002F928` | `0x34` | `0x0002FB5C` | `0x00034410` |
| JK08A | `0x0002F928` | `0x36` | `0x0002FB3C` | `0x000345F4` |
| JK08A | `0x0002F928` | `0x37` | `0x0002FB40` | `0x0003469C` |
| JK08A | `0x0002F928` | `0xBF` | `0x0002FB38` | `0x0003475C` |
| 1ND0A | `0x00035098` | `0x27` | `0x00035290` | `0x00039278` |
| 1ND0A | `0x00035098` | `0x34` | `0x00035294` | `0x0003A200` |
| 1ND0A | `0x00035098` | `0x36` | `0x000352C8` | `0x0003A494` |
| 1ND0A | `0x00035098` | `0x37` | `0x000352CC` | `0x0003A55C` |
| 1ND0A | `0x00035098` | `0xBF` | `0x000352C4` | `0x0003A624` |

`tools/tests/test_npkern_can_verifier.py` reads every row from the registered
stock image, requires the entry to hold the handler, and requires a `mov.l`
between the dispatcher entry point and the literal-pool entry to load it. Each
target in `verify_npkern_can.py` spans the loader-owned window from `origin`
to `boundary`, and its `aligned_limit` is that window rounded down to 32
bytes; the same test holds the relation.

## BFS rate state

The JK08A rate-state fixture reconstructs 310 instructions and 678 bound bytes
across the rate arithmetic, latch/timer coordinator, signed correction,
optional blend, natural six-shift helper, and diagnostic-record predicate.
Its 461 cases cover both unsigned 15-bit paths, product and word saturation,
same-value increment, latch boundaries, timer combinations, every mode-byte
value, independent inhibitor combinations, signed rounding and clamps,
weighted publication, and the natural word-sentinel query.

The caller passes R4=-1 in the query's JSR delay slot. The unchanged predicate
returns zero for that signed word regardless of diagnostic-record contents.
Its active third timer therefore decrements toward zero. Eight explicit
post-query entries at `0x0003BA6A` supply artificial zero or nonzero R0 values
to execute both timer arms; nonzero results establish no stock reachability.
Isolated correction and blend entries retain separate register-context scope.

Seven declared high-RAM pool words alone are aliased. A boundary outside the
tested code at `0x0003BB86` restores PR from SP+24 through R1, preserving the
cached R5. Cases compare all eight output states, read-only RAM, calibration,
32 bytes of fragment stack, and distinct before/after C-ABI register states.
Fragment register observations remain separate from the containing function's
entry and return contract. The static test binds 734 bytes, including the
preceding cache/flag/base loads, and rejects every single-byte corruption.
Published counts derive from the registered region and emitted execution
marker. The optional exact-PC observer below adds per-context helper-call
counts through the same registered execution API and byte-bound fixture.

## Knock threshold lookup

The registered JK08A knock-threshold fixture reconstructs 184 instructions
and binds 635 bytes, including the stock selector, six rows, word axis and
last neighboring word. Its 829 cases execute the complete accessor and its
word-axis wrapper, search, divider and unsigned linear finisher through
natural stock returns. Factory calibration is checked before artificial
selector, table or axis contexts. Every stock knot, adjacent coordinate and
interval midpoint is exercised for all six rows.

The accessor requires a one-based channel in 1..6 and contains no channel
guard. Its result is stored at the selected word; natural R0 is twice the
channel and R2 holds the threshold. Descending interpolation truncates the
positive decrement before subtraction. The last-cell path still reads the
following word even with zero fraction, so that word is bound too.

Only three high-RAM pool words are aliased. Cases compare the full aliased
RAM outside the selected output, sibling words, calibration and stack
footprints. Stock preserved registers and the external C caller ABI have
distinct before/after observations. Comparison, count publication, metric
production, reference learning, physical channel identity and engineering
scale are outside this executable slice. The detailed contract is in
[`JK08A.knock-detection.md`](../../defs/JK08A.knock-detection.md).

## Knock timing-state selection

`jk08a-knock-state-selection` binds 70 instructions, 208 bytes and 11615
literal cases: 7671 explicit post-lookup entries and 3944 standalone
alternative entries. The direct path computes widened signed R2 from the
signed target word and `256*(H-(uint32(R0)&127))`. The alternative path slews
the target within source +/-1280, applies the unsigned-byte floor -256*N
and caps at zero. Normal gate bits select these paths; standalone entry
executes only the alternative arithmetic.

The first lookup and second lookup are not executed. Static anchors bind
their tables, call/delay pairs and bases; explicit contexts supply their
operands. The second mask and stack byte store execute. All low7 differences,
both widened overflow directions, every gate byte and negative-bound byte,
valid slew/floor/cap neighbors and unreachable floor outcomes are checked.
Six RAM pool aliases leave the instruction words unchanged.

Every case checks full literal register exits, T/MACL, SP/driver PR, the
64-byte frame, separate external C ABI, all calibration/context bytes and
all other RAM bytes. The output publication slots are preserved. Natural PR
from the preceding lookup, full coordinator execution and hardware behavior
remain outside the proof. Separate conversion composes the low-word wrap
and signed-byte result without a joint execution claim or signed monotonic
claim across wrap. The narrow contract is in
[`JK08A.ignition-state.md`](../../defs/JK08A.ignition-state.md).

## Knock event correction publication

`jk08a-knock-event-publication` binds 26 instructions, 76 bytes and 8754
literal cases. Explicit RAM contexts supply signed S/W/C; the full
independent incoming R6 supplies P in 0..65535. The widened signed32 sum
S+W is published to `ffff1ff8`; the signed byte at `ffff12d6` is
`max(-128,min(127,S+W+C-P))`. Subsequent arithmetic retains the shared
register sum without RAM readback. The separately seeded `ffff1ff6` word
is preserved and supplies no numeric input to this slice.

Cases cover signed extrema, word-range crossings and both clamp edges.
Every case checks both publications, T, general/special registers,
SP/driver PR, the entire frame, independent C ABI, all calibration/pool
bytes and every other RAM byte. The natural R13 anchor at `0004da7c`
and other exact base anchors are not executed; the driver supplies their
register contexts. Declared high-RAM pool aliases preserve all checked
instructions. Full builder execution, timer/latch behavior, P production,
bypass paths, full-function return, cadence and hardware behavior remain
outside the proof. The narrow contract is in
[`JK08A.ignition-state.md`](../../defs/JK08A.ignition-state.md).

## Knock event retard

`jk08a-knock-event-retard` binds 63 instructions, 147 bytes and 7408 literal
cases. Explicit RAM contexts exercise all four combinations of Q (RAM flag
bit5 or bit2) and G (ROM mode bit5). K, A and B are signed bytes; H is the
unsigned high byte of the source word. Q0 writes -A; Q1/G0 writes min(K,-A);
Q1/G1 writes min(K-H,-B). With G1 the companion is -B for Q0 or min(K,-B)
for Q1; G0 preserves its complete prior word.

Stock mode `0x7c` and artificial mode contexts are labelled separately.
There are 3605 stock-mode and 3803 artificial cases. In the 3676 G0 cases the
companion retains the complete prior word through the no-store branch.
Coverage includes signed boundaries, high/low word contamination, independent
RAM bits and all ROM mode bytes. Every case checks output/retention, T, all
general/special registers, SP/driver PR, the full 52-byte frame, independent
caller ABI, all calibration/pool bytes and all other RAM bytes. Four RAM pool
aliases leave checked instruction words intact. The ordinary return boundary
at `0004da2a` is outside stock spans. Full builder mode reachability, timer/latch
behavior, producer identities, later summation, cadence and hardware behavior
remain outside the proof. The narrow contract is in
[`JK08A.ignition-state.md`](../../defs/JK08A.ignition-state.md).

## Knock event integration

`jk08a-knock-integration` binds 39 instructions, 114 bytes and 4035 literal
cases: 3967 event entries and 68 quiet entries. Independent event R4 is in
0..255; the 32-bit MUL.L consumes it without an in-fragment EXTU.B. RAM count
is seeded independently. The event result is signed saturation of S-307*R4;
the quiet result is signed saturation of S+13. Both clear the RAM count and
are alternative entry views, not sequential updates or a dispatch inference
from R4=0.

All byte counts, signed state boundaries and in-domain saturation transitions
are covered. MACL contains the event product or retains the quiet input.
Per-case checks bind the working arithmetic register, T, all general/special
registers, SP/driver PR, the full 52-byte frame, independent C caller ABI,
calibrations and all other RAM bytes. Five RAM pool aliases preserve all
checked instruction words. The ordinary return at `00049582` is outside
stock spans. Separate static dispatcher checks at `0004952c/0004952e` do not
execute the dispatcher or quiet predicate. Complete coordinator modes,
cadence, producer lifecycles and hardware behavior remain outside this proof.

## Knock timing-byte conversion

`jk08a-knock-timing-byte` binds 16 stock instructions, 48 bytes and 65650 cases.
The cases comprise all 65536 low words and 114 literal cases with independent
upper words. Entry `0004964a` sign-extends the incoming R2 low word to R12;
the delay-slot store publishes the raw word to `ffff121a`. The sign-dependent
255 adjustment and logical shift/reconstruction publish the signed byte
`trunc0(int16(ffff121a)/256)` to `ffff22fa`.

The two R9 anchors and their pools bind the explicit `ffff22f8` base without
executing its producers. Pool `000496c8` is the sole high-RAM alias. The return
boundary at `000496da` lies outside tested instructions. Per-case checks cover
outputs, neighbors, all general/special registers, T, SP/PR, the complete
52-byte frame, independent caller ABI and calibration/context anchors.

Every literal case checks all other 64k RAM bytes. Full RAM is observed at each
256-case sweep block boundary; the sweep does not assert full per-case RAM
observation, and compensating writes within a block remain outside snapshot
coverage. Both fixed stock stores have checked bases and outputs. Complete
coordinator modes, preceding calculation, cadence and hardware behavior remain
outside the bounded conversion proof.

## Knock threshold comparison

The registered JK08A comparison fixture reconstructs 314 instructions and
binds 963 bytes. Its 1100 cases contain 1048 comparisons and 52 direct shift
contexts. The comparison executes the natural threshold accessor and its real
word-axis, divider and linear helpers before the strict unsigned predicate
`metric > 0x80000000 + threshold`. Equality clears the condition. Selected
channels are `1..6`; metric production and the caller's channel-zero guard are
outside the bounded entry.

Status bit 6, the local byte at SP+12, the selected bitmap bit and the saturated
event count are checked independently. Legal shifts `0..5` execute the real
bitmap helper; isolated cases cover `6..7`, negative counts and counts `>=32`.
Positive shift counts `8..31` are outside this executable envelope. Stock and
artificial mode-byte contexts, every legal channel, strict predicate edges and
count boundaries retain separate literal expectations.

Eight high-RAM pool words alone are aliased. Cases check the full remaining
RAM, sibling metrics and thresholds, calibration, a 52-byte frame and distinct
fragment/C-ABI observations. Nested saved words include the wrapper/linear
tail slot, which holds the left cell on descending paths. The boundary at
`0x0004A386` restores driver PR from SP+16 through R1 outside tested code.
Reference learning, complete evaluator dispatch, physical timing and hardware
behavior are separate from this proof. The detailed contract is in
[`JK08A.knock-detection.md`](../../defs/JK08A.knock-detection.md).

## Optional exact PC observation

`Dockerfile.pctrace` builds a separate GNU16.3 simulator with a small host-only
observer. The default Dockerfile, runner and registered firmware gates retain
their existing contracts. The observer records the fetched instruction word
at its actual PC, including the actual delay-slot PC. It does not alter guest
registers, operations, memory, ROM or fixture bytes, and successful observation
preserves host errno. Observation is disabled unless explicitly requested.

The source archive is GNU's official
`https://ftp.gnu.org/gnu/gdb/gdb-16.3.tar.xz`, SHA256
`bcfcd095528a987917acf9fff3f1672181694926cc18d609c99d0042c00224c5`.
Use its existing ignored directory as the named `gnu-source` build context;
do not commit the archive or extracted tree. The recipe checks that archive,
the reviewed patch, and both pristine and modified `sim/sh/interp.c` digests.
It retains and compares the original assembler, compiler and simulator binary
digests while adding `/opt/gnu-sh-trace/bin/sh-elf-run`.

Build the primary stock image by its existing recipe, then build the separate
optional image from the repository root. Set `GNU_SOURCE_DIRECTORY` to the
existing directory containing the exact `gdb-16.3.tar.xz` archive.

```bash
docker --context default build \
  --build-context "gnu-source=$GNU_SOURCE_DIRECTORY" \
  --build-arg STOCK_IMAGE=vq-sh-elf-run:16.3 \
  -f tools/sh-elf-run/Dockerfile.pctrace \
  -t vq-sh-elf-run:16.3-pctrace .
PC_IMAGE_ID=$(docker --context default image inspect \
  --format '{{.Id}}' vq-sh-elf-run:16.3-pctrace)
```

Use the immutable ID for every validation command and preserve the resulting
reports in ignored output directories. Create each output directory empty
before its command; the tools refuse an occupied retained directory.

```bash
mkdir -p tmp/pc-observation/probe tmp/pc-observation/bfs
docker --context default run --rm --network none \
  --mount "type=bind,source=$PWD,target=/workspace,readonly" \
  --mount "type=bind,source=$PWD/tmp/pc-observation/probe,target=/observation" \
  --entrypoint python3 "$PC_IMAGE_ID" \
  tools/sh-elf-run/probe_pc_observation.py \
  --image-id "$PC_IMAGE_ID" --output /observation
```

The probe independently assembles the stock seven-instruction signed helper
at `0x000224fa`, binds its bytes to the SHA-locked JK08A ROM, and requires two
exact ordinary/return/delay PC sequences. Original simulator, observation
disabled, filtered observation and unfiltered observation must produce the
same values and errno result. Ten malformed or unwritable requests must stop
with exit 125. The report records the immutable image ID supplied by the host,
the actual simulator and linked ELF digests, and the trace digests.

Before using observations from an image as an assertion, run the complete
primary repository-contained GNU gate in that same image:

```bash
docker --context default run --rm --network none \
  --mount "type=bind,source=$PWD,target=/workspace,readonly" \
  "$PC_IMAGE_ID"
docker --context default run --rm --network none \
  --mount "type=bind,source=$PWD,target=/workspace,readonly" \
  --mount "type=bind,source=$PWD/tmp/pc-observation/bfs,target=/observation" \
  --entrypoint python3 "$PC_IMAGE_ID" \
  tools/sh-elf-run/verify_bfs_pc_observation.py \
  --image-id "$PC_IMAGE_ID" --output /observation
```

The BFS command delegates fixture identity, compilation and all 461 cases to
the primary `stock.run_region` API. It pins the dedicated assembly, harness,
literal case order, named Region contract, native harness bindings and the
invoker's own function block. Unrelated Region or invoker additions remain
permitted. Linked ELF markers and actual wrapper bytes bind the observation
after relocation. Every helper opcode, complete sequence and delay flag must
match stock bytes.

The trace separates 461 caller frames. Literal assertions check 20 correction
contexts and 7 blend contexts individually, covering zero, one and two helper
calls with 38 checked helper entries. The other 434 frames retain observed counts
without count assertions. A whole-run total cannot substitute for these
per-context expectations. Arithmetic outputs, RAM, calibration and ABI checks
continue to belong to the unchanged primary harness.

The observer's opt-in environment is `VQ_SH_PC_TRACE_FILE` plus
`VQ_SH_PC_TRACE_FORMAT=v1`. Optional `VQ_SH_PC_TRACE_RANGES` contains up to 8
comma-separated hexadecimal half-open `low:high` ranges. The tool selects only
the helper and compiled invoker ranges to avoid tracing the C RAM loops.
Unsupported requests, open/write/close errors and zero selected records fail
with exit 125. `pc_observation.py` accepts only raw ASCII bytes, exact LF syntax,
one header, one terminal complete footer, the exact positive record count and
a zero process exit. Pure refusal tests run through ordinary pytest discovery:

```bash
uv run pytest -q tools/tests/test_sh_pc_observation.py
```

This optional observer establishes direct invocation counts under the declared
execution contexts. Hardware eligibility still requires the mandatory byte,
execution and hardware validation contracts. Build logs, source archives,
ELFs, binaries, traces and observation reports remain ignored.

## Bank base-pulse builder

The stock Region `jk08a-bank-base-pulse` executes the complete natural
function at 0004ead4..0004eba2: 103 instructions, 232 bound bytes and
6184 literal cases. The natural RTS and MACL-restoring delay slot remain
exact. Only three high-RAM pointer longwords are simulator aliases; the
ROM pointer and arithmetic constant FFFF3800 remain unchanged.

Both legal bank selectors use independent full R4 upper bits and raw
unsigned16 RAM inputs. The gate covers conditional LTFT inclusion,
both control choices, strict control threshold, lower trim clamp, low32
product, unsigned offset wrap, zero-precursor bypass and cap equality.
Factory and artificial calibration/software contexts remain distinct.
Full machine-domain decreases prevent positive signs in the six shared
chain views.

Each case checks literal output and all fifteen GPRs, final T, complete
observed full SR, natural special-register/PR/SP restoration, distinct
external C ABI, the entire 80-byte frame, every other RAM byte and all
bound calibration/pool bytes. The SR setup retains GNU MD/RB and all
other nonT bits, reads actual SR after LDC, and verifies their preservation.
Stock saved GBR/MACL occupy SP-8/SP-4; capture above SP+32 does not
overlap the SP-48..SP+31 observer.

`defs/JK08A.fuel.md` section `Bounded bank base-pulse builder` owns the
explicit inputs and arithmetic. Named owner and registered-stock
contracts in `tools/kb/tests/test_bank_base_pulse_chain.py` bind this
publication to its actual registered Region, literal array, harness loop
and result marker. Caller dispatch, upstream production, live operating
states, physical units and hardware mapping remain separate evidence.

## Simulator boundaries

GNU `sh-elf-run` cannot map the ECU high-RAM windows. The gate first proves the
original literal bytes, then aliases validated `0xFFFE8000..0xFFFFFFFF` data
literals into a 64-KiB test window by their low 16 bits. Instruction bytes and
control-flow addresses remain unchanged. This covers both the SH7058
`0xFFFFxxxx` application RAM and the SH7059 1ND and 1ME3B `0xFFFExxxx`
application RAM.

HCAN status registers are write-one-to-clear in silicon but ordinary memory in
the simulator. Canonical simultaneous mailbox-26/mailbox-28 ISR cases place the
two flags in independent TXACK1 and ABACK1 words, so both mailbox paths execute
in one TRAPA exception without modifying instructions under test. The 8MFK
and VQ37 tail-chain cases exercise mailbox 26 alone and together with unrelated
stock mailbox-28 flags, then verify the target wrapper's register-preserving
stock-ISR boundary.
Individual ACK and abort cases execute each custom write-one-to-clear
instruction and boundary path. Mailbox-31 cases likewise execute RXPR1, RFPR1,
and UMSR1 writes, including data, remote-only, retained-remote, malformed, and
invalid-configuration paths; the fixture observes the write values rather than
emulating their hardware clearing effect.

The simulator does not model HCAN-II, the SH7058/SH7059 flash controller, or the
external watchdog. The 1.5-MiB target harness places its test driver beyond the
complete ROM image; this relocation affects only harness code, not target
instructions. The npkern marker therefore remains
`hardware_ready=NO`. Repository firmware fixtures also do not emulate the full
ECU, power sequencing, analog inputs, or engine.

Passing this gate proves a bounded software execution contract. It does not
make an image eligible for flashing without static review and the project's
bench, readback, and engine validation gates.

## Adding an instruction-changing patch

The same change that introduces a patch must extend this gate. Its verifier
must:

1. Independently assemble the source or reconstruct declared raw words and
   prove identity with the exact instructions emitted into the ROM.
2. Execute every changed entry and reachable branch outcome, including delay
   slots, call/return paths, failure paths, and relevant boundary inputs.
3. Use distinct fixture values where equal production defaults could conceal a
   wrong address, slot, width, or branch.
4. Declare simulator-only relocations and stock-function stubs, apply them only
   after byte identity, and leave instructions and control-flow addresses under
   test unchanged.
5. Add deterministic host-side tests and make `run.sh` execute the new
   repository-contained check.

A simulator limitation is not a waiver. Until an equivalent executable check
exists, the image remains ineligible for hardware testing.

## Bounded JK08A knock reference learning

`jk08a-knock-reference-learning` executes the complete RAM-only learner
and the real diagnostic predicate through natural stock calls and returns.
The exact-stock envelope binds 132 instructions, 304 bound bytes and
7336 cases: 264 instruction bytes and 40 data bytes, comprising 36 pool bytes and 4 calibration bytes.
The source is `stock_jk08a_knock_reference_learning.s`; a separate
`stock_knock_reference_learning_invoke.s` enters through the shared
invoker. The original literal result marker matches the Region key and
case count. Guest instructions, branch/delay slots and result text retain
their reconstructed bytes.

The ordered KB definitions supply the reference bank, unsigned sample
vector, two channel bytes, diagnostic-record base, selector byte, weight
byte and reset word. Five validated RAM pool words are aliased after
independent GNU byte comparison. The real predicate address, all other
pool values and calibration bytes retain stock identity. The fixture
uses no stock-function stub or synthetic boundary return.

The matrix contains 5256 normal learning cases, 540 forced reset cases and 1540
direct predicate cases. There are 5796 natural learner calls.
Stock calibration supplies 2015 stock normal cases and 18 stock forced cases,
totaling 2033 stock natural cases. The normal legal
channel domain is 1..6 with eight uint16 samples/old words and byte W.
The coefficients W and 255-W divide by 256; only q<old adds one.
The complete domain has q<=65279 and result<=65280, so it cannot take
the final upper clamp. Forced reset publishes the raw reset word to all
48 reference words across six rows. Artificial calibration cases remain
distinct from stock contexts.

Each case checks all fifteen GPRs, actual final SR.T, special registers,
natural SP/PR, a distinct external C ABI and the 80-byte observed frame
around the 36-byte natural save footprint. All 64k aliased RAM and all 40 bound
pool/calibration bytes are checked. Normal learning permits only the selected
16-byte reference row to change; forced reset permits the 96-byte reference bank; direct
predicate calls permit no RAM changes. Independent expectations cover
all 42048 normal output words and all 7336 register/flag vectors.
SR is not injected and non-T preservation is outside this fixture.

The two real diagnostic ids are 012d and 013f. Both bit7 outcomes,
short-circuit/reset branches, all record bytes, independent R4 upper
words and the low-word-ffff sentinel are covered. Static acquisition and
caller anchors remain separate from this execution. Other signed diagnostic
indices, complete record-array extent and hardware behavior are outside
this bounded proof. Physical sensor and
channel identity, diagnostic producers, acquisition, timing, engineering
units and full evaluator dispatch are not established by the bounded
RAM-only proof. The narrow mechanism contract is
`defs/JK08A.knock-detection.md#bounded-knock-reference-learning`.

## LTFT publication

The registered GNU16.3 Region jk08a-ltft-publication executes the
complete publisher at 57B26 with its second span at 57BD4..57C34 and real
predicate at 25E20..25E44: 108 instructions, 268 bound bytes and
12028 literal cases. Natural RTS/delay slots remain stock. Eight
high-RAM longword pools are aliases; the three words, both ROM pointers
and real helper pointer remain unchanged. The fixed caller uses id 0129;
the predicate sentinel branch/MOV at 25E3E is identity-only, with no
direct sentinel or independent helper upper-word execution claim.

Both legal banks use full incoming R4 with varied upper bits, independent
uint16 selected/adjustment words, full byte controls and unsigned U versus
signed V. The exact uint32 sum, both limit bypasses, active lower-then-upper
comparisons and all four neutral causes have independent expectations.
Stock and artificial/reversed bounds remain distinct. Full-domain
underflow and low-word wrap prevent broad positive signs in the two
shared publication views.

Each case checks output bytes, all fifteen GPRs and final T, full prepared
SR nonT preservation, natural special registers/PR/SP, distinct external
C ABI, all other RAM bytes and all 52 data bytes. The 80-byte observer
uses matching SP-48..SP+31 origins, with natural R13/R14/PR saves at
SP-4/-8/-12. Independent continuation and capture above SP+32 are
separate checks. RAM/data snapshots are per literal, without block
aggregation; an arbitrary full incoming SR=0/1 is not claimed.

The specification section Bounded LTFT publication defines inputs and
arithmetic. The mandatory contracts test_ltft_publication_chain_owner_contract
and test_ltft_publication_registered_stock_contract in
tools/kb/tests/test_ltft_publication_chain.py bind the exact Region, stock
bytes, independent literal output/T/GPR vectors, typed conditions, scoped
widths and Region/header-array/C-loop publication counts. Missing owners,
registration, header or publication sections fail these contracts.
The shared predicate retains its separate knock-reference direct-context
proof; those cases belong to that fixture and are not LTFT case counts.

Each legal bank has 6014 cases. Each incoming T value has 6014 cases.
There are 8564 factory-bound and 3464 artificial-bound contexts.
The envelope has 216 instruction bytes and 52 bound data bytes.

    raw = uint32(L+A-25600)
    active = ((M&(b+1))==0) and (U>V)
    limited = min(hi,max(lo,raw)) if active else raw
    neutral = diagnostic_byte1.bit7 or F.bit0
              or (G.bit0 and H.bit1) or (K.bit6 and H.bit0)
    output = 25600 if neutral else uint16(limited)

All held notes/properties/evidence and ledger selectors, existing units,
producer interpretations and other layouts are preserved. Caller dispatch,
upstream producers, physical mapping, percentages, timing, live-state
reachability, complete coordinator execution and hardware behavior remain
separate evidence.

## Injection start-delay publication

`jk08a-injection-start-delay` binds 404 instructions, 871 bound bytes, and
6855 literal cases for the natural `521a8` publisher and real `21bbc/21e14`
quotient/remainder helpers. Its envelope contains 808 instruction bytes and
63 data bytes. Nine high-RAM aliases relocate pool addresses while preserving
the instruction bytes, numeric constants, ROM and helper targets. Natural
calls and returns execute with `boundary=False`.

The first selected-speed product retains its uint32 wrap. Full unsigned16
speed, pulse, floor, and end words produce a nonnegative delay; control bit 5
enables a clamped unsigned-byte decrement. Division by 120 yields a quotient
stored through uint8, a clamped remainder byte, and a separate bit-0 forced
value 3. The 32-case control/T/register cross-product covers all eight relevant
bit combinations. The matrix includes 5446 primary and 1409 alternate speed
contexts, 4446 short and 2409 long helper paths, all 120 remainders,
5610 stock and 1245 artificial calibration contexts. The zero-numerator path
executes 1304 times. Invalid helper domains, sign correction, and the main
negative-angle adjustment are identity-only.

Each case checks both result bytes, all fifteen GPRs, actual full SR, natural
PR/SP, GBR/MACH/MACL, every other 64k RAM byte, all 63 data bytes, a 96-byte
frame at `SP-64..SP+31`, and a separate external C ABI snapshot. The prefix
preserves MD/RB, injects T, clears M/Q explicitly, and records actual prepared
SR. Frame origins agree and the exit capture begins at SP+32.

Two unconditional contracts require canonical owners, the registered Region,
exact execution sources, count bindings, and the three arithmetic-only chain
steps with sign `none`. Single-byte mutations are refused across the complete
bound envelope. The unsigned ROM83EA scalar states this conditional consumer.
Physical units, peripheral producers, complete scheduling, and hardware
behavior retain separate evidence requirements.

## Bounded injection result snapshot

The caller slice `00021314..0002131a` and its real byte-copy helper
`00022558..0002258e` bind 32 instructions, 72 bound bytes and
1700 literal cases. Entry registers are explicit: R11=00022558 and
R12=140. The two original pool words identify source `ffff23bc` and
destination `ffff2330`. The natural JSR delay slot supplies length 140.
The helper copies in ascending byte order, checks the limit after each
byte, and returns through its stock RTS and R2-restoring delay slot.
Only the two high-RAM data pointers are aliased for the simulator.

The copy places `ffff23f0 -> ffff2364` at offset 52 and
`ffff23bf -> ffff2333` at offset 3. Native `injection_phase`
steps 13 and 14 state `to = uint8(from)` through the ordered caller and
real helper. The sign is `positive` for the unsigned-byte source domain.
The 6 arithmetic records bound by the publisher and copy fixtures
comprise four publisher records and these two copies. They establish no physical scale
or upstream production claim.

The matrix contains 1024 affine caller contexts, 280 isolated-byte caller contexts,
384 direct helper contexts, and 12 successive caller contexts.
Every source position in the affine contexts takes all 256 byte values.
The isolated contexts exercise each of the 140 source positions independently.
Direct calls cover lengths 0, 1, 2, 3, 4, 5, 6, 7, 139, 140, 141 and 255,
all sixteen source/destination alignments, and both incoming T values.
Two register contexts cover both caller T values. Successive contexts
retain the preceding RAM state. A twelve-case preliminary matrix includes
the caller and every early helper exit before full execution.

Every case checks all fifteen GPRs, complete SR relative to the recorded
prepared SR, MACH, MACL, GBR, PR/SP, the immutable 76-byte input context,
the complete 96-byte frame, all 64k RAM bytes, both pool words, and an
independent external C ABI snapshot. Source and neighboring RAM bytes
remain unchanged; only the declared destination bytes receive source bytes.
The helper saves R2/R3/R4 even on its zero-length path.

The simulator boundary at `0002131c` restores PR from SP+24 using R7,
then returns outside all tested instructions. The caller's observed R7
therefore holds the boundary continuation; this is not a stock R7-preservation
claim. Direct helper calls retain incoming R7 and use the natural return.
The existing shared invocation prefix clears M/Q, sets entry T, and preserves
the other observed SR bits. Separate static bytes identify the upstream
R11 helper pool and the R12 length preparation; the executable slice begins
with explicit input registers. Complete scheduler execution, live cadence,
other copy calls, overlapping-source domains, hardware atomicity, and
hardware readiness retain separate evidence.

## Bounded injection slot construction

The bounded `00054a64..00054ac6` slice binds 50 instructions,
152 bound bytes and 8508 literal cases. Entry contexts are R2=255,
R5=ffff8510, R14=ffff4555 and GBR=ffff1ff4. Four RAM literal aliases
and the corresponding incoming base-register aliases place high RAM in
simulator memory after exact instruction identity. The original 52 pool
and order-table bytes are bound. The entry-preparation bytes at
`00054a56..00054a62` retain static identity; the prologue is not executed.
An appended RTS/NOP at `00054ac8` returns outside the stock slice.

The cylinder input c is an unsigned byte in 1..6. Two fixed stock ROM
lookups at `0002268e` and `0002269b` yield c in this domain. Counter
`ffff4555` saturates at 255. History `ffff1526` ORs `1<<(c-1)`.
Control byte `ffff8513`.bit5 selects unsigned lead `ffff2364` or constant 3.
The negative difference receives one addition of 6 before byte storage.
Cylinder 1, lead 7 and bit5 set stores 255; mathematical modulo-6 yields 5.
For a given c, lead <= c+5 makes the stored byte equal modulo-6 in 0..5.
The uniform bound lead <= 6 covers all six legal cylinder inputs.

The 2 arithmetic records at native injection_phase steps 15 and 16
bind lead and cylinder inputs to slot `ffff20b4` through the sequencer.
They use sign `none` and the exact bounded expression:

```text
F = (uint8(ffff8513)>>5)&1; L = F*uint8(ffff2364)+(1-F)*3; d = uint8(ffff11de)-1-L; to = uint8(d+6*min(1,max(0,-d)))
```

The matrix has 12 early contexts, 6144 enabled-lead contexts,
48 disabled-lead contexts, 2048 full-control-byte contexts and
256 counter-byte contexts. Enabled lead covers 0..255 for each legal c,
both incoming T values and two complete GPR variants. Control contexts
cover all 256 raw byte values, including other bits and sign extension.
Counter contexts cover every byte and both saturation branch outcomes.
EARLY_ONLY=1 executes the first twelve literals; the mandatory Region
uses EARLY_ONLY=0 and requires the complete declared count.

Each case observes all fifteen GPRs, actual prepared complete SR/T,
MACH, MACL, GBR, PR/SP, the immutable 76-byte context, all 96 frame bytes,
an independent outer C ABI, all 64k RAM bytes and every bound ROM byte.
Only counter, history and slot stores may change RAM. This slice has no
stock call, MMIO access or internal frame write. The shared invocation
prefix preserves its accepted instruction bytes and its SR preparation.

Full-byte lead values are explicit consumer contexts. Complete prologue
and tail behavior, upstream producer bounds, live scheduling, physical
cylinder identity and hardware reachability require separate evidence.
This proof does not establish that lead values above six occur in service.

## Bounded injection pending-mask selection

The accepted lookup and two selection entries bind 32 instructions,
80 bound bytes and 9216 literal cases. The direct lookup at
`00054d06..00054d0a` requires slot 0..5 and reads the six stock masks
`02 04 08 10 20 01` at `00022695`. Entry `00054bdc` supplies the
zero-lead-delta context: it clears pending byte `ffff2228`, computes the
next cursor as old cursor+1 below 5 and zero otherwise, and accepts only
a matching target slot. Acceptance stores the cursor and the looked-up
mask. Entry `00054c0e` supplies the negative-lead-delta context and clears
only the pending byte. The boundary at `00054d0c` is outside all three
stock spans; its RTS/NOP adds no sequencer semantics. One RAM literal
and incoming GBR/R14 alone use simulator RAM aliases.

The matrix contains 12 early contexts, 6144 valid-slot zero-delta contexts,
1500 invalid-slot contexts, 1024 negative-delta contexts, 24 accepted
direct lookups and 512 full-cursor extreme-invalid-slot contexts. The
zero-delta and negative-delta inputs cover complete unsigned byte domains;
direct lookup contexts keep the necessary valid table-index bound.
Earlier mode gates and earlier mode exits, positive-delta catch-up, stock
calls and MMIO are outside these spans. Native step 17 retains a separate
complete-selection question; this fixture does not assert that every
sequencer path without an accepted slot clears pending.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection reciprocal splitter

The complete `00028e7c..00028e9c` helper binds 17 instructions,
36 bound bytes and 12826 literal cases. It takes a full unsigned 32-bit
input M in R4 and independent word and byte output pointers in R5/R6.
The ROM word `00028ea0` is 6554. The actual operator is
`Q=floor(uint32(6554*M)/65536)` with word Q and byte `uint8(M-10*Q)`.
There is no saturating quotient cap. Both quotient-zero branch outcomes,
the word store in its BT/S delay slot, and the natural return with MACL
restoration in its delay slot execute. No literal or instruction alias
is needed. Prepared output pointers are explicit helper contexts; this
generic fixture does not identify all callers' destinations.

For M in 0..255, Q equals floor(M/10). Larger operands can differ through
reciprocal precision and low-32-bit wrap. The early M=200000 context
executes Q=20001 and residue byte 246. The matrix contains 12 early
contexts, 2816 coarse word-period products, 9450 product-wrap seam
contexts, 512 complete unsigned-byte/T contexts and 36 raw-32-bit corners.
All byte-valued remainders contribute wrap-seam boundaries where present.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection argument splitting and phase normalization

The caller at `0002b660..0002b6cc`, its complete phase normalizer at
`00028dc8..00028e7a` and its real reciprocal splitter bind 162 instructions,
350 bound bytes and 12668 literal cases. A=uint8(R4) executes in the
BT/S delay slot on both mode-bit6 outcomes. With bit6 clear, byte-domain
division by ten is exact: initial count is max(0,floor(A/10)-1), and
remainder is A%10 plus ten when the quotient is nonzero. The normalizer
reads raw position byte `ffff13b2` and writes count word `ffff13b8` and
remainder byte `ffff193b`. With bit6 set, A<120 stores count zero and
remainder A; other byte values store count one and remainder A-120.

At position 4 the normalizer maps count 4 to 3 with remainder+10, 5 to 3
with remainder+20, and 6..15 to count-2. At position 9 it maps 9 to 8
with remainder+10 and counts >=10 to count-2 with remainder+20. Other
raw position bytes map 1 to zero with remainder+10, 2 to zero with
remainder+20, 3..12 to count-2, 13 to ten with remainder+10, 14 to ten
with remainder+20, and 15..24 to count-4. Other counts are unchanged.
Byte additions keep uint8 storage while scratch GPRs retain signed
byte extension. This full raw consumer domain does not expand the
physical tooth domain.

The matrix contains 12 early contexts, 2560 normal byte/valid-position
contexts, 1536 fallback contexts, 3328 complete raw-position contexts,
1536 complete control-byte contexts, 288 upper-argument-bit contexts,
32 direct clamp contexts and 3376 direct normalizer contexts. The direct
clamp supplies entry `0002b676` to cover the signed clamp unreachable
after byte truncation. The normalizer uses its natural return. Caller
entries return through a PR restore at stack offset 24 in a boundary
at `0002b6ce`, with R11 as scratch outside the stock bytes. Three RAM
pool words alone are aliased. The prologue, source-argument dispatch,
preceding pending flag and following count decision and MMIO retain
separate evidence. Native step 18 requires composition with those
caller conditions before it gains a complete arithmetic record.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection offset multiplication

The `0002b6d4..0002b6f6` multiply and its complete real reciprocal helper
bind 35 instructions, 90 bound bytes and 14118 literal cases. The caller
reads unsigned period word `ffff22bc` and remainder byte `ffff193b`.
It computes M=P*R and passes the actual word output `ffff16c2` and byte
output `ffff166c` to `00028e7c`. The word is Q and the byte is
uint8(M-10*Q). MACL contains M after the helper restores its saved input;
it does not preserve the MACL value before the caller's multiplication.

Native injection_phase step 19 has sign `none`, includes the ordered
caller and real helper, and binds the exact bounded arithmetic:

```text
M = uint16(ffff22bc)*uint8(ffff193b); to = floor(uint32(6554*M)/65536)
```

P=8192,R=4 executes Q=3277 while ordinary division gives 3276.
P=25000,R=8 executes Q=20001 and byte 246. Across full word/byte
consumer contexts the reciprocal product wraps and Q can decrease
when an operand increases. The raw residue is not limited to 0..9.
The matrix contains 12 early contexts, 3328 coarse word/byte products,
9450 wrap-seam contexts, 1280 complete-byte contexts at five word values,
and 48 word-corner contexts. Two declared RAM literals alone are aliased.
The boundary at `0002b6f8` restores PR from stack offset 24 using R11
outside all tested bytes. The preceding zero-count decision, compare
programming, physical timer units and hardware retain separate evidence.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection positive-delta mask accumulation

The loop at `00054c54..00054cc6` binds 58 instructions,
138 bound bytes and 11340 literal cases. Its input N=uint8(R6) is a
prepared register context. For N=0 it leaves all RAM unchanged and writes
zero at SP+12 and SP+16. For N>0 each iteration increments the raw cursor
byte `ffff221e`, wraps a resulting byte >=6 to zero, and reads the mask
`02 04 08 10 20 01` at `00022695+cursor`. The final cursor is
`(min(old_cursor,5)+N)%6`. The accumulator ORs the next min(N,6) masks;
N>=6 produces 0x3f. It ORs that accumulator into `ffff20b5`, `ffff157e`
and `ffff16fe`, and clears its bits in `ffff1935`. Upper byte bits in the
four history values are preserved. Signed MOV.B scratch registers retain
their actual full GPR values before unsigned byte storage.

For N>0 the loop saves incoming R9 at SP and restores it, stores N at
SP+12 and stores the accumulated mask at SP+16. Other frame bytes are
held. The boundary at `00054cc8` uses an RTS/NOP outside the stock span.
The two RAM literal bases alone use simulator aliases; incoming R8 is
the stock table base `0002268e`, and incoming GBR is the declared RAM
alias of `ffff1ff4`. ROM instructions, masks and offsets are unchanged.

The matrix contains 12 early contexts, 7168 full-cursor and selected-delta
contexts with both GPR patterns and entry T values, 3072 full-delta
contexts over all six valid cursor values and two GPR patterns, 1024
independent full-byte history contexts and 64 upper-delta-bit contexts.
Every cursor byte and low delta byte occurs. N=0, loop completion,
cursor wrap, repeated complete cycles and both incoming T values execute.
The native owners describe unsigned byte storage and the exact bounded
writer. All 22 complete steps of injection_phase retain their current
bindings. The preceding mode/lead decision, later flag and duration-helper
paths, pending-mask publication, one-shot call, physical channel mapping
and hardware retain separate evidence. These raw direct contexts do not
establish service reachability or the full step-17 selection conditions.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires every literal. Each case observes all fifteen GPRs,
actual complete SR including T, MACH, MACL, GBR, PR/SP, the immutable
76-byte entry context, all 96 frame bytes, a separate twelve-word outer
C ABI, all 64k RAM bytes and every bound ROM pool byte. The original
shared invocation and pinned GNU tools execute the fixture.

## Bounded injection pre-call argument preparation

The mandatory `jk08a-injection-dispatch` Region reconstructs 12 instructions,
38 bound bytes and 9292 literal cases with `EARLY_ONLY=0`. It enters at
00054d0c and observes at 00054d24 before JSR to 0002b64a. The byte at
ffff221d receives uint8(R9). Bit 0 of ffff4251 selects argument 52 when set
and the complete 32-bit word at SP+8 when clear. Other flag bits are retained;
the MOV of 52 executes in the BRA delay slot. R2 holds the stock callee
address at the boundary. Further callee execution has separate evidence.

The stored-word domain includes 4*A for every byte A in 0..255, independent
upper-word contexts and both prepared T values. These are explicit entry
inputs; earlier producer and mode conditions retain their own proof. The
matrix contains 12 early cases, 4096 full-flag cases, 4096 byte-snapshot-word
cases, 1024 previous-lead cases and 64 upper-word cases. Every flag byte and
every previous lead byte is covered. The direct contexts do not establish
caller reachability or all combinations of 32-bit arguments and lead values.

The harness checks all fifteen GPRs and the actual complete SR, MACH, MACL,
GBR, PR/SP, the immutable 76-byte context, 96 frame bytes, an independent
12-word C caller ABI record, 64k RAM and every bound ROM-pool byte. R11 is
the explicit boundary scratch and equals the independently recorded driver
continuation. Fourteen other GPR results bind to the literal matrix. The
frame and RAM checks permit only the stock lead-byte write. The input flag,
saved argument, neighboring frame bytes and other RAM retain their values.

`stock_injection_dispatch_invoke.s` preserves the complete start-delay
observer after a symbol rename and two setup instructions. Those instructions
copy the explicit incoming R4 word into SP+8 before the before-frame capture.
The contract normalizes that insertion and compares the complete remaining
source with `stock_injection_start_delay_invoke.s`. Mutation checks reject
each register result, each bound byte, changed setup offset/source, missing
frame capture, changed Region boundaries and conflicting published counts.

Simulator RAM aliases affect only the declared words at 00054e8c and
00054e9c. The existing boundary stub at 00054d24 loads its continuation
from SP+24 through R11; the interval under test retains its exact ROM bytes.
The pinned GNU tools, image, runner and timeouts remain the standard gate.
The boundary precedes hardware compare and timer accesses; software proof
of argument preparation leaves hardware validation as a separate condition.

## Bounded injection count decision and saved-frame return

The mandatory `jk08a-injection-count` Region reconstructs 44 instructions,
108 bound bytes and 10252 literal cases with `EARLY_ONLY=0`. It enters at
0002b6ce, reads the stored unsigned word ffff13b8 through GBR and tests zero.
MOV.W sign-extends the scratch R0; that sign does not affect the zero test.
Count zero executes M=uint16(ffff22bc)*uint8(ffff193b), followed by the real
00028e7c reciprocal splitter: Q=floor(uint32(6554*M)/65536), word ffff16c2=Q
and byte ffff166c=uint8(M-10*Q). Observation at 0002b6f8 is before MMIO.
The reciprocal formula preserves 32-bit multiplication wrap and byte residue
truncation; exact division by ten does not describe every input context.

Nonzero count branches to the real saved-frame epilogue 0002b74a..0002b754.
It restores the explicitly staged GBR, MACL, PR, R14 and R13, including R13
in the RTS delay slot, and returns with SP+20. All RAM bytes are preserved.
The staged frame is an explicit direct-entry input. The original prologue,
validity of that frame as its product, earlier producers, actual dispatcher
invocation and complete caller composition retain separate evidence.

The matrix contains 12 early cases, 4096 count-word contexts, 4096 period-word
contexts, 1024 remainder-byte contexts and 1024 independent upper-count-byte
contexts. Both count-byte positions cover 0..255 independently; every period
low byte, remainder byte and both prepared T values are covered. These domains
do not claim all 65536 count words, a full Cartesian product or caller reachability.

The harness checks all fifteen GPRs and the actual complete SR, MACH, MACL,
GBR, actual PR/SP, the immutable 92-byte context, 96 frame bytes, an independent
12-word C caller ABI record, 64k RAM and every bound ROM-pool byte. R11 is
the declared scratch of the zero-path boundary and equals its recorded
continuation; the nonzero path preserves its incoming value. Saved GBR and
MACL differ from their incoming values, and saved R13/R14 are independently
seeded. The zero path permits only the offset word, residue byte and the real
splitter's saved-MACL frame word to change. The nonzero path permits no RAM
or frame change. The observer records actual returned SP before compensation.

`stock_injection_count_invoke.s` retains the complete start-delay observer
after normalization of symbol names, the declared frame allocation, saved-frame
setup, two return-capture sequences, actual-SP capture and continuation pointer.
Its entire normalized source equals `stock_injection_start_delay_invoke.s`.
Contracts bind every execution input by SHA-256 and reject changed registers,
saved state, every bound byte, missing reader evidence, altered chain description,
changed Region boundaries and conflicting published counts. The dispatch input
contract binds the shared invocation source including the count observer.

Simulator RAM aliases affect only the declared words at 0002b864 and 0002b874.
The standard boundary stub at 0002b6f8 reads SP+24 through R11. All instructions
under test retain their exact ROM bytes. The pinned GNU tools, image, runner
and timeouts are the standard gate. MMIO and hardware behavior have separate
validation conditions.

## Bounded injection programmer entry frame and byte flag

The mandatory `jk08a-injection-prologue` Region reconstructs 11 instructions,
28 bound bytes and 1036 literal cases with `EARLY_ONLY=0`. It enters at
0002b64a and observes at 0002b660 before the argument and mode calculations.
The five saved words are R13, R14, PR, MACL and GBR, pushed in that order;
actual SP-20 and every saved byte are observed before stack compensation.
The natural JSR continuation is saved PR. The long pool at 0002b864 loads
GBR from ffff128c. The exact word 0002b75c=84ec sign-extends to ffff84ec;
MOV.B loads that byte with sign extension, OR 0x80 sets bit 7 and MOV.B
stores the low byte. R0 retains the sign-extended byte OR 128; T is held.

The matrix covers every byte 0..255, two independent complete register
contexts and both prepared T values, plus 12 early cases. The harness checks
all fifteen GPRs, actual complete SR, MACH/MACL, loaded GBR, actual PR/SP,
the immutable 76-byte input context, 96 frame bytes, an independent 12-word
C caller ABI record, 64k RAM, all six pool bytes and sixteen low-alias bytes.
Only the alias byte's bit 7 and the five saved words may change. The complete
high-RAM test window and every neighboring low-alias byte are retained.

The declared simulator binding (0002b75c, ffff84ec, 0x7f00, 1) relocates only
the pointer's two pool bytes. Its original sign-extended target lies in the
configured MCU RAM domain. The positive signed-word alias and its extent
must fit the image, avoid all tested code, pool data and return boundaries,
and avoid repeated pool words or overlapping aliases and original RAM
extents. A simultaneous long-literal binding to the same original address
is refused. The long pointer alone maps to 0x0100128c. Every instruction
under test retains its stock bytes. Two padding bytes before the two-byte
aligned entry are outside the reconstructed code and preserve PC-relative
longword alignment. The boundary is the ordinary RTS/NOP pair.

The complete normalized observer equals the start-delay observer after the
declared allocation and actual-SP capture insertions. Every old Region's
complete declaration and simulator fixture remain exact with the empty
RAM-word binding default. The GNU image, tools, runner and timeouts are the
standard gate. Storage width is eight bits; the physical flag meaning,
following mode/delta selection, count/remainder composition, real dispatcher
invocation, whole-function return, MMIO and hardware retain separate evidence.

## Bounded channel pulse calculation and word snapshot

The mandatory `jk08a-channel-pulse` Region reconstructs 184 instructions,
423 bound bytes and 14132 literal cases with `EARLY_ONLY=0`. The complete
natural builder enters at 0004eba2, executes its second span at 0004ec24,
calls the real arithmetic-shift path 000224f8 and affine helper 0005b7ec,
and returns through its own RTS and delay slot at 0004eca8. The admitted
argument is uint8(R4)=i in 0..5; independent higher argument bits are retained.

A set aggregate inhibit bit i selects the unsigned opening word ffff2436
for both channel vectors and bypasses both helpers. Otherwise parity selects
ffff191c or ffff191e, adds signed16 ffff1396+2*i and conditionally subtracts
signed16 ffff1466+2*i under ROM8[8d92].bit3. A positive intermediate multiplies
unsigned ROM8[129c0+i] and shifts seven bits; nonpositive values become zero.
The compensated result is capped at 65535 and stored at ffff23c8+2*i.
The affine result at ffff23d4+2*i is the maximum of that input and two
independently saturated branches, each floor(uint32(a*x+100*b)/16384).
The four unsigned coefficients a,c,b,d occupy 91da,91dc,91de,91e0; exact
stock words are 3558,4000,109a,0000. All six exact stock multipliers are 0x80.
The second stock branch equals the input; artificial unsigned calibration
contexts execute separate branch saturation and low32 sum-wrap outcomes.
The generalized transformed relation uses `sign = "none"` because a wrap
does not establish global monotonicity.

The existing mandatory `jk08a-injection-snapshot` caller at 00021314 copies
the unsigned words ffff23d4+2*i to ffff2348+2*i through the real 140-byte
helper 00022558. Both vectors start at byte offset 24 of source ffff23bc and
destination ffff2330. Explicit R11=00022558 and R12=140 entry contexts and
the complete per-byte RAM checks bind this word relation. The copy does
not establish full scheduler execution, live cadence or hardware atomicity.

The shared copy witness captures this region through
`harness-injection-snapshot-capture.c`, retaining the original checked harness
and independently reconstructed caller/helper bytes. The host independently
generates the complete 1700-case matrix, validates actual entry/exit registers,
special registers, ABI, frame, pointer pools and full admitted memory effects,
and binds consumed sources, ELF, fixture and toolchain identities. The two RAM
pool relocations and SP+24/R7 return boundary are explicit simulation changes;
instruction bytes under test remain original. Twenty exact native reader/writer
claims can receive identity support through the schema-3 shared copy receipt.
Existing declared widths, signedness and relation slot/offset remain unchanged.
Full qualification uses the existing primary `--can-copy-witness` path and its
independent finalizer. `--injection-copy-early` executes twelve fixed cases only,
emits raw observations and supplies no production receipt or native acceptance.
Related TEST attachments require separate qualification.

The bounded coherent-caller descriptor is `defs/JK08A.coherent-copy.toml`.
The matrix declares 17228 cases and the fixed feedback selects 109 cases across
15 callers. `--coherent-copy-early` executes that selection through the primary
runner. Each caller uses a separate reconstructed ELF and an SP+24/R7 return
boundary outside its tested bytes. The host checks actual registers, SR,
PR/SP, ABI, seeded stack, all source and history lanes, pointer/dispatch pools
and the complete external RAM footprint. The length-88 and length-128 paths
include their source+length word read; their compact dispatch table is outside
the admitted path. The primary stock loop executes all fifteen complete windows
and the existing shared COPY packet binds their ordered observations, native
claim scope and private consumed sources. The independent finalizer requires
every complete window; early feedback cannot publish a receipt or qualify
a native claim. The reserved coherent-copy item supports exact identity only.
The formulas occupy fuel_pulse steps 20, 21, 22 and 23; all other fuel and
injection steps retain their independent contracts.

Four bounded windows belong to scheduler 000209D8 and bind fourteen exact
native reader/writer appends. Calls 00020BD0, 00020CBA, 00020CDC and 00020CE6
retain lengths 24, 8, 8 and 16 from their actual delay slots. The length-24
dispatch reads stock pointer 00022170 to 0002213E. Explicit incoming pointer
and helper registers define each bounded entry; scheduler reachability is
outside this claim. The 00020DFE and 000209D8 relations of the three shared
reader owners are selected by exact caller and evidence, rather than address
alone. The existing unique exact publication rule covers all registered
owning items; other facts and evidence retain their scope effect. Native
width/signedness, complete ledgers and every TEST position stay fixed. The
standard source generator writes both the input header and descriptor from
the pinned member/window declarations and owned image; it runs no MCU path.

The numeric harness checks all fifteen GPRs, actual complete SR, natural
PR/SP, restored MACH/MACL/GBR, the immutable 76-byte entry context, 96 frame bytes,
the independent C caller ABI, 64k RAM and all 55 bound pool/calibration bytes.
The aggregate bypass and both real calls include exact saved and local words.
Only the selected compensated and transformed word writes may change RAM.
The simulator relocates exactly the three declared long RAM pools to matching
low16 offsets in 0x01000000 RAM; all instruction bytes remain original.
The original GNU image, assembler, compiler, simulator and 120-second stock
timeouts execute the contract. The physical decomposition of the corrections,
producer acquisition, operating cadence, actuation and hardware validation
remain separate from this bounded numeric publication.

## Connected injection calculation and raw scheduling

Ten mandatory Regions bind 3021 instructions, 7319 bound bytes
and 194860 literal cases with EARLY_ONLY=0. Each function or bounded view
has independently reconstructed instruction bytes. The registered contracts
execute the complete opening-word publisher, pulse selector, delayed-start
programmer, one-shot, end-angle publisher, injector-event ISR and dispatcher.
Three RPM views cover word scaling, capped byte scaling and the real copy;
they do not establish whole RPM-producer execution or sample simultaneity.

The opening word uses unsigned battery B and ROM bytes Q/A:
min(65535,max(0,floor((175-B)*Q/128)+A)). The real seven-SHAR helper floors
negative products. The full byte domains have a maximum of 603, making the
upper clamp unreachable. Raw duration and voltage units remain unverified.

The selector distinguishes override, stopped, start modes 1/2/4 and running.
Start modes compare the threshold with capped opening plus ROM margin,
conditionally subtract the stopped word, then apply the selected floor.
Running takes the maximum of each snapshot word and the running floor.
Its real secondary tail clears pending corrections and scales or copies
secondary words under the independent aggregate mask and ROM control bit.

The one-shot requires explicit invocation and an enabled output byte. Any
intersection of the whole mask with inhibition or history selects opening
for every selected channel. A set start bit subtracts opening with floor0.
The capped increment is floor(800*d/256), or 1000 in diagnostic mode; addition
to the raw counter wraps modulo65536. Its chain sign is none. DSTR ORs only
bits0..5 under I15 and restores the incoming interrupt mask. Synthetic raw
register storage does not verify peripheral timing or physical actuation.

Normal end-angle equations read the state after the prefix, latch, countdown
and bias updates. They select the conditional curve, fixed override, or base
curve plus bias, then cap at209 and double. The unsigned eight-cell implicit
lookup uses step32 and last-cell clamp224. It adds or subtracts the floor of
the positive interpolation distance. Alternate and inhibited entries retain
separately executed outcomes. Synthetic curves and scalars expose branches
that stock calibration suppresses; their physical reachability is unverified.

The base path of publisher 00056bd0 executes wrapper 00026370 and linear
finisher 00026740, adds the updated unsigned byte ffff340c to the base curve
result, applies the 209-count cap, and stores the doubled word at ffff192e.

Pending-mask equations read staged state after optional trigger setup and
before lead/cursor updates. Equal lead accepts only a matching next cursor,
negative lead clears pending, and positive lead executes the actual catch-up
loop and both consumers before publishing the final slot mask. The programmer
receives 4*unsigned8[ffff2333] or52 and wraps it to uint8. Nonzero normalized
count retains offset. Zero count uses the exact wrapped remainder and the
low32 reciprocal product. Compare selection uses delta+2>q, including timer
wrap; raw status/control updates have independently checked word boundaries.
The ISR equations require an explicit invocation; hardware compare delivery
is not inferred from separate compare and raw-publication observations.

Every admitted path observes all15 GPRs, complete SR/PR/SP/MACH/MACL/GBR,
the immutable76-byte input, the C caller ABI, declared saved/local bytes,
64k RAM, all bound ROM inputs and declared alias neighbors. The combined
dispatcher and ISR compare all192 frame bytes. The pinned GNU simulator's TRAPA/RTE uses SPC/SSR
and leaves SP unchanged. It does not establish the SH-2E exception stack;
equivalent exception-stack coverage is required before hardware eligibility.
Only declared RAM and register pointer pools are relocated. Exact instruction
bytes, the original GNU image and standard timeouts remain under the gate.

The arithmetic covers fuel_pulse18/24/25/26 and
injection_phase1..8/17/18/20..22. Indexed one-shot context x[0] is the incoming
aggregate mask and x[1] is channel0..5. The raw counter's previous value is
prev. This specification fixes the meaning of lookup and staged-state
boundaries; physical units, acquisition cadence and hardware validation
require their separate evidence.

## Upstream fuel pulse calculations

Eleven mandatory Regions bind 2726 instructions, 6494 bound bytes
and 696084 literal cases through the primary stock verifier. The sixteen
formula-bearing fuel_pulse steps1..16 use raw operand widths and exact
rounding, wrapping, latch and call boundaries.

| Calculation | Region | Literal cases |
|---|---|---|
| base-accumulator | `jk08a-base-accumulator` | 132684 |
| transient-coefficient | `jk08a-transient-coefficient` | 7440 |
| transient-additive | `jk08a-transient-additive` | 87052 |
| coolant-conditional | `jk08a-coolant-conditional` | 14261 |
| transient-pair-1 | `jk08a-transient-pair-1` | 44640 |
| transient-pair-2 | `jk08a-transient-pair-2` | 44640 |
| fuel-multiplier | `jk08a-fuel-multiplier` | 77328 |
| pulse-precursor | `jk08a-pulse-precursor` | 78272 |
| common-gain | `jk08a-common-gain` | 68855 |
| enrichment-prefix | `jk08a-enrichment-prefix` | 70800 |
| enrichment-terminal | `jk08a-enrichment-terminal` | 70112 |

Natural function 000554ae performs modulo-2^32 addition of RAM32[ffff15f8], 16384, unsigned RAM16[ffff230c] and unsigned RAM16[ffff15da], interprets the low32 result as signed, then clamps it to0..65535 atffff231a. The signed wrap seam prevents a universal positive input sign. Producer domains and physical units require independent evidence.

Natural function000528be reads doubled normalized load, capped255, through the actual eight-cell lookup00026370 atROM00012176. It publishes half the cell atffff150a while signed RAM16[ffff1a66]<0, otherwise64. Its natural RTS at000528f2 returns without calling00052902 or writingffff2300.

Natural function00052902 publishes signed16 atffff2300: trunc0(uint8(ffff150a)*int16(ffff1a66)/256), or0 whenffff245d.bit5 andROM8[00008b40].bit2 are both set. The admitted product bounds-32640..32639 make the explicit signed saturation unreachable. No physical transient qualifier or cadence is inferred.

The two bounded caller windows0005243c..00052444 and0005249e..000524a6 in000522c4 execute their original BSR pairs to000528be and00052902 with both delay slots and natural returns. Each caller observes current coefficient then signed additive publication. The surrounding dispatcher is outside these bounded windows.

Natural function0005525a updates threshold/hysteresis bits inffff2492/ffff2493, admits the actual gate, and uses uint8(4*max(0,uint8(ffff106f)+int16(ROM16[0005533c]))) for eight-cell curve00012422. It publishes lookup byteffff15dd and selected coefficient byteffff15dc fromROM0000990a, with load/RPM bins at00011b1b/00011b17. Optional signed difference rate limiting against oldffff15da precedes cap max(0,ROM16[0000929a]-RAM16[ffff22e8]+16384); disabled entries publish0 and retain lookup/coefficient bytes. Wrapped coordinates have sign none.

Natural function000556ec scales min(65535,RAM16[ffff231a]+RAM16[ffff240a]) by unsigned mixtureffff22e8 over16384. It executes special multiplier0000838e, floorffff15cc, cap byte00008b9d, eligibility gates, floor/phase latches and normal/transition rates000084e6/0000840d. Transition progress usesffff84c3.bit7. It writes workingffff18e4 and publishesffff22e6 as0 only when aggregateffff22e0 equals0x3f. Full admitted contexts contain downward discontinuities, so both input views have sign none.

Natural function0004e974 selects unsigned BFSffff1024 orffff123e; optionalRPM cap uses max(ffff34f6,ROM32[000096e0]/RPMwordffff11bc), with all-ones quotient at zeroRPM. It publishes selected BFS atffff196a. H=floor(B*RAM16[ffff22e6]/131072). For bank0/1 it adds signedffff2300 to floor(H*RAM16[ffff40b6+2*b]/25600), then executes actual signed Q14 multiplication by unsigned gainffff165e, signed truncation toward zero, clamp0..65535 and floorROM16[000094e8]. Commonffff1876 uses H directly and updatesffff24a1.bit0 on its pre-floor clamp. Bank outputs areffff18c0/ffff18c2.

Natural function00053698 alternatesffff2485.bit3: inactive entries set the bit and retain all gain intermediates; active entries clear it. Diagnostic argument-1 has a fixed false predicate. Raw P=floor(RAM16[ffff4524]*ROM8[000089fe]/128)+ROM16[000093c6] is retained for arithmetic after min(65535,P) publication atffff517c. Selected correction, ordered low/high clamps, BFS scaling and two16-cell curves000129e2/000129f2 precede saturated sum, complement load, ratio and floor((ratio*5259+1213696)/10000). Final gainffff165e=floor(byteffff160d*ROM16[00009332]/256). No temperature, pressure scale or acquisition cadence follows from these consumer contexts.

Bounded original prefix0005594a..00055a52 executes wide-open hysteresis onffff3528 and16-cell curve0001214e, explicitRPM/load axis search00011cc0/00011ac7, and8x8 surface0000a9aa with horizontal then vertical positive-distance-floor interpolation. Optional00012552 correction uses true signed seven-SHAR flooring of the deviation from128. The rich latch uses unsigned32 hysteresis arithmetic with bytes00008b9b/00008b9f and publishes surface value or128 atffff15eb. Synthetic calibrations expose direction reversals and unsigned wrap; surface sign is none. The boundary preserves the live outer frame and does not execute the subsequent state machine.

Bounded entry000562e2 resumes after the upstream state machine with an independently staged word atSP+12. Exact mode/phase/enable/tick branches update primaryffff123a, clamp it to mixture*128 and updateffff2485.bit5. The real0005651c auxiliary call updates curve/latches/countdown andffff123c. The terminal max(primary,auxiliary) is forced to16384 below rawRPM32 or duringffff2531 delay, then capped byROM16[000094ec] underffff4252.bit1 beforeffff22e8 publication. Untouched state-machine domains, physical mixture interpretation and tick cadence retain separate evidence.


The transient coefficient function returns naturally without invoking the
additive function. The bounded two-call windows of the real parent establish
their composition. The enrichment prefix stops before the upstream state
machine. The terminal resumes with a staged candidate at SP+12; it executes
the actual auxiliary function and terminal publication without inferring
the omitted state machine. These boundaries retain their original stock
instruction bytes and expose the complete live frame state.

All contexts compare complete GPRs, SR including M/Q/T and interrupt mask,
PR/SP/GBR/MACH/MACL, immutable input records, 192 frame bytes and the complete
64k RAM window. Natural calls and returns, original branch delay slots,
declared lookup pools and the shared 16-bit RAM pointer's neighboring bytes
are checked. Relocations affect declared data pointers only. The boundary
observer restores the admitted outer stack through an explicit scratch
register; it does not replace arithmetic under test.

Before simulator entry, the linked big-endian ELF32 SH image is checked for
every allocated section and every LOAD segment's virtual and physical memory
extent, including uninitialized BSS. Storage that intersects the declared
RAM window is rejected. Exact adjacency is admitted. Truncated, wrapping or
missing storage declarations are rejected. Literal context compaction retains
full register observations while placing executable fixture data outside RAM.

The numerical contracts permit synthetic calibration contexts to expose
otherwise inactive branches. They establish neither physical units nor
acquisition cadence or live producer reachability. Hardware eligibility
requires the corresponding bench and engine evidence; the existing GNU
SPC/SSR exception contract does not establish the SH-2E exception stack.

The named specification covers these exact chain members:

`0000a9aa`, `00012176`, `00012422`, `000129e2`, `000129f2`, `0004e974`, `000528be`, `00052902`, `00053698`, `0005525a`, `000554ae`, `000556ec`, `0005594a`, `ffff1024`, `ffff102c`, `ffff106f`, `ffff11bc`, `ffff15da`, `ffff15eb`, `ffff165e`, `ffff18c0`, `ffff22e6`, `ffff22e8`, `ffff2300`, `ffff231a`.

## Bounded post-acquisition knock metric

One mandatory Region binds 362 instructions, 874 bound bytes and 9404 literal
cases. `jk08a-knock-metric` starts at 0004a2b6 and stops before threshold
lookup at 0004a2ee. Its alternate subtraction span is 0004a496..0004a4c8;
complete selection 00049d88..00049e96, complete scaler 00049e96..00049fc0,
bitmap dispatcher 000221bc..000221d6 and ladder 000221e0..000221f8 retain
their stock addresses and instruction bytes. A simulator-only boundary
restores the external continuation from SP+24 through R1. Direct selection
and scaler entries execute their natural returns.

The caller supplies eight unsigned software sample words at ffff20c2 and
the selected eight-word reference row at ffff2178+16*(c-1). Selector
ROM8[00008b3d].bit3 chooses unsigned channel ffff11de or ffff2143; c is 1..6.
Each signed difference is sample-reference in -65535..65535 and is published
at ffff2158+4*i. The raw source path begins with these explicit post-acquisition
words. ADC/DMAC, the channel-zero guard, filter/transform or bin production,
full evaluator dispatch, ISR/RTE, physical channel order, physical units,
asynchronous cadence and engine reachability remain separate evidence.

ROM8[00008618] masks slots with INT32_MIN sentinels. The complete helper
orders eight values descending and sums the first N ranks excluding
sentinels, with N=ROM8[00008870] in 0..8. N=0 yields zero; N=9..255 is outside
the contract. The selected signed sum is stored at ffff2274+4*(c-1), in
-524280..524280 for legal word differences. A finite network of 28 min/max
compare-exchanges expresses mathematical ordering with the existing
arithmetic Grammar. It is independent of the instruction sequence.

The complete scaler separately admits a full signed32 sum A. Its gain is
G=min(65535,floor(ROM8[000086ac]*ROM8[00008694]*ROM8[000086a7]/128)). The
gain factors are raw bytes; generic owners assign no stock value or scale.
q=floor(abs(A)*G/16384); positive output is min(q,2147483647), and negative
output is -min(q,2147483648). The signed cell at ffff21f8+4*(c-1) is stored
at 00049f32 and read back at 00049f3c. Addition at 00049f42 and store at
00049f4c publish uint32(metric+0x80000000) at ffff21d8+4*(c-1). The signed
cell reader is genuine RAM readback, independently of the normalization
sample/cache parallel stores.

The literal matrix contains 6488 composite, 972 direct selection and 1944
direct scaler contexts. Of the composite contexts, 386 retain the six stock
calibration bytes: selector 0x82, mask 0, count 3 and gain bytes 128. Other
calibrations are labelled artificial inputs. Mask 0..255, count 0..8, all
six channels, unsigned word boundaries, ties, mixed and negative order,
every maximum position, exact gain neighbors 65534/65535/65536 and both
signed saturation neighbors are independently literal. No runtime output
or instruction interpreter supplies an expectation.

Every context checks fifteen GPRs, observed full SR, MACL/MACH/GBR, PR/SP,
the outer C ABI, 112 frame bytes at incoming SP-80..SP+31, all declared
outputs and the remaining 64 KiB RAM and bound data. Entry mode bits are
retained; M/Q/T are cleared and independent T0/1 is seeded before STC
records the prepared SR. Exit is (sr_before&~1)|expected_t. Composite T=0;
direct selection T=((selector&8)==0); direct scaler
T=(A>=0 && q>=2147483648). No arbitrary entry M/Q or runtime-mode change
is claimed. Output capture and the SR observation lie outside the observed
stock frame.

Both subtraction loops, real BSR calls, eight real shift calls, helper
return delay slots and selected stores execute through stock bytes. Shift
indices are 0..7; the zero-result arm 000221e0..000221e4 has byte identity
only. Other shift domains are outside this Region. The early product/carry
branches 00049f12/00049f74 and late positive comparison branch 00049faa are
unreachable under the declared signed32/gain bounds. The full scalar
saturation contexts do not establish those inputs from acquisition.

The sample and reference chain signs vary one word with channel, mask,
count, gain and every other input fixed. The stated stock sign context
uses mask 0, count 3 and gain bytes 128, with sum -196605..196605. Changing
calibrations or channel has no joint monotonicity claim. Normalization and
metric have separate execution boundaries and no joint-invocation claim.
Hardware readiness is NO.

## Bounded software knock normalization

One mandatory Region binds 266 instructions, 631 bound bytes and 6563 literal
cases. `jk08a-knock-normalization` begins at 0004a26a or alternate 0004a3b0,
stops at 0004a2b6 before subtraction, and includes positive-word divider
00021ce0..00021d6a with its natural returns. Additional stock spans are
0004a3b0..0004a3fe, 0004a438..0004a496 and 0004a4fc..0004a58e. The
last span includes the real delay-slot store at 0004a58c; alignment at
0004a58e is outside the contract. Static selector and channel-guard anchors
provide input-context identity and have no executed guard claim. The
simulator-only SP+24/R1 continuation is outside stock instructions.

Explicit inputs are legal selected channel c=1..6, unsigned byte
B=ffff2154, unsigned word P=ffff2152, eight unsigned words
X[i]=RAM16[ffff2132+2*i] and raw byte F=ffff87e1. Selector
ROM8[00008b3d].bit3 chooses ffff11de or ffff2143. Primary R5=c/R11=0
and alternate R14=c/R11=8 agree with the selected byte and ROM bit.
The unused channel byte remains independently supplied and preserved.
The producers of these post-acquisition software inputs and registers are outside the fixture.

B=0 publishes 65535. B>0 gives q[i]=floor(X[i]*P/(32*B)); F=0 publishes
uint16(q[i]), while F!=0 publishes min(65535,8*q[i]). Both sample words at
ffff20c2 and cache words at ffff20d2+16*(c-1) use the same live register,
without a sample RAM readback. Each context checks all sixteen outputs.
Ordinary publication wraps the low word; it has no full-domain positive
sign. Weighted publication saturates separately. B=0 reads neither bins,
multiplier nor mode and calls no divider.

For positive B the exact divisor 32*B is 32..8160. X*P is at most 4294836225,
q at most 134213632, and 8*q at most 1073709056; no uint32 numerator or
weighted shift overflow occurs. Each positive context executes eight real
divider calls with MACL transferred in the delay slot. Fast and long
returns, threshold q 255/256/257, low-word neighbors 65535/65536/65537,
weighted neighbors 8191/8192/8193, both cache branches, both mode branches
and the zero-block fallback are covered. Raw weighted equality 65535 is
unreachable because 8*q is a multiple of eight. The zero and full 32-bit
denominator alternatives are outside the tested divider span.

The independent matrix contains 3281 primary and 3282 alternate contexts:
522 zero-block, 2512 ordinary and 3529 weighted. Its 1325 stock software
arithmetic contexts use selector 0x82, B<=8, P<=256 and F 0/1. These are
software classifications, without a live acquisition claim. Other byte/
word contexts and selector values are explicitly artificial inputs.

Every context checks fifteen GPRs, actual prepared full SR, MACL/MACH/GBR,
PR/SP, the outer ABI, 64 frame bytes at incoming SP-32..SP+31, bound data,
input context and all remaining 64 KiB RAM. Entry retains runtime mode bits,
clears M/Q/T, seeds independent T0/1 and observes SR after LDC. B=0 exits
with (sr_before&~1)|1; B>0 exits with
(sr_before&~0x301)|1|((1-(q[7]&1))<<8). Final Q uses the full quotient before
word wrapping or weighted cap; equal FFFF outputs at q 8192/8193 retain
different Q. Arbitrary incoming M/Q and new runtime modes are outside
this contract. The saved R2 and conditional last-long R3 words, sample/
cache pointer slots and all frame neighbors have literal expectations.

Eleven high-RAM pool aliases are applied after exact GNU reconstruction;
stock instruction bytes and natural calls/returns remain unchanged.
Normalization ends before metric subtraction. The separately registered
metric does not establish joint invocation. ADC/DMAC/MMIO completion,
filter/transform and bin production, ISR/RTE, full dispatch, channel-zero
guards, physical channel mapping, cadence, physical units and engine
reachability have no proof from this CPU contract. Hardware readiness is NO.

## Post-feedback STFT publication

One mandatory Region binds 43 instructions, 98 bound bytes and 6160 literal
cases. `jk08a-stft-publication` executes `0005ca08..0005ca5e` with its supplied
32-byte caller save frame and natural epilogue. Normal mode copies the two
independent unsigned working words; forced mode publishes the common clamped
byte times 256. The literals contain every mode and forced-percent byte,
word boundaries and both entry T values. Two 32-bit RAM pools and two declared
16-bit pointers are relocated after exact stock reconstruction. Fifteen GPRs,
special registers, full SR, PR/SP, the outer ABI, 64 frame bytes and the entire
64 KiB RAM image are observed. Preceding feedback, producer semantics, physical
units and cadence remain separate. Hardware readiness is NO.

## Learned-grid selection

One mandatory Region binds 326 instructions, 765 bound bytes and 10840 literal
cases. `jk08a-grid-selection` executes the complete `0005796c` selector with
the real word fill, auxiliary reset and diagnostic predicate helpers. Its
domain is bank 0..1, unsigned word load, unsigned byte speed, every prior
packed byte and independent byte calibrations. First-break searches admit
unsorted axes and apply prior-index hysteresis. The selected cell either
publishes its word or triggers full bank reset. Stock bound transition
23039/23040 prevents a universal positive cell influence. The matrix has
10621 normal and 219 reset calls; 10658 calls reach the real predicate with
descriptor index 297. Twelve RAM pools relocate after byte identity checks.
All GPRs, special registers, full SR, natural calls/returns and delay slots,
the outer ABI, 112 frame bytes and all 64 KiB RAM remain observable. Producer
semantics, physical units and cadence remain separate. Hardware readiness is NO.

## Bounded learned-grid update

One mandatory Region binds 267 instructions, 634 bound bytes and 9856 literal
cases. `jk08a-grid-learning` executes complete `00057d1e` with the real absolute
value, word fill and auxiliary helpers. Bank 0..1 and packed index 0..63 are
explicit. Two independent permit bits enable a signed displacement times
byte coefficient, division truncated toward zero, conditional minimum step
and upper-then-lower bounds. STFT supplies only the neutral-value gate; the
step direction follows an independent word. The auxiliary cell increments
modulo 256, conditionally decays and clears outside its retention interval.
There are 9340 enabled and 516 disabled calls, with 3179 conditional minimum
steps, 1054 decay cases and 2421 auxiliary clears among enabled calls. Fourteen
RAM pools relocate after exact reconstruction. Every GPR, special register,
full SR, natural call/return, delay slot, outer ABI, 112 frame bytes and the
complete 64 KiB RAM image are observed. Producer semantics, live permits,
physical units and cadence remain separate. Hardware readiness is NO.

The narrow mechanism and boundaries are in
`defs/JK08A.closed-loop-publication.md`. The three Regions execute independently;
their combined registration does not establish a jointly invoked feedback cycle.

## Bounded closed-loop input conversion

One mandatory Region binds 823 instructions, 2233 bound bytes and 4338 literal
cases. `jk08a-closed-loop-conversion` executes the complete `0003edb4` entry,
the natural `0003ef74` coordinate conditioner and nine real lookup or division
helpers. Both channels exercise the word-wrapped source selection, both
signed16 clamps, strict admission/bypass, directional integer interpolation,
signed adjustment and optional offset, and final unsigned16 saturation.
The matrix contains 4022 admitted calls and 46 zero-coefficient calls.
The observer checks all GPRs, full SR, natural PR/SP, MACH/MACL/GBR, outer ABI,
all 64 KiB RAM, two workspace aliases and neighbors, all bound bytes and the
complete 160-byte nested frame. Nine 32-bit RAM pools and two declared 16-bit
RAM pointers relocate after exact byte reconstruction. Producer semantics,
physical units, engine reachability, permission and cadence remain separate.
Hardware readiness is NO. The narrow mechanism and arithmetic are in
`defs/JK08A.closed-loop-conversion.md`.

## Bounded closed-loop adjustment

One mandatory Region binds 1231 instructions, 2678 bound bytes and 10286 literal
cases. `jk08a-closed-loop-adjustment` executes the complete `000a0ee8` entry and
four real unsigned lookup and division helpers. The two channels exercise all
four selectors, both-bank admission/bypass, signed saturation, ordered signed
bounds, byte counters and preserved state. The 512-case admission product
covers all four permission outcomes without claiming a full Cartesian product
of every raw input.
The observer checks all 15 GPRs, full SR/MQT, MACH/MACL/GBR, natural PR/SP, outer
ABI, all 64 KiB RAM, the 122-byte workspace and neighbors, bound bytes and the
complete 192-byte nested frame. Eight long RAM pools and one declared 16-bit
workspace pointer relocate after exact byte reconstruction. Counts describe
reconstructed instructions; they do not measure dynamic instruction coverage.
Physical units, source producers, permission, cadence, whole feedback and engine
reachability require separate evidence. Hardware readiness is NO. The narrow
mechanism and numerical views are in `defs/JK08A.closed-loop-adjustment.md`.

RAM word windows with different origins may overlap when their address
translation is identical. Identical windows may share distinct pool bindings.
Duplicate or overlapping pool words, conflicting translations and different
extents at the same origin are refused. Stock code, pools, return boundaries,
register windows and long RAM literal restrictions remain checked.

## Bounded whole closed-loop feedback

`jk08a-closed-loop-feedback` executes natural entry `0005cbec`, both banks and
fifteen real helpers. One mandatory Region binds 3067 instructions, 63998 bound
bytes and 1829 literal cases. Ten final-source alternatives and 3658 bank
observations bind transition, initialization, ordered limits and source
precedence to independent raw-state equations. Full RAM, the 302-byte coherent
workspace and neighbors, fifteen GPRs, actual prepared full SR, special
registers, natural PR/SP, outer ABI and the 352-byte nested frame are compared.
Forty-three long RAM pointers and seventeen word pointers use declared
simulator relocations. Stock code has no stubs or changed instruction bytes.
Physical units, producers, scheduling, cadence, peripherals and engine
reachability require separate evidence. Hardware readiness is NO. Exact reader
phases, literal boundaries and identity-only branches are specified in
`defs/JK08A.closed-loop-feedback.md`.

## Fuel-cut consumer and event history

Two existing mandatory Regions bind 679 instructions, 1582 bound bytes
and 15266 literal cases with EARLY_ONLY=0. The complete one-shot function
0002c13c has 8012 cases. The complete event handler 0002be40 and its real
duration selector and one-shot callees have 7254 cases. Their instruction
bytes, pools, declared simulator relocations, fixtures, literal headers,
full CPU/RAM/frame observations and standard execution remain unchanged.
Hardware readiness is NO.

The one-shot takes the whole mask from independent R4 and six duration words
from independent R5. The accepted domains include both ffff224e and ffff1568
arrays. Channels are i in 0..5. Formula arguments x=[R4,i,duration[i]] bind
the selected raw duration explicitly; they do not infer a producer or require
a single duration-array base. The prior counter word is prev. Step23 uses
from=inhibit byte ffff22e0; step25 uses from=entry history byte ffff1935.

With ffff4184.bit7 clear, all counter words, DSTR and history are preserved.
With the bit set, any intersection of the whole mask with the inhibit or
entry-history byte selects unsigned16 opening word ffff23aa for every
selected channel. The consumer ORs the whole low-byte mask into history.
An individual channel-bit test does not express this selection condition.
No selected bit in 0..5 means no counter, DSTR or one-shot history store,
including a mask whose only set bits are 6/7.

An already set DSTR bit i subtracts opening with floor 0. The increment is
min(65535,floor(800*d/256)), or 1000 under ffff4251.bit0. The raw counter
addition uses uint16 wrap, and DSTR ORs the selected bits. Other control
bits do not change these conditions. Counter wrap and aggregate selection
prevent a universal positive or negative influence; both step signs are none.

For step24, from is the incoming rotating count ffff1937 and prev is incoming
history ffff1935. RAM8[ffff1936] is read after the event handler copies pending
byte ffff2228 into it, before its history operations. The handler always
clears every bit of this current mask from history. If both the count and
the entire inhibit byte are nonzero, it decrements the count once and ORs
the entire mask into history, even when one-shot output is disabled or the
mask does not intersect inhibition. Auxiliary R in the formula is the
stored remaining count.

The real one-shot call can OR that mask into history again. The final history
formula includes its enable bit, the existence of a selected channel0..5,
and the whole-mask intersection with inhibition or the history immediately
before that call. It includes this call and the handler's
earlier history store. Its sign is none.

Mandatory arithmetic gates compare both counter formulas with 48072 raw
counter observations each and the history/count formula with all 7254 complete
event cases. Eight semantic mutations reject individual-bit intersection,
counter saturation in place of wrap, omitted opening subtraction, altered
diagnostic increment, omitted history clearing, inhibit bit0 in place of
nonzero-byte admission, omitted called-consumer publication and ignored
output enable. Explicit witnesses distinguish a multibit mask from an
individual channel test, disabled-output count/history updates and a
high-only mask without a selected channel.

| Owned operand | Role in the bounded consumer |
| --- | --- |
| 0002c13c | Complete one-shot function |
| 0002be40 | Complete event handler |
| 00054d3e | Real event duration selector |
| ffff22e0 | Entire aggregate inhibit byte |
| ffff1935 | Incoming, intermediate and final history byte |
| ffff1936 | Current mask copied before history operations |
| ffff1937 | Incoming and decremented release count |
| ffff23aa | Unsigned opening word |
| ffff4184 | Output-enable bit7 |
| ffff4251 | Diagnostic-increment bit0 |
| ffff224e | Scheduled duration-array base |
| ffff1568 | Alternate duration-array base |
| ffff2228 | Pending mask copied by the event handler |
| fffff640 | First counter word; six selected words at base+2*i |
| fffff666 | Start-register bits0..5 |

The event observer retains the accepted explicit return transport and complete
SH-2E exception stack. SPC/SSR peripheral exception behavior is outside this
software invocation. Synthetic register storage does not establish timer
evolution, physical units, channel-to-cylinder wiring, injector timing or fuel
delivery. Upstream inhibit/count/one-hot producers, physical reachability,
operating cadence and engine hardware validation retain separate evidence.

## Main RPM fuel-cut state

The bounded entry 0004f282 binds 81 stock instructions and 196 bytes:
162 instruction bytes, five long pool words, configuration byte 00008b38,
delay byte 00008c69 and six threshold words at 0000934e..00009358.
The two declared long RAM translations bind ffff244c and ffff119c to the
positive simulator RAM window. The natural RTS delay slot restores GBR.
Hardware readiness is NO.

Stock configuration 00008b38=63 has bit 7 clear. Raw selector byte ffff2468.bit4
chooses activation/release pairs (612,596) or (596,368). The third pair (0,0)
and its guarded path have identity-only evidence in this stock domain;
their execution is outside the contract. No calibration byte changes during
the bounded invocation. Other configuration-byte consumers retain their own
evidence.

The raw state byte is ffff2497. Bit1 is the arm and bit2 is active. While active,
RPM word ffff11bc at the release threshold or above preserves the state;
only a value below release clears both bits. While inactive, a value below
activation clears the arm. At activation or above, a clear arm loads the
stock delay into ffff24f1 and sets the arm. An existing arm retains its
incoming counter. Counter zero sets active; nonzero preserves the inactive
state. The function does not decrement the counter in this invocation.
All other state bits retain their incoming values.

Step 11 takes from as the four row-major words of the owned 2x2 table,
x=raw RPM and prev=incoming flags; bit 4 selects indices P and 2+P.
Step 12 takes from=raw RPM and prev=incoming flags;
its numerical expression reads the actual table pair through selector bit 4.
Auxiliary K is the stored delay byte. Both output the complete raw flag byte
and have sign none. Equality at activation admits the state transition;
equality at release retains active state. A stock zero reload applies to
a newly armed transition; an already armed nonzero counter still waits.

The literal matrix has 6400 independent contexts. It covers all 256 incoming
flag bytes, selector bytes and counter bytes; both table pairs; the raw RPM
boundaries 0, release-1, release, activation-1, activation, activation+1,
32768 and 65535; and all 128 supported incoming SR/MQT combinations.
The first six contexts contain all six branch outcomes. These axes do not
form the full Cartesian product and do not establish physical reachability.

The observer compares all fifteen natural exit GPRs, full SR/MQT,
MACH/MACL/GBR, PR/SP, a distinct C caller ABI, all 64 KiB RAM and all 34
pool/configuration/threshold bytes. Its independent 80-byte SP-48..SP+31
frame permits only the four-byte saved GBR at offsets 44..47. R7 is the
declared driver call target; the stock entry preserves it. Full incoming
GBR/MACH/MACL words include zero, all ones and both sign boundaries. The observer changes only
T, IMASK, Q and M in the actual incoming SR, retains every other status bit,
and independently compares the context pointer and R3 before and after
status preparation. The complete exit SR uses the independently observed
original status and the literal expected controls.

The numerical contract compares both complete flag/counter views with the
6400 literal contexts. Eight semantic mutations cover strict cut/release
equality, ignored arm counter, wrong selector bit, lost other flag bits,
signed RPM comparison, omitted delay loading and an in-call decrement.
Executable acceptance requires the exact-stock fixture and the mandatory
complete standard gate with EARLY_ONLY=0.

Physical RPM scaling, periodic decrement production, upstream state/selector
reachability, interrupt delivery, full ECU scheduling, invocation cadence,
the global inhibit coordinator and actual fuel delivery require separate
evidence. This entry does not establish those mechanisms.

## Vehicle-speed fuel-cut state

The bounded entry 0004f19c binds 63 stock instructions and 153 bytes.
The literal matrix has 12544 independent contexts. Hardware readiness is NO.

The invocation does not decrement the counter. The observer checks full SR/MQT.

The natural stock entry `0004f19c` returns bit 0 of `ffff24a6` and updates a
coarse vehicle-speed fuel-cut state. The function reads the raw speed byte at
`ffff110e`, the complete control byte at `ffff24a7`, and the delay counter at
`ffff24f6`. Its two code spans are `0004f19c..0004f1d8` and
`0004f240..0004f282`. All 63 instructions retain the stock ROM bytes.

### Raw state transition

Bit 0 of the incoming state byte selects active and inactive paths. An
inactive state below the activation byte `ROM8[00008db7] = 93` clears control
bit 7 and leaves the state and counter unchanged. At speed >= 93, a clear
control bit 7 loads `ROM8[00008caf] = 0` into the counter and sets control bit
7. A zero counter and clear control bit 5 set state bit 0. An already armed
nonzero counter waits without decrementing it.

For an active state, control bit 5 clears state bit 0. Speed below the release
byte `ROM8[00008dc3] = 91` clears both state bit 0 and control bit 7. At speed
>= 91, the incoming control bit 7 is retained, including when the control
bit 5 gate clears the state. The counter is unchanged on every active path.
All unrelated state and control bits are retained.

The speed and threshold comparisons preserve the unsigned byte ordering.
The stock loads sign-extend speed into R6, but unsigned `CMP/HS` compares its
32-bit representation with positive thresholds 93 and 91. Raw speed bytes
128..255 therefore satisfy both thresholds. A physical speed conversion,
counter cadence and engine reachability require separate evidence.

### Arithmetic view

The chain input `from` is the raw speed byte and `prev` is the complete
incoming state byte. `J` is the complete outgoing control byte, `K` is the
outgoing counter, and `D` is the returned Boolean.

```text
F = uint8(prev); C = RAM8[ffff24a7]; A = F&1;
B = (C>>7)&1; G = (C>>5)&1; S = uint8(from);
L = ROM8[00008db7]; H = ROM8[00008dc3];
N = min(1,max(0,S-L+1)); V = min(1,max(0,S-H+1));
U = (1-A)*N*(1-B);
K = (1-U)*RAM8[ffff24f6]+U*ROM8[00008caf]; Z = 1-min(1,K);
E = A*V*B+(1-A)*N; J = uint8((C&127)|(128*E));
D = (1-G)*(A*V+(1-A)*N*Z); to = uint8((F&254)|D)
```

### Bounded executable observations

The declared matrix has 12,544 contexts and ten natural path classes. It
covers all 256 state bytes, all 256 control bytes, all 256 counter bytes,
speed boundaries 0, 90, 91, 92, 93, 94, 127, 128 and 255, and all 128
combinations of T, IMASK, Q and M controls. These sets occur in separate
bounded partitions; the matrix is not their full Cartesian product.

Independent literals describe all fifteen GPRs, the complete controlled SR
and final T. The observer independently captures actual status bits outside
the declared controls and retains them through entry and return. It checks
natural PR/SP, MACH/MACL/GBR, the C caller ABI, an 80-byte frame, all 64 KiB of
working RAM, and all 27 bound pool and calibration bytes. The only stock
frame write is the four-byte saved GBR at offsets 44..47. R7 receives the
sign-extended incoming control byte and is an outgoing clobber.

Six stock long pools supply the working base, speed base and calibration
addresses. Three RAM long values have declared simulator translations;
instruction bytes, calibration bytes and stock call/return behavior retain
their original values. The function uses no helper stubs. Software execution
does not establish the global inhibit coordinator, interrupt delivery,
physical units, complete ECU scheduling or hardware readiness.

## Bounded working-state width views

The complete stock runner executes `width_view_capture.py` before its registered
stock loop. Its `jk08a-width-views` observations remain in `width_views` of the
same original COPY packet. They have a distinct marker and are not added to the
registered stock-region case totals. The common TEST primary independently
validates their physical capture and full-state equations and connects exact
diagnostic byte views to the same complete SID22 original.

`defs/JK08A.width-views.toml` declares the retained native questions and bounded
GBR, register, selector and SP+8 premises. Independent mnemonic assembly binds
the stock instructions and pools. The observer preserves complete raw state;
canonical RLE retains the entire before/after RAM. These observations grant no
automatic width resolution, natural caller or helper-output reachability,
selector range, distant GBR preservation or hardware conclusion. The precise
scope and remaining admission boundary are in `defs/JK08A.width-views.md`.

## Native byte-surface caller observations

`byte_surface_capture.py` executes the complete BFDC0 caller and natural
4x4/8x8/16x16 byte-surface helper closure in the same full stock primary.
`byte_surface_paths` remains part of the existing COPY packet with its own
marker and invocation count. The explicit input catalogue includes direct
helper roles, stock/synthetic calibrations, independent fifth/R7 arguments,
conditional outcomes and correction boundaries. Complete raw state/RAM and
calibration snapshots support independent physical, instruction-state and
numeric consumers. Their exact scope is in `defs/JK08A.byte-surface-paths.md`.
The positive later conditioning/diagnostic paths require their own evidence.

## Conditional exhaust-target observations

The complete stock process runs `exhaust_target_capture.py` alongside the
byte-surface capture and retains its raw `exhaust_target_paths` in the same
COPY original. `defs/JK08A.exhaust-target-path.toml` binds the exact BFE88
instruction spans, natural hysteresis helper and pointer aliases. The raw
driver has no expected-output columns. Independent consumers require the full
state, both selected endpoint paths through the intermediate local-frame
stores, explicit disabled/replacement modes and the actual final `FFFF2327`
store. This conditional component grants no native relation, scale or hardware
admission. Its invocation count is derived from its typed input matrix and is
separate from registered stock-region totals.

## Conditional BFS observations

`bfs_path_capture.py` retains the complete natural BFS producer and its declared
helpers in the same original stock process. Its `bfs_paths` COPY packet contains
full raw state and actual K calibration bytes. Independent physical, instruction
and wide integer consumers bind the admitted K-dependent quarter-BFS path,
normal cap and alternate selection to the actual `FFFF1026` diagnostic store.
The bounded modes and source contract are in `defs/JK08A.bfs-path.md`; native
relation and scale admission remain separate.

## Sequenced ignition diagnostic observations

`ignition_diagnostic_capture.py` records the natural event correction, final
coordinate and command builders on the same RAM. Its raw
`ignition_diagnostic_paths` stays in the existing COPY original. Exact private
sources, reconstruction, original streams, full state/frame/RAM and the actual
native control-memory window remain mandatory. The separately assembled APC
scheduler sink has an explicit synthetic return after the diagnostic stores;
no scheduler MMIO, timing or hardware behavior is admitted. Independent word
curve and conditioning equations include the physically read neighboring word
without extending semantic geometry. The exact scope is in
`defs/JK08A.ignition-diagnostic-path.md`.

