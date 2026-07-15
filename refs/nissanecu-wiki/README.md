# nissanecu-wiki – локальное зеркало NissanECU RE wiki

Полное зеркало community-вики реверс-инжиниринга ЭБУ Nissan/Infiniti (автор – fenugrec):
`https://nissanecu.miraheze.org`. **30 страниц** (namespace Main + `Nissan ECU RE:About`) +
**34 изображения** (`img/`). Первоисточник по firmware-механике, immo/seed-key, checksums,
протоколам и HW SH705x.

- Формат: markdown-конверсия рендер-HTML (`?action=render` -> `html2text`), ссылки на
  изображения переписаны на локальные (`img/`). Каждая страница несёт заголовок с исходным URL.
- Лицензия: **CC BY-SA 4.0** (атрибуция – NissanECU RE wiki / участники).
- Retrieved: **2026-07-15**.

Разметка проекта: [[Открытые дефы и тулинг]], [[Чексуммы]], [[Immo, NATS, клон ЭБУ]],
[[RE-стек и реверс таблиц]] (ноты в Obsidian).

## Ключевое под P0 (immo / seed-key / NV)

- `Firmware_re.md` (46 КБ) – структура прошивки: IVT / power-on reset, сигнатура `NHU\xF8`,
  **LOADER / FID-метаданные**, SID-tree разбора ISO14230, **seed-key (SID27) и ключи SID36**,
  ссылки на checksums. Центральный документ.
- `Checksums.md` – транспортная + content checksum, sum+XOR / RIPEMD-160, области.
- `Eeprom_code.md`, `Eeprom_dumps.md` – работа с внешним EEPROM (immo / marriage / NV вне flash).
- `SID22.md` – ReadDataByIdentifier.
- `Bootmode.md` – boot-режим SH705x (реколвери-прошивка через testpoints на PCB).
- `Wdt.md` – watchdog.

## Протоколы и связь

- `Communication_Protocols.md` (14.5 КБ) – обзор K-line / CAN, стек диагностики.
- `C2_14230.md` – Consult-II поверх ISO14230.
- `Std_14230.md` – стандарт ISO14230 (KWP2000), SID-и.
- `Connect.md`, `Tools.md` – подключение и инструментарий (nisprog, freediag, кабели).

## Железо / MCU

- `Ecu_hw.md` (9.4 КБ) – аппаратная часть ЭБУ: transceiver-чипы (CAN + K), раскладка,
  hardware-версии PCB.
- `Sh_dev.md`, `Sh_docs.md` – SH705x devices и документация (даташиты, ядро SH-2E).

## Размеченные референс-ROM (образцы для гомологии)

- `Rom_an.md` – методика аннотирования ROM.
- `Rom_an_cf43d.md`, `Rom_an_cf48d.md` – разобранные VQ35DE-ROM (опорные для кросс-референса).
- `Rom_an_al500.md` – разбор ещё одного ROM.
- `Rom_db.md` – база известных ROM (ECUID / FID / loader).

## Тюнинг / карты

- `Nissan_Map_Functionality.md`, `Tuning.md`, `Nissan_Tuning.md`, `Nissan.md` (часть –
  редиректы/заглушки).

## AUD (диагностический протокол Nissan)

- `AUD.md`, `AUD_debug_tool.md` (`AUD_AUD_debug_tool.md` – та же страница как subpage-алиас).

## Служебное

- `Main_Page.md`, `Nissan_ECU_RE_About.md`, `RE5R05A_TCM_Analysis.md` (АКПП, вне скоупа мотора).

## Обновление зеркала

1. Перечислить страницы: API `…/w/api.php?action=query&list=allpages&apnamespace=0&aplimit=500`
   (+ `apnamespace=4`).
2. Каждую страницу забрать как `…/wiki/<Title>?action=render`, прогнать через `html2text`
   (`body_width=0`), добавить заголовок с URL.
3. Изображения из markdown скачать в `img/`, переписать ссылки на локальные.
4. Лицензию сверить: API `meta=siteinfo&siprop=rightsinfo`.
