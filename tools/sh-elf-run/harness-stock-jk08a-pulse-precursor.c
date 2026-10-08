/* Natural precursor with actual division, signed multiply and complete observations. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "pulse-precursor-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? PULSE_PRECURSOR_EARLY_COUNT : PULSE_PRECURSOR_CASE_COUNT)
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
static uint8_t pools_before[72];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x94e8U,2},{0x96e0U,4},{0x21dc8U,4},{0x21dccU,4},{0x4eacaU,2},{0x4eaccU,2},{0x4eaceU,2},{0x4ead0U,2},{0x4ead2U,2},{0x4ebe8U,4},{0x4ebecU,4},{0x4ebf0U,4},{0x4ebf4U,4},{0x4ebf8U,4},{0x4ebfcU,4},{0x4ec00U,4},{0x4ec04U,4},{0x4ec08U,4},{0x4ec0cU,4},{0x4ec10U,4},{0x4ec14U,4}
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void set32(volatile uint8_t *p,uint32_t value){
    p[0]=(uint8_t)(value>>24);p[1]=(uint8_t)(value>>16);
    p[2]=(uint8_t)(value>>8);p[3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"pulse_precursor[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static uint32_t expected_reg(const struct pulse_precursor_case *test,unsigned index){
    static const uint32_t changed[]={0U,1U,2U,3U,4U,5U,6U,7U};
    unsigned i;
    for(i=0;i<ARRAY_SIZE(changed);++i)if(changed[i]==index)return test->expected_clobbered[i];
    return pulse_precursor_incoming[test->variant][index];
}
static int separate_from_test_ram(const void *pointer,size_t size){
    uintptr_t begin=(uintptr_t)pointer,end=begin+size;
    return end>=begin && (end<=RAM_BASE || begin>=RAM_BASE+65536U);
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    if(!separate_from_test_ram(pulse_precursor_cases,sizeof(pulse_precursor_cases))
       || !separate_from_test_ram(pulse_precursor_incoming,sizeof(pulse_precursor_incoming))
       || !separate_from_test_ram(ram_template,sizeof(ram_template))
       || !separate_from_test_ram(ram_before,sizeof(ram_before))
       || !separate_from_test_ram(ram_expected,sizeof(ram_expected))){
        fprintf(stderr,"literal data overlaps declared RAM: cases=%08lx bytes=%lu\n",
                (unsigned long)(uintptr_t)pulse_precursor_cases,(unsigned long)sizeof(pulse_precursor_cases));
        return 0;
    }
    return REGION_ENTRY==0x4e974U && OUTPUT==0xffff1876U && BANKS==0xffff18c0U
        && SELECTED_BFS==0xffff196aU
        && *(volatile uint32_t *)0x4ebe8U==0x0100245cU
        && *(volatile uint32_t *)0x4ec04U==0x0100128cU
        && *(volatile uint16_t *)0x4eaccU==0x06deU
        && *(volatile uint16_t *)0x4eaceU==0x0634U
        && *(volatile uint16_t *)0x4ead2U==0x05eaU;
}
static void seed(const struct pulse_precursor_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    *ram(0x245dU)=(uint8_t)test->source_flags;
    *ram(0x24d2U)=(uint8_t)test->cap_flags;
    *ram(0x24a1U)=(uint8_t)test->output_flags;
    set16(ram(0x1024U),test->bfs);
    set16(ram(0x123eU),test->alternate_bfs);
    set16(ram(0x11bcU),test->speed);
    set16(ram(0x34f6U),test->cap_floor);
    set16(ram(0x22e6U),test->multiplier);
    set16(ram(0x2300U),test->transient_raw);
    set16(ram(0x165eU),test->gain);
    set16(ram(0x40b6U),test->bank0);
    set16(ram(0x40b8U),test->bank1);
    set32((volatile uint8_t *)0x96e0U,test->cap_numerator);
    set16((volatile uint8_t *)0x94e8U,test->pulse_floor);
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct pulse_precursor_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    memcpy(context.r,pulse_precursor_incoming[test->variant],sizeof(context.r));
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
    if(out.exit[0]!=((out.sr_before&~0x301U)|(test->expected_sr&0x301U)))
        return fail(index,"complete SR",out.exit[0],(out.sr_before&~0x301U)|(test->expected_sr&0x301U));
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"natural complete MACL/MACH/GBR restoration",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)
        return fail(index,"actual natural continuation and stock SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    for(i=0;i<7U;++i)set32(expected_frame+156U-4U*i,context.r[8U+i]);
    set32(expected_frame+128U,out.continuation);
    set32(expected_frame+124U,context.macl);set32(expected_frame+120U,context.gbr);
    for(i=0;i<3U;++i)if(test->locals_mask&(1U<<i))set32(expected_frame+108U+4U*i,test->locals[i]);
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame, natural saves and real arithmetic locals",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    set16((uint8_t *)ram_expected+(OUTPUT&65535U),test->common_output);
    set16((uint8_t *)ram_expected+(BANKS&65535U),test->bank0_output);
    set16((uint8_t *)ram_expected+((BANKS+2U)&65535U),test->bank1_output);
    if(test->cap_flags&1U)set16((uint8_t *)ram_expected+(SELECTED_BFS&65535U),test->selected_bfs);
    ((uint8_t *)ram_expected)[0x24a1U]=(uint8_t)test->updated_flags;
    for(i=0;i<RAM_WORDS;++i)
        if(((volatile uint32_t *)(uintptr_t)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"all 65536 RAM bytes, output and immutable sources",4U*i,ram_expected[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all exact ROM words and RAM pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(pulse_precursor_cases)!=PULSE_PRECURSOR_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,pulse_precursor_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
