// EmulateMapSwitchingAdapters.java - execute the assembled exact-JK08A lookup
// adapters in Ghidra's SuperH p-code emulator.
//
// The test loads only the two raw assembly units and synthetic selector and
// pointer-table state. It stops when each adapter reaches its exact stock
// wrapper. It does not execute stock firmware, patch the current program, or
// write a ROM.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingAdapters.java \
//       <adapter-helper-blob> <lookup-adapters-blob>
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
import java.util.List;
import java.util.Locale;

public class EmulateMapSwitchingAdapters extends GhidraScript {

    static final long HELPER_BASE = 0x000D2270L;
    static final long ADAPTER_BASE = 0x000D2300L;
    static final long SELECTOR_ADDRESS = 0xFFFF5D00L;
    static final String HELPER_SHA =
            "40cea0183a38d189808b7637ea47cb594d8cb56ee615efb246c714da5f499a34";
    static final String ADAPTER_SHA =
            "a938e1334e7850a0c368c50e98dbbdf67bc2589524025659a31d5b5f328c0e6c";

    static class Vector {
        final String name;
        final long adapter;
        final long stockWrapper;
        final long canonicalBase;
        final long pointerTable;
        final long[] slotBases;

        Vector(
                String name,
                long adapter,
                long stockWrapper,
                long canonicalBase,
                long pointerTable,
                long... slotBases) {
            this.name = name;
            this.adapter = adapter;
            this.stockWrapper = stockWrapper;
            this.canonicalBase = canonicalBase;
            this.pointerTable = pointerTable;
            this.slotBases = slotBases;
            if (slotBases.length != 5 || slotBases[0] != canonicalBase) {
                throw new IllegalArgumentException(
                        name + ": expected five bases beginning with stock");
            }
        }
    }

    static class PassThrough {
        final String name;
        final long adapter;
        final long stockWrapper;
        final long requestedBase;

        PassThrough(
                String name,
                long adapter,
                long stockWrapper,
                long requestedBase) {
            this.name = name;
            this.adapter = adapter;
            this.stockWrapper = stockWrapper;
            this.requestedBase = requestedBase;
        }
    }

    final Vector[] vectors = {
        new Vector(
                "over_run_fuel_cut",
                0x000D2300L, 0x00026388L, 0x00012718L, 0x000D3540L,
                0x00012718L, 0x000D2400L, 0x000D2410L,
                0x000D2420L, 0x000D2430L),
        new Vector(
                "over_run_fuel_restore",
                0x000D2300L, 0x00026388L, 0x00012818L, 0x000D3554L,
                0x00012818L, 0x000D2440L, 0x000D2450L,
                0x000D2460L, 0x000D2470L),
        new Vector(
                "ignition_timing_trim_main",
                0x000D2340L, 0x00026230L, 0x00009A1AL, 0x000D3568L,
                0x00009A1AL, 0x000D2500L, 0x000D2600L,
                0x000D2700L, 0x000D2800L),
        new Vector(
                "ignition_timing_trim_high_det",
                0x000D2340L, 0x00026230L, 0x00009B1AL, 0x000D357CL,
                0x00009B1AL, 0x000D2900L, 0x000D2A00L,
                0x000D2B00L, 0x000D2C00L),
        new Vector(
                "fuel_compensation_main",
                0x000D2380L, 0x000261F0L, 0x0000A29AL, 0x000D35A4L,
                0x0000A29AL, 0x000D3100L, 0x000D3200L,
                0x000D3300L, 0x000D3400L),
        new Vector(
                "fuel_targets",
                0x000D23C0L, 0x000261B8L, 0x0000B33AL, 0x000D3590L,
                0x0000B33AL, 0x000D2D00L, 0x000D2E00L,
                0x000D2F00L, 0x000D3000L),
    };

