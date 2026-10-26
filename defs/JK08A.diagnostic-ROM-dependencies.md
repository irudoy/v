# JK08A conditional diagnostic ROM dependencies

`defs/JK08A.diagnostic-ROM-dependencies.toml` owns the exact four native
reader replacements, conditional geometry and alias-note transition. The
independent consumer uses the existing COPY and SID22 records from one complete
successful GNU primary. It publishes no additional receipt.

| Calibration | Software path | Diagnostic source |
|---|---|---|
| K word `00009284` | `0003B75C`, selected normal BFS path | Word `FFFF1026`, DID `1208` |
| Cold byte surface `0000B2FA` | `000BFDC0`, selected cold endpoint in `000BFE88` | Byte `FFFF2327`, DID `1166` |
| Main byte surface `0000B33A` | `000BFDC0`, selected main endpoint in `000BFE88` | Byte `FFFF2327`, DID `1166` |
| Correction word curve `000147DA` | `0004D99C`, `0004DBE8`, `0004DF82` | Byte `FFFF2022`, aliases from the executed SID22 descriptor |


The 147DA path keeps its three actual stage snapshots continuous. Its separate
GNU-assembled scheduler sink at `0002A892` provides a synthetic R0 return only.
The stock scheduler body, MMIO, timing and hardware effects remain outside the
admitted scope. The curve's semantic extent and additional physical neighbor
read remain separate; the geometry excludes that neighbor.

The joint consumer retains the exact existing RAM reader identities and every
SID22 SOURCE slot. The publisher observes the resulting RAM values. These
dependencies assert no physical ROM read by the publisher, universal absence of
ROM reads, units, scale, all operating modes, natural scheduling or hardware
qualification.


SID22 excludes only these exact complete before/after representations from its
RAM-publisher namespace. Modified properties, layouts, evidence, sources or
unrelated relations retain their full freshness boundary. This normalization
does not qualify the ROM dependency; the joint consumer supplies that separate
admission.
