/* Natural base accumulator with complete registers, frame and RAM checks. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "base-accumulator-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? BASE_ACCUMULATOR_EARLY_COUNT : BASE_ACCUMULATOR_CASE_COUNT)
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
static uint8_t pools_before[12];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x554f4U,4},{0x555c8U,4},{0x555ecU,4}
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void set32(volatile uint8_t *p,uint32_t value){
    p[0]=(uint8_t)(value>>24);p[1]=(uint8_t)(value>>16);
    p[2]=(uint8_t)(value>>8);p[3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"base_accumulator[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static uint32_t expected_reg(const struct base_accumulator_case *test,unsigned index){
    static const uint32_t changed[]={0U,1U,2U,4U,5U,6U,7U};
    unsigned i;
    for(i=0;i<ARRAY_SIZE(changed);++i)if(changed[i]==index)return test->expected_clobbered[i];
    return base_accumulator_incoming[test->variant][index];
}
static int separate_from_test_ram(const void *pointer,size_t size){
    uintptr_t begin=(uintptr_t)pointer,end=begin+size;
    return end>=begin && (end<=RAM_BASE || begin>=RAM_BASE+65536U);
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    if(!separate_from_test_ram(base_accumulator_cases,sizeof(base_accumulator_cases))
       || !separate_from_test_ram(base_accumulator_incoming,sizeof(base_accumulator_incoming))
       || !separate_from_test_ram(ram_template,sizeof(ram_template))
       || !separate_from_test_ram(ram_before,sizeof(ram_before))
       || !separate_from_test_ram(ram_expected,sizeof(ram_expected))){
        fprintf(stderr,"literal data overlaps declared RAM: cases=%08lx bytes=%lu\n",
                (unsigned long)(uintptr_t)base_accumulator_cases,(unsigned long)sizeof(base_accumulator_cases));
        return 0;
    }
    return REGION_ENTRY==0x554aeU && TERM==0xffff15f8U
        && CONDITIONAL==0xffff230cU && COOLANT==0xffff15daU && OUTPUT==0xffff231aU
        && *(volatile uint16_t *)0x554f4U==0x034eU
        && *(volatile uint16_t *)0x554f6U==0x036cU
        && *(volatile uint32_t *)0x555c8U==0x0100128cU
        && *(volatile uint32_t *)0x555ecU==0x010022f8U;
}
static void seed(const struct base_accumulator_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    set32(ram(TERM),test->term);set16(ram(CONDITIONAL),test->conditional);
    set16(ram(COOLANT),test->coolant);
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct base_accumulator_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    memcpy(context.r,base_accumulator_incoming[test->variant],sizeof(context.r));
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
    set32(expected_frame+156U,context.gbr);
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame, GBR save and neighbors",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    set16((uint8_t *)ram_expected+(OUTPUT&65535U),test->output);
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
    if(ARRAY_SIZE(base_accumulator_cases)!=BASE_ACCUMULATOR_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,base_accumulator_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
