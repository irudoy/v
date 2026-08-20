// EmulateMapSwitchingComposition.java - execute every exact-JK08A
// map-switching p-code case from one deterministic in-memory composition.
//
// The fixture begins with the exact 1 MiB stock program, applies all nine
// SHA-locked blobs, 15 hook literals, 48 calibration copies, and twelve pointer
// tables, and verifies the same SHA-256 and write boundary as the Python
// composer. Every test case receives a fresh emulator state loaded from those
// complete bytes.
//
// Deterministic stubs replace only stock callees outside the map-switching
// implementation after the composition itself has passed. Feedback cases may
// replace only the two documented frame-count bytes in emulator memory.
// The script never changes the current program and never writes a ROM file.
//
// Usage (headless):
//   -postScript EmulateMapSwitchingComposition.java \
//       <selector-host-blob> <adapter-helper-blob> <lookup-adapters-blob> \
//       <full-dfco-adapter-blob> <startup-wrapper-blob> \
//       <limiter-commit-blob> \
//       <feedback-wrapper-blob> <feedback-engine-blob> \
//       <idle-ignition-adapter-blob>
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
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

public class EmulateMapSwitchingComposition extends GhidraScript {

    static final int ROM_SIZE = 0x00100000;
    static final long RETURN_ADDRESS = 0x000D4100L;
    static final long STACK_TOP = 0xFFFF7F00L;
    static final long ENTRY_SR = 0x000000A1L;

    static final long SELECTOR_HOST = 0x000D2108L;
    static final long ADAPTER_HELPER = 0x000D2270L;
    static final long STARTUP_WRAPPER = 0x000D22A0L;
    static final long OVER_RUN_ADAPTER = 0x000D2300L;
    static final long IGNITION_ADAPTER = 0x000D2340L;
    static final long FUEL_COMP_ADAPTER = 0x000D2380L;
    static final long EXHAUST_CVTC_TARGET_ADAPTER = 0x000D23C0L;
    static final long FULL_DFCO_ADAPTER = 0x000D2480L;
    static final long FEEDBACK_WRAPPER = 0x000D35E0L;
    static final long LIMITER_COMMIT = 0x000D3660L;
    static final long FEEDBACK_ENGINE = 0x000D3760L;
    static final long IDLE_IGNITION_ADAPTER = 0x000D4000L;

    static final long STOCK_SELECTOR_HOST = 0x000D09D8L;
    static final long STOCK_INITIALIZER = 0x0002C648L;
    static final long STOCK_SERIALIZER = 0x000C5372L;

    static final long CURRENT_CODE = 0xFFFF2A85L;
    static final long ASCD_STATUS = 0xFFFF41AEL;
    static final long DIAGNOSTIC_STATUS = 0xFFFF2A84L;
    static final long PAYLOAD = 0xFFFF3AD5L;
    static final long CONFIG_ADDRESS = 0x000D3848L;

    static final long RAM_SENTINEL_BASE = 0xFFFF5CF0L;
    static final int RAM_SENTINEL_SIZE = 0x60;
    static final long RAM_RESERVATION_START = 0xFFFF5D00L;
    static final long RAM_RESERVATION_END = 0xFFFF5D3CL;
    static final long SELECTOR_STATE = 0xFFFF5D00L;
    static final long FUEL_SHADOW = 0xFFFF5D10L;
    static final long THROTTLE_SHADOW = 0xFFFF5D20L;
    static final long THROTTLE_RUNTIME = 0xFFFF1796L;

    static final long FUEL_STOCK = 0x0000934EL;
    static final long THROTTLE_STOCK = 0x00009424L;
    static final int THROTTLE_SELECTED_OFFSET = 8;

    static final String STOCK_SHA =
            "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23";
    static final String COMPOSED_SHA =
            "7eb703d38eef2ab51cd4a2b2b28a7a80e24d475debc1b8ddf69b6ccd7e96b222";

    static final byte[] RETURN_STUB = {
        0x00, 0x0B, 0x00, 0x09,
    };

    // mov.l @(0xc5380,pc),r1; mov #-0x4b,r0; mov.b r0,@r1; rts; nop
    // followed by alignment padding and the 0xFFFF3ADA literal.
    static final byte[] SERIALIZER_STUB = {
        (byte) 0xD1, 0x03, (byte) 0xE0, (byte) 0xB5,
        0x21, 0x00, 0x00, 0x0B, 0x00, 0x09,
        0x00, 0x09, 0x00, 0x09,
        (byte) 0xFF, (byte) 0xFF, 0x3A, (byte) 0xDA,
    };

    static final byte[] PAYLOAD_SEED = {
        0x11, 0x22, 0x33, 0x44, 0x55, 0x00, 0x77, (byte) 0x88,
    };

    record UnitSpec(
            String key,
            int argument,
            long start,
            int size,
            String sha) {
    }

    record HookSpec(
            String key,
            long address,
            long stock,
            long replacement) {
    }

    record FamilySpec(
            String key,
            long canonical,
            int size,
            long pointerTable,
            long[] copies) {

        long[] slots() {
            long[] result = new long[copies.length + 1];
            result[0] = canonical;
            System.arraycopy(copies, 0, result, 1, copies.length);
            return result;
        }
    }

    record AdapterSpec(
            String family,
            long entry,
            long stockWrapper) {
    }

    record PassThrough(
            String name,
            long entry,
            long stockWrapper,
            long requestedBase) {
    }

    record SelectorCase(
            String name,
            byte[] initialState,
            int previousCode,
            int currentCode,
            int ascdStatus,
            int diagnosticStatus,
            byte[] expectedState) {
    }

