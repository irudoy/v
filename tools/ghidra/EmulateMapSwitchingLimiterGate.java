// EmulateMapSwitchingLimiterGate.java - differentially execute the successful
// selector-init readback and cumulative Map 1 limiter-shadow overlays.
//
// Direct callees of FUN_0002C648 are replaced with identical deterministic
// return-zero stubs. Both images execute the complete stock initializer. The
// Overlay 1 installs inactive payload and storage. Overlay 2 executes the final
// startup wrapper and atomic limiter commit. Overlays 3 through 5 activate the
// fuel, throttle-cluster, and throttle-scalar hooks one at a time. Every stage
// must retain its exact expected startup behavior and protected ABI.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingLimiterGate.java <selector-rom> <gate-rom>
//   -postScript EmulateMapSwitchingLimiterGate.java <selector-rom> \
//       <overlay-01> <overlay-02> <overlay-03> <overlay-04> <overlay-05>
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
import java.util.Locale;

public class EmulateMapSwitchingLimiterGate extends GhidraScript {

    static final int ROM_SIZE = 0x100000;
    static final String SOURCE_SHA256 =
        "7dcb43b2181c030bde772999b674afb72a8cd196e93a0aae3fecf90069ed62d3";
    static final String[] OVERLAY_SHA256 = {
        "9bb1704f93a6050593abbf30b450cc1b75bc4d141ed4455b7528148de69f56c4",
        "135512525ed64b7728348a2b8859e9a7b607f931f57f6a7951e0d2d7dc847da5",
        "22f824be2e9ca941b42760de27accc7cd1c7365e23a0b19eda29387fd1dd196c",
        "3aa4bce11eb9030dc688c04744170e8aee61b1b9f8e3dd99a57a4d5ca1f626db",
        "1833922fc7d3428ed9f9998a99281d4c02b66c027cc39f7620aa3a79d541964a",
    };

    static final long STARTUP_THUNK = 0x00027CE4L;
    static final long STOCK_INITIALIZER = 0x0002C648L;
    static final long STARTUP_WRAPPER = 0x000D22A0L;
    static final long LIMITER_COMMIT = 0x000D3660L;
    static final long RETURN_ADDRESS = 0x000D4000L;
    static final long STACK_TOP = 0xFFFF7FFCL;
    static final long ENTRY_SR = 0x000000F0L;
    static final long ENTRY_GBR = 0xFFFF9F28L;

    static final long RAM_START = 0xFFFF0000L;
    static final int RAM_SIZE = 0xC000;
    static final long SELECTOR_STATE = 0xFFFF5D00L;
    static final long FUEL_SHADOW = 0xFFFF5D10L;
    static final long THROTTLE_SHADOW = 0xFFFF5D20L;
    static final long THROTTLE_RUNTIME = 0xFFFF1796L;
    static final int RESERVATION_SIZE = 0x3C;

    static final long FUEL_MAP_1 = 0x0000934EL;
    static final int FUEL_MAP_SIZE = 8;
    static final long FUEL_STOCK_TAIL = 0x00009356L;
    static final int FUEL_TAIL_SIZE = 4;
    static final long THROTTLE_CLUSTER = 0x00009424L;
    static final int THROTTLE_CLUSTER_SIZE = 28;
    static final int THROTTLE_SELECTED_OFFSET = 8;

    static final long[] FUEL_COPIES = {
        0x000D3500L, 0x000D3508L, 0x000D3510L, 0x000D3518L,
    };
    static final long[] THROTTLE_COPIES = {
        0x000D3520L, 0x000D3522L, 0x000D3524L, 0x000D3526L,
    };
    static final long FUEL_POINTER_TABLE = 0x000D35B8L;
    static final long THROTTLE_POINTER_TABLE = 0x000D35CCL;

    static final long[] LIMITER_HOOK_ADDRESSES = {
        0x0004F468L, 0x00075964L, 0x00077BACL,
    };
    static final long[] SOURCE_LIMITER_HOOK_VALUES = {
        0x0000934EL, 0x00009424L, 0x0000942CL,
    };
    static final long[] GATE_LIMITER_HOOK_VALUES = {
        0xFFFF5D10L, 0xFFFF5D20L, 0xFFFF5D28L,
    };

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
    static final String[] PROTECTED_REGISTERS = {
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15",
        "pr", "gbr", "sr", "mach", "macl",
    };

