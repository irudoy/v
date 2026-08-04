// EmulateMapSwitchingSelectorInit.java - compare the successful transparent
// startup-trampoline readback with the minimal selector-initialization gate.
//
// Direct callees of FUN_0002C648 are replaced with identical deterministic
// return-zero stubs. Both runs execute the complete stock initializer. The gate
// must preserve final register state and all RAM except for changing the single
// reserved selector byte at 0xFFFF5D00 from the sentinel to Map 1.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingSelectorInit.java <trampoline-rom> <gate-rom>
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
import java.util.Locale;

public class EmulateMapSwitchingSelectorInit extends GhidraScript {

    static final int ROM_SIZE = 0x100000;
    static final String SOURCE_SHA256 =
        "6b1df699f614151a7ddd09595671de021b7131d5524b16d1f27a9fed888abc55";
    static final String GATE_SHA256 =
        "7dcb43b2181c030bde772999b674afb72a8cd196e93a0aae3fecf90069ed62d3";
    static final long STARTUP_THUNK = 0x00027CE4L;
    static final long STOCK_INITIALIZER = 0x0002C648L;
    static final long WRAPPER = 0x000D22A0L;
    static final long WRAPPER_AFTER_INITIALIZER = 0x000D22AEL;
    static final long RETURN_ADDRESS = 0x000D4000L;
    static final long STACK_TOP = 0xFFFF7FFCL;
    static final long ENTRY_SR = 0x000000F0L;
    static final long ENTRY_GBR = 0xFFFF9F28L;
    static final long RAM_START = 0xFFFF0000L;
    static final int RAM_SIZE = 0xC000;
    static final long SELECTOR_STATE = 0xFFFF5D00L;
    static final int SELECTOR_SENTINEL = 0xA5;
    static final int MAP_1_INDEX = 0;

    static final long[] INITIALIZER_CALLEES = {
        0x00028668L,
        0x000263D8L,
        0x000BCED0L,
        0x000BD14AL,
        0x000B5760L,
        0x0007F30CL,
        0x000593ACL,
        0x000BCD44L,
        0x00056A7AL,
        0x0002C626L,
        0x0002C5C0L,
        0x0002C4F8L,
        0x0002C59CL,
        0x00026370L,
    };

    // mov #0,r0; rts; nop
    static final byte[] RETURN_ZERO_STUB = {
        (byte) 0xE0, 0x00, 0x00, 0x0B, 0x00, 0x09,
    };

    static final String[] RESULT_REGISTERS = {
        "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7",
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15",
        "pr", "gbr", "sr", "mach", "macl",
    };

    static class Result {
        final int instructions;
        final long minSp;
        final boolean sawWrapper;
        final boolean sawInitializer;
        final long[] registers;
        final byte[] ram;

        Result(
                int instructions,
                long minSp,
                boolean sawWrapper,
                boolean sawInitializer,
                long[] registers,
                byte[] ram) {
            this.instructions = instructions;
            this.minSp = minSp;
            this.sawWrapper = sawWrapper;
            this.sawInitializer = sawInitializer;
            this.registers = registers;
            this.ram = ram;
        }
    }

    Language language;
    AddressSpace space;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "need: <trampoline-rom> <gate-rom>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        byte[] sourceImage = readImage(args[0]);
        byte[] gateImage = readImage(args[1]);
        requireSha256(sourceImage, SOURCE_SHA256, "trampoline source");
        requireSha256(gateImage, GATE_SHA256, "selector-init gate");

