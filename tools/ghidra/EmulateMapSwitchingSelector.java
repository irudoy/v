// EmulateMapSwitchingSelector.java - execute the exact-JK08A selector host
// together with the locked limiter commit in Ghidra's SuperH p-code emulator.
//
// The test does not patch the current program or write a ROM.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingSelector.java \
//       <selector-host-blob> <limiter-commit-blob>
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

public class EmulateMapSwitchingSelector extends GhidraScript {

    static final long HOST_BASE = 0x000D2108L;
    static final long COMMIT_BASE = 0x000D3660L;
    static final long STOCK_HOST = 0x000D09D8L;
    static final long RETURN_ADDRESS = 0x000D4000L;
    static final long SELECTOR_STATE = 0xFFFF5D00L;
    static final long CURRENT_CODE = 0xFFFF2A85L;
    static final long ASCD_STATUS = 0xFFFF41AEL;
    static final long DIAGNOSTIC_STATUS = 0xFFFF2A84L;
    static final long FUEL_STOCK = 0x0000934EL;
    static final long FUEL_POINTER_TABLE = 0x000D35B8L;
    static final long THROTTLE_STOCK = 0x00009424L;
    static final long THROTTLE_POINTER_TABLE = 0x000D35CCL;
    static final long STACK_TOP = 0xFFFF7F00L;

    static final String HOST_SHA =
            "ebc0fb3e4ccd177e47c4420b90fb49a360e00f3bedceca11b3cdf2a4590e6e4c";
    static final String COMMIT_SHA =
            "e1e296e0d2f1dccef21982f14f4e3e1aebdc39fba6b68ae8b3e2ecbc16d5a5aa";

    byte[] host;
    byte[] commit;
    byte[] stockFuel;
    byte[] stockThrottle;
    Language language;
    AddressSpace space;
    int cases;
    int instructions;

