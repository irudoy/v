UpRev LLC Tuning Guide. Rev 8 Feb 2022

Nissan Tuning Guide

Page 1 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Contents

1.  Knowing Which ROM to use ............................................................................................................................................. 5

2.  ROM Dumps & Submitting ECU Data ............................................................................................................................... 5

3.  Flashing your Vehicle ........................................................................................................................................................ 6

IMPORTANT ................................................................................................................................................................... 6

Applying and Using your UpRev License ....................................................................................................................... 7

Flashing The ECU Back to Stock ..................................................................................................................................... 9

License & Flash Errors ................................................................................................................................................... 9

4.  Fuel Parameters................................................................................................................................................................ 9

Fuel Targets: .................................................................................................................................................................. 9

Fuel Compensation: .................................................................................................................................................... 10

K - Fuel Multiplier: ....................................................................................................................................................... 10

Important ...................................................................................................................................................................... 11

Mass Air Flow Sensor: ................................................................................................................................................. 11

Cranking Enrichment Initial Value: .............................................................................................................................. 12

Injector Priming Pulse Mode 1 - 4: .............................................................................................................................. 12

Cylinder Trim: .............................................................................................................................................................. 12

Injector Minimum: ...................................................................................................................................................... 12

Fuel Target Lookup Delay: ........................................................................................................................................... 12

Adjust Injector Latency: .............................................................................................................................................. 12

Calculated Load ........................................................................................................................................................... 13

Load Point Scaler: ........................................................................................................................................................ 13

5.

Ignition Advance Parameters ......................................................................................................................................... 13

Ignition Timing Trim / Burn Rate ................................................................................................................................. 13

Ignition Timing Knock Windows .................................................................................................................................. 14

Knock Listening Threshold........................................................................................................................................... 14

6.  Cam Phasing ................................................................................................................................................................... 14

7.  Rev & Speed Limits ......................................................................................................................................................... 15

8.  Electronic Throttle: ......................................................................................................................................................... 15

Throttle A: ................................................................................................................................................................... 15

Acc. Throttle Request .................................................................................................................................................. 16

Throttle Opening Area of Duct Area Calculation: ....................................................................................................... 17

Throttle Valve Opening Target: ................................................................................................................................... 17

Throttle Flow Potential for Fuel Comp X Trace (Low & High) ..................................................................................... 17

Page 2 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

9.  Torque Management ...................................................................................................................................................... 18

Estimated Torque Delivered: ...................................................................................................................................... 18

Target Drive Force: ...................................................................................................................................................... 19

10.  Utilities............................................................................................................................................................................ 19

Copy Map to Other Slots: ............................................................................................................................................ 19

Swap Map Slots: .......................................................................................................................................................... 19

11.  ARC ................................................................................................................................................................................. 19

Calibration – DO NOT CHANGE ................................................................................................................................... 19

Flat Foot Shifting ......................................................................................................................................................... 19

General ........................................................................................................................................................................ 19

Launch Control ............................................................................................................................................................ 20

Rolling Anti-Lag ........................................................................................................................................................... 20

12.  Simplified Timing (ARC) .................................................................................................................................................. 20

Simplified Timing (Map 1 – 5) ..................................................................................................................................... 20

Knock Correction ......................................................................................................................................................... 21

Oil temperature Correction ......................................................................................................................................... 22

Coolant Temperature Correction ................................................................................................................................ 22

Intake Air Temperature Correction ............................................................................................................................. 22

Settings -> Switchable Settings ................................................................................................................................... 22

13.  Cooling ............................................................................................................................................................................ 23

14.  Idle .................................................................................................................................................................................. 23

Idle Target (Map 1-5) .................................................................................................................................................. 23

Idle Target Gear ........................................................................................................................................................... 23

Idle Target Low ............................................................................................................................................................ 23

15.  Misfire ............................................................................................................................................................................. 23

Crank Drag A, B and C.................................................................................................................................................. 23

Crank Drag Crank Angle Pulse Width 1-4 .................................................................................................................... 23

16.  Settings ........................................................................................................................................................................... 23

ETC Control: ................................................................................................................................................................. 23

NATS: ........................................................................................................................................................................... 24

17.  VVEL ................................................................................................................................................................................ 24

VVEL Angle (Editing not recommended) ..................................................................................................................... 24

VVEL Decel ................................................................................................................................................................... 24

VVEL Intake Phasing .................................................................................................................................................... 24

VVEL Limit (Editing Not Recommended) ..................................................................................................................... 24

Page 3 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

VVEL Main Drivability .................................................................................................................................................. 25

VVEL Max & VVEL Min ................................................................................................................................................. 25

VVEL Duration WOT .................................................................................................................................................... 25

18.  Toggles ............................................................................................................................................................................ 25

Cruise Enabled. ............................................................................................................................................................ 25

Enable Manual Transmission Swap ............................................................................................................................. 25

Single Bank Fuel Trim O2 Hack .................................................................................................................................... 25

19.  ARC Toggles .................................................................................................................................................................... 25

Rolling Anti-lag ............................................................................................................................................................ 26

Burnout Mod ............................................................................................................................................................... 26

Flat-Foot Shifting ......................................................................................................................................................... 26

Launch Control ............................................................................................................................................................ 26

Load Activation for Simplified Timing ......................................................................................................................... 26

Simplified Timing ......................................................................................................................................................... 26

20.  Log-able parameter descriptions ................................................................................................................................... 26

UpRev ROM specific parameters ................................................................................................................................ 26

Nissan Standard parameters ....................................................................................................................................... 26

21.  Troubleshooting & Diagnostic ........................................................................................................................................ 27

Map switch not switching maps .................................................................................................................................. 27

Cruise Control light not flashing when switching Maps .............................................................................................. 27

UpRev License not Identified ...................................................................................................................................... 27

Launch Control not Engaging ...................................................................................................................................... 27

Flat-Foot Shifting Activates Randomly ........................................................................................................................ 28

Cruise Control Deactivates Randomly ......................................................................................................................... 28

Rolling Anti-lag not Activating ..................................................................................................................................... 28

This guide was written with the assumption that the reader is an experienced tuner with a solid understanding of
internal combustion engine tuning techniques. Keep in mind that some ROM versions have parameters that other ROMs
do not have.

Page 4 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

1.  Knowing Which ROM to use
To find out which ROM should be used on a given vehicle, check the ECU part number with the UpRev ROM Editor.  The
ECU part number is displayed by the ROM editor when the ECU is turned on and the cable establishes communication
with the ECU. The part number will automatically be displayed in the "ECU Part Number" section once the
communication is established.

Once the ECU part number has been identified click the "Get Tune and Stock Files" button. Type the last 5 digits of your
ECU part number into the pop-up window. The software will automatically fetch the latest master ROM available for the
application. Select the ROM and download it to the destination folder.