    static final UnitSpec[] UNITS = {
        new UnitSpec(
                "selector_host", 0, 0x000D2108L, 0x168,
                "ebc0fb3e4ccd177e47c4420b90fb49a360e00f3bedceca11b3cdf2a4590e6e4c"),
        new UnitSpec(
                "adapter_select_helper", 1, 0x000D2270L, 0x30,
                "40cea0183a38d189808b7637ea47cb594d8cb56ee615efb246c714da5f499a34"),
        new UnitSpec(
                "lookup_adapters", 2, 0x000D2300L, 0x100,
                "a938e1334e7850a0c368c50e98dbbdf67bc2589524025659a31d5b5f328c0e6c"),
        new UnitSpec(
                "full_dfco_adapter", 3, 0x000D2480L, 0x60,
                "2a5a65671e077400b753cb7fabb15c0520ddd7e96be8234e44297b6cd7052ba7"),
        new UnitSpec(
                "startup_wrapper", 4, 0x000D22A0L, 0x60,
                "352db08c013f1f3b91551afea5a12db60cb160698d7239e1e8ac7271054ac4a3"),
        new UnitSpec(
                "limiter_commit", 5, 0x000D3660L, 0x100,
                "e1e296e0d2f1dccef21982f14f4e3e1aebdc39fba6b68ae8b3e2ecbc16d5a5aa"),
        new UnitSpec(
                "cruise_feedback_wrapper", 6, 0x000D35E0L, 0x80,
                "b8e8c20cd365f27b7a8df59318f22911621ef51a33dfefc128563940be558d36"),
        new UnitSpec(
                "cruise_feedback_engine", 7, 0x000D3760L, 0x100,
                "0e0501f3d91e18a17c6a9bf7c4ebd187809c094fbf701f9d2864fd4792f9b32e"),
        new UnitSpec(
                "idle_ignition_adapter", 8, 0x000D4000L, 0x40,
                "122017573894f95daba3e94805fed278b65302243f161c7fa1ea59b2b26c4f35"),
    };

    static final HookSpec[] HOOKS = {
        new HookSpec(
                "selector_host_call", 0x000CE8DCL,
                0x000D09D8L, 0x000D2108L),
        new HookSpec(
                "startup_initializer", 0x00027D28L,
                0x0002C648L, 0x000D22A0L),
        new HookSpec(
                "overrun_cut_lookup", 0x0004FDD0L,
                0x00026388L, 0x000D2480L),
        new HookSpec(
                "overrun_restore_lookup", 0x00050258L,
                0x00026388L, 0x000D2480L),
        new HookSpec(
                "ignition_lookup_493e8", 0x000496C0L,
                0x00026230L, 0x000D2340L),
        new HookSpec(
                "ignition_lookup_4e1c0_a", 0x0004E474L,
                0x00026230L, 0x000D2340L),
        new HookSpec(
                "ignition_lookup_4e1c0_b", 0x0004E58CL,
                0x00026230L, 0x000D2340L),
        new HookSpec(
                "fuel_compensation_lookup_2c648", 0x0002CF1CL,
                0x000261F0L, 0x000D2380L),
        new HookSpec(
                "fuel_compensation_lookup_3be3c", 0x0003C388L,
                0x000261F0L, 0x000D2380L),
        new HookSpec(
                "exhaust_cvtc_target_lookup", 0x000C0020L,
                0x000261B8L, 0x000D23C0L),
        new HookSpec(
                "rev_fuel_cut_base", 0x0004F468L,
                0x0000934EL, 0xFFFF5D10L),
        new HookSpec(
                "rev_throttle_cluster_base", 0x00075964L,
                0x00009424L, 0xFFFF5D20L),
        new HookSpec(
                "rev_throttle_scalar_base", 0x00077BACL,
                0x0000942CL, 0xFFFF5D28L),
        new HookSpec(
                "cruise_feedback_serializer", 0x000C3FA4L,
                0x000C5372L, 0x000D35E0L),
        new HookSpec(
                "idle_ignition_lookup", 0x0004B224L,
                0x00026370L, 0x000D4000L),
    };

    static final FamilySpec[] FAMILIES = {
        new FamilySpec(
                "over_run_fuel_hold", 0x000126E4L, 16, 0x000D24E0L,
                new long[]{
                    0x000D3F80L, 0x000D3F90L,
                    0x000D3FA0L, 0x000D3FB0L,
                }),
        new FamilySpec(
                "over_run_fuel_cut", 0x00012718L, 16, 0x000D3540L,
                new long[]{
                    0x000D2400L, 0x000D2410L,
                    0x000D2420L, 0x000D2430L,
                }),
        new FamilySpec(
                "over_run_fuel_restore", 0x00012818L, 16, 0x000D3554L,
                new long[]{
                    0x000D2440L, 0x000D2450L,
                    0x000D2460L, 0x000D2470L,
                }),
        new FamilySpec(
                "over_run_fuel_intermediate_restore", 0x0001298CL, 16,
                0x000D3528L,
                new long[]{
                    0x000D3FC0L, 0x000D3FD0L,
                    0x000D3FE0L, 0x000D3FF0L,
                }),
        new FamilySpec(
                "high_octane_timing_state", 0x00009A1AL, 256,
                0x000D3568L,
                new long[]{
                    0x000D2500L, 0x000D2600L,
                    0x000D2700L, 0x000D2800L,
                }),
        new FamilySpec(
                "high_detonation_timing_state", 0x00009B1AL, 256,
                0x000D357CL,
                new long[]{
                    0x000D2900L, 0x000D2A00L,
                    0x000D2B00L, 0x000D2C00L,
                }),
        new FamilySpec(
                "cold_idle_ignition_timing", 0x00012196L, 8,
                0x000D4040L,
                new long[]{
                    0x000D4080L, 0x000D4088L,
                    0x000D4090L, 0x000D4098L,
                }),
        new FamilySpec(
                "idle_ignition_timing", 0x0001219EL, 8,
                0x000D4054L,
                new long[]{
                    0x000D40A0L, 0x000D40A8L,
                    0x000D40B0L, 0x000D40B8L,
                }),
        new FamilySpec(
                "exhaust_cvtc_target", 0x0000B33AL, 256, 0x000D3590L,
                new long[]{
                    0x000D2D00L, 0x000D2E00L,
                    0x000D2F00L, 0x000D3000L,
                }),
        new FamilySpec(
                "fuel_compensation_main", 0x0000A29AL, 256,
                0x000D35A4L,
                new long[]{
                    0x000D3100L, 0x000D3200L,
                    0x000D3300L, 0x000D3400L,
                }),
        new FamilySpec(
                "rev_limit_fuel_cut", 0x0000934EL, 8, 0x000D35B8L,
                new long[]{
                    0x000D3500L, 0x000D3508L,
                    0x000D3510L, 0x000D3518L,
                }),
        new FamilySpec(
                "rev_limit_throttle_cut", 0x0000942CL, 2,
                0x000D35CCL,
                new long[]{
                    0x000D3520L, 0x000D3522L,
                    0x000D3524L, 0x000D3526L,
                }),
    };

