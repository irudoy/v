// ExportFunctionSignatures.java - export relocation-tolerant function signatures.
//
// Exact bytes remain the strongest equality test. Mnemonic and normalized
// instruction-text hashes remove literal values, pool addresses, branch
// displacements, and immediate constants so related ROMs can be paired before
// their addressed operands are compared independently. The companion reference
// export preserves each ROM reference and loaded value by instruction ordinal.
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
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class ExportFunctionSignatures extends GhidraScript {
    static final long ROM_HI = 0x180000L;
    static final long RAM_LO = 0xffff0000L;

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
        File referencesOutput = new File(
                outDir, "function_references.csv");
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
        PrintWriter references = new PrintWriter(
                new FileWriter(referencesOutput));
        out.println("addr,size,instructions,exact_sha256,mnemonic_sha256,shape_sha256");
        sites.println("func_addr,ins_addr,ordinal,mnemonic");
        references.println(
                "func_addr,ins_addr,ordinal,mnemonic,ref_addr,width,value_hex,ref_type");
        Set<String> emittedReferences = new HashSet<>();
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
                int ordinal = instructionCount - 1;
                if (mnemonic.equals("jsr") || mnemonic.equals("bsr")) {
                    sites.printf(
                            "%s,%s,%d,%s%n",
                            function.getEntryPoint(),
                            instruction.getAddress(),
                            ordinal,
                            mnemonic);
                }
                exportReferences(
                        references,
                        memory,
                        function,
                        instruction,
                        ordinal,
                        mnemonic,
                        emittedReferences);
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
        references.close();
        println("VQ_SIG functions=" + emitted + " output=" + output
                + " sites=" + sitesOutput
                + " references=" + referencesOutput);
    }

    void exportReferences(
            PrintWriter out,
            Memory memory,
            Function function,
            Instruction instruction,
            int ordinal,
            String mnemonic,
            Set<String> emitted) {
        int width = referenceWidth(mnemonic);
        for (Reference reference : instruction.getReferencesFrom()) {
            Address target = reference.getToAddress();
            if (target == null || !target.isMemoryAddress()) {
                continue;
            }
            long offset = target.getOffset() & 0xffffffffL;
            boolean romReference = offset < ROM_HI;
            boolean ramReference = offset >= RAM_LO;
            if (!romReference && !ramReference) {
                continue;
            }
            String value = "";
            int exportedWidth = romReference ? width : 0;
            if (exportedWidth > 0) {
                try {
                    byte[] bytes = new byte[exportedWidth];
                    memory.getBytes(target, bytes);
                    value = hex(bytes);
                } catch (Exception error) {
                    continue;
                }
            }
            String referenceType = reference.getReferenceType()
                    .getName()
                    .toLowerCase(Locale.ROOT)
                    .replace(',', '_')
                    .replace(' ', '_');
            String row = String.format(
                    "%s,%s,%d,%s,%s,%d,%s,%s%n",
                    function.getEntryPoint(),
                    instruction.getAddress(),
                    ordinal,
                    mnemonic,
                    target,
                    exportedWidth,
                    value,
                    referenceType);
            if (emitted.add(row)) {
                out.print(row);
            }
        }
    }

    int referenceWidth(String mnemonic) {
        if (mnemonic.endsWith(".b")) {
            return 1;
        }
        if (mnemonic.endsWith(".w")) {
            return 2;
        }
        if (mnemonic.endsWith(".l")) {
            return 4;
        }
        return 0;
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
