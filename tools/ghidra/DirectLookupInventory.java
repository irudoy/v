// DirectLookupInventory.java – инвентаризация карт через банк примитивов с неявной осью.
//
// Модель отличается от MapInventory (explicit-axis): обёрток нет, аксессор зовёт
// примитив напрямую через pool-слот, указателя оси нет. Ось неявная и равномерная:
// точки 0..(N-1) с шагом step по сырому входу, последняя точка = лимит. Слот != вызов:
// один загруженный в callee-saved регистр указатель обслуживает несколько jsr подряд.
//
// Уровни: (1) слоты со значением примитива (BE u32) -> (2) инструкция-загрузка
// mov.l @(disp,pc),rN внутри аксессора -> (3) forward-скан по функции: каждый
// jsr/jmp @rN, пока rN не переопределён, = место вызова -> (4) снятие r4 (таблица,
// pc-relative pool load) и r5 (вход) с учётом delay slot.
//
// Геометрия каждого примитива задаётся аргументом и снята с его кода: примитив
// сравнивает вход с лимитом (CMP/HS) и на выходе за диапазон читает крайнюю точку
// (MOV.B @(N-1,R4) / MOV.W @(2*(N-1),R4)), а шаг задаётся точкой входа в общую
// цепочку SHLR/ROTCR: вход на K пар выше слияния даёт index = raw >> K, step = 2^K.
// Оба вывода независимы и сходятся на всех входах банка (см. JK03A.notes.md,
// раздел "Банк примитивов с неявной осью").
//
// Ширина элемента здесь выводится тем же правилом, что и в ПЗУ: цепочка делает
// SHLR8 R0; TST R0,R0 над лимитом, то есть лимит >= 256 означает word-таблицу.
// Отдельного флага ширины в коде нет. Оба пути читают элемент беззнаково (EXTU.B/EXTU.W).
//
// Запуск (headless):
//   -postScript DirectLookupInventory.java <out_dir> <prim_hex:points:step> [...]
// Выход: direct_lookup_inventory.csv
//   prim,points,step,width,slot,aligned,load_at,reg,from,from_func,mnem,table,vals,r5_src
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

public class DirectLookupInventory extends GhidraScript {

    static final long ROM_HI = 0x180000L;
    static final int FWD_LIMIT = 400;   // потолок forward-скана, инструкций
    static final int BACK_LIMIT = 14;   // окно backtrack, инструкций

    Listing listing;
    Memory mem;
    FunctionManager fm;

