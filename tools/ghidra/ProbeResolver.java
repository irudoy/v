// ProbeResolver.java - headless-спайк условия А резолвера операндов.
// Меряет, снимает ли декомпилятор константные аргументы (r4=table, r5/r6=оси)
// на косвенном вызове интерполятора внутри ignition-аксессора FUN_00082c8a
// (JK03A / as7058): сайт 0x832a0, jsr @r2 при r2=0x26320.
//   baseline      - как программа проанализирована сейчас;
//   intervention  - после форсирования сигнатуры 0x26320 (custom storage r4..r7)
//                   и (если нужно) добавления computed-call ссылки на сайте.
// Прогон под -readOnly: мутации живут в памяти, в проект не пишутся.
//@category VQ
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.listing.Variable;
import ghidra.program.model.lang.Register;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.Undefined1DataType;
import ghidra.program.model.data.Undefined2DataType;
import ghidra.program.model.pcode.HighFunction;
import ghidra.program.model.pcode.HighVariable;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.pcode.PcodeOpAST;
import ghidra.program.model.pcode.Varnode;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

public class ProbeResolver extends GhidraScript {

    static final long SITE    = 0x832a0L;  // блок загрузки операндов (mov.l ...,r4)
    static final long MEASURE = 0x832b6L;  // jsr @r2 карты 0xB81A (замер операндов)
    static final long INTERP  = 0x26320L;  // интерполятор 16x16
    // ожидаемые операнды сайта: r4=table, r5=axisX, r6=axisY
    static final long[] EXPECT = { 0xb81aL, 0x11b6bL, 0x11b8bL };
    static final String[] EXPECT_NAME = { "r4=table 0xb81a", "r5=axisX 0x11b6b", "r6=axisY 0x11b8b" };

    @Override
    public void run() throws Exception {
        Function accessor = getFunctionContaining(toAddr(SITE));
        Function interp   = getFunctionAt(toAddr(INTERP));
        println("=== ProbeResolver: условие А (снятие аргументов на CALLIND) ===");
        println("program : " + currentProgram.getName());
        println("accessor: " + (accessor == null ? "NULL" : accessor.getName() + " @" + accessor.getEntryPoint()));
        println("interp  : " + (interp == null ? "NULL" : interp.getName() + " @" + interp.getEntryPoint()));
        if (accessor == null) { println("!! нет функции на сайте, стоп"); return; }

        reportCallSites(accessor);
        reportSig("interp сигнатура BEFORE", interp);

        println("\n--- BASELINE: call-опкоды функции (сигнатура interp не форсирована) ---");
        int baseHits = probeCalls(accessor);
        println("BASELINE итог: снято " + baseHits + "/" + EXPECT.length + " операндов на вызове interp");

        println("\n--- INTERVENTION: форс custom storage r4=table*,r5=axisX*,r6=axisY*,r7=curX ---");
        int tx = currentProgram.startTransaction("probe-force-sig");
        boolean ok = false;
        try {
            forceSig(interp);
            ok = true;
        } catch (Exception e) {
            println("!! мутация не удалась (readOnly блокирует запись?): " + e);
        } finally {
            currentProgram.endTransaction(tx, ok);
        }
        reportSig("interp сигнатура AFTER", interp);

        println("\n--- AFTER: call-опкоды функции ---");
        int afterHits = probeCalls(accessor);
        println("AFTER итог: снято " + afterHits + "/" + EXPECT.length + " операндов на вызове interp");

        println("\n=== ВЕРДИКТ ===");
        println("baseline  : " + baseHits + "/" + EXPECT.length);
        println("после сигн: " + afterHits + "/" + EXPECT.length);
        if (afterHits == EXPECT.length) {
            println("=> условие А выполнимо: декомпилятор снимает r4/r5/r6 при заданной сигнатуре CALLIND");
        } else if (afterHits > baseHits) {
            println("=> частично: сигнатура помогает, но снято не всё - смотреть представление операндов выше");
        } else {
            println("=> условие А НЕ подтверждено на этом пути - резолвер операндов нужно строить иначе");
        }
    }

    // Скан тела функции: все инструкции с call-flow, их адрес, мнемоника и цель-ссылка.
    void reportCallSites(Function f) {
        println("\ncall-сайты в " + f.getName() + ":");
        Iterator<Instruction> ii = currentProgram.getListing().getInstructions(f.getBody(), true).iterator();
        while (ii.hasNext()) {
            Instruction ins = ii.next();
            if (!ins.getFlowType().isCall()) continue;
            StringBuilder tgt = new StringBuilder();
            for (Reference r : ins.getReferencesFrom()) {
                if (r.getReferenceType().isCall()) tgt.append(" -> ").append(r.getToAddress())
                        .append("(").append(r.getReferenceType()).append(")");
            }
            println("  @" + ins.getAddress() + ": " + ins.toString()
                    + " [" + ins.getFlowType() + "]" + (tgt.length() == 0 ? " -> <цель не разрешена>" : tgt));
        }
    }

    void reportSig(String tag, Function f) {
        if (f == null) { println(tag + ": interp NULL"); return; }
        Parameter[] ps = f.getParameters();
        println(tag + ": custom=" + f.hasCustomVariableStorage() + ", params=" + ps.length + ", conv=" + f.getCallingConventionName());
        for (Parameter p : ps) {
            println("    " + p.getName() + " : " + p.getDataType().getName() + " @ " + p.getVariableStorage());
        }
    }

