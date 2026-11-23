# VQ37 intake CVTC solenoid output stage

## Scope

This specification owns the intake CVTC solenoid output stage of the VQ37VHR
layouts `jk78c` (image JK78C), `1nd` (images 1ND0A and 1ND3B), and `1me3b`
(image 1ME3B): the scheme selector, the ATU-II channel-7 cycle and buffer
registers of the intake pair, the command path from the 16-bit duty words to
the 8-bit command cells, and the units of the cells. `JK08A.cvtc.md` owns the
JK08A output stage, which programs the intake pair from the 8-bit cells
`0xFFFF23B4` and `0xFFFF23B5`. The producers of the duty words and the
physical response of the solenoids are outside this specification.

## Scheme selector

Bit 2 of a calibration byte selects the duty scheme, and a factor byte `K`
scales both registers of the pair:

| Layout | Scheme byte | Factor byte `K` |
|---|---|---|
| `jk78c` | `ROM8[0x852A]` | `ROM8[0x8B5E]` |
| `1nd` | `ROM8[0x8561]` | `ROM8[0x8C4B]` |
| `1me3b` | `ROM8[0x8576]` | `ROM8[0x8CA1]` |

Every stock image sets bit 2 and holds `K = 1`.

## Cycle registers

Functions `0x00029002` (`jk78c`), `0x0002975A` (`1nd`), and `0x0002C4AA`
(`1me3b`) program cycle registers `CYLR7A` (`0xFFFFF588`) and `CYLR7B`
(`0xFFFFF58A`):

```text
bit 2 set:   CYLR7A = CYLR7B = min(1000 * K, 0xFFFF)
bit 2 clear: CYLR7A = CYLR7B = 125 * K
```

The stock cycle is 1000 counts.

## Buffer programmers

The buffer programmers write buffer register `BFR7B` (`0xFFFFF592`) from the
first cell or word of the pair and `BFR7A` (`0xFFFFF590`) from the second.
With bit 2 set they read the 16-bit duty words `w` and not the cells; with
bit 2 clear they read the 8-bit command cells `x` and not the words:

```text
bit 2 set:   BFR = floor(w * K * 125 / 8192)
bit 2 clear: BFR = floor(x * K * 39 / 80)
```

| Layout | Programmer | Duty words | Command cells |
|---|---|---|---|
| `jk78c` | `0x000E7994` | `0xFFFF25C4`, `0xFFFF25C6` | `0xFFFF2308`, `0xFFFF2309` |
| `1nd` | `0x001108D0` | `0xFFFE96BC`, `0xFFFE96BE` | `0xFFFE93BF`, `0xFFFE93C0` |
| `1me3b` | `0x0011C3A6` | `0xFFFE9692`, `0xFFFE9694` | `0xFFFE938F`, `0xFFFE9390` |

The equations hold while the mode bytes that each programmer tests are clear:
`0xFFFF45BF`, `0xFFFF45C2`, and `0xFFFF2406` on `jk78c`; `0xFFFE94CD`,
`0xFFFE8D94`, `0xFFFE9469`, `0xFFFE94E9`, `0xFFFEB8EE`, and `0xFFFEB8F3` on
`1nd`; `0xFFFE949D`, `0xFFFE8D38`, `0xFFFE9439`, `0xFFFE94BA`, `0xFFFEBA5B`,
and `0xFFFEBA60` on `1me3b`. The bit-2-clear equation is the JK08A conversion
of `JK08A.cvtc.md`.

## Command path

With bit 2 set the command cells follow the duty words through two copies of
the scheduler and a live-byte writer:

1. The scheduler functions `0x00020F1A` (`jk78c`), `0x00021218` (`1nd`), and
   `0x00021240` (`1me3b`) copy the duty words into `0xFFFF25A4` and
   `0xFFFF25A6`, `0xFFFE9694` and `0xFFFE9696`, and `0xFFFE966A` and
   `0xFFFE966C`.
2. The live-byte writers store the high byte `w >> 8` of the copied word of
   each cell into the live duty bytes: function `0x000E6226` into
   `0xFFFF239A` and `0xFFFF239B`, function `0x0010EA78` into `0xFFFE945B` and
   `0xFFFE945C`, and on `1me3b` function `0x0011AA10` into `0xFFFE942B` and
   its caller `0x00119B00` into `0xFFFE942C`. With bit 2 clear the writers
   skip the store.
3. The block copy of the scheduler moves the live bytes into the command
   cells: `0x92` bytes from `0xFFFF2314` to `0xFFFF2282` on `jk78c`, `0x9C`
   bytes from `0xFFFE93CC` to `0xFFFE9330` on `1nd`, and `0x9C` bytes from
   `0xFFFE939C` to `0xFFFE9300` on `1me3b`.

The live byte and the command cell therefore hold the high byte
`x = w >> 8` of their duty word, delayed by the scheduler copies.

## Units

With bit 2 set the duty of a solenoid is

```text
duty    = floor(w * K * 125 / 8192) / (1000 * K)
percent = w * 100 / 65536, less at most 0.1 / K
```

and the high byte `x = w >> 8` of the word carries

```text
percent = x * 25 / 64
```

At `K = 1` the programmed duty of a word with high byte `x` lies above
`x * 25 / 64 - 0.1` and below `(x + 1) * 25 / 64` percent; `x = 255` reads
99.61 percent. With bit 2 clear the cells carry the JK08A unit:

```text
percent = x * 39 / 100
```

The meanings of the command cells and the live bytes keep `x * 39 / 100`. The
symbols of `jk78c`, `1nd`, and `1me3b` override the scale with `x * 25 / 64`,
the unit of the stock images.

## Telemetry wire

The custom CAN telemetry carries the command cells and the live bytes raw and
decodes them with `x * 39 / 100`. Over the byte range the two units differ by
at most `x / 1600` percentage points, 0.159375 at `x = 255`, which is less
than half of the wire step 0.39, and the percent of a cell encoded on the wire
scale returns the cell itself. The wire keeps its decoding on every layout.

## Evidence boundary

- The gate executes the cycle programming at `K` = 1, 3, 66, and 255, the
  buffer programmers at `K` = 1 and 3 with the mode bytes clear, the scheduler
  copies, and the live-byte writers, each on both schemes where the scheme
  byte reaches it, on copies of the image that differ only in the scheme or
  factor byte.
- The spans start inside their functions. The gate executes the image
  instructions that set their base registers and checks that no instruction
  of the function between those instructions and the span writes the
  registers.
- The first cell of each pair drives `BFR7B` and the second `BFR7A`, as on
  JK08A; the bank names of the pair follow that order.
- The mode-byte paths of the programmers, the producers of the duty words,
  and the duty on the engine are outside the gate.
