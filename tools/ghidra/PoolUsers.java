// Find and decompile the function owning a selected address, usually a
// literal-pool slot or function body. Also list instructions that reference the
// address through mov.l @(disp,pc). This connects a table/pool address to its
// consuming function without requiring an exact entry point.
//
// Usage: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript PoolUsers.java <outdir> <addr> [<addr>...]
// Addresses are hexadecimal without 0x. Writes <outdir>/decomp_<funcEntry>.c and
// prints relationships to the log with VQ_POOL.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;
import java.io.File;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;

public class PoolUsers extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 2) { println("VQ_POOL need: <outdir> <addr>..."); return; }
        String outdir = a[0];
        new File(outdir).mkdirs();
        ReferenceManager rm = currentProgram.getReferenceManager();
        DecompInterface di = new DecompInterface();
        di.openProgram(currentProgram);
        Set<Address> entries = new LinkedHashSet<>();
        for (int i = 1; i < a.length; i++) {
            Address t = currentProgram.getAddressFactory().getAddress(a[i]);
            Function fc = getFunctionContaining(t);
            Function fb = getFunctionBefore(t);
            println("VQ_POOL target=" + a[i]
                    + " containing=" + (fc==null?"-":fc.getEntryPoint()+"("+fc.getName()+")")
                    + " before=" + (fb==null?"-":fb.getEntryPoint()+"("+fb.getName()+")"));
            // Instructions that reference the address and load the slot.
            for (Reference r : rm.getReferencesTo(t)) {
                Address from = r.getFromAddress();
                Function ff = getFunctionContaining(from);
                println("VQ_POOL   refFrom=" + from + " type=" + r.getReferenceType()
                        + " func=" + (ff==null?"-":ff.getEntryPoint()+"("+ff.getName()+")"));
                if (ff != null) entries.add(ff.getEntryPoint());
            }
            if (fc != null) entries.add(fc.getEntryPoint());
            else if (fb != null) entries.add(fb.getEntryPoint());
        }
        int ok = 0;
        for (Address ep : entries) {
            Function f = getFunctionAt(ep);
            if (f == null) continue;
            DecompileResults res = di.decompileFunction(f, 60, monitor);
            String c = res.decompileCompleted() ? res.getDecompiledFunction().getC()
                                                : "// decompile failed: " + res.getErrorMessage();
            PrintWriter w = new PrintWriter(new File(outdir, "decomp_" + ep.toString() + ".c"));
            w.println("// " + f.getName() + " @ " + ep + "  size=" + f.getBody().getNumAddresses());
            w.println(c);
            w.close();
            ok++;
        }
        di.dispose();
        println("VQ_POOL wrote=" + ok + " dir=" + outdir);
    }
}
