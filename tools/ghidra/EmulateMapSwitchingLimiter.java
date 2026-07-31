// EmulateMapSwitchingLimiter.java - execute the exact-JK08A startup wrapper
// and atomic limiter-shadow commit in Ghidra's SuperH p-code emulator.
//
// The test uses exact stock container bytes from the open read-only program,
// synthetic maps 2-5, and synthetic RAM sentinels. It does not patch the
// current program or write a ROM.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingLimiter.java \
//       <startup-wrapper-blob> <limiter-commit-blob>
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
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

public class EmulateMapSwitchingLimiter extends GhidraScript {

    static final long STARTUP_BASE = 0x000D22A0L;
    static final long COMMIT_BASE = 0x000D3660L;
    static final long STOCK_INITIALIZER = 0x0002C648L;
    static final long RETURN_ADDRESS = 0x000D4000L;

    static final long FUEL_STOCK = 0x0000934EL;
    static final long FUEL_STOCK_TAIL = 0x00009356L;
    static final long FUEL_POINTER_TABLE = 0x000D35B8L;
    static final long[] FUEL_SLOTS = {
        0x0000934EL, 0x000D3500L, 0x000D3508L,
        0x000D3510L, 0x000D3518L,
    };

    static final long THROTTLE_STOCK = 0x00009424L;
    static final int THROTTLE_SELECTED_OFFSET = 8;
    static final long THROTTLE_POINTER_TABLE = 0x000D35CCL;
    static final long[] THROTTLE_SLOTS = {
        0x0000942CL, 0x000D3520L, 0x000D3522L,
        0x000D3524L, 0x000D3526L,
    };

    static final long RAM_SENTINEL_BASE = 0xFFFF5CF0L;
    static final int RAM_SENTINEL_SIZE = 0x60;
    static final long SELECTOR_STATE = 0xFFFF5D00L;
    static final long FUEL_SHADOW = 0xFFFF5D10L;
    static final long THROTTLE_SHADOW = 0xFFFF5D20L;
    static final long THROTTLE_RUNTIME = 0xFFFF1796L;
    static final long STACK_TOP = 0xFFFF7F00L;
    static final long ENTRY_SR = 0x000000A1L;

    static final String STARTUP_SHA =
            "fbab3032582bfced276a09c737de62e0c82e58f28d1a1e17e58d8b4d42474dca";
    static final String COMMIT_SHA =
            "e1e296e0d2f1dccef21982f14f4e3e1aebdc39fba6b68ae8b3e2ecbc16d5a5aa";

