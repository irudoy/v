// NatsGate.java -- поиск единого калибровочного master-enable над immo-контуром.
// От заданных immo-точек (registration/lock/evaluator) поднимается вверх по дереву
// вызовов (включая мост через pointer-slot для COMPUTED_CALL) к диспетчеру/задаче,
// декомпилирует каждую функцию и печатает все чтения адресов, деля их на:
//   RAM/IO  (>=0xFFFE0000) -- живое состояние/регистры, не калибровка;
//   CODE    (низкий адрес, внутри функции) -- поток управления;
//   CALIB?  (низкий адрес, данные) -- КАНДИДАТ в калибровочный флаг.
// Master-enable проявится как CALIB?-чтение, гейтящее ветку вокруг immo-вызовов.
//
// Запуск: headless-analyze.sh <projdir> <proj> -process <prog> -noanalysis
//   -scriptPath tools/ghidra -postScript NatsGate.java <entry_hex> [<entry_hex> ...]
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;

public class NatsGate extends GhidraScript {
    DecompInterface dec;
    static final int MAX_FUNCS = 24;

    boolean isRamIo(long a) { return (a & 0xFFFFFFFFL) >= 0xFFFE0000L; }

    Function ensureFunc(Address e) throws Exception {
        if (getInstructionAt(e) == null) disassemble(e);
        Function f = getFunctionContaining(e);
        if (f == null) f = createFunction(e, null);
        return f;
    }

    // Собрать точки-входа функций, вызывающих f (для подъёма к диспетчеру).
    // Мост через pointer-slot: data-ссылка из слота -> кто читает слот.
    List<Address> callersOf(Function f) {
        List<Address> up = new ArrayList<>();
        for (Reference r : getReferencesTo(f.getEntryPoint())) {
            Address from = r.getFromAddress();
            Function ff = getFunctionContaining(from);
            if (ff != null) {
                up.add(ff.getEntryPoint());
            } else {
                // from -- слот данных (таблица указателей): climb к читателям слота
                for (Reference r2 : getReferencesTo(from)) {
                    Function f2 = getFunctionContaining(r2.getFromAddress());
                    if (f2 != null) up.add(f2.getEntryPoint());
                }
            }
        }
        return up;
    }

    void report(Function f) throws Exception {
        println("\n==================== FUNC " + f.getName() + " @" + f.getEntryPoint()
                + " size=" + f.getBody().getNumAddresses() + "B ====================");
        println("  --- callers (подъём к диспетчеру) ---");
        Set<String> seen = new LinkedHashSet<>();
        for (Reference r : getReferencesTo(f.getEntryPoint())) {
            Function cf = getFunctionContaining(r.getFromAddress());
            seen.add("    <- " + r.getFromAddress()
                    + (cf != null ? "  func=" + cf.getEntryPoint() : "  (data-slot/table)")
                    + "  [" + r.getReferenceType() + "]");
        }
        for (String s : seen) println(s);

        println("  --- чтения адресов (CALIB? = кандидат master-enable) ---");
        InstructionIterator it = currentProgram.getListing().getInstructions(f.getBody(), true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            for (Reference r : ins.getReferencesFrom()) {
                RefType rt = r.getReferenceType();
                if (!(rt.isData() || rt.isRead() || rt.isWrite())) continue;
                long t = r.getToAddress().getOffset();
                String kind;
                if (isRamIo(t)) kind = "RAM/IO";
                else if (getFunctionContaining(r.getToAddress()) != null) kind = "CODE";
                else kind = "CALIB?";
                String rw = rt.isWrite() ? "W" : "R";
                println(String.format("    %s  %-6s %s  @%08x  %s",
                        ins.getAddress(), kind + "/" + rw, "", t, ins.toString()));
            }
        }

        DecompileResults dr = dec.decompileFunction(f, 60, monitor);
        if (dr != null && dr.decompileCompleted()) {
            println("  --- C ---");
            for (String ln : dr.getDecompiledFunction().getC().split("\n")) println("    " + ln);
        } else {
            println("  (декомпиляция не удалась)");
        }
    }

    @Override
    protected void run() throws Exception {
        dec = new DecompInterface();
        dec.openProgram(currentProgram);

        Deque<Address> q = new ArrayDeque<>();
        for (String a : getScriptArgs()) q.add(toAddr(Long.parseLong(a, 16)));

        Set<Long> done = new LinkedHashSet<>();
        List<Function> order = new ArrayList<>();
        while (!q.isEmpty() && order.size() < MAX_FUNCS) {
            Address e = q.poll();
            Function f = ensureFunc(e);
            if (f == null) { println("!! нет функции @ " + e); continue; }
            long key = f.getEntryPoint().getOffset();
            if (done.contains(key)) continue;
            done.add(key);
            order.add(f);
            for (Address up : callersOf(f)) if (!done.contains(up.getOffset())) q.add(up);
        }
        println("### дерево immo (снизу вверх), функций: " + order.size());
        for (Function f : order) report(f);
        dec.dispose();
        println("\n[NatsGate done]");
    }
}
