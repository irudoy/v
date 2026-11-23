# Conditional exhaust-target paths

The `JK08A.exhaust-target-path.toml` descriptor binds the exact owned JK08A
image, the complete retained instruction listing of `000BFE88`, its PC-relative
pools and the natural `000259D0` hysteresis helper. Pools that hold RAM pointers
receive explicit simulator aliases. Tested instructions and natural returns
retain their stock bytes. No stock call is stubbed. Any observed call outside
the admitted helper fails the bounded consumer.

The conditioned input roles select either the cold result at `FFFF1C5F` or the
main result at `FFFF1C5D`. Explicit mode inputs enable the selected endpoint,
disable target processing, or admit its separate replacement path. Other RAM
starts at zero, except the declared mode bytes, a fixed history byte and a fixed
previous output. The input matrix does not seed a selected result into the local
frame or the previous output.

For each admitted positive endpoint, the independent consumer requires the
actual source load, the selected value at both intermediate local-frame writes
`000C04C6` and `000C05F6`, and the actual final byte store at `000C0CEE`. The
terminal destination is `FFFF2327`, the source of DID `1166`. The source at
`FFFF2022` belongs to the separate `147DA` ignition chain.

The raw driver emits independent register inputs, complete GPR and special
register state, SR, caller ABI, local frame and full RAM before and after every
invocation. It supplies no expected-output columns. The independent instruction
equations execute every admitted stock instruction, branch delay slot, helper
call and natural return. Separate endpoint and hysteresis equations constrain
the observed numeric outputs. Both outcomes of the explicitly required branches
and every ordered matrix row are mandatory. Physical reconstruction, fixture,
ELF, private consumed sources, original streams and the full original primary
remain separate requirements.

The raw packet stays in the existing COPY original as `exhaust_target_paths`.
It grants no native metadata publication. The descriptor records
`stock_function_stubs = false`, `native_relation_publication = false`,
`scale_admission = false`, `all_modes = false`,
`natural_caller_reachability = false` and `hardware_qualification = false`.
The conditional RAM path alone does not admit a ROM-to-DID dependency, a physical
ROM reader relation, interpolation geometry, physical units or hardware use.
Complete byte-surface and SID22 originals require their own independent admission.
