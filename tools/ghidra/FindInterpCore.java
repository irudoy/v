// FindInterpCore.java - detect interpolation cores and their wrappers by scanning data.
// The current discovery contract is in tools/map-analysis-pipeline.md.
//
// SIGNATURE: a slot plus TWO levels of indirection. The core address is stored in ROM as a
// 4-byte word (a literal-pool constant); an entry loads it with mov.l @(disp,pc),rN and
// transfers control through jsr @rN or jmp @rN (tail branch). A direct call does not need a
// slot, which distinguishes the access library from other code.
//
// A slot alone is insufficient: an accessor calls an ENTRY by the same mechanism, so a slot
// with jsr captures the whole indirect-call layer at once. Entries rank above cores by caller
// count (0x26370 has 62 callers versus 11 for core 0x26944). The second indirection level
// distinguishes a core: its callers are themselves slot targets, while accessors that call an
// entry are not. The indirect_callers column measures this property and drives the ranking
// instead of caller count.
//
// Properties that do NOT distinguish a core:
//   - caller count: 253 JK03A functions have calls from >= 2 locations, but only four are
//     cores;
//   - being a leaf: five of thirteen cores call shared helpers (0x26944 and 0x26984 both
//     call 0x26c78; 0x26a60 calls core 0x26740), so a "slot points to a leaf" filter would
//     discard the main core. Leaf status is reported in the outs column, not used as a
//     filter;
//   - being defined as a function: implicit-axis bank entries share one shift chain, and
//     Ghidra does not define 0x26a80/0x26a84/0x26a88 as functions at all (the body at
//     0x26a5c is four bytes). Therefore, a slot target is checked for code
//     (getInstructionAt), not for a function entry. Function definition belongs to Ghidra,
//     not to the firmware.
//
// WHAT THE SCAN LOCATES: the access library, not the core level within it. A core and a
// helper called by that core have the same signature: 0x26c78, the shared helper for 0x26944
// and 0x26984, ranks 11th despite not being a core. The handwritten defs/registries/<rom>.interp.csv
// registry identifies cores within this layer by the clamp in the delay slot, which also
// defines entry geometry. The script supplies candidates with evidence for each.
//
// Measured on JK03A (13 registry cores, 34 entries): all 13 are found. Four hub cores
// (0x26740, 0x26944, 0x26984, 0x26b84) rank 2nd, 3rd, 6th, and 8th among 799 candidates.
// The implicit-axis bank (0x26a5c..0x26a88, one entry each) ranks 53rd through 63rd. It is
// found but does not stand out by entry count because more than 200 candidates also have one
// entry. The bank is visible instead as eight adjacent addresses spaced four bytes apart and
// requires human inspection rather than a threshold.
//
// Independent cross-check: centrality in the call-graph projection
// (tools/memgraph/queries.cypher, section 8.2). PageRank places the access library near the
// top even before Stage 3. This signal is independent of the scan and therefore validates it
// instead of repeating the same evidence.
//
// Headless invocation: -postScript FindInterpCore.java <out_dir> [<min_wrappers>]
// Output: interp_core.csv (kernel,name,size,outs,slots,callers,indirect_callers,depth,
//        is_leaf,slot_list,caller_list), ranked by depth and entry count.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class FindInterpCore extends GhidraScript {

    // Core candidate: an address stored in a pool and functions that call through its slot.
    static class Cand {
        Address entry;
        Set<Address> slots = new LinkedHashSet<>();
        Set<Address> wrappers = new LinkedHashSet<>();
        int indirect;                       // callers that are themselves slot targets

        // Fraction of callers represented in pools: approximately 1.0 for a core, 0 for an entry.
        double depth() { return wrappers.isEmpty() ? 0 : (double) indirect / wrappers.size(); }
    }

    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 1) {
            println("VQ_CORE need: <out_dir> [<min_wrappers>]");
            return;
        }
        String outDir = a[0];
        int minWrappers = a.length > 1 ? Integer.parseInt(a[1]) : 1;

        Memory mem = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        ReferenceManager rm = currentProgram.getReferenceManager();

        // 1. Slots: 4-byte-aligned ROM words whose values point to code. Alignment is not
        //    heuristic: mov.l reads a long word only at a 4-byte boundary, and a pool constant
        //    read differently cannot become a call. Check the target for an instruction rather
        //    than a function entry because the implicit-axis bank is not defined as functions.
        Map<Long, Cand> cands = new TreeMap<>();
        int words = 0;
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized()) continue;
            Address lo = b.getStart(), hi = b.getEnd();
            for (long off = align4(lo.getOffset()); off + 3 <= hi.getOffset(); off += 4) {
                if (monitor.isCancelled()) return;
                Address at = lo.getNewAddress(off);
                long v;
                try { v = mem.getInt(at) & 0xFFFFFFFFL; } catch (Exception e) { continue; }
                words++;
                if (v == 0 || (v & 1) != 0) continue;          // SH-2 instructions are even-aligned
                Address target;
                try { target = lo.getNewAddress(v); } catch (Exception e) { continue; }
                if (listing.getInstructionAt(target) == null) continue;
                Cand c = cands.computeIfAbsent(v, k -> new Cand());
                c.slots.add(at);
                c.entry = target;
            }
        }
        // 2. Entries: functions that reference a slot AND branch indirectly through jsr @rN
        //    (call) or jmp @rN (tail branch into a finisher). A reference without an indirect
        //    branch means the address was not loaded for control transfer.
        for (Cand c : cands.values()) {
            for (Address slot : c.slots) {
                ReferenceIterator ri = rm.getReferencesTo(slot);
                while (ri.hasNext()) {
                    Function wf = fm.getFunctionContaining(ri.next().getFromAddress());
                    if (wf != null && hasIndirectBranch(listing, wf)) {
                        c.wrappers.add(wf.getEntryPoint());
                    }
                }
            }
        }

        // 3. Real slot targets are only those whose slots are read. A word that happens to
        //    point to code is not a target. Measuring all words is invalid: 2,181 such words
        //    exist for 2,312 ROM functions, so "the caller is a slot target" would be true
        //    almost always and would not discriminate anything.
        Set<Long> called = new LinkedHashSet<>();
        for (Map.Entry<Long, Cand> e : cands.entrySet()) {
            if (!e.getValue().wrappers.isEmpty()) called.add(e.getKey());
        }

        // 4. Second indirection level: count candidate callers that are themselves called
        //    through a slot. All callers of a core have this property because entries call
        //    cores and accessors call entries through slots. Almost no callers of an entry do,
        //    because accessors are absent from pools. This separates the layers, while caller
        //    count incorrectly ranks an entry above a core.
        List<Cand> hits = new ArrayList<>();
        for (Cand c : cands.values()) {
            if (c.wrappers.isEmpty()) continue;
            for (Address wa : c.wrappers) {
                if (called.contains(wa.getOffset() & 0xFFFFFFFFL)) c.indirect++;
            }
            if (c.wrappers.size() >= minWrappers) hits.add(c);
        }
        hits.sort(Comparator.comparingDouble((Cand c) -> -c.depth())
                            .thenComparingInt(c -> -c.indirect)
                            .thenComparing(c -> c.entry));

        PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "interp_core.csv")));
        w.println("kernel,name,size,outs,slots,callers,indirect_callers,depth,is_leaf,"
                  + "slot_list,caller_list");
        for (Cand c : hits) {
            Function f = fm.getFunctionAt(c.entry);
            int outs = f == null ? -1 : countCalls(listing, f);
            w.println(String.format("%s,%s,%d,%d,%d,%d,%d,%.2f,%b,%s,%s",
                    c.entry, f == null ? "" : f.getName(),
                    f == null ? 0 : f.getBody().getNumAddresses(), outs,
                    c.slots.size(), c.wrappers.size(), c.indirect, c.depth(), outs == 0,
                    join(c.slots), join(c.wrappers)));
        }
        w.close();
        println("VQ_CORE words=" + words + " slot_values=" + cands.size()
                + " candidates=" + hits.size() + " min_wrappers=" + minWrappers);
        int top = 0;
        for (Cand c : hits) {
            if (top++ >= 16) break;
            println(String.format("VQ_CORE %s callers=%d indirect=%d depth=%.2f",
                    c.entry, c.wrappers.size(), c.indirect, c.depth()));
        }
    }

    static long align4(long v) { return (v + 3) & ~3L; }

    String join(Set<Address> s) {
        StringBuilder sb = new StringBuilder();
        for (Address a : s) {
            if (sb.length() > 0) sb.append(';');
            sb.append(a);
        }
        return sb.toString();
    }

    // jsr @rN is an indirect call and jmp @rN is a tail branch. Both transfer an entry into
    // the core; checking only jsr loses entries that transfer control without returning.
    boolean hasIndirectBranch(Listing listing, Function f) {
        InstructionIterator it = listing.getInstructions(f.getBody(), true);
        while (it.hasNext()) {
            String m = it.next().getMnemonicString().toLowerCase();
            if (m.startsWith("jsr") || m.startsWith("jmp")) return true;
        }
        return false;
    }

    int countCalls(Listing listing, Function f) {
        int n = 0;
        InstructionIterator it = listing.getInstructions(f.getBody(), true);
        while (it.hasNext()) {
            for (Reference r : it.next().getReferencesFrom()) {
                if (r.getReferenceType().isCall()) n++;
            }
        }
        return n;
    }
}
