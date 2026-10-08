/* Exact six-channel one-shot with raw register storage and complete SR. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "oneshot-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? ONESHOT_EARLY_COUNT : ONESHOT_CASE_COUNT)
#define RAM_BASE 0x01000000U
#define RAM_WORDS 16384U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete entry context");
_Static_assert(offsetof(struct context,entry_sr)==72U,"controlled I/M/Q/T offset");
_Static_assert(sizeof(struct observation)==572U,"complete observation");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"frame after offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"full SR offset");
extern void stock_invoke_oneshot(uint32_t,const struct context *,struct observation *);
static uint32_t ram_template[RAM_WORDS],ram_before[RAM_WORDS],ram_expected[RAM_WORDS];
static uint8_t pools_before[30],io_before[56],io_expected[56];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={{0x2c234U,2},{0x2c238U,28}};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void frame_set(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);
    p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"oneshot[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    return REGION_ENTRY==0x2c13cU && REGISTER_ALIAS==0x7d00U
        && COUNTER_REGISTER==0xfffff640U && START_REGISTER==0xfffff666U
        && OPENING==0xffff23aaU && INHIBIT==0xffff22e0U && HISTORY==0xffff1935U
        && ENABLE==0xffff4184U && DIAGNOSTIC==0xffff4251U
        && *(volatile uint16_t *)0x2c234U==REGISTER_ALIAS;
}
static void seed(unsigned long index,const struct oneshot_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    *ram(ENABLE)=(uint8_t)test->enable;set16(ram(OPENING),test->opening);
    *ram(INHIBIT)=(uint8_t)test->inhibit;*ram(HISTORY)=(uint8_t)test->history;
    *ram(DIAGNOSTIC)=(uint8_t)test->diagnostic;
    for(i=0;i<6U;++i)set16((volatile uint8_t *)(uintptr_t)(test->pointer+2U*i),test->durations[i]);
    for(i=0;i<56U;++i)((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS-8U))[i]=(uint8_t)(0x6dU+i*17U+index);
    for(i=0;i<6U;++i)set16((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS+2U*i),test->counters[i]);
    set16((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS+38U),test->started);
    for(i=0;i<56U;++i)io_before[i]=((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS-8U))[i];
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct oneshot_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;uint32_t expected_sr;
    memcpy(context.r,test->incoming,sizeof(context.r));
    context.gbr=test->variant?0x01004567U:0x01003579U;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=test->entry_sr;before=context;
    seed(index,test);memset(&out,0xa6,sizeof(out));
    stock_invoke_oneshot(REGION_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    if((out.sr_before&0x3f1U)!=test->entry_sr)
        return fail(index,"actual prepared I/M/Q/T",out.sr_before&0x3f1U,test->entry_sr);
    expected_sr=out.sr_before|1U;
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=test->expected[i])return fail(index,"complete return GPR",reg(&out,i),test->expected[i]);
    if(out.exit[0]!=expected_sr)return fail(index,"complete SR and restored interrupt mask",out.exit[0],expected_sr);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"natural complete MACL/MACH/GBR restoration",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)
        return fail(index,"actual natural continuation and stock SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    for(i=8U;i<15U;++i)frame_set(expected_frame,188U-4U*i,context.r[i]);
    frame_set(expected_frame,124,context.gbr);frame_set(expected_frame,128,context.macl);
    if(test->enable&128U){
        frame_set(expected_frame,112,REGISTER_ALIAS+12U);expected_frame[116]=64U;
        if(test->selected)set16(expected_frame+120,test->last_increment);
    }
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete helper frame and neighbors",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    ((uint8_t *)ram_expected)[HISTORY&65535U]=(uint8_t)test->expected_history;
    for(i=0;i<RAM_WORDS;++i)
        if(((volatile uint32_t *)(uintptr_t)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"all 65536 RAM bytes, destinations and sources",4U*i,ram_expected[i]);
    memcpy(io_expected,io_before,sizeof(io_expected));
    for(i=0;i<6U;++i)set16(io_expected+8U+2U*i,test->output[i]);
    set16(io_expected+46U,test->expected_started);
    for(i=0;i<56U;++i)
        if(((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS-8U))[i]!=io_expected[i])
            return fail(index,"all declared register bytes and neighbors",i,io_expected[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all bound ROM inputs and pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(oneshot_cases)!=ONESHOT_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,oneshot_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
