DATASHEET PART13150
M150 ECU
MoTeC’s M1 ECU range begins a new era in engine
control. The M1’s unique technology redefines the
CONFIGURATION
meaning of customisation, delivering total control
without compromise. Highly advanced security
TheM1seriesECUscomewiththreeconfigurationoptions.
strategies make these ECUs ideal for both category
managed and unrestricted applications. LockedConfiguration
AlockedconfigurationisappropriatewhenanECUcontains
FEATURES specificfirmwaretosuittheapplication.Theusercantunethe
engineinthenormalwaybuttheECUcannotbere-configuredfor
• Smallandlightinrobustmagnesiumenclosure anotherapplication.
• Portinjectioninjectortype
StandardConfiguration
• Largeloggingmemory
Thestandardconfigurationallowstheusertoloadaselectionof
• Latestgenerationhighperformanceprocessor firmwarepackagesavailablefromMoTeC.Theyincorporate
differentlevelsoffunctionalityandtheusercanchooseoneto
• SuitableformodernengineswithDBW,CamControland
suittheirrequirements.Additionalpackagescanbeloadedinto
multipleCANbuses
theECUasandwhenrequirementschange.
• Advancedloggingfeatures,highspeed,multiplelogs(with
OpenConfiguration
accesslogins)
TheopenconfigurationprovidesafullyflexibleECUsolutionthat
• I/OexpansionusingE816,E888expanders
canbepreciselytailoredtoindividualrequirements.Thirdparty
• Flexibletuningsoftware developerscanbetrainedtouseMoTeCM1Buildsoftwareto
• Robustandcomprehensivesecurityfeatures developtheirowncontrolstrategies.
• Programmableinjectordrivecharacteristics IntellectualpropertyisprotectedbytheM1ECU’ssecuritysystem
andremainswiththeECUowner.
• ProgrammabledigitalinputsystemforRef/Sync,wheelspeeds
etc.
• Programmabletriggerlevels,diagnostics
• AllLowSideandHalfBridgeoutputshavePWMcapability
©MoTeCPublished1May2015 Checkforlatestversionatwww.motec.com 11

DATASHEET PART13150
SECURITY SOFTWARE
TheM1'sadvancedsecuritysystemisbasedonpublic-key • MicrosoftWindows™basedsoftware
cryptography,thecornerstoneofsecureinternettransactions,so
• PCTuningsoftware‘Tune’-Usedtotunefuelandignition,set
itisvirtuallyimpossibletochangetheECUfunctionwithout
upsensors,outputsandavailablefunctions
authorisedpermission.
• PCSoftware‘Build’-Usedtocreateacustomsoftware
SecurityisenforcedbytheECUandprotectedbya
packagewithuserspecificfunctions
microprocessorwithintegratedmeasurestopreventtampering.
Apasswordfeaturegrantsdifferentlevelsofaccessfordifferent
BASIC SPECIFICATIONS
userse.g.anenginetuner,adrivetraintuner,andadataanalysis
engineer.
Injector
ThisisalsosuitableforControlECUs.Scrutineeringteamscan
• PeakandHoldInjectorOutputs:12
haveaccesstoextrainformationandareabletolockdown
selectedpartsoftheECU,whileotherteammemberscanaccess • LowSideInjectorOutputs:6
selectedtuningparameters.
Ignition
• Outputs:12
CATEGORY MANAGEMENT
AuxiliaryOutputs
Thecombinationofanadvancedsecuritystrategy,configurable
firmwareandahighperformanceprocessormaketheM1ECUan • HalfBridge:10
idealchoiceforcategorieswithrestrictionsinplaceforeither
Inputs
performanceparityorcostcontainment.Firmwarecanbewritten
specificallyforthecategory,limitingthefunctionalitytotheclass • UniversalDigital:12
requirements.
• Digital:4
Multipledataloggingsetsareavailable,whichcanbepartitioned
• AnalogueVoltage:17
withrestrictedaccesstoallowgenerationofbothjudicial
(scrutineering)andteamdatafromthesamedevice.TheM1 • AnalogueTemperature:6
ECU’ssecuritysystempreventsunauthorisedaccesstodataand
• Knock:4
implementationofunspecifiedfunctionality.
• Lambda(narrowband):2
UPGRADES Data
• CANbus:3
• VariousLoggingOptionsareavailable.
Thelogginglicencedeterminesthenumberofchannelsand • RS232:1
thesampleratesavailable,thereare3levelsavailable:
• LIN:1
– LoggingLevel1Licence
• LoggingMemory:250Mb
Comesstandardwiththeproduct.Thisdiagnosticlogging
Physical
includesafixedlogsetandrate.
– LoggingLevel2Licence • Dimensions:162x127.5x40.5mm
Isanoptionalupgradewhichincludesonefixedlogset, • Weight:445g
200channels(includingdiagnostics)andamaximum200
• Connectors:
Hzsamplerate.
– 2x34pinplasticconnectors
– LoggingLevel3Licence
– 2x26pinplasticconnectors
Isanoptionalupgradewhichincludeseightfixedlogsets,
2000channelsandamaximum1000Hzsamplerate.
• Configuration:
– LockedConfiguration
– StandardConfiguration
– OpenConfiguration
©MoTeCPublished1May2015 Checkforlatestversionatwww.motec.com 22

