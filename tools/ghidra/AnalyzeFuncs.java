// AnalyzeFuncs.java - run auto-analysis restricted to the bodies of listed functions.
//
// RecoverFuncs.java disassembles seed entries that auto-analysis never reached. The
// disassembler produces instructions only; operand references (RAM and peripheral
// reads and writes, literal-pool loads, resolved pool constants) come from the
// analyzers, which do not run in a -noanalysis session. Until they run, ExportXrefs
// lists no reference for the recovered bodies, and the graph shows the recovered
// functions without any RAM access.
//
// The pass marks the body of every listed function for all enabled analyzers of the
// program and waits for the analysis to finish. Nothing outside the listed bodies is
// scheduled; references and labels created at their targets are the ordinary output
// of the analyzers. Analyzing a body whose references already exist is idempotent.
//
// Headless invocation: -postScript AnalyzeFuncs.java <addr>...
// Arguments are hexadecimal function entry addresses. Run without -readOnly so the
// references persist for the next ExportXrefs; with -readOnly the report is a dry run.
//@category VQ

import ghidra.app.plugin.core.analysis.AutoAnalysisManager;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;

public class AnalyzeFuncs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            println("VQ_AF usage: AnalyzeFuncs.java <addr>...");
            return;
        }
        AddressSet set = new AddressSet();
        int listed = 0;
        for (String arg : args) {
            Address entry = currentProgram.getAddressFactory().getDefaultAddressSpace()
                    .getAddress(Long.parseLong(arg, 16));
            Function fn = getFunctionAt(entry);
            if (fn == null) {
                println("VQ_AF no function at " + entry);
                continue;
            }
            set.add(fn.getBody());
            listed++;
        }
        if (set.isEmpty()) {
            println("VQ_AF nothing to analyze");
            return;
        }
        long before = countReferences(set);
        AutoAnalysisManager manager = AutoAnalysisManager.getAnalysisManager(currentProgram);
        manager.initializeOptions();
        manager.reAnalyzeAll(set);
        manager.startAnalysis(monitor);
        long after = countReferences(set);
        println("VQ_AF functions=" + listed + " bytes=" + set.getNumAddresses()
                + " references " + before + " -> " + after);
    }

    private long countReferences(AddressSet set) {
        long count = 0;
        for (Instruction ins : currentProgram.getListing().getInstructions(set, true)) {
            count += ins.getReferencesFrom().length;
        }
        return count;
    }
}