2.  ROM Dumps & Submitting ECU Data
If the ECU part number on the vehicle being tuned is unavailable for tuning the user will need to copy the ECU data and
submit it to UpRev. The process is simple, (*MAKE SURE UPREV ROM EDITOR IS RUNNING IN ADMINISTRATOR
MODE*) when the ECU is identified, the status window will change to “ECU Ready”. Click the “Copy ECU Data” button. A
dialog box will open, be sure to save the file in a folder that has read / write permissions. (My Documents is
recommended). The ECU Dump in some applications will be slow, so whenever doing an ECU dump it is recommended
that the user turns on the hazard lights and connects a battery tender. This is recommended to make sure the intelligent
power management does not turn off the ECU or deplete the battery voltage.  When the ROM Dump is complete, right
click the file and confirm the file size. Depending on the application the file size will be anywhere from 512kb to 3Mb. If
the ROM dump is 0kb this means the drive that was pointed to does not have enough storage space or the destination
folder did not have write permissions.

Page 5 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Once the ROM dump is complete the ROM data can be submitted either by email to roms@uprev.com or by pressing
YES on the “Submit dump now?” prompt after the ROM dump finishes. When the YES button is pressed, this form will
appear please attach the correct ROM file (.bin extension) and populate the data fields with the vehicle information.

When the information is filled out, ROM dump is attached and the submit button is pressed the user will get one of two
scenarios. The user will receive confirmation that the ROM dump has been successfully submitted. In the event the ROM
dump fails the user will be re-directed to the online ROM submission page.

3.  Flashing your Vehicle

IMPORTANT
Before re-flashing the ECU be sure that the battery terminals are clean and tight, make sure that the battery is properly
charged. If the battery voltage drops too low during the re-flash and the ECU turns off the incomplete flash can
potentially brick the ECU. It is very important that to maintain a solid and reliable connection. If the connection is
inconsistent this can be due to connector pins being out of spec, vehicle wiring, faulty USB ports, or simply a faulty
UpRev interface. DO NOT re-flash the vehicle until a reliable connection is made in a location that is safe. Some
applications are recoverable over the OBD port, but not all are. If the ECU cannot be recovered using the UpRev
Software over the OBD Port the user will have to purchase the UpRev ECU recovery service and ship the ECU to UpRev.

Page 6 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

We encourage customers to only re-flash their vehicle at a safe location. Do not re-flash your vehicle somewhere that
could leave the customer stranded.

Applying and Using your UpRev License
If the ECU is not UpRev Flashed the very first time it is programed using UpRev the ECU it will consume one re-flash
license from your UpRev interface cable. When the ECU is identified you will see “Unlicensed ECU” in the ECU License
Box like so;

To re-flash the ECU click the “Flash Tune File” Button. Select the desired OSIRIS ROM to flash, a message box will alert
the user a license will need to be consumed. When the re-flash is finished follow the instructions to cycle the ignition.

Page 7 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

When the re-programming sequence is complete the ECU will change to either “UpRev Flashed ECU” or “ARC Flashed
ECU” like so. (See example in the next page).

If the ECU already has an UpRev license installed, then the process will be identical with the only difference being that
no additional reflash licenses will be consumed.
*** NOTE: Only pro cables can hold multiple licenses and flash ECUs. If a customer has an “interface” or “tuner” cable
with a license in the cable AND the vehicle holds a license in the ECU the cable will not allow the user to re-flash until the
license is consumed. Once the cable holds no license in it, it can flash any vehicle that already holds an UpRev license in
the ECU; meaning the owner can own one cable and reprogram multiple Nissan vehicles. Users can continue to purchase
licenses for multiple vehicles if they wish to use UpRev in them, but flashing will only work if the conditions above are
met. The UpRev cable is not married to a specific vehicle or ECU.

Page 8 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Flashing The ECU Back to Stock
In certain situations, customers choose to flash their vehicles back to stock. Unless you receive written authorization
from an UpRev employee to remove the license for diagnostic purposes DO NOT USE THE “BACK TO STOCK.OSIRIS”
ROM. THE UPREV LICENSE WILL BE ERASED. CUSTOMERS WILL NEED TO PURCHASE A NEW LICENSE IF THEY WISH TO
RE-INSTALL UPREV AT A LATER DATE. Most diagnostics can be done by flashing the ECU with a brand new un-used un-
modified UpRev ROM. (Please refer to the “Knowing Which ROM to use” section for details on how to download a fresh
ROM). The ROMS downloaded from UpRev only contain map switching, however if left unmodified the ROMs will
function like a factory ECU with the exception it will not remove the UpRev License.
*** NOTE: If an unmodified UpRev ROM is flashed the ARC License WILL be refunded back to the cable used to flash the
ECU. (This means when the modified ROM with ARC enabled is flashed the ARC license will be re-installed back in the
ECU no problem.)  If the current ROM in the ECU has NATS disabled, flashing an unmodified ROM will turn NATS back on.
Only UpRev dealers and Pro-Tuners can disable NATS on a ROM File.

License & Flash Errors
License Error 00: The ECU does not have a recognized UpRev license and the cable flashing the ECU does not have an
available license in it.  If map switching is active or the customer KNOWS for a fact the ECU has an UpRev license in it
please refer to page 27 for K-line explanation. (Example: car has over sized intakes, bigger injectors, turbo NATS disabled
etc. vehicle runs fine but license is not recognized.)

License Error 0x07: This can be one of two things; The software has updated since the last cable license report was sent
back from processing, or the cable was used to diagnose or flash a vehicle while UpRev was processing the license
report. When a cable license report is sent processing switch the laptop in airplane mode so that the software does not
update overnight & do not use the cable until the new license report arrives and is applied to the cable.

License Error 11: ECU is currently locked by a non UpRev tuner. ECU needs to be flashed back to stock (remove their
license / software) to be able to use UpRev.

Software stuck on “Turn Vehicle off” Screen: This error occurs when the cable and software time-out after a re-flash. It
is important to pay attention and follow the instructions on the screen as they instruct in a timely manner. The solution
to this case is to turn off the vehicle, count 20 seconds, turn the Ignition back on (without starting the engine),
disconnect the UpRev cable from the USB port and plug it back in. This will re-start the timer and allow the  flash process
to finalize.

4.  Fuel Parameters

Fuel Targets:
X – Axis = BFS (theoretical injector PW), Y – Axis = Engine RPM
The values in the table tell the ECU what Air Fuel Ratio (AFR) to try to run.

** Fuel targets tuning tips:
This table should be set to the AFR targets the user WANTS the ECU to run.  Once the table is setup for the AFR targets
to run there should be no reason to adjust it again unless the user wants to run a different AFR target.  Using the fuel
compensation table and MAF curve to correct the air flow and in turn the injector pulse widths so that the ECU can
match the AFR targets programmed in this table to run. Do not try to adjust this table to get the ECU to run a desired
measured AFR different than the AFR in the target table. Once the fuel compensation and MAF curve are tuned so that

Page 9 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

the ECU is matching the targets set, adjusting the tune to run new targets is as simple as changing this table.  The ECU
should hit new targets with little to no tuning once the other fuel parameters are dialed in.

