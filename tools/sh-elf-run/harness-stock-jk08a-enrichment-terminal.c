/* Staged terminal mixture bounds with the natural auxiliary call and publication. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "enrichment-terminal-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? ENRICHMENT_TERMINAL_EARLY_COUNT : ENRICHMENT_TERMINAL_CASE_COUNT)
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
static uint8_t pools_before[182];
static uint8_t alias_before[17];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x849bU,2},{0x86eaU,1},{0x86f3U,1},{0x87d6U,1},{0x87d9U,1},{0x8b9bU,2},{0x8b9fU,1},{0x8befU,1},{0x8f86U,2},{0x929cU,2},{0x94ecU,2},{0x11edeU,8},{0x26382U,2},{0x26384U,4},{0x26abcU,4},{0x56316U,2},{0x563dcU,2},{0x563e0U,4},{0x563e4U,4},{0x563f0U,4},{0x563f4U,4},{0x563f8U,4},{0x563fcU,4},{0x56400U,4},{0x56404U,4},{0x5651aU,2},{0x5660eU,2},{0x56610U,4},{0x56614U,4},{0x56618U,4},{0x5661cU,4},{0x56620U,4},{0x56624U,4},{0x56628U,4},{0x5662cU,4},{0x56630U,4},{0x56634U,4},{0x56638U,4},{0x5663cU,4},{0x56640U,4},{0x56644U,4},{0x56648U,4},{0x5664cU,4},{0x56650U,4},{0x56654U,4},{0x56658U,4},{0x5665cU,4},{0x56660U,4},{0x56664U,4},{0x56668U,4},{0x56700U,4},{0x56704U,4},{0x56708U,4},{0x5670cU,4}
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void set32(volatile uint8_t *p,uint32_t value){
    p[0]=(uint8_t)(value>>24);p[1]=(uint8_t)(value>>16);
    p[2]=(uint8_t)(value>>8);p[3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"enrichment_terminal[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static uint32_t expected_reg(const struct enrichment_terminal_case *test,unsigned index){
    static const uint32_t changed[]={0U,1U,2U,3U,4U,5U,6U,7U,12U,13U,14U};
    unsigned i;
    for(i=0;i<ARRAY_SIZE(changed);++i)if(changed[i]==index)return test->expected_clobbered[i];
    return enrichment_terminal_incoming[test->variant][index];
}
static int separate_from_test_ram(const void *pointer,size_t size){
    uintptr_t begin=(uintptr_t)pointer,end=begin+size;
    return end>=begin && (end<=RAM_BASE || begin>=RAM_BASE+65536U);
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    if(!separate_from_test_ram(enrichment_terminal_cases,sizeof(enrichment_terminal_cases))
       || !separate_from_test_ram(enrichment_terminal_incoming,sizeof(enrichment_terminal_incoming))
       || !separate_from_test_ram(ram_template,sizeof(ram_template))
       || !separate_from_test_ram(ram_before,sizeof(ram_before))
       || !separate_from_test_ram(ram_expected,sizeof(ram_expected))){
        fprintf(stderr,"literal data overlaps declared RAM: cases=%08lx bytes=%lu\n",
                (unsigned long)(uintptr_t)enrichment_terminal_cases,(unsigned long)sizeof(enrichment_terminal_cases));
        return 0;
    }
    return REGION_ENTRY==0x56408U && TERMINAL_ENTRY==0x562e2U && OUTPUT==0xffff22e8U
        && WORD_ALIAS==0x7a00U
        && *(volatile uint16_t *)0x56316U==WORD_ALIAS
        && *(volatile uint16_t *)0x5660eU==WORD_ALIAS
        && *(volatile uint32_t *)0x563e0U==0x0100128cU;
}
static void seed(const struct enrichment_terminal_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    const struct enrichment_terminal_calibration *cal=enrichment_terminal_calibrations+test->calibration;
    *ram(0x1410U)=(uint8_t)test->mode;
    *ram(0x2485U)=(uint8_t)test->flags;
    *ram(0x2493U)=(uint8_t)test->phase_flags;
    *ram(0x15ebU)=(uint8_t)test->mixture;
    *ram(0x84c3U)=(uint8_t)test->tick;
    *ram(0x2700U)=(uint8_t)test->rpm;
    *ram(0x2531U)=(uint8_t)test->delay;
    *ram(0x4252U)=(uint8_t)test->override;
    *ram(0x2474U)=(uint8_t)test->aux_flags;
    *ram(0x102cU)=(uint8_t)test->normalized;
    *ram(0x110eU)=(uint8_t)test->temperature;
    *ram(0x24e9U)=(uint8_t)test->aux_delay;
    *ram(0x11b3U)=(uint8_t)test->rpm_byte;
    set16(ram(0x1278U),test->previous);
    set16(ram(0x127aU),test->aux_previous);
    set16(ram(0x123cU),test->aux_current);
    *((volatile uint8_t *)0x849bU)=cal->down;
    *((volatile uint8_t *)0x849cU)=cal->up;
    *((volatile uint8_t *)0x8b9bU)=cal->rich_set;
    *((volatile uint8_t *)0x8b9cU)=cal->rich_initial;
    *((volatile uint8_t *)0x8b9fU)=cal->rich_hold;
    *((volatile uint8_t *)0x86eaU)=cal->norm_hysteresis;
    *((volatile uint8_t *)0x86f3U)=cal->temperature_hysteresis;
    *((volatile uint8_t *)0x87d9U)=cal->temperature_threshold;
    *((volatile uint8_t *)0x8befU)=cal->delay_reload;
    *((volatile uint8_t *)0x87d6U)=cal->speed_reload;
    set16((volatile uint8_t *)0x929cU,cal->main_limit);
    set16((volatile uint8_t *)0x94ecU,cal->override_limit);
    set16((volatile uint8_t *)0x8f86U,cal->aux_cap);
    for(i=0;i<8U;++i)((volatile uint8_t *)0x11edeU)[i]=cal->curve[i];
    for(i=0;i<17U;++i)((volatile uint8_t *)(WORD_ALIAS-8U))[i]=(uint8_t)(0x69U+i*23U);
    *(volatile uint8_t *)WORD_ALIAS=(uint8_t)test->tick;
    for(i=0;i<17U;++i)alias_before[i]=((volatile uint8_t *)(WORD_ALIAS-8U))[i];
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct enrichment_terminal_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    memcpy(context.r,enrichment_terminal_incoming[test->variant],sizeof(context.r));
    context.r[0]=(context.r[0]&0xffff0000U)|test->staged;
    context.gbr=test->variant?0x01004567U:0x01003579U;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=test->entry_sr;before=context;
    seed(test);memset(&out,0xa6,sizeof(out));
    stock_invoke_oneshot(TERMINAL_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    if((out.sr_before&0x3f1U)!=test->entry_sr)
        return fail(index,"actual prepared I/M/Q/T",out.sr_before&0x3f1U,test->entry_sr);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=(i==11U?out.continuation:expected_reg(test,i)))return fail(index,"complete return GPR",reg(&out,i),i==11U?out.continuation:expected_reg(test,i));
    if(out.exit[0]!=((out.sr_before&~0x301U)|(test->expected_sr&0x301U)))
        return fail(index,"complete SR",out.exit[0],(out.sr_before&~0x301U)|(test->expected_sr&0x301U));
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"complete preserved MACL/MACH/GBR",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)
        return fail(index,"actual staged boundary continuation and stock SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    set32(expected_frame+184U,out.continuation);
    for(i=0;i<40U;++i)if(test->frame_mask[i/8U]&(1U<<(i%8U)))expected_frame[136U+i]=test->frame[i];
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame, natural saves and real arithmetic locals",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    set16((uint8_t *)ram_expected+0x123aU,test->primary_word);
    set16((uint8_t *)ram_expected+0x123cU,test->aux_word);
    set16((uint8_t *)ram_expected+(OUTPUT&65535U),test->output_word);
    ((uint8_t *)ram_expected)[0x2485U]=test->updated_flags;
    ((uint8_t *)ram_expected)[0x2474U]=test->updated_aux_flags;
    ((uint8_t *)ram_expected)[0x2493U]=test->updated_phase_flags;
    ((uint8_t *)ram_expected)[0x24e9U]=test->updated_aux_delay;
    ((uint8_t *)ram_expected)[0x12e7U]=test->aux_curve_value;
    ((uint8_t *)ram_expected)[0x2531U]=test->updated_delay;
    for(i=0;i<RAM_WORDS;++i)
        if(((volatile uint32_t *)(uintptr_t)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"all 65536 RAM bytes, output and immutable sources",4U*i,ram_expected[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all exact ROM words and RAM pools",pools[i].at+j,pools_before[at]);
    for(i=0;i<17U;++i)
        if(((volatile uint8_t *)(WORD_ALIAS-8U))[i]!=alias_before[i])
            return fail(index,"coherent one-byte RAM aliases and all neighbors",i,alias_before[i]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(enrichment_terminal_cases)!=ENRICHMENT_TERMINAL_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,enrichment_terminal_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
