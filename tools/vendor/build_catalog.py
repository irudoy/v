#!/usr/bin/env python3
# Сводит две транскрипции вендорских словарей - refs/vendor/proecu-maps.csv (ProECU/EcuTek) и
# refs/vendor/uprev-maps.csv (UpRev) - в refs/vendor/catalog.csv, вход load_vendor.py (Stage 5
# tools/map-flag-pipeline.md). Метод транскрипции и разметка - refs/vendor/README.md.
#
# Каталог генерируем, транскрипции рукописны, и правятся они, а не он: catalog.csv несёт
# выведенные колонки (origin, concept), а правка в нём разошлась бы со словарём молча - ошибка
# ровно того сорта, против которого стоит P5.
#
# Имена не нормализуются и не переписываются, регистр и опечатки источника сохраняются, включая
# собственные маркеры неопределённости ProECU (`Idle Target #1a - ??`, `Sensor Multiplier Unk`).
# Имя - единственное, что скриншот дерева ProECU вообще даёт, поэтому оно и есть цитата;
# вся аналитика уходит в отдельные колонки, ни одна запись не выбрасывается.
#
# Запуск: python3 tools/vendor/build_catalog.py
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VENDOR = os.path.join(ROOT, "refs", "vendor")

# --- origin: ProECU ---
# Весь racerom-supplement документирует функции RaceROM. В tuning-guide RaceROM
# только явная ветка дерева; остальное – заводское.
# origin нормализован: factory | patch | unknown. Чей это патч, говорит колонка
# vendor (ecutek -> RaceROM, uprev -> ARC).
#
# Колонка обязательна для Stage 5: patch-запись описывает чужой код, которого в стоке нет, и
# матч стоковой карты к ней был бы не слабой подсказкой, а неверной. Метка группы в правило не
# входит - она ненадёжна: `Rev Limit Per Gear Mode1-4` есть карты RaceROM, но лежат под группой
# `Limiters` рядом с заводскими. Решает документ-источник и явный корень дерева.
def proecu_origin(r):
    if r['doc'] == 'racerom-supplement':
        return 'patch'
    if r['group'].startswith('EcuTek RaceROM Maps//'):
        return 'patch'
    return 'factory'