Fuel Compensation:
X – Axis = Volumetric Flow Ratio; Y – Axis = RPM
There are 2 types of fuel compensation tables to be aware of depending on the ROM being used.
Fuel Compensation Main is the primary table that every ROM uses, Fuel Compensation Cold is only used when the
vehicle is still in warm up stage.  Once the coolant temperature gets up to 70°C the ECU will switch to the Main table. For
both tables, the values represent the amount of measured air in the plenum that will be used by the cylinder during that
fill cycle. 100 is all of the measured air inside the plenum.  Above 100 is adding injector PW, and below 100 is taking
injector PW out.

** Fuel Compensation tuning tips:
This is one of the tables that will be used to correct the AFR so that the AFR in the Fuel Target table matches what the
engine is running in real time. It is always recommended to use an aftermarket standalone wideband controller gauge to
confirm the Air Fuel Ratio mixture. Increase the values to richen the AFR and decrease them to lean out the AFR. This
table is used to fine tune the final fuel output after the Mass Air Flow sensor curve has been calibrated and smoothed
out.

K - Fuel Multiplier:
This is the multiplier that the ECU uses to determine the base fuel schedule (BFS).  The BASIC formula is current MAF
value times K value = BFS.  Base fuel schedule is the theoretical pulse width that the ECU would have to run in order to
maintain a stoichiometric AFR or Lambda of 1.  This is NOT the actual injector pulse width.  The ECU will increase the
injector pulse width based on the AFR target, fuel trims, other run time variable parameters, and environmental
conditions. There are some scenarios where the K-Fuel multiplier needs to be adjusted.  The value will need to decrease
it when running larger injectors and increase it when running a modified MAF sensor such as a PMAS sensor, UpRev
calibrated sensor or larger MAF tube.

Page 10 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

** K Fuel Multiplier tuning tips:
Before adjusting the K value for injectors or MAF sensor, start by setting up an “AFR test” table in the AFR targets.  This
table should have the same value everywhere except for the cranking and idle area.  The RPM axis should also be
adjusted so that with any increase in load and RPM the ECU will immediately start running the “flat” AFR target that was
set.  Here is an example of an AFR test table used to tune the K fuel multiplier:

With the AFR test map loaded start doing pulls and watching the AFR.  Keep adjusting the K value until the AFR starts to
get as close to the target as possible throughout the entire RPM range. (It won’t be perfect, but get it as close as
possible.)  Increasing the K will make it richer, decreasing the K will leaner. Once the K value is dialed in finish the rest of
the AFR tuning either with the fuel compensation table, or with the MAF table. Note: Closed loop fueling will only be
active when the AFR Targets are set to 14.7 on supported platforms as of the date this guide was written. AFR Targets
set to anything BUT 14.7 the engine will operate in open loop.

Important
 It is crucial that the K-fuel multiplier value is not lowered less than 10,000. If the K-fuel multiplier is this low (Injector
size is greater than 1300cc) the MAF scalar should be used to lower the injector pulse width to give you the desired A/F
ratio.

Mass Air Flow Sensor:
Single axis = sensor voltage; Axis is static (not adjustable).
Although the values in this table are percentage (no real-world conversion) they are directly related airflow.

** MAF table tuning tips:
Increasing the values will increase the injector PW and decreasing them will decrease the injector PW at the given
voltage.
** PMAS tuning tips:  The PMAS sensors are inconsistent from one sensor to the next.  To start, load the PMAS pre
tuned curve with the utility named “Select MAF Type” found under the fuel section of the ROM tree.  This curve will get
it into the ballpark, but will still need a lot of work, especially in the low voltage areas (idle, cranking). It is crucial to dial
the K value in under some load not just free revving the engine. Once the K value set for load so that the ECU is running
the targets that are set in the AFR Target table, adjust the MAF curve so that the car will idle correctly.  Adjustments will
still need to be made to the rest of the MAF curve to get your AFRs perfect.
** Helpful trick:  If the MAF values were raised so high that the table is maxed out more head room can be made by
raising the K value via multiplying it and then multiply the entire MAF table by the inverse of that value.  Example,

Page 11 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

multiply the K value by 1.2 (120%) and then multiply the ENTIRE MAF table by .8 (80%).  The result is that the vehicle will
run the same, but there is more room to raise the MAF table.

Cranking Enrichment Initial Value:
Axis = coolant temp.  Axis is static (not adjustable)
The Cranking Enrichment Initial Value is the raw injector pulse width that the ECU will command during the first
injection event during cranking; based on coolant temperature. This is the main table that needs to be tuned when
larger or smaller injectors are installed. Improper calibration of this table is known to trigger P0300 or other misfire
codes.

Injector Priming Pulse Mode 1 - 4:
Axis = coolant temp.  Axis is static (not adjustable)
These tables vary from vehicle to vehicle, but the function is the same. The main function is a decay rate of the injector
pulse, from the initial crank pulse to the calculated injector pulse width based on the measured airflow. (100% = slowest
possible decay rate, longer rich running time, 0% = shortest decay rate switching to measured air as soon as possible.)

Injector Priming Pulse by RPM 1 - 4:
Axis = RPM. Axis is static (not adjustable)
This is a multiplier table for the Cranking Enrichment Initial Value table based on engine RPM. 100% uses the entire
injector pulse width from the Initial value. We use this table to fine tune the cold start for big injector cars as you
approach the smaller pulse widths when the adjustable resolution on Cranking Enrichment Initial Value steps are too
big.

Cylinder Trim:
This table will adjust the injector PW for a single cylinder across the board.  It will multiply the final injector pulse width
based on this number. (100 = unchanged, 80 = injector pulse multiplied by 0.8, 120 = injector pulse multiplied by 1.2)

Injector Minimum:
Injector Minimum Pulse Width is the minimum injector pulse width that the ECU will ever run during normal operating
conditions. Injector manufacturers provide the minimum pulse width data sheets; Type those numbers in this table.

Fuel Target Lookup Delay:
This parameter is set to a value that is not zero on some V8 engines.  This parameter is a delay constant that is used to
“smooth” the AFR lookup when the throttle is snapped open. Most ROM's have this value set to 0, this is the amount of
time delayed when the AFR target is something other than 14.7 and how fast the ECU will target the different AFR
Target.

** Lookup delay tuning tips: Set this value to “0” when tuning a vehicle.  This becomes particularly critical when tuning
for forced induction.  If the value is left stock, then when the throttle is snapped open the AFR will slowly taper down to
the rich setting and the engine will probably knock while it is still running the leaner targets. (Leading to engine damage
in the long run.)

Adjust Injector Latency:
Injector latency in Nissan ECUs is modeled by a simple line (y = mX + B) where the 14V offset is the constant B and m is
the slope of the line.  This utility/wizard is used to calculate the injector latency for a given 14V offset and slope it then

Page 12 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

displays what the calculated latency will be for any given voltage. Set these values as close as possible to the Injector
manufacture specs. (Each injector manufacture is different.)

