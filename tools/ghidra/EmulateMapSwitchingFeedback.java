// EmulateMapSwitchingFeedback.java - execute the locked CAN 0x551 feedback
// wrapper and pulse engine with a deterministic stock-serializer stub.
//
// The stub writes 0xA5 to payload byte 5 before every engine invocation. This
// proves call order and lets the test verify that only bits 0-1 are overridden.
// The locked engine contains the pilot 10/10 frame counts. Individual cases
// modify only these two documented configuration bytes in emulator memory.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingFeedback.java \
//       <feedback-wrapper-blob> <feedback-engine-blob>
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

public class EmulateMapSwitchingFeedback extends GhidraScript {

    static final long WRAPPER_BASE = 0x000D35E0L;
    static final long ENGINE_BASE = 0x000D3760L;
    static final long STOCK_SERIALIZER = 0x000C5372L;
    static final long CONFIG_ADDRESS = 0x000D3848L;
    static final long SELECTOR_STATE = 0xFFFF5D00L;
    static final long PAYLOAD = 0xFFFF3AD5L;
    static final long STATUS = 0xFFFF3ADAL;
    static final long STACK_TOP = 0xFFFF7F00L;
    static final long RETURN_ADDRESS = 0x000D4000L;

    static final String WRAPPER_SHA =
            "b8e8c20cd365f27b7a8df59318f22911621ef51a33dfefc128563940be558d36";
    static final String ENGINE_SHA =
            "c3a10706e283bc53c5634730d7ad96a5c49bebd8dc22536f96cfc411ef46a784";

    // mov.l @(0xc5380,pc),r1; mov #-0x5b,r0; mov.b r0,@r1; rts; nop
    // followed by alignment padding and the 0xFFFF3ADA literal.
    static final byte[] SERIALIZER_STUB = {
        (byte) 0xD1, 0x03, (byte) 0xE0, (byte) 0xA5,
        0x21, 0x00, 0x00, 0x0B, 0x00, 0x09,
        0x00, 0x09, 0x00, 0x09,
        (byte) 0xFF, (byte) 0xFF, 0x3A, (byte) 0xDA,
    };
    static final byte[] PAYLOAD_SEED = {
        0x11, 0x22, 0x33, 0x44, 0x55, 0x00, 0x77, (byte) 0x88,
    };

