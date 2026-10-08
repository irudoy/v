/* Stock event ISR, real selector/one-shot calls, TRAPA frame and natural RTE. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "event-isr-cases.h"
#include "event-isr-pools.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? EVENT_ISR_EARLY_COUNT : EVENT_ISR_CASE_COUNT)
#define RAM_BASE 0x01000000U
#define RAM_WORDS 16384U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before,pr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete entry context");
_Static_assert(sizeof(struct observation)==576U,"complete exception observation");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"frame after offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"full SR offset");
_Static_assert(offsetof(struct observation,pr_before)==572U,"incoming PR offset");
extern void stock_invoke_injector_event(uint32_t,const struct context *,struct observation *);
static uint32_t ram_template[RAM_WORDS],ram_before[RAM_WORDS],ram_expected[RAM_WORDS];
static uint8_t pools_before[194],timer_before[52],timer_expected[52],pulse_before[56],pulse_expected[56];
static uint8_t control_before[16],event_before[16];
static unsigned long completed;
static const uint32_t event_addresses[8]={0x20b5U,0x157eU,0x16feU,0x2270U,0x226fU,0x226eU,0x14c3U,0x14c2U};
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static volatile uint32_t *exception_vector(void){
    uint32_t vbr;
    __asm__ volatile("stc vbr,%0":"=r"(vbr));
    return (volatile uint32_t *)(uintptr_t)(vbr+0x100U);
}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void frame_set(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);
    p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"event_isr[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;uint32_t vbr;uint8_t *bytes=(uint8_t *)ram_template;
    __asm__ volatile("stc vbr,%0":"=r"(vbr));
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    return vbr==0U && REGION_ENTRY==0x2be40U && TIMER_ALIAS==0x7e00U && PULSE_ALIAS==0x7d00U
        && CONTROL_ALIAS==0x7f00U && EVENT_ALIAS==0x7c00U && STATUS_REGISTER==0xfffff45eU
        && CONTROL_REGISTER==0xfffff462U && COUNTER_REGISTER==0xfffff640U && START_REGISTER==0xfffff666U
        && *(volatile uint16_t *)0x2bf7aU==TIMER_ALIAS && *(volatile uint16_t *)0x2bf7cU==CONTROL_ALIAS
        && *(volatile uint16_t *)0x2bf80U==EVENT_ALIAS && *(volatile uint16_t *)0x2c234U==PULSE_ALIAS;
}
static void seed(unsigned long index,const struct event_isr_case *test){
    const struct event_selector *s=&test->selection;unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    *ram(0x4184U)=(uint8_t)test->enable;*ram(0x4251U)=(uint8_t)test->diagnostic;
    *ram(0x1935U)=(uint8_t)test->history;*ram(0x1937U)=(uint8_t)test->release;
    *ram(0x2298U)=(uint8_t)test->event_mode;
    *ram(0x418cU)=(uint8_t)s->flag_a;*ram(0x24a0U)=(uint8_t)s->flag_b;
    *ram(0x2228U)=(uint8_t)s->pending;*ram(0x1220U)=(uint8_t)s->clear;*ram(0x22e0U)=(uint8_t)s->inhibit;
    set16(ram(0x23aaU),s->opening);set16(ram(0x238aU),s->stopped);set16(ram(0x2386U),s->start);
    set16(ram(0x2388U),s->threshold);set16(ram(0x238cU),s->floor1);set16(ram(0x238eU),s->floor2);
    set16(ram(0x2392U),s->floor4);set16(ram(0x2390U),s->running);
    *(volatile uint8_t *)0x8d92U=(uint8_t)s->config;
    *(volatile uint8_t *)0x85f7U=(uint8_t)s->tail_factor;
    *(volatile uint16_t *)0x94e8U=(uint16_t)s->calibration;
    for(i=0;i<6U;++i){
        set16(ram(0x2348U+2U*i),s->snapshot[i]);set16(ram(0x1466U+2U*i),s->correction[i]);
        set16(ram(0x195eU+2U*i),s->secondary[i]);set16(ram(0x2398U+2U*i),s->copy_source[i]);
    }
    for(i=0;i<8U;++i)*ram(event_addresses[i])=(uint8_t)test->event_bytes[i];
    for(i=0;i<52U;++i)((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS-8U))[i]=(uint8_t)(0x6dU+i*17U+index);
    set16((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS+30U),test->timer_status);
    set16((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS+34U),test->timer_control);
    for(i=0;i<52U;++i)timer_before[i]=((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS-8U))[i];
    for(i=0;i<56U;++i)((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS-8U))[i]=(uint8_t)(0x27U+i*31U+index);
    for(i=0;i<6U;++i)set16((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS+2U*i),test->counters[i]);
    set16((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS+38U),test->started);
    for(i=0;i<56U;++i)pulse_before[i]=((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS-8U))[i];
    for(i=0;i<16U;++i){
        ((volatile uint8_t *)(uintptr_t)(CONTROL_ALIAS-8U))[i]=(uint8_t)(i*19U+index);
        ((volatile uint8_t *)(uintptr_t)(EVENT_ALIAS-8U))[i]=(uint8_t)(i*37U+index);
    }
    *(volatile uint8_t *)(uintptr_t)CONTROL_ALIAS=(uint8_t)test->control_flag;
    *(volatile uint8_t *)(uintptr_t)EVENT_ALIAS=(uint8_t)test->event_flag;
    for(i=0;i<16U;++i){
        control_before[i]=((volatile uint8_t *)(uintptr_t)(CONTROL_ALIAS-8U))[i];
        event_before[i]=((volatile uint8_t *)(uintptr_t)(EVENT_ALIAS-8U))[i];
    }
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct event_isr_case *test){
    const struct event_selector *s=&test->selection;
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;uint32_t vector_before;
    volatile uint32_t *vector=exception_vector();
    uint8_t *expected_bytes=(uint8_t *)ram_expected;
    memcpy(context.r,test->incoming,sizeof(context.r));
    context.gbr=test->variant?0x01004567U:0x01003579U;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=test->entry_sr;before=context;
    seed(index,test);memset(&out,0xa6,sizeof(out));
    vector_before=*vector;
    *vector=REGION_ENTRY;
    stock_invoke_injector_event(REGION_ENTRY,&context,&out);
    if(exception_vector()!=vector || *vector!=REGION_ENTRY)return fail(index,"actual VBR and declared simulator exception vector held",1,0);
    *vector=vector_before;
    if((uintptr_t)vector!=0x100U)return fail(index,"declared TRAPA vector uses actual VBR",1,0);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    if((out.sr_before&0x3f1U)!=test->entry_sr)
        return fail(index,"actual prepared I/M/Q/T",out.sr_before&0x3f1U,test->entry_sr);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=context.r[i])return fail(index,"all interrupted GPR restored",reg(&out,i),context.r[i]);
    if(out.exit[0]!=out.sr_before)return fail(index,"RTE restores complete SR",out.exit[0],out.sr_before);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"complete MACL/MACH/GBR preservation",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.pr_before || out.pr_before!=out.abi_before[11])
        return fail(index,"natural RTE SP and interrupted PR",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    /* GNU 16.3 TRAPA/RTE use SSR/SPC and leave SP unchanged.
       This is the observed simulator frame, not an SH-2E exception frame. */
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    for(i=0;i<8U;++i)frame_set(expected_frame,156U-4U*i,context.r[i]);
    frame_set(expected_frame,124,context.r[12]);frame_set(expected_frame,120,context.r[13]);
    frame_set(expected_frame,116,context.r[14]);frame_set(expected_frame,112,out.pr_before);
    frame_set(expected_frame,108,context.gbr);set16(expected_frame+104,test->timer_status);
    frame_set(expected_frame,100,TIMER_ALIAS);frame_set(expected_frame,96,s->argument==4U?0x2be9cU:0x2be94U);
    frame_set(expected_frame,92,context.macl);frame_set(expected_frame,88,0x01001ff4U);
    if(s->local_written)frame_set(expected_frame,84,s->local_value);
    if(s->config&8U){
        for(i=0;i<4U;++i)frame_set(expected_frame,80U-4U*i,context.r[8U+i]);
        frame_set(expected_frame,64,test->event_flag&128U?context.r[12]:0x01001ff4U);
        frame_set(expected_frame,60,context.r[13]);
        frame_set(expected_frame,56,s->local_written?s->running:TIMER_ALIAS);
        frame_set(expected_frame,52,0x54e7cU);frame_set(expected_frame,48,s->child_macl);
        frame_set(expected_frame,44,0x01002330U);frame_set(expected_frame,40,s->child_r2);
    }
    for(i=0;i<4U;++i)frame_set(expected_frame,100U-4U*i,context.r[8U+i]);
    frame_set(expected_frame,84,0x01001ff4U);frame_set(expected_frame,80,0x0100128cU);
    frame_set(expected_frame,76,TIMER_ALIAS);frame_set(expected_frame,72,context.macl);
    frame_set(expected_frame,68,0x01001ff4U);
    if(test->enable&128U){
        frame_set(expected_frame,56,PULSE_ALIAS+12U);expected_frame[60]=64U;
        if(test->selected)set16(expected_frame+64,test->last_increment);
    }
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame))){
        fprintf(stderr,"event_isr[%lu] actual complete frame:",index);
        for(i=0;i<sizeof(expected_frame);++i)fprintf(stderr,"%s%02x",i%16U?" ":"\n",(unsigned)out.frame_after[i]);
        fprintf(stderr,"\nevent_isr[%lu] expected complete frame:",index);
        for(i=0;i<sizeof(expected_frame);++i)fprintf(stderr,"%s%02x",i%16U?" ":"\n",(unsigned)expected_frame[i]);
        fprintf(stderr,"\n");
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete nested exception frame and neighbors",out.frame_after[i],expected_frame[i]);
    }
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    for(i=0;i<6U;++i){
        set16(expected_bytes+0x224eU+2U*i,s->output[i]);set16(expected_bytes+0x1466U+2U*i,s->expected_correction[i]);
        set16(expected_bytes+0x195eU+2U*i,s->expected_secondary[i]);
    }
    for(i=0;i<8U;++i)expected_bytes[event_addresses[i]]=(uint8_t)test->expected_event_bytes[i];
    expected_bytes[0x1935U]=(uint8_t)test->expected_history;expected_bytes[0x1936U]=(uint8_t)s->pending;
    expected_bytes[0x1937U]=(uint8_t)test->expected_release;
    for(i=0;i<RAM_WORDS;++i)
        if(((volatile uint32_t *)(uintptr_t)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"all 65536 RAM bytes and exact event writes",4U*i,ram_expected[i]);
    memcpy(timer_expected,timer_before,sizeof(timer_expected));
    set16(timer_expected+38U,0x01feU);set16(timer_expected+42U,test->timer_control&65534U);
    for(i=0;i<52U;++i)
        if(((volatile uint8_t *)(uintptr_t)(TIMER_ALIAS-8U))[i]!=timer_expected[i])
            return fail(index,"all delayed timer register bytes and neighbors",i,timer_expected[i]);
    memcpy(pulse_expected,pulse_before,sizeof(pulse_expected));
    for(i=0;i<6U;++i)set16(pulse_expected+8U+2U*i,test->counter_output[i]);
    set16(pulse_expected+46U,test->started|((test->enable&128U)?(s->pending&63U):0U));
    for(i=0;i<56U;++i)
        if(((volatile uint8_t *)(uintptr_t)(PULSE_ALIAS-8U))[i]!=pulse_expected[i])
            return fail(index,"all pulse register bytes and neighbors",i,pulse_expected[i]);
    for(i=0;i<16U;++i){
        uint8_t expected=i==8U?(uint8_t)(test->control_flag&127U):control_before[i];
        if(((volatile uint8_t *)(uintptr_t)(CONTROL_ALIAS-8U))[i]!=expected)return fail(index,"control alias and neighbors",i,expected);
        expected=i==8U?(uint8_t)test->expected_event_flag:event_before[i];
        if(((volatile uint8_t *)(uintptr_t)(EVENT_ALIAS-8U))[i]!=expected)return fail(index,"event alias and neighbors",i,expected);
    }
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all bound ROM inputs and pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(event_isr_cases)!=EVENT_ISR_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,event_isr_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