Calculated Load
Axis = Engine RPM.  Axis is static (not adjustable).
The ECU calculates the Engine load by dividing the current base fuel schedule into the value that is in this table for the
given RPM.

** Calculated load tuning tips:
The calculated load will affect the way the Automatic Transmission reacts.  It is particularly important that the calculated
load read 100% at WOT on a forced induction AT vehicle so that the AT computer will run the correct line pressures.  If
you are not logging 100% at WOT, lower the values in this table at the given RPM.

Load Point Scaler:
Single Constant:
This is the main parameter that needs to be changed when resizing the fuel injectors. This directly affects all the tables
that use the BFS for load. It is especially important for forced Induction applications. This parameter should be set to
what the expected BFS at WOT will be at peak load and RPM. Use this to make sure that the timing tables, calculated
torque tables, AFR target etc. are all within range of the BFS. Unlike popular belief DO NOT manually re-scale the tables
by changing the numbers in the load axis, use the Load Point Scaler instead.

5.  Ignition Advance Parameters

Ignition Timing Trim / Burn Rate
X-Axis = Base Fuel Schedule; Y-Axis = Engine RPM
Nissan handles ignition timing differently than what most tuners are familiar with. Nissan calculated the required
ignition timing advance for MBT through a complex internal calculation, along with an Ignition correction table for fine
tuning. Some ECUs have Ignition Timing Trim Cold, Ignition Timing Trim Normal & Ignition Timing Trim High Octane while
other ECU's will only have Normal & Cold tables. During our early days we believed these numbers were "Burn rate"
values which many people have become accustomed to tuning with. However, we have discovered that the real value is
timing trim of the internally calculated Ignition timing value. Like so

RPM >> Engine Load >> Mass Air Flow >> Calculated MBT >> Ignition Timing Trim >> Knock Strength Feedback == Final
Ignition timing value.

Since the calculation for the MBT is not a table, but a formula based on a few inputs, there is no "base timing table". So,
we use the Timing Trim table for making changes when tuning with the OEM Ignition timing strategy.

** Ignition Timing Trim tuning tips:
There are different timing tables that Nissan ECUs use.
Timing Main – This is the primary ignition table that used under normal operation.
Timing High Det – This is the ignition table that the ECU will use if it detects too much activity with the knock sensor.
Timing Cold – This table is only found in the newer Nissan ECUs, and it is only used until the coolant temperature goes
above 70°C. After that the ECU will switch over to the “Main” table.

Page 13 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Although there is no way to convert the table to degrees BTDC, adjustments are made in the same way as any typical
timing table. (Higher values yield more ignition advance.) The only proper way to tune ignition advance is with the
assistance of a dynamometer to verify that the timing advance is adequate and not just stress on the engine.

When tuning any ECU to make sure the ignition table Is always being accessed within the load axis limits.  The easiest
way to do this is to use the “map tracing” feature and make sure the crosshair is not moving outside of the table during
a WOT run. If the crosshair does go outside of the table, then the RPM and/or BFS axis should be adjusted through the
Load Point Scaler so that this does not happen.

On newer vehicles the ignition timing algorithms rely heavily on knock sensor feedback and run a constant open loop
timing advance. You WILL still have to remove timing for forced induction applications so that it engine damage does not
occur before the ECU has a chance to do any learning. In our testing it was found that pulling LARGE values from the
main ignition table in a naturally aspirated application caused a LARGE power drop on the first run, but after a numerous
consecutive runs the ECU would advance the ignition right back to where it was before based on knock sensor feedback.

For the early ROM files (most pre-2009) there is a parameter that can be logged via the ROM editor called “knock
strength” (which is a knock counter.)  Every time the ECU detects a knock event, the counter will jump. The amount of
the jump will depend on what ROM is being run and how severe the knock was. Since the counter moves by different
amounts for different ROMs it is impossible to say what a good or bad number is. The knock counter is bound to move
around a little, even on a stock car with stock tune. If there is consistent knock, (continuous rise in knock strength) then
the advance is too aggressive.

For forced induction it is recommended that a knock listening device be used. Although there are knock parameters that
can be logged UpRev does not recommend relying on these parameters. (It is possible to hear knock on a set of
headphones or with a knock amp before the ECU detects knock or pulls enough timing.) We recommend the Plex Knock
Monitor.

Ignition Timing Knock Windows
**These tables are only available to pro tuners.
The X and Y axis are shared with the ignition tables.
The knock window tells the ECU where to use the knock sensor feedback. 1 turns the algorithm on and 0 turns it off.