DATASHEET PART13150
DIMENSIONS AND MOUNTING
©MoTeCPublished1May2015 Checkforlatestversionatwww.motec.com 33

DATASHEET PART13150
M150 PINOUT
M150ConnectorA-34Way
MatingConnector:TycoSuperseal34PositionKeying2–MoTeC#65067
| Pin Designation | FullName | OEPin | Function | Description |
| --------------- | -------- | ----- | -------- | ----------- |
Number
| A01 AT5        | AnalogueTemperatureInput5 |     | 1kPulluptoSEN_5V_C |     |
| -------------- | ------------------------- | --- | ------------------ | --- |
| A02 AT6        | AnalogueTemperatureInput6 |     | 1kPulluptoSEN_5V_C |     |
| A03 AV15       | AnalogueVoltageInput15    |     |                    |     |
| A04 AV16       | AnalogueVoltageInput16    |     |                    |     |
| A05 AV17       | AnalogueVoltageInput17    |     |                    |     |
| A06 IGN_LS9    | LowSideIgnition9          |     |                    |     |
| A07 IGN_LS10   | LowSideIgnition10         |     |                    |     |
| A08 IGN_LS11   | LowSideIgnition11         |     |                    |     |
| A09 IGN_LS12   | LowSideIgnition12         |     |                    |     |
| A10 SEN_5V0_C1 | Sensor5.0VC               |     |                    |     |
| A11 LA_NB1     | LambdaNarrowInput1        |     |                    |     |
| A12 LA_NB2     | LambdaNarrowInput2        |     |                    |     |
| A13 KNOCK3     | KnockInput3               |     |                    |     |
| A14 KNOCK4     | KnockInput4               |     |                    |     |
| A15 DIG2       | DigitalInput2             |     |                    |     |
| A16 DIG3       | DigitalInput3             |     |                    |     |
| A17 DIG4       | DigitalInput4             |     |                    |     |
| A18 SEN_5V0_C2 | Sensor5.0VC               |     |                    |     |
| A19 SEN_5V0_B2 | Sensor5.0VB               |     |                    |     |
| A20 LIN        | LINBus                    |     |                    |     |
| A21 RS232_RX   | RS232Receive              |     |                    |     |
| A22 RS232_TX   | RS232Transmit             |     |                    |     |
| A23 DIG1       | DigitalInput1             |     |                    |     |
| A24 BAT_NEG3   | BatteryNegative           |     |                    |     |
| A25 BAT_NEG4   | BatteryNegative           |     |                    |     |
| A26 SEN_0V_C1  | Sensor0VC                 |     |                    |     |
| A27 SEN_0V_C2  | Sensor0VC                 |     |                    |     |
| A28 CAN3_HI    | CANBus3High               |     |                    |     |
| A29 CAN3_LO    | CANBus3Low                |     |                    |     |
| A30 CAN2_HI    | CANBus2High               |     |                    |     |
| A31 CAN2_LO    | CANBus2Low                |     |                    |     |
| A32 BAT_NEG5   | BatteryNegative           |     |                    |     |
| A33 SEN_0V_B1  | Sensor0VB                 |     |                    |     |
| A34 SEN_0V_A1  | Sensor0VA                 |     |                    |     |
©MoTeCPublished1May2015 Checkforlatestversionatwww.motec.com 44

