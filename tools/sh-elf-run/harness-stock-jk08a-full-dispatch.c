/* Full stock dispatch, real callees and coherent declared pointer windows. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "full-dispatch-cases.h"
#include "full-dispatch-pools.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? FULL_DISPATCH_EARLY_COUNT : FULL_DISPATCH_CASE_COUNT)
#define RAM_BASE 0x01000000U
#define RAM_WORDS 16384U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete context");
_Static_assert(sizeof(struct observation)==572U,"complete observation");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before");
_Static_assert(offsetof(struct observation,frame_after)==376U,"frame after");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete SR");
extern void stock_invoke_oneshot(uint32_t,const struct context *,struct observation *);
static uint32_t ram_template[RAM_WORDS],ram_before[RAM_WORDS],ram_expected[RAM_WORDS];
static uint8_t pools_before[551],timer_before[52],timer_expected[52],pulse_before[56],pulse_expected[56];
static uint8_t control_before[17],event_before[21];
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
    fprintf(stderr,"full_dispatch[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static void seed(unsigned long index,const struct full_dispatch_case *test){
    const struct dispatch_selector *s=&test->selection;unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    *ram(0x4555U)=(uint8_t)test->in_ticks;
    *ram(0x11deU)=(uint8_t)test->in_cylinder;
    *ram(0x1526U)=(uint8_t)test->in_cylinder_history;
    *ram(0x2364U)=(uint8_t)test->in_lead_source;
    *ram(0x24c9U)=(uint8_t)test->in_event_source;
    *ram(0x2298U)=(uint8_t)test->in_event_mode;
    *ram(0x20b4U)=(uint8_t)test->in_slot;
    *ram(0x20b5U)=(uint8_t)test->in_queue;
    *ram(0x157eU)=(uint8_t)test->in_mask_a;
    *ram(0x16feU)=(uint8_t)test->in_mask_b;
    *ram(0x1935U)=(uint8_t)test->in_history;
    *ram(0x14c3U)=(uint8_t)test->in_mask_c;
    *ram(0x14c2U)=(uint8_t)test->in_mask_d;
    *ram(0x2228U)=(uint8_t)test->in_pending;
    *ram(0x221dU)=(uint8_t)test->in_old_lead;
    *ram(0x221eU)=(uint8_t)test->in_cursor;
    *ram(0x2333U)=(uint8_t)test->in_angle;
    *ram(0x4251U)=(uint8_t)test->in_diagnostic;
    *ram(0x24c9U)=(uint8_t)test->in_mode;
    *ram(0x13b2U)=(uint8_t)test->in_position;
    *ram(0x4184U)=(uint8_t)test->in_enable;
    *ram(0x166cU)=(uint8_t)test->in_scratch;
    *ram(0x193bU)=(uint8_t)test->in_remainder;
    set16(ram(0x22bcU),test->in_period);
    set16(ram(0x158aU),test->in_capture);
    set16(ram(0x13b8U),test->in_count);
    set16(ram(0x16c2U),test->in_offset);
    *ram(0x418cU)=(uint8_t)s->flag_a;*ram(0x24a0U)=(uint8_t)s->flag_b;
    *ram(0x1220U)=(uint8_t)s->clear;*ram(0x22e0U)=(uint8_t)s->inhibit;
    set16(ram(0x23aaU),s->opening);set16(ram(0x238aU),s->stopped);set16(ram(0x2386U),s->start);
    set16(ram(0x2388U),s->threshold);set16(ram(0x238cU),s->floor1);set16(ram(0x238eU),s->floor2);
    set16(ram(0x2392U),s->floor4);set16(ram(0x2390U),s->running);
    *(volatile uint8_t *)0x8d92U=(uint8_t)s->config;
    *(volatile uint8_t *)0x85f7U=(uint8_t)s->tail_factor;
    *(volatile uint16_t *)0x94e8U=(uint16_t)s->calibration;
    for(i=0;i<6U;++i){
        set16(ram(0x2348U+2U*i),s->snapshot[i]);set16(ram(0x1466U+2U*i),s->correction[i]);
        set16(ram(0x195eU+2U*i),s->secondary[i]);set16(ram(0x2398U+2U*i),s->copy_source[i]);
        set16(ram(0x224eU+2U*i),test->durations[i]);
    }
    for(i=0;i<52U;++i)((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS-8U))[i]=(uint8_t)(0x6dU+i*17U+index);
    set16((volatile uint8_t *)(uintptr_t)TIMER_ALIAS,test->timer);
    set16((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS+4U),test->compare);
    set16((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS+30U),test->timer_status);
    set16((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS+34U),test->timer_control);
    for(i=0;i<52U;++i)timer_before[i]=((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS-8U))[i];
    for(i=0;i<56U;++i)((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS-8U))[i]=(uint8_t)(0x27U+i*31U+index);
    for(i=0;i<6U;++i)set16((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS+2U*i),test->counters[i]);
    set16((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS+38U),test->started);
    for(i=0;i<56U;++i)pulse_before[i]=((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS-8U))[i];
    for(i=0;i<17U;++i)((volatile uint8_t *)(uintptr_t)(CONTROL_ALIAS-8U))[i]=(uint8_t)(i*19U+index);
    for(i=0;i<21U;++i)((volatile uint8_t *)(uintptr_t)(EVENT_ALIAS-8U))[i]=(uint8_t)(i*37U+index);
    *(volatile uint8_t *)(uintptr_t)CONTROL_ALIAS=(uint8_t)test->control_flag;
    ((volatile uint8_t *)(uintptr_t)EVENT_ALIAS)[3]=(uint8_t)test->event_flag;
    ((volatile uint8_t *)(uintptr_t)EVENT_ALIAS)[4]=(uint8_t)test->event_aux;
    for(i=0;i<17U;++i)control_before[i]=((volatile uint8_t *)(uintptr_t)(CONTROL_ALIAS-8U))[i];
    for(i=0;i<21U;++i)event_before[i]=((volatile uint8_t *)(uintptr_t)(EVENT_ALIAS-8U))[i];
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct full_dispatch_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;uint32_t expected_reg;
    uint8_t *expected_bytes=(uint8_t *)ram_expected;
    memcpy(context.r,test->incoming,sizeof(context.r));
    context.gbr=test->variant?0x01004567U:0x01003579U;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=test->entry_sr;before=context;
    seed(index,test);memset(&out,0xa6,sizeof(out));
    stock_invoke_oneshot(REGION_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    if((out.sr_before&0x3f1U)!=test->entry_sr)return fail(index,"actual prepared I/M/Q/T",out.sr_before&0x3f1U,test->entry_sr);
    for(i=0;i<15U;++i){
        expected_reg=test->expected[i];
        if(i==0U && test->r0_full_sr)expected_reg|=out.sr_before&~0x3f1U;
        if(reg(&out,i)!=expected_reg)return fail(index,"complete GPR state",reg(&out,i),expected_reg);
    }
    if(out.exit[0]!=((out.sr_before&~0x3f1U)|test->expected_sr))return fail(index,"complete exit SR",out.exit[0],(out.sr_before&~0x3f1U)|test->expected_sr);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)return fail(index,"complete MACL/MACH/GBR preservation",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)return fail(index,"natural complete return PR/SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));frame_set(expected_frame,128,out.continuation);
    for(i=0;i<test->frame_count;++i){
        if(test->frame[i].at>=sizeof(expected_frame))return fail(index,"bounded declared frame byte",test->frame[i].at,0);
        expected_frame[test->frame[i].at]=(uint8_t)test->frame[i].value;
    }
    for(i=0;i<sizeof(expected_frame);++i)
        if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete nested frame",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    expected_bytes[0x4555U]=(uint8_t)test->out_ticks;
    expected_bytes[0x11deU]=(uint8_t)test->out_cylinder;
    expected_bytes[0x1526U]=(uint8_t)test->out_cylinder_history;
    expected_bytes[0x2364U]=(uint8_t)test->out_lead_source;
    expected_bytes[0x24c9U]=(uint8_t)test->out_event_source;
    expected_bytes[0x2298U]=(uint8_t)test->out_event_mode;
    expected_bytes[0x20b4U]=(uint8_t)test->out_slot;
    expected_bytes[0x20b5U]=(uint8_t)test->out_queue;
    expected_bytes[0x157eU]=(uint8_t)test->out_mask_a;
    expected_bytes[0x16feU]=(uint8_t)test->out_mask_b;
    expected_bytes[0x1935U]=(uint8_t)test->out_history;
    expected_bytes[0x14c3U]=(uint8_t)test->out_mask_c;
    expected_bytes[0x14c2U]=(uint8_t)test->out_mask_d;
    expected_bytes[0x2228U]=(uint8_t)test->out_pending;
    expected_bytes[0x221dU]=(uint8_t)test->out_old_lead;
    expected_bytes[0x221eU]=(uint8_t)test->out_cursor;
    expected_bytes[0x2333U]=(uint8_t)test->out_angle;
    expected_bytes[0x4251U]=(uint8_t)test->out_diagnostic;
    expected_bytes[0x24c9U]=(uint8_t)test->out_mode;
    expected_bytes[0x13b2U]=(uint8_t)test->out_position;
    expected_bytes[0x4184U]=(uint8_t)test->out_enable;
    expected_bytes[0x166cU]=(uint8_t)test->out_scratch;
    expected_bytes[0x193bU]=(uint8_t)test->out_remainder;
    set16(expected_bytes+0x22bcU,test->out_period);
    set16(expected_bytes+0x158aU,test->out_capture);
    set16(expected_bytes+0x13b8U,test->out_count);
    set16(expected_bytes+0x16c2U,test->out_offset);
    for(i=0;i<6U;++i){
        set16(expected_bytes+0x224eU+2U*i,test->output_words[i]);
        set16(expected_bytes+0x1466U+2U*i,test->output_corrections[i]);
        set16(expected_bytes+0x195eU+2U*i,test->output_secondary[i]);
    }
    for(i=0;i<RAM_WORDS;++i)
        if(((volatile uint32_t *)(uintptr_t)RAM_BASE)[i]!=ram_expected[i])return fail(index,"all RAM bytes and exact publication",4U*i,ram_expected[i]);
    memcpy(timer_expected,timer_before,sizeof(timer_expected));
    set16(timer_expected+12U,test->expected_compare);set16(timer_expected+38U,test->expected_timer_status);
    set16(timer_expected+42U,test->expected_timer_control);
    for(i=0;i<52U;++i)
        if(((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS-8U))[i]!=timer_expected[i])return fail(index,"complete timer storage and neighbors",i,timer_expected[i]);
    memcpy(pulse_expected,pulse_before,sizeof(pulse_expected));
    for(i=0;i<6U;++i)set16(pulse_expected+8U+2U*i,test->counter_output[i]);
    set16(pulse_expected+46U,test->expected_started);
    for(i=0;i<56U;++i)
        if(((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS-8U))[i]!=pulse_expected[i])return fail(index,"complete pulse storage and neighbors",i,pulse_expected[i]);
    for(i=0;i<17U;++i){
        uint8_t expected=i==8U?(uint8_t)test->expected_control_flag:control_before[i];
        if(((volatile uint8_t *)(uintptr_t)(CONTROL_ALIAS-8U))[i]!=expected)return fail(index,"coherent control RAM and neighbors",i,expected);
    }
    for(i=0;i<21U;++i){
        uint8_t expected=i==11U?(uint8_t)test->expected_event_flag:i==12U?(uint8_t)test->expected_event_aux:event_before[i];
        if(((volatile uint8_t *)(uintptr_t)(EVENT_ALIAS-8U))[i]!=expected)return fail(index,"event RAM window and neighbors",i,expected);
    }
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])return fail(index,"all bound pools and ROM inputs",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned i;unsigned long index;uint8_t *bytes=(uint8_t *)ram_template;
    if(ARRAY_SIZE(full_dispatch_cases)!=FULL_DISPATCH_CASE_COUNT || REGION_ENTRY!=0x54a44U)return 1;
    if(*(volatile uint16_t *)0x54b5aU!=CONTROL_ALIAS || *(volatile uint16_t *)0x2b75cU!=CONTROL_ALIAS
       || *(volatile uint16_t *)0x54b52U!=EVENT_ALIAS || *(volatile uint16_t *)0x54c28U!=TIMER_ALIAS
       || *(volatile uint16_t *)0x2b764U!=TIMER_ALIAS || *(volatile uint16_t *)0x2c234U!=PULSE_ALIAS)return 1;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    for(index=0;index<ACTIVE_CASE_COUNT;++index)if(!run_case(index,full_dispatch_cases+index))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
