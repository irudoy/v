# Conditional ignition diagnostic source boundary

`JK08A.ignition-diagnostic-path.toml` describes the retained instruction
sequence `0004D99C`, `0004DBE8`, `0004DF82`, its declared natural helpers and
the owned stock image. The descriptor grants no execution or native publication.
Exact instruction reconstruction, complete raw state capture and independent
admission remain required.

The conditional word wrapper `000264CC` receives the curve at `000147DA`,
axis at `00013C48`, and the word coordinate at `FFFF237E`. Its axis search uses
the last byte offset 14 and a word stride. The semantic table occupies 16 bytes.
The wrapper loads both word operands even at the final endpoint: its physical
read extent is 18 bytes, and the final neighboring word has zero weight there.
That physical read does not establish an additional semantic curve point.
The source contract gates these bounds against the actual wrapper and axis
instructions in the owned image.

The source sequence carries the lookup result through `FFFF2000`, the selected
coefficient and signed clamp to `FFFF12D6`, the final-coordinate conditioning
to `FFFF11D4`, and the command-byte store to `FFFF2022`. Separate mode branches
can replace or limit these results. The diagnostic alias list requires current
SID22 admission; its presence in this preparation grants no ROM reader relation.

Two native control bytes, `FFFF99C4` and `FFFF9926`, are addressed through
sign-extended 16-bit PC literals. They are distinct from relocatable 32-bit
RAM-pointer pools. A complete fixture must preserve these instruction words,
declare the native control-memory window and observe its input, output and
coherence with any relocated view.

The command builder calls the natural upstream gate `0008C3FA` before the
command store and the APC scheduler `0002A892` after it. The scheduler's
hardware effects are outside the diagnostic-byte claim. Its declared simulator
sink supplies a synthetic R0 return and changes no instruction or literal in
the stock spans under test. The raw producer assembles the sink separately,
binds its actual bytes and source, and retains it outside the stock
reconstruction spans. The independent consumer requires that exact boundary,
its complete state and the actual argument after the command-byte stores.

Each typed case executes all three stages on the same RAM. Only the first
stage initializes RAM and calibration inputs. Complete raw observations bind
the next stage's entry to the previous stage's actual output. The native
control-memory window has separate complete before/after snapshots that must
agree with its relocated view. Stock and synthetic word curves preserve the
physical neighboring word. The independent numeric consumer checks the word
curve, selected coefficient, signed clamp, normal limits and command override
against the full instruction-state observations.

The existing COPY original retains `ignition_diagnostic_paths`; no additional
receipt is created. Current original-primary, source, fixture, ELF, stream and
ordered-invocation requirements remain mandatory. Conditional paths grant no
joint diagnostic relation or hardware admission on their own.

The descriptor records `native_relation_publication = false`,
`native_geometry_publication = false`, `scale_admission = false`,
`all_modes = false`, `natural_caller_reachability = false` and
`hardware_qualification = false`.
