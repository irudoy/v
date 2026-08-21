// ExportFunctionSignatures.java - export relocation-tolerant function signatures.
//
// Exact bytes remain the strongest equality test. Mnemonic and normalized
// instruction-text hashes remove literal values, pool addresses, branch
// displacements, and immediate constants so related ROMs can be paired before
// their addressed operands are compared independently.
//
// Usage: -postScript ExportFunctionSignatures.java <out_dir>
//@category VQ
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

public class ExportFunctionSignatures extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            println("VQ_SIG need: <out_dir>");
            return;
        }
        File outDir = new File(args[0]);
        outDir.mkdirs();
        File output = new File(outDir, "function_signatures.csv");
        File sitesOutput = new File(outDir, "function_sites.csv");
        Listing listing = currentProgram.getListing();
        Memory memory = currentProgram.getMemory();

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
        PrintWriter sites = new PrintWriter(new FileWriter(sitesOutput));
        out.println("addr,size,instructions,exact_sha256,mnemonic_sha256,shape_sha256");
        sites.println("func_addr,ins_addr,ordinal,mnemonic");
        int emitted = 0;
        for (Function function : functions) {
            if (monitor.isCancelled()) {
                break;
            }
            MessageDigest exact = MessageDigest.getInstance("SHA-256");
            MessageDigest mnemonics = MessageDigest.getInstance("SHA-256");
            MessageDigest shape = MessageDigest.getInstance("SHA-256");
            long size = 0;
            int instructionCount = 0;
            InstructionIterator instructions = listing.getInstructions(
                    function.getBody(), true);
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                byte[] bytes = new byte[instruction.getLength()];
                memory.getBytes(instruction.getAddress(), bytes);
                exact.update(bytes);
                size += bytes.length;
                instructionCount++;
                String mnemonic = instruction.getMnemonicString()
                        .toLowerCase(Locale.ROOT);
                if (mnemonic.equals("jsr") || mnemonic.equals("bsr")) {
                    sites.printf(
                            "%s,%s,%d,%s%n",
                            function.getEntryPoint(),
                            instruction.getAddress(),
                            instructionCount - 1,
                            mnemonic);
                }
                updateLine(mnemonics, mnemonic);
                updateLine(shape, normalize(instruction.toString()));
            }
            if (instructionCount == 0) {
                continue;
            }
            out.printf(
                    "%s,%d,%d,%s,%s,%s%n",
                    function.getEntryPoint(),
                    size,
                    instructionCount,
                    hex(exact.digest()),
                    hex(mnemonics.digest()),
                    hex(shape.digest()));
            emitted++;
        }
        out.close();
        sites.close();
        println("VQ_SIG functions=" + emitted + " output=" + output
                + " sites=" + sitesOutput);
    }

    void updateLine(MessageDigest digest, String value) {
        digest.update(value.toLowerCase(Locale.ROOT).getBytes(StandardCharsets.UTF_8));
        digest.update((byte) '\n');
    }

    String normalize(String text) {
        String value = text.toLowerCase(Locale.ROOT);
        value = value.replaceAll("\\b(?:fun|dat|lab|sub)_[0-9a-f]+\\b", "symbol");
        value = value.replaceAll("0x[0-9a-f]+", "#");
        value = value.replaceAll("(?<![a-z_])-?[0-9]+(?![a-z_])", "#");
        value = value.replaceAll("\\s+", " ").trim();
        return value;
    }

    String hex(byte[] bytes) {
        StringBuilder out = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) {
            out.append(String.format("%02x", value & 0xff));
        }
        return out.toString();
    }
}
