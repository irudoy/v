// TraceRamAccesses.java - resolve decompiler p-code memory accesses whose
// effective addresses fall in a selected RAM range.
//
// ExportXrefs records direct references and literal-pool address loads. A store
// through a base pointer can therefore be absent even when the function has a
// literal reference to the containing RAM block. This script follows the
// decompiler's SSA definition chain through pointer arithmetic and reports the
// concrete LOAD/STORE address when it can be reduced to a constant.
//
// Usage (headless):
//   -postScript TraceRamAccesses.java <out_dir> <lo_hex> <hi_hex> [<func_addr>...]
//
// With function addresses, only those functions are inspected. Without them,
// every defined function is inspected. Output:
//   ram_accesses.csv (func_addr,ins_addr,access,width,address)
//@category VQ
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.PcodeOpAST;
import ghidra.program.model.pcode.Varnode;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

public class TraceRamAccesses extends GhidraScript {

    static final long ROM_HI = 0x180000L;
    static final int SLICE_DEPTH = 32;

    Memory mem;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 3) {
            println("VQ_RAM need: <out_dir> <lo_hex> <hi_hex> [<func_addr>...]");
            return;
        }

        File outDir = new File(args[0]);
        outDir.mkdirs();
        long lo = Long.parseUnsignedLong(args[1], 16);
        long hi = Long.parseUnsignedLong(args[2], 16);
        if (Long.compareUnsigned(lo, hi) > 0) {
            throw new IllegalArgumentException("RAM range begins after it ends");
        }

        mem = currentProgram.getMemory();
        FunctionManager fm = currentProgram.getFunctionManager();
        List<Function> functions = new ArrayList<>();
        if (args.length > 3) {
            for (int i = 3; i < args.length; i++) {
                Address ep = currentProgram.getAddressFactory()
                        .getDefaultAddressSpace()
                        .getAddress(Long.parseUnsignedLong(args[i], 16));
                Function f = fm.getFunctionAt(ep);
                if (f == null) {
                    println("VQ_RAM no function at " + args[i]);
                    continue;
                }
                functions.add(f);
            }
        } else {
            for (Function f : fm.getFunctions(true)) {
                functions.add(f);
            }
        }

        TreeSet<String> rows = new TreeSet<>();
        DecompInterface ifc = new DecompInterface();
        DecompileOptions options = new DecompileOptions();
        options.grabFromProgram(currentProgram);
        // Large scheduler functions in the HR firmware can exceed the default
        // native decompiler response buffer even though decompilation itself
        // completes. The higher bound keeps their HighFunction available for
        // data-flow inspection.
        options.setMaxPayloadMBytes(256);
        ifc.setOptions(options);
        ifc.openProgram(currentProgram);
        int completed = 0;
        int failed = 0;
        try {
            for (Function f : functions) {
                DecompileResults result = ifc.decompileFunction(f, 120, monitor);
                HighFunction high = result.getHighFunction();
                if (high == null) {
                    failed++;
                    println("VQ_RAM decompile failed " + f.getEntryPoint()
                            + ": " + result.getErrorMessage());
                    continue;
                }
                completed++;
                Iterator<PcodeOpAST> it = high.getPcodeOps();
                while (it.hasNext()) {
                    PcodeOpAST op = it.next();
                    int opcode = op.getOpcode();
                    if (opcode != PcodeOp.LOAD && opcode != PcodeOp.STORE) {
                        continue;
                    }
                    Long address = eval(op.getInput(1), 0, new HashSet<Varnode>());
                    if (address == null) {
                        continue;
                    }
                    long normalized = address & 0xFFFFFFFFL;
                    if (Long.compareUnsigned(normalized, lo) < 0
                            || Long.compareUnsigned(normalized, hi) > 0) {
                        continue;
                    }
                    int width = opcode == PcodeOp.LOAD
                            ? op.getOutput().getSize()
                            : op.getInput(2).getSize();
                    rows.add(String.format(
                            "%s,%08x,%s,%d,%08x",
                            f.getEntryPoint(),
                            op.getSeqnum().getTarget().getOffset() & 0xFFFFFFFFL,
                            opcode == PcodeOp.LOAD ? "R" : "W",
                            width,
                            normalized));
                }
            }
        } finally {
            ifc.dispose();
        }

        PrintWriter out = new PrintWriter(new FileWriter(
                new File(outDir, "ram_accesses.csv")));
        out.println("func_addr,ins_addr,access,width,address");
        for (String row : rows) {
            out.println(row);
        }
        out.close();
        println("VQ_RAM completed=" + completed + " failed=" + failed
                + " accesses=" + rows.size() + " dir=" + outDir);
    }

    Long eval(Varnode node, int depth, Set<Varnode> active) {
        if (node == null || depth > SLICE_DEPTH || active.contains(node)) {
            return null;
        }
        if (node.isConstant()) {
            return mask(node.getOffset(), node.getSize());
        }
        if (isRomStorage(node)) {
            return readWord(node.getAddress(), node.getSize());
        }
        PcodeOp def = node.getDef();
        if (def == null) {
            return null;
        }
        active.add(node);
        Long value = evalOp(def, depth + 1, active);
        active.remove(node);
        return value == null ? null : mask(value, node.getSize());
    }

    Long evalOp(PcodeOp op, int depth, Set<Varnode> active) {
        Long a;
        Long b;
        Long c;
        switch (op.getOpcode()) {
            case PcodeOp.COPY:
            case PcodeOp.CAST:
            case PcodeOp.INT_ZEXT:
            case PcodeOp.INT_SEXT:
            case PcodeOp.INDIRECT:
                return eval(op.getInput(0), depth, active);
            case PcodeOp.SUBPIECE:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                return a == null || b == null ? null : a >>> (b * 8);
            case PcodeOp.INT_ADD:
            case PcodeOp.PTRSUB:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                return a == null || b == null ? null : a + b;
            case PcodeOp.INT_SUB:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                return a == null || b == null ? null : a - b;
            case PcodeOp.INT_MULT:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                return a == null || b == null ? null : a * b;
            case PcodeOp.INT_LEFT:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                return a == null || b == null ? null : a << b;
            case PcodeOp.INT_RIGHT:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                return a == null || b == null ? null : a >>> b;
            case PcodeOp.INT_AND:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                return a == null || b == null ? null : a & b;
            case PcodeOp.INT_OR:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                return a == null || b == null ? null : a | b;
            case PcodeOp.PTRADD:
                a = eval(op.getInput(0), depth, active);
                b = eval(op.getInput(1), depth, active);
                c = eval(op.getInput(2), depth, active);
                return a == null || b == null || c == null ? null : a + b * c;
            case PcodeOp.LOAD:
                a = eval(op.getInput(1), depth, active);
                if (a == null || op.getOutput() == null) {
                    return null;
                }
                return readWord(toAddress(a), op.getOutput().getSize());
            case PcodeOp.MULTIEQUAL:
                Long common = null;
                for (int i = 0; i < op.getNumInputs(); i++) {
                    Long value = eval(op.getInput(i), depth, active);
                    if (value == null) {
                        return null;
                    }
                    if (common == null) {
                        common = value;
                    } else if (!common.equals(value)) {
                        return null;
                    }
                }
                return common;
            default:
                return null;
        }
    }

    boolean isRomStorage(Varnode node) {
        return node != null
                && !node.isConstant()
                && !node.isRegister()
                && !node.isUnique()
                && "ram".equals(node.getAddress().getAddressSpace().getName())
                && Long.compareUnsigned(
                        node.getAddress().getOffset() & 0xFFFFFFFFL, ROM_HI) < 0;
    }

    Long readWord(Address address, int size) {
        if (address == null
                || Long.compareUnsigned(
                        address.getOffset() & 0xFFFFFFFFL, ROM_HI) >= 0) {
            return null;
        }
        try {
            switch (size) {
                case 1:
                    return (long) (mem.getByte(address) & 0xFF);
                case 2:
                    return (long) (mem.getShort(address) & 0xFFFF);
                case 4:
                    return mem.getInt(address) & 0xFFFFFFFFL;
                default:
                    return null;
            }
        } catch (Exception error) {
            return null;
        }
    }

    Address toAddress(long value) {
        return currentProgram.getAddressFactory()
                .getDefaultAddressSpace()
                .getAddress(value & 0xFFFFFFFFL);
    }

    long mask(long value, int size) {
        if (size >= 8) {
            return value;
        }
        long bits = size * 8L;
        return value & ((1L << bits) - 1);
    }
}