    final PassThrough[] passThroughs = {
        new PassThrough(
                "overrun_bosch_cut",
                0x000D2300L, 0x00026388L, 0x000126E4L),
        new PassThrough(
                "overrun_bosch_restore",
                0x000D2300L, 0x00026388L, 0x0001298CL),
        new PassThrough(
                "ignition_cold",
                0x000D2340L, 0x00026230L, 0x0000991AL),
        new PassThrough(
                "fuel_compensation_unknown",
                0x000D2380L, 0x000261F0L, 0x0000A29BL),
        new PassThrough(
                "fuel_targets_unknown",
                0x000D23C0L, 0x000261B8L, 0x0000B33BL),
    };

    byte[] helper;
    byte[] adapters;
    Language language;
    AddressSpace space;
    int cases;
    int instructions;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "need: <adapter-helper-blob> <lookup-adapters-blob>");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        helper = readLocked(
                Path.of(args[0]), 0x30, HELPER_SHA, "helper");
        adapters = readLocked(
                Path.of(args[1]), 0x100, ADAPTER_SHA, "adapters");

        for (Vector vector : vectors) {
            for (int index = 0; index < 5; index++) {
                runCase(
                        vector.name + ".map_" + (index + 1),
                        vector.adapter,
                        vector.stockWrapper,
                        vector.canonicalBase,
                        index,
                        vector.slotBases[index]);
            }
            runCase(
                    vector.name + ".invalid_5",
                    vector.adapter,
                    vector.stockWrapper,
                    vector.canonicalBase,
                    5,
                    vector.slotBases[0]);
            runCase(
                    vector.name + ".invalid_255",
                    vector.adapter,
                    vector.stockWrapper,
                    vector.canonicalBase,
                    0xFF,
                    vector.slotBases[0]);
        }
        for (PassThrough vector : passThroughs) {
            runCase(
                    vector.name,
                    vector.adapter,
                    vector.stockWrapper,
                    vector.requestedBase,
                    4,
                    vector.requestedBase);
        }
        println(String.format(
                "VQ_ADAPTER_EMU status=PASS language=%s cases=%d"
                + " instructions=%d",
                languageId, cases, instructions));
    }

    void runCase(
            String name,
            long entry,
            long stockWrapper,
            long requestedBase,
            int activeIndex,
            long expectedBase) throws Exception {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, HELPER_BASE, helper);
        setMemory(shared, ADAPTER_BASE, adapters);
        for (Vector vector : vectors) {
            setMemory(
                    shared, vector.pointerTable, encodeLongs(vector.slotBases));
        }
        setMemory(
                shared, SELECTOR_ADDRESS,
                new byte[]{(byte) activeIndex});

        PcodeThread<byte[]> thread = emulator.newThread(name);
        thread.overrideContextWithDefault();
        thread.reInitialize();
        thread.setCounter(toAddress(entry));
        setRegister(thread, "sr", 0);

        long[] volatileInputs = {
            0x51525354L,
            0x61626364L,
            0x71727374L,
        };
        setRegister(thread, "r4", requestedBase);
        setRegister(thread, "r5", volatileInputs[0]);
        setRegister(thread, "r6", volatileInputs[1]);
        setRegister(thread, "r7", volatileInputs[2]);

        List<String> protectedRegisters = new ArrayList<>();
        for (int number = 5; number <= 15; number++) {
            protectedRegisters.add("r" + number);
        }
        protectedRegisters.add("pr");
        protectedRegisters.add("gbr");
        protectedRegisters.add("mach");
        protectedRegisters.add("macl");
        long seed = 0x10203040L;
        for (String register : protectedRegisters) {
            if (register.equals("r5")
                    || register.equals("r6")
                    || register.equals("r7")) {
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
                thread.getCounter().getOffset() != stockWrapper
                && executed < 40) {
            thread.stepInstruction();
            executed++;
        }
        if (thread.getCounter().getOffset() != stockWrapper) {
            throw new IllegalStateException(
                    name + ": did not reach stock wrapper, pc="
                    + thread.getCounter());
        }
        if (readRegister(thread, "r4") != expectedBase) {
            throw new IllegalStateException(String.format(
                    "%s: r4=%08x expected=%08x",
                    name, readRegister(thread, "r4"), expectedBase));
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
        cases++;
        instructions += executed;
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
