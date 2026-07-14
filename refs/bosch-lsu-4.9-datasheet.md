PRODUCT
DATASHEET
#57006 rev 2.1
Bosch LSU 4.9 Sensor
Part Number #57006
Basic Specifications
 Maximum continuous operating
temperature is 930 °C
 Maximum temperature for short period is
1030 °C (maximum 10 minutes)
 Mounting torque 60 Nm max
 Lifetime estimates:
The Bosch LSU 4.9 sensor is a 5 wire
Sensor lifetimes are highly dependent on
wideband Lambda sensor. It is used to
application. Typically sensor lifetime for
control fuel and ignition systems to optimize
high performance engines is 500 hours in
a car's performance in the areas of emissions
unleaded fuel and 50 hours in leaded fuel.
and fuel economy.
See also Sensor lifetime page 4
 Fuel: Unleaded gasoline, ethanol gasoline The Lambda sensor can be connected directly
blends, methanol, diesel, LNG, CNG, LPG to any MoTeC ‘hundred series’ ECU with a
Lambda upgrade enabled. It can also be
Other Information
connected via the PLM to any ECU or Dash
Compatibility Logger.
 ‘hundred series’ ECUs: M400, M600, M800, Lambda gives a measure of the Air to Fuel
M880 Ratio (AFR) that is independent of the type of
fuel being used.
 PLM - Professional Lambda meter
 LTC/LTCD – Lambda to CAN modules Stoichiometric ratio: no
Lambda 1.00 excess fuel and no
Accessories excess air
 #59001 Mild steel weld-in bung M18x1.5 Lambda > 1.00 Lean: excess air
Lambda < 1.00 Rich: excess fuel
 #59002 Stainless steel weld-in bung
M18x1.5
For a quick reference table to convert Lambda
 #64010 Mating connector to AFR for various fuels see page 3.
 #61118 Adapter loom (sensor connector to
MoTeC ECUs allow for a Lambda aim table
DTM connector)
based on load and RPM. Referencing the
Complete Kit measured Lambda, the Quick Lambda
function in the software adjusts the values in
The complete Lambda kit contains a PLM,
the fuel control table at the specified load and
Bosch LSU 4.9 Lambda sensor, and all
RPM site to achieve the aim Lambda.
required looms and accessories:
Similarly, the Lambda Was function adjusts
 #15005 kit with short loom - length 2.6 m
the values in the fuel control table using
 #15005LL kit with long loom - length 6.0 m
recorded Lambda measurements from a data
log.
MoTeC Pty. Ltd, 121 Merrindale Drive, Croydon South, Victoria 3136, Australia
www.motec.com, Ph 61 3 9761 5050, Fax 61 3 9761 5051, support@motec.com.au
Product specifications are subject to change

PRODUCT
DATASHEET
#57006 rev 2.1
Connector and Pinout

6 pin connector
| Mating connector #64010   |       |          |     |     |     |     |
| ------------------------- | ----- | -------- | --- | --- | --- | --- |
| Pin no                    | Name  | Colour   |     |     |     |     |

| 1   | Ip  | Red  |     |     |     |     |
| --- | --- | ---- | --- | --- | --- | --- |

| 2   | Sensor 0 V  | Yellow  |     |     |     |     |
| --- | ----------- | ------- | --- | --- | --- | --- |

| 3   | Heater –  | White  |     |     |     |     |
| --- | --------- | ------ | --- | --- | --- | --- |

| 4   | Heater +  | Grey  |     |     |     |     |
| --- | --------- | ----- | --- | --- | --- | --- |

| 5   | Ipr  |     |     |     |     |     |
| --- | ---- | --- | --- | --- | --- | --- |

