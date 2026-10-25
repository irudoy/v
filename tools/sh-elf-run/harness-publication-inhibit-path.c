/* Complete raw cache/mode/snapshot state with one explicit external mode-bit update. */
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
struct path_case {
    uint32_t kind,entry,parent,pattern,flat,rpm,brake,fault,initial_mode,metadata,native_bit,variant,sr;
};
#include "publication-inhibit-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"independent lookup fifth argument ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[4],calibration_after[4],native_before[256],native_after[256];
static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;
    size_t index;
    for (index=0;index<size;++index)
        printf("%02x",(unsigned)data[index]);
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

static void calibrations(const struct path_case *input)
{
    static const uint8_t rising[4]={0U,1U,128U,255U};
    static const uint8_t falling[4]={255U,128U,1U,0U};
    volatile uint8_t *table=(volatile uint8_t *)(uintptr_t)0x1202eU;
    unsigned index;
    memcpy((void *)(uintptr_t)0x1202eU,publication_inhibit_stock_calibrations,4U);
    for (index=0;index<4U;++index) {
        if (input->pattern==1U) table[index]=(uint8_t)input->flat;
        else if (input->pattern==2U) table[index]=rising[index];
        else if (input->pattern==3U) table[index]=falling[index];
    }
}

static void calibration_snapshot(uint8_t *output)
{
    memcpy(output,(const void *)(uintptr_t)0x1202eU,4U);
}

static int observe(size_t index)
{
    const struct path_case *input=&publication_inhibit_cases[index];
    struct context context,initial;
    struct observation observation;
    volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    unsigned reg;
    if (input->kind==0U) {
        memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
        memset((void *)(uintptr_t)0xffff8400U,0,256U);
        unsigned address;
        uint32_t previous=input->rpm+64U;
        if (previous>65535U) previous=65535U;
        ram[0x2459U]=(uint8_t)input->initial_mode;
        ram[0x2451U]=(uint8_t)input->brake;
        ram[0x257aU]=173U;
        ram[0x4226U]=(uint8_t)input->metadata;
        ram[0x84c3U]=(uint8_t)input->native_bit;
        *(volatile uint8_t *)(uintptr_t)0xffff84c3U=(uint8_t)input->native_bit;
        ram[0x24b8U]=64U;
        ram[0x5718U+3U*0x14U+1U]=(uint8_t)(input->fault*128U);
        *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x114aU)=(uint16_t)input->rpm;
        *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1e58U)=0x1200U;
        for (address=0x1f6eU;address<0x1f78U;address+=2U)
            *(volatile uint16_t *)(uintptr_t)(RAM_BASE+address)=(uint16_t)previous;
        calibrations(input);
    } else if (input->kind==1U) {
        ram[0x2459U]|=32U;
    }
    for (reg=0;reg<15U;++reg)
        context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U+input->kind*0x01010101U;
    if (input->kind==2U) context.r[11]=0x22558U;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|input->rpm;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    calibration_snapshot(calibration_before);
    memcpy(native_before,(const void *)(uintptr_t)0xffff8400U,256U);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    calibration_snapshot(calibration_after);
    memcpy(native_after,(const void *)(uintptr_t)0xffff8400U,256U);
    if (memcmp(&initial,&context,sizeof(context))) {
        fprintf(stderr,"publication-inhibit[%lu]: const input context changes\n",(unsigned long)index);
        return 0;
    }
    printf("kb-publication-inhibit-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\""); hex(calibration_before,4U);
    printf("\",\"calibration_after\":\""); hex(calibration_after,4U);
    printf("\",\"native_before\":\""); hex(native_before,256U);
    printf("\",\"native_after\":\""); hex(native_after,256U);
    printf("\"}\n");
    return 1;
}

int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(publication_inhibit_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_PUBLICATION_INHIBIT status=PASS region=%s cases=%lu\n",
           PUBLICATION_INHIBIT_REGION,(unsigned long)ARRAY_SIZE(publication_inhibit_cases));
    return 0;
}
