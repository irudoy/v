// FindPoolWords.java - find instructions loading selected 16-bit literal-pool
// values. This is useful for indexed RAM references where Ghidra resolves the
// base pointer but cannot create a reference to base+offset.
//
// Usage (headless): -postScript FindPoolWords.java <word_hex> [<word_hex> ...]
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import java.util.HashSet;
import java.util.Set;

public class FindPoolWords extends GhidraScript {
    static final long ROM_HI = 0x180000L;

    @Override
    public void run() throws Exception {
        if (getScriptArgs().length == 0) {
            printerr("Usage: FindPoolWords.java <word_hex> [<word_hex> ...]");
            return;
        }

        Set<Integer> wanted = new HashSet<>();
        for (String arg : getScriptArgs()) {
            wanted.add(Integer.parseInt(arg, 16) & 0xffff);
        }

        Memory memory = currentProgram.getMemory();
        int hits = 0;
        for (Instruction ins : currentProgram.getListing().getInstructions(true)) {
            if (!"mov.w".equalsIgnoreCase(ins.getMnemonicString())
                    || !ins.toString().toLowerCase().contains(",pc)")) {
                continue;
            }
            for (Reference ref : ins.getReferencesFrom()) {
                Address target = ref.getToAddress();
                if (target == null || !target.isMemoryAddress()) {
                    continue;
                }
                long offset = target.getOffset() & 0xffffffffL;
                if (offset >= ROM_HI) {
                    continue;
                }
                int value;
                try {
                    value = memory.getShort(target) & 0xffff;
                } catch (Exception ignored) {
                    continue;
                }
                if (!wanted.contains(value)) {
                    continue;
                }
                Function function = getFunctionContaining(ins.getAddress());
                println(String.format(
                        "VQ_POOLWORD value=%04x pool=%s ins=%s func=%s text=%s",
                        value,
                        target,
                        ins.getAddress(),
                        function == null ? "-" : function.getEntryPoint(),
                        ins));
                hits++;
            }
        }
        println("VQ_POOLWORD hits=" + hits);
    }
}
