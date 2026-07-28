// Export machine references to 16-bit ROM constants and instruction immediates.
//
// The output is intentionally semantic-free. extract_static_bindings.py joins
// exact 16-bit values with known SID 0x22 DIDs and builds a review worklist.
// A literal match is only a candidate: this script does not assert that the
// function is a diagnostic dispatcher or that any RAM reference is its result.
//
// Usage:
// tools/ghidra/headless-analyze.sh <project_dir> <project> -process <bin> \
//   -noanalysis -scriptPath tools/ghidra \
//   -postScript ExportDiagnosticRefs.java <outdir>
//
// Writes <outdir>/diagnostic_refs.csv:
// func_addr,site,source_kind,literal_addr,value_hex
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.PrintWriter;
import java.util.Set;
import java.util.TreeSet;

public class ExportDiagnosticRefs extends GhidraScript {
    static final long ROM_HI = 0x180000L;

    private String hex8(long value) {
        return String.format("%08x", value & 0xFFFFFFFFL);
    }

    private String hex4(long value) {
        return String.format("%04x", value & 0xFFFFL);
    }

    @Override
    public void run() throws Exception {
        String outdir = getScriptArgs().length > 0 ? getScriptArgs()[0] : "/tmp";
        new File(outdir).mkdirs();

        FunctionManager functions = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        Memory memory = currentProgram.getMemory();
        Set<String> rows = new TreeSet<String>();

        for (Function function : functions.getFunctions(true)) {
            String functionAddress = hex8(function.getEntryPoint().getOffset());
            for (Instruction instruction :
                    listing.getInstructions(function.getBody(), true)) {
                String site = hex8(instruction.getAddress().getOffset());

                for (Reference reference : instruction.getReferencesFrom()) {
                    Address target = reference.getToAddress();
                    if (target == null || !target.isMemoryAddress()) {
                        continue;
                    }
                    long offset = target.getOffset() & 0xFFFFFFFFL;
                    if (offset >= ROM_HI) {
                        continue;
                    }
                    try {
                        int value = memory.getShort(target) & 0xFFFF;
                        rows.add(
                            functionAddress + "," + site + ",rom_ref,"
                            + hex8(offset) + "," + hex4(value)
                        );
                    } catch (MemoryAccessException error) {
                        // Skip uninitialized or one-byte tail locations.
                    }
                }

                for (int operand = 0;
                        operand < instruction.getNumOperands();
                        operand++) {
                    for (Object object : instruction.getOpObjects(operand)) {
                        if (!(object instanceof Scalar)) {
                            continue;
                        }
                        Scalar scalar = (Scalar) object;
                        long value = scalar.getUnsignedValue();
                        if (value <= 0xFFFFL) {
                            rows.add(
                                functionAddress + "," + site
                                + ",immediate,," + hex4(value)
                            );
                        }
                    }
                }
            }
        }

        PrintWriter output = new PrintWriter(
            new File(outdir, "diagnostic_refs.csv")
        );
        output.println("func_addr,site,source_kind,literal_addr,value_hex");
        for (String row : rows) {
            output.println(row);
        }
        output.close();
        println(
            "VQ_DIAGNOSTIC_REFS refs=" + rows.size() + " dir=" + outdir
        );
    }
}
