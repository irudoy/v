// RefsTo.java – кто ссылается на адрес: инструкция, её функция, тип ссылки.
// Для pool-слота getFunctionContaining бесполезен (слот - данные в литеральном
// пуле между функциями), поэтому владельца определяет ссылающаяся инструкция.
//
// Запуск (headless): -postScript RefsTo.java <addr_hex> [<addr_hex> ...]
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class RefsTo extends GhidraScript {
    public void run() throws Exception {
        for (String a : getScriptArgs()) {
            Address ad = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(Long.parseLong(a, 16));
            ReferenceIterator ri = currentProgram.getReferenceManager().getReferencesTo(ad);
            boolean any = false;
            while (ri.hasNext()) {
                Reference r = ri.next();
                Address from = r.getFromAddress();
                Function f = currentProgram.getFunctionManager().getFunctionContaining(from);
                println("VQ_REFSTO " + a + " <- " + from
                        + " func=" + (f == null ? "?" : f.getEntryPoint().toString())
                        + " size=" + (f == null ? "-" : String.valueOf(f.getBody().getNumAddresses()))
                        + " type=" + r.getReferenceType().getName());
                any = true;
            }
            if (!any) println("VQ_REFSTO " + a + " <- нет ссылок");
        }
    }
}
