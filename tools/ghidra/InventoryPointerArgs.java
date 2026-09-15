// Inventory pointer arguments and parameter-relative stores.
//
// Usage (headless postScript):
//   InventoryPointerArgs.java <out_dir>
//
// Writes:
//   pointer_args.csv  caller,call_addr,callee,reg,value
//       call sites where r0..r7 was loaded with a pool constant or an
//       immediate within the 8 preceding instructions and not redefined before
//       the call (delay slot included); values outside 0xffff0000..0xffffbfff
//       are lengths, immediates, or non-RAM pointers.
//   param_stores.csv  func_addr,ins_addr,mnemonic,base_reg,disp,width,access
//       memory operands based on r0..r7 that are still the incoming register
//       value (no earlier instruction of the function writes that register in
//       address order).  disp is the raw operand scalar (scaled by width for
//       @(disp,Rn) forms by the SH-2 encoding); "x" marks @(r0,Rn) forms.
//
// Both files are an over-approximation: the register-liveness check is
// address-ordered, not flow-sensitive.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.FlowType;
import ghidra.program.model.symbol.Reference;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class InventoryPointerArgs extends GhidraScript {

    // r4..r7 carry the C arguments; r0..r3 carry the arguments of the
    // register-convention library helpers (block copy and fill).
    private static boolean isParamReg(String n) {
        return n.length() == 2 && n.charAt(0) == 'r' && n.charAt(1) >= '0' && n.charAt(1) <= '7';
    }

    private static Set<String> writtenRegs(Instruction ins) {
        Set<String> out = new HashSet<>();
        for (Object o : ins.getResultObjects()) {
            if (o instanceof Register) {
                out.add(((Register) o).getName().toLowerCase());
            }
        }
        return out;
    }

    private Long poolValue(Instruction ins) {
        Memory mem = currentProgram.getMemory();
        for (Reference r : ins.getReferencesFrom()) {
            if (r.isMemoryReference() && !r.getReferenceType().isFlow()) {
                try {
                    if (ins.getMnemonicString().equals("mov.l")) {
                        return mem.getInt(r.getToAddress()) & 0xFFFFFFFFL;
                    }
                    if (ins.getMnemonicString().equals("mov.w")) {
                        return (long) mem.getShort(r.getToAddress()) & 0xFFFFFFFFL;
                    }
                } catch (Exception e) {
                    return null;
                }
            }
        }
        return null;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            printerr("usage: InventoryPointerArgs.java <out_dir>");
            return;
        }
        File outDir = new File(args[0]);
        outDir.mkdirs();
        Listing listing = currentProgram.getListing();

        List<String> argRows = new ArrayList<>();
        List<String> storeRows = new ArrayList<>();
        int nArgs = 0;
        int nStores = 0;

        for (Function f : listing.getFunctions(true)) {
            Set<String> live = new HashSet<>();
            for (int k = 0; k <= 7; k++) {
                live.add("r" + k);
            }
            List<Instruction> body = new ArrayList<>();
            InstructionIterator it = listing.getInstructions(f.getBody(), true);
            while (it.hasNext()) {
                body.add(it.next());
            }
            for (int idx = 0; idx < body.size(); idx++) {
                Instruction ins = body.get(idx);
                String mn = ins.getMnemonicString();
                String mnl = mn.startsWith("_") ? mn.substring(1) : mn;
                // parameter-relative memory operands.  The SH sleigh splits a
                // memory operand into separate fields: a store is
                // [data, disp, base] or [data, base], a load [disp, base, data]
                // or [base, data]; the indexed forms are [data, r0, base] and
                // [r0, base, data].
                if (mnl.startsWith("mov") && ins.getNumOperands() >= 2 && !mnl.equals("movt") && !mnl.equals("mova")) {
                    int n = ins.getNumOperands();
                    boolean pcOrGbr = false;
                    Long scalar = null;
                    int scalarIdx = -1;
                    List<Register> regs = new ArrayList<>();
                    List<Integer> regIdx = new ArrayList<>();
                    for (int op = 0; op < n; op++) {
                        for (Object o : ins.getOpObjects(op)) {
                            if (o instanceof Register) {
                                String rn = ((Register) o).getName().toLowerCase();
                                if (rn.equals("gbr") || rn.equals("pc")) {
                                    pcOrGbr = true;
                                }
                                regs.add((Register) o);
                                regIdx.add(op);
                            } else if (o instanceof Scalar) {
                                scalar = ((Scalar) o).getUnsignedValue();
                                scalarIdx = op;
                            }
                        }
                    }
                    Set<String> results = writtenRegs(ins);
                    String baseName = null;
                    String access = null;
                    String dispText = null;
                    if (!pcOrGbr && n == 3 && scalar != null && regs.size() == 2) {
                        if (scalarIdx == 1) {
                            baseName = regs.get(1).getName().toLowerCase();
                            access = "W";
                        } else if (scalarIdx == 0) {
                            baseName = regs.get(0).getName().toLowerCase();
                            access = "R";
                        }
                        dispText = Long.toHexString(scalar);
                    } else if (!pcOrGbr && n == 3 && scalar == null && regs.size() == 3) {
                        // indexed @(r0,Rn): the base is the non-r0 register of the pair
                        String a = regs.get(0).getName().toLowerCase();
                        String b = regs.get(1).getName().toLowerCase();
                        String c = regs.get(2).getName().toLowerCase();
                        if (b.equals("r0")) {
                            baseName = c;
                            access = "W";
                        } else if (a.equals("r0")) {
                            baseName = b;
                            access = "R";
                        }
                        dispText = "x";
                    } else if (!pcOrGbr && n == 2 && scalar == null && regs.size() == 2) {
                        String a = regs.get(0).getName().toLowerCase();
                        String b = regs.get(1).getName().toLowerCase();
                        if (results.contains(b) && !results.contains(a)) {
                            baseName = a;
                            access = "R";
                        } else if (results.contains(b) && results.contains(a)) {
                            baseName = a;          // post-increment load @Rm+
                            access = "R";
                        } else if (!results.contains(b)) {
                            baseName = b;
                            access = "W";
                        } else {
                            baseName = b;          // pre-decrement store @-Rn
                            access = "W";
                        }
                        dispText = "0";
                    }
                    if (baseName != null && isParamReg(baseName) && live.contains(baseName)) {
                        int width = mnl.endsWith(".w") ? 2 : (mnl.endsWith(".l") ? 4 : 1);
                        storeRows.add(f.getEntryPoint() + "," + ins.getAddress() + "," + mn + "," + baseName + ","
                            + dispText + "," + width + "," + access);
                        nStores++;
                    }
                }
                // pointer arguments at call sites
                FlowType ft = ins.getFlowType();
                if (ft.isCall()) {
                    Address callee = null;
                    for (Reference r : ins.getReferencesFrom()) {
                        if (r.getReferenceType().isCall()) {
                            callee = r.getToAddress();
                        }
                    }
                    Map<String, Long> argv = new HashMap<>();
                    Set<String> killed = new HashSet<>();
                    // delay slot may still load the register
                    int end = Math.min(idx + 1, body.size() - 1);
                    for (int k = end; k >= Math.max(0, idx - 8); k--) {
                        Instruction p = body.get(k);
                        if (k == idx) {
                            continue;
                        }
                        Set<String> w = writtenRegs(p);
                        for (String reg : w) {
                            if (!isParamReg(reg) || argv.containsKey(reg) || killed.contains(reg)) {
                                continue;
                            }
                            Long v = poolValue(p);
                            String pm = p.getMnemonicString();
                            if (v != null && (pm.equals("mov.l") || pm.equals("mov.w")) && v >= 0xFFFF0000L && v <= 0xFFFFBFFFL) {
                                argv.put(reg, v);
                            } else if (pm.equals("mov") && p.getNumOperands() == 2 && p.getOpObjects(0).length == 1
                                    && p.getOpObjects(0)[0] instanceof Scalar) {
                                long imm = (long) (byte) ((Scalar) p.getOpObjects(0)[0]).getUnsignedValue();
                                argv.put(reg, imm & 0xFFFFFFFFL);
                            } else if (v != null && (pm.equals("mov.l") || pm.equals("mov.w"))) {
                                argv.put(reg, v);
                            } else {
                                killed.add(reg);
                            }
                        }
                    }
                    for (Map.Entry<String, Long> e : argv.entrySet()) {
                        argRows.add(f.getEntryPoint() + "," + ins.getAddress() + "," + (callee == null ? "" : callee.toString())
                            + "," + e.getKey() + "," + String.format("%08x", e.getValue()));
                        nArgs++;
                    }
                }
                live.removeAll(writtenRegs(ins));
            }
        }
        try (PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "pointer_args.csv")))) {
            w.println("caller,call_addr,callee,reg,value");
            for (String r : argRows) {
                w.println(r);
            }
        }
        try (PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "param_stores.csv")))) {
            w.println("func_addr,ins_addr,mnemonic,base_reg,disp,width,access");
            for (String r : storeRows) {
                w.println(r);
            }
        }
        println("VQ_PTR args=" + nArgs + " param_accesses=" + nStores + " dir=" + outDir);
    }
}