Knock Listening Threshold
X-index Engine RPM, Y-index Cylinder Number
This table is where the ECU references to trigger as a knock event. We do not currently have an exact translation into
the KHz scaling for the sensor in correlation to the value in the ECM so it is displayed as 0-100% with very fine
adjustability. This table is important to calibrate for engines with forced induction or engines with aftermarket internal
components. We do-not recommend making changes to this table without a professional third party knock monitor
installed. (A higher value in this table means more noise will be filtered and less likely it is for the ECM to trigger a knock
event. Lower the value for more sensitivity, (in the event external knock monitor detects knock before ECU does.) Use
with extreme caution.

6.  Cam Phasing
X-Axis = Base Fuel Schedule; Y-Axis = Engine RPM
The value entered in the table is what camshaft advance or retard the ECU will target. Most vehicles have at least Intake
camshaft advance, some engines have both Intake & Exhaust.

Page 14 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

7.  Rev & Speed Limits
Rev and Speed Limits are exactly that. The value in these fields are the exact rev limit.
Rev and Speed Limits tuning tip:  One problem commonly encountered is not raising the “Throttle Cut Rev Limit” when
trying to raise the rev limit. It is best to set the throttle cut rev limit at least 100 RPM before the fuel cut. It is much safer
and better for the engine to use throttle cut instead of bouncing from the fuel cut RPM limiter. Some applications have
an oil temperature and coolant temperature RPM limiter.

8.  Electronic Throttle:

Throttle A:
X-Axis = Flow Potential; Y-Axis = Engine RPM
The values in this table reflect the estimated torque generated by the engine at different throttle positions and engine
RPM. We recommend tuning this table with a dyno to measure torque increase. (it is recommend increasing this table in
tandem with the Estimated Torque Delivered Table.) This table is especially crucial for automatic transmission forced
induction applications. Based on the generated torque at the flywheel the ECU will know to reduce the throttle input
and ignition advance during the gear shift event at high loads to help the transmission deal with the generated torque
and have safer faster shifts.

** Electronic Throttle tuning tips:  Tuning this table is a matter of trial and error. Since Throttle A increases based on
Flow potential in Comparison to Estimated Torque Delivered increasing based on the BFS it can be time consuming. A
properly matched Throttle torque table and estimated torque table will give you faster firm shifts and better drivability.
This is especially important for automatic transmission forced induction applications, the ECU pull the right amount of
torque during gear shifts. The way you want to tune this table is that at the area where the Throttle A table is tracing, if
your torque increased by 15% you go to the same spot on the Estimated Torque Table and increase the torque value by
15% as well. (The tables are not a 1:1 copy, we are unsure at the time this guide was written as to why this is, we
assume it is due to driveline torque conversion.) It is extremely important that the difference ratio between both tables
stay as close as possible to maintain a good relationship. Not all cars are the same, it is important to note the ratio
before making any changes, otherwise if Throttle A torque ratio and Estimated Torque ratio changes too much the ECU
will trigger a P0605.

Page 15 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Acc. Throttle Request
Y-Axis: Accel Deg
Some cars have multiple tables depending on their drive modes, while other cars only have two tables (low Speed &
High Speed.) Other ROMs will have MANY tables. (Low Speed, High Speed, Cold, Warm, Idle, Snow, Sport, Eco, etc).
These are the tables that open the throttle to a commanded degree based on the accelerator degree. We are still testing
on getting all the throttle table labels correct for vehicles with multiple drive modes.

***Acc Throttle Request Tuning tips: Some ROMs have normal tables and Alternative tables (ex: Acc Throttle Request
Low Speed, & Acc. Throttle Request Low Speed (Alt)). It is mandatory that both tables match. If these tables are different
the ECM will trigger a P0605 error code. If the Acc. Throttle Request Low Speed has a higher Value than the Acc. Throttle
Request High Speed, this will cause the ECM to Trigger a P0605 code; If Low speed Opening Degree is less than High
Speed it will be no faults triggered.

Page 16 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Throttle Opening Area of Duct Area Calculation:
Y-Axis: Throttle Opening (Degrees)
This table is what the ECU references for throttle opening degree and the available surface area for airflow. This is the
table to calibrate when upgrading to larger throttles. Calculations will need to be made to populate the opening area.
(Based on the new throttle body size and flow potential.)

Throttle Valve Opening Target:
Y-Axis: Throttle Opening (degrees)
This table works together with Throttle Opening Area of Duct Area Calculation. We recommend keeping the same
differential ratio between both tables. Due to the vast number of ROMs available there is no clear differential
percentage or ratio each platform is a little different, so we recommend maintaining the ratio.
NOTE: Throttle Valve Opening Target 1 & 2 must be an exact match.

Throttle Flow Potential for Fuel Comp X Trace (Low & High)
Y-Axis – Throttle Duct Opening Area
This table is what the ECM uses to determine where the tracer for the fuel compensation table will trace (dependent on
throttle flow.) Typically, this is never changed but vehicles with upgraded throttles need to use this table to dial in a
smooth tracer for the fuel compensation table.

Page 17 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

9.  Torque Management

Estimated Torque Delivered:
X-Axis = Base Fuel Schedule; Y-Axis = Engine RPM.
Although this table is present in all ROMs, it is ONLY used for automatic transmission vehicles.  The values in the table
are the estimated engine torque that will be delivered at the given RPM and load (BFS) in Newton Meters.  The ECU
sends this value to the AT computer so that the AT computer can run the appropriate line pressure.

** Estimated Torque Delivered tuning tips:
This table is particularly critical for forced induction vehicles with automatic transmission.  When running larger injectors
the load axis gets skewed due to the reduced injector pulse widths for the same flow.  The entire table should be shifted
to the right so that the AT expects more torque at lower BFS. The Load Point Scaler Live Tuning should be lowered so
that the Base Fuel Schedule traces along the right third of the map at WOT. The values in this table should increase by
the same percentage of gained torque from the power adders.  Verify that the transmission is not slipping by logging the
“AT Slip” parameter in the ROM editor.  This parameter should stabilize once the torque converter locks up.  If the
engine RPM is running above TC lock up and this parameter starts to waiver that is an indication that the clutches in the
AT are slipping. AT Slip will only be accurate at WOT above the torque converter stall lock speed.

Page 18 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Target Drive Force:
We do not recommend changing these cables at the time this guide revision was written. These tables affect the
selected gear based on accelerator position. This cable is BETA and Pro-Tuner access only. Current information is that
Throttle A Torque x Calculated gear Ratio = Delivered Torque.  In such the ECU will do it’s best to deliver the correct gear
ratio so that the Torque multiplication will deliver the correct amount of torque at the drive wheels. An improperly
calibrated table will cause erratic shifting behavior and possible driveline damage.   Sub Operation Mode is used when
“Tow Mode” is engaged in some vehicles. Alt Tables must be a 100% match to their perspective counterpart, otherwise
P0605 will be triggered.

10.  Utilities

Copy Map to Other Slots:
This is the utility used to copy Switchable map settings from one map to another. Ex: you can select to copy all of the
switchable contents of Map 1 to Map 2, Map 3, Map 4, Map 5, or All Maps.  Any parameter that has switchable map will
be copied to and from their perspective map.

Swap Map Slots:
This is used for swapping the data from two maps. Example: accidentally set customer Map 1 for 93 and Map 2 for 91.
Instead of manually making changes, simply use the map swap utility and select the two maps to swap.

11.  ARC

Calibration – DO NOT CHANGE
This is used for diagnostics, in rare cases when a tuner is testing in the field for our developers; we need tuners to have
access to these parameters. These values should not change unless instructed by an UpRev team member.

Flat Foot Shifting
These are the settings for “Flat Foot Shifting” (FFS) setup. All settings here are 100% user configurable. The default
settings are a guideline and starting point for N/A vehicles. Please be aware that ALL the conditions need to be met in
this menu along with the General settings for FFS to activate. These conditions are what the ECU is looking for to
activate FFS mode and the FFS output. Accelerator Pedal (Volts): this is the voltage the ECU will be looking for from
Accelerator Pedal Sensor S1, if the voltage is less than the value in the box, FFS will not enable. Flat-Foot Fuel
Compensation: this is the forced amount of fuel that the FFS mode will populate on the fuel compensation table while
flat food shifting is enabled. Tweak this setting to make sure the Air Fuel Ratio during FFS is appropriate. Flat-Foot
Vehicle Speed Activation; The minimum vehicle speed the ECU will be looking for to enable FFS. Flat-Foot Minimum
RPM: The minimum RPM the ECU will look for to enable FFS. Flat-Foot RPM Jump: this is the RPM difference the ECU
will try and maintain during FFS. (The default setting is +/- 50RPM.)

General
These are global settings; depending on the vehicle only certain parameters will be available. Global ARC Timing: This is
the ignition advance that the ECU will target during Launch Control, Rolling Anti-Lag & Flat Foot Shifting. The setting
there is a general starting point for N/A Vehicles (-6°), you will want to target something realistic for your application.
Coolant / Oil Temperature Minimum: Minimum coolant or oil temperature the ECU will need to see before it will
enable Two Step, Rolling Anti-Lag or FFS. Coolant / Oil Temperature Maximum: In tandem with the minimum coolant

Page 19 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

temperature this is the other side of the ARC window. If coolant or oil temperatures exceed this value Two Step, Rolling
Anti-lag or FFS will not be enabled due to overheating conditions. All parameters are 100% adjustable by the end user.

Launch Control
These are the settings for Launch control setup. All are 100% user configurable. The default settings are a guideline and
starting point for N/A vehicles. Please be aware that ALL of the conditions need to be met in this menu along with the
General settings in order for Launch control to activate. Launch RPM This is the target RPM at where the Launch control
will be armed, Launch RPM Restore this is the RPM where the Ignition will turn back on, typically this is called the
hysteresis. Launch Fuel Compensation, This is the value used as a substitute for the fuel compensation table during the
event where Launch Control is active. Launch Vehicle Speed, This is the maximum wheel speed allowed for Launch
control to be activated, meaning your wheel speed needs to be less than this for launch control to be active.  Launch
Accelerator Pedal (Volts), this is the minimum amount of Volts that the Accelerator Pedal S1 needs to be in order to
activate Launch Control.

Rolling Anti-Lag
Rolling Anti-Lag was developed to help turbo charged vehicles in roll-racing competitions. To activate this feature the
General conditions must be met, once those conditions are met you can arm the rolling launch control by pressing &
holding the “Cancel” button on your cruise control buttons. The following conditions are fully adjustable by the end user
and must be met along with the General settings. Rolling Anti-lag Accelerator Pedal (Volts): The minimum voltage the
ECU will be looking for from Accelerator Pedal S1. Rolling Anti-lag Fuel Compensation: The value that will be used in
place of the fuel compensation table while the Rolling Anti-lag feature is active. Rolling Anti-lag Vehicle Speed
Activation: The minimum vehicle speed required for the Rolling Anti-lag feature to be activated. Rolling Anti-lag
Minimum RPM: The minimum engine RPM required for the Rolling Anti-lag to be activated when the cancel button is
pressed.

12.  Simplified Timing (ARC)

Simplified Timing (Map 1 – 5)
The factory ignition strategy can be challenging to tune with, in some situations it can be dangerous to have the factory
open loop ignition control at the mercy of the factory knock sensor. Typically, high horse power competition vehicles
need fixed timing with some compensation and safety tables. Not all the vehicles we support are offered with ARC
Simplified Timing, but all our core vehicles are patched with it. Simplified timing is a timing table with values that
represent actual degrees BTDC. The X & Y Load axis are 100% independent of the factory Nissan timing table, (meaning
it is possible to enable a higher resolution of the normal timing table.) The timing values in the current ARC timing table
are base values meant to get the car started idling. These values are not intended to be track ready and can cause
damage if not calibrated properly.

Page 20 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Knock Correction
X-index Engine RPM; Y-index Knock Strength
The Knock correction table is the amount of timing that will be subtracted in the event the knock sensor detects noise.
Any time the knock sensor detects noise the knock strength value will change and so the timing correction table will pull
timing as populated in the knock correction table. The settings in the table are generic and meant to be as a starting
point for N/A Vehicles. It is important that this table is calibrated correctly for the application. In earlier ECU’s the knock
strength values are more sensitive to change compared to the 2009+ ECU’s. We is recommended this table is calibrated
in tandem with the Knock Listening Threshold tables. It is not uncommon for the factory knock sensor table calibration
to detect false knock from electrical or mechanical noise. (We have also experienced knock sensors that do not detect
real knock events.)

***KNOCK TUNING TIPS: It is highly recommended to tune the engine using aftermarket knock detection hardware (
such as the Plex Knock monitor or any other high grade knock detection device.) In 2009+ model ECU’s we have
observed that if we clear the ECU memory with a re-flash, and run the car logging ignition advance the knock strength
will first climb and show a very high value even though there is no audible knock through the knock monitor. As we
continue to drive the vehicle and perform more WOT runs the knock strength will decrease and ignition timing will
increase back to a normal value. Relying solely on the Knock strength parameter for forced induction applications can be
tricky, which is why a high grade knock detection device is recommended.

Page 21 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Oil temperature Correction
Y-index: Oil Temperature
This is an oil temperature correction table: Increases or decreases the base ignition advance based on Oil temperature
(only on vehicles fitted with a factory oil temperature sensor).  Not all vehicles are equipped with Oil temperature
sensors from the factory; coolant temperature is used instead.

Coolant Temperature Correction
Y-index: Coolant Temperature
Like the Oil Temperature Correction table this table works in the exact same manner with the exception that it is based
on engine coolant temperature.  Base settings are suggested values for N/A applications but are 100% adjustable by the
end user for their application.

Intake Air Temperature Correction
Y-index: Intake Air Temperature
This table works in the exact same manner as the Coolant Temperature correction & Oil Temperature Correction with
the exception that it is based on intake air temperature.  Base settings are suggested values for N/A applications but are
100% adjustable by the end user for their application.

Settings -> Switchable Settings
When ARC timing was first launched the activation setting was global, meaning all 5 maps would activate the same way.
Due to high demand now all 5 maps can be activated independently. This means the original Settings box will no longer
be used and now switchable settings is where the parameters for ARC activation are setup. Simplified Timing Map 1-5.
Simplified Timing Load Activation (After Cranking): This number is used to compare the BFS. When Load Activation is
used for ARC timing, any time BFS is equal to or higher than this number (regardless of Engine RPM) simplified timing
will be activated. If BFS is lower than this number the OEM Nissan timing strategy will be used. When Load Activation is
turned off Simplified timing will be used solely based on engine RPM. Simplified Timing RPM Activation (After Cranking)
when the engine RPM is equal to or greater than this value simplified timing will be activated; if engine RPM is less than
this value simplified timing will be deactivated.

*** Simplified Timing Tuning tips: Simplified Timing overrides the factory timing at the end of the function.  The way it
works is in these two possible scenarios.

Factory Timing output -> ARC Timing On? -> YES - > Simplified Timing + Knock Correction + Oil Temperature Correction +
Coolant Temperature Correction + Intake Air Temperature Correction = Actual Timing Used.
Factory Timing Output -> ARC Timing On? -> No -> Factory Timing strategy calculation used.

On Manual transmission Vehicles RPM based activation is typically used since it keeps things simple, however we
recommend to only activate after 2000 RPM. (Since the ARC Timing will override the factory timing it can affect cold
start. Setting it to 1500RPM or lower can cause the ECU to jump in and out of ARC timing at idle especially on the
VQ37VHR equipped vehicles.) Having ARC trigger at cold start can cause a P0507, P0506, P050A, or P050E DTC. In
automatic transmission vehicles we recommend using Load Activation for ARC Timing Activation. During shift events
RPM Activation will NOT retard ignition advance to reduce torque, so this will cause premature wear of the transmission
and torque converter. Instead, we recommend only activating ARC timing when the torque converter is locked meaning
the engine load (BFS) is in the upper 1/3 of the load cells.  We recommend logging the vehicle on the Dyno to see what
the BFS is at 75% throttle at 2000 RPM, then set the load activation to be 5 - 10% BFS lower than the logged BFS. This
ensures whenever a customer is at heavy load ARC Timing is used. When the TCM needs to shift and the ECM pulls load
it will revert back to factory timing in order remove ignition advance to reduce torque for the shift event.

Page 22 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

13.  Cooling
This is where the cooling fan settings are. Due to the broad range of vehicles there are two major ways Nissan
programmed the fans. In the earlier days Nissan had three Coolant Temp Fan Switch Point windows with constant Low
and High Parameters, (these would become the switch points for the fans). In 2009 Nissan introduced a 3D table for
some applications. Radiator Fan Speed by Temp: based on Vehicle Speed & Coolant Temperature. (This table
determined the FAN duty cycle.) Nissan also included a couple tables to control Fan speed based on AC Pressure called
Radiator Fan Speed by A/C Pressure (Upper & Lower). (All  three of these tables are fully editable. The old style tables
are in the ECU as well but no longer used in some models.)

14.

Idle

Idle Target (Map 1-5)
Axis = Engine coolant temperature.  Axis is static (not adjustable).
The ECU will try to idle at the set RPM for the given coolant temp.

Idle Target Gear
Axis = Engine Coolant Temperature, Axis is static (not adjustable).
This is the idle target when the transmission is in a drive gear (not Neutral or Park). This table applies only to A/T
Models.

Idle Target Low
Axis = Engine Coolant Temperature, Axis is static (not adjustable)
This is the idle target when additional load is detected from the HVAC, electrical system, and power steering pump.

15.  Misfire

Crank Drag A, B and C
X-Axis: Base Fuel Schedule | Y-Axis Engine RPM.
These tables represent the amount of drag on the crank.  Increasing the values in this table will make it harder for the
ECU to trip the misfire DTCs.  If all the tables are set to the maximum value it will be difficult for the ECM to detect
misfire. This table should only be changed when superchargers are installed when additional crank drag is added.

Crank Drag Crank Angle Pulse Width 1-4
Single Axis: RPM
This is the table where the ECM measures the crank rotation speed. Increased numbers will make it more difficult to
trigger a misfire event, lower values will cause a hypersensitive P0300 – P308 situation.

16.  Settings

ETC Control:
This setting disables the torque management aspects of the electronic throttle control.  Turning this setting off will have
the effect of making the throttle linear.  The ECU will try to run the throttle plate % at whatever the accelerator % is.

Page 23 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

** ETC on/off tuning tips:  Turning this setting off will also disable the cruise control.  Most of the feedback about
disabling this setting is “The throttle is far too touchy, even for race drivers.”

NATS:
** This setting is only available to pro tuners.
NATS stands for Nissan Anti-Theft System.  Turning this setting off will completely bypass the NATS code inside of the
ECU.  Disabling this makes it possible to start the engine without having a key that has been married to the vehicle.  The
setting is intended for testing purposes and for race cars where some users need to swap out ECUs for competition use.

17.  VVEL
These are the current tables available for the VVEL Equipped vehicles.  The way VVEL tables are displayed by Nissan is
based on when the valve begins to open to when the valve is at peak duration.  Since this number is only half of the
duration, to get the complete camshaft duration you can multiply by 2 to get complete cam degree, and by 4 to get
crank degree. (For example, VVEL Decel at 2000RPM = 33° this means at crank angle Cam angle = 66° so at crank angle
== 132°) in comparison VVEL at WOT target at 2000 RPM = 65° this means in Cam angle == 130° and in Crankshaft
Degree == 260°.) Additional to VVEL Duration when valve duration is increased valve lift is also increased, we believe this
to be a linear event (more lift meaning more duration) however we do not have exact measurements of the valve lift
value in exact correlation to valve duration.