    static final AdapterSpec[] ADAPTERS = {
        new AdapterSpec(
                "over_run_fuel_cut", OVER_RUN_ADAPTER, 0x00026388L),
        new AdapterSpec(
                "over_run_fuel_restore", OVER_RUN_ADAPTER, 0x00026388L),
        new AdapterSpec(
                "over_run_fuel_hold", FULL_DFCO_ADAPTER, 0x00026388L),
        new AdapterSpec(
                "over_run_fuel_cut", FULL_DFCO_ADAPTER, 0x00026388L),
        new AdapterSpec(
                "over_run_fuel_restore", FULL_DFCO_ADAPTER, 0x00026388L),
        new AdapterSpec(
                "over_run_fuel_intermediate_restore",
                FULL_DFCO_ADAPTER, 0x00026388L),
        new AdapterSpec(
                "high_octane_timing_state",
                IGNITION_ADAPTER, 0x00026230L),
        new AdapterSpec(
                "high_detonation_timing_state",
                IGNITION_ADAPTER, 0x00026230L),
        new AdapterSpec(
                "fuel_compensation_main",
                FUEL_COMP_ADAPTER, 0x000261F0L),
        new AdapterSpec(
                "exhaust_cvtc_target",
                EXHAUST_CVTC_TARGET_ADAPTER, 0x000261B8L),
        new AdapterSpec(
                "cold_idle_ignition_timing",
                IDLE_IGNITION_ADAPTER, 0x00026370L),
        new AdapterSpec(
                "idle_ignition_timing",
                IDLE_IGNITION_ADAPTER, 0x00026370L),
    };

    static final PassThrough[] PASS_THROUGHS = {
        new PassThrough(
                "overrun_bosch_cut",
                OVER_RUN_ADAPTER, 0x00026388L, 0x000126E4L),
        new PassThrough(
                "overrun_bosch_restore",
                OVER_RUN_ADAPTER, 0x00026388L, 0x0001298CL),
        new PassThrough(
                "full_dfco_unknown",
                FULL_DFCO_ADAPTER, 0x00026388L, 0x0001298DL),
        new PassThrough(
                "ignition_cold",
                IGNITION_ADAPTER, 0x00026230L, 0x0000991AL),
        new PassThrough(
                "fuel_compensation_unknown",
                FUEL_COMP_ADAPTER, 0x000261F0L, 0x0000A29BL),
        new PassThrough(
                "exhaust_cvtc_target_unknown",
                EXHAUST_CVTC_TARGET_ADAPTER, 0x000261B8L, 0x0000B33BL),
        new PassThrough(
                "idle_ignition_hidden",
                IDLE_IGNITION_ADAPTER, 0x00026370L, 0x000121A6L),
    };

    static final long[] CODE_ENTRIES = {
        SELECTOR_HOST,
        ADAPTER_HELPER,
        STARTUP_WRAPPER,
        OVER_RUN_ADAPTER,
        IGNITION_ADAPTER,
        FUEL_COMP_ADAPTER,
        EXHAUST_CVTC_TARGET_ADAPTER,
        FULL_DFCO_ADAPTER,
        FEEDBACK_WRAPPER,
        LIMITER_COMMIT,
        FEEDBACK_ENGINE,
        IDLE_IGNITION_ADAPTER,
    };

    static final long[][] CHECKSUM_FIELDS = {
        {0x00008200L, 2},
        {0x00020000L, 2},
        {0x000096D4L, 4},
        {0x000096DCL, 4},
        {0x00020404L, 4},
        {0x00020408L, 4},
    };

    byte[] stockRom;
    byte[] compositeRom;
    byte[][] unitBlobs;
    Language language;
    AddressSpace space;
    final Set<Long> executedPcs = new HashSet<>();