    static class Result {
        final int instructions;
        final long minSp;
        final boolean sawWrapper;
        final boolean sawInitializer;
        final boolean sawLimiter;
        final long[] registers;
        final byte[] ram;

        Result(
                int instructions,
                long minSp,
                boolean sawWrapper,
                boolean sawInitializer,
                boolean sawLimiter,
                long[] registers,
                byte[] ram) {
            this.instructions = instructions;
            this.minSp = minSp;
            this.sawWrapper = sawWrapper;
            this.sawInitializer = sawInitializer;
            this.sawLimiter = sawLimiter;
            this.registers = registers;
            this.ram = ram;
        }
    }

    Language language;
    AddressSpace space;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2 && args.length != 6) {
            throw new IllegalArgumentException(
                    "need: <selector-rom> <gate-rom> or <selector-rom>"
                    + " <overlay-01> <overlay-02> <overlay-03>"
                    + " <overlay-04> <overlay-05>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();

        byte[] sourceImage = readImage(args[0]);
        requireSha256(sourceImage, SOURCE_SHA256, "selector-init source");
        Result source = execute(sourceImage);
        if (!source.sawWrapper || !source.sawInitializer) {
            throw new IllegalStateException(
                    "source startup path was not reached");
        }
        if (source.sawLimiter) {
            throw new IllegalStateException(
                    "source unexpectedly reached limiter commit");
        }

        int firstStage = args.length == 2 ? 5 : 1;
        int overlayCount = args.length == 2 ? 1 : 5;
        for (int index = 0; index < overlayCount; index++) {
            int stage = firstStage + index;
            byte[] overlayImage = readImage(args[index + 1]);
            requireSha256(
                    overlayImage,
                    OVERLAY_SHA256[stage - 1],
                    "limiter overlay " + stage);
            verifyImageContract(sourceImage, overlayImage, stage);

            Result overlay = execute(overlayImage);
            verifyExecution(
                    sourceImage,
                    overlayImage,
                    source,
                    overlay,
                    stage);
            println(String.format(
                    Locale.ROOT,
                    "VQ_LIMITER_OVERLAY_STAGE status=PASS stage=%02d"
                    + " sha256=%s source_instructions=%d"
                    + " overlay_instructions=%d delta=%d"
                    + " source_min_sp=%08x overlay_min_sp=%08x"
                    + " limiter_hooks=%d",
                    stage,
                    sha256(overlayImage),
                    source.instructions,
                    overlay.instructions,
                    overlay.instructions - source.instructions,
                    source.minSp,
                    overlay.minSp,
                    activeHookCount(stage)));
        }

        println(String.format(
                Locale.ROOT,
                "VQ_LIMITER_GATE_EMU status=PASS language=%s"
                + " source_sha256=%s overlays=%d"
                + " selector_bytes=8 fuel_shadow_bytes=12"
                + " throttle_shadow_bytes=28 initializer_callees=%d",
                languageId,
                sha256(sourceImage),
                overlayCount,
                INITIALIZER_CALLEES.length));
    }

    void verifyExecution(
            byte[] sourceImage,
            byte[] overlayImage,
            Result source,
            Result overlay,
            int stage) {
        if (!overlay.sawWrapper || !overlay.sawInitializer) {
            throw new IllegalStateException(
                    "overlay startup path was not reached at stage " + stage);
        }
        boolean limiterExpected = stage >= 2;
        if (overlay.sawLimiter != limiterExpected) {
            throw new IllegalStateException(
                    "limiter reachability differs at stage " + stage);
        }
        int expectedDelta = limiterExpected ? 107 : 0;
        if (overlay.instructions != source.instructions + expectedDelta) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "stage %d p-code step delta is %d, expected %d",
                    stage,
                    overlay.instructions - source.instructions,
                    expectedDelta));
        }
        if (source.minSp != overlay.minSp) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "stage %d minimum SP differs: source=%08x overlay=%08x",
                    stage,
                    source.minSp,
                    overlay.minSp));
        }
        if (stage == 1) {
            verifyAllRegisters(source, overlay);
        } else {
            verifyProtectedRegisters(source, overlay);
        }
        verifyRam(sourceImage, overlayImage, source, overlay, stage);
    }

    static int activeHookCount(int stage) {
        return Math.max(0, stage - 2);
    }

    Result execute(byte[] image) throws Exception {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, 0, image);
        setMemory(shared, RAM_START, new byte[RAM_SIZE]);
        setMemory(shared, SELECTOR_STATE, reservationSentinel());
        for (long callee : INITIALIZER_CALLEES) {
            setMemory(shared, callee, RETURN_ZERO_STUB);
        }

        PcodeThread<byte[]> thread = emulator.newThread("limiter-gate");
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
        boolean sawLimiter = false;
        while (
                thread.getCounter().getOffset() != RETURN_ADDRESS
                && instructions < limit) {
            long pc = thread.getCounter().getOffset();
            sawWrapper |= pc == STARTUP_WRAPPER;
            sawInitializer |= pc == STOCK_INITIALIZER;
            sawLimiter |= pc == LIMITER_COMMIT;
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
                sawLimiter,
                registers,
                ram);
    }

    void verifyImageContract(byte[] source, byte[] overlay, int stage) {
        int activeHooks = activeHookCount(stage);
        for (int index = 0; index < LIMITER_HOOK_ADDRESSES.length; index++) {
            long address = LIMITER_HOOK_ADDRESSES[index];
            requireImageLong(
                    source,
                    address,
                    SOURCE_LIMITER_HOOK_VALUES[index],
                    "source limiter hook");
            requireImageLong(
                    overlay,
                    address,
                    index < activeHooks
                            ? GATE_LIMITER_HOOK_VALUES[index]
                            : SOURCE_LIMITER_HOOK_VALUES[index],
                    "overlay limiter hook");
        }

        byte[] fuelMap1 = Arrays.copyOfRange(
                overlay,
                (int) FUEL_MAP_1,
                (int) FUEL_MAP_1 + FUEL_MAP_SIZE);
        for (long address : FUEL_COPIES) {
            byte[] copy = Arrays.copyOfRange(
                    overlay,
                    (int) address,
                    (int) address + FUEL_MAP_SIZE);
            if (!Arrays.equals(copy, fuelMap1)) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "fuel Map 1 copy differs at %08x", address));
            }
        }
        byte[] throttleMap1 = Arrays.copyOfRange(
                overlay,
                (int) THROTTLE_CLUSTER + THROTTLE_SELECTED_OFFSET,
                (int) THROTTLE_CLUSTER + THROTTLE_SELECTED_OFFSET + 2);
        for (long address : THROTTLE_COPIES) {
            byte[] copy = Arrays.copyOfRange(
                    overlay, (int) address, (int) address + 2);
            if (!Arrays.equals(copy, throttleMap1)) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "throttle Map 1 copy differs at %08x", address));
            }
        }

        long[] expectedFuelPointers = {
            FUEL_MAP_1,
            FUEL_COPIES[0],
            FUEL_COPIES[1],
            FUEL_COPIES[2],
            FUEL_COPIES[3],
        };
        long[] expectedThrottlePointers = {
            THROTTLE_CLUSTER + THROTTLE_SELECTED_OFFSET,
            THROTTLE_COPIES[0],
            THROTTLE_COPIES[1],
            THROTTLE_COPIES[2],
            THROTTLE_COPIES[3],
        };
        requirePointerTable(
                overlay,
                FUEL_POINTER_TABLE,
                expectedFuelPointers,
                "fuel");
        requirePointerTable(
                overlay,
                THROTTLE_POINTER_TABLE,
                expectedThrottlePointers,
                "throttle");
    }

    void verifyAllRegisters(Result source, Result overlay) {
        for (int index = 0; index < RESULT_REGISTERS.length; index++) {
            if (source.registers[index] != overlay.registers[index]) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "stage 1 %s differs: source=%08x overlay=%08x",
                        RESULT_REGISTERS[index],
                        source.registers[index],
                        overlay.registers[index]));
            }
        }
    }

    void verifyProtectedRegisters(Result source, Result gate) {
        for (String name : PROTECTED_REGISTERS) {
            int index = Arrays.asList(RESULT_REGISTERS).indexOf(name);
            if (index < 0) {
                throw new IllegalStateException(
                        "protected register is not captured: " + name);
            }
            if (source.registers[index] != gate.registers[index]) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "%s differs: source=%08x gate=%08x",
                        name,
                        source.registers[index],
                        gate.registers[index]));
            }
        }
    }

    void verifyRam(
            byte[] sourceImage,
            byte[] overlayImage,
            Result source,
            Result overlay,
            int stage) {
        byte[] expectedSourceReservation = reservationSentinel();
        expectedSourceReservation[0] = 0;
        byte[] actualSourceReservation = sliceRam(
                source.ram, SELECTOR_STATE, RESERVATION_SIZE);
        if (!Arrays.equals(
                actualSourceReservation, expectedSourceReservation)) {
            throw new IllegalStateException(
                    "selector-init source changed reserved RAM unexpectedly");
        }

        byte[] expectedOverlayReservation = reservationSentinel();
        expectedOverlayReservation[0] = 0;
        if (stage >= 2) {
            Arrays.fill(expectedOverlayReservation, 0, 8, (byte) 0);
            System.arraycopy(
                    overlayImage,
                    (int) FUEL_MAP_1,
                    expectedOverlayReservation,
                    (int) (FUEL_SHADOW - SELECTOR_STATE),
                    FUEL_MAP_SIZE);
            System.arraycopy(
                    overlayImage,
                    (int) FUEL_STOCK_TAIL,
                    expectedOverlayReservation,
                    (int) (FUEL_SHADOW - SELECTOR_STATE) + FUEL_MAP_SIZE,
                    FUEL_TAIL_SIZE);
            System.arraycopy(
                    overlayImage,
                    (int) THROTTLE_CLUSTER,
                    expectedOverlayReservation,
                    (int) (THROTTLE_SHADOW - SELECTOR_STATE),
                    THROTTLE_CLUSTER_SIZE);
        }
        byte[] actualOverlayReservation = sliceRam(
                overlay.ram, SELECTOR_STATE, RESERVATION_SIZE);
        if (!Arrays.equals(
                actualOverlayReservation, expectedOverlayReservation)) {
            int offset = firstDifference(
                    actualOverlayReservation, expectedOverlayReservation);
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "stage %d reservation differs at %08x: actual=%02x"
                    + " expected=%02x",
                    stage,
                    SELECTOR_STATE + offset,
                    actualOverlayReservation[offset] & 0xFF,
                    expectedOverlayReservation[offset] & 0xFF));
        }

        byte[] expectedRuntime = Arrays.copyOfRange(
                sourceImage,
                (int) THROTTLE_CLUSTER + THROTTLE_SELECTED_OFFSET,
                (int) THROTTLE_CLUSTER + THROTTLE_SELECTED_OFFSET + 2);
        byte[] sourceRuntime = sliceRam(source.ram, THROTTLE_RUNTIME, 2);
        byte[] overlayRuntime = sliceRam(
                overlay.ram, THROTTLE_RUNTIME, 2);
        if (
                !Arrays.equals(sourceRuntime, expectedRuntime)
                || !Arrays.equals(overlayRuntime, expectedRuntime)) {
            throw new IllegalStateException(
                    "stock throttle runtime scalar differs");
        }

        int reservationStart = (int) (SELECTOR_STATE - RAM_START);
        int reservationEnd = reservationStart + RESERVATION_SIZE;
        for (int offset = 0; offset < RAM_SIZE; offset++) {
            if (offset >= reservationStart && offset < reservationEnd) {
                continue;
            }
            if (source.ram[offset] != overlay.ram[offset]) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "stage %d RAM differs outside reservation at %08x:"
                        + " source=%02x overlay=%02x",
                        stage,
                        RAM_START + offset,
                        source.ram[offset] & 0xFF,
                        overlay.ram[offset] & 0xFF));
            }
        }
    }

    byte[] reservationSentinel() {
        byte[] result = new byte[RESERVATION_SIZE];
        for (int index = 0; index < result.length; index++) {
            result[index] = (byte) (0xA0 + index);
        }
        return result;
    }

    byte[] sliceRam(byte[] ram, long address, int size) {
        int offset = (int) (address - RAM_START);
        return Arrays.copyOfRange(ram, offset, offset + size);
    }

    void requirePointerTable(
            byte[] image,
            long address,
            long[] expected,
            String context) {
        for (int index = 0; index < expected.length; index++) {
            long actual = readBigEndianLong(
                    image, (int) address + index * 4);
            if (actual != expected[index]) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "%s pointer %d is %08x, expected %08x",
                        context, index, actual, expected[index]));
            }
        }
    }

    void requireImageLong(
            byte[] image,
            long address,
            long expected,
            String context) {
        long actual = readBigEndianLong(image, (int) address);
        if (actual != expected) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "%s at %08x is %08x, expected %08x",
                    context, address, actual, expected));
        }
    }

    static int firstDifference(byte[] left, byte[] right) {
        for (int index = 0; index < left.length; index++) {
            if (left[index] != right[index]) {
                return index;
            }
        }
        return -1;
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
