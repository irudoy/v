// AssembleSh2.java - assemble a bounded SuperH source file into a raw blob
// without changing the current Ghidra program.
//
// The source format intentionally stays small:
//
//   label:
//   .org <absolute-address>
//   .align <power-of-two>
//   .byte <value>[, <value>...]
//   .word <value>[, <value>...]
//   .long <value-or-label>[, <value-or-label>...]
//   <one SH instruction>
//
// Labels may be used as complete instruction operands or directive values.
// Every instruction must encode to one 16-bit SH instruction. Unwritten bytes
// in the requested half-open output interval retain the selected fill value.
//
// Usage (headless):
//   -postScript AssembleSh2.java \
//       <source> <output> <base_hex> <end_hex> [fill_hex] [listing]
//
// This script uses a stand-alone AssemblyBuffer. It never patches memory,
// creates instructions, or otherwise mutates the current Ghidra program.
//@category VQ
import ghidra.app.plugin.assembler.Assembler;
import ghidra.app.plugin.assembler.Assemblers;
import ghidra.app.plugin.assembler.AssemblyBuffer;
import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoInstruction;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.InstructionPrototype;
import ghidra.program.model.lang.Language;
import ghidra.program.model.lang.ProcessorContextImpl;
import ghidra.program.model.mem.ByteMemBufferImpl;
import ghidra.program.model.mem.MemBuffer;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class AssembleSh2 extends GhidraScript {

    static final Pattern LABEL = Pattern.compile(
            "^([A-Za-z_][A-Za-z0-9_]*):$");
    static final Pattern SYMBOL = Pattern.compile(
            "\\b[A-Za-z_][A-Za-z0-9_]*\\b");

    enum Kind {
        INSTRUCTION,
        BYTE,
        WORD,
        LONG
    }

    static class Statement {
        final int lineNumber;
        final long address;
        final Kind kind;
        final String text;

        Statement(int lineNumber, long address, Kind kind, String text) {
            this.lineNumber = lineNumber;
            this.address = address;
            this.kind = kind;
            this.text = text;
        }
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 4 || args.length > 6) {
            throw new IllegalArgumentException(
                    "need: <source> <output> <base_hex> <end_hex>"
                    + " [fill_hex] [listing]");
        }
        String language = currentProgram.getLanguageID().toString();
        if (!language.startsWith("SuperH:BE:32:")) {
            throw new IllegalStateException(
                    "current program language is not big-endian SuperH: "
                    + language);
        }

        Path source = Path.of(args[0]).toAbsolutePath().normalize();
        Path output = Path.of(args[1]).toAbsolutePath().normalize();
        Path listing = args.length == 6
                ? Path.of(args[5]).toAbsolutePath().normalize()
                : null;
        long base = parseNumber(args[2], "base");
        long end = parseNumber(args[3], "end");
        int fill = args.length >= 5
                ? checkedUnsigned(parseNumber(args[4], "fill"), 8, "fill")
                : 0xFF;
        if (base < 0 || end <= base || end > 0x1_0000_0000L) {
            throw new IllegalArgumentException(
                    String.format(
                            "invalid half-open interval [%08x,%08x)",
                            base, end));
        }
        long outputSize = end - base;
        if (outputSize > Integer.MAX_VALUE) {
            throw new IllegalArgumentException("output interval is too large");
        }

        ParseResult parsed = parseSource(source, base, end);
        byte[] bytes = new byte[(int) outputSize];
        Arrays.fill(bytes, (byte) fill);
        boolean[] written = new boolean[bytes.length];
        Assembler assembler = Assemblers.getAssembler(currentProgram);
        int instructionCount = 0;
        int dataBytes = 0;
        List<String> listingLines = new ArrayList<>();

        for (Statement statement : parsed.statements) {
            byte[] encoded;
            if (statement.kind == Kind.INSTRUCTION) {
                String instruction = replaceSymbols(
                        statement.text, parsed.symbols);
                Address address = toAddress(statement.address);
                AssemblyBuffer buffer = new AssemblyBuffer(
                        assembler, address);
                try {
                    encoded = buffer.assemble(instruction);
                }
                catch (Exception error) {
                    throw new IllegalArgumentException(
                            source + ":" + statement.lineNumber
                            + ": cannot assemble at "
                            + hex32(statement.address) + ": "
                            + instruction, error);
                }
                if (encoded.length != 2) {
                    throw new IllegalArgumentException(
                            source + ":" + statement.lineNumber
                            + ": expected one 16-bit SH instruction, got "
                            + encoded.length + " bytes");
                }
                String decoded = decodeInstruction(
                        statement.address, encoded);
                listingLines.add(String.format(
                        Locale.ROOT, "%08x  %s  %-30s ; %s",
                        statement.address & 0xFFFFFFFFL,
                        bytesToHex(encoded), decoded, instruction));
                instructionCount++;
            }
            else {
                encoded = encodeData(statement, parsed.symbols);
                listingLines.add(String.format(
                        Locale.ROOT, "%08x  %s  .%s %s",
                        statement.address & 0xFFFFFFFFL,
                        bytesToHex(encoded),
                        statement.kind.name().toLowerCase(Locale.ROOT),
                        replaceSymbols(statement.text, parsed.symbols)));
                dataBytes += encoded.length;
            }
            writeBounded(
                    bytes, written, base, statement.address, encoded,
                    source, statement.lineNumber);
        }

        Path parent = output.getParent();
        if (parent != null) {
            Files.createDirectories(parent);
        }
        writeIdempotent(output, bytes);
        if (listing != null) {
            Path listingParent = listing.getParent();
            if (listingParent != null) {
                Files.createDirectories(listingParent);
            }
            writeIdempotent(
                    listing,
                    String.join(System.lineSeparator(), listingLines)
                            .concat(System.lineSeparator())
                            .getBytes(java.nio.charset.StandardCharsets.UTF_8));
        }
        int usedBytes = 0;
        for (boolean value : written) {
            if (value) {
                usedBytes++;
            }
        }
        println(String.format(
                "VQ_ASM status=PASS language=%s range=%s..%s"
                + " bytes=%d used=%d instructions=%d data_bytes=%d"
                + " fill=%02x sha256=%s",
                language, hex32(base), hex32(end), bytes.length, usedBytes,
                instructionCount, dataBytes, fill, sha256(bytes)));
        for (Map.Entry<String, Long> symbol : parsed.symbols.entrySet()) {
            println("VQ_ASM symbol " + symbol.getKey() + "="
                    + hex32(symbol.getValue()));
        }
        println("VQ_ASM output=" + output);
        if (listing != null) {
            println("VQ_ASM listing=" + listing);
        }
    }

    static class ParseResult {
        final List<Statement> statements;
        final LinkedHashMap<String, Long> symbols;

        ParseResult(
                List<Statement> statements,
                LinkedHashMap<String, Long> symbols) {
            this.statements = statements;
            this.symbols = symbols;
        }
    }

    ParseResult parseSource(Path source, long base, long end)
            throws IOException {
        List<String> lines = Files.readAllLines(source);
        List<Statement> statements = new ArrayList<>();
        LinkedHashMap<String, Long> symbols = new LinkedHashMap<>();
        long cursor = base;

        for (int index = 0; index < lines.size(); index++) {
            int lineNumber = index + 1;
            String line = stripComment(lines.get(index)).trim();
            if (line.isEmpty()) {
                continue;
            }
            Matcher label = LABEL.matcher(line);
            if (label.matches()) {
                String name = label.group(1);
                if (symbols.putIfAbsent(name, cursor) != null) {
                    throw sourceError(
                            source, lineNumber, "duplicate label " + name);
                }
                continue;
            }
            if (line.startsWith(".org ")) {
                long next = parseNumber(
                        line.substring(5).trim(),
                        source + ":" + lineNumber + " .org");
                if (next < cursor) {
                    throw sourceError(
                            source, lineNumber,
                            ".org moves backward or overlaps prior content");
                }
                cursor = next;
                requireCursor(source, lineNumber, cursor, base, end);
                continue;
            }
            if (line.startsWith(".align ")) {
                long alignment = parseNumber(
                        line.substring(7).trim(),
                        source + ":" + lineNumber + " .align");
                if (alignment <= 0
                        || (alignment & (alignment - 1)) != 0) {
                    throw sourceError(
                            source, lineNumber,
                            ".align must be a positive power of two");
                }
                cursor = (cursor + alignment - 1) & -alignment;
                requireCursor(source, lineNumber, cursor, base, end);
                continue;
            }

            Kind kind;
            String values;
            int width;
            if (line.startsWith(".byte ")) {
                kind = Kind.BYTE;
                values = line.substring(6).trim();
                width = 1;
            }
            else if (line.startsWith(".word ")) {
                kind = Kind.WORD;
                values = line.substring(6).trim();
                width = 2;
            }
            else if (line.startsWith(".long ")) {
                kind = Kind.LONG;
                values = line.substring(6).trim();
                width = 4;
            }
            else if (line.startsWith(".")) {
                throw sourceError(
                        source, lineNumber,
                        "unsupported directive " + line.split("\\s+", 2)[0]);
            }
            else {
                kind = Kind.INSTRUCTION;
                values = line;
                width = 2;
            }
            if ((cursor & 1) != 0 && kind == Kind.INSTRUCTION) {
                throw sourceError(
                        source, lineNumber,
                        "instruction address is not 16-bit aligned");
            }
            int count = kind == Kind.INSTRUCTION
                    ? 1 : splitValues(values, source, lineNumber).length;
            long size = (long) width * count;
            if (cursor < base || cursor + size > end) {
                throw sourceError(
                        source, lineNumber,
                        String.format(
                                "statement [%08x,%08x) is outside"
                                + " output [%08x,%08x)",
                                cursor, cursor + size, base, end));
            }
            statements.add(new Statement(
                    lineNumber, cursor, kind, values));
            cursor += size;
        }
        return new ParseResult(statements, symbols);
    }

    static String stripComment(String line) {
        int slash = line.indexOf("//");
        int semicolon = line.indexOf(';');
        int cut = line.length();
        if (slash >= 0) {
            cut = Math.min(cut, slash);
        }
        if (semicolon >= 0) {
            cut = Math.min(cut, semicolon);
        }
        return line.substring(0, cut);
    }

    static void requireCursor(
            Path source,
            int lineNumber,
            long cursor,
            long base,
            long end) {
        if (cursor < base || cursor > end) {
            throw sourceError(
                    source, lineNumber,
                    String.format(
                            "cursor %08x is outside [%08x,%08x)",
                            cursor, base, end));
        }
    }

    static String[] splitValues(
            String text, Path source, int lineNumber) {
        if (text.isBlank()) {
            throw sourceError(source, lineNumber, "empty data directive");
        }
        String[] values = text.split(",");
        for (int index = 0; index < values.length; index++) {
            values[index] = values[index].trim();
            if (values[index].isEmpty()) {
                throw sourceError(
                        source, lineNumber, "empty data value");
            }
        }
        return values;
    }

    byte[] encodeData(
            Statement statement, Map<String, Long> symbols) {
        int width = switch (statement.kind) {
            case BYTE -> 1;
            case WORD -> 2;
            case LONG -> 4;
            default -> throw new IllegalArgumentException(
                    "instruction passed to data encoder");
        };
        String[] values = splitValues(
                statement.text, Path.of("<source>"), statement.lineNumber);
        byte[] encoded = new byte[values.length * width];
        int offset = 0;
        for (String valueText : values) {
            long value = resolveValue(valueText, symbols);
            int checked = checkedUnsigned(
                    value, width * 8,
                    "line " + statement.lineNumber + " data value");
            for (int index = width - 1; index >= 0; index--) {
                encoded[offset + index] = (byte) checked;
                checked >>>= 8;
            }
            offset += width;
        }
        return encoded;
    }

    String decodeInstruction(long addressValue, byte[] encoded)
            throws Exception {
        Address address = toAddress(addressValue);
        Language language = currentProgram.getLanguage();
        ProcessorContextImpl context = new ProcessorContextImpl(language);
        MemBuffer buffer = new ByteMemBufferImpl(
                address, encoded, language.isBigEndian());
        InstructionPrototype prototype = language.parse(
                buffer, context, false);
        PseudoInstruction instruction = new PseudoInstruction(
                address, prototype, buffer, context);
        if (instruction.getParsedLength() != encoded.length) {
            throw new IllegalArgumentException(
                    "round-trip decoder consumed "
                    + instruction.getParsedLength() + " of "
                    + encoded.length + " bytes at " + hex32(addressValue));
        }
        return instruction.toString();
    }

    static String replaceSymbols(
            String instruction, Map<String, Long> symbols) {
        Matcher matcher = SYMBOL.matcher(instruction);
        StringBuffer result = new StringBuffer();
        while (matcher.find()) {
            Long value = symbols.get(matcher.group());
            if (value == null) {
                matcher.appendReplacement(
                        result, Matcher.quoteReplacement(matcher.group()));
            }
            else {
                matcher.appendReplacement(
                        result, Matcher.quoteReplacement(hex32(value)));
            }
        }
        matcher.appendTail(result);
        return result.toString();
    }

    static long resolveValue(String text, Map<String, Long> symbols) {
        Long symbol = symbols.get(text);
        if (symbol != null) {
            return symbol;
        }
        return parseNumber(text, "value");
    }

    static long parseNumber(String text, String context) {
        String value = text.trim().replace("_", "");
        try {
            if (value.startsWith("0x") || value.startsWith("0X")) {
                return Long.parseUnsignedLong(value.substring(2), 16);
            }
            if (value.matches("[0-9A-Fa-f]+")
                    && value.matches(".*[A-Fa-f].*")) {
                return Long.parseUnsignedLong(value, 16);
            }
            return Long.parseLong(value, 10);
        }
        catch (NumberFormatException error) {
            throw new IllegalArgumentException(
                    context + ": invalid integer " + text, error);
        }
    }

    static int checkedUnsigned(long value, int bits, String context) {
        long limit = bits == 32 ? 0x1_0000_0000L : 1L << bits;
        if (value < 0 || value >= limit) {
            throw new IllegalArgumentException(
                    context + " does not fit uint" + bits + ": " + value);
        }
        return (int) value;
    }

    static void writeBounded(
            byte[] output,
            boolean[] written,
            long base,
            long address,
            byte[] encoded,
            Path source,
            int lineNumber) {
        int offset = Math.toIntExact(address - base);
        for (int index = 0; index < encoded.length; index++) {
            int target = offset + index;
            if (written[target]) {
                throw sourceError(
                        source, lineNumber,
                        "statement overlaps byte at "
                        + hex32(base + target));
            }
            output[target] = encoded[index];
            written[target] = true;
        }
    }

    static void writeIdempotent(Path path, byte[] content)
            throws IOException {
        if (Files.exists(path)) {
            byte[] existing = Files.readAllBytes(path);
            if (!Arrays.equals(existing, content)) {
                throw new IOException(
                        "refusing to overwrite different output " + path);
            }
            return;
        }
        Files.write(path, content);
    }

    Address toAddress(long value) {
        return currentProgram.getAddressFactory().getDefaultAddressSpace()
                .getAddress(value);
    }

    static String hex32(long value) {
        return String.format(Locale.ROOT, "0x%08x", value & 0xFFFFFFFFL);
    }

    static String bytesToHex(byte[] values) {
        StringBuilder result = new StringBuilder(values.length * 2);
        for (byte value : values) {
            result.append(String.format(
                    Locale.ROOT, "%02x", value & 0xFF));
        }
        return result.toString();
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

    static IllegalArgumentException sourceError(
            Path source, int lineNumber, String message) {
        return new IllegalArgumentException(
                source + ":" + lineNumber + ": " + message);
    }
}
