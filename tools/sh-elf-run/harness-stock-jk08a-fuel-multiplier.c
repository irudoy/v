/* Complete natural multiplier publication with mode, mask, frame and RAM checks. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "fuel-multiplier-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? FUEL_MULTIPLIER_EARLY_COUNT : FUEL_MULTIPLIER_CASE_COUNT)
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
static uint8_t pools_before[60];
static uint8_t alias_before[17];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x838eU,1},{0x840dU,6},{0x84e6U,2},{0x8b9dU,1},{0x55850U,2},{0x55852U,2},{0x55858U,4},{0x5587cU,4},{0x55880U,4},{0x55884U,4},{0x55888U,4},{0x5588cU,4},{0x55890U,4},{0x55894U,4},{0x559f2U,2},{0x55adcU,4},{0x55ae0U,4},{0x55ae4U,4}
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void set32(volatile uint8_t *p,uint32_t value){
    p[0]=(uint8_t)(value>>24);p[1]=(uint8_t)(value>>16);
    p[2]=(uint8_t)(value>>8);p[3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"fuel_multiplier[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static uint32_t expected_reg(const struct fuel_multiplier_case *test,unsigned index){
    static const uint32_t changed[]={0U,1U,2U,4U,5U,6U,7U};
    unsigned i;
    for(i=0;i<ARRAY_SIZE(changed);++i)if(changed[i]==index)return test->expected_clobbered[i];
    return fuel_multiplier_incoming[test->variant][index];
}
static int separate_from_test_ram(const void *pointer,size_t size){
    uintptr_t begin=(uintptr_t)pointer,end=begin+size;
    return end>=begin && (end<=RAM_BASE || begin>=RAM_BASE+65536U);
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    if(!separate_from_test_ram(fuel_multiplier_cases,sizeof(fuel_multiplier_cases))
       || !separate_from_test_ram(fuel_multiplier_incoming,sizeof(fuel_multiplier_incoming))
       || !separate_from_test_ram(ram_template,sizeof(ram_template))
       || !separate_from_test_ram(ram_before,sizeof(ram_before))
       || !separate_from_test_ram(ram_expected,sizeof(ram_expected))){
        fprintf(stderr,"literal data overlaps declared RAM: cases=%08lx bytes=%lu\n",
                (unsigned long)(uintptr_t)fuel_multiplier_cases,(unsigned long)sizeof(fuel_multiplier_cases));
        return 0;
    }
    return REGION_ENTRY==0x556ecU && OUTPUT==0xffff22e6U && SNAPSHOT==0xffff18e4U
        && WORD_ALIAS==0x7a00U && *(volatile uint16_t *)0x55852U==WORD_ALIAS
        && *(volatile uint32_t *)0x55858U==0x010022dcU
        && *(volatile uint32_t *)0x5587cU==0x0100128cU
        && *(volatile uint32_t *)0x55880U==0x01004184U
        && *(volatile uint32_t *)0x55888U==0x01002468U;
}
static void seed(const struct fuel_multiplier_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    *ram(0x4184U)=(uint8_t)test->special;
    *ram(0x22e0U)=(uint8_t)test->aggregate;
    *ram(0x22eeU)=(uint8_t)test->other_mask;
    *ram(0x4186U)=(uint8_t)test->special_gate;
    *ram(0x2468U)=(uint8_t)test->control;
    *ram(0x246cU)=(uint8_t)test->floor_flags;
    *ram(0x246fU)=(uint8_t)test->previous_flags;
    *ram(0x24a2U)=(uint8_t)test->transition_flags;
    *ram(0x2473U)=(uint8_t)test->selector;
    *ram(0x84c3U)=(uint8_t)test->tick;
    set16(ram(0x231aU),test->base);
    set16(ram(0x240aU),test->conditional);
    set16(ram(0x22e8U),test->mixture);
    set16(ram(0x15ccU),test->floor);
    set16(ram(0x1414U),test->mode);
    set16(ram(0x22f4U),test->old);
    *(volatile uint8_t *)0x838eU=(uint8_t)test->special_gain;
    for(i=0;i<6U;++i)((volatile uint8_t *)0x840dU)[i]=(uint8_t)test->transition_rates[i];
    for(i=0;i<2U;++i)((volatile uint8_t *)0x84e6U)[i]=(uint8_t)test->rates[i];
    *(volatile uint8_t *)0x8b9dU=(uint8_t)test->cap;
    for(i=0;i<17U;++i)((volatile uint8_t *)(WORD_ALIAS-8U))[i]=(uint8_t)(0x69U+i*23U);
    *(volatile uint8_t *)WORD_ALIAS=(uint8_t)test->tick;
    for(i=0;i<17U;++i)alias_before[i]=((volatile uint8_t *)(WORD_ALIAS-8U))[i];
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct fuel_multiplier_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    memcpy(context.r,fuel_multiplier_incoming[test->variant],sizeof(context.r));
    context.gbr=test->variant?0x01004567U:0x01003579U;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=test->entry_sr;before=context;
    seed(test);memset(&out,0xa6,sizeof(out));
    stock_invoke_oneshot(REGION_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    if((out.sr_before&0x3f1U)!=test->entry_sr)
        return fail(index,"actual prepared I/M/Q/T",out.sr_before&0x3f1U,test->entry_sr);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=expected_reg(test,i))return fail(index,"complete return GPR",reg(&out,i),expected_reg(test,i));
    if(out.exit[0]!=((out.sr_before&~1U)|test->expected_t))
        return fail(index,"complete SR",out.exit[0],(out.sr_before&~1U)|test->expected_t);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"natural complete MACL/MACH/GBR restoration",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)
        return fail(index,"actual natural continuation and stock SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    set32(expected_frame+156U,context.r[13]);set32(expected_frame+152U,context.r[14]);
    set32(expected_frame+148U,context.macl);set32(expected_frame+144U,context.gbr);
    if(test->locals_mask&1U)expected_frame[128U]=(uint8_t)test->locals[0];
    if(test->locals_mask&2U)expected_frame[132U]=(uint8_t)test->locals[1];
    if(test->locals_mask&4U)set32(expected_frame+136U,test->locals[2]);
    if(test->locals_mask&8U)expected_frame[140U]=(uint8_t)test->locals[3];
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame, save words, byte locals and neighbors",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    set16((uint8_t *)ram_expected+(OUTPUT&65535U),test->output);
    set16((uint8_t *)ram_expected+(SNAPSHOT&65535U),test->snapshot);
    ((uint8_t *)ram_expected)[0x246cU]=(uint8_t)test->updated_floor;
    ((uint8_t *)ram_expected)[0x24a2U]=(uint8_t)test->updated_phase;
    for(i=0;i<RAM_WORDS;++i)
        if(((volatile uint32_t *)(uintptr_t)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"all 65536 RAM bytes, output and immutable sources",4U*i,ram_expected[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all exact ROM words and RAM pools",pools[i].at+j,pools_before[at]);
    for(i=0;i<17U;++i)
        if(((volatile uint8_t *)(WORD_ALIAS-8U))[i]!=alias_before[i])
            return fail(index,"one-byte RAM alias and all neighbors",i,alias_before[i]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(fuel_multiplier_cases)!=FUEL_MULTIPLIER_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,fuel_multiplier_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