    public void run() throws Exception {
        String[] a = getScriptArgs();
        String outDir = a[0];

        mem = currentProgram.getMemory();
        listing = currentProgram.getListing();
        fm = currentProgram.getFunctionManager();

        PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "direct_lookup_inventory.csv")));
        w.println("prim,points,step,width,slot,aligned,load_at,reg,from,from_func,mnem,table,vals,r5_src");

        LinkedHashSet<String> allSites = new LinkedHashSet<>();
        LinkedHashSet<String> allTables = new LinkedHashSet<>();
        int allSlots = 0, allLoads = 0;

        for (int i = 1; i < a.length; i++) {
            String[] spec = a[i].split(":");
            long prim = Long.parseLong(spec[0], 16);
            int points = Integer.parseInt(spec[1]);
            int step = Integer.parseInt(spec[2]);
            long limit = (long) (points - 1) * step;
            int width = ((limit >> 8) != 0) ? 2 : 1;   // SHLR8 R0; TST R0,R0

            Res r = census(w, prim, points, step, width);
            allSlots += r.slots;
            allLoads += r.loads;
            allSites.addAll(r.sites);
            allTables.addAll(r.tables);
            println(String.format("VQ_DLI %05x points=%d step=%d width=%d limit=%d"
                    + " slots=%d loads=%d no_load=%d sites=%d tables=%d",
                    prim, points, step, width, limit,
                    r.slots, r.loads, r.noload, r.sites.size(), r.tables.size()));
        }
        w.close();
        println("VQ_DLI_TOTAL slots=" + allSlots + " loads=" + allLoads
                + " call_sites=" + allSites.size() + " tables=" + allTables.size());
    }

    static class Res {
        int slots, loads, noload;
        LinkedHashSet<String> sites = new LinkedHashSet<>();
        LinkedHashSet<String> tables = new LinkedHashSet<>();
    }

    Res census(PrintWriter w, long prim, int points, int step, int width) throws Exception {
        Res res = new Res();
        ReferenceManager rm = currentProgram.getReferenceManager();

        // 1. слоты: локации со значением примитива (BE u32)
        byte[] pat = new byte[]{
            (byte) ((prim >> 24) & 0xff), (byte) ((prim >> 16) & 0xff),
            (byte) ((prim >> 8) & 0xff),  (byte) (prim & 0xff)};
        byte[] mask = new byte[]{-1, -1, -1, -1};
        List<Address> slots = new ArrayList<>();
        Address start = currentProgram.getMinAddress();
        while (true) {
            Address found = mem.findBytes(start, pat, mask, true, monitor);
            if (found == null) break;
            slots.add(found);
            start = found.add(1);
        }
        res.slots = slots.size();

        // 2. загрузки слота в регистр
        for (Address slot : slots) {
            boolean aligned = (slot.getOffset() & 3) == 0;
            ReferenceIterator ri = rm.getReferencesTo(slot);
            boolean any = false;
            while (ri.hasNext()) {
                Reference r = ri.next();
                Address at = r.getFromAddress();
                Instruction ins = listing.getInstructionContaining(at);
                if (ins == null) continue;
                Register reg = soleResultReg(ins);
                if (reg == null) continue;
                any = true;
                res.loads++;
                Function host = fm.getFunctionContaining(at);

                // 3. forward-скан: вызовы через этот регистр
                for (Address site : forwardCalls(ins, reg, host)) {
                    Instruction ci = listing.getInstructionContaining(site);
                    long t = poolValueOf(lastSetter(site, "r4"));
                    String vals = "", tbl = "";
                    if (t != -1 && t < ROM_HI) {
                        tbl = String.format("%08x", t);
                        vals = readVals(t, points, width);
                        res.tables.add(tbl);
                    }
                    Instruction s5 = lastSetter(site, "r5");
                    w.println(String.join(",",
                            String.format("%08x", prim), String.valueOf(points),
                            String.valueOf(step), String.valueOf(width),
                            slot.toString(), String.valueOf(aligned), at.toString(),
                            reg.getName(), site.toString(),
                            host == null ? "?" : host.getEntryPoint().toString(),
                            ci == null ? "?" : ci.getMnemonicString(),
                            tbl, q(vals), q(s5 == null ? "" : s5.toString())));
                    res.sites.add(site.toString());
                }
            }
            if (!any) res.noload++;
        }
        return res;
    }

    // Единственный регистр-результат инструкции (mov.l @(disp,pc),rN).
    Register soleResultReg(Instruction ins) {
        Register only = null;
        for (Object o : ins.getResultObjects()) {
            if (!(o instanceof Register)) continue;
            if (only != null) return null;
            only = (Register) o;
        }
        return only;
    }

    // Вызовы jsr/jmp @reg от загрузки до переопределения reg. Регистры r0..r7 -
    // caller-saved (SH ABI), поэтому за чужим вызовом их значение не переживает.
    List<Address> forwardCalls(Instruction load, Register reg, Function host) {
        List<Address> out = new ArrayList<>();
        Address lo = host == null ? null : host.getBody().getMinAddress();
        Address hi = host == null ? null : host.getBody().getMaxAddress();
        boolean scratch = isScratch(reg);
        Instruction cur = listing.getInstructionAfter(load.getAddress());
        for (int k = 0; k < FWD_LIMIT && cur != null; k++) {
            Address at = cur.getAddress();
            if (lo != null && (at.compareTo(lo) < 0 || at.compareTo(hi) > 0)) break;
            String m = cur.getMnemonicString().toLowerCase();
            boolean indirect = (m.startsWith("jsr") || m.startsWith("jmp")) && usesReg(cur, reg);
            if (indirect) {
                out.add(at);
            } else if (scratch && (m.startsWith("jsr") || m.startsWith("bsr"))) {
                break;  // чужой вызов затирает caller-saved регистр
            } else if (definesReg(cur, reg)) {
                break;  // переопределение: дальше живёт другое значение
            }
            cur = listing.getInstructionAfter(at);
        }
        return out;
    }

    boolean isScratch(Register reg) {
        String n = reg.getName();
        if (n.length() != 2 || n.charAt(0) != 'r') return false;
        char c = n.charAt(1);
        return c >= '0' && c <= '7';
    }

    boolean usesReg(Instruction ins, Register reg) {
        for (Object o : ins.getOpObjects(0)) if (reg.equals(o)) return true;
        return false;
    }

    boolean definesReg(Instruction ins, Register reg) {
        for (Object o : ins.getResultObjects()) if (reg.equals(o)) return true;
        return false;
    }

    // Инструкция, последней записавшая reg до фактического вызова. Delay slot
    // (site+1) исполняется ПЕРЕД телом callee, поэтому проверяется первым.
    Instruction lastSetter(Address site, String regName) {
        Register reg = currentProgram.getRegister(regName);
        Instruction ins = listing.getInstructionContaining(site);
        if (ins == null || reg == null) return null;
        Instruction ds = listing.getInstructionAfter(site);
        if (ds != null && definesReg(ds, reg)) return ds;
        Instruction cur = listing.getInstructionBefore(site);
        for (int k = 0; k < BACK_LIMIT && cur != null; k++) {
            if (definesReg(cur, reg)) return cur;
            cur = listing.getInstructionBefore(cur.getAddress());
        }
        return null;
    }

    // Значение, загруженное pc-relative (ближайшая ref = literal pool, disp < 0x800)
    long poolValueOf(Instruction cur) {
        if (cur == null) return -1;
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

    // Точки таблицы, беззнаково (обе ветви цепочки заканчиваются EXTU.B/EXTU.W).
    String readVals(long addr, int points, int width) {
        StringBuilder sb = new StringBuilder();
        try {
            Address base = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(addr);
            for (int i = 0; i < points; i++) {
                if (i > 0) sb.append(' ');
                if (width == 1) sb.append(mem.getByte(base.add(i)) & 0xff);
                else sb.append(mem.getShort(base.add(2L * i)) & 0xffff);
            }
        } catch (Exception e) { return ""; }
        return sb.toString();
    }

    String q(String s) {
        if (s == null) return "";
        return "\"" + s.replace("\"", "\"\"") + "\"";
    }
}
