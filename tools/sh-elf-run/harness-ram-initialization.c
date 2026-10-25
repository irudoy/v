/* Complete raw observations for explicit bounded stock memory windows. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(value) (sizeof(value)/sizeof((value)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr,fifth; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
struct path_case { uint32_t entry,seed; struct context context; };
struct word_range { uint32_t offset,count; };
#include "ram-initialization-cases.h"
#if !defined(RAM_INITIALIZATION_PREFIX) || !defined(RAM_INITIALIZATION_MARKER) || !defined(RAM_INITIALIZATION_WORD_SEED)
#error "the bounded memory source defines its exact stream identity and input pattern"
#endif
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete explicit input ABI");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"prepared SR offset");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t pools_before[4U*ARRAY_SIZE(ram_initialization_pools)];

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;
    size_t index;
    for (index=0;index<size;++index) printf("%02x",(unsigned)data[index]);
}

static void rle(const uint8_t *bytes,size_t size)
{
    size_t start=0;
    while (start<size) {
        size_t end=start+1U;
        while (end<size && bytes[end]==bytes[start]) ++end;
        printf("%s%lu:%02x",start ? "," : "",(unsigned long)(end-start),(unsigned)bytes[start]);
        start=end;
    }
}

static void pools_snapshot(uint8_t *data)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(ram_initialization_pools);++index)
        memcpy(data+4U*index,(const void *)(uintptr_t)ram_initialization_pools[index],4U);
}

int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(ram_initialization_cases);++index) {
        const struct path_case *input=&ram_initialization_cases[index];
        struct context context=input->context;
        struct observation observation;
        uint8_t pools_after[4U*ARRAY_SIZE(ram_initialization_pools)];
        uint8_t *ram=(uint8_t *)(uintptr_t)RAM_BASE;
        memset(ram,(int)input->seed,RAM_SIZE);
#if RAM_INITIALIZATION_WORD_SEED
        {
            size_t range_index,element;
            for (range_index=0;range_index<ARRAY_SIZE(ram_initialization_word_ranges);++range_index) {
                const struct word_range *range=&ram_initialization_word_ranges[range_index];
                for (element=0;element<range->count;++element) {
                    ram[range->offset+2U*element]=(uint8_t)(input->seed >> 8);
                    ram[range->offset+2U*element+1U]=(uint8_t)input->seed;
                }
            }
        }
#endif
#ifdef RAM_INITIALIZATION_BYTE_INPUTS
        {
            const struct byte_input *byte;
            if (ARRAY_SIZE(ram_initialization_byte_inputs)!=ARRAY_SIZE(ram_initialization_cases)) return 1;
            byte=&ram_initialization_byte_inputs[index];
            if (byte->enabled) {
                if (byte->enabled!=1U || byte->offset>=RAM_SIZE || byte->value>255U) return 1;
                ram[byte->offset]=(uint8_t)byte->value;
            }
        }
#endif
        memcpy(ram_before,ram,RAM_SIZE);
        pools_snapshot(pools_before);
        stock_invoke_ignition_consumer(input->entry,&context,&observation);
        pools_snapshot(pools_after);
        printf(RAM_INITIALIZATION_PREFIX "{\"schema\":1,\"index\":%lu,\"kind\":0,\"entry\":%lu,\"context\":\"",
               (unsigned long)index,(unsigned long)input->entry);
        hex(&input->context,sizeof(input->context));
        printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&observation,sizeof(observation));
        printf("\",\"ram_before\":\"");rle(ram_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle(ram,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(pools_before,sizeof(pools_before));
        printf("\",\"calibration_after\":\"");hex(pools_after,sizeof(pools_after));
        printf("\"}\n");
    }
    printf(RAM_INITIALIZATION_MARKER " status=PASS region=%s cases=%lu\n",
           RAM_INITIALIZATION_REGION,(unsigned long)ARRAY_SIZE(ram_initialization_cases));
    return 0;
}
