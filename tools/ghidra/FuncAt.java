// FuncAt.java - report the function containing each selected address, including
// entry point, size, and bounds. Associates pool slots with functions using
// actual Ghidra boundaries rather than distance to the nearest known entry.
//
// Usage (headless): -postScript FuncAt.java <addr_hex> [<addr_hex> ...]
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
                println("VQ_FUNCAT " + a + " -> no function");
            } else {
                println("VQ_FUNCAT " + a + " -> " + f.getEntryPoint() + " " + f.getName()
                        + " size=" + f.getBody().getNumAddresses()
                        + " [" + f.getBody().getMinAddress() + ".." + f.getBody().getMaxAddress() + "]");
            }
        }
    }
}
