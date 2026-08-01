// EmulateMapSwitchingReset.java - compare the exact JK08A TRAPA reset handler
// across a known-working input ROM and its map-switching composition.
//
// The harness starts at FUN_00027E24, reaches the real startup thunk from its
// real caller, executes the complete stock initializer and injected startup
// path, then continues through the first complete scheduler-loop iteration.
// Unchanged hardware-oriented callees before and after the thunk and inside
// FUN_0002C648 use identical deterministic return-zero stubs in all images.
// Every RAM byte outside the declared selector/shadow reservation, the selected
// runtime scalar, and stale bytes below the restored stack pointer must match
// the known-working execution. An optional tuned ROM is checked against the
// generated composition with the same rules.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingReset.java \
//       <working-rom> <patched-rom> [tuned-rom]
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
import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;

public class EmulateMapSwitchingReset extends GhidraScript {

    static final int ROM_SIZE = 0x100000;
    static final long RESET_HANDLER = 0x00027E24L;
    static final long STARTUP_THUNK = 0x00027CE4L;
    static final long THUNK_RETURN = 0x00027ECCL;
    static final long MAIN_LOOP_ENTRY = 0x00027EE6L;
    static final long TRAPA_STACK = 0xFFFF7FF4L;
    static final long RESET_GBR = 0xFFFF83CCL;
    static final long RAM_START = 0xFFFF0000L;
    static final int RAM_SIZE = 0xC000;
    static final long PERIPHERAL_PAGE = 0xFFFFF000L;
    static final int PERIPHERAL_PAGE_SIZE = 0x1000;
    static final long CLOCK_STATUS = 0xFFFFF75EL;
    static final long SCHEDULER_READY = 0xFFFF84B9L;
    static final long RESERVATION_START = 0xFFFF5D00L;
    static final long RESERVATION_END = 0xFFFF5D3CL;
    static final long FUEL_SHADOW = 0xFFFF5D10L;
    static final long THROTTLE_SHADOW = 0xFFFF5D20L;
    static final long THROTTLE_RUNTIME = 0xFFFF1796L;
    static final long FUEL_POINTER_TABLE = 0x000D35B8L;
    static final long THROTTLE_POINTER_TABLE = 0x000D35CCL;
    static final long FUEL_STOCK_TAIL = 0x00009356L;
    static final long THROTTLE_STOCK_CLUSTER = 0x00009424L;
    static final int THROTTLE_SELECTED_OFFSET = 8;

    static final long[] PRE_THUNK_CALLEES = {
        0x00027F48L,
        0x00028CEAL,
        0x00027B92L,
        0x00027AC0L,
        0x00027C50L,
        0x00027C34L,
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

    static final long[] POST_THUNK_CALLEES = {
        0x00027B88L,
        0x00027DE4L,
        0x00020DFEL,
        0x00027AA2L,
        0x00027A34L,
    };

    static final int[] SELECTOR_SEEDS = {
        0x00, 0x01, 0x02, 0x03, 0x04,
        0x05, 0x7F, 0x80, 0xFF,
    };

    // mov #0,r0; rts; nop
    static final byte[] RETURN_ZERO_STUB = {
        (byte) 0xE0, 0x00, 0x00, 0x0B, 0x00, 0x09,
    };

    static final String[] PROTECTED_REGISTERS = {
        "r8", "r9", "r10", "r11", "r12", "r13", "r14",
        "r15", "pr", "gbr", "mach", "macl",
    };

    static class Result {
        final byte[] ram;
        final Map<String, Long> before;
        final Map<String, Long> after;
        final long srBefore;
        final long srAfter;
        final Map<String, Long> checkpoint;
        final long srCheckpoint;
        final long minSp;
        final int instructions;

        Result(
                byte[] ram,
                Map<String, Long> before,
                Map<String, Long> after,
                long srBefore,
                long srAfter,
                Map<String, Long> checkpoint,
                long srCheckpoint,
                long minSp,
                int instructions) {
            this.ram = ram;
            this.before = before;
            this.after = after;
            this.srBefore = srBefore;
            this.srAfter = srAfter;
            this.checkpoint = checkpoint;
            this.srCheckpoint = srCheckpoint;
            this.minSp = minSp;
            this.instructions = instructions;
        }
    }

    Language language;
    AddressSpace space;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2 || args.length > 3) {
            throw new IllegalArgumentException(
                    "need: <working-rom> <patched-rom> [tuned-rom]");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        byte[] working = readImage(args[0]);
        byte[] patched = readImage(args[1]);
        byte[] tuned = args.length == 3 ? readImage(args[2]) : null;

        int totalInstructions = 0;
        long lowestSp = TRAPA_STACK;
        for (int selector : SELECTOR_SEEDS) {
            Result baseline = execute(working, selector);
            Result candidate = execute(patched, selector);
            verifyProtected("working", selector, baseline);
            verifyProtected("patched", selector, candidate);
            verifyPatchedState("patched", selector, candidate, patched);
            verifyDifferential(
                    "working", "patched", selector,
                    baseline, candidate, false);
            totalInstructions += baseline.instructions;
            totalInstructions += candidate.instructions;
            lowestSp = unsignedMin(lowestSp, baseline.minSp);
            lowestSp = unsignedMin(lowestSp, candidate.minSp);
            if (tuned != null) {
                Result tunedResult = execute(tuned, selector);
                verifyProtected("tuned", selector, tunedResult);
                verifyPatchedState("tuned", selector, tunedResult, tuned);
                verifyDifferential(
                        "patched", "tuned", selector,
                        candidate, tunedResult, true);
                totalInstructions += tunedResult.instructions;
                lowestSp = unsignedMin(lowestSp, tunedResult.minSp);
            }
        }

        println(String.format(
                Locale.ROOT,
                "VQ_RESET_EMU status=PASS language=%s"
                + " working_sha256=%s patched_sha256=%s%s"
                + " seeds=%d instructions=%d min_sp=%08x"
                + " pre_thunk_stubs=%d initializer_stubs=%d"
                + " post_thunk_stubs=%d",
                languageId, sha256(working), sha256(patched),
                tuned == null ? "" : " tuned_sha256=" + sha256(tuned),
                SELECTOR_SEEDS.length, totalInstructions, lowestSp,
                PRE_THUNK_CALLEES.length, INITIALIZER_CALLEES.length,
                POST_THUNK_CALLEES.length));
    }