    int selectorCases;
    int adapterCases;
    int limiterCases;
    int feedbackCases;
    int feedbackInvocations;
    int selectorInstructions;
    int adapterInstructions;
    int limiterInstructions;
    int feedbackInstructions;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != UNITS.length) {
            throw new IllegalArgumentException(
                    "need nine blobs in manifest order: selector, helper, "
                    + "adapters, full DFCO, startup, limiter, feedback wrapper, "
                    + "feedback engine, idle ignition adapter");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException(
                    "unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        buildComposition(args);

        runAdapterCases();
        runLimiterCases();
        runSelectorCases();
        runFeedbackCases();
        verifyTotals();

        int totalCases = selectorCases + adapterCases
                + limiterCases + feedbackCases;
        int totalInstructions = selectorInstructions + adapterInstructions
                + limiterInstructions + feedbackInstructions;
        println(String.format(
                "VQ_COMPOSITION_EMU status=PASS language=%s"
                + " fixture_sha256=%s cases=%d"
                + " selector=%d adapters=%d limiter=%d feedback=%d"
                + " feedback_invocations=%d instructions=%d"
                + " entries=%d hooks=%d changed_bytes=5803"
                + " permitted_write_bytes=6316",
                languageId, COMPOSED_SHA, totalCases,
                selectorCases, adapterCases, limiterCases, feedbackCases,
                feedbackInvocations, totalInstructions,
                CODE_ENTRIES.length, HOOKS.length));
    }

    void buildComposition(String[] args) throws Exception {
        stockRom = readProgram(0, ROM_SIZE);
        String stockDigest = sha256(stockRom);
        if (!stockDigest.equals(STOCK_SHA)) {
            throw new IllegalStateException(
                    "stock program SHA-256 is " + stockDigest
                    + ", expected " + STOCK_SHA);
        }
        compositeRom = stockRom.clone();
        boolean[] permitted = new boolean[ROM_SIZE];
        unitBlobs = new byte[UNITS.length][];

        for (FamilySpec family : FAMILIES) {
            byte[] source = slice(
                    stockRom, family.canonical(), family.size());
            for (long copy : family.copies()) {
                writeDeclared(
                        compositeRom, permitted, copy, source,
                        family.key() + ".copy");
            }
            writeDeclared(
                    compositeRom, permitted, family.pointerTable(),
                    encodeLongs(family.slots()),
                    family.key() + ".pointer_table");
        }
        for (HookSpec hook : HOOKS) {
            long actual = readUnsigned32(stockRom, hook.address());
            if (actual != hook.stock()) {
                throw new IllegalStateException(String.format(
                        Locale.ROOT,
                        "%s: stock hook at %08x is %08x, expected %08x",
                        hook.key(), hook.address(), actual, hook.stock()));
            }
            writeDeclared(
                    compositeRom, permitted, hook.address(),
                    encodeUnsigned(hook.replacement(), 4),
                    "hook." + hook.key());
        }
        for (int index = 0; index < UNITS.length; index++) {
            UnitSpec unit = UNITS[index];
            byte[] blob = readLocked(
                    Path.of(args[unit.argument()]),
                    unit.size(), unit.sha(), unit.key());
            unitBlobs[index] = blob;
            writeDeclared(
                    compositeRom, permitted, unit.start(), blob,
                    "assembly." + unit.key());
        }
        compositeRom[(int) CONFIG_ADDRESS] = 30;
        compositeRom[(int) CONFIG_ADDRESS + 1] = 30;

        int changed = 0;
        int permittedBytes = 0;
        for (int offset = 0; offset < ROM_SIZE; offset++) {
            if (permitted[offset]) {
                permittedBytes++;
            }
            if (stockRom[offset] != compositeRom[offset]) {
                if (!permitted[offset]) {
                    throw new IllegalStateException(String.format(
                            "composition changed undeclared byte %08x",
                            offset));
                }
                changed++;
            }
        }
        if (changed != 5803 || permittedBytes != 6316) {
            throw new IllegalStateException(
                    "composition boundary differs: changed=" + changed
                    + " permitted=" + permittedBytes);
        }
        String digest = sha256(compositeRom);
        if (!digest.equals(COMPOSED_SHA)) {
            throw new IllegalStateException(
                    "composed SHA-256 is " + digest
                    + ", expected " + COMPOSED_SHA);
        }
        if (
                compositeRom[(int) CONFIG_ADDRESS] != 30
                || compositeRom[(int) CONFIG_ADDRESS + 1] != 30) {
            throw new IllegalStateException(
                    "locked feedback frame counts are not 30/30");
        }
        for (long[] field : CHECKSUM_FIELDS) {
            byte[] stock = slice(stockRom, field[0], (int) field[1]);
            byte[] composed = slice(compositeRom, field[0], (int) field[1]);
            if (!Arrays.equals(stock, composed)) {
                throw new IllegalStateException(String.format(
                        "stored checksum field changed at %08x", field[0]));
            }
        }
    }

    void writeDeclared(
            byte[] destination,
            boolean[] permitted,
            long address,
            byte[] bytes,
            String name) {
        int start = checkedRomOffset(address, bytes.length, name);
        for (int offset = start; offset < start + bytes.length; offset++) {
            if (permitted[offset]) {
                throw new IllegalStateException(
                        name + ": composition write overlaps at "
                        + String.format("%08x", offset));
            }
            permitted[offset] = true;
        }
        System.arraycopy(bytes, 0, destination, start, bytes.length);
    }

    int checkedRomOffset(long address, int size, String name) {
        if (address < 0 || size < 0 || address + size > ROM_SIZE) {
            throw new IllegalArgumentException(
                    name + ": range is outside the stock ROM");
        }
        return (int) address;
    }

    byte[] slice(byte[] source, long address, int size) {
        int start = checkedRomOffset(address, size, "slice");
        return Arrays.copyOfRange(source, start, start + size);
    }

    long readUnsigned32(byte[] source, long address) {
        int start = checkedRomOffset(address, 4, "u32");
        return ((long) (source[start] & 0xFF) << 24)
                | ((long) (source[start + 1] & 0xFF) << 16)
                | ((long) (source[start + 2] & 0xFF) << 8)
                | (long) (source[start + 3] & 0xFF);
    }

    byte[] encodeUnsigned(long value, int size) {
        return Utils.longToBytes(value, size, language.isBigEndian());
    }

    FamilySpec family(String key) {
        for (FamilySpec family : FAMILIES) {
            if (family.key().equals(key)) {
                return family;
            }
        }
        throw new IllegalArgumentException("unknown family " + key);
    }

    PcodeEmulator newCompositeEmulator(String name) {
        PcodeEmulator emulator = new PcodeEmulator(language);
        setMemory(emulator.getSharedState(), 0, compositeRom);
        return emulator;
    }

    void runAdapterCases() throws Exception {
        for (AdapterSpec adapter : ADAPTERS) {
            FamilySpec family = family(adapter.family());
            long[] slots = family.slots();
            for (int index = 0; index < 5; index++) {
                runAdapterCase(
                        adapter.family() + ".map_" + (index + 1),
                        adapter.entry(), adapter.stockWrapper(),
                        family.canonical(), index, slots[index], family);
            }
            runAdapterCase(
                    adapter.family() + ".invalid_5",
                    adapter.entry(), adapter.stockWrapper(),
                    family.canonical(), 5, slots[0], family);
            runAdapterCase(
                    adapter.family() + ".invalid_255",
                    adapter.entry(), adapter.stockWrapper(),
                    family.canonical(), 0xFF, slots[0], family);
        }
        for (PassThrough vector : PASS_THROUGHS) {
            runAdapterCase(
                    vector.name(), vector.entry(), vector.stockWrapper(),
                    vector.requestedBase(), 4, vector.requestedBase(), null);
        }
    }

    void runAdapterCase(
            String name,
            long entry,
            long stockWrapper,
            long requestedBase,
            int activeIndex,
            long expectedBase,
            FamilySpec selectedFamily) throws Exception {
        PcodeEmulator emulator = newCompositeEmulator(name);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        byte[] expectedRam = seedRam(
                shared, state(activeIndex, 0, 0, 0, 0, 0, 0, 0));

        PcodeThread<byte[]> thread = emulator.newThread(name);
        initializeThread(thread, entry, stockWrapper, 0);
        setRegister(thread, "r4", requestedBase);
        setRegister(thread, "r5", 0x51525354L);
        setRegister(thread, "r6", 0x61626364L);
        setRegister(thread, "r7", 0x71727374L);

        String[] protectedRegisters = {
            "r5", "r6", "r7", "r8", "r9", "r10", "r11",
            "r12", "r13", "r14", "r15", "pr", "gbr", "mach", "macl",
        };
        long[] before = seedAndSnapshot(
                thread, protectedRegisters,
                Set.of("r5", "r6", "r7", "pr"));

        int executed = stepUntil(
                thread, stockWrapper, 40, "adapter." + name);
        if (readRegister(thread, "r4") != expectedBase) {
            throw new IllegalStateException(String.format(
                    "%s: r4=%08x expected=%08x",
                    name, readRegister(thread, "r4"), expectedBase));
        }
        verifyRegisters(thread, protectedRegisters, before, name);
        verifySrExceptT(thread, 0, name);
        byte[] actualRam = readMemory(
                thread, RAM_SENTINEL_BASE, RAM_SENTINEL_SIZE);
        if (!Arrays.equals(actualRam, expectedRam)) {
            throw new IllegalStateException(name + ": adapter changed RAM");
        }
        if (selectedFamily != null) {
            byte[] expected = slice(
                    compositeRom,
                    selectedFamily.canonical(),
                    selectedFamily.size());
            byte[] actual = readMemory(
                    thread, expectedBase, selectedFamily.size());
            if (!Arrays.equals(actual, expected)) {
                throw new IllegalStateException(
                        name + ": selected calibration bytes differ");
            }
        }
        adapterCases++;
        adapterInstructions += executed;
    }

    void runLimiterCases() throws Exception {
        int[] requestedIndices = {0, 1, 2, 3, 4, 5, 0xFF};
        for (int requested : requestedIndices) {
            runLimiterCase("commit." + requested, false, requested);
            runLimiterCase("startup." + requested, true, requested);
        }
    }

    void runLimiterCase(String name, boolean throughStartup, int requested)
            throws Exception {
        int normalized = requested >= 0 && requested < 5 ? requested : 0;
        int expectedIndex = throughStartup ? 0 : normalized;
        PcodeEmulator emulator = newCompositeEmulator(name);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, STOCK_INITIALIZER, RETURN_STUB);
        byte[] initialState = state(
                throughStartup ? requested : 0xA5,
                0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5, 0xA5);
        seedRam(shared, initialState);
        setMemory(
                shared, THROTTLE_RUNTIME,
                new byte[]{(byte) 0xA5, (byte) 0xA5});

        PcodeThread<byte[]> thread = emulator.newThread(name);
        initializeThread(
                thread,
                throughStartup ? STARTUP_WRAPPER : LIMITER_COMMIT,
                RETURN_ADDRESS,
                ENTRY_SR);
        setRegister(thread, "r4", requested);

        String[] protectedRegisters = {
            "r8", "r9", "r10", "r11", "r12", "r13", "r14",
            "r15", "pr", "gbr", "mach", "macl",
        };
        long[] before = seedAndSnapshot(
                thread, protectedRegisters, Set.of("r15", "pr"));

        int executed = stepUntil(
                thread, RETURN_ADDRESS, 200, "limiter." + name);
        if (readRegister(thread, "r4") != expectedIndex) {
            throw new IllegalStateException(name + ": normalized r4 differs");
        }
        if (readRegister(thread, "sr") != ENTRY_SR) {
            throw new IllegalStateException(String.format(
                    "%s: SR=%08x expected=%08x",
                    name, readRegister(thread, "sr"), ENTRY_SR));
        }
        verifyRegisters(thread, protectedRegisters, before, name);
        verifyLimiterMemory(thread, name, expectedIndex);
        limiterCases++;
        limiterInstructions += executed;
    }

    void verifyLimiterMemory(
            PcodeThread<byte[]> thread, String name, int normalized) {
        FamilySpec fuel = family("rev_limit_fuel_cut");
        FamilySpec throttle = family("rev_limit_throttle_cut");
        long[] fuelSlots = fuel.slots();
        long[] throttleSlots = throttle.slots();

        byte[] expectedFuel = new byte[12];
        byte[] selectedFuel = slice(
                compositeRom, fuelSlots[normalized], fuel.size());
        System.arraycopy(
                selectedFuel, 0, expectedFuel, 0, selectedFuel.length);
        System.arraycopy(
                stockRom, (int) FUEL_STOCK + fuel.size(),
                expectedFuel, fuel.size(), expectedFuel.length - fuel.size());

        byte[] expectedThrottle = slice(
                stockRom, THROTTLE_STOCK, 28);
        byte[] selectedThrottle = slice(
                compositeRom, throttleSlots[normalized], throttle.size());
        System.arraycopy(
                selectedThrottle, 0,
                expectedThrottle, THROTTLE_SELECTED_OFFSET,
                selectedThrottle.length);

        byte[] expectedRam = filled(RAM_SENTINEL_SIZE, 0xA5);
        int selectorOffset = ramOffset(SELECTOR_STATE);
        expectedRam[selectorOffset] = (byte) normalized;
        Arrays.fill(
                expectedRam, selectorOffset + 1, selectorOffset + 8,
                (byte) 0x00);
        System.arraycopy(
                expectedFuel, 0, expectedRam,
                ramOffset(FUEL_SHADOW), expectedFuel.length);
        System.arraycopy(
                expectedThrottle, 0, expectedRam,
                ramOffset(THROTTLE_SHADOW), expectedThrottle.length);

        byte[] actualRam = readMemory(
                thread, RAM_SENTINEL_BASE, RAM_SENTINEL_SIZE);
        if (!Arrays.equals(actualRam, expectedRam)) {
            throw new IllegalStateException(
                    name + ": selector/shadow RAM differs");
        }
        byte[] actualRuntime = readMemory(thread, THROTTLE_RUNTIME, 2);
        if (!Arrays.equals(actualRuntime, selectedThrottle)) {
            throw new IllegalStateException(
                    name + ": stock throttle runtime scalar differs");
        }
    }

    void runSelectorCases() throws Exception {
        SelectorCase[] tests = {
            selectorTest(
                    "idle", state(0, 0, 0, 0, 0, 0, 0, 0),
                    0x20, 0x20, 0,
                    state(0, 0, 0, 0, 0, 0, 0, 0)),
            selectorTest(
                    "arm", state(0, 0, 0, 0, 0, 0, 0, 0),
                    0x20, 8, 0, state(0, 1, 0, 1, 0, 0, 0, 0)),
            selectorTest(
                    "set-held", state(1, 1, 2, 7, 0, 0, 0, 0),
                    8, 8, 0, state(1, 1, 2, 8, 0, 0, 0, 0)),
            selectorTest(
                    "set-to-cancel", state(1, 1, 2, 7, 0, 0, 0, 0),
                    8, 2, 0, state(1, 2, 2, 8, 0, 0, 0, 0)),
            selectorTest(
                    "cancel-held", state(2, 2, 3, 9, 0, 0, 0, 0),
                    2, 2, 0, state(2, 2, 3, 10, 0, 0, 0, 0)),
            selectorTest(
                    "cancel-to-set", state(2, 2, 3, 9, 0, 0, 0, 0),
                    2, 8, 0, state(2, 1, 4, 10, 0, 0, 0, 0)),
            selectorTest(
                    "commit-map-1", state(3, 1, 1, 9, 0, 0, 0, 0),
                    8, 0x20, 0, state(0, 0, 0, 0, 1, 1, 0, 0)),
            selectorTest(
                    "commit-map-5", state(1, 1, 5, 9, 0, 0, 0, 0),
                    8, 0x20, 0, state(4, 0, 0, 0, 5, 1, 0, 0)),
            selectorTest(
                    "release-zero-abort",
                    state(3, 1, 0, 9, 0, 0, 0, 0),
                    8, 0, 0, state(3, 0, 0, 0, 0, 0, 0, 0)),
            selectorTest(
                    "sixth-pulse-abort",
                    state(2, 2, 5, 9, 0, 0, 0, 0),
                    2, 8, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            selectorTest(
                    "timeout-abort",
                    state(2, 1, 2, 99, 0, 0, 0, 0),
                    8, 8, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            selectorTest(
                    "ascd-abort", state(2, 1, 2, 9, 0, 0, 0, 0),
                    8, 8, 0x80, state(2, 0, 0, 0, 0, 0, 0, 0)),
            selectorTest(
                    "feedback-blocks",
                    state(2, 1, 2, 9, 3, 1, 4, 0),
                    8, 0, 0, state(2, 0, 0, 0, 3, 1, 4, 0)),
            selectorTest(
                    "feedback-corrupt",
                    state(2, 1, 2, 9, 6, 1, 4, 0),
                    8, 0, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            selectorTest(
                    "idle-feedback-corrupt",
                    state(2, 1, 2, 9, 0, 0, 1, 0),
                    8, 0, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            selectorTest(
                    "selector-corrupt",
                    state(2, 3, 2, 9, 0, 0, 0, 0),
                    8, 0, 0, state(2, 0, 0, 0, 0, 0, 0, 0)),
            selectorTest(
                    "invalid-index",
                    state(0xFF, 1, 2, 9, 3, 1, 4, 0),
                    8, 0, 0, state(0, 0, 0, 0, 0, 0, 0, 0)),
        };
        for (SelectorCase test : tests) {
            runSelectorCase(test);
        }
    }

    SelectorCase selectorTest(
            String name,
            byte[] initial,
            int previous,
            int current,
            int ascd,
            byte[] expected) {
        return new SelectorCase(
                name, initial, previous, current, ascd, 0x25, expected);
    }

    void runSelectorCase(SelectorCase test) throws Exception {
        PcodeEmulator emulator = newCompositeEmulator(test.name());
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, STOCK_SELECTOR_HOST, RETURN_STUB);
        seedRam(shared, test.initialState());
        setMemory(
                shared, THROTTLE_RUNTIME,
                new byte[]{(byte) 0xA5, (byte) 0xA5});
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
        initializeThread(
                thread, SELECTOR_HOST, RETURN_ADDRESS, ENTRY_SR);
        String[] protectedRegisters = {
            "r8", "r9", "r10", "r11", "r12", "r13", "r14",
            "r15", "pr", "gbr", "mach", "macl",
        };
        long[] before = seedAndSnapshot(
                thread, protectedRegisters, Set.of("r15", "pr"));

        int executed = stepUntil(
                thread, RETURN_ADDRESS, 500,
                "selector." + test.name());
        verifyRegisters(
                thread, protectedRegisters, before, test.name());
        verifySrExceptT(thread, ENTRY_SR, test.name());
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
        verifyRamGuards(thread, test.name());
        verifyOptionalSelectorShadows(thread, test.name(), active);
        selectorCases++;
        selectorInstructions += executed;
    }

    void verifyOptionalSelectorShadows(
            PcodeThread<byte[]> thread, String name, int active) {
        byte[] fuelShadow = readMemory(thread, FUEL_SHADOW, 12);
        byte[] throttleShadow = readMemory(thread, THROTTLE_SHADOW, 28);
        byte[] runtime = readMemory(thread, THROTTLE_RUNTIME, 2);
        boolean untouched = allValue(fuelShadow, 0xA5)
                && allValue(throttleShadow, 0xA5)
                && allValue(runtime, 0xA5);
        if (untouched) {
            return;
        }
        FamilySpec fuel = family("rev_limit_fuel_cut");
        FamilySpec throttle = family("rev_limit_throttle_cut");
        int normalized = active < 5 ? active : 0;

        byte[] expectedFuel = new byte[12];
        byte[] selectedFuel = slice(
                compositeRom, fuel.slots()[normalized], fuel.size());
        System.arraycopy(
                selectedFuel, 0, expectedFuel, 0, selectedFuel.length);
        System.arraycopy(
                stockRom, (int) FUEL_STOCK + fuel.size(),
                expectedFuel, fuel.size(), expectedFuel.length - fuel.size());

        byte[] expectedThrottle = slice(stockRom, THROTTLE_STOCK, 28);
        byte[] selectedThrottle = slice(
                compositeRom, throttle.slots()[normalized], throttle.size());
        System.arraycopy(
                selectedThrottle, 0,
                expectedThrottle, THROTTLE_SELECTED_OFFSET,
                selectedThrottle.length);
        if (
                !Arrays.equals(fuelShadow, expectedFuel)
                || !Arrays.equals(throttleShadow, expectedThrottle)
                || !Arrays.equals(runtime, selectedThrottle)) {
            throw new IllegalStateException(
                    name + ": selector commit shadows differ");
        }
    }

    void runFeedbackCases() throws Exception {
        runFeedbackSequence(
                "disabled", 0, state(0, 0, 0, 0, 1, 1, 0, 0),
                new int[]{0xB5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runFeedbackSequence(
                "two-pulses-2x2", 0x0202,
                state(0, 0, 0, 0, 2, 1, 0, 0),
                new int[]{
                    0xE5, 0xE5, 0x85, 0x85,
                    0xE5, 0xE5, 0x85, 0x85,
                },
                state(0, 0, 0, 0, 0, 0, 0, 0));
        runFeedbackSequence(
                "one-pulse-1x1", 0x0101,
                state(0, 0, 0, 0, 1, 1, 0, 0),
                new int[]{0xE5, 0x85},
                state(0, 0, 0, 0, 0, 0, 0, 0));
        runFeedbackSequence(
                "idle", 0x0202, state(0, 0, 0, 0, 0, 0, 0, 0),
                new int[]{0xB5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runFeedbackSequence(
                "corrupt-pulses", 0x0202,
                state(0, 0, 0, 0, 6, 1, 0, 0),
                new int[]{0xB5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runFeedbackSequence(
                "corrupt-phase", 0x0202,
                state(0, 0, 0, 0, 1, 3, 0, 0),
                new int[]{0xB5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runFeedbackSequence(
                "corrupt-idle", 0x0202,
                state(0, 0, 0, 0, 0, 0, 1, 0),
                new int[]{0xB5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runFeedbackSequence(
                "missing-off-count", 0x0200,
                state(0, 0, 0, 0, 1, 1, 0, 0),
                new int[]{0xB5}, state(0, 0, 0, 0, 0, 0, 0, 0));
        runFeedbackSequence(
                "missing-on-count", 0x0002,
                state(0, 0, 0, 0, 1, 1, 0, 0),
                new int[]{0xB5}, state(0, 0, 0, 0, 0, 0, 0, 0));
    }

    void runFeedbackSequence(
            String name,
            int counts,
            byte[] initialState,
            int[] expectedStatuses,
            byte[] expectedFinalState) throws Exception {
        PcodeEmulator emulator = newCompositeEmulator(name);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, STOCK_SERIALIZER, SERIALIZER_STUB);
        setMemory(
                shared, CONFIG_ADDRESS,
                new byte[]{(byte) (counts >>> 8), (byte) counts});
        seedRam(shared, initialState);
        setMemory(shared, PAYLOAD, PAYLOAD_SEED);

        PcodeThread<byte[]> thread = emulator.newThread(name);
        thread.overrideContextWithDefault();
        thread.reInitialize();
        setRegister(thread, "sr", ENTRY_SR);
        setRegister(thread, "r15", STACK_TOP);

        String[] protectedRegisters = {
            "r8", "r9", "r10", "r11", "r12", "r13", "r14",
            "r15", "gbr", "mach", "macl",
        };
        long[] before = seedAndSnapshot(
                thread, protectedRegisters, Set.of("r15"));

        for (int expectedStatus : expectedStatuses) {
            thread.setCounter(toAddress(FEEDBACK_WRAPPER));
            setRegister(thread, "pr", RETURN_ADDRESS);
            int executed = stepUntil(
                    thread, RETURN_ADDRESS, 300,
                    "feedback." + name);
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
            feedbackInvocations++;
            feedbackInstructions += executed;
        }
        byte[] actualState = readMemory(thread, SELECTOR_STATE, 8);
        if (!Arrays.equals(actualState, expectedFinalState)) {
            throw new IllegalStateException(
                    name + ": feedback state differs: "
                    + Arrays.toString(actualState));
        }
        verifyRegisters(thread, protectedRegisters, before, name);
        verifySrExceptT(thread, ENTRY_SR, name);
        verifyRamGuards(thread, name);
        feedbackCases++;
    }

    void initializeThread(
            PcodeThread<byte[]> thread,
            long entry,
            long returnAddress,
            long sr) {
        thread.overrideContextWithDefault();
        thread.reInitialize();
        thread.setCounter(toAddress(entry));
        setRegister(thread, "sr", sr);
        setRegister(thread, "pr", returnAddress);
        setRegister(thread, "r15", STACK_TOP);
    }

    int stepUntil(
            PcodeThread<byte[]> thread,
            long stop,
            int limit,
            String name) throws Exception {
        int executed = 0;
        while (
                thread.getCounter().getOffset() != stop
                && executed < limit) {
            executedPcs.add(thread.getCounter().getOffset());
            thread.stepInstruction();
            executed++;
        }
        if (thread.getCounter().getOffset() != stop) {
            throw new IllegalStateException(
                    name + ": did not reach stop, pc="
                    + thread.getCounter());
        }
        return executed;
    }

    byte[] seedRam(
            PcodeExecutorState<byte[]> shared, byte[] selectorState) {
        if (selectorState.length != 8) {
            throw new IllegalArgumentException(
                    "selector state must contain eight bytes");
        }
        byte[] sentinel = filled(RAM_SENTINEL_SIZE, 0xA5);
        System.arraycopy(
                selectorState, 0, sentinel,
                ramOffset(SELECTOR_STATE), selectorState.length);
        setMemory(shared, RAM_SENTINEL_BASE, sentinel);
        return sentinel;
    }

    void verifyRamGuards(PcodeThread<byte[]> thread, String name) {
        byte[] ram = readMemory(
                thread, RAM_SENTINEL_BASE, RAM_SENTINEL_SIZE);
        int reservationStart = ramOffset(RAM_RESERVATION_START);
        int reservationEnd = ramOffset(RAM_RESERVATION_END);
        for (int offset = 0; offset < ram.length; offset++) {
            boolean outside = offset < reservationStart
                    || offset >= reservationEnd;
            boolean internalGap =
                    (offset >= ramOffset(SELECTOR_STATE) + 8
                            && offset < ramOffset(FUEL_SHADOW))
                    || (offset >= ramOffset(FUEL_SHADOW) + 12
                            && offset < ramOffset(THROTTLE_SHADOW));
            if ((outside || internalGap) && (ram[offset] & 0xFF) != 0xA5) {
                throw new IllegalStateException(String.format(
                        "%s: RAM guard changed at %08x",
                        name, RAM_SENTINEL_BASE + offset));
            }
        }
    }

    int ramOffset(long address) {
        long offset = address - RAM_SENTINEL_BASE;
        if (offset < 0 || offset >= RAM_SENTINEL_SIZE) {
            throw new IllegalArgumentException(
                    String.format(
                            "RAM address %08x is outside sentinel", address));
        }
        return (int) offset;
    }

    byte[] state(int... values) {
        byte[] result = new byte[values.length];
        for (int index = 0; index < values.length; index++) {
            result[index] = (byte) values[index];
        }
        return result;
    }

    byte[] filled(int size, int value) {
        byte[] result = new byte[size];
        Arrays.fill(result, (byte) value);
        return result;
    }

    boolean allValue(byte[] values, int expected) {
        for (byte value : values) {
            if ((value & 0xFF) != expected) {
                return false;
            }
        }
        return true;
    }

    long[] seedAndSnapshot(
            PcodeThread<byte[]> thread,
            String[] names,
            Set<String> initialized) {
        long seed = 0x11223344L;
        for (String name : names) {
            if (!initialized.contains(name)) {
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
            long[] expected,
            String caseName) {
        for (int index = 0; index < names.length; index++) {
            long actual = readRegister(thread, names[index]);
            if (actual != expected[index]) {
                throw new IllegalStateException(String.format(
                        "%s: %s changed %08x -> %08x",
                        caseName, names[index], expected[index], actual));
            }
        }
    }

    void verifySrExceptT(
            PcodeThread<byte[]> thread, long entrySr, String caseName) {
        long actual = readRegister(thread, "sr");
        if ((actual & 0xFFFFFFFEL) != (entrySr & 0xFFFFFFFEL)) {
            throw new IllegalStateException(String.format(
                    "%s: non-T SR bits changed %08x -> %08x",
                    caseName, entrySr, actual));
        }
    }

    void verifyTotals() {
        if (
                selectorCases != 17
                || adapterCases != 91
                || limiterCases != 14
                || feedbackCases != 9
                || feedbackInvocations != 17) {
            throw new IllegalStateException(
                    "case totals differ: selector=" + selectorCases
                    + " adapters=" + adapterCases
                    + " limiter=" + limiterCases
                    + " feedback=" + feedbackCases
                    + " invocations=" + feedbackInvocations);
        }
        int totalInstructions = selectorInstructions + adapterInstructions
                + limiterInstructions + feedbackInstructions;
        if (totalInstructions != 5409) {
            throw new IllegalStateException(
                    "instruction total is " + totalInstructions
                    + ", expected 5409");
        }
        List<String> missing = new ArrayList<>();
        for (long entry : CODE_ENTRIES) {
            if (!executedPcs.contains(entry)) {
                missing.add(String.format("%08x", entry));
            }
        }
        if (!missing.isEmpty()) {
            throw new IllegalStateException(
                    "composed code entries were not executed: "
                    + String.join(", ", missing));
        }
    }

    byte[] readProgram(long address, int size) throws Exception {
        byte[] result = new byte[size];
        int read = currentProgram.getMemory().getBytes(
                toAddress(address), result);
        if (read != size) {
            throw new IllegalStateException(String.format(
                    "stock read %08x got %d of %d bytes",
                    address, read, size));
        }
        return result;
    }

    byte[] readLocked(
            Path path,
            int expectedLength,
            String expectedSha,
            String name) throws Exception {
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

    byte[] encodeLongs(long[] values) {
        byte[] result = new byte[values.length * 4];
        for (int index = 0; index < values.length; index++) {
            byte[] encoded = encodeUnsigned(values[index], 4);
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
