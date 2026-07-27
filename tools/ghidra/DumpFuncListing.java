// DumpFuncListing.java - disassemble a complete function from entry through its
// body, including resolved references (ref -> target [= value read]).
//
// Unlike DumpListing, which prints a +-24-instruction address window, this tool
// uses the function body as its unit and boundary. It supports cases where a
// complete short function is the subject of analysis. The arithmetic library at
// 0x21000..0x23000 passes arguments through registers, and its convention is
// visible only from the whole body. Pseudocode is unsuitable: expanding a
// 32-step division produces 31 KB from 282 bytes of code.
//
// Usage (headless): -postScript DumpFuncListing.java <out_dir> <addr> [<addr>...]
// Output: one funclisting_<addr>.txt per function.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DumpFuncListing extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 2) {
            println("VQ_FLST need: <outdir> <addr>...");
            return;
        }
        String outDir = a[0];
        new File(outDir).mkdirs();
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();
        int ok = 0;

        for (int i = 1; i < a.length; i++) {
            Address ep;
            try {
                ep = currentProgram.getAddressFactory().getDefaultAddressSpace()
                        .getAddress(Long.parseLong(a[i], 16));
            } catch (Exception e) {
                println("VQ_FLST bad addr " + a[i]);
                continue;
            }
            Function f = getFunctionAt(ep);
            if (f == null) {
                println("VQ_FLST no function at " + a[i]);
                continue;
            }
            String name = String.format("funclisting_%08x.txt", ep.getOffset() & 0xFFFFFFFFL);
            PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, name)));
            w.println("// " + f.getName() + " @ " + ep + "  size=" + f.getBody().getNumAddresses());
            // A function body is an address set rather than a continuous range.
            // Ghidra can include separated pieces such as a shared tail or
            // epilogue; iterating the set includes them.
            AddressSetView body = f.getBody();
            InstructionIterator it = listing.getInstructions(body, true);
            while (it.hasNext()) {
                Instruction cur = it.next();
                StringBuilder line = new StringBuilder();
                line.append("   ").append(cur.getAddress()).append("  ").append(cur.toString());
                for (Reference r : cur.getReferencesFrom()) {
                    Address to = r.getToAddress();
                    if (to == null || !to.isMemoryAddress()) continue;
                    line.append("   ; -> ").append(to);
                    long off = to.getOffset() & 0xFFFFFFFFL;
                    if (off < 0x180000L) {
                        try {
                            long v = mem.getInt(to) & 0xFFFFFFFFL;
                            line.append(String.format(" [=%08x]", v));
                        } catch (Exception e) { /* uninitialized */ }
                    }
                }
                w.println(line.toString());
            }
            w.close();
            ok++;
        }
        println("VQ_FLST wrote=" + ok + " dir=" + outDir);
    }
}
