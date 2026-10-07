/* Full stock channel calculation with literal registers and complete memory checks. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "channel-pulse-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : CHANNEL_PULSE_CASE_COUNT)
#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&65535U))
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
static uint8_t ram_before[65536],ram_expected[65536],pools_before[55];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x8d92U,1},{0x91daU,8},{0x129c0U,6},{0x4ec08U,4},{0x4ec20U,4},
    {0x4ed60U,8},{0x4ed70U,20},{0x5b884U,4}
};
static volatile uint8_t *ram(uint32_t at){return (volatile uint8_t *)(uintptr_t)ALIAS(at);}
static uint32_t reg(const struct observation *o,unsigned i){return o->exit[19U-i];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void frame_set(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);
    p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"channel_pulse[%lu] %s actual=%08lx expected=%08lx\n",
            index,field,(unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;
    static const struct { uint32_t at,value; } longs[]={
        {0x4ec08U,0x010022dcU},{0x4ec20U,0x010023bcU},{0x4ed70U,0x0100128cU},
        {0x4ed74U,0x8d92U},{0x4ed78U,0x129c0U},{0x4ed7cU,0x224f8U},
        {0x4ed80U,0x5b7ecU},{0x5b884U,0x91daU}
    };
    static const uint16_t words[]={0x0692U,0x0690U,0x010aU,0x01daU};
    static const uint16_t coefficients[]={13656U,16384U,4250U,0U};
    if(REGION_ENTRY!=0x4eba2U || INHIBIT!=0xffff22e0U || COMPENSATED!=0xffff23c8U
       || TRANSFORMED!=0xffff23d4U || OPENING!=0xffff2436U || ADDITIVE!=0xffff1396U
       || SUBTRACTIVE!=0xffff1466U || MULTIPLIER!=0x129c0U)return 0;
    if(*(volatile uint8_t *)0x8d92U!=0x7aU)return fail(0,"factory flag",1,0);
    for(i=0;i<6U;++i)
        if(((volatile uint8_t *)MULTIPLIER)[i]!=128U)return fail(i,"factory multiplier",1,0);
    for(i=0;i<4U;++i){
        if(((volatile uint16_t *)0x4ed60U)[i]!=words[i])return fail(i,"bound displacement",1,0);
        if(((volatile uint16_t *)0x91daU)[i]!=coefficients[i])return fail(i,"factory affine coefficient",1,0);
    }
    for(i=0;i<ARRAY_SIZE(longs);++i)
        if(*(volatile uint32_t *)longs[i].at!=longs[i].value)
            return fail(i,"exact pool and declared RAM alias",*(volatile uint32_t *)longs[i].at,longs[i].value);
    return 1;
}
static void seed(unsigned long index,const struct channel_pulse_case *t){
    unsigned i,j,at=0;
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*19U+(i>>8)+index);
    *ram(INHIBIT)=(uint8_t)t->mask;
    set16(ram(0xffff191cU),t->even_base);set16(ram(0xffff191eU),t->odd_base);
    set16(ram(ADDITIVE+2U*t->channel),t->additive);
    set16(ram(SUBTRACTIVE+2U*t->channel),t->subtractive);
    set16(ram(OPENING),t->opening);
    *(volatile uint8_t *)0x8d92U=(uint8_t)t->flag;
    for(i=0;i<6U;++i)((volatile uint8_t *)MULTIPLIER)[i]=128U;
    ((volatile uint8_t *)MULTIPLIER)[t->channel]=(uint8_t)t->multiplier;
    set16((volatile uint8_t *)0x91daU,t->a);set16((volatile uint8_t *)0x91dcU,t->c);
    set16((volatile uint8_t *)0x91deU,t->b);set16((volatile uint8_t *)0x91e0U,t->d);
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct channel_pulse_case *t){
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
    if((out.sr_before&0x301U)!=t->entry_t)
        return fail(index,"actual prepared M/Q/T",out.sr_before&0x301U,t->entry_t);
    if(out.exit[0]!=((out.sr_before&~1U)|t->expected_t))
        return fail(index,"complete SR",out.exit[0],(out.sr_before&~1U)|t->expected_t);
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
    frame_set(expected_frame,44,t->compensated);
    if(!t->inhibited){
        frame_set(expected_frame,40,2U*t->channel);
        frame_set(expected_frame,36,((int32_t)(t->even_base*(1U-(t->channel&1U))+t->odd_base*(t->channel&1U))
                   +(int32_t)(int16_t)t->additive-((t->flag&8U)?(int32_t)(int16_t)t->subtractive:0))>0
                   ?t->product:context.macl);
        frame_set(expected_frame,32,0x010023bcU);
    }
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame/save/local/neighbors",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    set16(ram_expected+(COMPENSATED&65535U)+2U*t->channel,t->compensated);
    set16(ram_expected+(TRANSFORMED&65535U)+2U*t->channel,t->transformed);
    for(i=0;i<65536U;++i)
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"full RAM, exact two word writes, immutable sources",i,ram_expected[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all declared ROM inputs and constant pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(channel_pulse_cases)!=CHANNEL_PULSE_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,channel_pulse_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
