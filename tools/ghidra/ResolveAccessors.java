// ResolveAccessors.java - differential-резолв операндов аксессоров карт
// (раздел 6 tools/map-flag-pipeline.md).
//
// Множество сайтов совпадает с цензом MapInventory (слоты со значением kernel ->
// обёртки, ссылающиеся на слот -> call-ссылки на вход обёртки), поэтому механизмы
// сравниваются сайт-в-сайт. На каждом сайте эмитятся обе тройки:
//   bt_r4/r5/r6 - MapInventory.backtrack: 14 инструкций назад, ближайший pc-literal
//                 (эталон, из которого собран текущий ценз);
//   df_r4..r7   - data-flow: входные varnode'ы CALL/CALLIND из HighFunction (условие А).
//                 Ram-varnode = слот пула, значение - его содержимое; register/unique
//                 сворачиваются backward-slice по p-code.
// Резерв - SymbolicPropogator по инструкциям: varnode'ы, не свернувшиеся в slice.
//
// GBR (условие Б) резолвится локально: значение ставится самой функцией (`ldc rN,gbr`)
// и своё в каждой - в JK03A и RAM-база (FUN_0003b75c: gbr=0xffff1dec), и ROM-база
// (gbr=0x11ebe у аксессоров 0x4e2xx). Поэтому и декомпилятор, и SymbolicPropogator от
// входа функции сворачивают gbr сами; глобальный register-context для gbr неверен.
// Функции, получающие gbr от вызывателя, дают gbr-relative операнд (kind gbrrel).
//
// Сайты вне функций: участок, куда нет прямых вызовов, Ghidra функциями не размечает,
// и декомпилятор туда не дотягивается (а backtrack работает - отсюда bt_only). Такие
// участки восстанавливаются: начало участка - пролог за rts предыдущей функции, тело
// Ghidra строит по flow. Прогон под -readOnly держит восстановленное в памяти; тот же
// дефект разметки скрывает эти вызовы и от ExportGraph (обёртки без вызывателей в графе).
//
// verdict сайта - по тройке r4/r5/r6, приоритет conflict > bt_only > df_only > agree:
//   agree     - обе тройки дали одно и то же;
//   df_only   - data-flow снял то, чего backtrack не дал;
//   bt_only   - backtrack снял то, чего data-flow не дал (регрессия на разбор);
//   conflict  - базы расходятся (латентная ошибка nearestLoad-эвристики в цензе).
// Инвариант принятия - data-flow покрывает backtrack, то есть bt_only = 0.
//
// Запуск (headless): -postScript ResolveAccessors.java <out_dir> <kernel_hex>
// Выход: accessors.<kernel>.csv - файл на ценз. Ядер доступа к таблицам несколько
// (JK03A: 0x26944 по байтовой оси, 0x26984 и 0x26b84 по словной), прогон идёт на каждое,
// и загрузчик собирает калибровочный слой из всех цензов сразу - поэтому имя несёт ядро,
// а строка - колонку kernel.
//   kernel,wrapper,slot,accessor,callsite,func,bt_r4,bt_r5,bt_r6,df_r4,df_r5,df_r6,df_r7,
//   k4,k5,k6,k7,verdict
// func: orig (функция была размечена) | recovered (восстановлена) | none.
// Источник каждого df-операнда - колонки k4..k7: pool (разыменован слот пула), const,
// slice (свёрнут по p-code), sp (резерв SymbolicPropogator), gbrrel (значение
// gbr-relative, gbr приходит от вызывателя), dyn (не сворачивается), none (входа нет).
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
    static final int SLICE_DEPTH = 12;      // глубина свёртки p-code
    static final int REGION_SCAN = 4096;    // потолок обхода участка вне функций

    Listing listing;
    Memory mem;
    FunctionManager fm;
    ReferenceManager rm;
    Register rGbr;
    Register[] argRegs = new Register[4];   // r4, r5, r6, r7
    boolean lastGbrRel;                     // SP дал gbr-relative, gbr не свёрнут

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
        println("VQ_RES вход: slots=" + slots.size() + " wrappers=" + wrappers.size()
                + " call_sites=" + sites.size());

        int recovered = recoverFuncs(sites);
        println("VQ_RES восстановлено функций: " + recovered);

        ifc = new DecompInterface();
        try {
            ifc.openProgram(currentProgram);
            int done = 0;
            for (Site s : sites) {
                try { s.bt = backtrack(s.at); } catch (Exception e) { /* эталон best-effort */ }
                dataflow(s);
                if (++done % 25 == 0) println("  ... " + done + "/" + sites.size());
            }
        } finally {
            ifc.dispose();
        }

        write(new File(outDir, "accessors." + Long.toHexString(kernel) + ".csv"), sites, kernel);
        summary(sites, wrappers);
    }

    // Восстановление функций под сайтами, оставшимися вне разметки: тело строится по flow
    // от начала участка (пролог за rts предыдущей функции). Участок может содержать
    // несколько неразмеченных функций подряд, поэтому проходы повторяются, пока растёт
    // покрытие: каждая созданная функция сдвигает начало участка к следующей.
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
                    println("  восстановление " + st + " не удалось: " + e);
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

    // 1. слоты: локации, содержащие значение kernel (BE u32)
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

    // 2. обёртки: функции, ссылающиеся на слот
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

    // 3. сайты: call-ссылки на вход обёртки
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

    // Условие А: аргументы CALLIND, поднятые декомпилятором как упорядоченные входы
    // вызова (in[1]=r4, in[2]=r5, in[3]=r6, in[4]=r7).
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
            }
        }
        // Резерв: varnode'ы, не свернувшиеся в slice.
        for (int k = 0; k < 4; k++) {
            if (s.df[k] != -1) continue;
            lastGbrRel = false;
            Long v = propagated(s, argRegs[k]);
            if (v != null) { s.df[k] = v; s.kind[k] = "sp"; }
            else if (lastGbrRel) s.kind[k] = "gbrrel";
        }
    }

    // Значение аргумента вызова: ram-varnode - ячейка (слот пула), значение = содержимое;
    // константа - значение напрямую; register/unique - свёртка backward-slice.
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

    // Свёртка backward-slice: register/unique - по define-use до константы. gbr отдельного
    // случая не требует: функция ставит его сама (ldc), и def сворачивается общим путём.
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
            case PcodeOp.PTRSUB:                 // &global: адрес, не содержимое
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
                return null;                     // MULTIEQUAL/INDIRECT и прочее: не одно значение
        }
    }

    // Резерв: значение регистра на адресе сайта по symbolic propagation. Register-relative
    // результат означает, что база приходит от вызывателя (для gbr - условие Б за пределами
    // функции): значения нет, сайт помечается gbrrel, а не теряется.
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
            // recordStartEndState=true: getRegisterValue даёт значение на адресе, а не итоговое
            sp = new SymbolicPropogator(currentProgram, true);
            sp.flowConstants(key, body, new ContextEvaluatorAdapter(), false, monitor);
        } catch (Exception e) {
            println("  SP не прошёл на " + key + ": " + e);
            sp = null;
        }
        spCache.put(key, sp);
        return sp;
    }

    // Границы участка кода вне функций: назад/вперёд по инструкциям, пока они не
    // принадлежат ни одной функции.
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
        } catch (Exception e) { /* ниже уйдёт в резерв */ }
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

    // Эталон: MapInventory.backtrack - 14 инструкций назад, ближайший pc-relative load.
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

    // Приоритет: conflict (базы расходятся) > bt_only (регрессия) > df_only > agree.
    String verdict(Site s) {
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
                + "df_r4,df_r5,df_r6,df_r7,k4,k5,k6,k7,verdict");
        String khex = String.format("%08x", kernel);
        for (Site s : sites) {
            w.println(String.format("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s",
                    khex, s.wrapper, s.slot, s.accessor, s.at, s.fsrc,
                    hx(s.bt[0]), hx(s.bt[1]), hx(s.bt[2]),
                    hx(s.df[0]), hx(s.df[1]), hx(s.df[2]), hx(s.df[3]),
                    s.kind[0], s.kind[1], s.kind[2], s.kind[3], verdict(s)));
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
        println("VQ_RES sites=" + n + " bt_r4=" + btR4 + " df_r4=" + dfR4
                + " резолюция bt=" + pct(btR4, n) + "% df=" + pct(dfR4, n) + "%");
        println("VQ_RES операндов r4/r5/r6: bt=" + btAll + " df=" + dfAll + " из " + (n * 3));
        println("VQ_RES verdict: " + vd);
        println("VQ_RES источник df_r4: " + kd);
        println("VQ_RES функция сайта: " + fs);
        // Обёртки, у которых call-ссылок на вход нет вовсе.
        for (Map.Entry<Function, Address> e : wrappers.entrySet()) {
            boolean any = false;
            for (Site s : sites) if (s.wrapper.equals(e.getKey().getEntryPoint())) { any = true; break; }
            if (!any) println("VQ_RES обёртка без call-сайтов: " + e.getKey().getEntryPoint());
        }
    }

    int pct(int a, int b) { return b == 0 ? 0 : (a * 100) / b; }

    String hx(long v) { return v == -1 ? "" : String.format("%08x", v); }
}
