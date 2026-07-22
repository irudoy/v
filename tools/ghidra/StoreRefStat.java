// StoreRefStat.java – асимметрия резолва обращений к памяти: сколько инструкций-чтений и
// инструкций-записей получили ссылку на конкретный адрес, а сколько остались без неё.
//
// Ребро USES строится из ссылки, а ссылку создаёт распространение константы в базовый
// регистр. Инструкция без ссылки в графе не видна вовсе, поэтому ячейка может иметь
// десятки читателей и ни одного писателя не потому, что её не пишут, а потому, что
// адрес записи не свернулся.
//
// Запуск (headless): -postScript StoreRefStat.java
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
