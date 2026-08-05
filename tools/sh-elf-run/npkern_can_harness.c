#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cmd_parser.h"
#include "crc.h"
#include "eep_funcs.h"
#include "iso_cmds.h"
#include "isotp.h"
#include "npk_errcodes.h"

#ifndef EXPECT_READ_ONLY
#error EXPECT_READ_ONLY must be 0 or 1
#endif

#define ARRAY_SIZE(values) (sizeof(values) / sizeof((values)[0]))
#define FIXTURE_ADDRESS 0x00180000U
#define CAPTURE_MAX 64U
#define FRAME_MAX 64U

#define CHECK(condition) \
	do { \
		if (!(condition)) { \
			printf("NPKERN_HARNESS_FAIL line=%u\n", \
			       (unsigned)__LINE__); \
			return 1; \
		} \
	} while (0)

struct captured_pdu {
	u16 len;
	u8 data[256];
};

struct can_frame_fixture {
	u8 len;
	u8 data[8];
};

struct fake_bus {
	struct can_frame_fixture rx[FRAME_MAX];
	struct can_frame_fixture tx[FRAME_MAX];
	size_t rx_count;
	size_t rx_position;
	size_t tx_count;
	unsigned delays[FRAME_MAX];
	size_t delay_count;
	int fail_send;
};

static u8 fixture[1024]
	__attribute__((section(".npkern_fixture"), aligned(256)));
static struct captured_pdu captures[CAPTURE_MAX];
static size_t capture_count;
static unsigned transport_init_count;
static u8 transport_init_parameter;
static struct npk_msg queued_message;
static int queued_receive_result = -1;
static u32 eeprom_function;
static unsigned die_count;
static int flash_init_ok = 1;
static u8 flash_init_error = SID34_BADFCCS;
static unsigned flash_init_count;
static unsigned flash_unprotect_count;
static unsigned flash_erase_count;
static unsigned flash_write_count;
static unsigned flash_erase_block;
static u32 flash_write_destination;
static u32 flash_write_length;
static u8 flash_write_first;
static u8 flash_write_last;
static u32 flash_erase_result;
static u32 flash_write_result;

static void clear_captures(void)
{
	capture_count = 0U;
	memset(captures, 0, sizeof(captures));
}

void transport_init(u8 parameter)
{
	transport_init_count++;
	transport_init_parameter = parameter;
}

int transport_recv(struct npk_msg *message)
{
	if (!message || (queued_receive_result != 0)) {
		return -1;
	}
	*message = queued_message;
	queued_receive_result = -1;
	return 0;
}

int transport_send(const u8 *payload, u16 len)
{
	if (!payload || (len == 0U) || (len > sizeof(captures[0].data)) ||
	    (capture_count >= CAPTURE_MAX)) {
		return -1;
	}
	captures[capture_count].len = len;
	memcpy(captures[capture_count].data, payload, len);
	capture_count++;
	return 0;
}

int transport_supports_speed_change(void)
{
	return 0;
}

void transport_idle(unsigned milliseconds)
{
	(void)milliseconds;
}

void eep_read16(uint8_t address, uint16_t *destination)
{
	*destination = (uint16_t)(0xA500U | address);
}

void eep_setptr(uint32_t new_address)
{
	eeprom_function = new_address;
}

bool platf_flash_init(uint8_t *error)
{
	flash_init_count++;
	if (!flash_init_ok) {
		*error = flash_init_error;
		return false;
	}
	return true;
}

void platf_flash_unprotect(void)
{
	flash_unprotect_count++;
}

uint32_t platf_flash_eb(unsigned block_number)
{
	flash_erase_count++;
	flash_erase_block = block_number;
	return flash_erase_result;
}

uint32_t platf_flash_wb(uint32_t destination, uint32_t source, uint32_t len)
{
	const uint8_t *data = (const uint8_t *)(uintptr_t)source;
	flash_write_count++;
	flash_write_destination = destination;
	flash_write_length = len;
	flash_write_first = data[0];
	flash_write_last = data[len - 1U];
	return flash_write_result;
}

void die(void)
{
	die_count++;
}

