# RomRaider custom checksum

`NissanImmoCoordinator.jar` реализует один пользовательский переключатель
always-ID-OK для exact-ROM JK08A. Исходный код и проверка находятся в
`tools/romraider/`.

RomRaider загружает класс `com.romraider.maps.checksum.NissanImmoCoordinator`
из JAR по относительному пути дефа. `JK08A.xml` и каталог `romraider/` поэтому
переносятся в каталог пользовательских определений вместе.

Порядок обработки при сохранении:

1. `NissanImmoCoordinator` проверяет размер ROM и известные состояния L1/L2,
   затем синхронизирует L2 по видимому состоянию L1.
2. Нативный менеджер `alt` пересчитывает checksum B.
3. Нативный менеджер `alt2` пересчитывает checksum A с учётом полей B.

Менеджер не исправляет неизвестные байты. Неожиданное состояние L1/L2 или
размер ROM приводит к отказу сохранения до пересчёта checksum.

Пересборка и тест на точном stock JK08A:

```bash
bash tools/romraider/build_immo_coordinator.sh
```

Скрипт также проверяет согласованность XML, JAR, L1/L2 и точного stock ROM через
`tools/romraider/verify_definition.py`.

API совместимости закреплён по официальному RomRaider commit
`dafe0c36c1a68efadbeedb2825f3855463fdbc35`. JAR содержит только custom-класс;
compile-only копия интерфейса `ChecksumManager` в артефакт не входит.
