# JK08A lavender nominal count scale

## Owner and evidence

`defs/JK08A.findings.csv` owns the scale of `lavender-butterfly/tbl` at
`7mfk:000131a2`. Identity is `code`; scale is `candidate`. The retained editor
unit is `centered ffff8d6c channel counts`, the nominal expression is
`x*10-73500`, and the inverse is `(x+73500)/10`. The unit names the home local
channel, not a physical unit or a shared address on every layout.

The scale evidence is
`test:tools/mapkit/tests/test_lavender_scale.py#test_lavender_nominal_initialized_scale`.
The named test executes actual H lookup, normal Q12 initialization, extraction,
local C1 word publication, signed register interpretation, and signed word
read/copy. It establishes the initialized no-floor relation in the linear
count domain, not a universal H-to-output relation. No confidence is promoted.

## Image and byte binding

The independent image identities are executable locks in
[`tools/mapkit/tests/test_lavender_scale.py`](../tools/mapkit/tests/test_lavender_scale.py).
The primary loader also checks the ROM registry
[`rom-images/roms.csv`](../rom-images/roms.csv). The digest values are stored in
those machine-readable sources, not repeated here.

| Image | Independent executable SHA lock |
|---|---|
| `JK00A` | `IMAGE_FIXTURES["JK00A"]` |
| `JK03A` | `IMAGE_FIXTURES["JK03A"]` |
| `JK03B` | `IMAGE_FIXTURES["JK03B"]` |
| `JK08A` | `IMAGE_FIXTURES["JK08A"]` |
| `JK00C` | `IMAGE_FIXTURES["JK00C"]` |
| `JK00D` | `IMAGE_FIXTURES["JK00D"]` |

Each image passes its own SHA lock and fixed expected instruction/literal
spans. The fixed `HOME_SPANS`, `JK00C_SPANS`, and `JK00D_SPANS` cover stock GBR
setup, table and axis pointers, wrapper and axis helper, finisher, state and
flag addresses, initialization, extraction, arithmetic literals, publication,
and the later copy. Expected bytes are retained fixture literals; the test
never derives them from the image it is checking.

## Stock cell domain

The fixture checks every H and T cell, the zero step curve, and the exact axis
points separately against every image. `STOCK_H` retains the complete H arrays.

| Image | H table | Stock raw domain | Local publication address |
|---|---|---|---|
| `JK00A` | `000131a2` | 7310..7350 | `ffff8d6c` |
| `JK03A` | `000131a2` | 7290..7350 | `ffff8d6c` |
| `JK03B` | `000131a2` | 7290..7350 | `ffff8d6c` |
| `JK08A` | `000131a2` | 7290..7350 | `ffff8d6c` |
| `JK00C` | `00015534` | 7310..7350 | `ffff8d7c` |
| `JK00D` | `00015554` | 7310..7350 | `ffff8d7c` |

All stock H cells lie in the initialized linear publication domain. Equality
of H and T and the zero step curve are image-byte facts, not evidence for a
physical quantity. Publication addresses come from executed stock GBR setup
plus the C1 displacement; the homologue address is not `ffff8d6c`.

## Executed local path

For the home layout, `000626c0` calls the actual uint16 curve wrapper
`000264f8` on H, axis `00015ce0`, and the incoming byte coordinate. The wrapper
calls word-axis helper `00026984`, reads word cells, and tail-calls finisher
`00026740`. The caller stores H at stack offset `0x14` at `000626c4`.

The no-floor normal initializer executes `00062788..0006279a`, writing
`H << 12` to `ffff33a8`. The extraction path executes
`00062874..00062890`, logically shifts the state right by 12, caps it at
65535, and stores selected count N at `ffff33a4`. Arithmetic and local
publication execute `00062892..000628c2`, including the actual
`MOV.W R0,@(0x14,GBR)` at `000628c0` and the signed interpretation in R10.

The separate copy segment executes the stock base-register load, signed GBR
word read `00062b94`, and word store `00062b96` to `ffff9a44`. The calculations
between the publication and this copy are not executed by this segment. The
fixture does not replace any helper, finisher, call, return, or delay slot and
does not store a computed result manually.

