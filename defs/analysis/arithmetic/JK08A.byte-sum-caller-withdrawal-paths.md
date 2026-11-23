# JK08A byte sum caller withdrawal

Source bindings: `JK08A.byte-sum-caller-withdrawal-paths.toml`.


## Complete real coordinate,curve and publications

The caller occupies464DE..46504 and4653C..465AE around its literal hole.
The complete helpers are26370..26382,26A60..26ABA and26740..2676E.
Entry26A80 remains inside the complete normal26A60 parent. The16 instructions
before that entry and seven word-cell sibling instructions are excluded by
the exact byte-mode literal224 after SHLR8.

The complete unsigned22E4 byte supplies the coordinate. Values below40
select0. Other values subtract40 and multiply4,then cap at255. Raw103 supplies
252;raw104 supplies255. The real26370 call at4654A receives fixed ROM128D8
and the exact EXTU.B argument after its real delay slot. Eight independent raw
bytes remain controlled inputs. Coordinates below224 interpolate adjacent bytes
at a32-unit step. Coordinates at or above224 keep the natural signed MOV.B
endpoint return at26380. The caller explicitly converts the returned value
to an unsigned byte and publishes1716. Raw96 is the first endpoint coordinate.

Unsigned1741,174F and1742 bytes add without an intermediate clamp. Their
complete sum ranges through765 and publishes the word173C. Independently,
the caller selects min(unsigned1742,curve_byte),adds unsigned1741 and the
complete unsigned174C word,then caps at65535 before publishing173E. It then
adds unsigned1740 to that already capped result and caps again at65535 before
publishing1748. The unclipped three-byte sum,byte minimum and two word caps
remain separate calculations. A shared saturation or signed174C word does
not replace them. The exact equality boundary keeps the nonoverflow branch.

The four real ordered stores are46552 (byte1716),46570 (word173C),46590
(word173E) and465A6 (word1748). The natural RTS at465AA restores R14 in its
delay slot. R0 returns0x4BC.
