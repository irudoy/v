// ScanFlags.java - detect flags from an identified map or guard function.
// The current control-trace contract is in tools/map-analysis-pipeline.md.
//
// MECHANICS. HR calibration flags use gbr addressing. The sequence is "load - test bit -
// branch":
//   mov.b @(0x93,gbr),r0   ; -> ffff4217     load flag byte
//   tst   0x1,r0                             test bit (immediate mask)
//   bt/bf <target>                           branch
// Flags are written similarly: or.b 0x20,@(r0,gbr) sets a bit, while
// and.b 0xdf,@(r0,gbr) clears it.
//
// Obtain the flag address from a Ghidra reference instead of adding a base and displacement.
// This is essential because THE GBR BASE IS NOT GLOBAL. The firmware resets it: 0x68cb8
// contains ldc r0,gbr and ldc.l @r15+,gbr, so gbr addresses another structure there and the
// same @(disp,gbr) resolves to different addresses in different functions. Computing the
// address locally would yield plausible addresses for the wrong cells, an error
// indistinguishable from fact.
//
// LOCAL, NOT EXHAUSTIVE. The script scans specified functions, namely accessors for
// identified maps and guard functions found by ScanImmoAnchors from DTC anchors, rather
// than the entire firmware. ROM contains thousands of bit tests, so a global scan produces
// noise instead of findings. The primary path starts from a map: identify a flag by WHAT it
// branches, not merely because it is a bit.
//
// Assign a role from branch contents only when one function makes them visible:
//   selector  - branches load different bases into r4 before the same call
//               (both receive :SELECTS);
//   gate      - one branch contains a call and the other does not (conditional skip, :GATES);
//   threshold - a path contains cmp with a pool constant pointing into ROM.
// A branch whose alternatives the script cannot distinguish receives role=unknown. This
// requests a trace rather than asserting that no flag exists. The role is a proposal; a trace
// establishes a :Flag node.
//
// BOUNDARY: this detects gbr flags, not every kind of flag. Measured on JK03A:
//   - accessor 0x82c8a (14 maps): 62 findings, including selector gbr+0x93 bit0, which
//     branches r4 between 0xb61a and 0xb71a. A prior trace established this annotation;
//     the script reproduces it independently and is validated against it;
//   - 25 accessors with an unresolved base (kind=sp, 42 sites): ZERO findings despite
//     containing gbr accesses and tst instructions. Their base is not selected by a bit:
//     0x68cb8 branches on cmp after mov.w @(0x2c,gbr), while the resolver census identifies
//     such sites as register-indexed table arrays (0x64344 has six tables selected by r5;
//     0xbe39a has two selected by r13). A flag does not explain them. Stage 6 resolves these
//     cases by enumerating branches rather than by this script.
// A flag addressed without gbr, such as through a pool pointer to an absolute RAM address,
// is outside this scan.
//
// Headless invocation: -postScript ScanFlags.java <out_dir> <func_addr> [<func_addr>...]
// Output: flags.csv (func,test_at,flag_addr,gbr_disp,mask,bit,branch,taken,role,evidence)
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.block.BasicBlockModel;
import ghidra.program.model.block.CodeBlock;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

public class ScanFlags extends GhidraScript {

