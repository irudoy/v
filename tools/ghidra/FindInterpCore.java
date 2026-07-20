// FindInterpCore.java – детект ядер интерполяции и их обёрток data-сканом (Stage 1,
// раздел 7 tools/map-flag-pipeline.md). Заменяет ручной поиск "найти 0x26944".
//
// СИГНАТУРА – слот плюс ДВА уровня косвенности. Адрес ядра лежит в ПЗУ 4-байтовым словом
// (константа литерального пула); вход грузит его mov.l @(disp,pc),rN и уходит туда jsr @rN
// либо jmp @rN (хвостовой переход). Прямому вызову слот не нужен - он и отделяет
// библиотеку доступа от прочего кода.
//
// Одного слота мало: аксессор зовёт ВХОД тем же механизмом, поэтому слот с jsr ловит весь
// слой косвенных вызовов разом, и входы стоят в нём выше ядер - их зовут чаще (0x26370:
// 62 вызывателя против 11 у ядра 0x26944). Ядро отличает второй уровень: его вызыватели
// сами суть цели слотов, тогда как аксессоры, зовущие вход, целями слотов не являются.
// Колонка indirect_callers это и меряет, и по ней ранжирование, а не по числу вызывателей.
//
// Чем ядро НЕ отличается:
//   - счётом вызывателей: из >= 2 мест в JK03A зовутся 253 функции, ядер среди них 4;
//   - листовостью: пять ядер из тринадцати зовут общие хелперы (0x26944 и 0x26984 - оба
//     0x26c78, 0x26a60 - ядро 0x26740), и фильтр "слот указывает на лист" отбросил бы
//     главное ядро. Лист не отбирают, а печатают колонкой outs;
//   - тем, что оно функция: банк implicit-axis - входы в одну цепочку сдвигов, и
//     0x26a80/0x26a84/0x26a88 функциями в Ghidra не размечены вовсе (у 0x26a5c тело - 4
//     байта). Поэтому слот проверяется на код (getInstructionAt), а не на вход функции:
//     разметка функций - дело Ghidra, а не прошивки.
//
// ЧТО СКАН ЛОКАЛИЗУЕТ - библиотеку доступа, а не уровень ядра в ней. Сигнатура одна и та
// же у ядра и у хелпера, который ядро зовёт: 0x26c78 (общий хелпер 0x26944 и 0x26984)
// стоит в выдаче рангом 11, ядром не являясь. Что внутри слоя ядро, объявляет рукописный
// реестр defs/<rom>.interp.csv по клэмпу в delay slot (он же задаёт геометрию входа), а
// скрипт предлагает кандидатов со свидетельством при каждом.
//
// Измерено на JK03A (13 ядер реестра, 34 входа): найдены все 13. Четыре hub-ядра
// (0x26740, 0x26944, 0x26984, 0x26b84) стоят рангами 2, 3, 6, 8 из 799 кандидатов; банк
// implicit-axis (0x26a5c..0x26a88, по одному входу у каждого) - рангами 53-63, то есть
// найден, но числом входов не выделен: у 200 с лишним кандидатов вход тоже один. Банк
// виден иначе - восьмёркой соседних адресов через 4 байта, и его читает глаз, а не порог.
//
// Независимая сверка - центральность на проекции call-графа (tools/memgraph/queries.cypher,
// раздел 8.2): PageRank выводит библиотеку доступа в топ и до Stage 3. Сигнал независим от
// этого скана, то есть сверка, а не повтор того же довода.
//
// Запуск (headless): -postScript FindInterpCore.java <out_dir> [<min_wrappers>]
// Выход: interp_core.csv (kernel,name,size,outs,slots,callers,indirect_callers,depth,
//        is_leaf,slot_list,caller_list), ранжированный по depth и числу входов.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

public class FindInterpCore extends GhidraScript {

    // Кандидат ядра: функция, чей адрес лежит в пуле, и функции, делающие через него jsr.
    static class Cand {
        Address entry;
        Set<Address> slots = new LinkedHashSet<>();
        Set<Address> wrappers = new LinkedHashSet<>();
        int indirect;                       // из них сами суть цели слотов

