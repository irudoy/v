# Communication Protocols

> Зеркало страницы NissanECU RE wiki. Источник: https://nissanecu.miraheze.org/wiki/Communication_Protocols
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

## KWP2000

Notes:  
\- Everything posted here is based on a USDM 2006 Nissan 350z 5AT. This entire page will be dedicated to Nissan 350Z communication protocol analysis. While I doubt that anything here will be incorrect, there's always a chance that something might be different across vehicles. \- It would appear that all modules communicate with a tester address of 0xFC  
\- Do NOT attempt to send these commands yourself. These SIDs are only listed here for reference when programming applications that will communicate with the ECU.   
\- The KWP2000 Full SID Tree is a GENERAL TREE! So not every listed SID will be supported by one of the following modules.  


Following Modules Communicate via KWP2000;  
**_ECU - Destination Address_**   


  * ECU - 0x10
  * TCM - 0x18
  * ABS - 0x28
  * SRS - 0x58



0xFE as destaddr might communicate with all nodes.  


### _Full SIDs Tree_

  * **$09** \- Request Vehicle Information
  * **$10** \- Diagnostic Session Control
  * **$11** \- Request ECU Reset
  * **$12** \- Read Freeze Frame Data
  * **$13** \- Read DTCs
  * **$14** \- Clear DTC Information
  * **$17** \- Read Status of DTCs
  * **$18** \- Read DTCs by Status
  * **$1A** \- Request ECU ID
  * **$20** \- Stop Diagnostic Session
  * **$21** \- Read Data by LID
  * **$22** \- Read Data by CID
  * **$23** \- Read Memory by Address
  * **$26** \- Set Data Rates
  * **$27** \- Security Access
  * **$2C** \- Dynamically Define Data
  * **$2E** \- Write Data by CID
  * **$2F** \- I/O Control by CID
  * **$30** \- I/O Control by LID
  * **$31** \- Start Routine by LID
  * **$32** \- Stop Routing by LID
  * **$33** \- Request Routine Results by LID
  * **$34** \- Request Download
  * **$35** \- Request Upload
  * **$36** \- Transfer Data
  * **$37** \- Request Transfer Exit
  * **$38** \- Start Routine by Address
  * **$39** \- Stop Routine by Address
  * **$3A** \- Request Routine Results by Address
  * **$3B** \- Write Data by LID
  * **$3D** \- Write Memory by Address
  * **$3E** \- Tester is Present
  * **$81** \- Start Communication
  * **$82** \- Stop Communication
  * **$83** \- Access Timing Parameters



  


#### _Universal SID Functionality_

All SIDs found in this section function identically across all control modules. The individual sections found in each respective control module will describe anything that's specific to that control module.   


Notes:  
\- Everything posted here is based on a USDM 2006 Nissan 350z 5AT. This entire page will be dedicated to Nissan 350Z communication protocol analysis. While I doubt that anything here will be incorrect, there's always a chance that something might be different across vehicles. \- It would appear that all modules communicate with a tester address of 0xFC  
\- Do NOT attempt to send these commands yourself. These SIDs are only listed here for reference when programming applications that will communicate with the ECU.   
\- The KWP2000 Full SID Tree is a GENERAL TREE! So not every listed SID will be supported by one of the following modules.  


Abbreviations;  


  * **TID** \- Tester ID
  * **DA** \- Destination Address
  * **LID** \- Local ID
  * **CID** \- Common ID
  * **TXM** \- Transmission Mode [0x04 = Fast (Single Response) 0x06 = Slow (Continuous Response)]
  * **NRS** \- Number of Responses (Typically 0x01)
  * **A0 A1 A2 A3** \- Full Memory Address Formatting. Ex: FF FF 00 01
  * **NDTCS** \- Number of DTC's Set
  * **DTCH** \- DTC High Byte. For P0605, it would be 06
  * **DTCL** \- DTC Low Byte. For P0605, it would be 05
  * **DLID** \- Dynamic LID (Created by $AC)



  
**_$09 - Request Vehicle Information_**  


  * **$09  ?** -



**_$10 - Diagnostic Session Control_**

  * **$10 DiagnosticSession**



  
