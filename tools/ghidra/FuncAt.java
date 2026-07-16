// FuncAt.java – функция, содержащая заданный адрес: точка входа, размер, границы.
// Нужен, чтобы относить pool-слоты к функциям по фактическим границам Ghidra,
// а не по расстоянию до ближайшей известной точки входа.
//
// Запуск (headless): -postScript FuncAt.java <addr_hex> [<addr_hex> ...]
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class FuncAt extends GhidraScript {
    public void run() throws Exception {
        for (String a : getScriptArgs()) {
            Address ad = currentProgram.getAddressFactory()
                    .getDefaultAddressSpace().getAddress(Long.parseLong(a, 16));
            Function f = currentProgram.getFunctionManager().getFunctionContaining(ad);
            if (f == null) {
                println("VQ_FUNCAT " + a + " -> нет функции");
            } else {
                println("VQ_FUNCAT " + a + " -> " + f.getEntryPoint() + " " + f.getName()
                        + " size=" + f.getBody().getNumAddresses()
                        + " [" + f.getBody().getMinAddress() + ".." + f.getBody().getMaxAddress() + "]");
            }
        }
    }
}
