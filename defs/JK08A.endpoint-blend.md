# Signed endpoint blend readers

The retained readers of `dark-earthworm/fn` at `7mfk:000740e2` belong to
`rare-baboon/tbl` at171C8, original
`e3166aeedf0e8b7891164614c667d709b489701c1d2900353ddedada7ca87361`, and
`rigorous-shrimp/tbl` at16FC8, original
`50df95db1f3b3e6ba6eccc362bfc1dd663bd1f9ae700616cc8f7ff84523b37ec`.
The owning appends support these identity relations. Native width and
signedness remain unset. Complete owner symbols, fields, unit/scale,
forward/reverse relations, ledger, evidence, TEST and three function
documents remain bound to their exact preimages and postimages.

`JK08A.endpoint-blend-paths.toml` binds 332 stock instructions, 664 instruction bytes,
8 contiguous spans, and 8 complete source bodies. It binds 18 literal pools, 4 four-byte RAM pointer
aliases, and 23 calibration spans. The actual full functions are740E2,
74028,740AE,26628,26AF8,26B28,26B84 and26D10. No helper is replaced by a
returned scalar or a stock stub. The input-only driver supplies complete
raw CPU/SR, RAM, surface, axis and weight inputs without expected results.

The endpoint caller74028 selects y from word10D2 or the maximum of
words10D2/10E2 through4255.bit7, and uses word1210 as x. The real calls
74072/7408C pass the two surfaces, axes18916/18936 and the caller-local y
word to26628. Full backward axis search, positive fractional division,
the actual26654/26656 tail and lazy neighbor word reads remain observable.
Unsigned word interpolation adds an unsigned truncated increment on an
ascending segment and subtracts it on a descending segment. Replacing
both directions by a single floor of the final weighted sum changes the
descending result. At zero axis fractions the actual raw word return
retains MOV.W sign extension before the caller's EXTU.W.

The real endpoint stores74082/74098 write signed16 endpoints to1CFC/1CFE.
Their full32-bit live decode registers remain separately checked: a
raw8000 endpoint has live registerFFFF0000 and stored word0000. The
existing raw-32768 representation is retained without new scale or
engineering-unit admission.

The stock weight step is 300. Function740AE updates word1D0C by subtracting
the raw step toward zero when245C.bit2 is clear, or adding it toward65535
when set; the actual store occupies its RTS delay. Function740E2 reads the
updated weight. Weight0 selects endpointA, weight65535 selects endpointB
exactly, and intermediate weights use the signed floor of
`((65536-w)*A+w*B)/65536`. The actual live register store7412E publishes
word1CF6. The maximum endpoint branch is distinct from a65535/65536 mix.

The surfaces are identical in stock JK08A. Independent admission requires
separate changed-word alternatives for each surface while the complete
other surface, axes, RAM, frame, CPU and weight inputs stay fixed. Every
surface word must change an actual observed output in its own held-other
pair. These alternatives use the stock weight step and real endpoint
saturation branches. The consumer requires every physical surface/axis
byte, all feasible instruction and branch paths, intermediate weights,
actual post-delay arguments/returns, complete CPU/SR, frame, RAM, ABI and
SP/PR. The generic divider's zero path is unreachable from a positive
fractional axis interval; the full existing denominator originals remain
separate obligations of the same primary.

Only declared four-byte RAM pointer pools are relocated. The existing
80-byte context,572-byte observation,192-byte frame and64K RAM profile
remain fixed. Instruction bytes and signed16 literals remain stock.
The physical table/axis byte windows are fixture boundaries and do not
publish native geometry or types.

`JK08A.endpoint-blend-claims.toml` permits both exact owning identity
appends as one ordered batch. It supplies no reverse function identity,
axis13D14 scale, physical quantity, engineering unit, natural cadence,
hardware or channel-to-bank admission. Coordinate provenance from7A592
is a separate association; the actual740E2 composition does not call that
producer. Native publication and receipts require their existing gates
after source preparation and the common acceptance.
