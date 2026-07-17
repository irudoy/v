# EcuTek 370Z ProECU – документация (Markdown)

Две страницы базы знаний EcuTek Support (Confluence, пространство `SUPPORT`,
раздел `EcuTek Knowledge Base / Vehicle Specific Guides / Nissan / 370Z`),
сконвертированные в самодостаточный Markdown с локальными изображениями.
Пригодно для чтения человеком и для машинной обработки агентом.

Двигатель 370Z – VQ37VHR (VVEL), поэтому обе страницы напрямую релевантны
проекту VQ HR ECU.

## Содержимое

| Документ | Файл | Page ID | Версия | Заголовков | Изображений | Размер MD |
|---|---|---|---|---|---|---|
| 370Z ProECU Tuning Guide | [tuning-guide/](tuning-guide/370Z-ProECU-Tuning-Guide.md) | 7143430 | 22 | 72 | 67 | 56 KB |
| 370Z ProECU RaceROM Supplement | [racerom-supplement/](racerom-supplement/370Z-ProECU-RaceROM-Supplement.md) | 6881638 | 25 | 110 | 106 | 76 KB |

Источники:
- Tuning Guide: https://ecutek.atlassian.net/wiki/spaces/SUPPORT/pages/7143430
- RaceROM Supplement: https://ecutek.atlassian.net/wiki/spaces/SUPPORT/pages/6881638

## Структура

```
markdown/
  README.md
  tuning-guide/
    370Z-ProECU-Tuning-Guide.md
    images/            # 67 файлов, ссылки относительные (images/...)
  racerom-supplement/
    370Z-ProECU-RaceROM-Supplement.md
    images/            # 106 файлов
```

Каждый документ самодостаточен: изображения лежат в собственной папке `images/`
рядом с `.md`, поэтому папку документа можно перемещать целиком. Имена файлов
изображений совпадают с именами вложений Confluence (в них закодированы даты).

## Как получено

Исходные сохранённые HTML (`*.html` + `*_files/`) в родительской папке – это
SPA-сейвы Confluence Cloud: медиа грузится лениво через blob-URL и в сохранённой
копии не сопоставлено с позициями в тексте (у RaceROM в сейве отсутствовали 12 из
13 изображений). Поэтому обе страницы перезабраны напрямую из публичного
Confluence REST API в формате `body.export_view` (чистый рендер-HTML с корректными
`<img>` в правильных позициях), после чего сконвертированы в Markdown, а все
вложения скачаны штатными download-ссылками. Пространство `SUPPORT` открыто
анонимно, аутентификация не требуется.

## Решения при конвертации

- Заголовки получают якоря по алгоритму GitHub; внутренние ссылки страницы
  переписаны на эти якоря (сверено – битых нет). В начале каждого файла –
  сворачиваемое оглавление (`<details>`).
- Info/Note/Warning-макросы Confluence -> GitHub-admonitions с сохранением цвета:
  Warning(красный)->`[!CAUTION]`, Note(жёлтый)->`[!WARNING]`,
  Information(синий)->`[!NOTE]`, Tip(зелёный)->`[!TIP]`.
- Многоколоночные layout-макросы разворачиваются в последовательный текст;
  таблицы -> Markdown-таблицы.
- Косметическая юникод-пунктуация приведена к ASCII (парные кавычки, стрелка,
  мусорный символ буллета из шрифта Symbol). En-dash `–`, знак градуса `°` и
  `·` в единице `lbs·ft` сохранены. Опечатки исходного текста не исправлялись.
- YAML-заголовок каждого файла содержит source-URL, page_id, версию и дату
  получения.

## Недоступные изображения

Два изображения в Tuning Guide не восстанавливаются анонимно и заменены
inline-плейсхолдерами `*[image unavailable: ...]*` с сохранением позиции и
исходного URL в HTML-комментарии:

- `Nissan 370z` (`www.ecutek.com/.../image1.jpg.aspx`) – маркетинговое фото, отдаёт 404;
- `CPC Enable.jpg` (`api.media.atlassian.com/...`) – инлайновая вставка с истёкшим
  токеном, среди вложений страницы отсутствует.

Остальные 173 изображения (67 + 106) скачаны локально.