        // Доля вызывателей, лежащих в пулах: у ядра ~1.0, у входа ~0.
        double depth() { return wrappers.isEmpty() ? 0 : (double) indirect / wrappers.size(); }
    }

    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 1) {
            println("VQ_CORE need: <out_dir> [<min_wrappers>]");
            return;
        }
        String outDir = a[0];
        int minWrappers = a.length > 1 ? Integer.parseInt(a[1]) : 1;

        Memory mem = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        ReferenceManager rm = currentProgram.getReferenceManager();

        // 1. Слоты: 4-выровненные слова ПЗУ, чьё значение указывает на код. Выравнивание -
        //    не догадка: mov.l читает длинное слово только по 4-байтовой границе, и
        //    константа пула, читаемая иначе, вызовом не становится. Цель проверяется на
        //    инструкцию, а не на вход функции: банк implicit-axis функциями не размечен.
        Map<Long, Cand> cands = new TreeMap<>();
        int words = 0;
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized()) continue;
            Address lo = b.getStart(), hi = b.getEnd();
            for (long off = align4(lo.getOffset()); off + 3 <= hi.getOffset(); off += 4) {
                if (monitor.isCancelled()) return;
                Address at = lo.getNewAddress(off);
                long v;
                try { v = mem.getInt(at) & 0xFFFFFFFFL; } catch (Exception e) { continue; }
                words++;
                if (v == 0 || (v & 1) != 0) continue;          // инструкция SH-2 чётна
                Address target;
                try { target = lo.getNewAddress(v); } catch (Exception e) { continue; }
                if (listing.getInstructionAt(target) == null) continue;
                Cand c = cands.computeIfAbsent(v, k -> new Cand());
                c.slots.add(at);
                c.entry = target;
            }
        }
        // 2. Входы: функции, ссылающиеся на слот И уходящие косвенно - jsr @rN (вызов) либо
        //    jmp @rN (хвостовой переход, которым вход уходит в finisher). Ссылка без
        //    косвенного перехода означает, что адрес взят не для передачи управления.
        for (Cand c : cands.values()) {
            for (Address slot : c.slots) {
                ReferenceIterator ri = rm.getReferencesTo(slot);
                while (ri.hasNext()) {
                    Function wf = fm.getFunctionContaining(ri.next().getFromAddress());
                    if (wf != null && hasIndirectBranch(listing, wf)) {
                        c.wrappers.add(wf.getEntryPoint());
                    }
                }
            }
        }

        // 3. Настоящие цели слотов - только те, чей слот кто-то читает. Слово, указавшее на
        //    код случайно, целью не является, и мерить по всем словам нельзя: их 2181 при
        //    2312 функциях ROM, то есть "вызыватель есть цель слота" было бы верно почти
        //    всегда, и признак не различал бы ничего.
        Set<Long> called = new LinkedHashSet<>();
        for (Map.Entry<Long, Cand> e : cands.entrySet()) {
            if (!e.getValue().wrappers.isEmpty()) called.add(e.getKey());
        }

        // 4. Второй уровень косвенности: сколько вызывателей кандидата сами вызываются через
        //    слот. У ядра таковы все - его зовут входы, а входы зовут аксессоры через слот;
        //    у входа почти никто - его зовут аксессоры, которых в пулах нет. Это и делит
        //    слои, тогда как счёт вызывателей ставит вход выше ядра.
        List<Cand> hits = new ArrayList<>();
        for (Cand c : cands.values()) {
            if (c.wrappers.isEmpty()) continue;
            for (Address wa : c.wrappers) {
                if (called.contains(wa.getOffset() & 0xFFFFFFFFL)) c.indirect++;
            }
            if (c.wrappers.size() >= minWrappers) hits.add(c);
        }
        hits.sort(Comparator.comparingDouble((Cand c) -> -c.depth())
                            .thenComparingInt(c -> -c.indirect)
                            .thenComparing(c -> c.entry));

        PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "interp_core.csv")));
        w.println("kernel,name,size,outs,slots,callers,indirect_callers,depth,is_leaf,"
                  + "slot_list,caller_list");
        for (Cand c : hits) {
            Function f = fm.getFunctionAt(c.entry);
            int outs = f == null ? -1 : countCalls(listing, f);
            w.println(String.format("%s,%s,%d,%d,%d,%d,%d,%.2f,%b,%s,%s",
                    c.entry, f == null ? "" : f.getName(),
                    f == null ? 0 : f.getBody().getNumAddresses(), outs,
                    c.slots.size(), c.wrappers.size(), c.indirect, c.depth(), outs == 0,
                    join(c.slots), join(c.wrappers)));
        }
        w.close();
        println("VQ_CORE words=" + words + " slot_values=" + cands.size()
                + " candidates=" + hits.size() + " min_wrappers=" + minWrappers);
        int top = 0;
        for (Cand c : hits) {
            if (top++ >= 16) break;
            println(String.format("VQ_CORE %s callers=%d indirect=%d depth=%.2f",
                    c.entry, c.wrappers.size(), c.indirect, c.depth()));
        }
    }

    static long align4(long v) { return (v + 3) & ~3L; }

    String join(Set<Address> s) {
        StringBuilder sb = new StringBuilder();
        for (Address a : s) {
            if (sb.length() > 0) sb.append(';');
            sb.append(a);
        }
        return sb.toString();
    }

    // jsr @rN - косвенный вызов, jmp @rN - хвостовой переход: вход уходит в ядро и так и
    // так, и проверка только на jsr теряет входы, отдающие управление без возврата.
    boolean hasIndirectBranch(Listing listing, Function f) {
        InstructionIterator it = listing.getInstructions(f.getBody(), true);
        while (it.hasNext()) {
            String m = it.next().getMnemonicString().toLowerCase();
            if (m.startsWith("jsr") || m.startsWith("jmp")) return true;
        }
        return false;
    }

    int countCalls(Listing listing, Function f) {
        int n = 0;
        InstructionIterator it = listing.getInstructions(f.getBody(), true);
        while (it.hasNext()) {
            for (Reference r : it.next().getReferencesFrom()) {
                if (r.getReferenceType().isCall()) n++;
            }
        }
        return n;
    }
}
