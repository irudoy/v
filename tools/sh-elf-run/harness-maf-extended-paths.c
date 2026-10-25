/* Natural MAF processing and publication inputs with complete state observations. */
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
    uint32_t kind,entry,argument,input,previous,correction,initialized,multiplier,bias;
    uint32_t mode,coefficient,reference,delta,magnitude,positive,enable;
    uint32_t diagnostic,inhibit,latch,fallback,weight,variant,sr;
};
#include "maf-extended-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
_Static_assert(sizeof(maf_extended_stock_calibrations)==13U,"complete declared MAF calibration bytes");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[sizeof(maf_extended_stock_calibrations)];
static const uint32_t calibration_starts[]={0x82b6U,0x82bdU,0x87f8U,0x8ac3U,0x92beU,0x9586U,0x958cU};
static const uint32_t calibration_sizes[]={3U,1U,2U,1U,2U,2U,2U};

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer; size_t index;
    for (index=0;index<size;++index) printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t start=0;
    while (start<size) {
        size_t end=start+1U;
        while (end<size && data[end]==data[start]) ++end;
        printf("%s%lu:%02x",start ? "," : "",(unsigned long)(end-start),(unsigned)data[start]);
        start=end;
    }
}
static void put_word(uint32_t offset,uint32_t value)
{ *(volatile uint16_t *)(uintptr_t)(RAM_BASE+offset)=(uint16_t)value; }
static void put_long(uint32_t offset,uint32_t value)
{ *(volatile uint32_t *)(uintptr_t)(RAM_BASE+offset)=value; }
static void put_byte(uint32_t offset,uint32_t value)
{ *(volatile uint8_t *)(uintptr_t)(RAM_BASE+offset)=(uint8_t)value; }
static void snapshot_calibrations(void)
{
    unsigned index,offset=0;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)calibration_starts[index],calibration_sizes[index]);
        offset+=calibration_sizes[index];
    }
}
static void print_calibrations(void)
{
    unsigned index;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index)
        hex((const void *)(uintptr_t)calibration_starts[index],calibration_sizes[index]);
}
static int prepare(const struct path_case *input)
{
    uint32_t bank=input->argument&255U,index,offset=0;
    if (bank>1U || input->kind>7U) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    for (index=0;index<2U;++index) {
        uint32_t selected=index==bank;
        uint32_t comp=selected && input->kind==0U;
        uint32_t contribution=selected && input->kind==1U;
        uint32_t scale=selected && input->kind==2U;
        uint32_t publication=selected && input->kind==3U;
        uint32_t diagnostic_copy=selected && input->kind==4U;
        put_word(0x101cU+index*2U,comp ? input->input : 0x2a39U);
        put_word(0x1e48U+index*2U,comp ? input->previous : 0xbeefU);
        put_long(0x3998U+index*4U,comp ? input->correction : 0x10203040U);
        put_word(0x1df0U+index*2U,contribution ? input->input : 0x1234U);
        put_long(0x1df8U+index*4U,publication ? input->input : 0xaabbccddU);
        put_word(0x1e00U+index*2U,0x2345U);
        put_word(0x1e08U+index*2U,contribution ? input->reference : 0x3456U);
        put_long(0x1e10U+index*4U,contribution ? input->fallback : 0x00123456U);
        put_word(0x1e18U+index*2U,contribution ? input->delta : 0x4567U);
        put_word(0x1e1cU+index*2U,contribution ? input->correction : 0xfedcU);
        put_word(0x1e30U+index*2U,contribution ? input->magnitude : 0x5678U);
        put_byte(0x43caU+index,contribution ? input->latch : 0x5aU);
        put_word(0x1d62U+index*2U,(scale || diagnostic_copy) ? input->input : 0x0369U);
        put_long(0x104cU+index*4U,0x12345678U);
        put_word(0x1a3eU+index*2U,0xd2c3U);
    }
    put_word(0x1e2aU,input->kind==3U ? input->correction : 0x1357U);
    put_word(0x2368U,input->kind==3U ? input->reference : 0x2468U);
    put_byte(0x3976U,0x80U | (bank==0U ? 2U : 1U)
        | ((input->kind==0U && input->initialized) ? bank+1U : 0U));
    if (input->kind==5U) {
        put_byte(0x3976U,0x80U | input->initialized);
        for (index=0;index<2U;++index) {
            put_word(0x101cU+index*2U,index ? input->previous : input->input);
            put_word(0x1e48U+index*2U,input->reference);
            put_long(0x3998U+index*4U,input->correction);
        }
    }
    if (input->kind==6U) {
        put_word(0x1d62U,input->input);
        put_word(0x1d64U,input->previous);
    }
    if (input->kind==7U) put_word(0x1d6eU,input->input);
    put_byte(0x2449U,input->kind==1U ? input->diagnostic : 0U);
    put_byte(0x24b8U,input->kind==1U ? input->inhibit : 0U);
    put_byte(0x2462U,input->kind==1U ? input->enable : 0U);
    put_byte(0x1e34U,0x40U | (bank==0U ? 2U : 1U)
        | ((input->kind==1U && input->positive) ? bank+1U : 0U));
    put_byte(0x4252U,(input->kind==2U || input->kind==6U || input->kind==7U) ? input->mode : 8U);
    put_word(0x4970U,(input->kind==2U || input->kind==6U || input->kind==7U) ? input->coefficient : 0x8000U);
    put_long(0x9818U,0xa5c3d2e1U);
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index) {
        memcpy((void *)(uintptr_t)calibration_starts[index],maf_extended_stock_calibrations+offset,calibration_sizes[index]);
        offset+=calibration_sizes[index];
    }
    if (input->kind==0U || input->kind==5U) {
        *(volatile uint16_t *)(uintptr_t)0x9586U=(uint16_t)input->multiplier;
        *(volatile uint16_t *)(uintptr_t)0x958cU=(uint16_t)input->bias;
    } else if (input->kind==1U) {
        *(volatile uint8_t *)(uintptr_t)0x8ac3U=(uint8_t)input->weight;
    }
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&maf_extended_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    if (!prepare(input)) return 0;
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[4]=input->argument;
    if (input->kind==5U) {
        context.r[12]=0U;context.r[13]=1U;context.r[14]=RAM_BASE+0x1e1cU;
    }
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot_calibrations();
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-maf-extended-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\""); hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\""); print_calibrations();
    printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(maf_extended_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_MAF_EXTENDED status=PASS region=%s cases=%lu\n",
           MAF_EXTENDED_REGION,(unsigned long)ARRAY_SIZE(maf_extended_cases));
    return 0;
}
