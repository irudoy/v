// ScanFlags.java – детект флагов от размеченной карты и guard-функции (Stage 6, раздел 7
// tools/map-flag-pipeline.md). Заменяет ручной трейс флагов.
//
// МЕХАНИКА. Калибровочные флаги HR живут по gbr. Тройка "загрузка - проверка бита -
// ветвление":
//   mov.b @(0x93,gbr),r0   ; -> ffff4217     загрузка байта флагов
//   tst   0x1,r0                             проверка бита (маска - непосредственная)
//   bt/bf <target>                           ветвление
// Пишется флаг тем же способом: or.b 0x20,@(r0,gbr) ставит бит, and.b 0xdf,@(r0,gbr) снимает.
//
// Адрес флага берётся из ссылки Ghidra, а не считается сложением базы со смещением, и это
// не удобство: БАЗА GBR НЕ ГЛОБАЛЬНА. Прошивка её переустанавливает - 0x68cb8 несёт
// ldc r0,gbr и ldc.l @r15+,gbr, то есть gbr там адресует другую структуру, и одно и то же
// @(disp,gbr) разрешается в разные адреса в разных функциях. Своё сложение дало бы
// правдоподобные адреса не тех ячеек - брак, который от факта не отличить.
//
// ЛОКАЛЬНО, А НЕ СПЛОШЬ. Скрипт идёт по заданным функциям - аксессорам размеченных карт и
// guard-функциям (их даёт ScanImmoAnchors по DTC-якорям), - а не по всей прошивке:
// bit-тестов в ROM тысячи, и сплошной скан даёт невод, а не находки. Первичный путь - от
// карты: флаг опознаётся тем, ЧТО он разветвляет, а не тем, что он бит.
//
// РОЛЬ ставится по тому, что лежит на ветвях, и только когда это видно из одной функции:
//   selector  - ветви грузят в r4 разные базы перед одним и тем же вызовом (:SELECTS обе);
//   gate      - вызов есть на одной ветви и отсутствует на другой (условный skip, :GATES);
//   threshold - на пути cmp с константой пула, указывающей в ПЗУ.
// Ветвление, чьи ветви скриптом не различены, выходит с role=unknown: это заявка на трейс,
// а не отсутствие флага. Роль здесь - предложение; узлом :Flag его делает трейс.
//
// ГРАНИЦА: детект gbr-флагов, а не всяких. Измерено на JK03A:
//   - аксессор 0x82c8a (14 карт): 62 находки, среди них selector gbr+0x93 bit0, ветвящий
//     r4 между 0xb61a и 0xb71a. Это разметка, снятая раньше трейсом, - скрипт её
//     воспроизводит независимо, и на ней он и проверяется;
//   - 25 аксессоров с невыбранной базой (kind=sp, 42 сайта): находок НОЛЬ, притом что
//     gbr-обращения и tst там есть. База там выбирается не битом: 0x68cb8 ветвит по cmp
//     после mov.w @(0x2c,gbr), а перепись резолвера называет такие сайты массивом таблиц
//     по регистру (0x64344 - шесть таблиц по r5, 0xbe39a - две по r13). Флаг их не
//     объясняет, и Stage 6 закрывает их перечислением ветвей, а не этим скриптом.
// Флаг, живущий не по gbr (указатель из пула на абсолютный адрес RAM), сюда не попадает.
//
// Запуск (headless): -postScript ScanFlags.java <out_dir> <func_addr> [<func_addr>...]
// Выход: flags.csv (func,test_at,flag_addr,gbr_disp,mask,bit,branch,taken,role,evidence)
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.block.BasicBlockModel;
import ghidra.program.model.block.CodeBlock;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

public class ScanFlags extends GhidraScript {