    record TestCase(
            String name,
            byte[] initialState,
            int previousCode,
            int currentCode,
            int ascdStatus,
            int diagnosticStatus,
            byte[] expectedState) {
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "need: <selector-host-blob> <limiter-commit-blob>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        host = readLocked(Path.of(args[0]), 0x168, HOST_SHA, "selector");
        commit = readLocked(Path.of(args[1]), 0x100, COMMIT_SHA, "commit");
        stockFuel = readProgram(FUEL_STOCK, 12);
        stockThrottle = readProgram(THROTTLE_STOCK, 28);

        TestCase[] tests = {
            test("idle", state(0, 0, 0, 0, 0, 0, 0, 0),
                    0x20, 0x20, 0,
                    state(0, 0, 0, 0, 0, 0, 0, 0)),
            test("arm", state(0, 0, 0, 0, 0, 0, 0, 0),
                    0x20, 8, 0, state(0, 1, 0, 1, 0, 0, 0, 0)),
            test("set-held", state(1, 1, 2, 7, 0, 0, 0, 0),
                    8, 8, 0, state(1, 1, 2, 8, 0, 0, 0, 0)),
            test("set-to-cancel", state(1, 1, 2, 7, 0, 0, 0, 0),
                    8, 2, 0, state(1, 2, 2, 8, 0, 0, 0, 0)),
            test("cancel-held", state(2, 2, 3, 9, 0, 0, 0, 0),
                    2, 2, 0, state(2, 2, 3, 10, 0, 0, 0, 0)),
            test("cancel-to-set", state(2, 2, 3, 9, 0, 0, 0, 0),
                    2, 8, 0, state(2, 1, 4, 10, 0, 0, 0, 0)),
            test("commit-map-1", state(3, 1, 1, 9, 0, 0, 0, 0),
                    8, 0x20, 0, state(0, 0, 0, 0, 1, 1, 0, 0)),
            test("commit-map-5", state(1, 1, 5, 9, 0, 0, 0, 0),
                    8, 0x20, 0, state(4, 0, 0, 0, 5, 1, 0, 0)),
            test("release-zero-abort", state(3, 1, 0, 9, 0, 0, 0, 0),
                    8, 0, 0, state(3, 0, 0, 0, 0, 0, 0, 0)),
            test("sixth-pulse-abort", state(2, 2, 5, 9, 0, 0, 0, 0),
                    2, 8, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            test("timeout-abort", state(2, 1, 2, 99, 0, 0, 0, 0),
                    8, 8, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            test("ascd-abort", state(2, 1, 2, 9, 0, 0, 0, 0),
                    8, 8, 0x80, state(2, 0, 0, 0, 0, 0, 0, 0)),
            test("feedback-blocks", state(2, 1, 2, 9, 3, 1, 4, 0),
                    8, 0, 0, state(2, 0, 0, 0, 3, 1, 4, 0)),
            test("feedback-corrupt", state(2, 1, 2, 9, 6, 1, 4, 0),
                    8, 0, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            test("idle-feedback-corrupt",
                    state(2, 1, 2, 9, 0, 0, 1, 0),
                    8, 0, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            test("selector-corrupt", state(2, 3, 2, 9, 0, 0, 0, 0),
                    8, 0, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            test("invalid-index", state(0xFF, 1, 2, 9, 3, 1, 4, 0),
                    8, 0, 0, state(0, 0, 0, 0, 0, 0, 0, 0)),
        };
        for (TestCase test : tests) {
            runCase(test);
        }
        println(String.format(
                "VQ_SELECTOR_EMU status=PASS language=%s cases=%d"
                + " instructions=%d",
                languageId, cases, instructions));
    }

    TestCase test(
            String name, byte[] initial, int previous, int current,
            int ascd, byte[] expected) {
        return new TestCase(
                name, initial, previous, current, ascd, 0x25, expected);
    }

    byte[] state(int... values) {
        byte[] result = new byte[values.length];
        for (int index = 0; index < values.length; index++) {
            result[index] = (byte) values[index];
        }
        return result;
    }

    void runCase(TestCase test) throws Exception {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, HOST_BASE, host);
        setMemory(shared, COMMIT_BASE, commit);
        setMemory(
                shared, STOCK_HOST,
                new byte[]{0x00, 0x0B, 0x00, 0x09});
        setMemory(shared, FUEL_STOCK, stockFuel);
        setMemory(shared, THROTTLE_STOCK, stockThrottle);
        long[] fuelPointers = {
            FUEL_STOCK, FUEL_STOCK, FUEL_STOCK, FUEL_STOCK, FUEL_STOCK,
        };
        long throttleScalar = THROTTLE_STOCK + 8;
        long[] throttlePointers = {
            throttleScalar, throttleScalar, throttleScalar,
            throttleScalar, throttleScalar,
        };
        setMemory(shared, FUEL_POINTER_TABLE, encodeLongs(fuelPointers));
        setMemory(
                shared, THROTTLE_POINTER_TABLE,
                encodeLongs(throttlePointers));
        setMemory(shared, SELECTOR_STATE, test.initialState());
        setMemory(
                shared, CURRENT_CODE,
                new byte[]{
                    (byte) test.currentCode(), (byte) test.previousCode(),
                });
        setMemory(
                shared, ASCD_STATUS, new byte[]{(byte) test.ascdStatus()});
        setMemory(
                shared, DIAGNOSTIC_STATUS,
                new byte[]{(byte) test.diagnosticStatus()});

        PcodeThread<byte[]> thread = emulator.newThread(test.name());
        thread.overrideContextWithDefault();
        thread.reInitialize();
        thread.setCounter(toAddress(HOST_BASE));
        setRegister(thread, "sr", 0x000000A1L);
        setRegister(thread, "pr", RETURN_ADDRESS);
        setRegister(thread, "r15", STACK_TOP);
        long[] before = seedProtectedRegisters(thread);

        int executed = 0;
        while (
                thread.getCounter().getOffset() != RETURN_ADDRESS
                && executed < 500) {
            thread.stepInstruction();
            executed++;
        }
        if (thread.getCounter().getOffset() != RETURN_ADDRESS) {
            throw new IllegalStateException(
                    test.name() + ": did not return, pc="
                    + thread.getCounter());
        }
        verifyProtectedRegisters(thread, before, test.name());
        byte[] actualState = readMemory(thread, SELECTOR_STATE, 8);
        if (!Arrays.equals(actualState, test.expectedState())) {
            throw new IllegalStateException(
                    test.name() + ": selector state differs: "
                    + Arrays.toString(actualState));
        }
        int active = test.expectedState()[0] & 0xFF;
        int expectedDiagnostic =
                (test.diagnosticStatus() & 0x7F)
                | (active == 0 ? 0 : 0x80);
        int actualDiagnostic =
                readMemory(thread, DIAGNOSTIC_STATUS, 1)[0] & 0xFF;
        if (actualDiagnostic != expectedDiagnostic) {
            throw new IllegalStateException(String.format(
                    "%s: diagnostic=%02x expected=%02x",
                    test.name(), actualDiagnostic, expectedDiagnostic));
        }
        cases++;
        instructions += executed;
    }

    long[] seedProtectedRegisters(PcodeThread<byte[]> thread) {
        String[] names = {
            "r8", "r9", "r10", "r11", "r12", "r13", "r14",
            "pr", "gbr", "mach", "macl",
        };
        long[] values = new long[names.length];
        long seed = 0x11223344L;
        for (int index = 0; index < names.length; index++) {
            String name = names[index];
            long value = name.equals("pr") ? RETURN_ADDRESS : seed;
            setRegister(thread, name, value);
            values[index] = value;
            seed += 0x01010101L;
        }
        return values;
    }

    void verifyProtectedRegisters(
            PcodeThread<byte[]> thread, long[] expected, String caseName) {
        String[] names = {
            "r8", "r9", "r10", "r11", "r12", "r13", "r14",
            "pr", "gbr", "mach", "macl",
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

    byte[] readProgram(long address, int size) throws Exception {
        byte[] result = new byte[size];
        int read = currentProgram.getMemory().getBytes(
                toAddress(address), result);
        if (read != size) {
            throw new IllegalStateException("stock read is incomplete");
        }
        return result;
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

    byte[] encodeLongs(long[] values) {
        byte[] result = new byte[values.length * 4];
        for (int index = 0; index < values.length; index++) {
            byte[] encoded = Utils.longToBytes(
                    values[index], 4, language.isBigEndian());
            System.arraycopy(encoded, 0, result, index * 4, 4);
        }
        return result;
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
