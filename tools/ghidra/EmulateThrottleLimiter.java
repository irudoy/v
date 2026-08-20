// EmulateThrottleLimiter.java - execute the exact stock JK08A rotational-speed
// request limiter and a declared isolated downstream throttle-target projection.
//
// The limiter cases execute unmodified instructions at 0x0007584e from the
// SHA-locked stock ROM. Synthetic calibration values are used only in cases
// that exercise stock-inert threshold-ramp branches. The optional CSV sweep
// treats all other signed request bounds as permissive, publishes
// min(APP request, limiter request) through 0x00070d82 and 0x00079030, sets the
// idle/opening-area additions to zero, and enables the normal two-channel
// target path. It is an isolated transfer projection, not a vehicle prediction.
//
// Usage (headless):
//   -postScript EmulateThrottleLimiter.java [<sweep.csv>]
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
import java.io.PrintWriter;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class EmulateThrottleLimiter extends GhidraScript {

    static final int ROM_SIZE = 0x100000;
    static final long RAM_START = 0xFFFF0000L;
    static final int RAM_SIZE = 0xC000;
    static final long STACK_TOP = 0xFFFF7F00L;
    static final long RETURN_ADDRESS = 0x000DFF00L;

    static final long LIMITER = 0x0007584EL;
    static final long REQUEST_SELECTOR = 0x00070D82L;
    static final long REQUEST_BOUNDARY = 0x00079030L;
    static final long SPEED_NORMALIZER = 0x0003DE4CL;
    static final long REQUEST_TO_AREA = 0x000730FCL;
    static final long AREA_COMPOSITOR = 0x00072C3CL;
    static final long CHANNEL_TARGET = 0x0006F48CL;

    static final long CAL_BASE = 0x00009424L;
    static final long CAL_THRESHOLD = 0x0000942CL;
    static final long CAL_OVERRIDE_CAP = 0x0000942EL;
    static final long CAL_THRESHOLD_DOWN = 0x00009430L;
    static final long CAL_ALTERNATE_THRESHOLD = 0x00009434L;
    static final long CAL_THRESHOLD_UP = 0x00009436L;
    static final long CAL_AUX_DURATION = 0x0000943EL;
    static final long AUX_TABLE = 0x00014384L;

    static final long SPEED_RAW = 0xFFFF11B6L;
    static final long SPEED_FILTERED = 0xFFFF1794L;
    static final long DYNAMIC_THRESHOLD = 0xFFFF1796L;
    static final long BLENDED_THRESHOLD = 0xFFFF1798L;
    static final long LIMITER_OUTPUT = 0xFFFF19D8L;
    static final long RAMP_STATE = 0xFFFF19DAL;
    static final long RECOVERY_STATE = 0xFFFF19DCL;
    static final long SHARED_REQUEST = 0xFFFF19C6L;
    static final long APP_REQUEST = 0xFFFF243CL;
    static final long SELECTED_LIMIT = 0xFFFF243AL;
    static final long SELECTOR_FLAGS = 0xFFFF2490L;
    static final long SPEED_FILTER_FLAGS = 0xFFFF2485L;
    static final long COOLANT_FLAGS = 0xFFFF249EL;
    static final long RAMP_FLAGS = 0xFFFF24A3L;
    static final long RAMP_MODE = 0xFFFF25B0L;
    static final long RAW_COOLANT = 0xFFFF1071L;
    static final long CURRENT_GEAR_INDEX = 0xFFFF1082L;
    static final long TARGET_GEAR_INDEX = 0xFFFF1083L;
    static final long GEAR_PHASE_INDEX = 0xFFFF1064L;
    static final long DYNAMIC_ENABLE_FLAGS = 0xFFFF84C3L;
    static final long THRESHOLD_CAP_FLAGS = 0xFFFF4188L;
    static final long FORCE_NEUTRAL_FLAGS = 0xFFFF4252L;
    static final long AUX_REQUEST = 0xFFFF2400L;
    static final long AUX_DURATION = 0xFFFF413CL;

    static final long REQUEST_UPPER_0 = 0xFFFF34B8L;
    static final long REQUEST_UPPER_1 = 0xFFFF34BAL;
    static final long REQUEST_UPPER_2 = 0xFFFF34B4L;
    static final long SELECTOR_LOWER = 0xFFFF34CAL;
    static final long SELECTOR_LOWER_2 = 0xFFFF3482L;
    static final long SELECTOR_UPPER_2 = 0xFFFF347EL;
    static final long REQUEST_LOWER = 0xFFFF3484L;
    static final long REQUEST_UPPER_3 = 0xFFFF3480L;
    static final long ARBITER_LIMIT = 0xFFFF349AL;
    static final long CONTROLLER_LOWER = 0xFFFF413AL;
    static final long CONTROLLER_UPPER = 0xFFFF4138L;

    static final long AREA_REQUEST = 0xFFFF183EL;
    static final long IDLE_AREA = 0xFFFF1340L;
    static final long AREA_SUBTRACTION = 0xFFFF120EL;
    static final long SHARED_TARGET_AREA = 0xFFFF19B2L;
    static final long TARGET_MODE_FLAGS = 0xFFFF41A5L;
    static final long TIMING_STATE_FLAGS = 0xFFFF244FL;
    static final long TARGET_CHANNEL_0 = 0xFFFF28BCL;
    static final long TARGET_CHANNEL_1 = 0xFFFF28BEL;

    static final String STOCK_SHA256 =
            "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23";

    static class Context {
        final PcodeExecutorState<byte[]> shared;
        final PcodeThread<byte[]> thread;

        Context(PcodeExecutorState<byte[]> shared, PcodeThread<byte[]> thread) {
            this.shared = shared;
            this.thread = thread;
        }
    }

    static class SweepRow {
        final int rpm;
        final int appRequest;
        final int limiterRequest;
        final int sharedRequest;
        final int areaRequest;
        final int targetArea;
        final int channel0;
        final int channel1;

        SweepRow(
                int rpm,
                int appRequest,
                int limiterRequest,
                int sharedRequest,
                int areaRequest,
                int targetArea,
                int channel0,
                int channel1) {
            this.rpm = rpm;
            this.appRequest = appRequest;
            this.limiterRequest = limiterRequest;
            this.sharedRequest = sharedRequest;
            this.areaRequest = areaRequest;
            this.targetArea = targetArea;
            this.channel0 = channel0;
            this.channel1 = channel1;
        }
    }

    Language language;
    AddressSpace space;
    byte[] image;
    int cases;
    int instructions;

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length > 1) {
            throw new IllegalArgumentException("need: [<sweep.csv>]");
        }
        language = currentProgram.getLanguage();
        String languageId = language.getLanguageID().toString();
        if (!languageId.equals("SuperH:BE:32:SH-2A")) {
            throw new IllegalStateException("unexpected language " + languageId);
        }
        space = language.getDefaultSpace();
        image = readProgram(0, ROM_SIZE);
        String digest = sha256(image);
        if (!digest.equals(STOCK_SHA256)) {
            throw new IllegalStateException(
                    "stock ROM SHA-256 is " + digest + ", expected " + STOCK_SHA256);
        }

        testDisabledBranch();
        testSpeedFilter();
        testCoolantHysteresis();
        testDynamicThreshold();
        testRequestBoundaries();
        testFastRampMode();

        List<SweepRow> rows = runSweep();
        if (args.length == 1) {
            writeSweep(Path.of(args[0]), rows);
        }
        println(String.format(
                Locale.ROOT,
                "VQ_THROTTLE_LIMITER_EMU status=PASS language=%s"
                + " rom_sha256=%s cases=%d instructions=%d sweep_rows=%d",
                languageId, digest, cases, instructions, rows.size()));
    }

    void testDisabledBranch() throws Exception {
        Context context = newContext("disabled");
        seedLimiter(context, 2400, 1234, 321, 456, 789, 20000);
        writeU16(context.shared, CAL_THRESHOLD, 0xFFFF);
        writeU16(context.shared, AUX_REQUEST, 0x2222);
        writeU16(context.shared, AUX_DURATION, 0x3333);
        execute(context, LIMITER, 0);
        expectU16(context, LIMITER_OUTPUT, 0x7FFF, "disabled output");
        expectU16(context, SPEED_FILTERED, 1234, "disabled speed state");
        expectU16(context, RAMP_STATE, 456, "disabled ramp state");
        expectU16(context, AUX_REQUEST, 0x2222, "disabled auxiliary request");
        expectU16(context, AUX_DURATION, 0x3333, "disabled auxiliary duration");
        cases++;
    }

    void testSpeedFilter() throws Exception {
        Context first = newContext("speed_filter_first");
        seedLimiter(first, 20000, 1234, 0, 0, 0x7FFF, -32768);
        writeU8(first.shared, SPEED_FILTER_FLAGS, 0);
        execute(first, LIMITER, 0);
        expectU16(first, SPEED_FILTERED, 0xFFFF, "first-pass saturated speed");
        expectMask(first, SPEED_FILTER_FLAGS, 0x01, true, "speed filter latch");
        cases++;

        Context later = newContext("speed_filter_later");
        seedLimiter(later, 1000, 4004, 0, 0, 0x7FFF, -32768);
        execute(later, LIMITER, 0);
        expectU16(later, SPEED_FILTERED, 4003, "recursive speed filter");
        cases++;
    }

    void testCoolantHysteresis() throws Exception {
        Context context = newContext("coolant_hysteresis");
        seedLimiter(context, 2400, 9600, 0, 0, 0x7FFF, -32768);
        writeU8(context.shared, RAW_COOLANT, 255);
        execute(context, LIMITER, 0);
        expectMask(context, COOLANT_FLAGS, 0x01, true, "coolant set at 255");
        writeU8(context.shared, RAW_COOLANT, 239);
        execute(context, LIMITER, 0);
        expectMask(context, COOLANT_FLAGS, 0x01, true, "coolant retained at 239");
        writeU8(context.shared, RAW_COOLANT, 238);
        execute(context, LIMITER, 0);
        expectMask(context, COOLANT_FLAGS, 0x01, false, "coolant cleared at 238");
        cases += 3;
    }

    void testDynamicThreshold() throws Exception {
        Context down = newContext("threshold_down");
        seedLimiter(down, 2400, 9600, 9500, 0, 0x7FFF, -32768);
        writeU16(down.shared, CAL_ALTERNATE_THRESHOLD, 9000);
        writeU16(down.shared, CAL_THRESHOLD_DOWN, 16);
        writeU8(down.shared, RAW_COOLANT, 255);
        writeU8(down.shared, DYNAMIC_ENABLE_FLAGS, 0x80);
        execute(down, LIMITER, 0);
        expectU16(down, DYNAMIC_THRESHOLD, 9484, "threshold decrement");
        cases++;

        Context up = newContext("threshold_up");
        seedLimiter(up, 2400, 9600, 9000, 0, 0x7FFF, -32768);
        writeU16(up.shared, CAL_THRESHOLD_UP, 5);
        writeU8(up.shared, DYNAMIC_ENABLE_FLAGS, 0x80);
        execute(up, LIMITER, 0);
        expectU16(up, DYNAMIC_THRESHOLD, 9005, "threshold increment");
        cases++;

        Context equal = newContext("threshold_equal");
        seedLimiter(equal, 2400, 9600, 9600, 0, 0x7FFF, -32768);
        writeU16(equal.shared, CAL_THRESHOLD_DOWN, 16);
        writeU16(equal.shared, CAL_THRESHOLD_UP, 5);
        writeU8(equal.shared, DYNAMIC_ENABLE_FLAGS, 0x80);
        execute(equal, LIMITER, 0);
        expectU16(equal, DYNAMIC_THRESHOLD, 9600, "threshold equality hold");
        cases++;

        Context gated = newContext("threshold_gate_clear");
        seedLimiter(gated, 2400, 9600, 9000, 0, 0x7FFF, -32768);
        writeU16(gated.shared, CAL_THRESHOLD_UP, 5);
        execute(gated, LIMITER, 0);
        expectU16(gated, DYNAMIC_THRESHOLD, 9000, "threshold gate hold");
        cases++;

        Context capped = newContext("threshold_override_cap");
        seedLimiter(capped, 2400, 9600, 9600, 0, 0x7FFF, -32768);
        writeU16(capped.shared, CAL_OVERRIDE_CAP, 9400);
        writeU8(capped.shared, THRESHOLD_CAP_FLAGS, 0x02);
        execute(capped, LIMITER, 0);
        expectU16(capped, DYNAMIC_THRESHOLD, 9400, "mode-controlled threshold cap");
        cases++;
    }

    void testRequestBoundaries() throws Exception {
        checkRequestCase("below_deadband_13", 2397, 9587, 10000, 0x7FFF,
                20000, 9587, 9587, 10000, 10000);
        checkRequestCase("below_deadband_14", 2397, 9586, 10000, 0x7FFF,
                20000, 9586, 9587, 10001, 10016);
        checkRequestCase("equal_threshold", 2400, 9600, 10000, 0x7FFF,
                20000, 9600, 9600, 10000, 10000);
        checkRequestCase("above_one_raw", 2401, 9601, 10000, 0x7FFF,
                20000, 9601, 9600, 9998, 9982);
        checkRequestCase("above_200_rpm", 2464, 9856, 10000, 0x7FFF,
                20000, 9856, 9837, 9970, 9673);

        Context rollback = newContext("recovery_rollback");
        seedLimiter(rollback, 2464, 9856, 9600, 10000, 9000, 20000);
        execute(rollback, LIMITER, 0);
        expectS16(rollback, RECOVERY_STATE, 9050, "recovery increment");
        expectS16(rollback, LIMITER_OUTPUT, 9050, "recovery envelope output");
        expectS16(rollback, RAMP_STATE, 10000, "ramp rollback");
        cases++;

        Context tracking = newContext("recovery_tracking");
        seedLimiter(tracking, 2464, 9856, 9600, 10000, 12000, 20000);
        writeU8(tracking.shared, CURRENT_GEAR_INDEX, 0);
        writeU8(tracking.shared, TARGET_GEAR_INDEX, 1);
        execute(tracking, LIMITER, 0);
        expectS16(tracking, RECOVERY_STATE, 9673, "recovery tracks lower request");
        expectS16(tracking, LIMITER_OUTPUT, 9673, "tracked limiter output");
        expectS16(tracking, AUX_REQUEST, 1300, "auxiliary request table index 1");
        expectU16(tracking, AUX_DURATION, 182, "auxiliary duration");
        cases++;

        Context neutral = newContext("forced_neutral");
        seedLimiter(neutral, 2464, 9856, 9600, 10000, 12000, 20000);
        writeU8(neutral.shared, FORCE_NEUTRAL_FLAGS, 0x02);
        writeU16(neutral.shared, SHARED_REQUEST, 1234);
        execute(neutral, LIMITER, 0);
        expectU16(neutral, LIMITER_OUTPUT, 0x7FFF, "forced-neutral output");
        expectS16(neutral, RAMP_STATE, 1234, "forced-neutral ramp synchronization");
        cases++;

        Context equalRequest = newContext("previous_equals_app");
        seedLimiter(equalRequest, 2400, 9600, 9600, 10000, 0x7FFF, 5000);
        writeU16(equalRequest.shared, LIMITER_OUTPUT, 5000);
        writeU8(equalRequest.shared, RAMP_MODE, 7);
        writeU8(equalRequest.shared, RAMP_FLAGS, 0x04);
        execute(equalRequest, LIMITER, 0);
        expectS16(equalRequest, RAMP_STATE, 5000, "equality resets ramp to APP");
        expectU8(equalRequest, RAMP_MODE, 100, "equality resets ramp mode");
        expectMask(equalRequest, RAMP_FLAGS, 0x04, false, "equality clears ramp latch");
        cases++;
    }

    void testFastRampMode() throws Exception {
        Context fast = newContext("fast_ramp_mode");
        seedLimiter(fast, 2464, 9856, 9600, 10000, 0x7FFF, 20000);
        writeU16(fast.shared, LIMITER_OUTPUT, 0x7FFF);
        execute(fast, LIMITER, 0);
        expectS16(fast, RAMP_STATE, 10000, "inactive pass retains neutral-entry ramp");
        expectS16(fast, LIMITER_OUTPUT, 9703, "inactive pass applies final reduction");
        expectU8(fast, RAMP_MODE, 100, "inactive pass loads fast mode");
        expectMask(fast, RAMP_FLAGS, 0x04, false, "inactive pass clears ramp latch");
        cases++;

        execute(fast, LIMITER, 0);
        expectS16(fast, RAMP_STATE, 9777, "fast rate applies while ramp is positive");
        expectS16(fast, LIMITER_OUTPUT, 9480, "fast-rate output");
        expectMask(fast, RAMP_FLAGS, 0x04, false, "positive ramp leaves latch clear");
        cases++;

        Context transition = newContext("fast_ramp_transition");
        seedLimiter(transition, 2464, 9856, 9600, 0, 0x7FFF, 20000);
        writeU8(transition.shared, RAMP_MODE, 100);
        execute(transition, LIMITER, 0);
        expectMask(transition, RAMP_FLAGS, 0x04, true, "nonpositive ramp sets latch");
        cases++;
    }

    void checkRequestCase(
            String name,
            int speedRaw,
            int speedPrevious,
            int ramp,
            int recovery,
            int app,
            int expectedSpeed,
            int expectedBlend,
            int expectedRamp,
            int expectedOutput) throws Exception {
        Context context = newContext(name);
        seedLimiter(
                context, speedRaw, speedPrevious, 9600,
                ramp, recovery, app);
        execute(context, LIMITER, 0);
        expectU16(context, SPEED_FILTERED, expectedSpeed, name + " speed");
        expectU16(context, BLENDED_THRESHOLD, expectedBlend, name + " blend");
        expectS16(context, RAMP_STATE, expectedRamp, name + " ramp");
        expectS16(context, LIMITER_OUTPUT, expectedOutput, name + " output");
        cases++;
    }

    List<SweepRow> runSweep() throws Exception {
        int[] appRequests = {5000, 10000, 20000, 30000};
        List<SweepRow> rows = new ArrayList<>();
        for (int appRequest : appRequests) {
            for (int rpm = 7200; rpm <= 7800; rpm += 100) {
                int speedRaw = rpm * 8 / 25;
                Context context = newContext(
                        "sweep_" + appRequest + "_" + rpm);
                seedLimiter(
                        context, speedRaw, speedRaw * 4, 9600,
                        appRequest, 0x7FFF, appRequest);
                writeU16(context.shared, LIMITER_OUTPUT, 0x7FFF);
                for (int tick = 0; tick < 20; tick++) {
                    execute(context, LIMITER, 0);
                }
                int limiterRequest = readS16(context, LIMITER_OUTPUT);
                int projectedRequest = Math.min(appRequest, limiterRequest);
                seedTransparentRequestBoundary(context, projectedRequest);
                execute(context, REQUEST_SELECTOR, 0);
                execute(context, REQUEST_BOUNDARY, 0);
                int sharedRequest = readS16(context, SHARED_REQUEST);
                if (sharedRequest != projectedRequest) {
                    throw new IllegalStateException(
                            "isolated request boundary changed " + projectedRequest
                            + " to " + sharedRequest);
                }
                execute(context, SPEED_NORMALIZER, 0);
                execute(context, REQUEST_TO_AREA, 0);
                writeU16(context.shared, IDLE_AREA, 0);
                writeU16(context.shared, AREA_SUBTRACTION, 0);
                execute(context, AREA_COMPOSITOR, 0);
                seedChannelTargetPath(context);
                execute(context, CHANNEL_TARGET, 0);
                execute(context, CHANNEL_TARGET, 1);
                int channel0 = readU16(context, TARGET_CHANNEL_0);
                int channel1 = readU16(context, TARGET_CHANNEL_1);
                if (channel0 != channel1) {
                    throw new IllegalStateException(
                            "symmetric channel projection diverged: "
                            + channel0 + " != " + channel1);
                }
                rows.add(new SweepRow(
                        rpm,
                        appRequest,
                        limiterRequest,
                        sharedRequest,
                        readU16(context, AREA_REQUEST),
                        readU16(context, SHARED_TARGET_AREA),
                        channel0,
                        channel1));
                cases++;
            }
        }
        return rows;
    }

    void seedLimiter(
            Context context,
            int speedRaw,
            int speedPrevious,
            int dynamicThreshold,
            int ramp,
            int recovery,
            int app) {
        writeU16(context.shared, SPEED_RAW, speedRaw);
        writeU16(context.shared, SPEED_FILTERED, speedPrevious);
        writeU16(context.shared, DYNAMIC_THRESHOLD, dynamicThreshold);
        writeU16(context.shared, RAMP_STATE, ramp);
        writeU16(context.shared, RECOVERY_STATE, recovery);
        writeU16(context.shared, LIMITER_OUTPUT, 0);
        writeU16(context.shared, APP_REQUEST, app);
        writeU8(context.shared, SPEED_FILTER_FLAGS, 0x01);
        writeU8(context.shared, COOLANT_FLAGS, 0);
        writeU8(context.shared, RAMP_FLAGS, 0);
        writeU8(context.shared, RAMP_MODE, 0);
        writeU8(context.shared, RAW_COOLANT, 100);
        writeU8(context.shared, CURRENT_GEAR_INDEX, 0);
        writeU8(context.shared, TARGET_GEAR_INDEX, 0);
        writeU8(context.shared, GEAR_PHASE_INDEX, 0);
        writeU8(context.shared, DYNAMIC_ENABLE_FLAGS, 0);
        writeU8(context.shared, THRESHOLD_CAP_FLAGS, 0);
        writeU8(context.shared, FORCE_NEUTRAL_FLAGS, 0);
    }

    void seedTransparentRequestBoundary(Context context, int request) {
        writeU16(context.shared, SELECTED_LIMIT, request);
        writeU8(context.shared, SELECTOR_FLAGS, 0);
        writeU16(context.shared, REQUEST_UPPER_0, 0x7FFF);
        writeU16(context.shared, REQUEST_UPPER_1, 0x7FFF);
        writeU16(context.shared, REQUEST_UPPER_2, 0x7FFF);
        writeU16(context.shared, SELECTOR_LOWER, 0x8000);
        writeU16(context.shared, SELECTOR_LOWER_2, 0x8000);
        writeU16(context.shared, SELECTOR_UPPER_2, 0x7FFF);
        writeU16(context.shared, REQUEST_LOWER, 0x8000);
        writeU16(context.shared, REQUEST_UPPER_3, 0x7FFF);
        writeU16(context.shared, ARBITER_LIMIT, 0x7FFF);
        writeU16(context.shared, CONTROLLER_LOWER, 0x8000);
        writeU16(context.shared, CONTROLLER_UPPER, 0x7FFF);
    }

    void seedChannelTargetPath(Context context) {
        writeU8(context.shared, TARGET_MODE_FLAGS, 0x04);
        writeU8(context.shared, TIMING_STATE_FLAGS, 0x20);
    }

    Context newContext(String name) {
        PcodeEmulator emulator = new PcodeEmulator(language);
        PcodeExecutorState<byte[]> shared = emulator.getSharedState();
        setMemory(shared, 0, image);
        setMemory(shared, RAM_START, new byte[RAM_SIZE]);
        PcodeThread<byte[]> thread = emulator.newThread(name);
        thread.overrideContextWithDefault();
        thread.reInitialize();
        for (int index = 0; index <= 15; index++) {
            setRegister(thread, "r" + index, 0);
        }
        setRegister(thread, "sr", 0);
        setRegister(thread, "gbr", 0);
        setRegister(thread, "mach", 0);
        setRegister(thread, "macl", 0);
        setRegister(thread, "pr", 0);
        return new Context(shared, thread);
    }

    void execute(Context context, long entry, long r4) {
        context.thread.setCounter(toAddress(entry));
        setRegister(context.thread, "pr", RETURN_ADDRESS);
        setRegister(context.thread, "r15", STACK_TOP);
        setRegister(context.thread, "r4", r4);
        int executed = 0;
        int limit = 200000;
        while (
                context.thread.getCounter().getOffset() != RETURN_ADDRESS
                && executed < limit) {
            context.thread.stepInstruction();
            executed++;
        }
        if (context.thread.getCounter().getOffset() != RETURN_ADDRESS) {
            throw new IllegalStateException(String.format(
                    Locale.ROOT,
                    "entry %08x did not return after %d instructions; pc=%s",
                    entry, executed, context.thread.getCounter()));
        }
        instructions += executed;
    }

    void writeSweep(Path path, List<SweepRow> rows) throws Exception {
        try (PrintWriter writer = new PrintWriter(path.toFile())) {
            writer.println(
                    "rpm,app_request,limiter_request,shared_request,"
                    + "area_request,target_area,channel_0,channel_1");
            for (SweepRow row : rows) {
                writer.printf(
                        Locale.ROOT,
                        "%d,%d,%d,%d,%d,%d,%d,%d%n",
                        row.rpm,
                        row.appRequest,
                        row.limiterRequest,
                        row.sharedRequest,
                        row.areaRequest,
                        row.targetArea,
                        row.channel0,
                        row.channel1);
            }
        }
    }

    void expectU8(Context context, long address, int expected, String name) {
        int actual = readU8(context, address);
        if (actual != (expected & 0xFF)) {
            throw new IllegalStateException(
                    name + ": " + actual + " != " + (expected & 0xFF));
        }
    }

    void expectU16(Context context, long address, int expected, String name) {
        int actual = readU16(context, address);
        if (actual != (expected & 0xFFFF)) {
            throw new IllegalStateException(
                    name + ": " + actual + " != " + (expected & 0xFFFF));
        }
    }

    void expectS16(Context context, long address, int expected, String name) {
        int actual = readS16(context, address);
        if (actual != expected) {
            throw new IllegalStateException(
                    name + ": " + actual + " != " + expected);
        }
    }

    void expectMask(
            Context context,
            long address,
            int mask,
            boolean expected,
            String name) {
        boolean actual = (readU8(context, address) & mask) != 0;
        if (actual != expected) {
            throw new IllegalStateException(
                    name + ": " + actual + " != " + expected);
        }
    }

    int readU8(Context context, long address) {
        return readMemory(context.thread, address, 1)[0] & 0xFF;
    }

    int readU16(Context context, long address) {
        byte[] bytes = readMemory(context.thread, address, 2);
        return ((bytes[0] & 0xFF) << 8) | (bytes[1] & 0xFF);
    }

    int readS16(Context context, long address) {
        return (short) readU16(context, address);
    }

    void writeU8(PcodeExecutorState<byte[]> state, long address, int value) {
        setMemory(state, address, new byte[]{(byte) value});
    }

    void writeU16(PcodeExecutorState<byte[]> state, long address, int value) {
        setMemory(
                state,
                address,
                Utils.longToBytes(value & 0xFFFFL, 2, language.isBigEndian()));
    }

    byte[] readProgram(long address, int size) throws Exception {
        byte[] result = new byte[size];
        int read = currentProgram.getMemory().getBytes(toAddress(address), result);
        if (read != size) {
            throw new IllegalStateException(
                    String.format(
                            Locale.ROOT,
                            "stock read %08x got %d of %d bytes",
                            address, read, size));
        }
        return result;
    }

    void setMemory(
            PcodeExecutorState<byte[]> state, long address, byte[] bytes) {
        state.setVar(space, address, bytes.length, true, bytes);
    }

    byte[] readMemory(PcodeThread<byte[]> thread, long address, int size) {
        return thread.getState().getVar(
                space, address, size, true, Reason.INSPECT);
    }

    void setRegister(PcodeThread<byte[]> thread, String name, long value) {
        Register register = requireRegister(name);
        thread.getState().setVar(
                register,
                Utils.longToBytes(
                        value,
                        register.getNumBytes(),
                        language.isBigEndian()));
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
            result.append(String.format(Locale.ROOT, "%02x", value & 0xFF));
        }
        return result.toString();
    }
}
