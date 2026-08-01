// EmulateMapSwitchingBoot.java - execute the patched JK08A startup thunk with
// the complete stock initializer body instead of the short return stub used by
// the composition unit tests.
//
// Direct callees of FUN_0002C648 are replaced with deterministic return-zero
// stubs. The fuel-compensation call still traverses the injected adapter and
// the stock lookup wrapper at 0x261F0. This isolates thunk, wrapper,
// initializer-body, adapter, stack, and limiter-commit integration without
// emulating unchanged subroutines outside the patched lookup path.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingBoot.java <patched-rom>
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

public class EmulateMapSwitchingBoot extends GhidraScript {

    static final int ROM_SIZE = 0x100000;
    static final long STARTUP_THUNK = 0x00027CE4L;
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

    static final long FUEL_MAP_1 = 0x0000934EL;
    static final long FUEL_STOCK_TAIL = 0x00009356L;
    static final long THROTTLE_CLUSTER = 0x00009424L;
    static final int THROTTLE_SELECTED_OFFSET = 8;

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

    Language language;
    AddressSpace space;
    byte[] image;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("need: <patched-rom>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        image = Files.readAllBytes(Path.of(args[0]));
        if (image.length != ROM_SIZE) {
            throw new IllegalArgumentException(
                    "patched ROM length is " + image.length
                    + ", expected " + ROM_SIZE);
        }

        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, 0, image);
        setMemory(shared, RAM_START, new byte[RAM_SIZE]);
        setMemory(shared, SELECTOR_STATE, new byte[]{(byte) 0xA5});
        for (long callee : INITIALIZER_CALLEES) {
            setMemory(shared, callee, RETURN_ZERO_STUB);
        }

        PcodeThread<byte[]> thread = emulator.newThread("boot");
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

        String[] protectedRegisters = {
            "r8", "r9", "r10", "r11", "r12", "r13", "r14",
            "r15", "pr", "gbr", "mach", "macl",
        };
        long[] expectedRegisters = seedAndSnapshot(
                thread, protectedRegisters);

        int instructions = 0;
        int limit = 100000;
        while (
                thread.getCounter().getOffset() != RETURN_ADDRESS
                && instructions < limit) {
            thread.stepInstruction();
            instructions++;
        }
        if (thread.getCounter().getOffset() != RETURN_ADDRESS) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "startup did not return after %d instructions; pc=%s",
                    instructions, thread.getCounter()));
        }

        verifyRegisters(thread, protectedRegisters, expectedRegisters);
        verifyStartupMemory(thread);
        println(String.format(
                Locale.ROOT,
                "VQ_BOOT_EMU status=PASS language=%s rom_sha256=%s"
                + " instructions=%d initializer_callees=%d",
                languageId, sha256(image), instructions,
                INITIALIZER_CALLEES.length));
    }

    long[] seedAndSnapshot(
            PcodeThread<byte[]> thread, String[] names) {
        long seed = 0x11223344L;
        for (String name : names) {
            if (
                    !name.equals("r15")
                    && !name.equals("pr")
                    && !name.equals("gbr")) {
                setRegister(thread, name, seed);
            }
            seed += 0x01010101L;
        }
        long[] result = new long[names.length];
        for (int index = 0; index < names.length; index++) {
            result[index] = readRegister(thread, names[index]);
        }
        return result;
    }

    void verifyRegisters(
            PcodeThread<byte[]> thread,
            String[] names,
            long[] expected) {
        for (int index = 0; index < names.length; index++) {
            long actual = readRegister(thread, names[index]);
            if (actual != expected[index]) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "%s changed %08x -> %08x",
                        names[index], expected[index], actual));
            }
        }
    }

    void verifyStartupMemory(PcodeThread<byte[]> thread) {
        byte[] state = readMemory(thread, SELECTOR_STATE, 8);
        if (!Arrays.equals(state, new byte[8])) {
            throw new IllegalStateException(
                    "invalid startup index did not normalize to map 1: "
                    + Arrays.toString(state));
        }

        byte[] expectedFuel = new byte[12];
        System.arraycopy(
                image, (int) FUEL_MAP_1,
                expectedFuel, 0, 8);
        System.arraycopy(
                image, (int) FUEL_STOCK_TAIL,
                expectedFuel, 8, 4);
        byte[] actualFuel = readMemory(thread, FUEL_SHADOW, 12);
        if (!Arrays.equals(actualFuel, expectedFuel)) {
            throw new IllegalStateException("fuel shadow differs");
        }

        byte[] expectedThrottle = Arrays.copyOfRange(
                image,
                (int) THROTTLE_CLUSTER,
                (int) THROTTLE_CLUSTER + 28);
        byte[] actualThrottle = readMemory(
                thread, THROTTLE_SHADOW, 28);
        if (!Arrays.equals(actualThrottle, expectedThrottle)) {
            throw new IllegalStateException("throttle shadow differs");
        }
        byte[] expectedRuntime = Arrays.copyOfRange(
                expectedThrottle,
                THROTTLE_SELECTED_OFFSET,
                THROTTLE_SELECTED_OFFSET + 2);
        byte[] actualRuntime = readMemory(
                thread, THROTTLE_RUNTIME, 2);
        if (!Arrays.equals(actualRuntime, expectedRuntime)) {
            throw new IllegalStateException(
                    "stock throttle runtime scalar differs");
        }
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
