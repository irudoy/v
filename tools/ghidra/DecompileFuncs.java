// Декомпиляция заданных функций нативным декомпилятором Ghidra (headless) в C-псевдокод.
// Для прицельного чтения кандидатов (напр. CAN-приёмников RXPR) без GUI.
//
// Запуск: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript DecompileFuncs.java <outdir> <addr> [<addr>...]
// Адреса – hex без 0x (как в funcs.csv). Пишет <outdir>/decomp_<addr>.c на каждую функцию.
import ghidra.app.decompiler.DecompInterface;
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
        di.openProgram(currentProgram);
        int ok = 0;
        for (int i = 1; i < a.length; i++) {
            Address ep = currentProgram.getAddressFactory().getAddress(a[i]);
            Function f = getFunctionAt(ep);
            if (f == null) {
                println("VQ_DECOMP no function at " + a[i]);
                continue;
            }
            DecompileResults res = di.decompileFunction(f, 60, monitor);
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
