# Indexed timer refresh writer


The ROM-bound native permission is a byte read/write at `FFFF850C` and a byte
read at `FFFF850D`. The descriptor ID, image digest, entry, exact code span
and typed window declaration select that permission. All other bytes in the
native snapshot are preservation canaries. Neither the signed `850C` literal
nor the native control addresses are relocated. The three aliases relocate
only the ordinary RAM bases at the declared four-byte literal sites.

The independent equations preserve these complete instruction effects:

- Full `R4` is copied to `R7`; the mask is `u32(R4+1)`. The software input
  premise contains every index `0..255` and the additional wrap input
  `FFFFFFFF`. The timer address is `u32(FFFF43B8+R7)` before ordinary RAM
  relocation. Full `R5 == 0` selects the disabled path; every other full
  register value selects the enabled path.
- The judged byte at `FFFF3581` gates the leaf. A matching mask clears the
  corresponding bits of the arm byte at `FFFF4179` and returns. The disabled
  path also clears that arm byte and records its sign-extended prior value
  in the real temporary stack word.
- An enabled invocation sets the arm byte. If neither its prior value nor
  `FFFF4178` intersects the mask, the real SR sequence saves the interrupt
  field, raises it to `F0`, performs `native[FFFF850C] |= 80`, and restores
  the complete SR. The independent state snapshots check every instruction
  in that critical section, including the full signed byte carrier.
- The indicator is `(u8(native[FFFF850D]) >> 4) & 3`. When it intersects the
  full mask, a nonzero indexed timer returns without a reload. A zero timer
  sets the judged byte in the real branch delay slot. A clear indicator or
  disabled invocation loads the signed byte at ROM `8E23` into full `R6`
  and publishes its low byte in the real `9023E` branch delay slot.
- The real stack saves full `R14` at entry SP minus four and GBR at entry SP
  minus eight. The temporary word is at entry SP minus twelve. The leaf
  restores GBR, SP and full `R14`, with the last restore in the real RTS
  delay slot. PR, MACH, MACL and the complete surrounding frame are checked.

The consumer requires both outcomes at all 6 conditional sites, every
feasible instruction and delay slot, every raw native reset preimage, and
the judged, disabled, critical-reset, already-armed, timer-live,
timer-expired and indicator-clear path classes. Independent numerical
equations and instruction-state reconstruction must both agree with the
actual exit, complete memory, frame and ordered physical operands.

Positive writer admission requires two actual storage alternatives with
every other complete input held fixed. The exact-owner reload alternatives
vary only the raw ROM `8E23` byte and produce different actual bytes at
`FFFF43BE`. The native reset alternatives vary only the complete prior
`FFFF850C` byte and produce distinct changed bytes through the actual OR80.
An echoed, unchanged, detached or arbitrarily supplied output fails these
obligations even when another path or final timer byte matches.


The software index premise supplies no bank mapping, natural caller or
scheduling qualification. The proof admits no scale, unit conversion,
storage geometry or hardware behavior. Hardware qualification requires
the project bench and live-data evidence.