| 6   | Vs  | Black  |     |     |     |     |
| --- | --- | ------ | --- | --- | --- | --- |
Connecting to a ‘hundred series’ ECU
Connecting to a PLM
Lambda
|     |     | ‘Hundred series’ ECU  |     |     | Lambda sensor   | PLM  |
| --- | --- | --------------------- | --- | --- | --------------- | ---- |
sensor
|                | M400/M600/  |           | M880   |         |                |                |
| -------------- | ----------- | --------- | ------ | ------- | -------------- | -------------- |
| Pin            | Name        |           |        | Name    | Pin   Name     | Pin   Name     |
|                |             | M800 Pin  | Pin    |         |                |                |
| 1  Ip          | B_26        |           | 60     | LA1–P   | 1  Ip          | M_9  Ipr       |
| 2  Sensor 0 V  | B_16        |           | 27     | 0V–ENG  | 2  Sensor 0 V  | M_5  Common    |
|                | A_1, A_18,  |           |        |         | 3  Heater –    | M_7  Heater -  |
8, 9, 43,
|              | A_23, A_24,  |     |                      |     | 4  Heater +  | M_2  Heater +  |
| ------------ | ------------ | --- | -------------------- | --- | ------------ | -------------- |
| 3  Heater –  |              |     | 51, 58, 59, Any Aux  |     |              |                |
A_31, A_32,
|     |     |     | 65, 64  |     | 5  Ipr  | M_4  Ip  |
| --- | --- | --- | ------- | --- | ------- | -------- |
A_33, A_34
|              |       |     |             |        | 6  Vs  | M_8  Vs  |
| ------------ | ----- | --- | ----------- | ------ | ------ | -------- |
| 4  Heater +  | A_26  |     | 23, 32, 41  | VBAT   |        |          |
| 5  Ipr       | NC    |     | NC          | NC     |        |          |
| 6  Vs        | B_25  |     | 54          | LA1–S  |        |          |
When connecting a second Lambda sensor (not
available on M400)
| 1  Ip  | B_13  |     | 61  | LA2–P  |     |     |
| ------ | ----- | --- | --- | ------ | --- | --- |
| 6  Vs  | B_12  |     | 55  | LA2–S  |     |     |
MoTeC Pty. Ltd, 121 Merrindale Drive, Croydon South, Victoria 3136, Australia
www.motec.com, Ph 61 3 9761 5050, Fax 61 3 9761 5051, support@motec.com.au

PRODUCT
DATASHEET
#57006 rev 2.1
| Configuration in ‘hundred  |     |     | Lambda versus Air Fuel Ratio   |     |     |     |
| -------------------------- | --- | --- | ------------------------------ | --- | --- | --- |
| series’ ECU                |     |     | Examples of typical values.    |     |     |     |
Procedure described for Version 3 software.
Air Fuel Ratio
| Configuration in Version 2 software is similar.  |     |     |          |     | d    |     |
| ------------------------------------------------ | --- | --- | -------- | --- | ---- | --- |
|                                                  |     |     |          |     | l    |     |
|                                                  |     |     |          | e   | o n  |     |
|                                                  |     |     | Lambda   | n   | n e  |     |
1.  O n  t h e  A d j u s t   m e n u ,  c l ic k  S e n s o r   S e tup
|             |                 |                |     | l i | a b l | e l |
| ----------- | --------------- | -------------- | --- | --- | ----- | --- |
|             |                 |                |     | o   | h     | G   |
| a n d   t h | e n   I n p u t |  S e t u p .   |     | s   | t 5   | s   |
|             |                 |                |     | a e |       | e   |
|             |                 |                |     | M   | 8 i   | P   |
   D o u b l e - c l i c k   th e   L a m b d a  1   ( L a 1 )   G   E D L
channel and in the Input Source box,
|                   |     |     | 0.70  | 10.3  4.5  | 6.8  10.2  | 10.9  |
| ----------------- | --- | --- | ----- | ---------- | ---------- | ----- |
| select Lambda 1.  |     |     | 0.75  | 11.0  4.8  | 7.3  10.9  | 11.6  |
Click Predefined, select #38
|    |     |     | 0.80  | 11.8  5.1  | 7.8  11.6  | 12.4  |
| --- | --- | --- | ----- | ---------- | ---------- | ----- |
Lambda Internal LSU or NTK and
|     |     |     | 0.85  | 12.5  5.4  | 8.3  12.3  | 13.2  |
| --- | --- | --- | ----- | ---------- | ---------- | ----- |
click OK twice.
|     |     |     | 0.90  | 13.2  5.8  | 8.8  13.1  | 14.0  |
| --- | --- | --- | ----- | ---------- | ---------- | ----- |
2.  On the Adjust menu, click Sensor Setup
|     |     |     | 0.95  | 14.0  6.1  | 9.3  13.8  | 14.7  |
| --- | --- | --- | ----- | ---------- | ---------- | ----- |
and then Wideband Lambda Setup.
|     |     |     | 1.00  | 14.7  6.4  | 9.8  14.5  | 15.5  |
| --- | --- | --- | ----- | ---------- | ---------- | ----- |
  Click Sensor Type and enter 7 (LSU
|     |     |     | 1.05  | 15.4  6.7  | 10.3  15.2  | 16.3  |
| --- | --- | --- | ----- | ---------- | ----------- | ----- |
4.9 Normal) or optional 8 (LSU 4.9
| Fast Heat).  |     |     | 1.10  | 16.2  7.0  | 10.8  16.0  | 17.1  |
| ------------ | --- | --- | ----- | ---------- | ----------- | ----- |
|              |     |     | 1.15  | 16.9  7.4  | 11.2  16.7  | 17.8  |
  Click ESC, then click Calibration