Every stock axis point and the clamped end inputs are covered. Execution is
restricted to exact/end points. A nonzero-fraction explicit-axis entry raises
an assertion before the fractional helper executes. The same exclusion is
bound independently to the relocated helper entry on JK00C and JK00D.
At the terminal point, the wrapper also reads the following word while its
fraction is zero; the gate does not claim that every read stays inside H.

Incoming mode operands and existing state are explicitly seeded. Earlier
argument producers, calculations before the T lookup, and the unrelated
saved-word copy at home `000626b4` are outside this gate. This is a local path
contract, not whole-function or vehicle-mode reachability evidence.

## Nominal and exact local publication

The editor conversion is nominal `10*H-73500`. For selected uint16 count N,
the exact stored signed component is:

```text
C(N) = min(32767, max(-32768, 10*N-73500))
```

The integer linear domain is 4074..10626. The gate executes the boundaries
4073/4074 and 10626/10627, plus raw extrema, separately from the stock-domain
samples. Initialization without a floor gives N=H, so the linear domain binds
the stored component to the nominal conversion. Outside that domain, the
component saturates and the nominal inverse does not recover H.

Word representation is essential. The linear branch sign-extends the low word
of `10*N` before adding the 32-bit offset -73500. For H=N=7350, R0 before
publication is `ffff0000`, while the actual stored word and signed read are
zero. The oracle checks the stored low word and its signed interpretation,
not an unbounded comparison with the pre-store register. The tests also check
that the word publication and copy preserve adjacent sentinel words.

Independent incoming Q12-state tests cover low fractional bits and extraction
above 65535. Those states are not claimed reachable from the uint16 H
initializer. The nominal inverse is exact on its integer count grid;
saturated values and off-grid counts do not define an integer raw inverse.

## State and mode counterexamples

The initialized state is not replaced by H on every call. Stock H=T selects
the subtraction branch, and stock S=0 can preserve a prior larger state.
The retained-state test supplies prior `7350 << 12` and the last axis point:
selected N remains 7350 and the actual component is zero, although the current
H has a negative nominal value. A separate below-target state executes the
actual target replacement in its delay slot.

The alternate path selects the alternate curve, saves an initialized normal
state when needed, and writes the alternate lookup shifted by 12. The gate
executes alternate/save and restore paths and checks their real stores and
flags. At the selected witness the alternate component is 350 while nominal
H is zero; restore recovers prior state rather than current H. The incoming
mode predicate has separate normal and alternate boundary witnesses.

These counterexamples disprove a universal H-to-component relation without
changing the retained editor expression or scale confidence.

## Optional floor and downstream boundary

The optional floor is an explicitly excluded static boundary. The stock code
selects a floor-source curve, multiplies it by another lookup, divides the
unsigned product by 50000, caps the floor, and selects the larger floor or
extracted state count. That selected N is not a property of H alone.
The fixture forces the no-floor flag and rejects the optional floor entry;
it does not claim execution coverage for the floor lookups or divider.

The local component participates in subsequent mixed arithmetic and is copied
into a saved channel. It is not a final actuator output. Downstream arithmetic,
complete function output, physical-unit identification, and hardware behavior
are outside this gate. There is no hardware validation or flashing eligibility
claim.

## Negative checks and compiled owner

Snapshot mutants change retained literals, register operands, width,
displacement, branches, or delay-slot instructions and are rejected by fixed
byte binding. Separate execution mutants bypass snapshot binding and run the
changed instruction through the same primary interpreter. Their observed
publication, stores, registers, or extracted counts are compared with an
independent oracle. Arithmetic, centering offset, saturation, width, and
signedness have distinct witnesses; a signedness mutant can change a register
or Q12 state while preserving the saturated or low-word component.

The compiled-owner test checks the real typed `supports=scale` token, the
retained owner fields, and the named top-level AST function. A nonexistent
function key is rejected by both the evidence matcher and homology check.
The specification test reads the image-lock keys, stock domains, publication
addresses, inverse contract, and explicit exclusions from the executable
fixture. `tools/single_source.py` includes this document while it is untracked.