static void process_bytes(const u8 *data, u16 len)
{
	struct npk_msg message;
	memset(&message, 0, sizeof(message));
	message.len = len;
	if (len <= sizeof(message.data)) {
		memcpy(message.data, data, len);
	}
	cmd_process(&message);
}

static int expect_response(const u8 *expected, u16 len)
{
	CHECK(capture_count == 1U);
	CHECK(captures[0].len == len);
	CHECK(memcmp(captures[0].data, expected, len) == 0);
	return 0;
}

static int expect_negative(u8 sid, u8 nrc)
{
	const u8 expected[] = {0x7FU, sid, nrc};
	return expect_response(expected, sizeof(expected));
}

static int start_ready_session(void)
{
	const u8 request[] = {SID_STARTCOMM};
	const u8 response[] = {0xC1U, 0x67U, 0x8FU};
	clear_captures();
	cmd_init(9U);
	CHECK(transport_init_parameter == 9U);
	process_bytes(request, sizeof(request));
	CHECK(expect_response(response, sizeof(response)) == 0);
	clear_captures();
	return 0;
}

static int test_command_parser(void)
{
	unsigned cases = 0U;
	u8 request[SIDFL_WB_DLEN + 6U];
	u8 expected[36];
	struct npk_msg invalid;
	unsigned index;

	CHECK((uintptr_t)fixture == FIXTURE_ADDRESS);
	for (index = 0U; index < sizeof(fixture); index++) {
		fixture[index] = (u8)(index ^ (index >> 3));
	}

	clear_captures();
	cmd_init(7U);
	process_bytes((const u8[]){SID_TP}, 1U);
	CHECK(capture_count == 0U);
	cases++;

	CHECK(start_ready_session() == 0);
	cases++;

	process_bytes((const u8[]){SID_RECUID}, 1U);
	CHECK(capture_count == 1U);
	CHECK(captures[0].len > 1U);
	CHECK(captures[0].data[0] == (SID_RECUID + 0x40U));
	clear_captures();
	cases++;

	process_bytes((const u8[]){SID_TP}, 1U);
	CHECK(expect_response((const u8[]){SID_TP + 0x40U}, 1U) == 0);
	clear_captures();
	process_bytes((const u8[]){0x99U}, 1U);
	CHECK(expect_negative(0x99U, ISO_NRC_SNS) == 0);
	clear_captures();
	cases++;

	process_bytes((const u8[]){SID_CONF, SID_CONF_SETSPEED, 4U}, 3U);
	CHECK(expect_negative(SID_CONF, ISO_NRC_SFNS_IF) == 0);
	CHECK(transport_init_count >= 2U);
	clear_captures();
	cases++;

	set_lasterr(0x5AU);
	process_bytes((const u8[]){SID_CONF, SID_CONF_LASTERR}, 2U);
	CHECK(expect_response((const u8[]){SID_CONF + 0x40U, 0x5AU}, 2U) == 0);
	clear_captures();
	process_bytes((const u8[]){SID_CONF, SID_CONF_LASTERR}, 2U);
	CHECK(expect_response((const u8[]){SID_CONF + 0x40U, 0U}, 2U) == 0);
	clear_captures();
	cases++;

	process_bytes(
		(const u8[]){SID_CONF, SID_CONF_SETEEPR, 0x12U, 0x34U, 0x56U},
		5U);
	CHECK(expect_response((const u8[]){SID_CONF + 0x40U}, 1U) == 0);
	CHECK(eeprom_function == 0x00123456U);
	clear_captures();
	cases++;

	request[0] = SID_RMBA;
	request[1] = 0x18U;
	request[2] = 0U;
	request[3] = 0U;
	request[4] = 3U;
	process_bytes(request, 5U);
	expected[0] = SID_RMBA + 0x40U;
	memcpy(expected + 1, fixture, 3U);
	expected[4] = 0x18U;
	expected[5] = 0U;
	expected[6] = 0U;
	CHECK(expect_response(expected, 7U) == 0);
	clear_captures();
	process_bytes((const u8[]){SID_RMBA, 0U, 0U, 0U, 0U}, 5U);
	CHECK(expect_negative(SID_RMBA, ISO_NRC_SFNS_IF) == 0);
	clear_captures();
	cases++;

	process_bytes((const u8[]){SID_WMBA, 0U, 0x10U, 0U, 1U, 0xA5U}, 6U);
	CHECK(expect_negative(SID_WMBA, ISO_NRC_CNDTSA) == 0);
	clear_captures();
	process_bytes(
		(const u8[]){SID_WMBA, 0xFFU, 0xBFU, 0xFFU, 2U, 0xA5U,
		             0x5AU},
		7U);
	CHECK(expect_negative(SID_WMBA, ISO_NRC_CNDTSA) == 0);
	clear_captures();
	cases++;

	process_bytes(
		(const u8[]){SID_DUMP, SID_DUMP_ROM, 0U, 1U, 0xC0U, 0U},
		6U);
	expected[0] = SID_DUMP + 0x40U;
	memcpy(expected + 1, fixture, 32U);
	CHECK(expect_response(expected, 33U) == 0);
	clear_captures();
	process_bytes((const u8[]){SID_DUMP, 2U, 0U, 1U, 0U, 0U}, 6U);
	CHECK(expect_negative(SID_DUMP, ISO_NRC_SFNS_IF) == 0);
	clear_captures();
	cases++;

	request[0] = SID_CONF;
	request[1] = SID_CONF_CKS1;
	request[2] = 0x18U;
	request[3] = 0U;
	for (index = 0U; index < ROMCRC_NUMCHUNKS; index++) {
		u16 value = crc16(fixture + index * ROMCRC_CHUNKSIZE,
		                  ROMCRC_CHUNKSIZE);
		request[4U + index * 2U] = (u8)(value >> 8);
		request[5U + index * 2U] = (u8)value;
	}
	process_bytes(request, 12U);
	CHECK(expect_response((const u8[]){SID_CONF + 0x40U}, 1U) == 0);
	clear_captures();
	request[5] ^= 1U;
	process_bytes(request, 12U);
	CHECK(expect_negative(SID_CONF, SID_CONF_CKS1_BADCKS) == 0);
	clear_captures();
	cases++;

	memset(&invalid, 0, sizeof(invalid));
	cmd_process(NULL);
	invalid.len = 257U;
	cmd_process(&invalid);
	CHECK(capture_count == 0U);
	cases++;

	queued_message.len = 1U;
	queued_message.data[0] = SID_STARTCOMM;
	queued_receive_result = 0;
	cmd_init(9U);
	CHECK(cmd_step() == 0);
	CHECK(capture_count == 1U);
	clear_captures();
	queued_receive_result = -1;
	CHECK(cmd_step() == -1);
	process_bytes((const u8[]){SID_TP}, 1U);
	CHECK(capture_count == 0U);
	CHECK(start_ready_session() == 0);
	cases++;

#if EXPECT_READ_ONLY
	process_bytes((const u8[]){SID_FLREQ}, 1U);
	CHECK(expect_negative(SID_FLREQ, ISO_NRC_SNS) == 0);
	clear_captures();
	process_bytes((const u8[]){SID_FLASH, SIDFL_EB, 0U}, 3U);
	CHECK(expect_negative(SID_FLASH, ISO_NRC_SNS) == 0);
	clear_captures();
	cases++;
#else
	process_bytes((const u8[]){SID_FLASH, SIDFL_EB, 0U}, 3U);
	CHECK(expect_negative(SID_FLASH, ISO_NRC_CNCORSE) == 0);
	clear_captures();
	flash_init_ok = 0;
	process_bytes((const u8[]){SID_FLREQ}, 1U);
	CHECK(expect_negative(SID_FLREQ, flash_init_error) == 0);
	clear_captures();
	flash_init_ok = 1;
	process_bytes((const u8[]){SID_FLREQ}, 1U);
	CHECK(expect_response((const u8[]){SID_FLREQ + 0x40U}, 1U) == 0);
	CHECK(flash_init_count == 2U);
	clear_captures();
	cases += 3U;

	process_bytes((const u8[]){SID_FLASH, SIDFL_UNPROTECT, 0U}, 3U);
	CHECK(expect_negative(SID_FLASH, ISO_NRC_IK) == 0);
	clear_captures();
	process_bytes(
		(const u8[]){SID_FLASH, SIDFL_UNPROTECT,
		             (u8)~SIDFL_UNPROTECT},
		3U);
	CHECK(expect_response((const u8[]){SID_FLASH + 0x40U}, 1U) == 0);
	CHECK(flash_unprotect_count == 1U);
	clear_captures();
	cases += 2U;

	process_bytes((const u8[]){SID_FLASH, SIDFL_EB, 7U}, 3U);
	CHECK(expect_response((const u8[]){SID_FLASH + 0x40U}, 1U) == 0);
	CHECK((flash_erase_count == 1U) && (flash_erase_block == 7U));
	clear_captures();
	flash_erase_result = PFEB_BADBLOCK;
	process_bytes((const u8[]){SID_FLASH, SIDFL_EB, 99U}, 3U);
	CHECK(expect_negative(SID_FLASH, PFEB_BADBLOCK) == 0);
	flash_erase_result = 0U;
	clear_captures();
	cases += 2U;

	request[0] = SID_FLASH;
	request[1] = SIDFL_WB;
	request[2] = 0x01U;
	request[3] = 0x20U;
	request[4] = 0U;
	for (index = 0U; index < SIDFL_WB_DLEN; index++) {
		request[5U + index] = (u8)(index ^ 0xA5U);
	}
	{
		u16 sum = 0U;
		for (index = 2U; index < 133U; index++) {
			sum += request[index];
			if (sum & 0x100U) {
				sum += 1U;
			}
			sum = (u8)sum;
		}
		request[133] = (u8)sum;
	}
	process_bytes(request, sizeof(request));
	CHECK(expect_response((const u8[]){SID_FLASH + 0x40U}, 1U) == 0);
	CHECK(flash_write_count == 1U);
	CHECK(flash_write_destination == 0x00012000U);
	CHECK(flash_write_length == SIDFL_WB_DLEN);
	CHECK((flash_write_first == 0xA5U) &&
	      (flash_write_last == (u8)(127U ^ 0xA5U)));
	clear_captures();
	request[133] ^= 1U;
	process_bytes(request, sizeof(request));
	CHECK(expect_negative(SID_FLASH, SID_CONF_CKS1_BADCKS) == 0);
	clear_captures();
	cases += 2U;
#endif

	process_bytes((const u8[]){SID_RESET}, 1U);
	CHECK(expect_response((const u8[]){SID_RESET + 0x40U}, 1U) == 0);
	CHECK(die_count == 1U);
	clear_captures();
	cases++;

	printf("NPKERN_PARSER status=PASS variant=%s cases=%u\n",
	       EXPECT_READ_ONLY ? "RO" : "RW", cases);
	return 0;
}

