// Write the SHA-256 that Ghidra recorded for the imported executable of the
// current program. decompile.sh compares it with the registered stock image
// before it accepts any output of the same headless run.
//
// Usage: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -readOnly -scriptPath tools/ghidra -postScript ProgramSha256.java <outfile>
import ghidra.app.script.GhidraScript;
import java.io.File;
import java.io.PrintWriter;

public class ProgramSha256 extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length != 1) {
            println("VQ_PROGRAM_SHA256 need: <outfile>");
            return;
        }
        String sha256 = currentProgram.getExecutableSHA256();
        PrintWriter w = new PrintWriter(new File(a[0]));
        w.println(sha256 == null ? "" : sha256.toLowerCase());
        w.close();
        println("VQ_PROGRAM_SHA256 " + currentProgram.getName() + " " + sha256);
    }
}