**_$11 - ECU Reset_**  


  * **$11 OptionByte**



  
**_$12 - Read Freeze Frame Data_**  


  * **$12 01 01 DLID** \- Read Freeze Frame Data by Dynamic LID



  
**_$14 - Clear DTCs_**  


  * **$14** \- Clear all Temporary and Permanent DTCs



**_$1A - Request ECU ID_**  


  * **$1A OptionByte**



**_$20 - Stop Diagnostic Session_**  


  
**_$21 - Read Data by LID_**  


  
**_$22 - Read Data by CID_**  


**_$30 - I/O Control by LID_**  


  
**_$3E - Tester is Present_**  


  
**_$81 - Start Communication_**  


  
**_$82 - Stop Communication_**  


  
**_$83 - Access Timing Parameters_**  


* * *

### _Engine Control Unit (ECU)_

#### _SID Tree_

  * **$09** \- Request Vehicle Information
  * **$10** \- Diagnostic Session Control
  * **$11** \- Request ECU Reset
  * **$12** \- Read Freeze Frame Data
  * **$13** \- Read DTCs
  * **$14** \- Clear DTC Information
  * **$17** \- Read Status of DTCs
  * **$18** \- Read DTCs by Status
  * **$1A** \- Request ECU ID
  * **$20** \- Stop Diagnostic Session
  * **$21** \- Read Data by LID
  * **$22** \- Read Data by CID
  * **$23** \- Read Memory by Address
  * **$26** \- Set Data Rates
  * **$27** \- Security Access
  * **$2C** \- Dynamically Define Data
  * **$2E** \- Write Data by CID
  * **$2F** \- I/O Control by CID
  * **$30** \- I/O Control by LID
  * **$31** \- Start Routine by LID
  * **$32** \- Stop Routing by LID
  * **$33** \- Request Routine Results by LID
  * **$34** \- Request Download
  * **$35** \- Request Upload
  * **$36** \- Transfer Data
  * **$37** \- Request Transfer Exit
  * **$38** \- Start Routine by Address
  * **$39** \- Stop Routine by Address
  * **$3A** \- Request Routine Results by Address
  * **$3B** \- Write Data by LID
  * **$3D** \- Write Memory by Address
  * **$3E** \- Tester is Present
  * **$80** \- "Escape Code (Not Part of DSS; KWP2000 Only)"
  * **$81** \- Start Communication
  * **$82** \- Stop Communication
  * **$83** \- Access Timing Parameters



Notes:  
\- Everything posted here is based on a USDM 2006 Nissan 350z 5AT. This entire page will be dedicated to Nissan 350Z communication protocol analysis. While I doubt that anything here will be incorrect, there's always a chance that something might be different across vehicles. \- It would appear that all modules communicate with a tester address of 0xFC  
\- Do NOT attempt to send these commands yourself. These SIDs are only listed here for reference when programming applications that will communicate with the ECU.   
\- The KWP2000 Full SID Tree is a GENERAL TREE! So not every listed SID will be supported by one of the following modules.  


##### _SID Analysis_

**_$09 - Request Vehicle Information_**  


  * **$09  ?** -



**_$10 - Diagnostic Session Control_**

  * **$10 DiagnosticSession**



  
**_$11 - ECU Reset_**  


  * **$11 OptionByte**



  
**_$12 - Read Freeze Frame Data_**  


  * **$12 01 01 DLID** \- Read Freeze Frame Data by Dynamic LID



  
**_$14 - Clear DTCs_**  


  * **$14** \- Clear all Temporary and Permanent DTCs



**_$1A - Request ECU ID_**  


  * **$1A OptionByte**



**_$20 - Stop Diagnostic Session_**  


  
**_$21 - Read Data by LID_**  


  
**_$22 - Read Data by CID_**  


**_$30 - I/O Control by LID_**  


  
**_$3E - Tester is Present_**  


  
**_$81 - Start Communication_**  


  
**_$82 - Stop Communication_**  


  
**_$83 - Access Timing Parameters_**  


**_$09 - Request Vehicle Information_**  


  * **$09 OptionByte**



  
**_$11 - ECU Reset_**  


  * **$11 80** \- Backup RAM Reset



  
