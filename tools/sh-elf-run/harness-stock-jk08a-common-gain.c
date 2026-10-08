/* Natural common gain with real diagnostic, division and interpolation paths. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "common-gain-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? COMMON_GAIN_EARLY_COUNT : COMMON_GAIN_CASE_COUNT)
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
static uint8_t pools_before[180];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x83c4U,3},{0x89feU,1},{0x8ae7U,1},{0x8b51U,1},{0x9332U,2},{0x93c6U,2},{0x129e2U,16},{0x129f2U,16},{0x21dc8U,4},{0x21dccU,4},{0x25f10U,4},{0x2639aU,2},{0x2639cU,4},{0x26abcU,4},{0x537e4U,2},{0x537e6U,2},{0x537e8U,2},{0x537eaU,2},{0x537ecU,2},{0x53890U,2},{0x53892U,2},{0x53894U,2},{0x53896U,2},{0x53898U,2},{0x5389aU,2},{0x5389cU,2},{0x538a0U,4},{0x538a4U,4},{0x538a8U,4},{0x538acU,4},{0x538b0U,4},{0x538b4U,4},{0x538b8U,4},{0x538bcU,4},{0x538c0U,4},{0x538c4U,4},{0x538c8U,4},{0x538ccU,4},{0x538d0U,4},{0x538d4U,4},{0x538d8U,4},{0x538dcU,4},{0x538e0U,4},{0x538e4U,4},{0x538e8U,4},{0x538ecU,4},{0x538f0U,4},{0x538f4U,4},{0x538f8U,4}
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void set32(volatile uint8_t *p,uint32_t value){
    p[0]=(uint8_t)(value>>24);p[1]=(uint8_t)(value>>16);
    p[2]=(uint8_t)(value>>8);p[3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"common_gain[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static uint32_t expected_reg(const struct common_gain_case *test,unsigned index){
    static const uint32_t changed[]={0U,1U,2U,3U,4U,5U,6U,7U};
    unsigned i;
    for(i=0;i<ARRAY_SIZE(changed);++i)if(changed[i]==index)return test->expected_clobbered[i];
    return common_gain_incoming[test->variant][index];
}
static int separate_from_test_ram(const void *pointer,size_t size){
    uintptr_t begin=(uintptr_t)pointer,end=begin+size;
    return end>=begin && (end<=RAM_BASE || begin>=RAM_BASE+65536U);
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    if(!separate_from_test_ram(common_gain_cases,sizeof(common_gain_cases))
       || !separate_from_test_ram(common_gain_incoming,sizeof(common_gain_incoming))
       || !separate_from_test_ram(ram_template,sizeof(ram_template))
       || !separate_from_test_ram(ram_before,sizeof(ram_before))
       || !separate_from_test_ram(ram_expected,sizeof(ram_expected))){
        fprintf(stderr,"literal data overlaps declared RAM: cases=%08lx bytes=%lu\n",
                (unsigned long)(uintptr_t)common_gain_cases,(unsigned long)sizeof(common_gain_cases));
        return 0;
    }
    return REGION_ENTRY==0x53698U && OUTPUT==0xffff165eU && FACTOR==0xffff160dU
        && *(volatile uint32_t *)0x538a0U==0x01002470U
        && *(volatile uint32_t *)0x538d8U==0x0100128cU
        && *(volatile uint32_t *)0x25f10U==0x01005718U
        && *(volatile uint32_t *)0x538a8U==0x0000ca99U
        && *(volatile uint32_t *)0x538d0U==0x00012a00U
        && *(volatile uint32_t *)0x538f4U==0x00128500U
        && *(volatile uint16_t *)0x53896U==0x148bU
        && *(volatile uint16_t *)0x53898U==0x2710U;
}
static void seed(const struct common_gain_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    *ram(0x2485U)=(uint8_t)test->flags;
    *ram(0x5aa3U)=(uint8_t)test->diagnostic;
    *ram(0x2733U)=(uint8_t)test->correction;
    *ram(0x11b3U)=(uint8_t)test->rpm;
    set16(ram(0x4524U),test->pressure_input);
    set16(ram(0x1024U),test->bfs);
    *((volatile uint8_t *)0x83c4U)=(uint8_t)test->a_floor;
    *((volatile uint8_t *)0x83c5U)=(uint8_t)test->factor_low;
    *((volatile uint8_t *)0x83c6U)=(uint8_t)test->factor_high;
    *((volatile uint8_t *)0x89feU)=(uint8_t)test->pressure_slope;
    set16((volatile uint8_t *)0x93c6U,test->pressure_offset);
    *((volatile uint8_t *)0x8b51U)=(uint8_t)test->constant_correction;
    *((volatile uint8_t *)0x8ae7U)=(uint8_t)test->ratio_constant;
    set16((volatile uint8_t *)0x9332U,test->gain_scalar);
    for(i=0;i<16U;++i)((volatile uint8_t *)0x129e2U)[i]=test->load_curve[i];
    for(i=0;i<16U;++i)((volatile uint8_t *)0x129f2U)[i]=test->rpm_curve[i];
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct common_gain_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    memcpy(context.r,common_gain_incoming[test->variant],sizeof(context.r));
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
    set32(expected_frame+156U,context.r[12]);
    set32(expected_frame+152U,context.r[13]);set32(expected_frame+148U,context.r[14]);
    set32(expected_frame+144U,out.continuation);set32(expected_frame+140U,context.macl);
    for(i=0;i<6U;++i)if(test->locals_mask&(1U<<i))set32(expected_frame+116U+4U*i,test->locals[i]);
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame, natural saves and real arithmetic locals",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    ((uint8_t *)ram_expected)[0x2485U]=(uint8_t)test->updated_flags;
    if(test->flags&8U){
        set16((uint8_t *)ram_expected+0x517cU,test->pressure_word);
        ((uint8_t *)ram_expected)[0x13b1U]=(uint8_t)test->coordinate;
        ((uint8_t *)ram_expected)[0x17baU]=(uint8_t)test->load_value;
        ((uint8_t *)ram_expected)[0x17bbU]=(uint8_t)test->rpm_value;
        ((uint8_t *)ram_expected)[0x17b9U]=(uint8_t)test->curve_sum;
        set16((uint8_t *)ram_expected+0x31d8U,test->load_word);
        ((uint8_t *)ram_expected)[0x17eeU]=(uint8_t)test->ratio_byte;
        ((uint8_t *)ram_expected)[(FACTOR&65535U)]=(uint8_t)test->affine_byte;
        set16((uint8_t *)ram_expected+(OUTPUT&65535U),test->gain_word);
    }
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
    if(ARRAY_SIZE(common_gain_cases)!=COMMON_GAIN_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,common_gain_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
