// EmulateMapSwitchingLookupGate.java - compare lookup Overlay 06 and 07
// through the complete exact JK08A DFCO cut caller.
//
// The existing adapter harness stops at the stock wrapper entry. This gate
// starts at dfco_cut_request (0x4FBE2), executes both lookup calls, traverses
// the stock interpolation code, and returns through the real function
// epilogue. Overlay 07 must produce the same return value, protected register
// state, and complete RAM image as Overlay 06 because all five DFCO Entry
// tables are byte-identical at this hardware-isolation stage.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingLookupGate.java <overlay-06> <overlay-07>
//@category VQ
import ghidra.app.script.GhidraScript;
import ghidra.pcode.emu.PcodeEmulator;
import ghidra.pcode.emu.PcodeThread;
import ghidra.pcode.exec.PcodeExecutorState;
import ghidra.pcode.exec.PcodeExecutorStatePiece.Reason;
import ghidra.pcode.utils.Utils;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.Register;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

public class EmulateMapSwitchingLookupGate extends GhidraScript {

    static final int ROM_SIZE = 0x100000;
    static final long ENTRY = 0x0004FBE2L;
    static final long RETURN_SENTINEL = 0x00100000L;
    static final long RAM_START = 0xFFFF0000L;
    static final int RAM_SIZE = 0xC000;
    static final long STACK = 0xFFFF7F00L;
    static final long SELECTOR = 0xFFFF5D00L;
    static final long ADAPTER = 0x000D2300L;
    static final long HELPER = 0x000D2270L;
    static final long STOCK_WRAPPER = 0x00026388L;
    static final long STOCK_KERNEL = 0x00026A84L;
    static final int INSTRUCTION_LIMIT = 10000;

    static final String SOURCE_SHA =
            "990c7aff5dc62f33682900ff93b30b4888bd7171147689b1d43c58c13452d59f";
    static final String GATE_SHA =
            "95049dca436d74375954bf2e8586525573f9c7b864636144e9b5195130a8a6ba";

    static final int[] SELECTOR_VALUES = {
        0, 1, 2, 3, 4, 5, 0xFF,
    };

    static final String[] PROTECTED_REGISTERS = {
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15",
        "pr", "gbr", "mach", "macl",
    };

    static class Result {
        final byte[] ram;
        final Map<String, Long> registers;
        final long returnValue;
        final long sr;
        final int instructions;
        final int adapterVisits;
        final int helperVisits;
        final int wrapperVisits;
        final int kernelVisits;

        Result(
                byte[] ram,
                Map<String, Long> registers,
                long returnValue,
                long sr,
                int instructions,
                int adapterVisits,
                int helperVisits,
                int wrapperVisits,
                int kernelVisits) {
            this.ram = ram;
            this.registers = registers;
            this.returnValue = returnValue;
            this.sr = sr;
            this.instructions = instructions;
            this.adapterVisits = adapterVisits;
            this.helperVisits = helperVisits;
            this.wrapperVisits = wrapperVisits;
            this.kernelVisits = kernelVisits;
        }
    }

    Language language;
    AddressSpace space;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "need: <overlay-06-rom> <overlay-07-rom>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();

        byte[] source = readImage(Path.of(args[0]), SOURCE_SHA, "overlay-06");
        byte[] gate = readImage(Path.of(args[1]), GATE_SHA, "overlay-07");

        int instructions = 0;
        for (int selector : SELECTOR_VALUES) {
            Result baseline = execute(source, selector);
            Result candidate = execute(gate, selector);
            verifyBaseline(selector, baseline);
            verifyGate(selector, candidate);
            verifyEquivalent(selector, baseline, candidate);
            instructions += baseline.instructions + candidate.instructions;
        }