VVEL Angle (Editing not recommended)
There are two tables for VVEL Angle these tables are meant as safety so that the ECU cannot be configured to have valve
interference during normal operation.  We do not recommend making changes to this table; do so at your own risk as
catastrophic failure can be caused from improper calibration. There are two tables VVEL Angle & VVEL Angle Alt. These
two should always be the same. They affect the VVEL Shaft Angle in comparison to the camshaft duration that the VVEL
Control unit & ECM will use for their calculation.

VVEL Decel
Single Axis – Engine RPM
This is the target amount of valve duration during deceleration.

VVEL Intake Phasing
Single Axis – VVEL Duration
This is the table where the ECU references the maximum amount of intake camshaft advance in comparison to the VVEL
Camshaft duration. When commanding additional intake valve phasing in the Cam Advance WOT the value must be
equal to or less than this table. If more camshaft advance is desired increase the value of this table accordingly. Be
careful with Valve to piston or valve to valve contact when adding increased valve overlap.

VVEL Limit (Editing Not Recommended)
Single Axis – Cam Timing (Intake Phasing)
This table is cross referenced when requesting Cam Advance on the intake camshaft to set the maximum amount of
VVEL Duration.  This table is used in order to keep the engine from having valve to piston interference during normal
operation. This table together with VVEL Angle is what the ECM uses to target VVEL Angle limits.

