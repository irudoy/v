// ImmoConfirm.java -- headless-подтверждение immo-контура HR-дампа (SH-2).
// Декомпилирует immo_registration и immo_lock_setter, печатает их callers/callees
// и listing патч-сайтов always-ID-OK с байтами. Адреса передаются через
// -scriptArgs "<reg_entry> <lock_entry> <site1> <site2> ...".
// Прогон: headless-analyze.sh <projdir> <proj> -process <prog> -noanalysis
//           -scriptPath <dir> -postScript ImmoConfirm.java <scriptArgs...>
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.mem.Memory;

public class ImmoConfirm extends GhidraScript {
    DecompInterface dec;

    void decompile(String label, Address entry) throws Exception {
        println("\n==================== " + label + " ====================");
        // SH GBR-код часто не дизассемблирован авто-анализом -> форсируем
        if (getInstructionAt(entry) == null) {
            println("  (нет инструкции @ " + entry + " -> disassemble)");
            disassemble(entry);
        }
        Function f = getFunctionContaining(entry);
        if (f == null) {
            println("  (нет функции -> createFunction @ " + entry + ")");
            f = createFunction(entry, null);
        }
        if (f == null) { println("  НЕ удалось создать функцию @ " + entry); return; }
        println("  func: " + f.getName() + "  entry=" + f.getEntryPoint()
                + "  size=" + f.getBody().getNumAddresses() + "B");
        // callers
        println("  --- callers (кто вызывает) ---");
        Reference[] refs = getReferencesTo(f.getEntryPoint());
        int nc = 0;
        for (Reference r : refs) {
            if (r.getReferenceType().isCall() || r.getReferenceType().isFlow()) {
                Function cf = getFunctionContaining(r.getFromAddress());
                println("    <- " + r.getFromAddress() + (cf != null ? "  " + cf.getName() : "")
                        + "  [" + r.getReferenceType() + "]");
                nc++;
            }
        }
        if (nc == 0) println("    (нет прямых call-ссылок; возможно хвост таблицы/косвенный)");
        // decompile
        DecompileResults dr = dec.decompileFunction(f, 60, monitor);
        if (dr != null && dr.decompileCompleted()) {
            println("  --- C-псевдокод ---");
            String c = dr.getDecompiledFunction().getC();
            for (String ln : c.split("\n")) println("    " + ln);
        } else {
            println("  (декомпиляция не удалась)");
        }
    }

    void site(Address a) throws Exception {
        if (getInstructionAt(a) == null) disassemble(a);
        Instruction ins = getInstructionAt(a);
        Memory mem = currentProgram.getMemory();
        byte[] b = new byte[2];
        try { mem.getBytes(a, b); } catch (Exception e) {}
        String hex = String.format("%02x %02x", b[0] & 0xff, b[1] & 0xff);
        println(String.format("  @%s  %s  %s", a, hex, ins != null ? ins.toString() : "(нет инструкции)"));
    }

    @Override
    protected void run() throws Exception {
        String[] a = getScriptArgs();
        dec = new DecompInterface();
        dec.openProgram(currentProgram);

        Address regE = toAddr(Long.parseLong(a[0], 16));
        Address lockE = toAddr(Long.parseLong(a[1], 16));
        decompile("immo_registration (FUN_" + a[0] + ")", regE);
        decompile("immo_lock_setter (FUN_" + a[1] + ")", lockE);

        println("\n==================== ПАТЧ-САЙТЫ (listing + байты) ====================");
        for (int i = 2; i < a.length; i++) {
            site(toAddr(Long.parseLong(a[i], 16)));
        }
        dec.dispose();
        println("\n[ImmoConfirm done]");
    }
}
