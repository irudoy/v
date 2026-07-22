// DumpFuncListing.java — дизассемблинг функции целиком, от точки входа до конца тела,
// с разрешёнными ссылками (ref -> target [= прочитанное значение]).
//
// Отличие от DumpListing: тот печатает окрестность адреса (окно +-24 инструкции) и
// отвечает на вопрос "что стоит вокруг этого места". Здесь единица - функция, и границу
// задаёт её тело, а не окно. Нужно там, где короткая функция целиком есть предмет
// разбора: библиотека арифметики 0x21000..0x23000 передаёт аргументы регистрами, и
// соглашение читается только по всему телу. Псевдокод для этого не годится - разворот
// 32-шагового деления даёт 31 КБ на 282 байта кода.
//
// Запуск (headless): -postScript DumpFuncListing.java <out_dir> <addr> [<addr>...]
// Выход: funclisting_<addr>.txt на каждую функцию.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;

public class DumpFuncListing extends GhidraScript {

    @Override
    public void run() throws Exception {
        String[] a = getScriptArgs();
        if (a.length < 2) {
            println("VQ_FLST need: <outdir> <addr>...");
            return;
        }
        String outDir = a[0];
        new File(outDir).mkdirs();
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();
        int ok = 0;

        for (int i = 1; i < a.length; i++) {
            Address ep;
            try {
                ep = currentProgram.getAddressFactory().getDefaultAddressSpace()
                        .getAddress(Long.parseLong(a[i], 16));
            } catch (Exception e) {
                println("VQ_FLST bad addr " + a[i]);
                continue;
            }
            Function f = getFunctionAt(ep);
            if (f == null) {
                println("VQ_FLST no function at " + a[i]);
                continue;
            }
            String name = String.format("funclisting_%08x.txt", ep.getOffset() & 0xFFFFFFFFL);
            PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, name)));
            w.println("// " + f.getName() + " @ " + ep + "  size=" + f.getBody().getNumAddresses());
            // Тело функции - набор адресов, а не отрезок: Ghidra относит к функции и
            // отделённые куски (общий хвост, разделяемый эпилог). Обход по набору берёт их.
            AddressSetView body = f.getBody();
            InstructionIterator it = listing.getInstructions(body, true);
            while (it.hasNext()) {
                Instruction cur = it.next();
                StringBuilder line = new StringBuilder();
                line.append("   ").append(cur.getAddress()).append("  ").append(cur.toString());
                for (Reference r : cur.getReferencesFrom()) {
                    Address to = r.getToAddress();
                    if (to == null || !to.isMemoryAddress()) continue;
                    line.append("   ; -> ").append(to);
                    long off = to.getOffset() & 0xFFFFFFFFL;
                    if (off < 0x180000L) {
                        try {
                            long v = mem.getInt(to) & 0xFFFFFFFFL;
                            line.append(String.format(" [=%08x]", v));
                        } catch (Exception e) { /* не инициализировано */ }
                    }
                }
                w.println(line.toString());
            }
            w.close();
            ok++;
        }
        println("VQ_FLST wrote=" + ok + " dir=" + outDir);
    }
}