*** VVEL Safety tip:

Page 24 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

VVEL Limit & VVEL Angle: The ECU determines the maximum amount of VVEL Duration based on the camshaft advance,
it will also determine the maximum amount of camshaft advance based on the current amount of VVEL duration. If
requesting more VVEL duration and no increase, it is likely user has reached the duration limit based on Intake phasing
angle. If user requests an increase the Intake advance and do not see it target immediately it is likely user has reached
the limit based on current VVEL position.  We strongly recommend not making changes to these parameters.

VVEL Main Drivability
X-Axis BFS, Y-Axis Engine RPM
This is the main table the ECU uses for VVEL Duration based on engine RPM and engine load (BFS) there are two tables,
the main table used during normal operation and the High Detonation table.

VVEL Max & VVEL Min
Single Axis – Engine RPM
These two tables are the Maximum and Minimum values of VVEL Duration based on Engine RPM.

VVEL Duration WOT
Single Axis – Engine RPM
This is the table the ECU references at WOT during its RPM sweet to target VVEL Duration.

-

18.  Toggles

Cruise Enabled.
This is the toggle that was found on the 2003 – 2008 Vehicles without intelligent cruise control. By properly wiring the
cruise control hardware to the vehicle & ECU, enabling this toggle will enable map switching if all other hardware is
connected correctly. It will not enable the actual cruise control function. To install cruise control in the vehicle an actual
cruise control ROM and hardware are required.

Enable Manual Transmission Swap
In 2003 – 2008 VQ35 ROMS and 2009+ VQ37VHR vehicles, when performing a M/T Swap users can set this toggle ON,
turn off all the A/T DTC’s and so long the clutch switch is wired properly the car will function as normal and ignore all the
A/T Tables.  However due to the DTC’s most customers still prefer to flash a M/T ROM.

Single Bank Fuel Trim O2 Hack
This toggle turns off the B2 O2 sensor feedback. This was originally developed for the turbo SE-R Sentra QR25 platform.
This allowed the ECM to have normal O2 feedback by averaging the AFR feedback from all 4 cylinders into B1 S1. ( ot
available for all platforms.)

19.  ARC Toggles
This is the menu to turn on or turn off ARC Features. In order to use these features customer must have an ARC license
in their cable if a license is not already present in their ECU.