    byte[] wrapper;
    byte[] engine;
    Language language;
    AddressSpace space;
    int cases;
    int invocations;
    int instructions;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "need: <feedback-wrapper-blob> <feedback-engine-blob>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        wrapper = readLocked(
                Path.of(args[0]), 0x80, WRAPPER_SHA, "wrapper");
        engine = readLocked(
                Path.of(args[1]), 0x100, ENGINE_SHA, "engine");

        runSequence(
                "disabled", 0, state(0, 0, 0, 0, 1, 1, 0, 0),
                new int[]{0xA5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runSequence(
                "two-pulses-2x2", 0x0202,
                state(0, 0, 0, 0, 2, 1, 0, 0),
                new int[]{
                    0xA6, 0xA6, 0xA4, 0xA4,
                    0xA6, 0xA6, 0xA4, 0xA4,
                },
                state(0, 0, 0, 0, 0, 0, 0, 0));
        runSequence(
                "one-pulse-1x1", 0x0101,
                state(0, 0, 0, 0, 1, 1, 0, 0),
                new int[]{0xA6, 0xA4},
                state(0, 0, 0, 0, 0, 0, 0, 0));
        runSequence(
                "idle", 0x0202, state(0, 0, 0, 0, 0, 0, 0, 0),
                new int[]{0xA5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runSequence(
                "corrupt-pulses", 0x0202,
                state(0, 0, 0, 0, 6, 1, 0, 0),
                new int[]{0xA5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runSequence(
                "corrupt-phase", 0x0202,
                state(0, 0, 0, 0, 1, 3, 0, 0),
                new int[]{0xA5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runSequence(
                "corrupt-idle", 0x0202,
                state(0, 0, 0, 0, 0, 0, 1, 0),
                new int[]{0xA5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runSequence(
                "missing-off-count", 0x0200,
                state(0, 0, 0, 0, 1, 1, 0, 0),
                new int[]{0xA5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runSequence(
                "missing-on-count", 0x0002,
                state(0, 0, 0, 0, 1, 1, 0, 0),
                new int[]{0xA5}, state(0, 0, 0, 0, 0, 0, 0, 0));

        println(String.format(
                "VQ_FEEDBACK_EMU status=PASS language=%s cases=%d"
                + " invocations=%d instructions=%d",
                languageId, cases, invocations, instructions));
    }

    void runSequence(
            String name, int counts, byte[] initialState,
            int[] expectedStatuses, byte[] expectedFinalState)
            throws Exception {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, WRAPPER_BASE, wrapper);
        setMemory(shared, ENGINE_BASE, engine);
        setMemory(shared, STOCK_SERIALIZER, SERIALIZER_STUB);
        setMemory(
                shared, CONFIG_ADDRESS,
                new byte[]{(byte) (counts >>> 8), (byte) counts});
        setMemory(shared, SELECTOR_STATE, initialState);
        setMemory(shared, PAYLOAD, PAYLOAD_SEED);

        PcodeThread<byte[]> thread = emulator.newThread(name);
        thread.overrideContextWithDefault();
        thread.reInitialize();
        setRegister(thread, "sr", 0x000000A1L);
        setRegister(thread, "r15", STACK_TOP);
        long[] protectedBefore = seedProtectedRegisters(thread);

        for (int expectedStatus : expectedStatuses) {
            thread.setCounter(toAddress(WRAPPER_BASE));
            setRegister(thread, "pr", RETURN_ADDRESS);
            int executed = 0;
            while (
                    thread.getCounter().getOffset() != RETURN_ADDRESS
                    && executed < 300) {
                thread.stepInstruction();
                executed++;
            }
            if (thread.getCounter().getOffset() != RETURN_ADDRESS) {
                throw new IllegalStateException(
                        name + ": did not return, pc="
                        + thread.getCounter());
            }
            byte[] actualPayload = readMemory(thread, PAYLOAD, 8);
            for (int index = 0; index < actualPayload.length; index++) {
                int expected = index == 5
                        ? expectedStatus : PAYLOAD_SEED[index] & 0xFF;
                if ((actualPayload[index] & 0xFF) != expected) {
                    throw new IllegalStateException(String.format(
                            "%s: payload[%d]=%02x expected=%02x",
                            name, index, actualPayload[index] & 0xFF,
                            expected));
                }
            }
            invocations++;
            instructions += executed;
        }
        byte[] actualState = readMemory(thread, SELECTOR_STATE, 8);
        if (!Arrays.equals(actualState, expectedFinalState)) {
            throw new IllegalStateException(
                    name + ": feedback state differs: "
                    + Arrays.toString(actualState));
        }
        verifyProtectedRegisters(thread, protectedBefore, name);
        if (readRegister(thread, "r15") != STACK_TOP) {
            throw new IllegalStateException(name + ": stack is unbalanced");
        }
        cases++;
    }

    byte[] state(int... values) {
        byte[] result = new byte[values.length];
        for (int index = 0; index < values.length; index++) {
            result[index] = (byte) values[index];
        }
        return result;
    }

    long[] seedProtectedRegisters(PcodeThread<byte[]> thread) {
        String[] names = {
            "r8", "r9", "r10", "r11", "r12", "r13", "r14",
            "gbr", "mach", "macl",
        };
        long[] values = new long[names.length];
        long seed = 0x11223344L;
        for (int index = 0; index < names.length; index++) {
            setRegister(thread, names[index], seed);
            values[index] = seed;
            seed += 0x01010101L;
        }
        return values;
    }

    void verifyProtectedRegisters(
            PcodeThread<byte[]> thread, long[] expected, String caseName) {
        String[] names = {
            "r8", "r9", "r10", "r11", "r12", "r13", "r14",
            "gbr", "mach", "macl",
        };
        for (int index = 0; index < names.length; index++) {
            long actual = readRegister(thread, names[index]);
            if (actual != expected[index]) {
                throw new IllegalStateException(String.format(
                        "%s: %s changed %08x -> %08x",
                        caseName, names[index], expected[index], actual));
            }
        }
    }

    byte[] readLocked(
            Path path, int expectedLength, String expectedSha, String name)
            throws Exception {
        byte[] bytes = Files.readAllBytes(path);
        if (bytes.length != expectedLength) {
            throw new IllegalArgumentException(
                    name + " blob has unexpected length");
        }
        String digest = sha256(bytes);
        if (!digest.equals(expectedSha)) {
            throw new IllegalArgumentException(
                    name + " blob SHA-256 is " + digest
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
