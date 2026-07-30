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
//   -postScript TraceRamAccesses.java <out_dir> <lo_hex> <hi_hex>
//       [--candidates] [<func_addr>...]
//
// With function addresses, only those functions are inspected. Without them,
// every defined function is inspected. --candidates also records unresolved
// memory addresses that depend on a concrete RAM anchor. Output:
//   ram_accesses.csv
//   ram_calls.csv
//   ram_access_candidates.csv (with --candidates)
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
            println("VQ_RAM need: <out_dir> <lo_hex> <hi_hex>"
                    + " [--candidates] [<func_addr>...]");
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
        boolean candidates = false;
        List<String> functionArgs = new ArrayList<>();
        for (int i = 3; i < args.length; i++) {
            if ("--candidates".equals(args[i])) {
                candidates = true;
            } else {
                functionArgs.add(args[i]);
            }
        }
        if (!functionArgs.isEmpty()) {
            for (String functionArg : functionArgs) {
                Address ep = currentProgram.getAddressFactory()
                        .getDefaultAddressSpace()
                        .getAddress(Long.parseUnsignedLong(functionArg, 16));
                Function f = fm.getFunctionAt(ep);
                if (f == null) {
                    println("VQ_RAM no function at " + functionArg);
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
        TreeSet<String> callRows = new TreeSet<>();
        TreeSet<String> candidateRows = new TreeSet<>();
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
                    if (opcode == PcodeOp.CALL || opcode == PcodeOp.CALLIND) {
                        collectCallArguments(f, op, lo, hi, callRows);
                        continue;
                    }
                    if (opcode != PcodeOp.LOAD && opcode != PcodeOp.STORE) {
                        continue;
                    }
                    Long address = eval(op.getInput(1), 0, new HashSet<Varnode>());
                    if (address == null) {
                        if (candidates) {
                            collectCandidate(f, op, lo, hi, candidateRows);
                        }
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
        writeRows(
                new File(outDir, "ram_calls.csv"),
                "func_addr,ins_addr,callee,arg_index,address",
                callRows);
        if (candidates) {
            writeRows(
                    new File(outDir, "ram_access_candidates.csv"),
                    "func_addr,ins_addr,access,width,ram_anchors,address_expr",
                    candidateRows);
        }
        println("VQ_RAM completed=" + completed + " failed=" + failed
                + " accesses=" + rows.size()
                + " calls=" + callRows.size()
                + " candidates=" + candidateRows.size()
                + " dir=" + outDir);
    }

    void collectCallArguments(
            Function function,
            PcodeOpAST op,
            long lo,
            long hi,
            Set<String> rows) {
        Long callee = eval(op.getInput(0), 0, new HashSet<Varnode>());
        String calleeText = callee == null
                ? csv(op.getInput(0).toString())
                : String.format("%08x", callee & 0xFFFFFFFFL);
        for (int i = 1; i < op.getNumInputs(); i++) {
            Long value = eval(op.getInput(i), 0, new HashSet<Varnode>());
            if (value == null) {
                continue;
            }
            long normalized = value & 0xFFFFFFFFL;
            if (Long.compareUnsigned(normalized, lo) < 0
                    || Long.compareUnsigned(normalized, hi) > 0) {
                continue;
            }
            rows.add(String.format(
                    "%s,%08x,%s,%d,%08x",
                    function.getEntryPoint(),
                    op.getSeqnum().getTarget().getOffset() & 0xFFFFFFFFL,
                    calleeText,
                    i - 1,
                    normalized));
        }
    }

    void collectCandidate(
            Function function,
            PcodeOpAST op,
            long lo,
            long hi,
            Set<String> rows) {
        TreeSet<Long> anchors = new TreeSet<>((a, b) ->
                Long.compareUnsigned(a, b));
        collectRamAnchors(
                op.getInput(1), 0, new HashSet<Varnode>(), lo, hi, anchors);
        if (anchors.isEmpty()) {
            return;
        }
        int opcode = op.getOpcode();
        int width = opcode == PcodeOp.LOAD
                ? op.getOutput().getSize()
                : op.getInput(2).getSize();
        StringBuilder anchorText = new StringBuilder();
        for (Long anchor : anchors) {
            if (anchorText.length() != 0) {
                anchorText.append(';');
            }
            anchorText.append(String.format("%08x", anchor & 0xFFFFFFFFL));
        }
        rows.add(String.format(
                "%s,%08x,%s,%d,%s,%s",
                function.getEntryPoint(),
                op.getSeqnum().getTarget().getOffset() & 0xFFFFFFFFL,
                opcode == PcodeOp.LOAD ? "R" : "W",
                width,
                csv(anchorText.toString()),
                csv(describe(op.getInput(1), 0, new HashSet<Varnode>()))));
    }

    void collectRamAnchors(
            Varnode node,
            int depth,
            Set<Varnode> active,
            long lo,
            long hi,
            Set<Long> anchors) {
        if (node == null || depth > SLICE_DEPTH || active.contains(node)) {
            return;
        }
        Long exact = eval(node, 0, new HashSet<Varnode>());
        if (exact != null && isSelectedAddress(exact, lo, hi)) {
            anchors.add(exact & 0xFFFFFFFFL);
            return;
        }
        if (node.isConstant()) {
            long value = mask(node.getOffset(), node.getSize());
            if (isSelectedAddress(value, lo, hi)) {
                anchors.add(value & 0xFFFFFFFFL);
            }
            return;
        }
        if (isRomStorage(node)) {
            Long value = readWord(node.getAddress(), node.getSize());
            if (value != null && isSelectedAddress(value, lo, hi)) {
                anchors.add(value & 0xFFFFFFFFL);
            }
            return;
        }
        PcodeOp def = node.getDef();
        if (def == null) {
            return;
        }
        active.add(node);
        for (int i = 0; i < def.getNumInputs(); i++) {
            collectRamAnchors(
                    def.getInput(i), depth + 1, active, lo, hi, anchors);
        }
        active.remove(node);
    }

    String describe(Varnode node, int depth, Set<Varnode> active) {
        if (node == null) {
            return "null";
        }
        if (depth > 10 || active.contains(node)) {
            return "...";
        }
        if (node.isConstant()) {
            return String.format("0x%x", mask(node.getOffset(), node.getSize()));
        }
        if (isRomStorage(node)) {
            Long value = readWord(node.getAddress(), node.getSize());
            if (value != null) {
                return String.format(
                        "ROM[%s]=0x%x", node.getAddress(), value);
            }
        }
        PcodeOp def = node.getDef();
        if (def == null) {
            return node.toString();
        }
        active.add(node);
        StringBuilder text = new StringBuilder(def.getMnemonic());
        text.append('(');
        for (int i = 0; i < def.getNumInputs(); i++) {
            if (i != 0) {
                text.append(',');
            }
            text.append(describe(def.getInput(i), depth + 1, active));
        }
        text.append(')');
        active.remove(node);
        return text.toString();
    }

    boolean isSelectedAddress(long value, long lo, long hi) {
        long normalized = value & 0xFFFFFFFFL;
        return Long.compareUnsigned(normalized, lo) >= 0
                && Long.compareUnsigned(normalized, hi) <= 0;
    }

    void writeRows(File file, String header, Set<String> rows) throws Exception {
        PrintWriter out = new PrintWriter(new FileWriter(file));
        out.println(header);
        for (String row : rows) {
            out.println(row);
        }
        out.close();
    }

    String csv(String value) {
        return "\"" + value.replace("\"", "\"\"") + "\"";
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
