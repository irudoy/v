// RecoverFuncs.java - define functions for code left outside function bodies (Stage 0,
// section 7 of tools/map-flag-pipeline.md).
//
// Auto-analysis creates a function for a region that has a direct call reference. Code
// reachable only indirectly (jsr @rN through a pool slot) or through a pointer dispatcher
// does not become a function: its instructions are disassembled but belong to no function.
// The consequences are measurable in the JK03A map census: 17 of 124 call sites for core
// 0x26944 are outside function bodies, so ExportGraph does not list their calls (wrappers
// 0x26100 and 0x26230 remain without callers in the graph), and the decompiler cannot reach
// such a region, leaving operand data flow unavailable.
//
// A pass finds contiguous regions of instructions outside functions and creates a function
// at the start of each region; Ghidra builds the body from control flow. A region may contain
// several consecutive functions, so passes repeat while coverage grows: each created
// function consumes its prologue and moves the start of the remainder to the next function.
//
// Function definition does not create code: it groups only instructions already produced by
// the disassembler. A region that does not start at a prologue (jump-only entry) or starts
// with a delay slot makes createFunction fail; the report counts it and leaves the region.
//
// Headless invocation: -postScript RecoverFuncs.java
// With -readOnly the pass calculates and reports results but does not save definitions to the
// project (dry run). Without -readOnly, headless analysis saves them for the next ExportGraph.
//@category VQ
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import java.util.ArrayList;
import java.util.List;

public class RecoverFuncs extends GhidraScript {

    static final int MAX_PASS = 32;   // pass limit; stop when coverage no longer grows

    Listing listing;
    FunctionManager fm;

    @Override
    public void run() throws Exception {
        listing = currentProgram.getListing();
        fm = currentProgram.getFunctionManager();

        int insBefore = countOutside();
        int regBefore = regionStarts().size();
        int funcBefore = fm.getFunctionCount();
        println("VQ_RF input: " + funcBefore + " functions, " + insBefore
                + " instructions outside functions in " + regBefore + " regions");

        int made = 0, failed = 0;
        for (int pass = 1; pass <= MAX_PASS; pass++) {
            if (monitor.isCancelled()) break;
            List<Address> starts = regionStarts();
            if (starts.isEmpty()) break;
            int mp = 0, fp = 0;
            for (Address st : starts) {
                if (monitor.isCancelled()) break;
                if (fm.getFunctionContaining(st) != null) continue;   // covered by adjacent body
                int tx = currentProgram.startTransaction("recover-func");
                boolean ok = false;
                try {
                    ok = createFunction(st, null) != null;
                } catch (Exception e) {
                    ok = false;
                } finally {
                    currentProgram.endTransaction(tx, ok);
                }
                if (ok) mp++; else fp++;
            }
            made += mp;
            failed = fp;                                              // failures in the last pass
            println("  pass " + pass + ": " + starts.size() + " regions, " + mp
                    + " created, " + fp + " failed");
            if (mp == 0) break;                                       // no further growth
        }

        int insAfter = countOutside();
        List<Address> left = regionStarts();
        println("VQ_RF functions created: " + made + ", total functions: "
                + fm.getFunctionCount());
        println("VQ_RF instructions outside functions: " + insBefore + " -> " + insAfter
                + " (regions " + regBefore + " -> " + left.size() + ", failures " + failed + ")");
        for (int i = 0; i < left.size() && i < 20; i++) {
            Instruction ins = listing.getInstructionAt(left.get(i));
            println("  remains outside functions: " + left.get(i)
                    + (ins == null ? "" : "  " + ins.toString()));
        }
        if (left.size() > 20) println("  ... " + (left.size() - 20) + " more regions");
    }

    // Starts of contiguous instruction regions outside functions: an instruction outside a
    // function preceded by either a function or a disassembly gap (literal pool or data).
    List<Address> regionStarts() {
        List<Address> out = new ArrayList<>();
        Address prevMax = null;
        boolean prevOutside = false;
        for (Instruction ins : listing.getInstructions(true)) {
            boolean outside = fm.getFunctionContaining(ins.getAddress()) == null;
            boolean gap = !ins.getAddress().equals(after(prevMax));
            if (outside && (!prevOutside || gap)) out.add(ins.getAddress());
            prevOutside = outside;
            prevMax = ins.getMaxAddress();
        }
        return out;
    }

    int countOutside() {
        int n = 0;
        for (Instruction ins : listing.getInstructions(true)) {
            if (fm.getFunctionContaining(ins.getAddress()) == null) n++;
        }
        return n;
    }

    Address after(Address a) {
        if (a == null) return null;
        try {
            return a.add(1);
        } catch (Exception e) {
            return null;
        }
    }
}
