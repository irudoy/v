/* Whole stock programmer with declared synthetic register storage and full SR. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "full-programmer-cases.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? FULL_PROGRAMMER_EARLY_COUNT : FULL_PROGRAMMER_CASE_COUNT)
#define RAM_BASE 0x01000000U
#define RAM_WORDS 16384U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define CAPTURE_ADDRESS 0xffff158aU
struct context { uint32_t r[15],gbr,mach,macl,entry_sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete entry context");
_Static_assert(offsetof(struct context,entry_sr)==72U,"controlled I/M/Q/T offset");
_Static_assert(sizeof(struct observation)==572U,"complete observation");
_Static_assert(offsetof(struct observation,sp)==80U,"actual SP offset");
_Static_assert(offsetof(struct observation,continuation)==84U,"natural PR offset");
_Static_assert(offsetof(struct observation,abi_before)==88U,"ABI before offset");
_Static_assert(offsetof(struct observation,abi_after)==136U,"ABI after offset");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"frame after offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"full SR offset");
extern void stock_invoke_injection_scheduler(uint32_t,const struct context *,struct observation *);
static uint32_t ram_template[RAM_WORDS],ram_before[RAM_WORDS],ram_expected[RAM_WORDS];
static uint8_t pools_before[42],alias_before[16],io_before[52],io_expected[52];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } pools[]={
    {0x28e9eU,4},{0x29020U,4},{0x2b75aU,14},{0x2b864U,20}
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static void frame_set(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);
    p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"full_programmer[%lu] %s actual=%08lx expected=%08lx\n",index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;
    uint8_t *bytes=(uint8_t *)ram_template;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    return REGION_ENTRY==0x2b64aU && CONTROL==0xffff84ecU && WORD_ALIAS==0x7f00U
        && COUNT==0xffff13b8U && REMAINDER==0xffff193bU && MODE==0xffff24c9U
        && POSITION==0xffff13b2U && PERIOD==0xffff22bcU && OUTPUT==0xffff16c2U && SCRATCH==0xffff166cU
        && REGISTER_ALIAS==0x7e00U && COUNTER_REGISTER==0xfffff440U
        && COMPARE_REGISTER==0xfffff444U && STATUS_REGISTER==0xfffff45eU && CONTROL_REGISTER==0xfffff462U
        && *(volatile uint16_t *)0x2b75cU==WORD_ALIAS && *(volatile uint16_t *)0x2b764U==REGISTER_ALIAS;
}
static void seed(unsigned long index,const struct full_programmer_case *test){
    unsigned i,j,at=0;
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    set16(ram(COUNT),0xa7b8U);*ram(REMAINDER)=0xa9U;
    *ram(MODE)=(uint8_t)test->mode;*ram(POSITION)=(uint8_t)test->position;
    set16(ram(PERIOD),test->period);set16(ram(OUTPUT),0xa7b8U);*ram(SCRATCH)=0xc9U;
    set16(ram(CAPTURE_ADDRESS),test->capture);
    for(i=0;i<16U;++i)((volatile uint8_t *)(uintptr_t)(WORD_ALIAS-8U))[i]=(uint8_t)(0x36U+i*31U+index);
    *(volatile uint8_t *)(uintptr_t)WORD_ALIAS=(uint8_t)test->flag;
    for(i=0;i<16U;++i)alias_before[i]=((volatile uint8_t *)(uintptr_t)(WORD_ALIAS-8U))[i];
    for(i=0;i<52U;++i)((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS-8U))[i]=(uint8_t)(0x6dU+i*17U+index);
    set16((volatile uint8_t *)(uintptr_t)REGISTER_ALIAS,test->timer);
    set16((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS+4U),test->compare);
    set16((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS+30U),test->status);
    set16((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS+34U),test->control);
    for(i=0;i<52U;++i)io_before[i]=((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS-8U))[i];
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
}
static int run_case(unsigned long index,const struct full_programmer_case *test){
    struct context context,before;
    struct observation out;
    uint8_t expected_frame[192];unsigned i,j,at=0;
    uint32_t expected_sr;uint8_t *expected_bytes=(uint8_t *)ram_expected;
    memcpy(context.r,test->incoming,sizeof(context.r));
    context.gbr=test->variant?0x01004567U:0x01003579U;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=test->entry_sr;before=context;
    seed(index,test);memset(&out,0xa6,sizeof(out));
    stock_invoke_injection_scheduler(REGION_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    if((out.sr_before&0x3f1U)!=test->entry_sr)
        return fail(index,"actual prepared I/M/Q/T",out.sr_before&0x3f1U,test->entry_sr);
    expected_sr=test->count ? (out.sr_before&~1U)|test->expected_t
                           : (out.sr_before&~0xf1U)|0x80U|test->expected_t;
    for(i=0;i<15U;++i){
        uint32_t expected=(i==0U && !test->count)?expected_sr:test->expected[i];
        if(reg(&out,i)!=expected)return fail(index,"complete full GPR",reg(&out,i),expected);
    }
    if(out.exit[0]!=expected_sr)return fail(index,"complete exit SR",out.exit[0],expected_sr);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"natural complete MACL/MACH/GBR restoration",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)
        return fail(index,"actual natural continuation and stock SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    frame_set(expected_frame,140,context.gbr);frame_set(expected_frame,144,context.macl);
    frame_set(expected_frame,148,out.continuation);frame_set(expected_frame,152,context.r[14]);
    frame_set(expected_frame,156,context.r[13]);
    if(!test->count || test->normal)frame_set(expected_frame,136,test->count?context.macl:test->product);
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete helper frame and neighbors",i,expected_frame[i]);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    set16(expected_bytes+(COUNT&65535U),test->count);
    expected_bytes[REMAINDER&65535U]=(uint8_t)test->remainder;
    if(!test->count){set16(expected_bytes+(OUTPUT&65535U),test->quotient);expected_bytes[SCRATCH&65535U]=(uint8_t)test->scratch;}
    for(i=0;i<RAM_WORDS;++i){
        uint32_t actual=((volatile uint32_t *)(uintptr_t)RAM_BASE)[i];
        if(actual!=ram_expected[i])return fail(index,"all 65536 RAM bytes, exact destinations and sources",4U*i,ram_expected[i]);
    }
    for(i=0;i<16U;++i){
        uint8_t expected=i==8U?((uint8_t)test->flag|128U):alias_before[i];
        uint8_t actual=((volatile uint8_t *)(uintptr_t)(WORD_ALIAS-8U))[i];
        if(actual!=expected)return fail(index,"complete low RAM alias and neighbors",actual,expected);
    }
    memcpy(io_expected,io_before,sizeof(io_expected));
    set16(io_expected+12U,test->expected_compare);set16(io_expected+38U,test->expected_status);
    set16(io_expected+42U,test->expected_control);
    for(i=0;i<52U;++i){
        uint8_t actual=((volatile uint8_t *)(uintptr_t)(REGISTER_ALIAS-8U))[i];
        if(actual!=io_expected[i])return fail(index,"all declared register bytes and neighbors",i,io_expected[i]);
    }
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all bound ROM inputs and pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(ARRAY_SIZE(full_programmer_cases)!=FULL_PROGRAMMER_CASE_COUNT || !initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i){
        uint32_t index=EARLY_ONLY?full_programmer_early_indices[i]:i;
        if(!run_case(index,full_programmer_cases+index))return 1;
    }
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
