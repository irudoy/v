/* Complete stock angle publication and actual helper calls. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "end-angle-cases.h"
#include "end-angle-pools.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? END_ANGLE_EARLY_COUNT : END_ANGLE_CASE_COUNT)
#define RAM_BASE 0x01000000U
#define RAM_WORDS 16384U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete context");
_Static_assert(sizeof(struct observation)==572U,"complete observation");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before");
_Static_assert(offsetof(struct observation,frame_after)==376U,"frame after");
_Static_assert(offsetof(struct observation,sr_before)==568U,"full SR");
extern void stock_invoke_oneshot(uint32_t,const struct context *,struct observation *);
static uint32_t ram_template[RAM_WORDS],ram_before[RAM_WORDS],ram_expected[RAM_WORDS];
static uint8_t pools_before[291];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void frame_set(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);
    p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"end_angle[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static void seed(const struct end_angle_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    *(volatile uint8_t *)0x8b34U=(uint8_t)test->mode_a;
    *(volatile uint8_t *)0x8b42U=(uint8_t)test->mode_b;
    *(volatile uint8_t *)0x870bU=(uint8_t)test->inhibit;
    *(volatile uint8_t *)0x8770U=(uint8_t)test->warm_limit;
    *(volatile uint8_t *)0x876fU=(uint8_t)test->reload_a;
    *(volatile uint8_t *)0x876eU=(uint8_t)test->reload_b;
    *(volatile uint8_t *)0x8729U=(uint8_t)test->override;
    *(volatile uint8_t *)0x8e03U=(uint8_t)test->threshold_a;
    *(volatile uint8_t *)0x8e06U=(uint8_t)test->threshold_b;
    *(volatile uint8_t *)0x8d2cU=(uint8_t)test->threshold_sub;
    *(volatile uint8_t *)0x8bdbU=(uint8_t)test->bias_cap;
    *(volatile uint8_t *)0x8cecU=(uint8_t)test->cold_limit;
    *(volatile uint8_t *)0x88bbU=(uint8_t)test->rpm_limit;
    *(volatile uint8_t *)0x86f9U=(uint8_t)test->alternate_flag;
    set16((volatile uint8_t *)0x9504U,test->bias_period);
    set16((volatile uint8_t *)0x9038U,test->window_low);
    set16((volatile uint8_t *)0x9036U,test->window_high);
    set16((volatile uint8_t *)0x90faU,test->alternate_word);
    for(i=0;i<8U;++i)((volatile uint8_t *)0x12136U)[i]=(uint8_t)test->counter_curve[i];
    for(i=0;i<8U;++i)((volatile uint8_t *)0x12302U)[i]=(uint8_t)test->base_curve[i];
    for(i=0;i<8U;++i)((volatile uint8_t *)0x1230aU)[i]=(uint8_t)test->conditional_curve[i];
    for(i=0;i<9U;++i)((volatile uint8_t *)0x12c12U)[i]=(uint8_t)test->transient_curve[i];
    for(i=0;i<8U;++i)((volatile uint8_t *)0x11bb3U)[i]=(uint8_t)test->coolant_axis[i];
    *ram(0x106eU)=(uint8_t)test->coolant;
    *ram(0x106fU)=(uint8_t)test->previous_coolant;
    *ram(0x1071U)=(uint8_t)test->warm_input;
    *ram(0x11b2U)=(uint8_t)test->rpm_check;
    *ram(0x11b3U)=(uint8_t)test->rpm;
    *ram(0x4184U)=(uint8_t)test->source_flag;
    *ram(0x41d0U)=(uint8_t)test->warm_flag;
    *ram(0x2484U)=(uint8_t)test->selector_flag;
    *ram(0x244fU)=(uint8_t)test->gate_flag;
    *ram(0x24dfU)=(uint8_t)test->delay_a;
    *ram(0x2593U)=(uint8_t)test->delay_b;
    *ram(0x2468U)=(uint8_t)test->delay_flag;
    *ram(0x24d0U)=(uint8_t)test->prefix_flag;
    *ram(0x24a0U)=(uint8_t)test->window_flag;
    *ram(0x54eeU)=(uint8_t)test->counter;
    *ram(0x14dfU)=(uint8_t)test->counter_value;
    *ram(0x4205U)=(uint8_t)test->bias_flag;
    *ram(0x5a98U)=(uint8_t)test->fault;
    *ram(0x340bU)=(uint8_t)test->transient;
    *ram(0x340cU)=(uint8_t)test->bias;
    set16(ram(0x269eU),test->window_input);
    set16(ram(0x1002U),test->alternate_input);
    set16(ram(0x5584U),test->alternate_ram);
    set16(ram(0x340eU),test->bias_progress);
    set16(ram(0x192eU),test->angle);
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct end_angle_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    uint8_t *expected_bytes=(uint8_t *)ram_expected;
    memcpy(context.r,test->incoming,sizeof(context.r));
    context.gbr=test->variant?0x01004567U:0x01003579U;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=test->entry_sr;before=context;
    seed(test);memset(&out,0xa6,sizeof(out));
    stock_invoke_oneshot(REGION_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete context",1,0);
    if((out.sr_before&0x3f1U)!=test->entry_sr)return fail(index,"actual incoming I/M/Q/T",out.sr_before&0x3f1U,test->entry_sr);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=test->expected[i])return fail(index,"complete GPR",reg(&out,i),test->expected[i]);
    if(out.exit[0]!=((out.sr_before&~0x3f1U)|test->expected_sr))
        return fail(index,"complete exit SR",out.exit[0],(out.sr_before&~0x3f1U)|test->expected_sr);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"MACL/MACH/GBR restored",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)
        return fail(index,"natural return PR/SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"complete independent C ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    frame_set(expected_frame,140,out.continuation);
    for(i=0;i<test->frame_count;++i){
        if(test->frame[i].at>=sizeof(expected_frame))return fail(index,"bounded declared frame byte",test->frame[i].at,0);
        expected_frame[test->frame[i].at]=(uint8_t)test->frame[i].value;
    }
    for(i=0;i<sizeof(expected_frame);++i)
        if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete nested frame byte",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    expected_bytes[0x106eU]=(uint8_t)test->out_coolant;
    expected_bytes[0x106fU]=(uint8_t)test->out_previous_coolant;
    expected_bytes[0x1071U]=(uint8_t)test->out_warm_input;
    expected_bytes[0x11b2U]=(uint8_t)test->out_rpm_check;
    expected_bytes[0x11b3U]=(uint8_t)test->out_rpm;
    expected_bytes[0x4184U]=(uint8_t)test->out_source_flag;
    expected_bytes[0x41d0U]=(uint8_t)test->out_warm_flag;
    expected_bytes[0x2484U]=(uint8_t)test->out_selector_flag;
    expected_bytes[0x244fU]=(uint8_t)test->out_gate_flag;
    expected_bytes[0x24dfU]=(uint8_t)test->out_delay_a;
    expected_bytes[0x2593U]=(uint8_t)test->out_delay_b;
    expected_bytes[0x2468U]=(uint8_t)test->out_delay_flag;
    expected_bytes[0x24d0U]=(uint8_t)test->out_prefix_flag;
    expected_bytes[0x24a0U]=(uint8_t)test->out_window_flag;
    expected_bytes[0x54eeU]=(uint8_t)test->out_counter;
    expected_bytes[0x14dfU]=(uint8_t)test->out_counter_value;
    expected_bytes[0x4205U]=(uint8_t)test->out_bias_flag;
    expected_bytes[0x5a98U]=(uint8_t)test->out_fault;
    expected_bytes[0x340bU]=(uint8_t)test->out_transient;
    expected_bytes[0x340cU]=(uint8_t)test->out_bias;
    set16(expected_bytes+0x269eU,test->out_window_input);
    set16(expected_bytes+0x1002U,test->out_alternate_input);
    set16(expected_bytes+0x5584U,test->out_alternate_ram);
    set16(expected_bytes+0x340eU,test->out_bias_progress);
    set16(expected_bytes+0x192eU,test->out_angle);
    for(i=0;i<RAM_WORDS;++i)
        if(((volatile uint32_t *)(uintptr_t)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"complete RAM publication",4U*i,ram_expected[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all declared ROM inputs and pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned i;unsigned long index;uint8_t *bytes=(uint8_t *)ram_template;
    if(ARRAY_SIZE(end_angle_cases)!=END_ANGLE_CASE_COUNT || REGION_ENTRY!=0x56bd0U)return 1;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    for(index=0;index<ACTIVE_CASE_COUNT;++index)if(!run_case(index,end_angle_cases+index))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
