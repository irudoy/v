/* Natural enrichment prefix through the selected mixture byte and SP-40 boundary. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "enrichment-prefix-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? ENRICHMENT_PREFIX_EARLY_COUNT : ENRICHMENT_PREFIX_CASE_COUNT)
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
static uint8_t pools_before[235];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x8b9bU,1},{0x8b9fU,1},{0xa9aaU,64},{0x11ac7U,8},{0x11cc0U,8},{0x11cd8U,8},{0x1214eU,16},{0x12552U,9},{0x261acU,4},{0x261b0U,4},{0x261b4U,4},{0x2639aU,2},{0x2639cU,4},{0x26498U,4},{0x2649cU,4},{0x267c8U,4},{0x26980U,4},{0x26a08U,4},{0x26abcU,4},{0x559f4U,2},{0x559f6U,2},{0x55ad8U,2},{0x55ae4U,4},{0x55ae8U,4},{0x55aecU,4},{0x55af0U,4},{0x55af4U,4},{0x55af8U,4},{0x55afcU,4},{0x55b00U,4},{0x55b04U,4},{0x55b08U,4},{0x55b0cU,4},{0x55b10U,4},{0x55b14U,4},{0x55b18U,4},{0x55b1cU,4},{0x55b20U,4},{0x55b24U,4},{0x55b28U,4}
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void set32(volatile uint8_t *p,uint32_t value){
    p[0]=(uint8_t)(value>>24);p[1]=(uint8_t)(value>>16);
    p[2]=(uint8_t)(value>>8);p[3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"enrichment_prefix[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static uint32_t expected_reg(const struct enrichment_prefix_case *test,unsigned index){
    static const uint32_t changed[]={0U,1U,2U,3U,4U,5U,6U,7U,12U,13U,14U};
    unsigned i;
    for(i=0;i<ARRAY_SIZE(changed);++i)if(changed[i]==index)return test->expected_clobbered[i];
    return enrichment_prefix_incoming[test->variant][index];
}
static int separate_from_test_ram(const void *pointer,size_t size){
    uintptr_t begin=(uintptr_t)pointer,end=begin+size;
    return end>=begin && (end<=RAM_BASE || begin>=RAM_BASE+65536U);
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    if(!separate_from_test_ram(enrichment_prefix_cases,sizeof(enrichment_prefix_cases))
       || !separate_from_test_ram(enrichment_prefix_incoming,sizeof(enrichment_prefix_incoming))
       || !separate_from_test_ram(ram_template,sizeof(ram_template))
       || !separate_from_test_ram(ram_before,sizeof(ram_before))
       || !separate_from_test_ram(ram_expected,sizeof(ram_expected))){
        fprintf(stderr,"literal data overlaps declared RAM: cases=%08lx bytes=%lu\n",
                (unsigned long)(uintptr_t)enrichment_prefix_cases,(unsigned long)sizeof(enrichment_prefix_cases));
        return 0;
    }
    return REGION_ENTRY==0x559f8U && PREFIX_ENTRY==0x5594aU && OUTPUT==0xffff15ebU
        && *(volatile uint32_t *)0x55ae4U==0x0100128cU
        && *(volatile uint32_t *)0x55ae8U==0x0100119cU
        && *(volatile uint32_t *)0x55af8U==0x01002464U
        && *(volatile uint32_t *)0x55b00U==0x0000a9aaU
        && *(volatile uint32_t *)0x55b04U==0x00011cc0U
        && *(volatile uint32_t *)0x55b08U==0x00011ac7U;
}
static void seed(const struct enrichment_prefix_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    const struct enrichment_prefix_calibration *cal=enrichment_prefix_calibrations+test->calibration;
    *ram(0x11b3U)=(uint8_t)test->rpm_byte;
    *ram(0x3528U)=(uint8_t)test->load_threshold;
    *ram(0x2468U)=(uint8_t)test->wide_flags;
    *ram(0x102cU)=(uint8_t)test->normalized;
    *ram(0x2466U)=(uint8_t)test->correction_flags;
    *ram(0x11aeU)=(uint8_t)test->correction_coordinate;
    *ram(0x24a2U)=(uint8_t)test->rich_flags;
    set16(ram(0x11bcU),test->speed);
    for(i=0;i<16U;++i)((volatile uint8_t *)0x1214eU)[i]=cal->wide_curve[i];
    for(i=0;i<64U;++i)((volatile uint8_t *)0xa9aaU)[i]=cal->surface[i];
    for(i=0;i<8U;++i)((volatile uint8_t *)0x11cc0U)[i]=cal->row_axis[i];
    for(i=0;i<8U;++i)((volatile uint8_t *)0x11ac7U)[i]=cal->column_axis[i];
    for(i=0;i<9U;++i)((volatile uint8_t *)0x12552U)[i]=cal->correction_curve[i];
    for(i=0;i<8U;++i)((volatile uint8_t *)0x11cd8U)[i]=cal->correction_axis[i];
    *((volatile uint8_t *)0x8b9bU)=cal->rich_set;
    *((volatile uint8_t *)0x8b9fU)=cal->rich_hold;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct enrichment_prefix_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    memcpy(context.r,enrichment_prefix_incoming[test->variant],sizeof(context.r));
    context.gbr=test->variant?0x01004567U:0x01003579U;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=test->entry_sr;before=context;
    seed(test);memset(&out,0xa6,sizeof(out));
    stock_invoke_oneshot(PREFIX_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    if((out.sr_before&0x3f1U)!=test->entry_sr)
        return fail(index,"actual prepared I/M/Q/T",out.sr_before&0x3f1U,test->entry_sr);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=(i==11U?out.continuation:expected_reg(test,i)))return fail(index,"complete return GPR",reg(&out,i),i==11U?out.continuation:expected_reg(test,i));
    if(out.exit[0]!=((out.sr_before&~0x301U)|(test->expected_sr&0x301U)))
        return fail(index,"complete SR",out.exit[0],(out.sr_before&~0x301U)|(test->expected_sr&0x301U));
    if(out.exit[2]!=test->expected_macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"complete live MACL and preserved MACH/GBR",1,0);
    if(out.sp!=out.abi_before[10]-204U || out.exit[1]!=out.continuation)
        return fail(index,"actual boundary continuation and stock SP-40",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    set32(expected_frame+140U,out.continuation);
    for(i=0;i<64U;++i)if(test->frame_mask[i/8U]&(1U<<(i%8U)))expected_frame[96U+i]=test->frame[i];
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame, natural saves and real arithmetic locals",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    ((uint8_t *)ram_expected)[0x2468U]=(uint8_t)test->updated_wide_flags;
    ((uint8_t *)ram_expected)[0x24a2U]=(uint8_t)test->updated_rich_flags;
    ((uint8_t *)ram_expected)[0x14efU]=(uint8_t)test->wide_value;
    ((uint8_t *)ram_expected)[OUTPUT&65535U]=(uint8_t)test->mixture_byte;
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
    if(ARRAY_SIZE(enrichment_prefix_cases)!=ENRICHMENT_PREFIX_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,enrichment_prefix_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
