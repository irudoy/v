// ResolveAccessors.java - differential operand resolution for map accessors
// (section 6 of tools/map-flag-pipeline.md).
//
// The site set matches the MapInventory census (slots containing a kernel value ->
// wrappers that reference a slot -> call references to a wrapper entry), so the mechanisms
// are compared site by site. Every site emits both triples:
//   bt_r4/r5/r6 - MapInventory.backtrack: 14 instructions backward to the nearest PC literal
//                 (the baseline used to build the current census);
//   df_r4..r7   - data flow: CALL/CALLIND input varnodes from HighFunction (condition A).
//                 A RAM varnode is a pool slot whose value is the slot contents;
//                 register/unique varnodes are reduced with a backward p-code slice.
// Fallback: SymbolicPropogator over instructions for varnodes not reduced by the slice.
//
// GBR (condition B) is resolved locally: each function sets its own value (`ldc rN,gbr`).
// JK03A has both a RAM base (FUN_0003b75c: gbr=0xffff1dec) and a ROM base
// (gbr=0x11ebe in 0x4e2xx accessors). Both the decompiler and SymbolicPropogator can
// therefore reduce gbr from the function entry; a global register context for gbr is
// incorrect. Functions that receive gbr from their caller produce a gbr-relative operand
// (kind gbrrel).
//
// Sites outside functions: Ghidra does not define a function for a region without direct
// calls, and the decompiler cannot reach it (while backtrack works, producing bt_only).
// Such regions are recovered: the region begins with the prologue after the previous
// function's rts, and Ghidra builds its body from control flow. Under -readOnly, recovered
// definitions remain in memory. The same definition gap hides these calls from ExportGraph
// and leaves their wrappers without callers in the graph.
//
// A site's verdict is based on the r4/r5/r6 triple, with precedence
// selector > conflict > bt_only > df_only > agree:
//   agree     - both triples produced the same values;
//   df_only   - data flow recovered a value that backtrack did not;
//   bt_only   - backtrack recovered a value that data flow did not (analysis regression);
//   conflict  - bases differ (a latent nearestLoad heuristic error in the census);
//   selector  - branching defines the operand, so the site has a set of values.
// The acceptance invariant is that data flow covers backtrack, meaning bt_only = 0. The
// invariant does not apply to selector sites: by construction, backtrack yields one literal
// and cannot fully represent a set.
//
// Operand branching (MULTIEQUAL). A conditionally selected base or axis reaches a call as
// a phi node: `if (cfg) t = A; else t = B;` gives CALL a merge with one input per incoming
// block edge instead of a single value. Reducing it to one value is fundamentally wrong:
// both tables exist, and calibration rather than analysis selects the executed one. Such a
// site emits one row per branch, with its number in the branch column.
//
// Build each triple by index rather than by taking a Cartesian product: input i of every phi
// in one block arrives through edge i, so (r4,r5,r6) for branch i is a consistent triple.
// Cross-pairs such as a base from one branch and an axis from another do not occur in code.
// This applies only when every operand phi belongs to the same block and has equal length.
// Otherwise, alignment is unsupported and the fallback leaves the site as one row.
//
// Headless invocation: -postScript ResolveAccessors.java <out_dir> <kernel_hex>
// Output: accessors.<kernel>.csv, one file per census. Several table-access cores exist
// (JK03A: 0x26944 for byte axes, 0x26984 and 0x26b84 for word axes). Run the script for
// each core; the loader builds the calibration layer from all censuses together. Therefore,
// the filename identifies the core and every row carries a kernel column.
//   kernel,wrapper,slot,accessor,callsite,func,bt_r4,bt_r5,bt_r6,df_r4,df_r5,df_r6,df_r7,
//   k4,k5,k6,k7,verdict
// func: orig (function was already defined) | recovered (created here) | none.
// Source of each data-flow operand in columns k4..k7: pool (dereferenced pool slot), const,
// slice (reduced through p-code), sp (SymbolicPropogator fallback), gbrrel (gbr-relative
// value with gbr supplied by the caller), dyn (not reducible), or none (no input).
//@category VQ
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.PcodeBlockBasic;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.PcodeOpAST;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;
import ghidra.program.util.ContextEvaluatorAdapter;
import ghidra.program.util.SymbolicPropogator;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class ResolveAccessors extends GhidraScript {

    static final long ROM_HI = 0x180000L;
    static final int SLICE_DEPTH = 12;      // p-code reduction depth
    static final int REGION_SCAN = 4096;    // scan limit for a region outside functions

    Listing listing;
    Memory mem;
    FunctionManager fm;
    ReferenceManager rm;
    Register rGbr;
    Register[] argRegs = new Register[4];   // r4, r5, r6, r7
    boolean lastGbrRel;                     // SP returned a gbr-relative value; gbr was not reduced

    DecompInterface ifc;
    Map<Address, HighFunction> hfCache = new HashMap<>();
    Map<Address, SymbolicPropogator> spCache = new HashMap<>();
    Map<Address, Address[]> regionCache = new HashMap<>();

    static class Site {
        Address wrapper, slot, at, accessor;
        Function func;
        String fsrc = "none";               // orig | recovered | none
        long[] bt = {-1, -1, -1};
        long[] df = {-1, -1, -1, -1};
        String[] kind = {"none", "none", "none", "none"};
        List<long[]> alts = new ArrayList<>();   // selector branches after the first
    }

    public void run() throws Exception {
        String[] a = getScriptArgs();
        String outDir = a[0];
        long kernel = Long.parseLong(a[1], 16);

        listing = currentProgram.getListing();
        mem = currentProgram.getMemory();
        fm = currentProgram.getFunctionManager();
        rm = currentProgram.getReferenceManager();
        rGbr = currentProgram.getRegister("gbr");
        for (int i = 0; i < 4; i++) argRegs[i] = currentProgram.getRegister("r" + (i + 4));

        List<Address> slots = findSlots(kernel);
        Map<Function, Address> wrappers = findWrappers(slots);
        List<Site> sites = collectSites(wrappers);
        println("VQ_RES input: slots=" + slots.size() + " wrappers=" + wrappers.size()
                + " call_sites=" + sites.size());

        int recovered = recoverFuncs(sites);
        println("VQ_RES recovered functions: " + recovered);

        ifc = new DecompInterface();
        try {
            ifc.openProgram(currentProgram);
            int done = 0;
            for (Site s : sites) {
                try { s.bt = backtrack(s.at); } catch (Exception e) { /* best-effort baseline */ }
                dataflow(s);
                if (++done % 25 == 0) println("  ... " + done + "/" + sites.size());
            }
        } finally {
            ifc.dispose();
        }

        write(new File(outDir, "accessors." + Long.toHexString(kernel) + ".csv"), sites, kernel);
        summary(sites, wrappers);
    }

    // Recover functions for sites outside existing definitions. Build each body from control
    // flow beginning at the region start (the prologue after the previous function's rts).
    // A region can contain several consecutive undefined functions, so repeat passes while
    // coverage grows: every created function advances the region start to the next one.
    int recoverFuncs(List<Site> sites) {
        int made = 0;
        for (int pass = 0; pass < 16; pass++) {
            int before = made;
            for (Site s : sites) {
                if (s.func != null) continue;
                Address st = regionOf(s.at)[0];
                if (st == null || fm.getFunctionContaining(st) != null) continue;
                int tx = currentProgram.startTransaction("recover-func");
                boolean ok = false;
                try {
                    ok = createFunction(st, null) != null;
                } catch (Exception e) {
                    println("  failed to recover " + st + ": " + e);
                } finally {
                    currentProgram.endTransaction(tx, ok);
                }
                if (ok) made++;
            }
            regionCache.clear();
            for (Site s : sites) {
                if (s.func != null) continue;
                s.func = fm.getFunctionContaining(s.at);
                if (s.func != null) {
                    s.accessor = s.func.getEntryPoint();
                    s.fsrc = "recovered";
                } else {
                    s.accessor = regionOf(s.at)[0];
                }
            }
            if (made == before) break;
        }
        return made;
    }

    // 1. Slots: locations containing the kernel value (BE u32).
    List<Address> findSlots(long kernel) throws Exception {
        byte[] pat = {(byte) ((kernel >> 24) & 0xff), (byte) ((kernel >> 16) & 0xff),
                      (byte) ((kernel >> 8) & 0xff), (byte) (kernel & 0xff)};
        byte[] mask = {-1, -1, -1, -1};
        List<Address> out = new ArrayList<>();
        Address start = currentProgram.getMinAddress();
        while (true) {
            Address f = mem.findBytes(start, pat, mask, true, monitor);
            if (f == null) break;
            out.add(f);
            start = f.add(1);
        }
        return out;
    }

    // 2. Wrappers: functions that reference a slot.
    Map<Function, Address> findWrappers(List<Address> slots) {
        Map<Function, Address> out = new LinkedHashMap<>();
        for (Address slot : slots) {
            ReferenceIterator ri = rm.getReferencesTo(slot);
            while (ri.hasNext()) {
                Function wf = fm.getFunctionContaining(ri.next().getFromAddress());
                if (wf != null) out.putIfAbsent(wf, slot);
            }
        }
        return out;
    }

    // 3. Sites: call references to a wrapper entry.
    List<Site> collectSites(Map<Function, Address> wrappers) {
        List<Site> out = new ArrayList<>();
        for (Map.Entry<Function, Address> e : wrappers.entrySet()) {
            Address wentry = e.getKey().getEntryPoint();
            ReferenceIterator ri = rm.getReferencesTo(wentry);
            while (ri.hasNext()) {
                Reference r = ri.next();
                if (!r.getReferenceType().isCall()) continue;
                Site s = new Site();
                s.wrapper = wentry;
                s.slot = e.getValue();
                s.at = r.getFromAddress();
                s.func = fm.getFunctionContaining(s.at);
                if (s.func != null) { s.accessor = s.func.getEntryPoint(); s.fsrc = "orig"; }
                else s.accessor = regionOf(s.at)[0];
                out.add(s);
            }
        }
        return out;
    }

    // Condition A: CALLIND arguments recovered by the decompiler as ordered call inputs
    // (in[1]=r4, in[2]=r5, in[3]=r6, in[4]=r7).
    void dataflow(Site s) {
        if (s.func != null) {
            HighFunction hf = highFunc(s.func);
            PcodeOpAST call = hf == null ? null : findCall(hf, s.at);
            if (call != null) {
                Varnode[] in = call.getInputs();
                for (int k = 0; k < 4 && k + 1 < in.length; k++) {
                    Long v = argValue(in[k + 1]);
                    if (v != null) { s.df[k] = v; s.kind[k] = kindOf(in[k + 1]); }
                    else s.kind[k] = "dyn";
                }
                selectorBranches(s, in);
            }
        }
        // Fallback for varnodes not reduced by the slice.
        for (int k = 0; k < 4; k++) {
            if (s.df[k] != -1) continue;
            lastGbrRel = false;
            Long v = propagated(s, argRegs[k]);
            if (v != null) { s.df[k] = v; s.kind[k] = "sp"; }
            else if (lastGbrRel) s.kind[k] = "gbrrel";
        }
        // The fallback recovers an operand shared by all branches after expansion; copy it
        // into each branch.
        for (long[] t : s.alts)
            for (int k = 0; k < 4; k++) if (t[k] == -1) t[k] = s.df[k];
    }

    // Find a phi beneath an operand through transfers (COPY/CAST/extensions) inserted by the
    // decompiler between the merge and the call. Stop beyond transfers because arithmetic
    // over a merge computes an address instead of selecting a table.
    PcodeOp phiOf(Varnode vn, int depth) {
        if (vn == null || depth > SLICE_DEPTH) return null;
        PcodeOp d = vn.getDef();
        if (d == null) return null;
        switch (d.getOpcode()) {
            case PcodeOp.MULTIEQUAL:
                return d;
            case PcodeOp.COPY:
            case PcodeOp.CAST:
            case PcodeOp.SUBPIECE:
            case PcodeOp.INT_ZEXT:
            case PcodeOp.INT_SEXT:
                return phiOf(d.getInput(0), depth + 1);
            default:
                return null;
        }
    }

    // Expand operand branching into one row per branch. The first branch occupies the site's
    // df/kind fields and the rest go into alts. Validate applicability before writing:
    // operand phi nodes must be in one block and have equal input counts. Otherwise, index
    // alignment is unsupported and the site remains one row.
    void selectorBranches(Site s, Varnode[] in) {
        PcodeOp[] phi = new PcodeOp[3];
        PcodeBlockBasic blk = null;
        int n = 0;
        for (int k = 0; k < 3 && k + 1 < in.length; k++) {
            PcodeOp d = phiOf(in[k + 1], 0);
            if (!(d instanceof PcodeOpAST)) continue;
            PcodeBlockBasic b = ((PcodeOpAST) d).getParent();
            if (b == null) continue;
            // Index alignment is valid only within one block and for equally sized merges.
            // Exclude an operand merged differently. Traversal visits the base first, so it
            // determines the length instead of an auxiliary argument.
            if (n == 0) { n = d.getNumInputs(); blk = b; }
            else if (d.getNumInputs() != n || blk != b) continue;
            phi[k] = d;
        }
        if (n < 2) return;

        // Exclude an operand whose branches cannot be reduced to values and keep its prior
        // analysis. Accessor branches can differ in both ROM pointers and a runtime RAM input,
        // but the latter is unrelated to table selection.
        long[][] val = new long[3][];
        for (int k = 0; k < 3; k++) {
            if (phi[k] == null) continue;
            long[] col = new long[n];
            for (int i = 0; i < n; i++) {
                Long v = eval(phi[k].getInput(i), 0);
                if (v == null) { col = null; break; }
                col[i] = v & 0xFFFFFFFFL;
            }
            if (col == null) phi[k] = null;
            else val[k] = col;
        }
        if (val[0] == null && val[1] == null && val[2] == null) return;

        List<long[]> branches = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            long[] t = {s.df[0], s.df[1], s.df[2], s.df[3]};
            for (int k = 0; k < 3; k++) if (val[k] != null) t[k] = val[k][i];
            branches.add(t);
        }
        // Branches with identical values are one read through different paths, not different tables.
        List<long[]> uniq = new ArrayList<>();
        for (long[] t : branches) {
            boolean dup = false;
            for (long[] u : uniq) if (u[0] == t[0] && u[1] == t[1] && u[2] == t[2]) dup = true;
            if (!dup) uniq.add(t);
        }
        if (uniq.size() < 2) return;

        for (int k = 0; k < 3; k++) {
            if (phi[k] == null) continue;
            s.df[k] = uniq.get(0)[k];
            s.kind[k] = "phi";
        }
        for (int i = 1; i < uniq.size(); i++) s.alts.add(uniq.get(i));
    }

    // Call argument value: a RAM varnode is a cell (pool slot) whose value is its contents;
    // a constant is used directly; register/unique varnodes use backward-slice reduction.
    Long argValue(Varnode vn) {
        if (vn == null) return null;
        if (vn.isConstant()) return vn.getOffset() & 0xFFFFFFFFL;
        if (isRam(vn)) return readWord(vn.getAddress(), vn.getSize());
        Long v = eval(vn, 0);
        return v == null ? null : (v & 0xFFFFFFFFL);
    }

    String kindOf(Varnode vn) {
        if (vn.isConstant()) return "const";
        if (isRam(vn)) return "pool";
        return "slice";
    }

    // Backward-slice reduction follows define-use chains from register/unique varnodes to a
    // constant. gbr needs no special case because the function sets it with ldc and its
    // definition reduces through the common path.
    Long eval(Varnode vn, int depth) {
        if (vn == null || depth > SLICE_DEPTH) return null;
        if (vn.isConstant()) return vn.getOffset();
        if (isRam(vn)) return readWord(vn.getAddress(), vn.getSize());
        PcodeOp d = vn.getDef();
        return d == null ? null : evalOp(d, depth + 1);
    }

    Long evalOp(PcodeOp op, int depth) {
        Long a, b, c;
        switch (op.getOpcode()) {
            case PcodeOp.COPY:
            case PcodeOp.CAST:
            case PcodeOp.INT_ZEXT:
            case PcodeOp.INT_SEXT:
            case PcodeOp.SUBPIECE:
                return eval(op.getInput(0), depth);
            case PcodeOp.INT_ADD:
            case PcodeOp.PTRSUB:                 // &global: address, not contents
                a = eval(op.getInput(0), depth); b = eval(op.getInput(1), depth);
                return (a == null || b == null) ? null : a + b;
            case PcodeOp.INT_SUB:
                a = eval(op.getInput(0), depth); b = eval(op.getInput(1), depth);
                return (a == null || b == null) ? null : a - b;
            case PcodeOp.INT_MULT:
                a = eval(op.getInput(0), depth); b = eval(op.getInput(1), depth);
                return (a == null || b == null) ? null : a * b;
            case PcodeOp.INT_LEFT:
                a = eval(op.getInput(0), depth); b = eval(op.getInput(1), depth);
                return (a == null || b == null) ? null : a << b;
            case PcodeOp.PTRADD:                 // base + index*size
                a = eval(op.getInput(0), depth); b = eval(op.getInput(1), depth);
                c = eval(op.getInput(2), depth);
                return (a == null || b == null || c == null) ? null : a + b * c;
            case PcodeOp.LOAD:
                a = eval(op.getInput(1), depth);
                if (a == null) return null;
                return readWord(toAddr(a & 0xFFFFFFFFL), op.getOutput().getSize());
            default:
                return null;                     // MULTIEQUAL/INDIRECT and others: not one value
        }
    }

    // Fallback: register value at the site address from symbolic propagation. A
    // register-relative result means the caller supplies the base (for gbr, condition B
    // beyond the function). No concrete value exists, so mark the site gbrrel instead of
    // dropping it.
    Long propagated(Site s, Register reg) {
        if (reg == null) return null;
        SymbolicPropogator sp = propagator(s);
        if (sp == null) return null;
        SymbolicPropogator.Value v = sp.getRegisterValue(s.at, reg);
        if (v == null) return null;
        if (v.isRegisterRelativeValue()) {
            Register rel = v.getRelativeRegister();
            if (rGbr != null && rel != null && rGbr.getName().equals(rel.getName())) lastGbrRel = true;
            return null;
        }
        return v.getValue() & 0xFFFFFFFFL;
    }

    SymbolicPropogator propagator(Site s) {
        Address key = s.accessor;
        if (key == null) return null;
        if (spCache.containsKey(key)) return spCache.get(key);
        SymbolicPropogator sp = null;
        try {
            AddressSetView body = s.func != null ? s.func.getBody()
                    : new AddressSet(regionOf(s.at)[0], regionOf(s.at)[1]);
            // recordStartEndState=true makes getRegisterValue return the value at the address,
            // not the final value.
            sp = new SymbolicPropogator(currentProgram, true);
            sp.flowConstants(key, body, new ContextEvaluatorAdapter(), false, monitor);
        } catch (Exception e) {
            println("  SP failed at " + key + ": " + e);
            sp = null;
        }
        spCache.put(key, sp);
        return sp;
    }

    // Bounds of a code region outside functions: walk backward and forward through
    // instructions while none belongs to a function.
    Address[] regionOf(Address at) {
        Instruction ins = listing.getInstructionContaining(at);
        if (ins == null) return new Address[]{at, at};
        Address[] hit = regionCache.get(ins.getAddress());
        if (hit != null) return hit;
        Address lo = ins.getAddress(), hi = ins.getMaxAddress();
        Instruction cur = ins;
        for (int k = 0; k < REGION_SCAN; k++) {
            Instruction p = listing.getInstructionBefore(cur.getAddress());
            if (p == null || fm.getFunctionContaining(p.getAddress()) != null) break;
            cur = p; lo = cur.getAddress();
        }
        cur = ins;
        for (int k = 0; k < REGION_SCAN; k++) {
            Instruction n = listing.getInstructionAfter(cur.getAddress());
            if (n == null || fm.getFunctionContaining(n.getAddress()) != null) break;
            cur = n; hi = cur.getMaxAddress();
        }
        Address[] out = {lo, hi};
        regionCache.put(ins.getAddress(), out);
        return out;
    }

    HighFunction highFunc(Function f) {
        Address k = f.getEntryPoint();
        if (hfCache.containsKey(k)) return hfCache.get(k);
        HighFunction hf = null;
        try {
            DecompileResults r = ifc.decompileFunction(f, 90, monitor);
            hf = r.getHighFunction();
        } catch (Exception e) { /* the fallback below will handle it */ }
        hfCache.put(k, hf);
        return hf;
    }

    PcodeOpAST findCall(HighFunction hf, Address at) {
        Iterator<PcodeOpAST> it = hf.getPcodeOps(at);
        while (it.hasNext()) {
            PcodeOpAST op = it.next();
            if (op.getOpcode() == PcodeOp.CALL || op.getOpcode() == PcodeOp.CALLIND) return op;
        }
        return null;
    }

    // Baseline: MapInventory.backtrack, 14 instructions backward to the nearest
    // PC-relative load.
    long[] backtrack(Address site) {
        long[] out = {-1, -1, -1};
        Instruction ins = listing.getInstructionContaining(site);
        if (ins == null) return out;
        Instruction cur = listing.getInstructionBefore(ins.getAddress());
        for (int k = 0; k < 14 && cur != null; k++) {
            for (Object o : cur.getResultObjects()) {
                if (!(o instanceof Register)) continue;
                Register rg = (Register) o;
                int idx = -1;
                for (int i = 0; i < 3; i++) if (rg.equals(argRegs[i])) idx = i;
                if (idx >= 0 && out[idx] == -1) {
                    long v = nearestLoad(cur);
                    out[idx] = (v == -1) ? -2 : v;
                }
            }
            if (out[0] != -1 && out[1] != -1 && out[2] != -1) break;
            cur = listing.getInstructionBefore(cur.getAddress());
        }
        for (int i = 0; i < 3; i++) if (out[i] == -2) out[i] = -1;
        return out;
    }

    long nearestLoad(Instruction cur) {
        long ia = cur.getAddress().getOffset() & 0xFFFFFFFFL;
        Address best = null;
        long bestDist = Long.MAX_VALUE;
        for (Reference r : cur.getReferencesFrom()) {
            Address to = r.getToAddress();
            if (to == null || !to.isMemoryAddress()) continue;
            long off = to.getOffset() & 0xFFFFFFFFL;
            long dist = off > ia ? off - ia : ia - off;
            if (dist < bestDist) { bestDist = dist; best = to; }
        }
        if (best != null && bestDist < 0x800 && (best.getOffset() & 0xFFFFFFFFL) < ROM_HI) {
            try { return mem.getInt(best) & 0xFFFFFFFFL; } catch (Exception e) { }
        }
        return -1;
    }

    boolean isRam(Varnode vn) {
        return vn != null && !vn.isConstant() && !vn.isRegister() && !vn.isUnique()
                && "ram".equals(vn.getAddress().getAddressSpace().getName());
    }

    Long readWord(Address a, int size) {
        if (a == null || (a.getOffset() & 0xFFFFFFFFL) >= ROM_HI) return null;
        try {
            switch (size) {
                case 1: return (long) (mem.getByte(a) & 0xff);
                case 2: return (long) (mem.getShort(a) & 0xffff);
                default: return mem.getInt(a) & 0xFFFFFFFFL;
            }
        } catch (Exception e) {
            return null;
        }
    }

    // Precedence: selector (operand is a set) > conflict (bases differ) >
    // bt_only (regression) > df_only > agree. A single backtrack value cannot be compared
    // with a set, so branching supersedes other verdicts instead of combining with them.
    String verdict(Site s) {
        if (!s.alts.isEmpty()) return "selector";
        boolean conflict = false, btOnly = false, dfOnly = false, any = false;
        for (int k = 0; k < 3; k++) {
            long b = s.bt[k], d = s.df[k];
            if (b == -1 && d == -1) continue;
            any = true;
            if (b != -1 && d != -1) { if (b != d) conflict = true; }
            else if (b != -1) btOnly = true;
            else dfOnly = true;
        }
        if (conflict) return "conflict";
        if (btOnly) return "bt_only";
        if (dfOnly) return "df_only";
        return any ? "agree" : "none";
    }

    void write(File f, List<Site> sites, long kernel) throws Exception {
        PrintWriter w = new PrintWriter(new FileWriter(f));
        w.println("kernel,wrapper,slot,accessor,callsite,func,bt_r4,bt_r5,bt_r6,"
                + "df_r4,df_r5,df_r6,df_r7,k4,k5,k6,k7,verdict,branch");
        String khex = String.format("%08x", kernel);
        for (Site s : sites) {
            String vd = verdict(s);
            List<long[]> rows = new ArrayList<>();
            rows.add(s.df);
            rows.addAll(s.alts);
            for (int i = 0; i < rows.size(); i++) {
                long[] d = rows.get(i);
                w.println(String.format(
                        "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s",
                        khex, s.wrapper, s.slot, s.accessor, s.at, s.fsrc,
                        hx(s.bt[0]), hx(s.bt[1]), hx(s.bt[2]),
                        hx(d[0]), hx(d[1]), hx(d[2]), hx(d[3]),
                        s.kind[0], s.kind[1], s.kind[2], s.kind[3], vd,
                        s.alts.isEmpty() ? "" : String.valueOf(i)));
            }
        }
        w.close();
    }

    void summary(List<Site> sites, Map<Function, Address> wrappers) {
        int n = sites.size(), btR4 = 0, dfR4 = 0, dfAll = 0, btAll = 0;
        Map<String, Integer> vd = new TreeMap<>(), kd = new TreeMap<>(), fs = new TreeMap<>();
        for (Site s : sites) {
            if (s.bt[0] != -1) btR4++;
            if (s.df[0] != -1) dfR4++;
            for (int k = 0; k < 3; k++) { if (s.bt[k] != -1) btAll++; if (s.df[k] != -1) dfAll++; }
            vd.merge(verdict(s), 1, Integer::sum);
            kd.merge(s.kind[0], 1, Integer::sum);
            fs.merge(s.fsrc, 1, Integer::sum);
        }
        int selSites = 0, selRows = 0;
        for (Site s : sites) if (!s.alts.isEmpty()) { selSites++; selRows += s.alts.size() + 1; }
        println("VQ_RES sites=" + n + " bt_r4=" + btR4 + " df_r4=" + dfR4
                + " resolution bt=" + pct(btR4, n) + "% df=" + pct(dfR4, n) + "%");
        println("VQ_RES operand branching: " + selSites + " sites -> " + selRows + " rows");
        println("VQ_RES r4/r5/r6 operands: bt=" + btAll + " df=" + dfAll + " of " + (n * 3));
        println("VQ_RES verdict: " + vd);
        println("VQ_RES df_r4 source: " + kd);
        println("VQ_RES site function: " + fs);
        // Wrappers with no call references to their entries.
        for (Map.Entry<Function, Address> e : wrappers.entrySet()) {
            boolean any = false;
            for (Site s : sites) if (s.wrapper.equals(e.getKey().getEntryPoint())) { any = true; break; }
            if (!any) println("VQ_RES wrapper without call sites: " + e.getKey().getEntryPoint());
        }
    }

    int pct(int a, int b) { return b == 0 ? 0 : (a * 100) / b; }

    String hx(long v) { return v == -1 ? "" : String.format("%08x", v); }
}
