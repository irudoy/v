# Indexed diagnostic-record bit4 writer

Original `3655c66e3ef972ce95f95db39da784ed70f454d346be7a51411fffaeb1fa00b5`
is the `hallowed-malkoha/ram` writer relation to `cherry-wildcat/fn` at
`0008C968`. The complete natural leaf computes `FFFF5718 + 3*R4`, reads the
third byte, sets only bit 4 and writes the computed byte at the same member.
Its natural RTS delay slot writes the byte value `1` to `FFFF508C`.

The ordinary observer uses an explicit full-R4 input premise: indices
`00000000`, `00000001`, `00000047`, `00000123`, `00000128`, `00000129` and
`00000156`. These direct-entry software contexts neither establish the complete
array extent nor identify caller scheduling, hardware status names or other
record writers. The address calculation uses the complete incoming R4 and
preserves it. It does not truncate R4 to a byte or sign-extended word.


Independent scalar equations bind `old_byte | 0x10`, the full sign-extended R0
before and after the OR, complete index and address carriers, the final R0
value `00000B34`, final R2 `1`, preserved R4 and all remaining register values.
The actual SHLL sets T from the incoming index's high bit; the admitted direct
indices clear T. M, Q, interrupt and all other observed SR controls remain
preserved. Separate physical obligations bind the ordered read, computed byte
write, both pointer loads, displacement load and the RTS-delay flag write.
The frame is unchanged and the complete natural return retains PR and SP.

Every admitted index has complete byte preimages. Positive alternatives hold
all other complete CPU, frame, RAM and literal inputs fixed and require two
distinct, changed actual computed bytes at the same physical member. An input
echo, an arbitrary changed byte, identical results, a missing publication or a
changed write-set alone supplies no admission. The index contributes an exact
physical address obligation; these contexts grant no numerical causality from
an address-only change. First and second record bytes, every other selected
record and the complete remaining ordinary RAM retain their original bytes.


The source package and shared registration fragments establish no accepted
execution, native publication, physical scale, array geometry, hardware result
or completion of another original. The common B acceptance executes the
independent reconstruction, state, physical, numerical, positive, native, TEST
and refusal contracts together.
