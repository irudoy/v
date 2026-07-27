// Apply curated function names from symbols.csv to the current Ghidra program.
// Git file tools/ghidra/symbols.csv is the naming source of truth. Ghidra and
// Memgraph consume the names for readable decompilation and Lab navigation.
// A subsequent ExportGraph.java run reads them through getName() into funcs.csv.
//
// Usage: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript RenameFuncs.java <symbols.csv>
// -noanalysis is valid because setName does not require auto-analysis, and the
// program is still saved when headless commits the script transaction. The CSV
// path is absolute. CSV columns are addr,name,note; addr is hexadecimal without
// 0x, and optional note becomes the function plate comment.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;
import java.io.BufferedReader;
import java.io.FileReader;

public class RenameFuncs extends GhidraScript {
    @Override
    public void run() throws Exception {
        if (getScriptArgs().length < 1) {
            println("VQ_RENAME: missing <symbols.csv> argument");
            return;
        }
        String csv = getScriptArgs()[0];
        BufferedReader br = new BufferedReader(new FileReader(csv));
        String line;
        int applied = 0, renamedComment = 0, skipped = 0, missing = 0;
        while ((line = br.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] p = line.split(",", 3);
            if (p.length < 2) continue;
            String addrStr = p[0].trim();
            if (addrStr.equalsIgnoreCase("addr")) continue;   // header row
            String name = p[1].trim();
            String note = p.length > 2 ? p[2].trim() : null;

            Address a;
            try { a = toAddr(addrStr); } catch (Exception e) { a = null; }
            if (a == null) { println("VQ_RENAME invalid address: " + addrStr); missing++; continue; }
            Function f = getFunctionAt(a);
            if (f == null) { println("VQ_RENAME no function @ " + addrStr); missing++; continue; }

            if (f.getName().equals(name)) {
                skipped++;
            } else {
                f.setName(name, SourceType.USER_DEFINED);
                applied++;
            }
            if (note != null && !note.isEmpty()) {
                f.setComment(note);   // plate comment above function
                renamedComment++;
            }
        }
        br.close();
        println("VQ_RENAME applied=" + applied + " comment=" + renamedComment
                + " skipped=" + skipped + " missing=" + missing);
    }
}