    int probeCalls(Function f) {
        DecompInterface ifc = new DecompInterface();
        int hits = 0;
        try {
            ifc.openProgram(currentProgram);
            DecompileResults r = ifc.decompileFunction(f, 60, monitor);
            HighFunction hf = r.getHighFunction();
            if (hf == null) { println("  декомпиляция не удалась: " + r.getErrorMessage()); return 0; }
            Iterator<PcodeOpAST> it = hf.getPcodeOps();
            boolean sawInterp = false;
            while (it.hasNext()) {
                PcodeOpAST op = it.next();
                int oc = op.getOpcode();
                if (oc != PcodeOp.CALL && oc != PcodeOp.CALLIND) continue;
                Varnode[] in = op.getInputs();
                boolean isInterp = targetIsInterp(op);
                if (!isInterp) continue;
                sawInterp = true;
                println("  опкод: " + (oc == PcodeOp.CALL ? "CALL" : "CALLIND") + " @" + op.getSeqnum().getTarget()
                        + "  inputs=" + in.length + " (in[0]=цель)  <== interp 0x26320");
                for (int i = 0; i < in.length; i++) {
                    println("    in[" + i + "] = " + describe(in[i]));
                }
                if (op.getSeqnum().getTarget().getOffset() != MEASURE) continue;
                for (int k = 0; k < EXPECT.length; k++) {
                    boolean hit = false;
                    for (int i = 1; i < in.length; i++) if (isVal(in[i], EXPECT[k])) hit = true;
                    if (hit) hits++;
                    println("    [" + EXPECT_NAME[k] + "]: " + (hit ? "СНЯТ (разыменованием пула)" : "нет"));
                }
            }
            if (!sawInterp) println("  !! вызов interp 0x26320 среди call-опкодов не найден");
            String c = r.getDecompiledFunction() != null ? r.getDecompiledFunction().getC() : null;
            if (c != null) {
                println("  -- C (строки вокруг вызова interp) --");
                for (String line : c.split("\n")) {
                    if (line.contains("83368") || line.contains("8336c") || line.contains("83370")
                            || line.contains("83378") || line.contains("8337c")
                            || line.contains("26320") || line.contains("PTR_DAT_000833")) {
                        println("    " + line.trim());
                    }
                }
            }
        } finally {
            ifc.dispose();
        }
        return hits;
    }

    // Целит ли call-опкод в интерполятор: по константе в in[0] либо по call-ссылке на его адресе.
    boolean targetIsInterp(PcodeOpAST op) {
        Varnode t = op.getInput(0);
        if (t != null && t.getOffset() == INTERP && (t.isConstant() || t.isAddress())) return true;
        Address at = op.getSeqnum().getTarget();
        for (Reference r : currentProgram.getReferenceManager().getReferencesFrom(at)) {
            if (r.getReferenceType().isCall() && r.getToAddress().getOffset() == INTERP) return true;
        }
        return false;
    }

    String describe(Varnode vn) {
        if (vn == null) return "null";
        if (vn.isConstant()) return "const 0x" + Long.toHexString(vn.getOffset());
        if (vn.isRegister()) {
            Register rg = currentProgram.getRegister(vn.getAddress(), vn.getSize());
            return "reg " + (rg != null ? rg.getName() : vn.getAddress().toString());
        }
        HighVariable hv = vn.getHigh();
        String nm = (hv != null && hv.getName() != null) ? hv.getName() : "?";
        String base = vn.getAddress().getAddressSpace().getName() + ":0x" + Long.toHexString(vn.getOffset()) + " (" + nm + ")";
        if (isRam(vn)) {
            Long d = derefRomWord(vn.getAddress());
            if (d != null) base += " => *=0x" + Long.toHexString(d);
        }
        return base;
    }

    // Резолвер: аргумент-указатель = адрес слота пула; база таблицы/оси - его содержимое.
    boolean isVal(Varnode vn, long v) {
        if (vn == null) return false;
        if (vn.isConstant() && vn.getOffset() == v) return true;         // прямая константа
        if (vn.isRegister() || vn.isUnique()) return false;
        if (vn.getOffset() == v) return true;                            // адрес совпал напрямую
        if (isRam(vn)) {                                                 // разыменование pool-слота
            Long d = derefRomWord(vn.getAddress());
            if (d != null && d.longValue() == v) return true;
        }
        return false;
    }

    boolean isRam(Varnode vn) {
        return vn != null && !vn.isConstant() && !vn.isRegister() && !vn.isUnique()
                && "ram".equals(vn.getAddress().getAddressSpace().getName());
    }

    Long derefRomWord(Address a) {
        try {
            byte[] b = new byte[4];
            currentProgram.getMemory().getBytes(a, b);
            return ((b[0] & 0xffL) << 24) | ((b[1] & 0xffL) << 16) | ((b[2] & 0xffL) << 8) | (b[3] & 0xffL);
        } catch (Exception e) {
            return null;
        }
    }

    void forceSig(Function f) throws Exception {
        if (f == null) { println("  interp NULL, форс невозможен"); return; }
        f.setCustomVariableStorage(true);
        Register r4 = currentProgram.getRegister("r4");
        Register r5 = currentProgram.getRegister("r5");
        Register r6 = currentProgram.getRegister("r6");
        Register r7 = currentProgram.getRegister("r7");
        DataType pv = new PointerDataType(new Undefined1DataType());
        List<Variable> params = new ArrayList<>();
        params.add(new ParameterImpl("table", pv, r4, currentProgram));
        params.add(new ParameterImpl("axisX", pv, r5, currentProgram));
        params.add(new ParameterImpl("axisY", pv, r6, currentProgram));
        params.add(new ParameterImpl("curX", new Undefined2DataType(), r7, currentProgram));
        f.updateFunction(null, null, params,
                Function.FunctionUpdateType.CUSTOM_STORAGE, true, SourceType.USER_DEFINED);
        println("  сигнатура interp форсирована: 4 параметра в r4..r7");
    }

}