**_$12 - Read Freeze Frame Data_**  


  * **$12 01 01 DLID** \- Read Freeze Frame Data by Dynamic LID



  
**_$14 - Clear DTCs_**  
\- Sets vHOSCMAX = mHOSCINT and vHOSCMAX_R#2 = mHOSCINT2  


  
**_$1A - Request ECU ID_**  


**_$27 - Security Access_**  


**_$30 - I/O Control by LID_**  


  
**_$31|$32|$33 - Request Routine Control by LID_**  


  
**_$3B - Write Data by LID_**  


Notes:  
\- Everything posted here is based on a USDM 2006 Nissan 350z 5AT. This entire page will be dedicated to Nissan 350Z communication protocol analysis. While I doubt that anything here will be incorrect, there's always a chance that something might be different across vehicles. \- It would appear that all modules communicate with a tester address of 0xFC  
\- Do NOT attempt to send these commands yourself. These SIDs are only listed here for reference when programming applications that will communicate with the ECU.   
\- The KWP2000 Full SID Tree is a GENERAL TREE! So not every listed SID will be supported by one of the following modules.  


* * *

### _Anti-Lock Brake System Control Module (ABS)_

Notes:  
\- Everything posted here is based on a USDM 2006 Nissan 350z 5AT. This entire page will be dedicated to Nissan 350Z communication protocol analysis. While I doubt that anything here will be incorrect, there's always a chance that something might be different across vehicles. \- It would appear that all modules communicate with a tester address of 0xFC  
\- Do NOT attempt to send these commands yourself. These SIDs are only listed here for reference when programming applications that will communicate with the ECU.   
\- The KWP2000 Full SID Tree is a GENERAL TREE! So not every listed SID will be supported by one of the following modules.  


#### _SID Tree_

  * **$09** \- Request Vehicle Information
  * **$10** \- Diagnostic Session Control
  * **$11** \- Request ECU Reset
  * **$12** \- Read Freeze Frame Data
  * **$13** \- Read DTCs
  * **$14** \- Clear DTC Information
  * **$17** \- Read Status of DTCs
  * **$18** \- Read DTCs by Status
  * **$1A** \- Request ECU ID
  * **$20** \- Stop Diagnostic Session
  * **$21** \- Read Data by LID
  * **$22** \- Read Data by CID
  * **$23** \- Read Memory by Address
  * **$26** \- Set Data Rates
  * **$27** \- Security Access
  * **$2C** \- Dynamically Define Data
  * **$2E** \- Write Data by CID
  * **$2F** \- I/O Control by CID
  * **$30** \- I/O Control by LID
  * **$31** \- Start Routine by LID
  * **$32** \- Stop Routing by LID
  * **$33** \- Request Routine Results by LID
  * **$34** \- Request Download
  * **$35** \- Request Upload
  * **$36** \- Transfer Data
  * **$37** \- Request Transfer Exit
  * **$38** \- Start Routine by Address
  * **$39** \- Stop Routine by Address
  * **$3A** \- Request Routine Results by Address
  * **$3B** \- Write Data by LID
  * **$3D** \- Write Memory by Address
  * **$3E** \- Tester is Present
  * **$81** \- Start Communication
  * **$82** \- Stop Communication
  * **$83** \- Access Timing Parameters



  


##### SID Analysis

**_$09 - Request Vehicle Information_**  


  * **$09  ?** -



**_$10 - Diagnostic Session Control_**

  * **$10 DiagnosticSession**



  
**_$11 - ECU Reset_**  


  * **$11 OptionByte**



  
**_$12 - Read Freeze Frame Data_**  


  * **$12 01 01 DLID** \- Read Freeze Frame Data by Dynamic LID



  
**_$14 - Clear DTCs_**  


  * **$14** \- Clear all Temporary and Permanent DTCs



**_$1A - Request ECU ID_**  


  * **$1A OptionByte**



**_$20 - Stop Diagnostic Session_**  


  
**_$21 - Read Data by LID_**  


  
**_$22 - Read Data by CID_**  


**_$30 - I/O Control by LID_**  


  
**_$3E - Tester is Present_**  


  
**_$81 - Start Communication_**  


  
**_$82 - Stop Communication_**  


  
**_$83 - Access Timing Parameters_**  


