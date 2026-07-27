// FindTableRefs.java - find functions addressing a selected ROM range [lo,hi],
// such as a DTC table. Include direct references and literal-pool references
// where mov.l @(disp,PC) loads a 32-bit constant within the range. The result
// identifies base/record loaders as starting points for the DTC runner and
// immobilizer setter.
//
// Usage (headless): -postScript FindTableRefs.java <out_dir> <lo_hex> <hi_hex>
// Output: table_refs.csv (func,ins_addr,value,kind[direct|literal]).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

public class FindTableRefs extends GhidraScript {

    static final long ROM_HI = 0x180000L; // 1.5 MiB image

    public void run() throws Exception {
        String[] a = getScriptArgs();
        String outDir = a[0];
        long lo = Long.parseLong(a[1], 16);
        long hi = Long.parseLong(a[2], 16);

        Memory mem = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();

        PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "table_refs.csv")));
        w.println("func,ins_addr,value,kind");
        int n = 0;
        for (Function f : fm.getFunctions(true)) {
            for (Instruction ins : listing.getInstructions(f.getBody(), true)) {
                for (Reference r : ins.getReferencesFrom()) {
                    Address to = r.getToAddress();
                    if (to == null || !to.isMemoryAddress()) continue;
                    long toOff = to.getOffset() & 0xFFFFFFFFL;
                    if (toOff >= lo && toOff <= hi) {
                        w.println(String.format("%s,%08x,%08x,direct",
                                f.getEntryPoint(), ins.getAddress().getOffset(), toOff));
                        n++;
                        continue;
                    }
                    if (toOff < ROM_HI) {
                        try {
                            long v = mem.getInt(to) & 0xFFFFFFFFL;
                            if (v >= lo && v <= hi) {
                                w.println(String.format("%s,%08x,%08x,literal",
                                        f.getEntryPoint(), ins.getAddress().getOffset(), v));
                                n++;
                            }
                        } catch (MemoryAccessException e) {
                            // Skip literals outside initialized memory.
                        }
                    }
                }
            }
        }
        w.close();
        println("VQ_TREF hits=" + n + " range=" + a[1] + ".." + a[2]);
    }
}
