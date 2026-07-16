// MapInventory.java — инвентаризация карт через общий interp-kernel.
// Уровни: (1) слоты со значением kernel (BE u32) -> (2) обёртки-интерполяторы
// (функции, ссылающиеся на слот) -> (3) все ссылки на вход обёртки = места
// вызова (аксессоры карт), с best-effort снятием r4/r5/r6 (table + оси) из
// register-setup перед вызовом.
//
// Запуск (headless): -postScript MapInventory.java <out_dir> <kernel_hex>
// Выход: map_inventory.csv (wrapper,slot,from,from_func,reftype,is_call,r4,r5,r6).
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
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;

public class MapInventory extends GhidraScript {

    static final long ROM_HI = 0x180000L;

    public void run() throws Exception {
        String[] a = getScriptArgs();
        String outDir = a[0];
        long kernel = Long.parseLong(a[1], 16);

        Memory mem = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        ReferenceManager rm = currentProgram.getReferenceManager();

        // 1. слоты: локации, содержащие значение kernel (BE u32)
        byte[] pat = new byte[]{
            (byte) ((kernel >> 24) & 0xff), (byte) ((kernel >> 16) & 0xff),
            (byte) ((kernel >> 8) & 0xff),  (byte) (kernel & 0xff)};
        byte[] mask = new byte[]{-1, -1, -1, -1};
        List<Address> slots = new ArrayList<>();
        Address start = currentProgram.getMinAddress();
        while (true) {
            Address found = mem.findBytes(start, pat, mask, true, monitor);
            if (found == null) break;
            slots.add(found);
            start = found.add(1);
        }

        // 2. обёртки: функции, ссылающиеся на слот
        Map<Function, Address> wrappers = new LinkedHashMap<>();
        for (Address slot : slots) {
            ReferenceIterator ri = rm.getReferencesTo(slot);
            while (ri.hasNext()) {
                Reference r = ri.next();
                Function wf = fm.getFunctionContaining(r.getFromAddress());
                if (wf != null) wrappers.putIfAbsent(wf, slot);
            }
        }

        // 3. места вызова каждой обёртки + best-effort r4/r5/r6
        PrintWriter w = new PrintWriter(new FileWriter(new File(outDir, "map_inventory.csv")));
        w.println("wrapper,slot,from,from_func,reftype,is_call,r4,r5,r6");
        int rows = 0;
        LinkedHashSet<String> sites = new LinkedHashSet<>();
        for (Map.Entry<Function, Address> e : wrappers.entrySet()) {
            Address wentry = e.getKey().getEntryPoint();
            ReferenceIterator ri = rm.getReferencesTo(wentry);
            while (ri.hasNext()) {
                Reference r = ri.next();
                Address from = r.getFromAddress();
                Function ff = fm.getFunctionContaining(from);
                boolean isCall = r.getReferenceType().isCall();
                long[] regs = {-1, -1, -1};
                try { regs = backtrack(listing, mem, from); } catch (Exception ex) { /* best-effort */ }
                w.println(String.format("%s,%s,%s,%s,%s,%b,%s,%s,%s",
                        wentry, e.getValue(), from,
                        ff == null ? "?" : ff.getEntryPoint().toString(),
                        r.getReferenceType().getName(), isCall,
                        hx(regs[0]), hx(regs[1]), hx(regs[2])));
                if (isCall) sites.add(from.toString());
                rows++;
            }
        }
        w.close();
        println("VQ_INV slots=" + slots.size() + " wrappers=" + wrappers.size()
                + " refrows=" + rows + " call_sites=" + sites.size());
    }

    String hx(long v) { return v == -1 ? "" : String.format("%08x", v); }

    // отойти назад до 14 инструкций, снять ближайший pc-relative load в r4/r5/r6
    long[] backtrack(Listing listing, Memory mem, Address site) {
        long[] out = {-1, -1, -1};
        Register r4 = currentProgram.getRegister("r4");
        Register r5 = currentProgram.getRegister("r5");
        Register r6 = currentProgram.getRegister("r6");
        Instruction ins = listing.getInstructionContaining(site);
        if (ins == null) return out;
        Instruction cur = listing.getInstructionBefore(ins.getAddress());
        for (int k = 0; k < 14 && cur != null; k++) {
            for (Object o : cur.getResultObjects()) {
                if (!(o instanceof Register)) continue;
                Register rg = (Register) o;
                int idx = rg.equals(r4) ? 0 : rg.equals(r5) ? 1 : rg.equals(r6) ? 2 : -1;
                if (idx >= 0 && out[idx] == -1) {
                    long v = nearestLoad(cur, mem);
                    out[idx] = (v == -1) ? -2 : v; // -2: записан не простым load
                }
            }
            if (out[0] != -1 && out[1] != -1 && out[2] != -1) break;
            cur = listing.getInstructionBefore(cur.getAddress());
        }
        for (int i = 0; i < 3; i++) if (out[i] == -2) out[i] = -1;
        return out;
    }

    // значение, загруженное pc-relative (ближайшая ref = literal pool, disp < 0x800)
    long nearestLoad(Instruction cur, Memory mem) {
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
}