DATASHEET PART13150
M150ConnectorB-26Way
MatingConnector:TycoSuperseal26PositionKeying3–MoTeC#65068
| Pin Designation | FullName | OEPin | Function | Description |
| --------------- | -------- | ----- | -------- | ----------- |
Number
| B01 OUT_HB9   | HalfBridgeOutput9       |     |     |     |
| ------------- | ----------------------- | --- | --- | --- |
| B02 OUT_HB10  | HalfBridgeOutput10      |     |     |     |
| B03 UDIG8     | UniversalDigitalInput8  |     |     |     |
| B04 UDIG9     | UniversalDigitalInput9  |     |     |     |
| B05 UDIG10    | UniversalDigitalInput10 |     |     |     |
| B06 UDIG11    | UniversalDigitalInput11 |     |     |     |
| B07 UDIG12    | UniversalDigitalInput12 |     |     |     |
| B08 INJ_LS5   | LowSideInjector5        |     |     |     |
| B09 INJ_LS3   | LowSideInjector3        |     |     |     |
| B10 AV9       | AnalogueVoltageInput9   |     |     |     |
| B11 AV10      | AnalogueVoltageInput10  |     |     |     |
| B12 AV11      | AnalogueVoltageInput11  |     |     |     |
| B13 BAT_POS   | BatteryPositive         |     |     |     |
| B14 INJ_LS6   | LowSideInjector6        |     |     |     |
| B15 INJ_LS4   | LowSideInjector4        |     |     |     |
| B16 AV12      | AnalogueVoltageInput12  |     |     |     |
| B17 AV13      | AnalogueVoltageInput13  |     |     |     |
| B18 AV14      | AnalogueVoltageInput14  |     |     |     |
| B19 BAT_POS   | BatteryPositive         |     |     |     |
| B20 OUT_HB7   | HalfBridgeOutput7       |     |     |     |
| B21 OUT_HB8   | HalfBridgeOutput8       |     |     |     |
| B22 INJ_PH9   | PeakHoldInjector9       |     |     |     |
| B23 INJ_PH10  | PeakHoldInjector10      |     |     |     |
| B24 INJ_PH11  | PeakHoldInjector11      |     |     |     |
| B25 INJ_PH12  | PeakHoldInjector12      |     |     |     |
| B26 SEN_5V0_A | Sensor5.0VA             |     |     |     |
©MoTeCPublished1May2015 Checkforlatestversionatwww.motec.com 55

DATASHEET PART13150
M150ConnectorC-34Way
MatingConnector:TycoSuperseal34PositionKeying1–MoTeC#65044
| Pin Designation | FullName | OEPin | Function | Description |
| --------------- | -------- | ----- | -------- | ----------- |
Number
| C01 OUT_HB2   | HalfBridgeOutput2     |     |     |     |
| ------------- | --------------------- | --- | --- | --- |
| C02 SEN_5V0_A | Sensor5.0VA           |     |     |     |
| C03 IGN_LS1   | LowSideIgnition1      |     |     |     |
| C04 IGN_LS2   | LowSideIgnition2      |     |     |     |
| C05 IGN_LS3   | LowSideIgnition3      |     |     |     |
| C06 IGN_LS4   | LowSideIgnition4      |     |     |     |
| C07 IGN_LS5   | LowSideIgnition5      |     |     |     |
| C08 IGN_LS6   | LowSideIgnition6      |     |     |     |
| C09 SEN_5V0_B | Sensor5.0VB           |     |     |     |
| C10 BAT_NEG1  | BatteryNegative       |     |     |     |
| C11 BAT_NEG2  | BatteryNegative       |     |     |     |
| C12 IGN_LS7   | LowSideIgnition7      |     |     |     |
| C13 IGN_LS8   | LowSideIgnition8      |     |     |     |
| C14 AV1       | AnalogueVoltageInput1 |     |     |     |
| C15 AV2       | AnalogueVoltageInput2 |     |     |     |
| C16 AV3       | AnalogueVoltageInput3 |     |     |     |
| C17 AV4       | AnalogueVoltageInput4 |     |     |     |
| C18 OUT_HB1   | HalfBridgeOutput1     |     |     |     |
| C19 INJ_PH1   | PeakHoldInjector1     |     |     |     |
| C20 INJ_PH2   | PeakHoldInjector2     |     |     |     |
| C21 INJ_PH3   | PeakHoldInjector3     |     |     |     |
| C22 INJ_PH4   | PeakHoldInjector4     |     |     |     |
| C23 INJ_LS1   | LowSideInjector1      |     |     |     |
| C24 INJ_LS2   | LowSideInjector2      |     |     |     |
| C25 AV5       | AnalogueVoltageInput5 |     |     |     |
| C26 BAT_POS   | BatteryPositive       |     |     |     |
| C27 INJ_PH5   | PeakHoldInjector5     |     |     |     |
| C28 INJ_PH6   | PeakHoldInjector6     |     |     |     |
| C29 INJ_PH7   | PeakHoldInjector7     |     |     |     |
| C30 INJ_PH8   | PeakHoldInjector8     |     |     |     |
| C31 OUT_HB3   | HalfBridgeOutput3     |     |     |     |
| C32 OUT_HB4   | HalfBridgeOutput4     |     |     |     |
| C33 OUT_HB5   | HalfBridgeOutput5     |     |     |     |
| C34 OUT_HB6   | HalfBridgeOutput6     |     |     |     |
©MoTeCPublished1May2015 Checkforlatestversionatwww.motec.com 66

