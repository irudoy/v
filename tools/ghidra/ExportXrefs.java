// Экспорт обращений функций к периферии SH7058/59 (якоря для поиска immo/NATS).
// Помимо прямых data-references на регистры (0xFFFF0000+), разрешает literal-pool:
// PC-relative загрузка 32-битной константы, чьё значение указывает в периферию,
// засчитывается как обращение функции к регистру (типовой путь SH-2 к memory-mapped
// I/O: mov.l @(disp,PC),Rn затем mov @Rn). Классификация региона – в загрузчике.
//
// Запуск: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript ExportXrefs.java <outdir>
// Пишет <outdir>/xrefs.csv (func_addr,periph_addr,kind): kind = R/W/D прямой,
// L – через literal-pool.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.PrintWriter;

public class ExportXrefs extends GhidraScript {
    // Нижняя граница = on-chip RAM base SH7059 (0xFFFE8000, 48 KB); включает RAM
    // (переменные, CAN message-table) и регистры периферии до 0xFFFFFFFF.
    static final long PERIPH_LO = 0xFFFE8000L;
    static final long PERIPH_HI = 0xFFFFFFFFL;
    static final long ROM_HI = 0x180000L;

    private boolean isPeriph(long v) {
        return v >= PERIPH_LO && v <= PERIPH_HI;
    }

    @Override
    public void run() throws Exception {
        String outdir = getScriptArgs().length > 0 ? getScriptArgs()[0] : "/tmp";
        new File(outdir).mkdirs();
        FunctionManager fm = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        Memory mem = currentProgram.getMemory();
        PrintWriter xw = new PrintWriter(new File(outdir, "xrefs.csv"));
        xw.println("func_addr,periph_addr,kind");
        int nx = 0;
        for (Function f : fm.getFunctions(true)) {
            String faddr = f.getEntryPoint().toString();
            for (Instruction instr : listing.getInstructions(f.getBody(), true)) {
                for (Reference ref : instr.getReferencesFrom()) {
                    Address to = ref.getToAddress();
                    if (to == null || !to.isMemoryAddress()) {
                        continue;
                    }
                    long toOff = to.getOffset() & 0xFFFFFFFFL;
                    long periph = -1;
                    String kind = "?";
                    if (isPeriph(toOff)) {
                        periph = toOff;                      // прямой ref на регистр
                        RefType rt = ref.getReferenceType();
                        kind = rt.isWrite() ? "W" : (rt.isRead() ? "R" : "D");
                    } else if (toOff < ROM_HI) {
                        try {
                            long v = mem.getInt(to) & 0xFFFFFFFFL;  // BE (программа big-endian)
                            if (isPeriph(v)) {
                                periph = v;                  // адрес регистра через literal-pool
                                kind = "L";
                            }
                        } catch (MemoryAccessException e) {
                            // неинициализированная память – пропустить
                        }
                    }
                    if (periph < 0) {
                        continue;
                    }
                    xw.println(faddr + "," + String.format("%08x", periph) + "," + kind);
                    nx++;
                }
            }
        }
        xw.close();
        println("VQ_XREFS periph_refs=" + nx + " dir=" + outdir);
    }
}