    Result execute(byte[] image, int selector) throws Exception {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, 0, image);
        setMemory(shared, RAM_START, new byte[RAM_SIZE]);
        setMemory(
                shared, PERIPHERAL_PAGE,
                new byte[PERIPHERAL_PAGE_SIZE]);
        setMemory(shared, CLOCK_STATUS, new byte[]{0x00, 0x10});
        setMemory(shared, SCHEDULER_READY, new byte[]{0x04});

        byte[] selectorState = new byte[8];
        for (int index = 0; index < selectorState.length; index++) {
            selectorState[index] = (byte) (selector + index * 0x31);
        }
        setMemory(shared, RESERVATION_START, selectorState);
        for (long callee : PRE_THUNK_CALLEES) {
            setMemory(shared, callee, RETURN_ZERO_STUB);
        }
        for (long callee : INITIALIZER_CALLEES) {
            setMemory(shared, callee, RETURN_ZERO_STUB);
        }
        for (long callee : POST_THUNK_CALLEES) {
            setMemory(shared, callee, RETURN_ZERO_STUB);
        }

        PcodeThread<byte[]> thread = emulator.newThread("reset");
        thread.overrideContextWithDefault();
        thread.reInitialize();
        thread.setCounter(toAddress(RESET_HANDLER));
        setRegister(thread, "sr", 0x700000F0L | (selector & 1));
        setRegister(thread, "pr", 0x13579BDFL);
        setRegister(thread, "r15", TRAPA_STACK);
        setRegister(thread, "gbr", RESET_GBR);
        long seed = 0x10203040L;
        for (int number = 0; number <= 14; number++) {
            setRegister(thread, "r" + number, seed);
            seed += 0x01010101L;
        }
        setRegister(thread, "r15", TRAPA_STACK);
        setRegister(thread, "mach", 0x2468ACE0L);
        setRegister(thread, "macl", 0xFDB97531L);

        int instructions = 0;
        int limit = 200000;
        long minSp = readRegister(thread, "r15");
        while (
                thread.getCounter().getOffset() != STARTUP_THUNK
                && instructions < limit) {
            thread.stepInstruction();
            instructions++;
            minSp = unsignedMin(minSp, readRegister(thread, "r15"));
        }
        if (thread.getCounter().getOffset() != STARTUP_THUNK) {
            throw stopped("startup thunk not reached", thread, instructions);
        }
        Map<String, Long> before = snapshot(thread);
        long srBefore = readRegister(thread, "sr");