    static final long ROM_HI = 0x180000L;
    BasicBlockModel bbm;
    static final int WINDOW = 8;        // instructions from flag load to branch

    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 2) {
            println("VQ_FLAGS need: <out_dir> <func_addr>...");
            return;
        }
        bbm = new BasicBlockModel(currentProgram);
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        PrintWriter w = new PrintWriter(new FileWriter(new File(a[0], "flags.csv")));
        w.println("func,test_at,flag_addr,gbr_disp,mask,bit,branch,taken,role,evidence");

        int rows = 0, funcs = 0;
        for (int i = 1; i < a.length; i++) {
            Address ep = currentProgram.getAddressFactory().getAddress(a[i]);
            if (ep == null) { println("VQ_FLAGS bad address " + a[i]); continue; }
            Function f = fm.getFunctionAt(ep);
            if (f == null) { println("VQ_FLAGS no function at " + a[i]); continue; }
            funcs++;
            for (String row : scan(listing, f)) { w.println(row); rows++; }
        }
        w.close();
        println("VQ_FLAGS funcs=" + funcs + " flags=" + rows);
    }

    List<String> scan(Listing listing, Function f) throws Exception {
        List<String> out = new ArrayList<>();
        InstructionIterator it = listing.getInstructions(f.getBody(), true);
        List<Instruction> body = new ArrayList<>();
        while (it.hasNext()) body.add(it.next());

        // Walk backward from the test, not forward from the load: the nearest preceding write
        // to the test register supplies its value. Searching forward from every load pairs
        // both loads with one test when two loads are consecutive, inventing the second hit.
        for (int ti = 0; ti < body.size(); ti++) {
            Instruction tst = body.get(ti);
            String m = tst.getMnemonicString().toLowerCase();
            if (!m.equals("tst") && !m.equals("and")) continue;
            long mask = scalarOf(tst, 0);
            if (mask <= 0) continue;
            String reg = tst.getDefaultOperandRepresentation(tst.getNumOperands() - 1);
            if (reg == null) continue;
            reg = reg.trim();

            Instruction ld = null;
            for (int k = ti - 1; k >= Math.max(0, ti - WINDOW); k--) {
                if (!writesReg(body.get(k), reg)) continue;
                if (isGbrLoad(body.get(k))) ld = body.get(k);
                break;                       // the nearest register write supplies the value
            }
            if (ld == null) continue;
            Address flag = gbrTarget(ld);
            long disp = scalarOf(ld, 0);

            // Branch after the test.
            Instruction br = null;
            for (int k = ti + 1; k < Math.min(ti + 4, body.size()); k++) {
                String bm = body.get(k).getMnemonicString().toLowerCase();
                if (bm.startsWith("bt") || bm.startsWith("bf")) { br = body.get(k); break; }
            }
            if (br == null) continue;

            String[] verdict = classify(br);
            out.add(String.format("%s,%s,%s,%02x,%02x,%s,%s,%s,%s,%s",
                    f.getEntryPoint(), tst.getAddress(),
                    flag == null ? "" : flag.toString(), disp, mask, bitOf(mask),
                    br.getMnemonicString(), target(br), verdict[0], verdict[1]));
        }
        return out;
    }

    // Assign a role from branch contents and obtain branches from Ghidra's CFG rather than
    // guessing from an instruction window. A conditional branch has two successor blocks,
    // which an index-based window cannot distinguish; the code after a branch may be a merge
    // point rather than the alternative branch. Classify only cases visible within one
    // function. Everything else remains unknown for tracing instead of receiving a guess.
    String[] classify(Instruction br) throws Exception {
        // Obtain branches from the instruction itself: getFlows() is the taken branch and
        // getFallThrough() is the untaken branch, including the bt/s or bf/s delay slot.
        // Do not enumerate exits from the containing block: it can have more than two, and
        // they do not identify which alternative belongs to the branch.
        Address taken = brTarget(br), fall = br.getFallThrough();
        if (taken == null || fall == null) {
            return new String[]{"unknown", "unresolved branch"};
        }
        CodeBlock bt = bbm.getFirstCodeBlockContaining(taken, monitor);
        CodeBlock bf = bbm.getFirstCodeBlockContaining(fall, monitor);
        if (bt == null || bf == null) return new String[]{"unknown", "branch block not found"};

        List<String> b0 = basesIn(bf), b1 = basesIn(bt);
        if (!b0.isEmpty() && !b1.isEmpty() && !b0.equals(b1)) {
            return new String[]{"selector", "r4: " + join(b0) + " | " + join(b1)};
        }
        boolean c0 = hasCallIn(bf), c1 = hasCallIn(bt);
        if (c0 != c1) {
            return new String[]{"gate", "call only in block "
                    + (c0 ? bf : bt).getFirstStartAddress()};
        }
        String cmp = cmpConstIn(bf);
        if (cmp == null) cmp = cmpConstIn(bt);
        if (cmp != null) return new String[]{"threshold", "cmp with " + cmp};
        return new String[]{"unknown", "branches not distinguished"};
    }

    // Bases loaded into r4 within a block. mov.l @(disp,pc),r4 has TWO references: one to the
    // pool slot and one to the resolved value. The latter is the base. Distance distinguishes
    // them: the slot is read PC-relative and lies within 0x800, while a calibration base does
    // not. Taking both would compare pool addresses, which always differ between branches,
    // and would classify every branch as a selector.
    List<String> basesIn(CodeBlock b) {
        List<String> out = new ArrayList<>();
        InstructionIterator it = currentProgram.getListing().getInstructions(b, true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            if (!ins.getMnemonicString().toLowerCase().startsWith("mov.l")) continue;
            String dst = ins.getDefaultOperandRepresentation(ins.getNumOperands() - 1);
            if (dst == null || !dst.trim().equals("r4")) continue;
            long ia = ins.getAddress().getOffset() & 0xFFFFFFFFL;
            for (Reference r : ins.getReferencesFrom()) {
                Address t = r.getToAddress();
                if (t == null || !t.isMemoryAddress()) continue;
                long off = t.getOffset() & 0xFFFFFFFFL;
                long dist = off > ia ? off - ia : ia - off;
                if (off < ROM_HI && dist >= 0x800) out.add(String.format("%08x", off));
            }
        }
        return out;
    }

    boolean hasCallIn(CodeBlock b) {
        InstructionIterator it = currentProgram.getListing().getInstructions(b, true);
        while (it.hasNext()) {
            String m = it.next().getMnemonicString().toLowerCase();
            if (m.startsWith("jsr") || m.startsWith("bsr")) return true;
        }
        return false;
    }

    // Threshold: cmp with a constant that points into calibration ROM
    // (0x8FDC is the section 7 example).
    String cmpConstIn(CodeBlock b) {
        InstructionIterator it = currentProgram.getListing().getInstructions(b, true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            if (!ins.getMnemonicString().toLowerCase().startsWith("cmp")) continue;
            for (Reference r : ins.getReferencesFrom()) {
                Address t = r.getToAddress();
                if (t != null && t.isMemoryAddress()
                        && (t.getOffset() & 0xFFFFFFFFL) < ROM_HI) return t.toString();
            }
        }
        return null;
    }

    // mov.b @(disp,gbr),r0 loads a flag byte.
    //
    // Ghidra represents gbr addressing with THREE operands rather than one
    // "@(0x93,gbr)" operand:
    //   load   mov.b @(0x93,gbr),r0  ->  op0=0x93  op1=gbr  op2=r0
    //   store  mov.b r0,@(0x45,gbr)  ->  op0=r0    op1=0x45 op2=gbr
    // A load therefore has gbr among its operands but NOT last. The final operand is the
    // destination, which is memory for a store. Searching operand zero for gbr is useless
    // because it contains the displacement.
    int gbrOperand(Instruction ins) {
        for (int k = 0; k < ins.getNumOperands(); k++) {
            String r = ins.getDefaultOperandRepresentation(k);
            if (r != null && r.trim().equalsIgnoreCase("gbr")) return k;
        }
        return -1;
    }

    // A flag element is not necessarily a byte: 0x68cb8 reads mov.w @(0x2c,gbr),r0.
    // The bit test is identical for any storage width, so width is not a filter here.
    boolean isGbrLoad(Instruction ins) {
        String m = ins.getMnemonicString().toLowerCase();
        if (!m.startsWith("mov.b") && !m.startsWith("mov.w") && !m.startsWith("mov.l")) {
            return false;
        }
        int g = gbrOperand(ins);
        return g > 0 && g < ins.getNumOperands() - 1;
    }

    // Obtain the absolute flag address from a Ghidra reference, which knows the gbr base.
    // Computing it here would create a second source for the same fact.
    Address gbrTarget(Instruction ins) {
        for (Reference r : ins.getReferencesFrom()) {
            Address to = r.getToAddress();
            if (to != null && to.isMemoryAddress()
                    && (to.getOffset() & 0xFFFFFFFFL) >= 0xFFFF0000L) return to;
        }
        return null;
    }

    // An instruction writes a register when the register itself is a result object.
    boolean writesReg(Instruction ins, String reg) {
        for (Object o : ins.getResultObjects()) {
            if (o instanceof Register && ((Register) o).getName().equalsIgnoreCase(reg)) {
                return true;
            }
        }
        return false;
    }

    Address brTarget(Instruction br) {
        Address[] fl = br.getFlows();
        return fl.length > 0 ? fl[0] : null;
    }

    String target(Instruction br) {
        Address t = brTarget(br);
        return t == null ? "" : t.toString();
    }

    long scalarOf(Instruction ins, int op) {
        Object[] objs = ins.getOpObjects(op);
        for (Object o : objs) if (o instanceof Scalar) return ((Scalar) o).getUnsignedValue();
        return -1;
    }

    // A one-bit mask yields a bit number; a multi-bit mask does not represent one bit.
    String bitOf(long mask) {
        if (mask <= 0 || (mask & (mask - 1)) != 0) return "";
        return String.valueOf(Long.numberOfTrailingZeros(mask));
    }

    String join(List<String> xs) {
        StringBuilder sb = new StringBuilder();
        for (String x : xs) { if (sb.length() > 0) sb.append(';'); sb.append(x); }
        return sb.length() == 0 ? "-" : sb.toString();
    }
}