**_$1A - Request ECU ID_**  


**_$21 - Read Data by LID_**  
Supported Supmasks:  


  
**_$22 - Read Data by CID_**  


  
**_$30 - I/O Control by LID_**  


**_$A4 - Read Memory by Address_**  


**_$AC - Create Dynamic LIDs_**  


  


* * *

### _Safety Restraint System (SRS)_

Notes:  
\- Everything posted here is based on a USDM 2006 Nissan 350z 5AT. This entire page will be dedicated to Nissan 350Z communication protocol analysis. While I doubt that anything here will be incorrect, there's always a chance that something might be different across vehicles. \- It would appear that all modules communicate with a tester address of 0xFC  
\- Do NOT attempt to send these commands yourself. These SIDs are only listed here for reference when programming applications that will communicate with the ECU.   
\- The KWP2000 Full SID Tree is a GENERAL TREE! So not every listed SID will be supported by one of the following modules.  


#### _SID Tree_

  * **$09** \- Request Vehicle Information
  * **$10** \- Diagnostic Session Control
  * **$11** \- Request ECU Reset
  * **$12** \- Read Freeze Frame Data
  * **$13** \- Read DTCs
  * **$14** \- Clear DTC Information
  * **$17** \- Read Status of DTCs
  * **$18** \- Read DTCs by Status
  * **$1A** \- Request ECU ID
  * **$20** \- Stop Diagnostic Session
  * **$21** \- Read Data by LID
  * **$22** \- Read Data by CID
  * **$23** \- Read Memory by Address
  * **$26** \- Set Data Rates
  * **$27** \- Security Access
  * **$2C** \- Dynamically Define Data
  * **$2E** \- Write Data by CID
  * **$2F** \- I/O Control by CID
  * **$30** \- I/O Control by LID
  * **$31** \- Start Routine by LID
  * **$32** \- Stop Routing by LID
  * **$33** \- Request Routine Results by LID
  * **$34** \- Request Download
  * **$35** \- Request Upload
  * **$36** \- Transfer Data
  * **$37** \- Request Transfer Exit
  * **$38** \- Start Routine by Address
  * **$39** \- Stop Routine by Address
  * **$3A** \- Request Routine Results by Address
  * **$3B** \- Write Data by LID
  * **$3D** \- Write Memory by Address
  * **$3E** \- Tester is Present
  * **$81** \- Start Communication
  * **$82** \- Stop Communication
  * **$83** \- Access Timing Parameters



  


##### _SID Analysis_

Abbreviations;  


  * **TID** \- Tester ID
  * **DA** \- Destination Address
  * **LID** \- Local ID
  * **CID** \- Common ID
  * **CIDH** \- CID High Byte (12 for CID 1200)
  * **CIDL** \- CID Low Byte (00 for CID 1200)



**_$09 - Request Vehicle Information_**  


  * **$09  ?** -



**_$10 - Diagnostic Session Control_**

  * **$10 DiagnosticSession**



  
**_$11 - ECU Reset_**  


  * **$11 OptionByte**



  
**_$12 - Read Freeze Frame Data_**  


  * **$12 01 01 DLID** \- Read Freeze Frame Data by Dynamic LID



  
**_$14 - Clear DTCs_**  


  * **$14** \- Clear all Temporary and Permanent DTCs



**_$1A - Request ECU ID_**  


  * **$1A OptionByte**



**_$20 - Stop Diagnostic Session_**  


  
**_$21 - Read Data by LID_**  


  
**_$22 - Read Data by CID_**  


**_$30 - I/O Control by LID_**  


  
**_$3E - Tester is Present_**  


  
**_$81 - Start Communication_**  


  
**_$82 - Stop Communication_**  


  
**_$83 - Access Timing Parameters_**  


**_$14 - Clear DTCs_**  


  * **$14** \- Clear all Temporary and Permanent DTCs



Notes:  
\- Cannot clear recorded faults (According to NDS2)  


  
**_$1A_**  


  
**_$22 - Read Data by CID_**  


  


**_$A2 - Read DTCs_**