#if EXPECT_READ_ONLY
static int fake_send(void *user, const uint8_t *data, uint8_t len,
		     unsigned timeout_ms)
{
	struct fake_bus *bus = user;
	(void)timeout_ms;
	if (!bus || bus->fail_send || !data || (len > 8U) ||
	    (bus->tx_count >= FRAME_MAX)) {
		return -1;
	}
	bus->tx[bus->tx_count].len = len;
	memcpy(bus->tx[bus->tx_count].data, data, len);
	bus->tx_count++;
	return 0;
}

static int fake_recv(void *user, uint8_t *data, uint8_t *len,
		     unsigned timeout_ms)
{
	struct fake_bus *bus = user;
	struct can_frame_fixture *frame;
	(void)timeout_ms;
	if (!bus || !data || !len || (bus->rx_position >= bus->rx_count)) {
		return -1;
	}
	frame = &bus->rx[bus->rx_position++];
	if (frame->len > *len) {
		return -1;
	}
	*len = frame->len;
	memcpy(data, frame->data, frame->len);
	return 0;
}

static void fake_sleep(void *user, unsigned delay_us)
{
	struct fake_bus *bus = user;
	if (bus->delay_count < FRAME_MAX) {
		bus->delays[bus->delay_count++] = delay_us;
	}
}

