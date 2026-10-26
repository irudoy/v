# Indexed timer refresh writer

`JK08A.indexed-timer-refresh-writer-paths.toml` binds 98 stock instructions in 1 entry and 1 span,
7 literal pools, 3 four-byte RAM pointer aliases and 8 calibration spans.
The complete leaf is `9018C..90250`; it has no callees. Its independent assembly
reconstructs every instruction and literal from the owned JK08A image. The
consumer admits the complete image digest, immutable code, reconstruction,
consumed sources, original terminal streams and pinned GNU tools together.

The existing ordinary observer uses an 80-byte context, 572-byte observer and
192-byte frame. It records 20 complete context words and all 65536 ordinary RAM bytes
before and after each invocation. The separate 256-byte native window is
`FFFF8500..FFFF85FF`. Its complete before/after bytes remain separate from
the ordinary snapshots. The existing byte-surface equations use a logical
view of the native window at the corresponding low offsets; the consumer
also checks the unchanged physical ordinary shadow independently.

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

The retained original is
`a4d8fa46eb520c07e6ddda8e50c5f471654b0caf8ae461f2809fc46bc49b89ba`:
`silent-elephant/ram` has a writer relation to `satisfied-myna/fn`.
The exact physical reload reaches `FFFF43BE` at full `R4=6`; this one relation
receives one identity-support evidence append. The complete owner,
function, other writers and readers, symbol evidence, ledgers and TEST
origins retain their exact recorded facts. Native width and signedness
remain unset, and the existing unit remains `102.4 ms counts`.

The software index premise supplies no bank mapping, natural caller or
scheduling qualification. The proof admits no scale, unit conversion,
storage geometry or hardware behavior. Hardware qualification requires
the project bench and live-data evidence.