# --- concept: курируемая разметка, только там, где связка обоснована ---
# Ключ соединения словарей: записи с одним concept описывают одну сущность. Имена вербатим, и
# два словаря называют одно разными словами (`BFS Multiplier (K-Factor)` против
# `K - Fuel Multiplier`), поэтому джойн по имени не сошёлся бы вовсе, а джойн по похожести имён
# сводил бы разное. Отсюда ручной словарь: связка - утверждение, а не строковая операция.
# Пустой concept означает "связка не установлена", а не "связки нет".
# exact: точное имя -> concept; prefix: имя начинается с -> concept
PROECU_EXACT = {
    'BFS Multiplier (K-Factor)': 'bfs-multiplier',
    'MAF Sensor Scale (% to g/s) for Load': 'maf-gps-scalar',
    'MAF Sensor Scale Bank #1 (V to %)': 'maf-curve',
    'MAF Sensor Scale Bank #2 (V to %)': 'maf-curve',
    'MAF Voltage Min Allowed': 'maf-volts-min',
    'MAP Sensor Multiplier': 'map-sensor-scaling',
    'MAP Sensor Offset': 'map-sensor-scaling',
    'Sensor Multiplier Unk': 'map-sensor-scaling',
    'Sensor Offset Unk': 'map-sensor-scaling',
    'Coolant & AIT Sensor Scale': 'temp-sensor-scale',
    'Eng Oil Temp Scale': 'temp-sensor-scale',
    'Fuel Map': 'fuel-target',
    'Fuel Enrichment - Cold': 'fuel-comp',
    'Fuel Enrichment - Hot': 'fuel-comp',
    'Fuel Trim Per Cyl': 'cylinder-trim',
    'Injector Flow Scaling': 'injector-size',
    'Injector Lag Time Multiplier': 'injector-latency',
    'Injector Lag Time Offset': 'injector-latency',
    'Injector Minimum Open Time': 'injector-minimum',
    'Knock Sensitivity': 'knock-threshold',
    'Rev Limit - Fuel Cut': 'rev-limit-fuel',
    'Rev Limit - Fuel Cut Restore': 'rev-limit-restore',
    'Rev Limit - Fuel Cut Maximum': 'rev-limit-max',
    'Rev Limit - Throttle Cut': 'rev-limit-throttle',
    'Torque Actual': 'torque-actual',
    'Torque Demand': 'torque-demand',
    'Torque Demand - Trustful': 'torque-demand',
    'Idle Target #1 - Drive': 'idle-target-drive',
    'Idle Target #2 - Neutral': 'idle-target-neutral',
    'Idle Target #1a - ??': 'idle-target-load',
    'VVEL Control Shaft Angle to Duration': 'vvel-cs-angle',
    'VVEL Control Shaft Angle Trustful': 'vvel-cs-angle',
    'VVEL Control Shaft Max': 'vvel-cs-limit',
    'DoNotAdjust: VTC Max Advance by VVEL CS Angle': 'vvel-interference-vtc',
    'DoNotAdjust: VVEL Control Shaft Max by VTC Angle': 'vvel-interference-cs',
    'Accel Map Slow/Fast Switch': 'accel-map-switch',
    'Accel Map Slow/Fast Switch Trustful': 'accel-map-switch',
    'Accel To Throttle Lo/Hi Switch': 'accel-throttle-switch',
}
PROECU_PREFIX = [
    ('Cranking Fuel Injector Pulsewidth Initial', 'cranking-initial'),
    ('Cranking Fuel Injector Pulsewidth step',    'cranking-decay'),
    ('Cranking Fuel RPM Compensation',            'cranking-rpm-comp'),
    ('Overrun Fuel Cut',                          'overrun-fuel-cut'),
    ('Idle - target airflow rate',                'idle-airflow'),
    ('Idle Ignition Timing',                      'idle-ignition'),
    ('Ignition Timing Mode A1 Adj',               'ignition-trim'),
    ('Ignition Timing Mode B1',                   'ignition-mode-b'),
    ('Knock Control Enable A1',                   'knock-enable'),
    ('Knock Retard Multiplier',                   'knock-multiplier'),
    ('Speed Limit -',                             'speed-limit'),
    ('VTC Valve Advance',                         'vtc-advance'),
    ('VVEL Valve Duration',                       'vvel-duration'),
    ('VVEL Control Shaft Min',                    'vvel-cs-limit'),
    ('Accel to Throttle',                         'accel-throttle'),
    ('Accel To Throttle Lo',                      'accel-throttle'),
    ('Accel Map',                                 'accel-pedal'),
    ('Torque Filtering WOT',                      'torque-filtering-wot'),
]
UPREV_EXACT = {
    'K - Fuel Multiplier': 'bfs-multiplier',
    'Calculated Load': 'load-100pct',
    'Load Point Scaler': 'load-point-scaler',
    'Mass Air Flow Sensor': 'maf-curve',
    'Fuel Targets': 'fuel-target',
    'Fuel Compensation Main': 'fuel-comp',
    'Fuel Compensation Cold': 'fuel-comp',
    'Cylinder Trim': 'cylinder-trim',
    'Injector Minimum': 'injector-minimum',
    'Cranking Enrichment Initial Value': 'cranking-initial',
    'Ignition Timing Knock Windows': 'knock-enable',
    'Knock Listening Threshold': 'knock-threshold',
    'Cam Phasing': 'vtc-advance',
    'Rev Limit': 'rev-limit-fuel',
    'Throttle Cut Rev Limit': 'rev-limit-throttle',
    'Speed Limit': 'speed-limit',
    'Throttle A': 'throttle-torque',
    'Estimated Torque Delivered': 'torque-actual',
    # Та же карта, что 'Torque Demand' EcuTek и 'QH0/ Torque Conversion Map' A2L: совпадают оси,
    # шкала выхода, раздел и наличие контрольной копии. Трактовки вендоров расходятся (запрос
    # момента против оценки выданного), сведена структура - разбор в facts.csv.
    'Throttle A': 'torque-demand',
    'Radiator Fan Speed by Temp': 'rad-fan-duty',
    'Idle Target': 'idle-target-neutral',
    'Idle Target Gear': 'idle-target-drive',
    'Idle Target Low': 'idle-target-load',
    'VVEL Angle': 'vvel-cs-angle',
    'VVEL Angle Alt': 'vvel-cs-angle',
    'VVEL Intake Phasing': 'vvel-interference-vtc',
    'VVEL Limit': 'vvel-interference-cs',
    'VVEL Max': 'vvel-cs-limit',
    'VVEL Min': 'vvel-cs-limit',
    'VVEL Decel': 'vvel-duration',
    'VVEL Duration WOT': 'vvel-duration',
    'ETC Control': 'etc-control',
    'NATS': 'nats',
}
UPREV_PREFIX = [
    ('Injector Priming Pulse Mode',   'cranking-decay'),
    ('Injector Priming Pulse by RPM', 'cranking-rpm-comp'),
    ('Ignition Timing Trim',          'ignition-trim'),
    ('Acc. Throttle Request',         'accel-throttle'),
    ('VVEL Main Drivability',         'vvel-duration'),
]

