// RecoverFuncs.java - разметка функциями кода, оставшегося вне функций (Stage 0,
// раздел 7 tools/map-flag-pipeline.md).
//
// Автоанализ делает функцию из участка, на который есть прямая ссылка вызова. Код,
// достижимый только косвенно (jsr @rN через слот пула) или через диспетчер по указателю,
// функцией не становится: инструкции дизассемблированы, но ни в одну функцию не входят.
// Следствия измеримы на цензе карт JK03A: 17 из 124 call-сайтов ядра 0x26944 лежат вне
// разметки, поэтому ExportGraph их вызовы не перечисляет (обёртки 0x26100 и 0x26230 в
// графе остаются без вызывателей), а декомпилятор в такой участок не дотягивается, и
// data-flow операндов там недоступен.
//
// Проход ищет непрерывные участки инструкций вне функций и создаёт функцию с начала
// каждого; тело Ghidra строит по flow. Участок может содержать несколько функций подряд,
// поэтому проходы повторяются, пока покрытие растёт: созданная функция отсекает свой
// пролог, и начало остатка сдвигается к следующей.
//
// Разметка не создаёт код: она группирует в функции только те инструкции, которые
// дизассемблер уже произвёл. Участок, начинающийся не с пролога (вход только по jump) или
// с delay slot, даёт отказ createFunction - он считается в отчёте и участок остаётся.
//
// Запуск (headless): -postScript RecoverFuncs.java
// Под -readOnly прогон считает и отчитывается, но разметку в проект не сохраняет (dry-run);
// без -readOnly headless сохраняет её в проект, и её видит следующий ExportGraph.
//@category VQ
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import java.util.ArrayList;
import java.util.List;

public class RecoverFuncs extends GhidraScript {

    static final int MAX_PASS = 32;   // потолок проходов; выход по исчерпанию роста

    Listing listing;
    FunctionManager fm;

    @Override
    public void run() throws Exception {
        listing = currentProgram.getListing();
        fm = currentProgram.getFunctionManager();

        int insBefore = countOutside();
        int regBefore = regionStarts().size();
        int funcBefore = fm.getFunctionCount();
        println("VQ_RF вход: функций " + funcBefore + ", инструкций вне функций " + insBefore
                + " в " + regBefore + " участках");

        int made = 0, failed = 0;
        for (int pass = 1; pass <= MAX_PASS; pass++) {
            if (monitor.isCancelled()) break;
            List<Address> starts = regionStarts();
            if (starts.isEmpty()) break;
            int mp = 0, fp = 0;
            for (Address st : starts) {
                if (monitor.isCancelled()) break;
                if (fm.getFunctionContaining(st) != null) continue;   // покрыт телом соседней
                int tx = currentProgram.startTransaction("recover-func");
                boolean ok = false;
                try {
                    ok = createFunction(st, null) != null;
                } catch (Exception e) {
                    ok = false;
                } finally {
                    currentProgram.endTransaction(tx, ok);
                }
                if (ok) mp++; else fp++;
            }
            made += mp;
            failed = fp;                                              // отказы последнего прохода
            println("  проход " + pass + ": участков " + starts.size() + ", создано " + mp
                    + ", отказ " + fp);
            if (mp == 0) break;                                       // рост исчерпан
        }

        int insAfter = countOutside();
        List<Address> left = regionStarts();
        println("VQ_RF создано функций: " + made + ", функций всего " + fm.getFunctionCount());
        println("VQ_RF инструкций вне функций: " + insBefore + " -> " + insAfter
                + " (участков " + regBefore + " -> " + left.size() + ", отказ " + failed + ")");
        for (int i = 0; i < left.size() && i < 20; i++) {
            Instruction ins = listing.getInstructionAt(left.get(i));
            println("  остаётся вне функций: " + left.get(i)
                    + (ins == null ? "" : "  " + ins.toString()));
        }
        if (left.size() > 20) println("  ... ещё " + (left.size() - 20) + " участков");
    }

    // Начала непрерывных участков инструкций вне функций: инструкция вне функции, перед
    // которой либо функция, либо разрыв дизассемблера (пул литералов, данные).
    List<Address> regionStarts() {
        List<Address> out = new ArrayList<>();
        Address prevMax = null;
        boolean prevOutside = false;
        for (Instruction ins : listing.getInstructions(true)) {
            boolean outside = fm.getFunctionContaining(ins.getAddress()) == null;
            boolean gap = !ins.getAddress().equals(after(prevMax));
            if (outside && (!prevOutside || gap)) out.add(ins.getAddress());
            prevOutside = outside;
            prevMax = ins.getMaxAddress();
        }
        return out;
    }

    int countOutside() {
        int n = 0;
        for (Instruction ins : listing.getInstructions(true)) {
            if (fm.getFunctionContaining(ins.getAddress()) == null) n++;
        }
        return n;
    }

    Address after(Address a) {
        if (a == null) return null;
        try {
            return a.add(1);
        } catch (Exception e) {
            return null;
        }
    }
}