        println(String.format(
                Locale.ROOT,
                "VQ_LOOKUP_GATE_EMU status=PASS language=%s"
                + " source_sha256=%s gate_sha256=%s"
                + " cases=%d instructions=%d",
                languageId, SOURCE_SHA, GATE_SHA,
                SELECTOR_VALUES.length, instructions));
    }

    Result execute(byte[] image, int selector) throws Exception {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, 0, image);

        byte[] ram = new byte[RAM_SIZE];
        for (int index = 0; index < ram.length; index++) {
            ram[index] = (byte) ((index * 37 + 11) & 0xFF);
        }
        setMemory(shared, RAM_START, ram);
        setMemory(shared, SELECTOR, new byte[]{(byte) selector});

        PcodeThread<byte[]> thread = emulator.newThread(
                String.format(Locale.ROOT, "selector_%02x", selector));
        thread.overrideContextWithDefault();
        thread.reInitialize();
        thread.setCounter(toAddress(ENTRY));

        long seed = 0x10203040L;
        for (int number = 0; number <= 14; number++) {
            setRegister(thread, "r" + number, seed);
            seed += 0x01010101L;
        }
        setRegister(thread, "r15", STACK);
        setRegister(thread, "pr", RETURN_SENTINEL);
        setRegister(thread, "gbr", 0xFFFF83CCL);
        setRegister(thread, "mach", 0x2468ACE0L);
        setRegister(thread, "macl", 0xFDB97531L);
        setRegister(thread, "sr", 0x700000F1L);

        int instructions = 0;
        int adapterVisits = 0;
        int helperVisits = 0;
        int wrapperVisits = 0;
        int kernelVisits = 0;
        while (
                thread.getCounter().getOffset() != RETURN_SENTINEL
                && instructions < INSTRUCTION_LIMIT) {
            long pc = thread.getCounter().getOffset();
            if (pc == ADAPTER) {
                adapterVisits++;
            } else if (pc == HELPER) {
                helperVisits++;
            } else if (pc == STOCK_WRAPPER) {
                wrapperVisits++;
            } else if (pc == STOCK_KERNEL) {
                kernelVisits++;
            }
            thread.stepInstruction();
            instructions++;
        }
        if (thread.getCounter().getOffset() != RETURN_SENTINEL) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x did not return: pc=%s instructions=%d",
                    selector, thread.getCounter(), instructions));
        }

        Map<String, Long> registers = new LinkedHashMap<>();
        for (String name : PROTECTED_REGISTERS) {
            registers.put(name, readRegister(thread, name));
        }
        return new Result(
                readMemory(thread, RAM_START, RAM_SIZE),
                registers,
                readRegister(thread, "r0"),
                readRegister(thread, "sr"),
                instructions,
                adapterVisits,
                helperVisits,
                wrapperVisits,
                kernelVisits);
    }

    void verifyBaseline(int selector, Result result) {
        if (result.adapterVisits != 0 || result.helperVisits != 0) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x source entered injected lookup code",
                    selector));
        }
        if (result.wrapperVisits != 2 || result.kernelVisits != 2) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x source coverage wrapper=%d kernel=%d",
                    selector, result.wrapperVisits, result.kernelVisits));
        }
    }

    void verifyGate(int selector, Result result) {
        if (result.adapterVisits != 2 || result.helperVisits != 1) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x gate coverage adapter=%d helper=%d",
                    selector, result.adapterVisits, result.helperVisits));
        }
        if (result.wrapperVisits != 2 || result.kernelVisits != 2) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x gate coverage wrapper=%d kernel=%d",
                    selector, result.wrapperVisits, result.kernelVisits));
        }
    }

    void verifyEquivalent(int selector, Result source, Result gate) {
        if (source.returnValue != gate.returnValue) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x return differs %08x != %08x",
                    selector, source.returnValue, gate.returnValue));
        }
        for (String name : PROTECTED_REGISTERS) {
            long expected = source.registers.get(name);
            long actual = gate.registers.get(name);
            if (expected != actual) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "selector=%02x %s differs %08x != %08x",
                        selector, name, expected, actual));
            }
        }
        if ((source.sr & 0xFFFFFFFEL) != (gate.sr & 0xFFFFFFFEL)) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x protected SR differs %08x != %08x",
                    selector, source.sr, gate.sr));
        }
        if (!Arrays.equals(source.ram, gate.ram)) {
            for (int index = 0; index < source.ram.length; index++) {
                if (source.ram[index] != gate.ram[index]) {
                    throw new IllegalStateException(String.format(
                            Locale.ROOT,
                            "selector=%02x RAM differs at %08x: %02x != %02x",
                            selector, RAM_START + index,
                            source.ram[index] & 0xFF,
                            gate.ram[index] & 0xFF));
                }
            }
        }
    }

    byte[] readImage(Path path, String expectedSha, String name)
            throws Exception {
        byte[] bytes = Files.readAllBytes(path);
        if (bytes.length != ROM_SIZE) {
            throw new IllegalArgumentException(
                    name + " has " + bytes.length + " bytes");
        }
        String digest = sha256(bytes);
        if (!digest.equals(expectedSha)) {
            throw new IllegalArgumentException(
                    name + " SHA-256 is " + digest
                    + ", expected " + expectedSha);
        }
        return bytes;
    }

    void setMemory(
            PcodeExecutorState<byte[]> state, long address, byte[] bytes) {
        state.setVar(space, address, bytes.length, true, bytes);
    }

    byte[] readMemory(
            PcodeThread<byte[]> thread, long address, int size) {
        return thread.getState().getVar(
                space, address, size, true, Reason.INSPECT);
    }

    void setRegister(
            PcodeThread<byte[]> thread, String name, long value) {
        Register register = requireRegister(name);
        thread.getState().setVar(
                register,
                Utils.longToBytes(
                        value,
                        register.getNumBytes(),
                        language.isBigEndian()));
    }

    long readRegister(PcodeThread<byte[]> thread, String name) {
        Register register = requireRegister(name);
        byte[] bytes = thread.getState().getVar(register, Reason.INSPECT);
        return Utils.bytesToLong(
                bytes, register.getNumBytes(), language.isBigEndian())
                & 0xFFFFFFFFL;
    }

    Register requireRegister(String name) {
        Register register = language.getRegister(name);
        if (register == null) {
            register = language.getRegister(name.toUpperCase(Locale.ROOT));
        }
        if (register == null) {
            throw new IllegalArgumentException("unknown register " + name);
        }
        return register;
    }

    Address toAddress(long value) {
        return space.getAddress(value);
    }

    static String sha256(byte[] data) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(data);
        StringBuilder result = new StringBuilder(digest.length * 2);
        for (byte value : digest) {
            result.append(String.format(
                    Locale.ROOT, "%02x", value & 0xFF));
        }
        return result.toString();
    }
}
