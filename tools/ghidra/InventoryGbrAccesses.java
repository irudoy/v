// Inventory every instruction that addresses memory through GBR.
//
// Usage (headless postScript):
//   InventoryGbrAccesses.java <out_dir>
//
// Writes:
//   gbr_accesses.csv  func_addr,ins_addr,mnemonic,operands,disp,access,width,gbr_source,gbr_value,eff_addr
//                     (disp is the raw instruction field; eff_addr = gbr_value + disp * width;
//                      access R/W/RW, suffix x for the @(r0,gbr) indexed forms)
//   gbr_loads.csv     func_addr,ins_addr,mnemonic,operands,gbr_value
//
// gbr_source is "own" when a constant `ldc Rn,gbr` precedes the access in the
// same function (nearest preceding site in address order), "stack" when the
// nearest site is `ldc.l @Rn+,gbr`, and "inherited" when the function has no
// GBR load before the access.  gbr_value / eff_addr are filled for "own" only;
// inherited sites are resolved by the caller of this script from gbr_loads.csv
// and the call graph.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;

import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;
import java.util.TreeMap;

public class InventoryGbrAccesses extends GhidraScript {

    private static boolean mentionsGbr(Instruction ins, int op) {
        for (Object o : ins.getOpObjects(op)) {
            if (o instanceof Register && ((Register) o).getName().equalsIgnoreCase("gbr")) {
                return true;
            }
        }
        return false;
    }

    private static Register regOperand(Instruction ins, int op) {
        for (Object o : ins.getOpObjects(op)) {
            if (o instanceof Register) {
                return (Register) o;
            }
        }
        return null;
    }

    private static Long scalarOperand(Instruction ins, int op) {
        for (Object o : ins.getOpObjects(op)) {
            if (o instanceof Scalar) {
                return ((Scalar) o).getUnsignedValue();
            }
        }
        return null;
    }

    // Value moved into Rn by the nearest preceding pc-relative pool load
    // (`mov.l @(disp,pc),Rn` -> 32-bit word, `mov.w @(disp,pc),Rn` -> sign
    // extended 16-bit word) or immediate `mov #imm,Rn` in the same function.
    private Long poolValueFor(Function f, Instruction ldc, Register rn) {
        Memory mem = currentProgram.getMemory();
        Instruction cur = ldc.getPrevious();
        int steps = 0;
        while (cur != null && steps < 24 && f.getBody().contains(cur.getAddress())) {
            String mn = cur.getMnemonicString();
            if ((mn.equals("mov.l") || mn.equals("mov.w") || mn.equals("mov")) && cur.getNumOperands() == 2) {
                Register dst = regOperand(cur, 1);
                if (dst != null && dst.getName().equalsIgnoreCase(rn.getName())) {
                    if (mn.equals("mov")) {
                        Long imm = scalarOperand(cur, 0);
                        return imm == null ? null : (long) (byte) imm.longValue() & 0xFFFFFFFFL;
                    }
                    for (Reference r : cur.getReferencesFrom()) {
                        if (r.isMemoryReference()) {
                            try {
                                if (mn.equals("mov.l")) {
                                    return mem.getInt(r.getToAddress()) & 0xFFFFFFFFL;
                                }
                                return (long) mem.getShort(r.getToAddress()) & 0xFFFFFFFFL;
                            } catch (Exception e) {
                                return null;
                            }
                        }
                    }
                    return null;
                }
            }
            cur = cur.getPrevious();
            steps++;
        }
        return null;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1) {
            printerr("usage: InventoryGbrAccesses.java <out_dir>");
            return;
        }
        File outDir = new File(args[0]);
        outDir.mkdirs();
        Listing listing = currentProgram.getListing();