Page 25 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Rolling Anti-lag
This toggle will enable or disable the rolling Anti-lag feature; (In order to use this feature Simplified timing must be
activated.)

Burnout Mod
This disables the safety feature in the ECU to reduce engine torque output (In the event that the brake pedal is pressed
at the same time as the accelerator.) This feature is so that customers can stage at the drag strip and perform a burnout
without needing to disconnect their brake switch or add external hardware. Turn this toggle on and you can perform
burnouts as normal. (This is also used for left foot braking or “Trail braking” in road racing / time attack applications.)

Flat-Foot Shifting
This will enable or disable the Flat-Foot Shifting feature; (In order to use this feature Simplified timing must be
activated.)

Launch Control
This toggle enables the Launch Control feature; (In order to use this feature Simplified timing must be activated.)

Load Activation for Simplified Timing
If this toggle is activated in conjunction with Simplified Timing the ECU will use load (BFS) to activate the simplified
timing strategy instead of engine RPM.

Simplified Timing
This toggle is used to enable Simplified Timing. (If the Load Activation flag is not turned on the ARC timing will be
activated by Engine RPM only regardless of load.)

20.  Log-able parameter descriptions

UpRev ROM specific parameters (these can only be logged via the ROM editor):
-  Target Air/Fuel Ratio:  The AFR that the ECU is attempting to run.  Should coincide with the AFR table lookup +

lookup delay.

-  AFR (only available on vehicles that are equipped with a WB O2 sensor from the factory):  The AFR is calculated
based on the A/F Sensor voltage which is referenced to a table in the software.  It is NOT returned directly from
the ECU.  The reading SHOULD be close, but checking against another WB O2 sensor is ideal.

-  Knock Strength: The value will jump up every time there is a knock event.  The amount of jump will depend on

the ROM that is being used and the severity of the knock event.

-  High Det Flag: This parameter will switch from 0 to 1 when the ECU has detected too many knock events in a

-

given amount of time.  When it changes to 1 the ECU will run the high det timing table.
Injector Duty Cycle:  The injector duty cycle is calculated directly from the engine speed and injector pulse width.
The ECU CAN report injector pulse widths that give a duty cycle greater than 100% even though that just means
the injectors are wide open.

-  AT slip:  This parameter is derived from a division of the engine speed and vehicle speed.  The value should

stabilize anytime the transmission is in gear and the torque converter is locked up.  If this value starts to waiver
at WOT after TC lockup, then the clutches inside the transmission are slipping.

Nissan Standard parameters:  **There are MANY more standard Nissan parameters that will not be described
here, most are self-explanatory.
-  A/F correction (B1/B2) = Actual real time fuel trims.  Above 100% is adding fuel, below 100% is taking fuel out.

Page 26 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

-  Base Fuel Schedule (BFS) = The theoretical injector pulse width that the ECU would have to run in order to

maintain a 14.7 AFR.  This is NOT the actual pulse width which will be different depending on the target AFR and
fuel trims.

21.  Troubleshooting & Diagnostic

Map switch not switching maps
It has become popular to add cruise control hardware to the user vehicle to enable the map switching feature. Map
switching doesn’t always work after the install. (Sometimes customers that have vehicles with factory cruise control lose
the map switching feature.) The ECU feature for map switching has not changed in years, and so it is vital that our
dealers and customers know how to diagnose this. With the UpRev interface cable, UpRev Rom Editor logger and a few
hand tools the end user can diagnose the problem.

To diagnose the issue user should log the parameter “Cruise Button Values”. With the ignition in the on position begin
logging this parameter. User will look to see that this value changes when you press the Cancel button, when the toggle
“COAST / SET” and “ACCEL / RES” are pressed it should also change the value at the logger. If the Cruise Button values
number does not change this means the ECU is not seeing the cruise control buttons. This means the hardware has
communication issues; typically, this is faulty wiring or a faulty clock spring.

Cruise Control light not flashing when switching Maps
If the car did not have cruise control fitted from the factory on the early years the light is not soldered into the board so
the light will not work, however, if the car has functioning cruise control light and works normal when operating cruise
control the issue is fixed easily. Disconnect the battery for 5-10 minutes (be sure to turn the ignition on and the
headlamps on to make sure all components are drained completely of their back-up power.) Re-connect the battery, all
systems should be reset and working properly.  (This is assuming user has already verified map switching is working
properly.)

UpRev License not Identified
If the UpRev cable is connected to the vehicle, ignition on and UpRev software displays “Unlicensed ECU” when
customer has already flashed the ECU. If ARC features are activated and working, map switching is active, car is using
oversized intakes or aftermarket injectors driving and properly these are all signs of a tune file being flashed in the ECU.
The problem is the vehicles wiring, whenever the K-Line communication is faulty or disabled the license will not be
identified by the UpRev cable. If the ECU does have a license or flashed and used the license, diagnostic of the K-line
wiring will need to be made. Each vehicle is different so please refer to the corresponding Nissan / Infiniti factory service
manual for details on K-Line wiring and diagnostic. The other alternative cause has been bad / improper ECU power
supply if the ECU is running only on back-up power and not all the power pins the K-line will not be active.  Best place to
diagnose this issue is again with the Nissan Factory Service manual for your vehicle or testing the ECU with a bench
harness.

Launch Control not Engaging
The number one cause of Launch control engaging “randomly” is due to the Temperature windows. Remember to check
the Oil and Coolant temperature Min & Max are met. If the engine is too cold or too hot the ARC functions will not work.
Please refer to ARC -> General for details. Another cause of Launch Control not activating is the accelerator pedal
voltage value is not being met.  Finally, there have been cases where the Neutral / Park switch are not reporting the car
going into gear. (Mainly in M/T vehicles.)  This can be due to faulty wiring or a neutral switch. If the ECU does not see the
transmission is in first gear launch control will not activate.

Page 27 of 28

UpRev LLC Tuning Guide. Rev 8 Feb 2022

Flat-Foot Shifting Activates Randomly
This issue is always related to the clutch switch. Usually, a vehicle’s clutch switch is adjusted too sensitive and if the
customer is resting their foot on the clutch pedal (while all other FFS conditions are met) the feature will activate. Also,
there are cases where customers are not touching the clutch pedal at all, however when the clutch switch is looked at it
is at the very edge of its window and road vibrations, or feedback will cause the switch to arm / disarm; Do not confuse
the clutch switch for the starter switch.  See Diagram below for clarification.

Cruise Control Deactivates Randomly
Same explanation as Flat Foot Shifting randomly activating, please see the section above.

Rolling Anti-lag not Activating
For rolling anti-lag, the reasons for it to not arm is either the general or basic requirements are not being set. See ARC ->
General & ARC -> Rolling Anti-Lag. However, if all the conditions are being met, (engine is not too hot or not too cold,
vehicle speed or RPM not too low.) The only other cause for it to not arm is the Cancel button not being identified by the
ECU. This can be checked by Logging the “Cruise Button Values” and confirming it’s changing when the button is
pressed.

Page 28 of 28


