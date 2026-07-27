// DumpListing.java - disassemble neighborhoods around selected addresses with
// resolved references (ref -> target [= value read]). Supports focused reading
// where code accesses a specific constant or table, such as an immobilizer DTC
// entry, after the decompiler has folded the address into a literal.
//
// Usage (headless): -postScript DumpListing.java <out_dir> <addr> [<addr>...]
// Output: one listing_<addr>.txt per address with a +-24-instruction window.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DumpListing extends GhidraScript {

    public void run() throws Exception {
        String[] a = getScriptArgs();
        String outDir = a[0];
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();

        for (int i = 1; i < a.length; i++) {
            Address target;
            try {
                target = currentProgram.getAddressFactory().getDefaultAddressSpace()
                        .getAddress(Long.parseLong(a[i], 16));
            } catch (Exception e) { println("VQ_LST bad addr " + a[i]); continue; }
            Instruction ins = listing.getInstructionContaining(target);
            if (ins == null) { println("VQ_LST no instr @ " + a[i]); continue; }
            // Walk back 24 instructions.
            Instruction cur = ins;
            for (int k = 0; k < 24 && cur != null; k++) {
                Instruction prev = listing.getInstructionBefore(cur.getAddress());
                if (prev == null) break;
                cur = prev;
            }
            // Name the file from the parsed address rather than argument text.
            // build_artifacts.py obtains an eight-digit graph address, so
            // "26a80" and "00026a80" differ only in invocation spelling.
            String name = String.format("listing_%08x.txt", target.getOffset() & 0xFFFFFFFFL);
            PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, name)));
            for (int k = 0; k < 56 && cur != null; k++) {
                StringBuilder line = new StringBuilder();
                boolean mark = cur.getAddress().equals(ins.getAddress());
                line.append(mark ? ">> " : "   ");
                line.append(cur.getAddress()).append("  ").append(cur.toString());
                for (Reference r : cur.getReferencesFrom()) {
                    Address to = r.getToAddress();
                    if (to == null || !to.isMemoryAddress()) continue;
                    line.append("   ; -> ").append(to);
                    long off = to.getOffset() & 0xFFFFFFFFL;
                    if (off < 0x180000L) {
                        try {
                            long v = mem.getInt(to) & 0xFFFFFFFFL;
                            line.append(String.format(" [=%08x]", v));
                        } catch (Exception e) { /* not initialized */ }
                    }
                }
                w.println(line.toString());
                cur = cur.getNext();
            }
            w.close();
            println("VQ_LST wrote " + name);
        }
    }
}
