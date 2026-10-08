/* Complete stock selector and actual per-channel correction callees. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "pulse-selector-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : PULSE_SELECTOR_CASE_COUNT)
#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_t; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[96],frame_after[96];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete entry context");
_Static_assert(offsetof(struct context,entry_t)==72U,"entry T offset");
_Static_assert(sizeof(struct observation)==380U,"complete observation");
_Static_assert(offsetof(struct observation,sp)==80U,"SP offset");
_Static_assert(offsetof(struct observation,continuation)==84U,"natural PR offset");
_Static_assert(offsetof(struct observation,abi_before)==88U,"ABI before offset");
_Static_assert(offsetof(struct observation,abi_after)==136U,"ABI after offset");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before offset");
_Static_assert(offsetof(struct observation,frame_after)==280U,"frame after offset");
_Static_assert(offsetof(struct observation,sr_before)==376U,"full SR offset");
extern void stock_invoke_injection_start_delay(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[65536],ram_expected[65536],pools_before[110];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x85f7U,1},{0x8d92U,1},{0x94e8U,2},{0x2219cU,32},{0x221d8U,8},
    {0x54dccU,2},{0x54e88U,2},{0x54e8cU,4},{0x54e94U,4},{0x54ea4U,20},
    {0x5729cU,6},{0x57354U,28}
};
static volatile uint8_t *ram(uint32_t at){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(at&65535U));}
static uint32_t reg(const struct observation *o,unsigned i){return o->exit[19U-i];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void frame_set(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);
    p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"pulse_selector[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;
    static const struct { uint32_t at,value; } longs[]={
        {0x221d8U,0x221e6U},{0x221dcU,0x2219cU},{0x54e8cU,0x01001ff4U},
        {0x54e94U,0x8d92U},{0x54ea4U,0x01002330U},{0x54ea8U,0x01004188U},
        {0x54eacU,0x01002470U},{0x54eb0U,0x94e8U},{0x54eb4U,0x571c0U},
        {0x57354U,0x0100128cU},{0x57358U,0x01001ff4U},{0x5735cU,0x221bcU},
        {0x57360U,0x0100120eU},{0x57364U,0x010022dcU},{0x57368U,0x85f7U},{0x5736cU,0x01002330U}
    };
    if(REGION_ENTRY!=0x54d3eU || OUTPUT!=0xffff224eU || SNAPSHOT!=0xffff2348U)return 0;
    if(*(volatile uint8_t *)0x85f7U!=128U || *(volatile uint8_t *)0x8d92U!=122U
       || *(volatile uint16_t *)0x94e8U!=170U)return 0;
    for(i=0;i<ARRAY_SIZE(longs);++i)
        if(*(volatile uint32_t *)longs[i].at!=longs[i].value)
            return fail(i,"exact pool and declared RAM aliases",*(volatile uint32_t *)longs[i].at,longs[i].value);
    return 1;
}
static void seed(unsigned long index,const struct pulse_selector_case *t){
    unsigned i,j,at=0;
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*19U+(i>>8)+index);
    *ram(0x418cU)=(uint8_t)t->flag_a;*ram(0x24a0U)=(uint8_t)t->flag_b;
    *ram(0x2228U)=(uint8_t)t->pending;*ram(0x1220U)=(uint8_t)t->clear;*ram(0x22e0U)=(uint8_t)t->inhibit;
    set16(ram(0x23aaU),t->opening);set16(ram(0x238aU),t->stopped);set16(ram(0x2386U),t->start);
    set16(ram(0x2388U),t->threshold);set16(ram(0x238cU),t->floor1);set16(ram(0x238eU),t->floor2);
    set16(ram(0x2392U),t->floor4);set16(ram(0x2390U),t->running);
    *(volatile uint8_t *)0x8d92U=(uint8_t)t->config;
    *(volatile uint8_t *)0x85f7U=(uint8_t)t->tail_factor;
    *(volatile uint16_t *)0x94e8U=(uint16_t)t->calibration;
    for(i=0;i<6U;++i){
        set16(ram(SNAPSHOT+2U*i),t->snapshot[i]);set16(ram(0x1466U+2U*i),t->correction[i]);
        set16(ram(0x195eU+2U*i),t->secondary[i]);set16(ram(0x2398U+2U*i),t->copy_source[i]);
    }
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct pulse_selector_case *t){
    struct context context,before;struct observation out;
    uint8_t expected_frame[96];unsigned i,j,at=0;char field[40];
    memcpy(context.r,t->incoming,sizeof(context.r));
    context.gbr=t->variant?0xd8b6a491U:0x456789abU;
    context.mach=t->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=t->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_t=t->entry_t;before=context;
    seed(index,t);memset(&out,0xa6,sizeof(out));
    stock_invoke_injection_start_delay(REGION_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=t->expected[i]){
            snprintf(field,sizeof(field),"literal full GPR R%u",i);
            return fail(index,field,reg(&out,i),t->expected[i]);
        }
    if((out.sr_before&0x301U)!=t->entry_t)return fail(index,"actual prepared M/Q/T",out.sr_before&0x301U,t->entry_t);
    if(out.exit[0]!=((out.sr_before&~1U)|1U))return fail(index,"complete SR",out.exit[0],(out.sr_before&~1U)|1U);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"complete MACL/MACH/GBR preservation",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)
        return fail(index,"natural full-function PR/SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"distinct C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    frame_set(expected_frame,60,context.r[14]);frame_set(expected_frame,56,out.continuation);
    frame_set(expected_frame,52,context.macl);frame_set(expected_frame,48,context.gbr);
    if(t->local_written)frame_set(expected_frame,44,t->local_value);
    if(t->config&8U){
        for(i=0;i<6U;++i)frame_set(expected_frame,40U-4U*i,context.r[8U+i]);
        frame_set(expected_frame,16,t->child_r14);frame_set(expected_frame,12,0x54e7cU);
        frame_set(expected_frame,8,t->child_macl);frame_set(expected_frame,4,0x01002330U);
        frame_set(expected_frame,0,t->child_r2);
    }
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete nested frame and neighbors",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    for(i=0;i<6U;++i){
        set16(ram_expected+(OUTPUT&65535U)+2U*i,t->output[i]);
        set16(ram_expected+0x1466U+2U*i,t->expected_correction[i]);
        set16(ram_expected+0x195eU+2U*i,t->expected_secondary[i]);
    }
    for(i=0;i<65536U;++i)
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"full RAM and exact channel writes",i,ram_expected[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all declared ROM inputs and pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(pulse_selector_cases)!=PULSE_SELECTOR_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,pulse_selector_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
