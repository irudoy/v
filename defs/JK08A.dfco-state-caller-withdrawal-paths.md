# JK08A DFCO state caller withdrawals

Source bindings: `JK08A.dfco-state-caller-withdrawal-paths.toml`.


## Complete caller, frame and real helper

The natural 503E0 body retains 503E0..50400, 50402..50444, 50484..50552,
50554..5068C, 50698..506AE and 506E8..50766. All five literal holes remain data.
The real 50766..5079C helper is complete. All prologue saves, local operands,
conditional outcomes, delay slots, loop calls and natural returns remain explicit.

The caller first writes the low word of incomingR6 at local SP+2. It then
overwrites local SP with the complete incomingR6 dword. The subsequent timer
loads read the actual bytes at local SP+2 and local SP+3. Equal final frame bytes
cannot replace either initial write, the full overwrite or either intermediate
read. RawR4/R5/R6/R7 and every preserved register remain independent inputs.

## Full state, threshold and counter paths

The complete byte 14C1 state and 2468/2458/24CF/4250/259C gates remain explicit.
The early state 4 threshold path retains the real sign-extended MOV.B carriers
before CMP/HS. All low-state initialization, 2571/2572 expiry and state 3/state 4
paths preserve their natural raw-register conditions and individual byte stores.

Configuration 8711 and 8B3F select the actual threshold mechanism. The 11B3 byte
and 8C1E byte retain their real sign-extended 32-bit words before CMP/HI. The
word 11B6 and unsigned 110E byte retain their actual products with independent
8C1C/8C1D bytes. The alternative 1517 path retains its two independent 8C1A/8C1B
thresholds and comparisons. The selected index is 0, 1 or 2 only on this exact
delay-selection path. Six independently controlled delay bytes occupy
1269A..1269D and 1269D..126A0. The caller actually writes the index at 1939,
the selected hold byte at 193A and the selected restore byte at 1938.

RAM1939 has a separate check of access direction. Its exact reader is removed;
the actual writer, enum_u8 unit, unset width and signedness, symbol evidence and
other ledger selectors remain fixed. Reads at native FFFF1939, alias 01001939
or any overlapping container are refused. Only the actual byte writes at 50574 from R6
with classes 0..2 and at 50594 from R2 with value 10 are admitted. The seven strict
no-read-or-write guards for the other roots remain exact.

Three held-other groups supply all 256 prior byte values for bypass and each
actual writer. Every group requires the same complete CPU, frame, other RAM,
source bytes and calibration. Bypass preserves the unread byte. Writer paths
must publish their actual store value independently of the prior byte.
Missing raw values, either missing writer path and input echoes are refused.
The complete prior 123 reference records and 66 function records retain their
exact full-record digests.

The saved state, 2573 counter, 193A sentinel 255, new-delay sentinel inR6,
nonzero decrement and 1938-to-1937 transfer remain separate. The counter byte
may remain above 6. Reset paths retain every actual 193A/1938/1937 store and
do not substitute one terminal RAM image for their ordered physical effects.
Every publication remains independent of the final return mask.

## Real bounded rotation and complete byte-indexed table

The loop reads unsigned 1937 before each admitted iteration. Real BSR50642
enters 50766 with the actual EXTU.B argument and updated count in its delay
path. Valid masks 1/2/4/8/16/32 rotate to 2/4/8/16/32/1. Every other byte mask
returns zero through the real helper branch path. All comparisons, jumps,
delay slots and natural helper returns remain executable obligations.

The caller accumulates returned masks and stops after at most six real calls.
A raw count 255 therefore retains six calls and the original counter byte.
Complete actual CPU states after each delay slot and each helper return bind
every repeated call;one call or a final accumulated value cannot replace the
intermediate argument, return and loop-read sequence.

The final state-table lookup uses the complete unsigned byte stored at 14C1.
States outside 0..4 remain admitted by the exact raw function input domain.
The complete 256-byte physical table at 2371C..2381C is independently controlled,
including its last byte at 2381B. Each physical byte has a fixed-other alternative
at its actual index. No reduced state domain, representative cell or native
geometry assumption replaces that full extent. Sign-extended lookup bytes
remain complete words until the final EXTU.B return.

The resulting mask and 249F flags retain their independent clear/set paths,
14C4/251B publications and 153C/17BD bit clearing. The exact initial and final
RAM, full saved frame, all known CPU/SR/special-register values, physical operands,
instruction sites and bytes, helper entries and natural returns remain bound.

## Restore caller source closure


The caller retains both diagnostic calls at 50042 and 5005E, both byte lookups
at 500AC and 500BC, their real delay slots, the complete prologue/local frame,
saved GBR and natural return. The diagnostic calls use fixed indexes 0129 and
012A, with actual record-byte inputs at FFFF5A95 and FFFF5A98. The sentinel
argument FFFF belongs to the retained helper source and is unreachable from
these two constant caller arguments. Table/fallback paths retain actual byte
publications at 501AA to FFFF1778 from R4 and at 501AE to FFFF16AA from R14.
The 501AE publication is a writer obligation even when a reader claim is withdrawn.

