/* Complete natural coolant-context update with exact calls, locals and RAM effects. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "coolant-conditional-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? COOLANT_CONDITIONAL_EARLY_COUNT : COOLANT_CONDITIONAL_CASE_COUNT)
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
static uint8_t pools_before[126];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x86ebU,1},{0x87a5U,3},{0x9090U,2},{0x929aU,2},{0x990aU,16},{0x11b17U,4},{0x11b1bU,4},{0x12422U,8},{0x26382U,2},{0x26384U,4},{0x26abcU,4},{0x5533cU,2},{0x55350U,4},{0x55370U,4},{0x55374U,4},{0x55378U,4},{0x5537cU,4},{0x55380U,4},{0x554f0U,2},{0x554f2U,2},{0x554f4U,2},{0x555c0U,4},{0x555c4U,4},{0x555c8U,4},{0x555ccU,4},{0x555d0U,4},{0x555d4U,4},{0x555d8U,4},{0x555dcU,4},{0x555e0U,4},{0x555e4U,4},{0x555e8U,4}
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void set32(volatile uint8_t *p,uint32_t value){
    p[0]=(uint8_t)(value>>24);p[1]=(uint8_t)(value>>16);
    p[2]=(uint8_t)(value>>8);p[3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"coolant_conditional[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    return REGION_ENTRY==0x5525aU && OUTPUT==0xffff15daU
        && *(volatile uint32_t *)0x555c8U==0x0100128cU
        && *(volatile uint32_t *)0x55370U==0x01002458U
        && *(volatile uint16_t *)0x5533cU==0xff40U;
}
static void seed(const struct coolant_conditional_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    *ram(0x11b3U)=(uint8_t)test->rpm;
    *ram(0x1107U)=(uint8_t)test->warm;
    *ram(0x106fU)=(uint8_t)test->previous_coolant;
    *ram(0x102cU)=(uint8_t)test->load;
    *ram(0x11aeU)=(uint8_t)test->rpm_select;
    *ram(0x2492U)=(uint8_t)test->flags_a;
    *ram(0x2493U)=(uint8_t)test->flags_b;
    *ram(0x2458U)=(uint8_t)test->source_flag;
    *ram(0x2485U)=(uint8_t)test->direction_flag;
    set16(ram(0x15daU),test->old);
    set16(ram(0x22e8U),test->mixture);
    for(i=0;i<3U;++i)((volatile uint8_t *)0x87a5U)[i]=(uint8_t)test->thresholds[i];
    *(volatile uint8_t *)0x86ebU=(uint8_t)test->hysteresis;
    for(i=0;i<8U;++i)((volatile uint8_t *)0x12422U)[i]=(uint8_t)test->curve[i];
    for(i=0;i<4U;++i)((volatile uint8_t *)0x11b1bU)[i]=(uint8_t)test->load_axis[i];
    for(i=0;i<4U;++i)((volatile uint8_t *)0x11b17U)[i]=(uint8_t)test->rpm_axis[i];
    for(i=0;i<16U;++i)((volatile uint8_t *)0x990aU)[i]=(uint8_t)test->coefficients[i];
    set16((volatile uint8_t *)0x9090U,test->rate);
    set16((volatile uint8_t *)0x929aU,test->cap);
    set16((volatile uint8_t *)0x5533cU,test->coolant_offset);
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct coolant_conditional_case *test){
    struct context context,before;struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    memcpy(context.r,test->incoming,sizeof(context.r));
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
        if(reg(&out,i)!=test->expected[i])return fail(index,"complete return GPR",reg(&out,i),test->expected[i]);
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
    for(i=0;i<5U;++i)set32(expected_frame+156U-4U*i,context.r[10U+i]);
    set32(expected_frame+136U,out.continuation);
    set32(expected_frame+132U,context.macl);set32(expected_frame+128U,context.gbr);
    for(i=0;i<6U;++i)if(test->locals_mask&(1U<<i))set32(expected_frame+104U+4U*i,test->locals[i]);
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame, save words, locals and lookup neighbors",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    set16((uint8_t *)ram_expected+(OUTPUT&65535U),test->output);
    ((uint8_t *)ram_expected)[0x2492U]=(uint8_t)test->updated_a;
    ((uint8_t *)ram_expected)[0x2493U]=(uint8_t)test->updated_b;
    ((uint8_t *)ram_expected)[0x2485U]=(uint8_t)test->updated_direction;
    if(test->enabled){
        ((uint8_t *)ram_expected)[0x15ddU]=(uint8_t)test->lookup;
        ((uint8_t *)ram_expected)[0x15dcU]=(uint8_t)test->selected;
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
    if(ARRAY_SIZE(coolant_conditional_cases)!=COOLANT_CONDITIONAL_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i,coolant_conditional_cases+i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
