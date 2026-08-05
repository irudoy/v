#include <stdint.h>
#include <stdio.h>

#include "stypes.h"
#include "npk_errcodes.h"
#include "platf.h"

#ifndef EXPECT_FLASH_MAX
#error EXPECT_FLASH_MAX is required
#endif

#define CHECK(condition) \
	do { \
		if (!(condition)) { \
			printf("NPKERN_FLASH_GUARD_FAIL line=%u\n", \
			       (unsigned)__LINE__); \
			return 1; \
		} \
	} while (0)

int main(void)
{
	CHECK(platf_flash_wb(EXPECT_FLASH_MAX + 1U, 0U, 128U) == PFWB_OOB);
	CHECK(platf_flash_wb(EXPECT_FLASH_MAX - 127U, 0U, 256U) == PFWB_OOB);
	CHECK(platf_flash_wb(1U, 0U, 128U) == PFWB_MISALIGNED);
	CHECK(platf_flash_wb(0U, 0U, 127U) == PFWB_LEN);
	CHECK(platf_flash_wb(0U, 0U, 0U) == PFWB_LEN);
	printf("NPKERN_FLASH_GUARD status=PASS max=%#x cases=5\n",
	       (unsigned)EXPECT_FLASH_MAX);
	return 0;
}
