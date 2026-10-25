/* Natural learned-grid inputs and complete raw state; no expected outputs. */
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
#include "learning-transfer-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete independent context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[LEARNING_TRANSFER_CALIBRATION_SIZE];

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t index;
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
static void put_byte(uint32_t offset,uint32_t value)
{ *(volatile uint8_t *)(uintptr_t)(RAM_BASE+offset)=(uint8_t)value; }
static void snapshot_calibrations(void)
{
    unsigned index,offset=0;
    for (index=0;index<ARRAY_SIZE(learning_transfer_calibration_starts);++index) {
        unsigned size=learning_transfer_calibration_sizes[index];
        memcpy(calibration_before+offset,(const void *)(uintptr_t)learning_transfer_calibration_starts[index],size);
        offset+=size;
    }
}
static void print_calibrations(void)
{
    unsigned index;
    for (index=0;index<ARRAY_SIZE(learning_transfer_calibration_starts);++index)
        hex((const void *)(uintptr_t)learning_transfer_calibration_starts[index],learning_transfer_calibration_sizes[index]);
}
static int prepare(const struct path_case *input)
{
    unsigned bank=input->argument&255U,index,offset=0;
    uint32_t grid,auxiliary;
    if (bank>1U || input->kind>3U
            || (input->cell_index>=64U && !(input->kind==2U && input->cell_index==255U))) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    for (index=0;index<64U;++index) {
        put_word(0x4b10U+index*2U,0x5a5aU);
        put_word(0x4b90U+index*2U,0x5a5aU);
    }
    grid=bank ? 0x4b10U : 0x4b90U;
    auxiliary=bank ? 0x49b0U : 0x49f0U;
    if (input->kind==0U) {
        put_word(0x1024U,input->load);put_byte(0x11aeU,input->speed);
        put_byte(0x130aU+bank,input->packed);
        for (index=0;index<64U;++index) put_word(grid+index*2U,input->cell);
        put_byte(0x41b5U,input->flag);put_byte(0x5a94U,input->diagnostic);
    } else if (input->kind==3U) {
        if (input->entry!=0x57b26U) return 0;
        put_word(0x2306U+bank*2U,input->ltft_l);put_word(0x5648U+bank*2U,input->ltft_a);
        put_word(0x15fcU,input->ltft_u);put_word(0x15feU,input->ltft_v);
        put_byte(0x230eU,input->ltft_mask);put_byte(0x5a94U,input->diagnostic);
        put_byte(0x41b5U,input->ltft_f);put_byte(0x41faU,input->ltft_g);
        put_byte(0x248bU,input->ltft_h);put_byte(0x249cU,input->ltft_k);
    } else {
        put_word(0x134eU+bank*2U,input->word);put_word(0x22dcU+bank*2U,input->stft);
        put_word(0x2306U+bank*2U,input->previous);put_byte(0x130aU+bank,input->cell_index);
        if (input->cell_index<64U) put_byte(auxiliary+input->cell_index,input->counter);
        put_byte(0x1458U,input->permit_a);put_byte(0x1457U,input->permit_b);
        for (index=0;index<3U;++index) put_byte(0x2c21U+index,input->thresholds[index]);
    }
    for (index=0;index<ARRAY_SIZE(learning_transfer_calibration_starts);++index) {
        unsigned size=learning_transfer_calibration_sizes[index];
        memcpy((void *)(uintptr_t)learning_transfer_calibration_starts[index],input->calibration+offset,size);
        offset+=size;
    }
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&learning_transfer_cases[index];
    struct context context=input->context,initial;struct observation observation;
    if (!prepare(input)) return 0;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot_calibrations();memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-learning-transfer-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
    printf("\",\"observation\":\"");hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\"");rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\"");print_calibrations();printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(learning_transfer_cases);++index) if (!observe(index)) return 1;
    printf("VQ_SH_ELF_LEARNING_TRANSFERS status=PASS region=%s cases=%lu\n",
           LEARNING_TRANSFER_REGION,(unsigned long)ARRAY_SIZE(learning_transfer_cases));
    return 0;
}