    static final long ROM_HI = 0x180000L;
    BasicBlockModel bbm;
    static final int WINDOW = 8;        // инструкций от загрузки флага до ветвления

    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 2) {
            println("VQ_FLAGS need: <out_dir> <func_addr>...");
            return;
        }
        bbm = new BasicBlockModel(currentProgram);
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        PrintWriter w = new PrintWriter(new FileWriter(new File(a[0], "flags.csv")));
        w.println("func,test_at,flag_addr,gbr_disp,mask,bit,branch,taken,role,evidence");

        int rows = 0, funcs = 0;
        for (int i = 1; i < a.length; i++) {
            Address ep = currentProgram.getAddressFactory().getAddress(a[i]);
            if (ep == null) { println("VQ_FLAGS bad address " + a[i]); continue; }
            Function f = fm.getFunctionAt(ep);
            if (f == null) { println("VQ_FLAGS no function at " + a[i]); continue; }
            funcs++;
            for (String row : scan(listing, f)) { w.println(row); rows++; }
        }
        w.close();
        println("VQ_FLAGS funcs=" + funcs + " flags=" + rows);
    }

    List<String> scan(Listing listing, Function f) throws Exception {
        List<String> out = new ArrayList<>();
        InstructionIterator it = listing.getInstructions(f.getBody(), true);
        List<Instruction> body = new ArrayList<>();
        while (it.hasNext()) body.add(it.next());

        // Идти НАДО от проверки назад, а не от загрузки вперёд: тест кормит ближайшая
        // предшествующая запись в его регистр. Поиск вперёд от каждой загрузки спаривает с
        // одним тестом обе загрузки, если их две подряд, и вторая находка - выдумка.
        for (int ti = 0; ti < body.size(); ti++) {
            Instruction tst = body.get(ti);
            String m = tst.getMnemonicString().toLowerCase();
            if (!m.equals("tst") && !m.equals("and")) continue;
            long mask = scalarOf(tst, 0);
            if (mask <= 0) continue;
            String reg = tst.getDefaultOperandRepresentation(tst.getNumOperands() - 1);
            if (reg == null) continue;
            reg = reg.trim();

            Instruction ld = null;
            for (int k = ti - 1; k >= Math.max(0, ti - WINDOW); k--) {
                if (!writesReg(body.get(k), reg)) continue;
                if (isGbrLoad(body.get(k))) ld = body.get(k);
                break;                       // ближайшая запись в регистр - она и кормит
            }
            if (ld == null) continue;
            Address flag = gbrTarget(ld);
            long disp = scalarOf(ld, 0);

            // ветвление после проверки
            Instruction br = null;
            for (int k = ti + 1; k < Math.min(ti + 4, body.size()); k++) {
                String bm = body.get(k).getMnemonicString().toLowerCase();
                if (bm.startsWith("bt") || bm.startsWith("bf")) { br = body.get(k); break; }
            }
            if (br == null) continue;

            String[] verdict = classify(br);
            out.add(String.format("%s,%s,%s,%02x,%02x,%s,%s,%s,%s,%s",
                    f.getEntryPoint(), tst.getAddress(),
                    flag == null ? "" : flag.toString(), disp, mask, bitOf(mask),
                    br.getMnemonicString(), target(br), verdict[0], verdict[1]));
        }
        return out;
    }

    // Роль ставится по тому, что лежит на ветвях, и ветви берутся из CFG Ghidra, а не
    // угадываются окном инструкций: у условного перехода два блока-наследника, и окно по
    // индексам их не различает - за ветвлением может лежать не альтернативная ветвь, а
    // точка схождения. Различаются только случаи, видимые из одной функции; прочее выходит
    // unknown и уходит в трейс, а не размечается наугад.
    String[] classify(Instruction br) throws Exception {
        // Ветви берутся у самой инструкции: getFlows() - взятая, getFallThrough() -
        // непрошедшая (и она же учитывает delay slot у bt/s и bf/s). Перечислять выходы
        // блока, содержащего ветвление, нельзя: у него их бывает больше двух, и какой из
        // них чья ветвь, оттуда не видно.
        Address taken = brTarget(br), fall = br.getFallThrough();
        if (taken == null || fall == null) {
            return new String[]{"unknown", "ветвь не разрешена"};
        }
        CodeBlock bt = bbm.getFirstCodeBlockContaining(taken, monitor);
        CodeBlock bf = bbm.getFirstCodeBlockContaining(fall, monitor);
        if (bt == null || bf == null) return new String[]{"unknown", "блок ветви не найден"};

        List<String> b0 = basesIn(bf), b1 = basesIn(bt);
        if (!b0.isEmpty() && !b1.isEmpty() && !b0.equals(b1)) {
            return new String[]{"selector", "r4: " + join(b0) + " | " + join(b1)};
        }
        boolean c0 = hasCallIn(bf), c1 = hasCallIn(bt);
        if (c0 != c1) {
            return new String[]{"gate", "вызов только в блоке "
                    + (c0 ? bf : bt).getFirstStartAddress()};
        }
        String cmp = cmpConstIn(bf);
        if (cmp == null) cmp = cmpConstIn(bt);
        if (cmp != null) return new String[]{"threshold", "cmp с " + cmp};
        return new String[]{"unknown", "ветви не различены"};
    }

    // Базы, загружаемые в r4 внутри блока. У mov.l @(disp,pc),r4 ссылок ДВЕ - на слот пула
    // и на разрешённое значение, - и базой является вторая. Различает их расстояние: слот
    // читается pc-относительно и лежит ближе 0x800, база калибровки - нет. Взять обе
    // значило бы сравнивать адреса пулов, которые на разных ветвях различны всегда, и
    // всякое ветвление выходило бы selector'ом.
    List<String> basesIn(CodeBlock b) {
        List<String> out = new ArrayList<>();
        InstructionIterator it = currentProgram.getListing().getInstructions(b, true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            if (!ins.getMnemonicString().toLowerCase().startsWith("mov.l")) continue;
            String dst = ins.getDefaultOperandRepresentation(ins.getNumOperands() - 1);
            if (dst == null || !dst.trim().equals("r4")) continue;
            long ia = ins.getAddress().getOffset() & 0xFFFFFFFFL;
            for (Reference r : ins.getReferencesFrom()) {
                Address t = r.getToAddress();
                if (t == null || !t.isMemoryAddress()) continue;
                long off = t.getOffset() & 0xFFFFFFFFL;
                long dist = off > ia ? off - ia : ia - off;
                if (off < ROM_HI && dist >= 0x800) out.add(String.format("%08x", off));
            }
        }
        return out;
    }

    boolean hasCallIn(CodeBlock b) {
        InstructionIterator it = currentProgram.getListing().getInstructions(b, true);
        while (it.hasNext()) {
            String m = it.next().getMnemonicString().toLowerCase();
            if (m.startsWith("jsr") || m.startsWith("bsr")) return true;
        }
        return false;
    }

    // Порог: cmp с константой, указывающей в ПЗУ калибровки (0x8FDC - образец раздела 7).
    String cmpConstIn(CodeBlock b) {
        InstructionIterator it = currentProgram.getListing().getInstructions(b, true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            if (!ins.getMnemonicString().toLowerCase().startsWith("cmp")) continue;
            for (Reference r : ins.getReferencesFrom()) {
                Address t = r.getToAddress();
                if (t != null && t.isMemoryAddress()
                        && (t.getOffset() & 0xFFFFFFFFL) < ROM_HI) return t.toString();
            }
        }
        return null;
    }

    // mov.b @(disp,gbr),r0 - загрузка байта флагов.
    //
    // Ghidra раскладывает gbr-адресацию на ТРИ операнда, а не на один "@(0x93,gbr)":
    //   загрузка  mov.b @(0x93,gbr),r0  ->  op0=0x93  op1=gbr  op2=r0
    //   запись    mov.b r0,@(0x45,gbr)  ->  op0=r0    op1=0x45 op2=gbr
    // Отсюда признак загрузки: gbr есть среди операндов и НЕ последний - последним стоит
    // приёмник, и у записи это память. Искать "gbr" в нулевом операнде бесполезно: там
    // лежит смещение.
    int gbrOperand(Instruction ins) {
        for (int k = 0; k < ins.getNumOperands(); k++) {
            String r = ins.getDefaultOperandRepresentation(k);
            if (r != null && r.trim().equalsIgnoreCase("gbr")) return k;
        }
        return -1;
    }

    // Элемент флага - не только байт: 0x68cb8 читает mov.w @(0x2c,gbr),r0. Бит проверяется
    // так же, чем бы флаг ни хранился, поэтому ширина здесь не фильтр.
    boolean isGbrLoad(Instruction ins) {
        String m = ins.getMnemonicString().toLowerCase();
        if (!m.startsWith("mov.b") && !m.startsWith("mov.w") && !m.startsWith("mov.l")) {
            return false;
        }
        int g = gbrOperand(ins);
        return g > 0 && g < ins.getNumOperands() - 1;
    }

    // Абсолютный адрес флага - из ссылки Ghidra: базу gbr знает она, и считать её здесь
    // значило бы завести второй источник одного факта.
    Address gbrTarget(Instruction ins) {
        for (Reference r : ins.getReferencesFrom()) {
            Address to = r.getToAddress();
            if (to != null && to.isMemoryAddress()
                    && (to.getOffset() & 0xFFFFFFFFL) >= 0xFFFF0000L) return to;
        }
        return null;
    }

    // Пишет ли инструкция в регистр: результат-объект есть сам регистр.
    boolean writesReg(Instruction ins, String reg) {
        for (Object o : ins.getResultObjects()) {
            if (o instanceof Register && ((Register) o).getName().equalsIgnoreCase(reg)) {
                return true;
            }
        }
        return false;
    }

    Address brTarget(Instruction br) {
        Address[] fl = br.getFlows();
        return fl.length > 0 ? fl[0] : null;
    }

    String target(Instruction br) {
        Address t = brTarget(br);
        return t == null ? "" : t.toString();
    }

    long scalarOf(Instruction ins, int op) {
        Object[] objs = ins.getOpObjects(op);
        for (Object o : objs) if (o instanceof Scalar) return ((Scalar) o).getUnsignedValue();
        return -1;
    }

    // Маска из одного бита даёт номер бита; маска из нескольких битом не является.
    String bitOf(long mask) {
        if (mask <= 0 || (mask & (mask - 1)) != 0) return "";
        return String.valueOf(Long.numberOfTrailingZeros(mask));
    }

    String join(List<String> xs) {
        StringBuilder sb = new StringBuilder();
        for (String x : xs) { if (sb.length() > 0) sb.append(';'); sb.append(x); }
        return sb.length() == 0 ? "-" : sb.toString();
    }
}
