// MergeFuncs.java - join function fragments back into the function they belong to.
//
// Auto-analysis of SH-2E code creates two kinds of false function entries inside one
// function:
// - the Shared Return Calls analyzer gives a `bra` to a function entry a CALL_RETURN flow
//   override, so the jump becomes a call and its target stays a function of its own;
// - a function created at the first instruction after a literal pool cuts the body of the
//   function whose branch reaches that instruction.
// The body of the real function then ends at the fragment, and the exports attribute the
// fragment's instructions, references, and calls to the fragment.
//
// tools/ghidra/merges/<layout>.csv is the tracked repair registry of one layout of
// rom-images/homology.toml; apply it only to a program of that layout. Each row names a
// function entry and one fragment entry that belongs to it. For every entry the script
// clears the flow override of each instruction that references one of its fragments,
// removes the fragment functions, and recomputes the body of the entry from its flow, in
// one transaction. The transaction is rolled back, and the program keeps the entry
// unchanged, when a fragment is reached by a call without a flow override, when the entry
// is not a function, or when the recomputed body lacks a fragment or an instruction that
// references one. A fragment that is no function entry and lies in the body of its entry
// is already joined.
//
// Usage: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript MergeFuncs.java <merges/<layout>.csv>
// Without -readOnly the joined bodies persist for the next export; with -readOnly the
// script reports the result without saving it. The CSV path is absolute. CSV columns are
// entry,fragment,note; addresses are hexadecimal without 0x.
//@category VQ
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.FlowOverride;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.Reference;
import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class MergeFuncs extends GhidraScript {

    Listing listing;
    FunctionManager fm;

    @Override
    public void run() throws Exception {
        if (getScriptArgs().length < 1) {
            println("VQ_MERGE: missing <merges/<layout>.csv> argument");
            return;
        }
        listing = currentProgram.getListing();
        fm = currentProgram.getFunctionManager();

        Map<Address, List<Address>> fragments = new LinkedHashMap<>();
        BufferedReader br = new BufferedReader(new FileReader(getScriptArgs()[0]));
        String line;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] p = line.split(",", 3);
            if (p.length < 2 || p[0].trim().equalsIgnoreCase("entry")) continue;
            Address entry = toAddr(Long.parseLong(p[0].trim(), 16));
            Address fragment = toAddr(Long.parseLong(p[1].trim(), 16));
            fragments.computeIfAbsent(entry, k -> new ArrayList<>()).add(fragment);
        }
        br.close();

        int merged = 0, joined = 0, failed = 0;
        for (Map.Entry<Address, List<Address>> item : fragments.entrySet()) {
            if (monitor.isCancelled()) break;
            Address entry = item.getKey();
            List<Address> pending = new ArrayList<>();
            for (Address fragment : item.getValue()) {
                if (isJoined(entry, fragment)) {
                    println("VQ_MERGE " + entry + " already holds " + fragment);
                    joined++;
                } else {
                    pending.add(fragment);
                }
            }
            if (pending.isEmpty()) continue;
            int tx = currentProgram.startTransaction("merge-func");
            String problem = null;
            try {
                problem = merge(entry, pending);
            } catch (Exception e) {
                problem = e.toString();
            } finally {
                currentProgram.endTransaction(tx, problem == null);
            }
            if (problem == null) {
                Function f = fm.getFunctionAt(entry);
                println("VQ_MERGE " + entry + " joined " + pending + ": body "
                        + f.getBody().getNumAddresses() + " bytes in "
                        + f.getBody().getNumAddressRanges() + " ranges");
                merged += pending.size();
            } else {
                println("VQ_MERGE " + entry + " failed for " + pending + ": " + problem);
                failed += pending.size();
            }
        }
        println("VQ_MERGE merged=" + merged + " joined=" + joined + " failed=" + failed);
    }

    boolean isJoined(Address entry, Address fragment) {
        Function f = fm.getFunctionAt(entry);
        return f != null && fm.getFunctionAt(fragment) == null
                && f.getBody().contains(fragment);
    }

    // Join the fragments into the function at entry; null on success, else the reason.
    String merge(Address entry, List<Address> pending) throws Exception {
        Function f = fm.getFunctionAt(entry);
        if (f == null) return "no function at the entry";
        List<Address> sources = new ArrayList<>();
        for (Address fragment : pending) {
            for (Reference r : getReferencesTo(fragment)) {
                if (!r.getReferenceType().isFlow()) continue;
                Instruction ins = listing.getInstructionAt(r.getFromAddress());
                if (ins == null) continue;
                if (ins.getFlowOverride() != FlowOverride.NONE) {
                    ins.setFlowOverride(FlowOverride.NONE);
                } else if (r.getReferenceType().isCall()) {
                    return "the call at " + r.getFromAddress() + " reaches " + fragment;
                }
                sources.add(r.getFromAddress());
            }
            if (fm.getFunctionAt(fragment) != null && !fm.removeFunction(fragment)) {
                return "the fragment function " + fragment + " could not be removed";
            }
        }
        if (!CreateFunctionCmd.fixupFunctionBody(currentProgram, f, monitor)) {
            return "the body could not be recomputed";
        }
        AddressSetView body = fm.getFunctionAt(entry).getBody();
        for (Address fragment : pending) {
            if (!body.contains(fragment)) return "the body lacks " + fragment;
        }
        for (Address source : sources) {
            if (!body.contains(source)) return "the body lacks the reference at " + source;
        }
        return null;
    }
}
