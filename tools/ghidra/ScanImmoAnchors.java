// ScanImmoAnchors.java — поиск числовых якорей immo в дампе ECM: immo-DTC константы
// (P1610/P1611/P1612 = 0x1610/0x1611/0x1612; B2193 = 0xA193 в OBD-II 2-byte кодировке)
// как immediate-операнды в коде и как 16/32-битные данные (literal pool, DTC-таблица),
// с обратными ссылками на функции. Кластер из нескольких DTC в узком окне помечается
// как кандидат в DTC-таблицу — от неё xref ведёт к immo-хендлеру / гейту Lock Mode.
//
// Запуск (headless): -postScript ScanImmoAnchors.java <out_dir>
// Выход: immo_anchors.csv (dtc,hit_addr,kind,ctx), immo_tables.csv (окна-кандидаты).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;
import java.io.File;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ScanImmoAnchors extends GhidraScript {

    // immo-DTC в OBD-II 2-байтовой кодировке (big-endian): P1610/11/12 -> 0x1610/11/12,
    // B2193 -> 0xA193. Nissan P16xx — manufacturer-диапазон, эти три — NATS.
    static final int[] DTC = {0x1610, 0x1611, 0x1612, 0xA193};

    public void run() throws Exception {
        String[] a = getScriptArgs();
        String outDir = a.length > 0 ? a[0] : ".";
        new File(outDir).mkdirs();

        Memory mem = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();
        ReferenceManager rm = currentProgram.getReferenceManager();
        FunctionManager fm = currentProgram.getFunctionManager();

        Set<Integer> want = new HashSet<>();
        for (int d : DTC) want.add(d);

        PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "immo_anchors.csv")));
        w.println("dtc,hit_addr,kind,ctx");

        int nImm = 0, nData = 0;
        int[] perDtc = new int[DTC.length];

        // ---- 1. данные: 16-бит по чётным адресам + 32-бит по адресам /4 ----
        List<long[]> dataHits = new ArrayList<>(); // {value, addrOffset}
        for (MemoryBlock b : mem.getBlocks()) {
            if (!b.isInitialized()) continue;
            long s = b.getStart().getOffset(), e = b.getEnd().getOffset();
            for (long off = s; off + 1 < e; off += 2) {
                Address at = toAddr(off);
                int v;
                try { v = mem.getShort(at) & 0xFFFF; } catch (MemoryAccessException ex) { continue; }
                if (!want.contains(v)) continue;
                // отсечь совпадения внутри инструкции (их ловит проход по коду)
                if (listing.getInstructionContaining(at) != null) continue;
                dataHits.add(new long[]{v, off});
                StringBuilder ctx = new StringBuilder();
                ReferenceIterator ri = rm.getReferencesTo(at);
                int nref = 0;
                while (ri.hasNext() && nref < 8) {
                    Reference r = ri.next();
                    Address from = r.getFromAddress();
                    Function f = fm.getFunctionContaining(from);
                    ctx.append(from);
                    if (f != null) ctx.append("(").append(f.getEntryPoint()).append(")");
                    ctx.append(";");
                    nref++;
                }
                w.println(String.format("%04x,%08x,data,%s", v, off, ctx.toString()));
                nData++;
                for (int k = 0; k < DTC.length; k++) if (DTC[k] == v) perDtc[k]++;
            }
        }

        // ---- 2. код: immediate-операнды ----
        for (Function f : fm.getFunctions(true)) {
            for (Instruction ins : listing.getInstructions(f.getBody(), true)) {
                for (int i = 0; i < ins.getNumOperands(); i++) {
                    for (Object o : ins.getOpObjects(i)) {
                        if (!(o instanceof Scalar)) continue;
                        int sv = (int) (((Scalar) o).getUnsignedValue() & 0xFFFF);
                        if (!want.contains(sv)) continue;
                        w.println(String.format("%04x,%08x,imm,%s@%s", sv,
                                ins.getAddress().getOffset(), f.getEntryPoint(),
                                ins.toString().replace(",", " ")));
                        nImm++;
                    }
                }
            }
        }
        w.close();

        // ---- 3. кластеры близких DTC (окно 0x40) = кандидат в DTC-таблицу ----
        dataHits.sort((x, y) -> Long.compare(x[1], y[1]));
        PrintWriter tw = new PrintWriter(new FileWriter(new File(outDir, "immo_tables.csv")));
        tw.println("window_start,window_end,n_hits,distinct_dtc");
        int i = 0, nClusters = 0;
        while (i < dataHits.size()) {
            int j = i;
            Set<Integer> distinct = new HashSet<>();
            distinct.add((int) dataHits.get(i)[0]);
            while (j + 1 < dataHits.size()
                    && dataHits.get(j + 1)[1] - dataHits.get(j)[1] <= 0x40) {
                j++;
                distinct.add((int) dataHits.get(j)[0]);
            }
            int n = j - i + 1;
            if (n >= 2) {
                tw.println(String.format("%08x,%08x,%d,%d",
                        dataHits.get(i)[1], dataHits.get(j)[1], n, distinct.size()));
                println(String.format("VQ_IMMO table? %08x..%08x n=%d distinct=%d",
                        dataHits.get(i)[1], dataHits.get(j)[1], n, distinct.size()));
                nClusters++;
            }
            i = j + 1;
        }
        tw.close();

        StringBuilder sum = new StringBuilder("VQ_IMMO data=" + nData + " imm=" + nImm
                + " clusters=" + nClusters + " perDtc=");
        for (int k = 0; k < DTC.length; k++)
            sum.append(String.format("%04x:%d ", DTC[k], perDtc[k]));
        println(sum.toString());
        println("VQ_IMMO done -> immo_anchors.csv, immo_tables.csv");
    }
}
