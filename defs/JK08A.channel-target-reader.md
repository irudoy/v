# Indexed channel target reader

The exact retained original is
`285cf25d5dc9e3c82ef1dd07662e419b9cf9ee2874326c2cdb4c30fda1455c73`:
`throttle_target_channel_1/ram` at `7mfk:ffff28be` has reader
`throttle_target_scaler/fn` at `7mfk:000cb1ca`. The owning evidence supports
this identity relation. The complete owner, function, symbols, relations,
ledger, evidence and TEST positions remain bound to their native preimages.
Native width 16, absent signedness, unit and scale remain exact.

`JK08A.channel-target-reader-paths.toml` binds 23 stock instructions, 46 instruction bytes,
1 contiguous span, and 1 complete source body. It binds 3 literal pools, 2 four-byte RAM pointer
aliases, and 3 calibration spans. The complete leaf has no calls or stock stubs.
The uint8 index domain contains 256 raw values. The input-only driver supplies
complete source and prior-output word arrays, incoming CPU/SR context and
other RAM. It supplies no expected numerical result.

`EXTU.B R4,R5` selects the index. The actual word load at `CB1D4` reads
`FFFF28BC + 2*index`; index 1 selects `FFFF28BE`. `MOV.W` sign extension is
retained before the actual `EXTU.W`. Independent equations compute
`min(65535, 16*uint16(word) + 8192)`. Input 3583 yields 65520;
input 3584 takes the saturation branch and yields 65535. The actual live R6
word is stored at `CB1F6` to `FFFF387A + 2*index` in the real RTS delay slot.
The full input byte domain and upper 24 R4 bits remain observable.

The signed16 literal is `01A2`.

Held-other alternatives change only the actual owning word at 28BE while
index 1 and every other complete input remain fixed. The observed published
word must change. Separate index 0/2/255 controls retain the other selected
source word and reject an effect from the unselected 28BE input. Matching a
scalar, matching final bytes without the live register, or reading an
arbitrary synthetic pointer does not establish this relation.

`JK08A.channel-target-reader-claims.toml` permits its one normal owning reader
evidence append together with the exact known `6F48C` writer append. Both
declarations bind the same complete native owner postimage containing exactly
these two evidence appends. Partial, duplicate or additional appends refuse
the exact boundary; both individual claim images and every other owner fact
remain fixed. The complete `6F48C` writer source binds the existing reader
original from the same primary. Independent raw capture and native guards
remain mandatory under the same complete primary. The contract supplies no scale, units,
array geometry, natural scheduling, channel-to-bank, hardware or physical
throttle-motion admission. It does not remove another reader or replace an
existing proof obligation. Native publication and receipts remain separate
from source preparation and require their existing gates.