The shared input descriptor declares 503E0 and 50018 through the existing
ordinary adapter. It contains 894 shared stock instructions, 81 shared literal spans,
30 shared RAM pointer aliases, 39 shared RAM fields, 322 shared configuration fields,
98 shared calibration spans and 371 shared raw input fields. The old input field
prefix, state RAM preimages, state loop inputs and state calibration subsets remain
explicit. The 14 additional ordinary RAM bytes default to A5 in state cases.
Both restore curves contain 16 independent physical bytes. The four speed thresholds
and four floors retain separate raw bytes and their complete index range.

Four held-other groups supply every prior byte at FFFF16AA across first-diagnostic
fallback, second-diagnostic fallback, ordinary lookup and offset lookup. Complete
coordinate values 0..255 retain rising, falling and alternating table inputs.
Every curve byte, speed threshold, floor, mode, diagnostic and complete CPU/SR input
has independent alternatives. Case construction uses only raw inputs.

The generated driver and owning postimages
require completion before common acceptance. The source declaration does not
establish selected-reader absence, prior-byte independence, native identity or a
claim correction. Admission retains all feasible branch and call/return paths,
complete state, actual writer and exact owning postimages. The 409-instruction state
unit and its selected claims retain their separate complete boundaries.

## Independent restore state equations

The restore consumer composes the real diagnostic calls, byte lookup and signed
endpoint promotion independently of instruction decoding. The existing sixteen-byte
curve equation supplies the numerical interpolation. Each physical input, branch,
call/return, delay slot, local dword, saved register, GBR and final state has its
own ordered obligation. The complete RAM image retains the two actual byte stores
and the distinct classifier return values 0, 1, 2 and 3. Fallback retains its fixed
threshold publications; its optional offset changes the separate classifier bound.

There are 459 feasible restore instructions. The 26 fixed-mode helper instructions
remain bound stock source: 25C54 is the diagnostic sentinel outcome, 26A60..26A84
is the skipped word/eight-point prefix and 26A9C..26AAA is the unselected word-data
branch. Both caller diagnostic indexes differ from FFFF. The actual 26388 wrapper
enters 26A84 and supplies a zero width flag. These premises admit no other caller
argument or lookup width. The full source functions remain mandatory. The
409-instruction state unit and restore unit require 868 feasible shared instructions.

The independent source checks include diagnostic fallback before either lookup,
both real lookup calls, offset saturation, all four speed-indexed floors, byte
endpoint sign extension before EXTU.B, complete frame/GBR restoration and each
classifier result. Executable qualification, complete causal alternatives,
selected-reader guards and owning publication remain separate obligations.

## Restore reader direction and shared capture

The shared consumer requires 109 two-sided shared conditions and two fixed helper outcomes.
The 47 state conditions retain their complete outcomes; 62 restore conditions
retain both outcomes. The diagnostic sentinel branch at 25C3C falls through and
the byte-width branch at 26A9A is taken. All feasible instructions, actual calls,
delay slots and complete returns remain mandatory in the same original capture.

The seven strict selected-datum guards and the direction-specific 1939 guard
apply to their exact 503E0 entry. The restore reader has its own exact identity
`a66ad148b5399b0aa33727484628763c1d8210c778dd76e365159d56098cf5f8`.
Native FFFF16AA reads, alias 010016AA reads and overlapping wider reads are refused.
Every restore invocation requires one byte store at 501AE from R14 to 010016AA.
Another site, register, width, domain, missing store or duplicated store is refused.
The physical byte extent supplies no declared native width or signedness.

There are four complete prior16AA groups: first-diagnostic fallback,
second-diagnostic fallback, ordinary lookup and offset lookup. Each group retains
all 256 distinct input bytes and holds every other RAM byte, context, frame,
SP, continuation, ABI, SR, source and calibration fixed. Complete returned RAM,
CPU, frame, ABI, actual writer, ordered accesses, controls, calls, trace and code
must remain equal. The actual raw diagnostic/table call sequence binds each group.
Partial, duplicated, substituted or changed groups are refused.

Actual-original refusal sources cover six restore windows, physical read/write
direction, complete returned and intermediate state, helper entries/returns,
calibration, executable bytes and full prior domains. The active table and floor
alternatives change actual computed publications with all other inputs held.
The last speed threshold remains a physical loop/condition operand; it does not
claim an additional floor index or an output-value dependency.


## Intermediate restore reader direction

The RAM1778 reader has its separate exact original
`ee78dd754d5bc5778e829fa0e0fad67c39036ac7bf491d27c0fd7f3a9af3dbf7`.
The existing 50018 closure, independent equations, raw byte1778 input, 80/572
observer and generated driver remain the same. A second exact writer identity
extends the existing restore direction guard: each invocation requires the real
byte store at 501AA from R4 to 01001778. Native or aliased reads and overlapping
wider reads are refused. The actual 501AE/R14 writer for RAM16AA remains mandatory.

Four complete prior1778 groups retain every byte value 0..255 while holding every
other RAM byte, including prior16AA, and every CPU/frame/ABI/calibration/source
input fixed. They use the same two diagnostic fallback paths and two lookup
paths as the prior16AA groups. Complete returned state, actual writes, calls,
controls and instruction trace remain equal within each group. The two exact
reader identities cannot donate an observation or retained-writer result to each
other. Both raw domains have actual-original substitution and partial-domain
refusal sources. These obligations do not supply semantic width, signedness,
native geometry, identity or hardware qualification.