        while (
                thread.getCounter().getOffset() != THUNK_RETURN
                && instructions < limit) {
            thread.stepInstruction();
            instructions++;
            minSp = unsignedMin(minSp, readRegister(thread, "r15"));
        }
        if (thread.getCounter().getOffset() != THUNK_RETURN) {
            throw stopped("startup thunk did not return", thread, instructions);
        }
        Map<String, Long> after = snapshot(thread);
        long srAfter = readRegister(thread, "sr");

        int loopVisits = 0;
        while (instructions < limit) {
            if (thread.getCounter().getOffset() == MAIN_LOOP_ENTRY) {
                loopVisits++;
                if (loopVisits == 2) {
                    break;
                }
            }
            thread.stepInstruction();
            instructions++;
            minSp = unsignedMin(minSp, readRegister(thread, "r15"));
        }
        if (loopVisits != 2) {
            throw stopped(
                    "first scheduler iteration did not complete",
                    thread, instructions);
        }
        Map<String, Long> checkpoint = snapshot(thread);
        long srCheckpoint = readRegister(thread, "sr");
        byte[] ram = readMemory(thread, RAM_START, RAM_SIZE);
        return new Result(
                ram, before, after, srBefore, srAfter,
                checkpoint, srCheckpoint,
                minSp, instructions);
    }

    void verifyProtected(String image, int selector, Result result) {
        for (String name : PROTECTED_REGISTERS) {
            long before = result.before.get(name);
            long after = result.after.get(name);
            if (before != after) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "%s selector=%02x changed %s %08x -> %08x",
                        image, selector, name, before, after));
            }
        }
        if ((result.srBefore & 0xFFFFFFFEL)
                != (result.srAfter & 0xFFFFFFFEL)) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "%s selector=%02x changed protected SR bits"
                    + " %08x -> %08x",
                    image, selector, result.srBefore, result.srAfter));
        }
    }

    void verifyDifferential(
            String baselineName,
            String candidateName,
            int selector,
            Result baseline,
            Result candidate,
            boolean allowRuntimeScalar) {
        for (String name : PROTECTED_REGISTERS) {
            long expected = baseline.after.get(name);
            long actual = candidate.after.get(name);
            if (expected != actual) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "selector=%02x %s/%s %s differs"
                        + " %08x != %08x",
                        selector, baselineName, candidateName,
                        name, expected, actual));
            }
        }
        if ((baseline.srAfter & 0xFFFFFFFEL)
                != (candidate.srAfter & 0xFFFFFFFEL)) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x %s/%s protected SR differs"
                    + " %08x != %08x",
                    selector, baselineName, candidateName,
                    baseline.srAfter, candidate.srAfter));
        }
        for (String name : PROTECTED_REGISTERS) {
            long expected = baseline.checkpoint.get(name);
            long actual = candidate.checkpoint.get(name);
            if (expected != actual) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "selector=%02x %s/%s checkpoint %s differs"
                        + " %08x != %08x",
                        selector, baselineName, candidateName,
                        name, expected, actual));
            }
        }
        if ((baseline.srCheckpoint & 0xFFFFFFFEL)
                != (candidate.srCheckpoint & 0xFFFFFFFEL)) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x %s/%s checkpoint SR differs"
                    + " %08x != %08x",
                    selector, baselineName, candidateName,
                    baseline.srCheckpoint, candidate.srCheckpoint));
        }

        int reservedStart = (int) (RESERVATION_START - RAM_START);
        int reservedEnd = (int) (RESERVATION_END - RAM_START);
        int runtimeStart = (int) (THROTTLE_RUNTIME - RAM_START);
        int runtimeEnd = runtimeStart + 2;
        long stackStart = unsignedMin(baseline.minSp, candidate.minSp);
        if (Long.compareUnsigned(stackStart, RESERVATION_END) <= 0) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x %s/%s stack reached reservation: %08x",
                    selector, baselineName, candidateName, stackStart));
        }
        long restoredSp = baseline.checkpoint.get("r15");
        if (Long.compareUnsigned(restoredSp, stackStart) < 0
                || Long.compareUnsigned(restoredSp, TRAPA_STACK) > 0) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "selector=%02x %s/%s restored SP is outside"
                    + " the observed stack interval: %08x not in"
                    + " [%08x,%08x]",
                    selector, baselineName, candidateName,
                    restoredSp, stackStart, TRAPA_STACK));
        }
        int stackStartOffset = (int) (stackStart - RAM_START);
        int staleStackEndOffset = (int) (restoredSp - RAM_START);
        for (int offset = 0; offset < RAM_SIZE; offset++) {
            if (offset >= reservedStart && offset < reservedEnd) {
                continue;
            }
            if (
                    allowRuntimeScalar
                    && offset >= runtimeStart
                    && offset < runtimeEnd) {
                continue;
            }
            if (
                    offset >= stackStartOffset
                    && offset < staleStackEndOffset) {
                continue;
            }
            if (baseline.ram[offset] != candidate.ram[offset]) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "selector=%02x %s/%s RAM differs outside"
                        + " reservation and stale stack at"
                        + " %08x: %02x != %02x",
                        selector, baselineName, candidateName,
                        RAM_START + offset,
                        baseline.ram[offset] & 0xFF,
                        candidate.ram[offset] & 0xFF));
            }
        }
    }

    void verifyPatchedState(
            String imageName,
            int selector,
            Result result,
            byte[] image) {
        int normalized = 0;
        int fuelSource = readRomPointer(
                image, FUEL_POINTER_TABLE + normalized * 4L);
        int throttleSource = readRomPointer(
                image, THROTTLE_POINTER_TABLE + normalized * 4L);

        byte[] expectedFuel = new byte[12];
        System.arraycopy(image, fuelSource, expectedFuel, 0, 8);
        System.arraycopy(
                image, (int) FUEL_STOCK_TAIL,
                expectedFuel, 8, 4);
        verifyRamBytes(
                imageName, selector, "fuel shadow",
                result, FUEL_SHADOW, expectedFuel);

        byte[] expectedThrottle = new byte[28];
        System.arraycopy(
                image, (int) THROTTLE_STOCK_CLUSTER,
                expectedThrottle, 0, expectedThrottle.length);
        expectedThrottle[THROTTLE_SELECTED_OFFSET] =
                image[throttleSource];
        expectedThrottle[THROTTLE_SELECTED_OFFSET + 1] =
                image[throttleSource + 1];
        verifyRamBytes(
                imageName, selector, "throttle shadow",
                result, THROTTLE_SHADOW, expectedThrottle);
        verifyRamBytes(
                imageName, selector, "throttle runtime",
                result, THROTTLE_RUNTIME,
                new byte[]{
                    image[throttleSource], image[throttleSource + 1],
                });

        verifyRamBytes(
                imageName, selector, "selector state",
                result, RESERVATION_START,
                new byte[]{
                    (byte) normalized, 0, 0, 0, 0, 0, 0, 0,
                });
    }

    int readRomPointer(byte[] image, long address) {
        int offset = (int) address;
        int result =
                ((image[offset] & 0xFF) << 24)
                | ((image[offset + 1] & 0xFF) << 16)
                | ((image[offset + 2] & 0xFF) << 8)
                | (image[offset + 3] & 0xFF);
        if (result < 0 || result + 2 > image.length) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "ROM pointer at %08x is outside the image: %08x",
                    address, result));
        }
        return result;
    }

    void verifyRamBytes(
            String imageName,
            int selector,
            String label,
            Result result,
            long address,
            byte[] expected) {
        int offset = (int) (address - RAM_START);
        for (int index = 0; index < expected.length; index++) {
            int actual = result.ram[offset + index] & 0xFF;
            int wanted = expected[index] & 0xFF;
            if (actual != wanted) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "%s selector=%02x %s differs at %08x:"
                        + " %02x != %02x",
                        imageName, selector, label,
                        address + index, actual, wanted));
            }
        }
    }

    long unsignedMin(long left, long right) {
        return Long.compareUnsigned(left, right) <= 0 ? left : right;
    }

    Map<String, Long> snapshot(PcodeThread<byte[]> thread) {
        Map<String, Long> result = new LinkedHashMap<>();
        for (String name : PROTECTED_REGISTERS) {
            result.put(name, readRegister(thread, name));
        }
        return result;
    }

    IllegalStateException stopped(
            String message, PcodeThread<byte[]> thread, int instructions) {
        return new IllegalStateException(String.format(
                Locale.ROOT, "%s after %d instructions; pc=%s",
                message, instructions, thread.getCounter()));
    }

    byte[] readImage(String name) throws Exception {
        byte[] image = Files.readAllBytes(Path.of(name));
        if (image.length != ROM_SIZE) {
            throw new IllegalArgumentException(
                    name + " length is " + image.length
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
