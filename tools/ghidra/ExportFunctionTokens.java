// ExportFunctionTokens.java - export normalized instruction sequences for
// reviewable cross-ROM structural similarity analysis.
//
// Exact and whole-function hashes in ExportFunctionSignatures remain the
// authority for byte equality. This export retains one normalized instruction
// per row so an offline matcher can tolerate bounded insertions, deletions, and
// literal relocation without treating approximate similarity as equality.
//
// Usage: -postScript ExportFunctionTokens.java <out_dir>
// Output: function_tokens.csv (func_addr,ordinal,mnemonic,shape).
//@category VQ
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

public class ExportFunctionTokens extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            println("VQ_TOK need: <out_dir>");
            return;
        }
        File outDir = new File(args[0]);
        outDir.mkdirs();
        File output = new File(outDir, "function_tokens.csv");
        Listing listing = currentProgram.getListing();

        List<Function> functions = new ArrayList<>();
        FunctionIterator iterator = currentProgram.getFunctionManager()
                .getFunctions(true);
        while (iterator.hasNext()) {
            Function function = iterator.next();
            if (!function.isExternal() && !function.getBody().isEmpty()) {
                functions.add(function);
            }
        }
        functions.sort(Comparator.comparing(Function::getEntryPoint));

        PrintWriter out = new PrintWriter(new FileWriter(output));
        out.println("func_addr,ordinal,mnemonic,shape");
        int emittedFunctions = 0;
        int emittedInstructions = 0;
        for (Function function : functions) {
            if (monitor.isCancelled()) {
                break;
            }
            int ordinal = 0;
            InstructionIterator instructions = listing.getInstructions(
                    function.getBody(), true);
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                String mnemonic = instruction.getMnemonicString()
                        .toLowerCase(Locale.ROOT);
                out.printf(
                        "%s,%d,%s,%s%n",
                        function.getEntryPoint(),
                        ordinal++,
                        csv(mnemonic),
                        csv(normalize(instruction.toString())));
                emittedInstructions++;
            }
            if (ordinal > 0) {
                emittedFunctions++;
            }
        }
        out.close();
        println("VQ_TOK functions=" + emittedFunctions
                + " instructions=" + emittedInstructions
                + " output=" + output);
    }

    String normalize(String text) {
        String value = text.toLowerCase(Locale.ROOT);
        value = value.replaceAll("\\b(?:fun|dat|lab|sub)_[0-9a-f]+\\b", "symbol");
        value = value.replaceAll("0x[0-9a-f]+", "#");
        value = value.replaceAll(
                "(?<![a-z0-9_])-?[0-9]+(?![a-z0-9_])", "#");
        value = value.replaceAll("\\s+", " ").trim();
        return value;
    }

    String csv(String value) {
        return "\"" + value.replace("\"", "\"\"") + "\"";
    }
}
