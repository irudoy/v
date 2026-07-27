// Decompile selected functions to C pseudocode with the native Ghidra decompiler
// in headless mode. Supports focused inspection of candidates such as RXPR CAN
// receivers without a GUI.
//
// Usage: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript DecompileFuncs.java <outdir> <addr> [<addr>...]
// Addresses are hexadecimal without 0x, as in funcs.csv. Writes one
// <outdir>/decomp_<addr>.c per function.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import java.io.File;
import java.io.PrintWriter;

public class DecompileFuncs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 2) {
            println("VQ_DECOMP need: <outdir> <addr>...");
            return;
        }
        String outdir = a[0];
        new File(outdir).mkdirs();
        DecompInterface di = new DecompInterface();
        // Large functions around 17 KB hit the decompiler response-buffer limit,
        // "Response buffer size exceeded", rather than the timeout.
        DecompileOptions opts = new DecompileOptions();
        opts.setMaxPayloadMBytes(256);
        di.setOptions(opts);
        di.openProgram(currentProgram);
        int ok = 0;
        for (int i = 1; i < a.length; i++) {
            Address ep;
            try {
                ep = currentProgram.getAddressFactory().getDefaultAddressSpace()
                        .getAddress(Long.parseLong(a[i], 16));
            } catch (Exception e) {
                println("VQ_DECOMP bad addr " + a[i]);
                continue;
            }
            Function f = getFunctionAt(ep);
            if (f == null) {
                println("VQ_DECOMP no function at " + a[i]);
                continue;
            }
            // 240 seconds leaves margin for large functions; normal runs need <10 seconds.
            DecompileResults res = di.decompileFunction(f, 240, monitor);
            String c = res.decompileCompleted() ? res.getDecompiledFunction().getC()
                                                : "// decompile failed: " + res.getErrorMessage();
            PrintWriter w = new PrintWriter(new File(outdir, "decomp_" + a[i] + ".c"));
            w.println("// " + f.getName() + " @ " + a[i] + "  size=" + f.getBody().getNumAddresses());
            w.println(c);
            w.close();
            ok++;
        }
        di.dispose();
        println("VQ_DECOMP wrote=" + ok + " dir=" + outdir);
    }
}