    byte[] startup;
    byte[] commit;
    byte[] stockFuel;
    byte[] stockThrottle;
    byte[][] fuelValues = new byte[5][];
    byte[][] throttleValues = new byte[5][];
    Language language;
    AddressSpace space;
    int cases;
    int instructions;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "need: <startup-wrapper-blob> <limiter-commit-blob>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        startup = readLocked(
                Path.of(args[0]), 0x60, STARTUP_SHA, "startup");
        commit = readLocked(
                Path.of(args[1]), 0x100, COMMIT_SHA, "commit");
        stockFuel = readProgram(FUEL_STOCK, 12);
        stockThrottle = readProgram(THROTTLE_STOCK, 28);
        fuelValues[0] = Arrays.copyOf(stockFuel, 8);
        throttleValues[0] = Arrays.copyOfRange(
                stockThrottle,
                THROTTLE_SELECTED_OFFSET,
                THROTTLE_SELECTED_OFFSET + 2);
        for (int index = 1; index < 5; index++) {
            fuelValues[index] = new byte[8];
            for (int offset = 0; offset < 8; offset++) {
                fuelValues[index][offset] =
                        (byte) (index * 0x20 + offset);
            }
            int scalar = 0x2500 + index * 0x100;
            throttleValues[index] = Utils.longToBytes(
                    scalar, 2, language.isBigEndian());
        }

        int[] requestedIndices = {0, 1, 2, 3, 4, 5, 0xFF};
        for (int requested : requestedIndices) {
            runCase("commit." + requested, false, requested);
            runCase("startup." + requested, true, requested);
        }
        println(String.format(
                "VQ_LIMITER_EMU status=PASS language=%s cases=%d"
                + " instructions=%d",
                languageId, cases, instructions));
    }

    void runCase(String name, boolean throughStartup, int requested)
            throws Exception {
        int normalized = requested >= 0 && requested < 5 ? requested : 0;
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, STARTUP_BASE, startup);
        setMemory(shared, COMMIT_BASE, commit);
        setMemory(
                shared, STOCK_INITIALIZER,
                new byte[]{0x00, 0x0B, 0x00, 0x09});
        setMemory(shared, FUEL_STOCK, stockFuel);
        setMemory(shared, THROTTLE_STOCK, stockThrottle);
        for (int index = 1; index < 5; index++) {
            setMemory(shared, FUEL_SLOTS[index], fuelValues[index]);
            setMemory(
                    shared, THROTTLE_SLOTS[index],
                    throttleValues[index]);
        }
        setMemory(shared, FUEL_POINTER_TABLE, encodeLongs(FUEL_SLOTS));
        setMemory(
                shared, THROTTLE_POINTER_TABLE,
                encodeLongs(THROTTLE_SLOTS));
        byte[] sentinel = new byte[RAM_SENTINEL_SIZE];
        Arrays.fill(sentinel, (byte) 0xA5);
        if (throughStartup) {
            sentinel[(int) (SELECTOR_STATE - RAM_SENTINEL_BASE)] =
                    (byte) requested;
        }
        setMemory(shared, RAM_SENTINEL_BASE, sentinel);
        setMemory(
                shared, THROTTLE_RUNTIME,
                new byte[]{(byte) 0xA5, (byte) 0xA5});

        PcodeThread<byte[]> thread = emulator.newThread(name);
        thread.overrideContextWithDefault();
        thread.reInitialize();
        thread.setCounter(toAddress(
                throughStartup ? STARTUP_BASE : COMMIT_BASE));
        setRegister(thread, "sr", ENTRY_SR);
        setRegister(thread, "pr", RETURN_ADDRESS);
        setRegister(thread, "r4", requested);
        setRegister(thread, "r15", STACK_TOP);

        List<String> protectedRegisters = new ArrayList<>();
        for (int number = 8; number <= 15; number++) {
            protectedRegisters.add("r" + number);
        }
        protectedRegisters.add("pr");
        protectedRegisters.add("gbr");
        protectedRegisters.add("mach");
        protectedRegisters.add("macl");
        long seed = 0x11223344L;
        for (String register : protectedRegisters) {
            if (register.equals("r15") || register.equals("pr")) {
                continue;
            }
            setRegister(thread, register, seed);
            seed += 0x01010101L;
        }
        long[] before = protectedRegisters.stream()
                .mapToLong(register -> readRegister(thread, register))
                .toArray();

        int executed = 0;
        while (
                thread.getCounter().getOffset() != RETURN_ADDRESS
                && executed < 200) {
            thread.stepInstruction();
            executed++;
        }
        if (thread.getCounter().getOffset() != RETURN_ADDRESS) {
            throw new IllegalStateException(
                    name + ": did not return, pc=" + thread.getCounter());
        }
        if (readRegister(thread, "r4") != normalized) {
            throw new IllegalStateException(
                    name + ": normalized r4 differs");
        }
        if (readRegister(thread, "sr") != ENTRY_SR) {
            throw new IllegalStateException(String.format(
                    "%s: SR=%08x expected=%08x",
                    name, readRegister(thread, "sr"), ENTRY_SR));
        }
        for (int index = 0; index < protectedRegisters.size(); index++) {
            String register = protectedRegisters.get(index);
            long after = readRegister(thread, register);
            if (after != before[index]) {
                throw new IllegalStateException(String.format(
                        "%s: %s changed %08x -> %08x",
                        name, register, before[index], after));
            }
        }
        verifyMemory(thread, name, normalized);
        cases++;
        instructions += executed;
    }

    void verifyMemory(
            PcodeThread<byte[]> thread, String name, int normalized) {
        byte[] expectedFuel = new byte[12];
        System.arraycopy(fuelValues[normalized], 0, expectedFuel, 0, 8);
        System.arraycopy(stockFuel, 8, expectedFuel, 8, 4);

        byte[] expectedThrottle = stockThrottle.clone();
        System.arraycopy(
                throttleValues[normalized], 0,
                expectedThrottle, THROTTLE_SELECTED_OFFSET, 2);

        byte[] expectedRam = new byte[RAM_SENTINEL_SIZE];
        Arrays.fill(expectedRam, (byte) 0xA5);
        int selectorOffset = (int) (SELECTOR_STATE - RAM_SENTINEL_BASE);
        expectedRam[selectorOffset] = (byte) normalized;
        Arrays.fill(
                expectedRam,
                selectorOffset + 1,
                selectorOffset + 8,
                (byte) 0x00);
        System.arraycopy(
                expectedFuel, 0, expectedRam,
                (int) (FUEL_SHADOW - RAM_SENTINEL_BASE),
                expectedFuel.length);
        System.arraycopy(
                expectedThrottle, 0, expectedRam,
                (int) (THROTTLE_SHADOW - RAM_SENTINEL_BASE),
                expectedThrottle.length);

        byte[] actualRam = readMemory(
                thread, RAM_SENTINEL_BASE, RAM_SENTINEL_SIZE);
        if (!Arrays.equals(actualRam, expectedRam)) {
            throw new IllegalStateException(
                    name + ": selector/shadow RAM differs");
        }
        byte[] actualRuntime = readMemory(thread, THROTTLE_RUNTIME, 2);
        if (!Arrays.equals(
                actualRuntime, throttleValues[normalized])) {
            throw new IllegalStateException(
                    name + ": stock throttle runtime scalar differs");
        }
    }

    byte[] readProgram(long address, int size) throws Exception {
        byte[] result = new byte[size];
        int read = currentProgram.getMemory().getBytes(
                toAddress(address), result);
        if (read != size) {
            throw new IllegalStateException(
                    String.format(
                            "stock read %08x got %d of %d bytes",
                            address, read, size));
        }
        return result;
    }

    byte[] readLocked(
            Path path, int expectedLength, String expectedSha, String name)
            throws Exception {
        byte[] bytes = Files.readAllBytes(path);
        if (bytes.length != expectedLength) {
            throw new IllegalArgumentException(
                    name + " blob length is " + bytes.length
                    + ", expected " + expectedLength);
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
