// Экспорт call-графа текущей программы в CSV (узлы функций + рёбра CALLS)
// для загрузки в Memgraph. Java GhidraScript (headless, PyGhidra не требуется).
//
// Запуск: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript ExportGraph.java <outdir>
// Пишет <outdir>/funcs.csv (addr,name,size,is_thunk,is_external) и
//       <outdir>/calls.csv (src,dst). Адреса – hex-строка без 0x (ключ узла).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import java.io.File;
import java.io.PrintWriter;
import java.util.Set;

public class ExportGraph extends GhidraScript {
    @Override
    public void run() throws Exception {
        String outdir = getScriptArgs().length > 0 ? getScriptArgs()[0] : "/tmp";
        new File(outdir).mkdirs();
        FunctionManager fm = currentProgram.getFunctionManager();
        PrintWriter fw = new PrintWriter(new File(outdir, "funcs.csv"));
        PrintWriter cw = new PrintWriter(new File(outdir, "calls.csv"));
        fw.println("addr,name,size,is_thunk,is_external");
        cw.println("src,dst");
        int nf = 0, nc = 0;
        for (Function f : fm.getFunctions(true)) {
            String addr = f.getEntryPoint().toString();
            String name = f.getName().replace("\"", "'");
            long size = f.getBody().getNumAddresses();
            fw.println(addr + ",\"" + name + "\"," + size + "," + f.isThunk() + "," + f.isExternal());
            nf++;
            Set<Function> called = f.getCalledFunctions(monitor);
            for (Function c : called) {
                cw.println(addr + "," + c.getEntryPoint().toString());
                nc++;
            }
        }
        fw.close();
        cw.close();
        println("VQ_EXPORT funcs=" + nf + " calls=" + nc + " dir=" + outdir);
    }
}
