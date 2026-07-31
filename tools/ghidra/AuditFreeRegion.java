// AuditFreeRegion.java - verify that an inclusive ROM interval is an unclaimed
// fill region: every byte matches the requested value and Ghidra contains no
// instruction, defined data, function body, or inbound reference in the range.
//
// Usage (headless):
//   -postScript AuditFreeRegion.java <lo_hex> <hi_hex> [fill_hex]
//@category VQ
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.util.ArrayList;
import java.util.List;

public class AuditFreeRegion extends GhidraScript {

    static final int MAX_DETAILS = 20;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2 || args.length > 3) {
            println("VQ_FREE need: <lo_hex> <hi_hex> [fill_hex]");
            return;
        }

        Address lo = toAddress(args[0]);
        Address hi = toAddress(args[1]);
        if (lo.compareTo(hi) > 0) {
            throw new IllegalArgumentException("range begins after it ends");
        }
        int fill = args.length == 3
                ? Integer.parseUnsignedInt(args[2], 16)
                : 0xFF;
        if (fill > 0xFF) {
            throw new IllegalArgumentException("fill is not a byte");
        }

        Memory memory = currentProgram.getMemory();
        Listing listing = currentProgram.getListing();
        AddressSet range = new AddressSet(lo, hi);
        List<String> details = new ArrayList<>();
        long byteCount = 0;
        long badBytes = 0;
        long references = 0;

        Address current = lo;
        while (current != null && current.compareTo(hi) <= 0) {
            byteCount++;
            int actual = memory.getByte(current) & 0xFF;
            if (actual != fill) {
                badBytes++;
                addDetail(details, String.format(
                        "byte %s=%02x expected=%02x", current, actual, fill));
            }
            ReferenceIterator refs = currentProgram.getReferenceManager()
                    .getReferencesTo(current);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                references++;
                addDetail(details, "reference " + ref.getFromAddress()
                        + " -> " + current + " "
                        + ref.getReferenceType().getName());
            }
            current = current.next();
        }

        long instructions = 0;
        InstructionIterator instructionIterator =
                listing.getInstructions(range, true);
        while (instructionIterator.hasNext()) {
            Instruction instruction = instructionIterator.next();
            instructions++;
            addDetail(details, "instruction " + instruction.getAddress());
        }

        long definedData = 0;
        DataIterator dataIterator = listing.getDefinedData(range, true);
        while (dataIterator.hasNext()) {
            Data data = dataIterator.next();
            definedData++;
            addDetail(details, "defined-data " + data.getAddress()
                    + " length=" + data.getLength());
        }

        long functions = 0;
        FunctionIterator functionIterator =
                currentProgram.getFunctionManager().getFunctions(true);
        while (functionIterator.hasNext()) {
            Function function = functionIterator.next();
            if (!function.getBody().intersect(range).isEmpty()) {
                functions++;
                addDetail(details, "function " + function.getEntryPoint()
                        + " " + function.getName());
            }
        }

        boolean pass = badBytes == 0 && instructions == 0 && definedData == 0
                && functions == 0 && references == 0;
        println(String.format(
                "VQ_FREE status=%s range=%s..%s bytes=%d fill=%02x bad_bytes=%d"
                + " instructions=%d data=%d functions=%d references=%d",
                pass ? "PASS" : "FAIL", lo, hi, byteCount, fill, badBytes,
                instructions, definedData, functions, references));
        for (String detail : details) {
            println("VQ_FREE detail " + detail);
        }

        if (!pass) {
            throw new IllegalStateException("region is not free");
        }
    }

    Address toAddress(String text) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace()
                .getAddress(Long.parseUnsignedLong(text, 16));
    }

    void addDetail(List<String> details, String detail) {
        if (details.size() < MAX_DETAILS) {
            details.add(detail);
        }
    }
}
