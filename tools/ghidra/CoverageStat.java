// CoverageStat.java - image coverage by defined instructions, data, undefined
// bytes, and the share of instructions outside function bodies. This measures
// how much code analysis can see: only disassembled instructions have
// references, and xref export walks function bodies, so undefined code produces
// neither references nor graph edges.
//
// Usage (headless): -postScript CoverageStat.java
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;

public class CoverageStat extends GhidraScript {
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        long total = 0;
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            if (b.isInitialized() && b.getStart().getOffset() < 0x180000L) {
                total += b.getSize();
            }
        }
        long insBytes = 0, insCount = 0, insOutside = 0, insOutsideBytes = 0;
        for (Instruction ins : listing.getInstructions(true)) {
            Address a = ins.getMinAddress();
            if (a.getOffset() >= 0x180000L) {
                continue;
            }
            insBytes += ins.getLength();
            insCount++;
            if (currentProgram.getFunctionManager().getFunctionContaining(a) == null) {
                insOutside++;
                insOutsideBytes += ins.getLength();
            }
        }
        long dataBytes = 0;
        for (Data d : listing.getDefinedData(true)) {
            if (d.getMinAddress().getOffset() < 0x180000L) {
                dataBytes += d.getLength();
            }
        }
        long funcBytes = 0;
        int nf = 0;
        for (ghidra.program.model.listing.Function f :
                currentProgram.getFunctionManager().getFunctions(true)) {
            AddressSetView body = f.getBody();
            funcBytes += body.getNumAddresses();
            nf++;
        }
        println("VQ_COV total=" + total + " instr_bytes=" + insBytes + " instr=" + insCount
                + " data_bytes=" + dataBytes + " func_bytes=" + funcBytes + " funcs=" + nf
                + " instr_outside_func=" + insOutside + " bytes=" + insOutsideBytes);
    }
}
