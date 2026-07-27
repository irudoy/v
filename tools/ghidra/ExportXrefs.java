// Export function accesses to SH7058/59 peripheral space as anchors for
// immobilizer/NATS analysis. In addition to direct data references to registers
// at 0xFFFF0000+, resolve literal pools: a PC-relative load of a 32-bit constant
// pointing into peripheral space counts as a function access. This is the usual
// SH-2 path to memory-mapped I/O: mov.l @(disp,PC),Rn followed by mov @Rn.
// Region classification is performed by the loader.
//
// Usage: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript ExportXrefs.java <outdir>
// Writes <outdir>/xrefs.csv (func_addr,periph_addr,kind): R/W/D are direct and
// L uses a literal pool.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.PrintWriter;

public class ExportXrefs extends GhidraScript {
    // Lower bound is the SH7059 on-chip RAM base at 0xFFFE8000 (48 KB). This
    // includes RAM variables and CAN message tables through peripheral
    // registers at 0xFFFFFFFF.
    static final long PERIPH_LO = 0xFFFE8000L;
    static final long PERIPH_HI = 0xFFFFFFFFL;
    static final long ROM_HI = 0x180000L;

    private boolean isPeriph(long v) {
        return v >= PERIPH_LO && v <= PERIPH_HI;
    }

    @Override
    public void run() throws Exception {
        String outdir = getScriptArgs().length > 0 ? getScriptArgs()[0] : "/tmp";
        new File(outdir).mkdirs();
        FunctionManager fm = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();
        PrintWriter xw = new PrintWriter(new File(outdir, "xrefs.csv"));
        xw.println("func_addr,periph_addr,kind");
        int nx = 0;
        for (Function f : fm.getFunctions(true)) {
            String faddr = f.getEntryPoint().toString();
            for (Instruction instr : listing.getInstructions(f.getBody(), true)) {
                for (Reference ref : instr.getReferencesFrom()) {
                    Address to = ref.getToAddress();
                    if (to == null || !to.isMemoryAddress()) {
                        continue;
                    }
                    long toOff = to.getOffset() & 0xFFFFFFFFL;
                    long periph = -1;
                    String kind = "?";
                    if (isPeriph(toOff)) {
                        periph = toOff;                      // direct register reference
                        RefType rt = ref.getReferenceType();
                        kind = rt.isWrite() ? "W" : (rt.isRead() ? "R" : "D");
                    } else if (toOff < ROM_HI) {
                        try {
                            long v = mem.getInt(to) & 0xFFFFFFFFL;  // BE program
                            if (isPeriph(v)) {
                                periph = v;                  // register address through literal pool
                                kind = "L";
                            }
                        } catch (MemoryAccessException e) {
                            // Skip uninitialized memory.
                        }
                    }
                    if (periph < 0) {
                        continue;
                    }
                    xw.println(faddr + "," + String.format("%08x", periph) + "," + kind);
                    nx++;
                }
            }
        }
        xw.close();
        println("VQ_XREFS periph_refs=" + nx + " dir=" + outdir);
    }
}
