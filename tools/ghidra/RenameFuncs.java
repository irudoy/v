// Применение курируемых имён функций (symbols.csv) к текущей программе Ghidra.
// Источник истины по именам реверса – git (tools/ghidra/symbols.csv). Ghidra и Memgraph –
// потребители: имена нужны в декомпиляции (читаемый реверс) и в графе (навигация в Lab).
// После прогона повторный ExportGraph.java подхватывает имена через getName() -> funcs.csv.
//
// Запуск: tools/ghidra/headless-analyze.sh <proj_dir> <proj> -process <bin> -noanalysis \
//           -scriptPath tools/ghidra -postScript RenameFuncs.java <symbols.csv>
// -noanalysis допустимо: setName не требует авто-анализа, программа всё равно
// сохраняется в проект (headless коммитит транзакцию скрипта). Путь к CSV – абсолютный.
// CSV: addr,name,note  – addr hex без 0x; note (опц.) идёт в plate comment функции.
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
            println("VQ_RENAME: нет аргумента <symbols.csv>");
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
            if (addrStr.equalsIgnoreCase("addr")) continue;   // строка-заголовок
            String name = p[1].trim();
            String note = p.length > 2 ? p[2].trim() : null;

            Address a;
            try { a = toAddr(addrStr); } catch (Exception e) { a = null; }
            if (a == null) { println("VQ_RENAME плохой адрес: " + addrStr); missing++; continue; }
            Function f = getFunctionAt(a);
            if (f == null) { println("VQ_RENAME нет функции @ " + addrStr); missing++; continue; }

            if (f.getName().equals(name)) {
                skipped++;
            } else {
                f.setName(name, SourceType.USER_DEFINED);
                applied++;
            }
            if (note != null && !note.isEmpty()) {
                f.setComment(note);   // plate comment над функцией
                renamedComment++;
            }
        }
        br.close();
        println("VQ_RENAME applied=" + applied + " comment=" + renamedComment
                + " skipped=" + skipped + " missing=" + missing);
    }
}
