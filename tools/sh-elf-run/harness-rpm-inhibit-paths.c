/* Explicit bounded contributor inputs and complete unclassified state observations. */
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
    uint32_t kind,entry,rpm,speed,main_flags,vehicle_flags,vehicle_control,main_delay,vehicle_delay;
    uint32_t selector,condition1,condition2,condition3,config,t0,t1,t2,t3,t4,t5;
    uint32_t main_reload,vehicle_reload,speed_on,speed_off;
    uint32_t summary_flags,shared_status,summary_rpm,low_flags,high_flags,seed_flags,low_rpm;
    uint32_t low_gate1,low_gate2,high_gate1,high_gate2,hysteresis,c0,c1,c2,c3,c4,c5,c6,c7;
    uint32_t prior14,prior2,prior,variant,sr;
};
#include "rpm-inhibit-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete context ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
_Static_assert(sizeof(rpm_inhibit_stock_calibrations)==27U,"complete declared contributor calibration bytes");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE];
static uint8_t calibration_before[27];
static const uint32_t calibration_starts[]={0x8b38U,0x8c69U,0x8cafU,0x8db7U,0x8dc3U,0x934eU,0x9462U,0x12a32U};
static const uint32_t calibration_sizes[]={1U,1U,1U,1U,1U,12U,2U,8U};

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
    unsigned index,offset=0;
    const uint32_t threshold[6]={input->t0,input->t1,input->t2,input->t3,input->t4,input->t5};
    const uint32_t curve[8]={input->c0,input->c1,input->c2,input->c3,input->c4,input->c5,input->c6,input->c7};
    if (input->kind>3U) return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    put_word(0x11bcU,input->rpm);put_byte(0x110eU,input->speed);
    put_byte(0x2497U,input->main_flags);put_byte(0x24a6U,input->vehicle_flags);
    put_byte(0x24a7U,input->vehicle_control);put_byte(0x24f1U,input->main_delay);
    put_byte(0x24f6U,input->vehicle_delay);put_byte(0x2468U,input->selector);
    put_byte(0x2499U,input->condition1);put_byte(0x2494U,input->condition2);put_byte(0x244fU,input->condition3);
    if (input->kind==1U) {
        put_byte(0x2448U,input->summary_flags);put_byte(0x11b2U,input->summary_rpm);
    } else if (input->kind==2U) put_byte(0x418cU,input->shared_status);
    else if (input->kind==3U) {
        put_byte(0x2489U,input->low_flags);put_byte(0x249fU,input->high_flags);
        put_byte(0x41eaU,input->seed_flags);put_byte(0x11b3U,input->low_rpm);
        put_byte(0x245dU,input->low_gate1);put_byte(0x2458U,input->low_gate2);
        put_byte(0x24ceU,input->high_gate1);put_byte(0x24d2U,input->high_gate2);
    }
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=0xa5c3d2e1U;
    for (index=0;index<ARRAY_SIZE(calibration_starts);++index) {
        memcpy((void *)(uintptr_t)calibration_starts[index],rpm_inhibit_stock_calibrations+offset,calibration_sizes[index]);
        offset+=calibration_sizes[index];
    }
    *(volatile uint8_t *)(uintptr_t)0x8b38U=(uint8_t)input->config;
    *(volatile uint8_t *)(uintptr_t)0x8c69U=(uint8_t)input->main_reload;
    *(volatile uint8_t *)(uintptr_t)0x8cafU=(uint8_t)input->vehicle_reload;
    *(volatile uint8_t *)(uintptr_t)0x8db7U=(uint8_t)input->speed_on;
    *(volatile uint8_t *)(uintptr_t)0x8dc3U=(uint8_t)input->speed_off;
    for (index=0;index<6U;++index)
        *(volatile uint16_t *)(uintptr_t)(0x934eU+index*2U)=(uint16_t)threshold[index];
    if (input->kind==3U) {
        *(volatile uint16_t *)(uintptr_t)0x9462U=(uint16_t)input->hysteresis;
        for (index=0;index<8U;++index)
            *(volatile uint8_t *)(uintptr_t)(0x12a32U+index)=(uint8_t)curve[index];
    }
    return 1;
}
static int observe(size_t index)
{
    const struct path_case *input=&rpm_inhibit_cases[index];
    struct context context,initial;struct observation observation;unsigned reg;
    if (!prepare(input)) return 0;
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.r[0]=input->prior;context.gbr=0x01009f34U;
    if (input->kind!=0U) { context.r[2]=input->prior2;context.r[14]=input->prior14; }
    context.mach=0x13579bdfU;context.macl=0x2468ace0U;
    context.entry_sr=input->sr;context.fifth=0xb6c70000U;initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);snapshot_calibrations();
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    printf("kb-rpm-inhibit-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
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
    for (index=0;index<ARRAY_SIZE(rpm_inhibit_cases);++index) if (!observe(index)) return 1;
    printf("VQ_SH_ELF_RPM_INHIBIT status=PASS region=%s cases=%lu\n",RPM_INHIBIT_REGION,
        (unsigned long)ARRAY_SIZE(rpm_inhibit_cases));
    return 0;
}
