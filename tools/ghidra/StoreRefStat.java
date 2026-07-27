// StoreRefStat.java - memory-access resolution asymmetry: count read and write
// instructions that received a reference to a concrete address and those that
// did not.
//
// A USES edge comes from a reference, which comes from constant propagation into
// a base register. An instruction without a reference is invisible in the graph.
// A cell may therefore have dozens of readers and no writer because the write
// address was not resolved, not because no write exists.
//
// Usage (headless): -postScript StoreRefStat.java
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.pcode.PcodeOp;
import ghidra.program.model.symbol.Reference;

public class StoreRefStat extends GhidraScript {
    static final long LO = 0xFFFE8000L;

    private boolean hasMemRef(Instruction ins) {
        for (Reference r : ins.getReferencesFrom()) {
            Address to = r.getToAddress();
            if (to != null && to.isMemoryAddress()
                    && (to.getOffset() & 0xFFFFFFFFL) >= LO) {
                return true;
            }
        }
        return false;
    }

    public void run() throws Exception {
        long ldTotal = 0, ldRef = 0, stTotal = 0, stRef = 0;
        for (Instruction ins : currentProgram.getListing().getInstructions(true)) {
            boolean load = false, store = false;
            for (PcodeOp op : ins.getPcode()) {
                if (op.getOpcode() == PcodeOp.LOAD) {
                    load = true;
                } else if (op.getOpcode() == PcodeOp.STORE) {
                    store = true;
                }
            }
            if (!load && !store) {
                continue;
            }
            boolean ref = hasMemRef(ins);
            if (store) {
                stTotal++;
                if (ref) {
                    stRef++;
                }
            } else {
                ldTotal++;
                if (ref) {
                    ldRef++;
                }
            }
        }
        println("VQ_STREF loads=" + ldTotal + " loads_with_ref=" + ldRef
                + " stores=" + stTotal + " stores_with_ref=" + stRef);
    }
}