DATASHEET PART13150
M150ConnectorD—26way
MatingConnector:TycoSuperseal26PositionKeying1–MoTeC#65045
| Pin Designation | FullName | OEPin | Function | Description |
| --------------- | -------- | ----- | -------- | ----------- |
Number
| D01 UDIG1    | UniversalDigitalInput1    |          |                    |     |
| ------------ | ------------------------- | -------- | ------------------ | --- |
| D02 UDIG2    | UniversalDigitalInput2    |          |                    |     |
| D03 AT1      | AnalogueTemperatureInput1 |          | 1kPulluptoSEN_5V_A |     |
| D04 AT2      | AnalogueTemperatureInput2 |          | 1kPulluptoSEN_5V_A |     |
| D05 AT3      | AnalogueTemperatureInput3 |          | 1kPulluptoSEN_5V_B |     |
| D06 AT4      | AnalogueTemperatureInput4 |          | 1kPulluptoSEN_5V_B |     |
| D07 KNOCK1   | KnockInput1               |          |                    |     |
| D08 UDIG3    | UniversalDigitalInput3    |          |                    |     |
| D09 UDIG4    | UniversalDigitalInput4    |          |                    |     |
| D10 UDIG5    | UniversalDigitalInput5    |          |                    |     |
| D11 UDIG6    | UniversalDigitalInput6    |          |                    |     |
| D12 BAT_BAK  | BatteryBackup             |          |                    |     |
| D13 KNOCK2   | KnockInput2               |          |                    |     |
| D14 UDIG7    | UniversalDigitalInput7    |          |                    |     |
| D15 SEN_0V_A | Sensor0VA                 |          |                    |     |
| D16 SEN_0V_B | Sensor0VB                 |          |                    |     |
| D17 CAN1_HI  | CANBus1High               |          |                    |     |
| D18 CAN1_LO  | CANBus1Low                |          |                    |     |
| D19 SEN_6V3  | Sensor6.3V                |          |                    |     |
| D20 AV6      | AnalogueVoltageInput6     |          |                    |     |
| D21 AV7      | AnalogueVoltageInput7     |          |                    |     |
| D22 AV8      | AnalogueVoltageInput8     |          |                    |     |
| D23 ETH_TX+  | EthernetTransmit+         | Ethernet |                    |     |
Green/White
| D24 ETH_TX- | EthernetTransmit- | EthernetGreen |     |     |
| ----------- | ----------------- | ------------- | --- | --- |
| D25 ETH_RX+ | EthernetReceive+  | Ethernet      |     |     |
Orange/White
| D26 ETH_RX- | EthernetReceive- | Ethernet |     |     |
| ----------- | ---------------- | -------- | --- | --- |
©MoTeCPublished1May2015 Checkforlatestversionatwww.motec.com 77
