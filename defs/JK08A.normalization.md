# Conditional sequenced normalization product

The explicit `000627A6` entry reads word curve `0001495A` through natural
`000264F8` with axis `00013A98` and a supplied byte coordinate in R6. The
lookup is published at `FFFF2B68`. R8 is explicitly nonzero so the observer
can stop before the parent reads its distant stack flag. This premise does
not establish the parent's original flag selection.

The second observation starts at `000627C2` for `0001459A` or `000627C8`
for `000145CA`. Both entries use the explicit word coordinate in R10,
axis `00015CE0` in R13 and wrapper `000264F8` in R14. R12 supplies the
relocated `FFFF28F8` base; GBR supplies the relocated `FFFF8D58` workspace.
The selected table's word is stored at `FFFF8D68`. The actual coefficient
load at `000627D6` reads `FFFF2B68` and multiplies it by the selected lookup.
Unsigned call `000627E0` uses R0=50000; delay slot `000627E2` places the
low32 product in R1. The quotient is stored at `FFFF8D60`, capped at 65535
and stored at `FFFF8D6A`.

Every curve has sixteen semantic words and its physically read stock
neighbor; the independent input contract preserves each neighbor. The raw
driver resets RAM only before coefficient publication. It retains the
complete resulting RAM for the following selected entry. Independent
consumers require equality of all RAM and calibration bytes between those
observations, actual physical word reads, the live coefficient load,
post-delay arguments, full CPU/SR/ABI/frame/RAM state and positive independent
changes of both U alternatives and K.

The stock window stores its bounded result at SP+24. A dedicated observer
preserves a second continuation at SP+28, and separately assembled observing
returns at `000627B8..000627C0` and `0006284A..00062852` use SP+28 through R7.
Their bytes `57F7472A000B0009` lie outside the tested stock spans. The full
frame equations retain the stock write at SP+24. No stock helper is stubbed;
the complete parent entry, distant stack flags, preceding admission checks,
following parent instructions and scheduling remain unadmitted.

The exact native proposals replace the arithmetic reader claims of the
three tables and `FFFF2B68` with conditional `arithmetic-argument`
dependencies. Complete original claims and ledgers preserve all other facts.
Native write operations are not registered. The raw component remains in
the complete primary's existing COPY packet. Source preparation supplies no
qualification, physical datum reader on the arithmetic callee, units, scale,
complete parent reachability, natural scheduling or hardware result.
