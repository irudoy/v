// Exact-image, read-only preparation of reviewed function entries and fragments.
// Usage: -postScript PrepareProgram.java prepare <plan.tsv> <receipt.json> <file>...
//        <output scripts>
//        -postScript PrepareProgram.java seal <plan.tsv> <receipt.json> <file>...
// Preparation invokes the existing primary scripts, verifies all requested joins,
// and checks preserved instructions and references before it writes a receipt.
// Seal binds successfully produced output bytes to that independently prepared run.
// HeadlessScript failure aborts following scripts without deleting the program.
import ghidra.app.util.headless.HeadlessScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.Reference;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class PrepareProgram extends HeadlessScript {
    Listing listing;
    String wireHash;
    JsonObject preservation = new JsonObject();
    Map<String, String> scalar = new HashMap<>();
    List<String[]> inputs = new ArrayList<>();
    List<String[]> seeds = new ArrayList<>();
    List<String[]> pins = new ArrayList<>();
    List<String[]> sites = new ArrayList<>();
    List<String[]> fragments = new ArrayList<>();
    List<String[]> joins = new ArrayList<>();
    List<String[]> references = new ArrayList<>();
    List<String[]> forbidden = new ArrayList<>();

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 3 || !(args[0].equals("prepare") || args[0].equals("seal"))) {
            throw new IllegalArgumentException("prepare/seal <plan> <receipt> [outputs]");
        }
        listing = currentProgram.getListing();
        Path plan = Path.of(args[1]);
        Path receipt = Path.of(args[2]);
        readPlan(plan);
        wireHash = hash(Files.readAllBytes(plan));
        monitor.checkCancelled();
        if (args[0].equals("prepare")) {
            Files.deleteIfExists(receipt);
            preflight();
            clearStageOutputs(receipt, Arrays.copyOfRange(args, 3, args.length));
            prepare(receipt);
        } else {
            seal(receipt, Arrays.copyOfRange(args, 3, args.length));
        }
    }

    void readPlan(Path path) throws Exception {
        Map<String, List<String[]>> arrays = Map.of(
            "input", inputs, "seed", seeds, "pin", pins, "site", sites,
            "fragment", fragments, "join", joins, "reference", references,
            "forbidden", forbidden);
        Set<String> keys = Set.of("schema", "layout", "digest", "image_sha256",
                "image_size", "merges", "run_id");
        for (String line : Files.readAllLines(path, StandardCharsets.UTF_8)) {
            String[] row = line.split("\t", -1);
            if (arrays.containsKey(row[0])) arrays.get(row[0]).add(row);
            else if (keys.contains(row[0]) && row.length == 2
                    && scalar.putIfAbsent(row[0], row[1]) == null) continue;
            else throw new IllegalArgumentException("invalid preparation plan row " + line);
        }
        if (!scalar.keySet().equals(keys) || !scalar.get("schema").equals("1")
                || seeds.isEmpty() || pins.isEmpty() || inputs.isEmpty()) {
            throw new IllegalArgumentException("incomplete preparation plan");
        }
        for (String[] row : inputs) requireLength(row, 4);
        for (String[] row : seeds) requireLength(row, 6);
        for (String[] row : fragments) requireLength(row, 5);
        for (String[] row : pins) requireLength(row, 3);
        for (String[] row : sites) requireLength(row, 3);
        for (String[] row : joins) requireLength(row, 3);
        for (String[] row : references) requireLength(row, 5);
        for (String[] row : forbidden) requireLength(row, 2);
    }

    void clearStageOutputs(Path receipt, String[] outputs) throws Exception {
        if (outputs.length == 0) throw new IllegalArgumentException("no prepared output files");
        for (String output : outputs) {
            if (!Path.of(output).getFileName().toString().equals(output)) {
                throw new IllegalArgumentException("output must be a local file name");
            }
            Path file = receipt.getParent().resolve(output);
            if (Files.isSymbolicLink(file) || Files.exists(file) && !Files.isRegularFile(file)) {
                throw new IllegalStateException("unsafe stage output " + output);
            }
        }
        for (String output : outputs) Files.deleteIfExists(receipt.getParent().resolve(output));
    }

    void requireLength(String[] row, int length) {
        if (row.length != length) throw new IllegalArgumentException("bad " + row[0] + " row");
    }

    void verifyInputs() throws Exception {
        for (String[] row : inputs) {
            monitor.checkCancelled();
            if (!hash(Files.readAllBytes(Path.of(row[3]))).equals(row[2])) {
                throw new IllegalStateException("preparation input changed: " + row[1]);
            }
        }
    }

    void preflight() throws Exception {
        verifyInputs();
        String expected = scalar.get("image_sha256");
        if (!expected.equals(currentProgram.getExecutableSHA256())) {
            throw new IllegalStateException("program holds another imported image");
        }
        if (!imageHash().equals(expected)) {
            throw new IllegalStateException("current program memory differs from the exact image");
        }
        for (String[] row : pins) {
            byte[] expectedBytes = unhex(row[2]);
            byte[] actual = new byte[expectedBytes.length];
            if (currentProgram.getMemory().getBytes(address(row[1]), actual) != actual.length
                    || !Arrays.equals(expectedBytes, actual)) {
                throw new IllegalStateException("current bytes differ at pin " + row[1]);
            }
        }
    }

    String imageHash() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        int size = Integer.parseInt(scalar.get("image_size"));
        for (int offset = 0; offset < size; offset += 65536) {
            monitor.checkCancelled();
            byte[] bytes = new byte[Math.min(65536, size - offset)];
            if (currentProgram.getMemory().getBytes(toAddr(offset), bytes) != bytes.length) {
                throw new IllegalStateException("incomplete current image bytes");
            }
            digest.update(bytes);
        }
        return hex(digest.digest());
    }

    void prepare(Path receipt) throws Exception {
        Map<String, Snapshot> before = snapshots();
        Set<String> modified = new HashSet<>();
        for (String[] row : seeds) modified.add(row[1]);
        for (String[] row : fragments) modified.add(row[2]);
        for (String[] row : forbidden) {
            if (before.containsKey(row[1])) {
                throw new IllegalStateException("unreviewed outside-function entry " + row[1]);
            }
        }
        for (String[] row : fragments) {
            Snapshot former = before.get(row[2]);
            if (former != null && (former.instructions.size() != Integer.parseInt(row[3])
                    || !former.exact.equals(row[4]))) {
                throw new IllegalStateException("fragment bytes differ at " + row[2]);
            }
        }
        String[] entries = seeds.stream().map(row -> row[1]).toArray(String[]::new);
        String[] recover = new String[entries.length + 1];
        recover[0] = "--seeds-only";
        System.arraycopy(entries, 0, recover, 1, entries.length);
        runScript("RecoverFuncs.java", recover, state);
        requireSeeds();
        runScript("AnalyzeFuncs.java", entries, state);
        runScript("MergeFuncs.java", new String[] { scalar.get("merges") }, state);
        runScript("AnalyzeFuncs.java", entries, state);
        postconditions();
        Map<String, Snapshot> after = snapshots();
        Set<String> expected = new HashSet<>(before.keySet());
        expected.addAll(Arrays.asList(entries));
        for (String[] row : joins) expected.remove(row[2]);
        if (!expected.equals(after.keySet())) {
            throw new IllegalStateException("preparation changes an unreviewed function entry");
        }
        int unchangedFunctions = 0;
        for (Map.Entry<String, Snapshot> item : before.entrySet()) {
            if (modified.contains(item.getKey())) continue;
            unchangedFunctions++;
            if (!item.getValue().same(after.get(item.getKey()))) {
                throw new IllegalStateException("preparation changes another function: "
                        + item.getKey());
            }
        }
        for (String[] seed : seeds) {
            Snapshot old = before.get(seed[1]);
            if (old != null) preserve(old, after.get(seed[1]), seed[1]);
        }
        for (String[] join : joins) {
            Snapshot old = before.get(join[2]);
            if (old != null) {
                boolean borrowedFrame = fragments.stream().anyMatch(row ->
                        row[1].equals(join[1]) && row[2].equals(join[2]));
                preserve(old, after.get(join[1]), join[2], borrowedFrame);
            }
        }
        JsonObject result = new JsonObject();
        result.addProperty("schema_version", 1);
        result.addProperty("layout", scalar.get("layout"));
        result.addProperty("digest", scalar.get("digest"));
        result.addProperty("wire_sha256", wireHash);
        result.addProperty("image_sha256", scalar.get("image_sha256"));
        result.addProperty("current_sha256", imageHash());
        result.addProperty("preserved", true);
        result.addProperty("complete", false);
        result.addProperty("functions", after.size());
        result.addProperty("unchanged_functions", unchangedFunctions);
        result.add("preservation", preservation);
        Files.writeString(receipt, result.toString() + "\n");
        println("VQ_PREP prepared " + scalar.get("layout") + " functions=" + after.size());
    }

    void preserve(Snapshot old, Snapshot owner, String entry) {
        preserve(old, owner, entry, false);
    }

    void preserve(Snapshot old, Snapshot owner, String entry, boolean borrowedFrame) {
        if (owner == null) {
            throw new IllegalStateException("prepared owner is absent for " + entry);
        }
        List<String> lostInstructions = new ArrayList<>();
        for (Map.Entry<String, String> ins : old.instructions.entrySet()) {
            if (!ins.getValue().equals(owner.instructions.get(ins.getKey()))) {
                lostInstructions.add(ins.getKey() + ": " + ins.getValue() + " -> "
                        + owner.instructions.get(ins.getKey()));
            }
        }
        Set<String> lostReferences = new java.util.TreeSet<>(old.references);
        lostReferences.removeAll(owner.references);
        Set<String> required = new HashSet<>(old.references);
        // Only a registered borrowed fragment can acquire its owner's stack frame.
        // Stack-space references are analysis annotations, not ROM/RAM addresses.
        // All non-stack references and all other function snapshots remain exact.
        if (borrowedFrame) required.removeAll(old.stackReferences);
        Set<String> lostRequired = new java.util.TreeSet<>(required);
        lostRequired.removeAll(owner.references);
        println("VQ_PREP preserve " + entry + " instructions=" + old.instructions.size()
                + " references=" + old.references.size() + " memory_references="
                + old.memoryReferences.size() + " changed_instructions="
                + lostInstructions.size() + " lost_required=" + lostRequired.size()
                + " lost_all=" + lostReferences.size());
        if (!owner.instructions.entrySet().containsAll(old.instructions.entrySet())
                || (!borrowedFrame && !owner.references.containsAll(old.references))
                || !lostRequired.isEmpty()) {
            for (String item : lostInstructions.stream().limit(80).toList()) {
                println("VQ_PREP changed instruction " + item);
            }
            for (String item : lostRequired.stream().limit(80).toList()) {
                println("VQ_PREP lost required reference " + item);
            }
            throw new IllegalStateException("prepared owner loses instructions/references " + entry);
        }
        JsonObject kept = new JsonObject();
        kept.addProperty("instructions", old.instructions.size());
        kept.addProperty("memory_references", old.memoryReferences.size());
        kept.addProperty("non_stack_references", required.size());
        kept.addProperty("all_references_before", old.references.size());
        kept.addProperty("borrowed_frame", borrowedFrame);
        JsonArray removed = new JsonArray();
        for (String item : lostReferences) {
            if (!borrowedFrame || !old.stackReferences.contains(item)) {
                throw new IllegalStateException("non-stack reference was exempted " + item);
            }
            removed.add(item);
            println("VQ_PREP recomputed abstract stack reference " + item);
        }
        kept.add("removed_abstract_stack", removed);
        JsonArray added = new JsonArray();
        for (String item : new java.util.TreeSet<>(owner.stackReferences)) {
            String site = item.substring(0, item.indexOf(':'));
            if (old.instructions.containsKey(site) && !old.stackReferences.contains(item)) {
                added.add(item);
            }
        }
        kept.add("added_abstract_stack", added);
        preservation.add(entry, kept);
    }

    void requireSeeds() throws Exception {
        monitor.checkCancelled();
        for (String[] row : seeds) {
            if (getFunctionAt(address(row[1])) == null) {
                throw new IllegalStateException("missing reviewed entry " + row[1]);
            }
        }
    }

    void postconditions() throws Exception {
        requireSeeds();
        for (String[] row : seeds) {
            Function function = getFunctionAt(address(row[1]));
            Snapshot body = snapshot(function);
            if (function.getBody().getNumAddresses() != Long.parseLong(row[2])
                    || body.instructions.size() != Integer.parseInt(row[3])
                    || function.getBody().getNumAddressRanges() != Integer.parseInt(row[4])
                    || !body.exact.equals(row[5])) {
                throw new IllegalStateException("prepared body differs at " + row[1]);
            }
        }
        for (String[] row : sites) {
            Function owner = getFunctionContaining(address(row[2]));
            if (listing.getInstructionAt(address(row[2])) == null || owner == null
                    || !owner.getEntryPoint().equals(address(row[1]))) {
                throw new IllegalStateException("reviewed instruction has wrong owner: " + row[2]);
            }
        }
        for (String[] row : joins) {
            Function owner = getFunctionAt(address(row[1]));
            if (owner == null || getFunctionAt(address(row[2])) != null
                    || !owner.getBody().contains(address(row[2]))) {
                throw new IllegalStateException("reviewed join is absent: " + row[2]);
            }
        }
        for (String[] row : forbidden) {
            if (getFunctionAt(address(row[1])) != null) {
                throw new IllegalStateException("unreviewed outside-function entry " + row[1]);
            }
        }
        for (String[] row : references) {
            Instruction ins = listing.getInstructionAt(address(row[2]));
            Function owner = getFunctionContaining(address(row[2]));
            if (ins == null || owner == null || !owner.getEntryPoint().equals(address(row[1]))) {
                throw new IllegalStateException("reference has wrong owner " + row[2]);
            }
            boolean found = false;
            for (Reference ref : ins.getReferencesFrom()) {
                if (!ref.getToAddress().equals(address(row[3]))) continue;
                String type = row[4];
                if (type.equals("read") && ref.getReferenceType().isRead()
                        || type.equals("write") && ref.getReferenceType().isWrite()
                        || type.equals("call") && ref.getReferenceType().isCall()) found = true;
            }
            if (!found) throw new IllegalStateException("missing " + row[4] + " at " + row[2]);
        }
    }

    void seal(Path receipt, String[] outputs) throws Exception {
        verifyInputs();
        monitor.checkCancelled();
        JsonObject result = JsonParser.parseString(Files.readString(receipt)).getAsJsonObject();
        if (!result.get("wire_sha256").getAsString().equals(wireHash)
                || !result.get("digest").getAsString().equals(scalar.get("digest"))
                || !result.get("preserved").getAsBoolean()
                || !imageHash().equals(scalar.get("image_sha256"))) {
            throw new IllegalStateException("preparation receipt is not current");
        }
        postconditions();
        if (outputs.length == 0) throw new IllegalArgumentException("no prepared output files");
        JsonObject files = new JsonObject();
        for (String output : outputs) {
            if (!Path.of(output).getFileName().toString().equals(output)) {
                throw new IllegalArgumentException("output must be a local file name");
            }
            Path path = receipt.getParent().resolve(output);
            byte[] bytes = Files.readAllBytes(path);
            if (bytes.length == 0) throw new IllegalStateException("empty output " + output);
            String text = new String(bytes, StandardCharsets.UTF_8);
            if (output.startsWith("decomp_") && text.contains("// decompile failed:")) {
                throw new IllegalStateException("decompiler failed for " + output);
            }
            if (output.startsWith("funclisting_") || output.startsWith("decomp_")) {
                String entry = output.substring(output.indexOf('_') + 1, output.indexOf('.'));
                if (!text.startsWith("// ") || !text.contains(" @ " + entry + "  size=")) {
                    throw new IllegalStateException("requested output has wrong entry " + output);
                }
            }
            files.addProperty(output, hash(bytes));
        }
        result.add("outputs", files);
        result.addProperty("complete", true);
        Files.writeString(receipt, result.toString() + "\n");
        println("VQ_PREP sealed " + outputs.length + " outputs");
    }

    Map<String, Snapshot> snapshots() throws Exception {
        Map<String, Snapshot> result = new HashMap<>();
        for (Function function : currentProgram.getFunctionManager().getFunctions(true)) {
            monitor.checkCancelled();
            result.put(function.getEntryPoint().toString(), snapshot(function));
        }
        return result;
    }

    Snapshot snapshot(Function function) throws Exception {
        Snapshot result = new Snapshot();
        result.size = function.getBody().getNumAddresses();
        result.ranges = function.getBody().toString();
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        InstructionIterator instructions = listing.getInstructions(function.getBody(), true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction ins = instructions.next();
            byte[] bytes = new byte[ins.getLength()];
            currentProgram.getMemory().getBytes(ins.getAddress(), bytes);
            digest.update(bytes);
            result.instructions.put(ins.getAddress().toString(), hex(bytes) + ":"
                    + ins.getMnemonicString() + ":" + ins.getFlowOverride());
            for (Reference ref : ins.getReferencesFrom()) {
                String key = ins.getAddress() + ":" + ref.getToAddress() + ":"
                        + ref.getReferenceType().getName() + ":" + ref.getOperandIndex();
                result.references.add(key);
                if (ref.getToAddress().isStackAddress()) result.stackReferences.add(key);
                if (ref.getToAddress().isMemoryAddress()) result.memoryReferences.add(key);
            }
        }
        result.exact = hex(digest.digest());
        return result;
    }

    static class Snapshot {
        long size;
        String ranges, exact;
        Map<String, String> instructions = new LinkedHashMap<>();
        Set<String> references = new HashSet<>();
        Set<String> stackReferences = new HashSet<>();
        Set<String> memoryReferences = new HashSet<>();
        boolean same(Snapshot other) {
            return other != null && size == other.size && ranges.equals(other.ranges)
                    && exact.equals(other.exact) && instructions.equals(other.instructions)
                    && references.equals(other.references);
        }
    }

    Address address(String value) { return toAddr(Long.parseLong(value, 16)); }
    String hash(byte[] bytes) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }
    String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte value : bytes) result.append(String.format("%02x", value & 0xff));
        return result.toString();
    }
    byte[] unhex(String value) {
        byte[] result = new byte[value.length() / 2];
        for (int i = 0; i < result.length; i++) {
            result[i] = (byte) Integer.parseInt(value.substring(2 * i, 2 * i + 2), 16);
        }
        return result;
    }
}
