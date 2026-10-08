/* Stock battery-dependent opening word with complete register and memory checks. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "opening-word-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? 12U : OPENING_WORD_CASE_COUNT)
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
static uint8_t ram_before[65536],ram_expected[65536],pools_before[22];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x84f6U,1},{0x8c9eU,1},{0x5700cU,20}
};
static volatile uint8_t *ram(uint32_t at){return (volatile uint8_t *)(uintptr_t)ALIAS(at);}
static uint32_t reg(const struct observation *o,unsigned i){return o->exit[19U-i];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void frame_set(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);
    p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"opening_word[%lu] %s actual=%08lx expected=%08lx\n",
            index,field,(unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;
    static const struct { uint32_t at,value; } longs[]={
        {0x5700cU,0x01001094U},{0x57010U,0x84f6U},{0x57014U,0x8c9eU},
        {0x57018U,0x224f8U},{0x5701cU,0x010023bcU}
    };
    if(REGION_ENTRY!=0x56fc0U || BATTERY!=0xffff1108U || OPENING!=0xffff2436U)return 0;
    if(*(volatile uint8_t *)0x84f6U!=92U || *(volatile uint8_t *)0x8c9eU!=70U)
        return fail(0,"factory byte calibrations",1,0);
    for(i=0;i<ARRAY_SIZE(longs);++i)
        if(*(volatile uint32_t *)longs[i].at!=longs[i].value)
            return fail(i,"exact pool and declared RAM alias",*(volatile uint32_t *)longs[i].at,longs[i].value);
    return 1;
}
static void seed(unsigned long index,const struct opening_word_case *t){
    unsigned i,j,at=0;
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*19U+(i>>8)+index);
    *ram(BATTERY)=(uint8_t)t->battery;
    *(volatile uint8_t *)0x84f6U=(uint8_t)t->slope;
    *(volatile uint8_t *)0x8c9eU=(uint8_t)t->additive;
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct opening_word_case *t){
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
    frame_set(expected_frame,60,context.r[14]);
    frame_set(expected_frame,56,out.continuation);
    frame_set(expected_frame,52,context.macl);
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame/save/local/neighbors",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    set16(ram_expected+(OPENING&65535U),t->value);
    for(i=0;i<65536U;++i)
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"full RAM, exact opening word write, immutable sources",i,ram_expected[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all declared ROM inputs and constant pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(opening_word_cases)!=OPENING_WORD_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,opening_word_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
