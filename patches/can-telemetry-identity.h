// Generated from can-telemetry-profile.toml. Do not edit.
// Wire identity of the tuning profile. The configuration guards of
// can-telemetry-capture.s and can-telemetry-control.s compare the ROM
// configuration record with the integer symbols, and the executable
// harness installs TELEMETRY_CONFIGURATION, the enabled record of the
// candidate CAN ID and tick divisor.

#define TELEMETRY_PROFILE_ID 0x08
#define TELEMETRY_PAGE_COUNT 0x0B
#define TELEMETRY_PROFILE_CRC 0xBCAB
#define TELEMETRY_CONFIGURATION { 0x43, 0x54, 0x02, 0x01, 0x08, 0x0B, 0x01, 0x00, 0x06, 0xF0, 0xBC, 0xAB, 0x54, 0x45, 0x4C, 0x32 }