def concept(name, exact, prefixes):
    if name in exact:
        return exact[name]
    for p, c in prefixes:
        if name.startswith(p):
            return c
    return ''

def read(name):
    with open(os.path.join(VENDOR, name), newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


out = []
for r in read('proecu-maps.csv'):
    out.append(dict(
        vendor='ecutek', doc=r['doc'], section=r['section'], group=r['group'],
        name=r['name'], dims='', axis_x='', axis_y='', output='',
        origin=proecu_origin(r), level=r['level'],
        concept=concept(r['name'], PROECU_EXACT, PROECU_PREFIX),
        source=r['source_image'], note=r['note']))
for r in read('uprev-maps.csv'):
    out.append(dict(
        vendor='uprev', doc=r['doc'], section=r['section'], group='',
        name=r['name'], dims=r['dims'], axis_x=r['axis_x'], axis_y=r['axis_y'],
        output=r['output'], origin=r['origin'], level='',
        concept=concept(r['name'], UPREV_EXACT, UPREV_PREFIX),
        source=r['anchor'], note=r['note']))

# Разметка, не попавшая ни в одно имя, - опечатка словаря, а не пустая работа: она молча
# оставила бы связку непроставленной, и джойн Stage 5 недосчитался бы записей без отказа.
named = {r['name'] for r in out}
stale = sorted((set(PROECU_EXACT) | set(UPREV_EXACT)) - named)
if stale:
    raise SystemExit(f"concept ссылается на имена, которых нет в словарях: {stale}")

cols = ['vendor','doc','section','group','name','dims','axis_x','axis_y','output',
        'origin','level','concept','source','note']
with open(os.path.join(VENDOR, 'catalog.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_MINIMAL)
    w.writeheader(); w.writerows(out)

origins = {o: sum(1 for r in out if r['origin'] == o) for o in ('factory', 'patch', 'unknown')}
concepts = {r['concept'] for r in out if r['concept']}
both = sum(1 for c in concepts
           if len({r['vendor'] for r in out if r['concept'] == c}) > 1)
print(f"catalog.csv: {len(out)} записей "
      f"({sum(1 for r in out if r['vendor'] == 'ecutek')} ecutek, "
      f"{sum(1 for r in out if r['vendor'] == 'uprev')} uprev)")
print(f"origin: factory {origins['factory']}, patch {origins['patch']}, "
      f"unknown {origins['unknown']} (Stage 5 матчит только factory)")
print(f"concept: {sum(1 for r in out if r['concept'])} записей, {len(concepts)} значений, "
      f"{both} покрыты обоими словарями")
