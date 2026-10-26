# JK08A bounded closed-loop adjustment

## Entry

The natural stock entry `000a0ee8` decodes independent input bytes, updates
two channels of persistent workspace, selects unsigned increment and
decrement words, and publishes two bounded signed state words. Four real
helpers execute: `000264cc`, `00026740`, `00026984`, and `00026c78`.

## Input decoding and state

The workspace base is `ffff977c`, with a 122-byte observed window.
Raw bytes at `ffff48c0`, `ffff48be`, `ffff48b7`, `ffff302e`, `ffff326a`,
`ffff2a89`, `ffff48b4`, `ffff32ce`, `ffff32cf`, `ffff334c`, `ffff334d`,
`ffff3522`, `ffff3523`, `ffff2fd1`, and `ffff2fd2` contribute bits 0 and 1
to the respective bank bytes. The decoded workspace offsets are
`2c`, `2e`, `30`, `33`, `35`, `37`, `39`, `3b`, `3d`, `3f`, `41`,
`43`, `45`, `47`, and `49`. Only the reader interpretation is established;
source producers and physical permission meanings require separate evidence.

Raw extras at `ffff14e8/ffff14e9` and `ffff2f1c/ffff2f1d` are interpreted
as zero or nonzero. Bit 2 of `ffff424f` becomes workspace byte `32`.
Previous bytes at offsets `6`, `2`, `12`, `10`, `e`, `c`, and `a`
per bank are independent unsigned bytes, including non-Boolean values.
Current decoded flags, edge predicates, latched pulse predicates, selector
bytes, previous-state copies, and activity counters have exact byte-level
expectations. Counters at `ffff29f3/ffff29f4` wrap modulo 256.

## Step selection

Each direction selects one of four modes. Mode 1 supplies zero.
Mode 2 calls the real unsigned eight-word lookup with coordinate
`RAM16[ffff2a92+2*bank]`. Mode 3 supplies ROM16 `00008e78` for the
increment and ROM16 `00008e7a` for the decrement. Mode 4 supplies ROM16
`00008fa2` for the increment and ROM16 `00008fa0` for the decrement.
The stock words are respectively zero, zero, one, and one.

The increment table starts at `0001462a`, with thresholds at `00015d00`.
The decrement table starts at `0001463a`, with thresholds at `00015d10`.
Both readers use eight unsigned thresholds and the real 16-bit fractional
division and directional integer interpolation. The word immediately after
the increment table is the first decrement word.

The selected decrement and increment words are published at
`ffff97a0/ffff97a2` and `ffff97a4/ffff97a6`. Selectors are published at
`ffff97c7/ffff97c8` and `ffff97c9/ffff97ca`.

## Bounded integration

For bank `B`, the signed incoming state is `int16(RAM16[ffff45a0+2*B])`.
Let `U` and `D` be the selected unsigned increment and decrement words.
The admission predicate is

```text
G = !(workspace[39+B] || workspace[2c+B] || workspace[2e+B] || workspace[30+B])
    || !workspace[32]
I = G ? clamp(state + U - D, -32768, 32767) : 0
output = min(int16(ROM16[00008e7e]), max(int16(ROM16[00008e7c]), I))
```

The intermediate words at `ffff9798/ffff979a`, the lower-bounded words at
`ffff979c/ffff979e`, and the final states at `ffff45a0/ffff45a2` are distinct
observations. Shared signed32 scratch words at `ffff9790` and `ffff9794`
contain the first sum and difference only on admitted paths. Bypass paths
preserve those scratch contents. The bound order remains explicit when a
synthetic lower bound exceeds the upper bound; it is not a reordered clamp.

Chain steps 5 and 6 provide two typed views of this common update.
The table-2 path supplies the respective selected word; the other direction
and every gate input remain explicit RAM dependencies. No claim of physical monotonicity
over arbitrary raw contexts follows from the chain sign.

## Evidence limits

Hardware readiness is NO. The independent raw software domain does not
establish physical units, scale, source producers, acquisition cadence,
engine reachability, or hardware learning permission. Candidate scales and
other existing owner properties retain their separate evidence status.
The complete feedback producer `0005cbec`, which supplies earlier inputs
of the wider closed-loop path, requires its own whole-path evidence.
A terminal slice reading `ffff2898` does not establish its relation from
`ffff29e2`. GNU simulator observations also do not prove the hardware
SH-2E exception frame.
