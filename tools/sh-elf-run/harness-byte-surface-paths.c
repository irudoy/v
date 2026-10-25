/* Complete raw state for explicit byte-surface entries and natural helpers. */
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
struct surface_case {
    uint32_t kind,entry,table,row_axis,col_axis,cols,axis,axis_max,row,col;
    uint32_t pattern,configuration,force,correction,row_index,col_index;
    uint32_t row_fraction,col_fraction,first,second,divisor,dividend,variant,sr,bridge,bridge_selected;
};
struct calibration_span { uint32_t start,size,offset,table; };
#include "byte-surface-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"independent lookup fifth argument ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[BYTE_SURFACE_CALIBRATION_BYTES];

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

static uint8_t calibration_byte(const struct surface_case *input,const struct calibration_span *span,unsigned offset)
{
    uint8_t value=byte_surface_stock_calibrations[span->offset+offset];
    if (span->table && input->pattern) {
        if (input->pattern>=8U)
            value=span->start==0xb2faU ? (input->pattern==8U ? 150U : 151U) : span->start==0xb33aU ? (input->pattern==8U ? 160U : 180U) : 128U;
        else if (input->pattern>=6U)
            value=span->start==0xb33aU ? (input->pattern==6U ? 0U : 255U) : 128U;
        else if (input->pattern==3U) value=128U;
        else if (input->pattern==1U || input->pattern==2U) {
            if (span->start==0xb2faU) value=input->pattern==1U ? 128U : 127U;
            else if (span->start==0xb33aU) value=input->pattern==1U ? 0U : 255U;
            else value=input->pattern==1U ? 255U : 0U;
        } else {
            value=(uint8_t)(offset*37U+19U);
            if (input->pattern==5U) value=(uint8_t)(255U-value);
        }
    }
    if (span->start==0x8615U && input->configuration!=2U)
        value=(uint8_t)((value&254U)|input->configuration);
    return value;
}

static void calibrations(const struct surface_case *input)
{
    unsigned index,offset;
    for (index=0;index<ARRAY_SIZE(byte_surface_calibrations);++index) {
        const struct calibration_span *span=&byte_surface_calibrations[index];
        volatile uint8_t *destination=(volatile uint8_t *)(uintptr_t)span->start;
        for (offset=0;offset<span->size;++offset)
            destination[offset]=calibration_byte(input,span,offset);
    }
}

static void calibration_snapshot(uint8_t *output)
{
    unsigned index;
    for (index=0;index<ARRAY_SIZE(byte_surface_calibrations);++index) {
        const struct calibration_span *span=&byte_surface_calibrations[index];
        memcpy(output+span->offset,(const void *)(uintptr_t)span->start,span->size);
    }
}

static int observe(size_t index)
{
    const struct surface_case *input=&byte_surface_cases[index];
    struct context context,initial;
    struct observation observation;
    uint8_t calibration_after[BYTE_SURFACE_CALIBRATION_BYTES];
    volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    unsigned reg;
    memset((void *)(uintptr_t)RAM_BASE,input->bridge ? 0 : (int)((0x5dU+input->variant*37U)&255U),RAM_SIZE);
    if (input->bridge) {
        ram[0x248bU]=5U; ram[0x1284U]=1U; ram[0x1c90U]=255U; ram[0x2327U]=91U;
        ram[0x1071U]=(uint8_t)(input->bridge_selected==0U ? 0U : 255U);
    }
    ram[0x11aeU]=(uint8_t)input->row;
    ram[0x102cU]=(uint8_t)input->col;
    ram[0x2468U]=(uint8_t)input->force;
    ram[0x2466U]=(uint8_t)input->correction;
    calibrations(input);
    for (reg=0;reg<15U;++reg)
        context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    if (input->kind==1U) {
        context.r[4]=input->table; context.r[5]=input->row_axis;
        context.r[6]=input->col_axis; context.r[7]=0xa1b20000U|input->row;
    } else if (input->kind==2U) {
        context.r[0]=input->axis; context.r[4]=input->axis_max; context.r[5]=input->row;
    } else if (input->kind==3U) {
        context.r[0]=input->row_index; context.r[1]=input->row_fraction;
        context.r[2]=input->col_index; context.r[3]=input->col_fraction;
        context.r[4]=input->table; context.r[5]=input->cols;
    } else if (input->kind==4U) {
        context.r[0]=input->first; context.r[2]=input->second; context.r[3]=input->col_fraction;
    } else if (input->kind==5U) {
        context.r[0]=input->divisor; context.r[1]=input->dividend;
    }
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|input->col;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    calibration_snapshot(calibration_before);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    calibration_snapshot(calibration_after);
    if (memcmp(&initial,&context,sizeof(context))) {
        fprintf(stderr,"byte-surface[%lu]: const input context changes\n",(unsigned long)index);
        return 0;
    }
    printf("kb-byte-surface-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->kind,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"calibration_before\":\""); hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\""); hex(calibration_after,sizeof(calibration_after));
    printf("\"}\n");
    return 1;
}

int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(byte_surface_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_BYTE_SURFACES status=PASS region=%s cases=%lu\n",
           BYTE_SURFACE_REGION,(unsigned long)ARRAY_SIZE(byte_surface_cases));
    return 0;
}