        // Pass 1: GBR load sites per function (address ordered).
        TreeMap<Long, String[]> loads = new TreeMap<>();
        InstructionIterator it = listing.getInstructions(true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            String mn = ins.getMnemonicString();
            if (!(mn.equals("ldc") || mn.equals("ldc.l"))) {
                continue;
            }
            if (ins.getNumOperands() < 2 || !mentionsGbr(ins, 1)) {
                continue;
            }
            Function f = listing.getFunctionContaining(ins.getAddress());
            String fa = f == null ? "" : f.getEntryPoint().toString();
            String val = "";
            String kind = mn.equals("ldc") ? "own" : "stack";
            if (mn.equals("ldc") && f != null) {
                Register rn = regOperand(ins, 0);
                Long v = rn == null ? null : poolValueFor(f, ins, rn);
                if (v != null) {
                    val = String.format("%08x", v);
                }
            }
            loads.put(ins.getAddress().getOffset(), new String[] {fa, ins.getAddress().toString(), mn,
                ins.getDefaultOperandRepresentation(0) + ";" + ins.getDefaultOperandRepresentation(1), kind, val});
        }

        List<String> accRows = new ArrayList<>();
        it = listing.getInstructions(true);
        int n = 0;
        while (it.hasNext()) {
            Instruction ins = it.next();
            String mn = ins.getMnemonicString();
            if (mn.equals("ldc") || mn.equals("ldc.l") || mn.equals("stc") || mn.equals("stc.l")) {
                continue;
            }
            int memOp = -1;
            for (int i = 0; i < ins.getNumOperands(); i++) {
                if (mentionsGbr(ins, i)) {
                    memOp = i;
                }
            }
            if (memOp < 0) {
                continue;
            }
            Function f = listing.getFunctionContaining(ins.getAddress());
            String fa = f == null ? "" : f.getEntryPoint().toString();
            Long disp = null;
            for (int i = 0; i < ins.getNumOperands(); i++) {
                Long sc = scalarOperand(ins, i);
                if (sc != null) {
                    disp = sc;
                }
            }
            boolean indexed = false;
            for (int i = 0; i < ins.getNumOperands(); i++) {
                Register rr = regOperand(ins, i);
                if (rr != null && rr.getName().equalsIgnoreCase("r0") && mentionsGbr(ins, i)) {
                    indexed = true;
                }
            }
            String mnl = mn.startsWith("_") ? mn.substring(1) : mn;
            int width = mnl.endsWith(".w") ? 2 : (mnl.endsWith(".l") ? 4 : 1);
            String access;
            if (mnl.startsWith("mov")) {
                Register first = regOperand(ins, 0);
                access = (first != null && first.getName().equalsIgnoreCase("r0") && !mentionsGbr(ins, 0)) ? "W" : "R";
            } else if (mnl.equals("tst.b")) {
                access = "R";
            } else {
                access = "RW";
            }
            if (indexed) {
                access = access + "x";
                disp = null;
            }
            String source = "inherited";
            String val = "";
            String eff = "";
            if (f != null) {
                Long best = null;
                for (Long k : loads.keySet()) {
                    if (k > ins.getAddress().getOffset()) {
                        break;
                    }
                    if (f.getBody().contains(currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(k))) {
                        best = k;
                    }
                }
                if (best != null) {
                    String[] l = loads.get(best);
                    source = l[4];
                    val = l[5];
                    if (source.equals("own") && !val.isEmpty() && disp != null) {
                        long ea = (Long.parseLong(val, 16) + disp * width) & 0xFFFFFFFFL;
                        eff = String.format("%08x", ea);
                    }
                }
            }
            StringBuilder ops = new StringBuilder();
            for (int i = 0; i < ins.getNumOperands(); i++) {
                if (i > 0) {
                    ops.append(";");
                }
                ops.append(ins.getDefaultOperandRepresentation(i));
            }
            accRows.add(fa + "," + ins.getAddress() + "," + mn + "," + ops + "," + (disp == null ? "" : Long.toHexString(disp))
                + "," + access + "," + width + "," + source + "," + val + "," + eff);
            n++;
        }

        try (PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "gbr_loads.csv")))) {
            w.println("func_addr,ins_addr,mnemonic,operands,kind,gbr_value");
            for (String[] l : loads.values()) {
                w.println(l[0] + "," + l[1] + "," + l[2] + "," + l[3] + "," + l[4] + "," + l[5]);
            }
        }
        try (PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "gbr_accesses.csv")))) {
            w.println("func_addr,ins_addr,mnemonic,operands,disp,access,width,gbr_source,gbr_value,eff_addr");
            for (String r : accRows) {
                w.println(r);
            }
        }
        println("VQ_GBR loads=" + loads.size() + " accesses=" + n + " dir=" + outDir);
    }
}
