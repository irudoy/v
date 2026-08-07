// InspectAddress.java - report ownership and references for selected addresses
// and optionally decompile the participating functions.
//
// Usage (headless):
//   -postScript InspectAddress.java <outdir|-> <addr_hex> [<addr_hex> ...]
//
// A dash disables file output. With an output directory, the script writes one
// decomp_<entry>.c file for every containing, preceding, or referencing
// function found across the selected addresses.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.io.File;
import java.io.PrintWriter;
import java.util.LinkedHashSet;
import java.util.Set;

public class InspectAddress extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) {
            printerr(
                "Usage: InspectAddress.java <outdir|-> "
                + "<addr_hex> [<addr_hex> ...]"
            );
            return;
        }

        File output = "-".equals(args[0]) ? null : new File(args[0]);
        if (output != null && !output.exists() && !output.mkdirs()) {
            throw new IllegalArgumentException(
                "cannot create output directory " + output
            );
        }

        Set<Address> functions = new LinkedHashSet<>();
        for (int index = 1; index < args.length; index++) {
            Address target;
            try {
                target = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace()
                    .getAddress(Long.parseLong(args[index], 16));
            } catch (RuntimeException error) {
                printerr("VQ_INSPECT invalid address " + args[index]);
                continue;
            }

            Function containing = getFunctionContaining(target);
            Function preceding = getFunctionBefore(target);
            println(
                "VQ_INSPECT target=" + target
                + " containing=" + describe(containing)
                + " preceding=" + describe(preceding)
            );
            add(functions, containing);
            if (containing == null) {
                add(functions, preceding);
            }

            ReferenceIterator references = currentProgram
                .getReferenceManager()
                .getReferencesTo(target);
            int count = 0;
            while (references.hasNext()) {
                Reference reference = references.next();
                Address from = reference.getFromAddress();
                Function owner = getFunctionContaining(from);
                println(
                    "VQ_INSPECT ref=" + from
                    + " type=" + reference.getReferenceType().getName()
                    + " owner=" + describe(owner)
                );
                add(functions, owner);
                count++;
            }
            println("VQ_INSPECT target=" + target + " references=" + count);
        }

        if (output == null) {
            println("VQ_INSPECT decompiled=0 output=-");
            return;
        }

        DecompInterface decompiler = new DecompInterface();
        int written = 0;
        try {
            decompiler.openProgram(currentProgram);
            for (Address entry : functions) {
                Function function = getFunctionAt(entry);
                if (function == null) {
                    continue;
                }
                DecompileResults result = decompiler.decompileFunction(
                    function, 60, monitor
                );
                String body = result.decompileCompleted()
                    ? result.getDecompiledFunction().getC()
                    : "// decompile failed: " + result.getErrorMessage();
                File path = new File(output, "decomp_" + entry + ".c");
                try (PrintWriter writer = new PrintWriter(path)) {
                    writer.println(
                        "// " + function.getName() + " @ " + entry
                        + " size=" + function.getBody().getNumAddresses()
                    );
                    writer.println(body);
                }
                written++;
            }
        } finally {
            decompiler.dispose();
        }
        println(
            "VQ_INSPECT decompiled=" + written + " output=" + output
        );
    }

    private void add(Set<Address> entries, Function function) {
        if (function != null) {
            entries.add(function.getEntryPoint());
        }
    }

    private String describe(Function function) {
        if (function == null) {
            return "-";
        }
        return function.getEntryPoint()
            + "(" + function.getName()
            + ",size=" + function.getBody().getNumAddresses()
            + ",bounds=" + function.getBody().getMinAddress()
            + ".." + function.getBody().getMaxAddress() + ")";
    }
}
