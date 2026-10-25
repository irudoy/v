# Conditional publication of paired scaled words

The explicit `0007A778` window in `0007A592` accepts an unsigned word in
R6 and ceiling 65535 in R12. It multiplies the word by 727 and calls signed
divider `00021BBC` at `0007A784`; delay slot `0007A786` supplies the product
in R1. R0 holds 800. Store `0007A794` publishes the returned word at
`FFFF1210`. The unsigned word input and coefficient below the divisor leave
the ceiling replacement unreachable under these explicit premises.

The explicit `0007A968` window in `0007A804` accepts an unsigned word in
R5 and the relocated `FFFF28F8` base in R9. It stores the input at `FFFF35CC`,
multiplies it by 727 and calls unsigned divider `00021CE0` at `0007A976`.
Delay slot `0007A978` supplies the product in R1; R0 holds 800. Store
`0007A980` publishes the quotient word at `FFFF1248`.

Both bounded windows retain complete natural divider instructions and
literal pools. Separately assembled observing returns at
`0007A796..0007A79E` and `0007A982..0007A98A` read the saved continuation
from SP+24 through R7. Their bytes `57F6472A000B0009` lie outside the tested
stock spans. The complete parent path, origin of the incoming selected
value, following parent instructions and scheduler are not admitted.

The raw component remains inside the existing complete COPY original.
Independent physical, complete CPU/SR/ABI/frame/RAM and integer consumers
require both actual calls after their delay slots, exact word stores,
preserved fault state and distinct returned outputs under explicit input
variation. Neither bounded window reads its previous output value. The
unsigned entry also requires its separate `FFFF35CC` input store.

The exact native proposals replace the two legacy arithmetic reader claims
with conditional `arithmetic-output` dependencies. Complete original claim
and ledger identities preserve other facts and legacy selectors. Native
write operations are not registered. Source preparation supplies no
qualification, physical RAM access by an arithmetic callee, units, scale,
complete parent reachability, natural scheduling or hardware behavior.