Number and enter the number as  1.20  17.6  7.7  11.7  17.4  18.6
| explained on screen.  |     |     | 1.25  | 18.4  8.0  | 12.2  18.1  | 19.4  |
| --------------------- | --- | --- | ----- | ---------- | ----------- | ----- |
  Click ESC, then click Quick Lambda  1.30  19.1  8.3  12.7  18.9  20.2
MODE and enter the number as
|                        |     |     | 1.35  | 19.8  8.6  | 13.2  19.6  | 20.9  |
| ---------------------- | --- | --- | ----- | ---------- | ----------- | ----- |
| explained on screen.   |     |     | 1.40  | 20.6  9.0  | 13.7  20.3  | 21.7  |
3.  On the Adjust menu, click Auxiliary
|                   |     |     | 1.45  | 21.3  9.3  | 14.2  21.0  | 22.5  |
| ----------------- | --- | --- | ----- | ---------- | ----------- | ----- |
| Output Functions  |     |     | 1.50  | 22.1  9.6  | 14.7  21.8  | 23.3  |
  Click Auxiliary Out #X - choose the
|     |     |     | 1.55  | 22.8  9.9  | 15.1  22.5  | 24.0  |
| --- | --- | --- | ----- | ---------- | ----------- | ----- |
number of the output that has the
|     |     |     | 1.60  | 23.5  10.2  | 15.6  23.2  | 24.8  |
| --- | --- | --- | ----- | ----------- | ----------- | ----- |
sensor heater connected.
  Enter 9 (Lambda Sensor Heater) and
| click ESC.  |     |     |     |     |     |     |
| ----------- | --- | --- | --- | --- | --- | --- |
  Click Parameters and enter 1 for
Lambda 1.
Repeat the configuration for a second Lambda
sensor if required (not available in M400).
MoTeC Pty. Ltd, 121 Merrindale Drive, Croydon South, Victoria 3136, Australia
www.motec.com, Ph 61 3 9761 5050, Fax 61 3 9761 5051, support@motec.com.au

PRODUCT
DATASHEET
#57006 rev 2.1
Lambda Sensor Installation
If the sensor has to be placed near a slip
joint, reverse the slip joints to reduce the
Note: The Lambda sensors are factory
influence of introduced air.
calibrated with a trimming resistor embedded
in the sensor connector. If this connector is
cut off and replaced the sensor will require a Introduced air No air introduced
free air calibration.
The Lambda sensor should be fitted to the
exhaust flow
exhaust system with the sensor tip protruding
into the exhaust gas flow.
Incorrect Correct
Considerations when fitting a sensor:
Sensor Warm-up
 Place the sensor on an angle between 10
The internal heater in the sensor is powerful
and 90 degrees to the vertical with the tip of
enough to allow accurate measurement when
the sensor pointing down to prevent
gas temperature is at room temperature. The
condensation build up between the sensor
sensor will take approximately 20 seconds to
case and the sensor ceramic.
heat up.
 Do not place the sensor in a vertical
The maximum continuous operating
position; excess heat soak will prevent
temperature of the sensor is 930 °C. Sensors
proper operation.
should not be used at higher temperatures for
a prolonged period. The sensor can be heated
to 1030 °C for a maximum of 10 minutes, but
this may reduce the accuracy.
Sensor Lifetime
Sensor lifetimes are highly dependent on
application for example the type of fuel used
Correct
and the volume of gas flow over the sensor.
Incorrect
Some factors that reduce sensor lifetime are:
 Place the sensor at least 1 meter from the
 Contaminants such as silicon, lead, oil, etc.
exhaust ports to avoid excessive heat
(use sensor-friendly sealants)
(recommended).
 Thermal cycling and exposure to exhaust
 Place the sensor at least 1 meter from the
fumes without any heating control active
open end of the exhaust system to avoid
incorrect readings due to outside oxygen  Incorrect placement in the exhaust that can
(recommended). overheat the sensor
 Place the sensor away from the flame front  Leaded fuel – substantially reduces lifetime
coming out of the cylinder head and away  Water jacketed exhaust manifolds as in
from areas where one cylinder may have PWCs – substantially reduces lifetime
more effect than another.
At the end of its life the sensor becomes slow
 If possible, do not place the sensor near to respond and does not read rich properly.
exhaust slip joints; some designs allow air Regular free air calibrations will maintain the
to enter resulting in incorrect readings. accuracy of the sensor over its lifetime.
MoTeC Pty. Ltd, 121 Merrindale Drive, Croydon South, Victoria 3136, Australia
www.motec.com, Ph 61 3 9761 5050, Fax 61 3 9761 5051, support@motec.com.au