        Result source = execute(sourceImage);
        Result gate = execute(gateImage);
        if (!source.sawWrapper || !gate.sawWrapper) {
            throw new IllegalStateException(
                    "0xD22A0 was not reached in both runs");
        }
        if (!source.sawInitializer || !gate.sawInitializer) {
            throw new IllegalStateException(
                    "stock initializer was not reached in both runs");
        }
        // The selector wrapper has ten physical instructions. Ghidra executes
        // each delayed control transfer with its delay-slot NOP in one step.
        // Relative to the three-instruction transparent trampoline, it adds six
        // p-code steps.
        if (gate.instructions != source.instructions + 6) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "p-code step delta is %d, expected 6",
                    gate.instructions - source.instructions));
        }
        verifyRegisters(source, gate);
        verifyRam(source, gate);
        long expectedGateMinSp = (source.minSp - 4) & 0xFFFFFFFFL;
        if (gate.minSp != expectedGateMinSp) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "minimum SP differs unexpectedly: source=%08x gate=%08x"
                    + " expected_gate=%08x",
                    source.minSp, gate.minSp, expectedGateMinSp));
        }

        println(String.format(
                Locale.ROOT,
                "VQ_SELECTOR_INIT_EMU status=PASS language=%s"
                + " source_sha256=%s gate_sha256=%s"
                + " source_instructions=%d gate_instructions=%d delta=%d"
                + " source_min_sp=%08x gate_min_sp=%08x"
                + " selector=%08x:%02x->%02x initializer_callees=%d",
                languageId,
                sha256(sourceImage),
                sha256(gateImage),
                source.instructions,
                gate.instructions,
                gate.instructions - source.instructions,
                source.minSp,
                gate.minSp,
                SELECTOR_STATE,
                SELECTOR_SENTINEL,
                MAP_1_INDEX,
                INITIALIZER_CALLEES.length));
    }

    Result execute(byte[] image) throws Exception {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, 0, image);
        setMemory(shared, RAM_START, new byte[RAM_SIZE]);
        setMemory(
                shared,
                SELECTOR_STATE,
                new byte[]{(byte) SELECTOR_SENTINEL});
        for (long callee : INITIALIZER_CALLEES) {
            setMemory(shared, callee, RETURN_ZERO_STUB);
        }

        PcodeThread<byte[]> thread = emulator.newThread("startup");
        thread.overrideContextWithDefault();
        thread.reInitialize();
        thread.setCounter(toAddress(STARTUP_THUNK));
        setRegister(thread, "sr", ENTRY_SR);
        setRegister(thread, "pr", RETURN_ADDRESS);
        setRegister(thread, "r15", STACK_TOP);
        setRegister(thread, "gbr", ENTRY_GBR);
        for (int number = 0; number <= 7; number++) {
            setRegister(thread, "r" + number, 0);
        }
        long seed = 0x11223344L;
        for (int number = 8; number <= 14; number++) {
            setRegister(thread, "r" + number, seed);
            seed += 0x01010101L;
        }
        setRegister(thread, "mach", 0x89ABCDEFL);
        setRegister(thread, "macl", 0x76543210L);

        int instructions = 0;
        int limit = 100000;
        long minSp = STACK_TOP;
        boolean sawWrapper = false;
        boolean sawInitializer = false;
        while (
                thread.getCounter().getOffset() != RETURN_ADDRESS
                && instructions < limit) {
            long pc = thread.getCounter().getOffset();
            sawWrapper |= pc == WRAPPER;
            sawInitializer |= pc == STOCK_INITIALIZER;
            thread.stepInstruction();
            instructions++;
            minSp = unsignedMin(minSp, readRegister(thread, "r15"));
        }
        if (thread.getCounter().getOffset() != RETURN_ADDRESS) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "startup did not return after %d instructions; pc=%s",
                    instructions, thread.getCounter()));
        }

        long[] registers = new long[RESULT_REGISTERS.length];
        for (int index = 0; index < RESULT_REGISTERS.length; index++) {
            registers[index] = readRegister(
                    thread, RESULT_REGISTERS[index]);
        }
        byte[] ram = readMemory(thread, RAM_START, RAM_SIZE);
        return new Result(
                instructions,
                minSp,
                sawWrapper,
                sawInitializer,
                registers,
                ram);
    }

    void verifyRegisters(Result source, Result gate) {
        for (int index = 0; index < RESULT_REGISTERS.length; index++) {
            if (source.registers[index] != gate.registers[index]) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "%s differs: source=%08x gate=%08x",
                        RESULT_REGISTERS[index],
                        source.registers[index],
                        gate.registers[index]));
            }
        }
    }

    void verifyRam(Result source, Result gate) {
        int selectorOffset = (int) (SELECTOR_STATE - RAM_START);
        for (int offset = 0; offset < RAM_SIZE; offset++) {
            long address = RAM_START + offset;
            int sourceValue = source.ram[offset] & 0xFF;
            int gateValue = gate.ram[offset] & 0xFF;
            if (offset == selectorOffset) {
                if (
                        sourceValue != SELECTOR_SENTINEL
                        || gateValue != MAP_1_INDEX) {
                    throw new IllegalStateException(String.format(
                            Locale.ROOT,
                            "selector state differs unexpectedly:"
                            + " source=%02x gate=%02x",
                            sourceValue, gateValue));
                }
            }
            else if (address >= gate.minSp && address < STACK_TOP) {
                continue;
            }
            else if (sourceValue != gateValue) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "RAM differs outside selector at %08x:"
                        + " source=%02x gate=%02x",
                        RAM_START + offset, sourceValue, gateValue));
            }
        }
        verifyShiftedStack(source, gate);
    }

    void verifyShiftedStack(Result source, Result gate) {
        int returnAddressSubstitutions = 0;
        for (long address = source.minSp; address < STACK_TOP; address += 4) {
            int sourceOffset = (int) (address - RAM_START);
            int gateOffset = (int) (address - 4 - RAM_START);
            long sourceValue = readBigEndianLong(source.ram, sourceOffset);
            long gateValue = readBigEndianLong(gate.ram, gateOffset);
            if (sourceValue != gateValue) {
                if (
                        sourceValue == RETURN_ADDRESS
                        && gateValue == WRAPPER_AFTER_INITIALIZER) {
                    returnAddressSubstitutions++;
                    continue;
                }
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "shifted stack differs: source[%08x]=%08x"
                        + " gate[%08x]=%08x",
                        address,
                        sourceValue,
                        address - 4,
                        gateValue));
            }
        }
        if (returnAddressSubstitutions != 1) {
            throw new IllegalStateException(
                    "shifted stack has " + returnAddressSubstitutions
                    + " initializer return-address substitutions, expected 1");
        }
        byte[] expectedSavedPr = {
            0x00, 0x0D, 0x40, 0x00,
        };
        int savedPrOffset = (int) (STACK_TOP - 4 - RAM_START);
        for (int index = 0; index < expectedSavedPr.length; index++) {
            int actual = gate.ram[savedPrOffset + index] & 0xFF;
            int expected = expectedSavedPr[index] & 0xFF;
            if (actual != expected) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "saved PR differs at %08x: actual=%02x expected=%02x",
                        STACK_TOP - 4 + index,
                        actual,
                        expected));
            }
        }
    }

    static long readBigEndianLong(byte[] data, int offset) {
        return ((long) (data[offset] & 0xFF) << 24)
                | ((long) (data[offset + 1] & 0xFF) << 16)
                | ((long) (data[offset + 2] & 0xFF) << 8)
                | (long) (data[offset + 3] & 0xFF);
    }

    static long unsignedMin(long left, long right) {
        return Long.compareUnsigned(left, right) <= 0 ? left : right;
    }

    byte[] readImage(String path) throws Exception {
        byte[] image = Files.readAllBytes(Path.of(path));
        if (image.length != ROM_SIZE) {
            throw new IllegalArgumentException(
                    path + ": ROM length is " + image.length
                    + ", expected " + ROM_SIZE);
        }
        return image;
    }

    void setMemory(
            PcodeExecutorState<byte[]> state,
            long address,
            byte[] bytes) {
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

    static void requireSha256(
            byte[] data, String expected, String context) throws Exception {
        String actual = sha256(data);
        if (!actual.equals(expected)) {
            throw new IllegalArgumentException(
                    context + " SHA-256 is " + actual
                    + ", expected " + expected);
        }
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
