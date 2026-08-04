// EmulateMapSwitchingTrampoline.java - compare the exact stock startup thunk
// through the hardware-readback baseline and the minimal tail trampoline gate.
//
// Direct callees of FUN_0002C648 are replaced with the same deterministic
// return-zero stubs in both runs. The complete initializer body still executes.
// The gate must enter 0xD22A0, tail-jump to 0x2C648, return through the original
// PR, and produce register and RAM state identical to the baseline.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingTrampoline.java <baseline-rom> <gate-rom>
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

public class EmulateMapSwitchingTrampoline extends GhidraScript {

    static final int ROM_SIZE = 0x100000;
    static final long STARTUP_THUNK = 0x00027CE4L;
    static final long STOCK_INITIALIZER = 0x0002C648L;
    static final long TRAMPOLINE = 0x000D22A0L;
    static final long RETURN_ADDRESS = 0x000D4000L;
    static final long STACK_TOP = 0xFFFF7FFCL;
    static final long ENTRY_SR = 0x000000F0L;
    static final long ENTRY_GBR = 0xFFFF9F28L;
    static final long RAM_START = 0xFFFF0000L;
    static final int RAM_SIZE = 0xC000;
    static final long SELECTOR_STATE = 0xFFFF5D00L;

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
        final boolean sawTrampoline;
        final boolean sawInitializer;
        final long[] registers;
        final byte[] ram;

        Result(
                int instructions,
                long minSp,
                boolean sawTrampoline,
                boolean sawInitializer,
                long[] registers,
                byte[] ram) {
            this.instructions = instructions;
            this.minSp = minSp;
            this.sawTrampoline = sawTrampoline;
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
                    "need: <baseline-rom> <gate-rom>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        byte[] baselineImage = readImage(args[0]);
        byte[] gateImage = readImage(args[1]);

        Result baseline = execute(baselineImage);
        Result gate = execute(gateImage);
        if (baseline.sawTrampoline) {
            throw new IllegalStateException(
                    "baseline unexpectedly entered the trampoline");
        }
        if (!baseline.sawInitializer || !gate.sawInitializer) {
            throw new IllegalStateException(
                    "stock initializer was not reached in both runs");
        }
        if (!gate.sawTrampoline) {
            throw new IllegalStateException(
                    "gate did not enter the trampoline");
        }
        // Ghidra executes JMP and its delay-slot NOP in one p-code step. The
        // three physical trampoline instructions therefore add two steps.
        if (gate.instructions != baseline.instructions + 2) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "p-code step delta is %d, expected 2",
                    gate.instructions - baseline.instructions));
        }
        verifyRegisters(baseline, gate);
        if (!Arrays.equals(baseline.ram, gate.ram)) {
            int offset = firstDifference(baseline.ram, gate.ram);
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "RAM differs at %08x: baseline=%02x gate=%02x",
                    RAM_START + offset,
                    baseline.ram[offset] & 0xFF,
                    gate.ram[offset] & 0xFF));
        }
        if (baseline.minSp != gate.minSp) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "minimum SP differs: baseline=%08x gate=%08x",
                    baseline.minSp, gate.minSp));
        }

        println(String.format(
                Locale.ROOT,
                "VQ_TRAMPOLINE_EMU status=PASS language=%s"
                + " baseline_sha256=%s gate_sha256=%s"
                + " baseline_instructions=%d gate_instructions=%d"
                + " delta=%d min_sp=%08x initializer_callees=%d",
                languageId,
                sha256(baselineImage),
                sha256(gateImage),
                baseline.instructions,
                gate.instructions,
                gate.instructions - baseline.instructions,
                gate.minSp,
                INITIALIZER_CALLEES.length));
    }

    Result execute(byte[] image) throws Exception {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, 0, image);
        setMemory(shared, RAM_START, new byte[RAM_SIZE]);
        setMemory(shared, SELECTOR_STATE, new byte[]{(byte) 0xA5});
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
        boolean sawTrampoline = false;
        boolean sawInitializer = false;
        while (
                thread.getCounter().getOffset() != RETURN_ADDRESS
                && instructions < limit) {
            long pc = thread.getCounter().getOffset();
            sawTrampoline |= pc == TRAMPOLINE;
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
                sawTrampoline,
                sawInitializer,
                registers,
                ram);
    }

    void verifyRegisters(Result baseline, Result gate) {
        for (int index = 0; index < RESULT_REGISTERS.length; index++) {
            if (baseline.registers[index] != gate.registers[index]) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "%s differs: baseline=%08x gate=%08x",
                        RESULT_REGISTERS[index],
                        baseline.registers[index],
                        gate.registers[index]));
            }
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