static struct isotp_link fake_link(struct fake_bus *bus)
{
	struct isotp_link link;
	memset(&link, 0, sizeof(link));
	link.user = bus;
	link.send_frame = fake_send;
	link.recv_frame = fake_recv;
	link.sleep_us = fake_sleep;
	link.frame_timeout_ms = 50U;
	link.max_wait_frames = 2U;
	link.pad_frames = 1U;
	link.pad_byte = 0xAAU;
	return link;
}

static void queue_frame(struct fake_bus *bus, const u8 *data, u8 len)
{
	struct can_frame_fixture *frame = &bus->rx[bus->rx_count++];
	frame->len = len;
	memcpy(frame->data, data, len);
}

static int test_isotp(void)
{
	unsigned cases = 0U;
	u8 payload[128];
	u8 output[128];
	size_t length;
	unsigned index;

	CHECK(isotp_stmin_to_us(0x00U) == 0U);
	CHECK(isotp_stmin_to_us(0x7FU) == 127000U);
	CHECK(isotp_stmin_to_us(0xF1U) == 100U);
	CHECK(isotp_stmin_to_us(0xF9U) == 900U);
	CHECK(isotp_stmin_to_us(0x80U) == 127000U);
	CHECK(isotp_stmin_to_us(0xFAU) == 127000U);
	cases++;

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		CHECK(isotp_send(NULL, payload, 1U) == ISOTP_ERR_ARG);
		CHECK(isotp_send(&link, payload, 0U) == ISOTP_ERR_ARG);
		CHECK(isotp_send(&link, payload, ISOTP_MAX_PAYLOAD + 1U) ==
		      ISOTP_ERR_ARG);
		CHECK(isotp_recv(&link, output, sizeof(output), NULL) ==
		      ISOTP_ERR_ARG);
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		const u8 data[] = {0x22U, 0xF1U, 0x90U};
		CHECK(isotp_send(&link, data, sizeof(data)) == ISOTP_OK);
		CHECK((bus.tx_count == 1U) && (bus.tx[0].len == 8U));
		CHECK(bus.tx[0].data[0] == 3U);
		CHECK(memcmp(bus.tx[0].data + 1, data, sizeof(data)) == 0);
		CHECK(bus.tx[0].data[7] == 0xAAU);
		cases++;
	}

	for (index = 0U; index < sizeof(payload); index++) {
		payload[index] = (u8)index;
	}
	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus, (const u8[]){0x31U, 0U, 0U}, 3U);
		queue_frame(&bus, (const u8[]){0x30U, 2U, 0xF1U}, 3U);
		queue_frame(&bus, (const u8[]){0x30U, 0U, 0U}, 3U);
		CHECK(isotp_send(&link, payload, 27U) == ISOTP_OK);
		CHECK(bus.tx_count == 4U);
		CHECK((bus.tx[1].data[0] == 0x21U) &&
		      (bus.tx[2].data[0] == 0x22U) &&
		      (bus.tx[3].data[0] == 0x23U));
		CHECK((bus.delay_count == 2U) && (bus.delays[0] == 100U));
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus, (const u8[]){0x31U, 0U, 0U}, 3U);
		queue_frame(&bus, (const u8[]){0x31U, 0U, 0U}, 3U);
		queue_frame(&bus, (const u8[]){0x31U, 0U, 0U}, 3U);
		CHECK(isotp_send(&link, payload, 8U) == ISOTP_ERR_WAIT);
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus, (const u8[]){0x32U, 0U, 0U}, 3U);
		CHECK(isotp_send(&link, payload, 8U) == ISOTP_ERR_OVERFLOW);
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus, (const u8[]){0x20U, 0U, 0U}, 3U);
		CHECK(isotp_send(&link, payload, 8U) == ISOTP_ERR_PROTOCOL);
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		CHECK(isotp_send(&link, payload, 8U) == ISOTP_ERR_TIMEOUT);
		bus.fail_send = 1;
		CHECK(isotp_send(&link, payload, 1U) == ISOTP_ERR_IO);
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus, (const u8[]){3U, 0x62U, 1U, 2U}, 4U);
		length = 0U;
		CHECK(isotp_recv(&link, output, sizeof(output), &length) == ISOTP_OK);
		CHECK((length == 3U) && (output[0] == 0x62U) &&
		      (output[2] == 2U));
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus, (const u8[]){0U}, 0U);
		length = 0U;
		CHECK(isotp_recv(&link, output, sizeof(output), &length) ==
		      ISOTP_ERR_PROTOCOL);
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus, (const u8[]){8U, 1U, 2U, 3U, 4U, 5U, 6U, 7U},
		            8U);
		length = 0U;
		CHECK(isotp_recv(&link, output, sizeof(output), &length) ==
		      ISOTP_ERR_PROTOCOL);
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus,
		            (const u8[]){0x10U, 20U, 0U, 1U, 2U, 3U, 4U, 5U},
		            8U);
		queue_frame(&bus,
		            (const u8[]){0x21U, 6U, 7U, 8U, 9U, 10U, 11U, 12U},
		            8U);
		queue_frame(&bus,
		            (const u8[]){0x22U, 13U, 14U, 15U, 16U, 17U, 18U,
		                         19U},
		            8U);
		length = 0U;
		CHECK(isotp_recv(&link, output, sizeof(output), &length) == ISOTP_OK);
		CHECK((length == 20U) && (memcmp(output, payload, 20U) == 0));
		CHECK((bus.tx_count == 1U) && (bus.tx[0].data[0] == 0x30U));
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		link.rx_block_size = 1U;
		queue_frame(&bus,
		            (const u8[]){0x10U, 20U, 0U, 1U, 2U, 3U, 4U, 5U},
		            8U);
		queue_frame(&bus,
		            (const u8[]){0x21U, 6U, 7U, 8U, 9U, 10U, 11U, 12U},
		            8U);
		queue_frame(&bus,
		            (const u8[]){0x22U, 13U, 14U, 15U, 16U, 17U, 18U,
		                         19U},
		            8U);
		length = 0U;
		CHECK(isotp_recv(&link, output, sizeof(output), &length) == ISOTP_OK);
		CHECK((length == 20U) && (bus.tx_count == 2U));
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus,
		            (const u8[]){0x10U, 10U, 0U, 1U, 2U, 3U, 4U, 5U},
		            8U);
		queue_frame(&bus, (const u8[]){0x22U, 6U, 7U, 8U, 9U}, 5U);
		length = 0U;
		CHECK(isotp_recv(&link, output, sizeof(output), &length) ==
		      ISOTP_ERR_SEQUENCE);
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		queue_frame(&bus,
		            (const u8[]){0x10U, 20U, 0U, 1U, 2U, 3U, 4U, 5U},
		            8U);
		length = 0U;
		CHECK(isotp_recv(&link, output, 8U, &length) == ISOTP_ERR_OVERFLOW);
		CHECK((bus.tx_count == 1U) && (bus.tx[0].data[0] == 0x32U));
		cases++;
	}

	{
		struct fake_bus bus = {0};
		struct isotp_link link = fake_link(&bus);
		length = 0U;
		CHECK(isotp_recv(&link, output, sizeof(output), &length) ==
		      ISOTP_ERR_TIMEOUT);
		queue_frame(&bus,
		            (const u8[]){0x10U, 7U, 0U, 1U, 2U, 3U, 4U, 5U},
		            8U);
		CHECK(isotp_recv(&link, output, sizeof(output), &length) ==
		      ISOTP_ERR_PROTOCOL);
		cases++;
	}

	printf("NPKERN_ISOTP status=PASS cases=%u\n", cases);
	return 0;
}
#endif

int main(void)
{
	if (test_command_parser() != 0) {
		return 1;
	}
#if EXPECT_READ_ONLY
	if (test_isotp() != 0) {
		return 1;
	}
#endif
	printf("NPKERN_CAN_HARNESS status=PASS variant=%s\n",
	       EXPECT_READ_ONLY ? "RO" : "RW");
	return 0;
}
