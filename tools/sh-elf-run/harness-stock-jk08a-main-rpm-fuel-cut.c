/* Complete bounded raw main-RPM state and natural CPU/frame observation. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "main-rpm-fuel-cut-cases.h"

#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif

#if !defined(REGION_KEY) || !defined(REGION_ENTRY) || !defined(FUEL_INHIBIT) \
    || !defined(ENGINE_SPEED) || !defined(PAIR_SELECTOR) || !defined(DELAY_COUNTER)
#error "The primary verifier defines the entry and owned software cells."
#endif

struct context { uint32_t r[15],gbr,mach,macl,sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[80],frame_after[80];
    uint32_t sr_before,prepared_r3,observed_context,observed_word;
    uint32_t original_sr,context_before_ldc,word_before_ldc;
};
extern void stock_invoke_main_rpm_fuel_cut(uint32_t entry,
    const struct context *context,struct observation *observation);

static uint8_t ram_before[65536],rom_before[34];
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,
    0x10203040U,0x50607080U
};
static const struct { uint32_t address,size; } bound_data[]={
    {0x4f460U,20},{0x8b38U,1},{0x8c69U,1},{0x934eU,12}
};

static volatile uint8_t *ram(uint32_t address)
{ return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&0xffffU)); }

static uint32_t reg(const struct observation *out,unsigned n)
{ return out->exit[19U-n]; }

static uint32_t frame_word(const uint8_t *p,unsigned at)
{
    return (uint32_t)p[at]<<24 | (uint32_t)p[at+1]<<16 |
           (uint32_t)p[at+2]<<8 | p[at+3];
}

static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected)
{
    fprintf(stderr,"main-rpm[%lu] %s actual=%08lx expected=%08lx\n",index,field,
        (unsigned long)actual,(unsigned long)expected);
    return 0;
}

static void set_word(uint32_t address,uint16_t value)
{
    volatile uint8_t *p=ram(address);
    p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;
}

static int initial_contract(void)
{
    unsigned i;
    static const uint16_t table[]={612,596,596,368,0,0};
    static const uint32_t pools[]={0x0100244cU,0x8b38U,0x934eU,0x0100119cU,0x8c69U};
    if(REGION_ENTRY!=0x4f282U || FUEL_INHIBIT!=0xffff2497U ||
       ENGINE_SPEED!=0xffff11bcU || PAIR_SELECTOR!=0xffff2468U || DELAY_COUNTER!=0xffff24f1U)
        return fail(0,"owned entry and operands",1,0);
    if(*(volatile uint8_t *)(uintptr_t)0x8b38U!=0x63U ||
       *(volatile uint8_t *)(uintptr_t)0x8c69U!=0)
        return fail(0,"stock configuration and delay",1,0);
    for(i=0;i<ARRAY_SIZE(table);++i)
        if(((volatile uint16_t *)(uintptr_t)0x934eU)[i]!=table[i])
            return fail(i,"all six stock threshold words",
                ((volatile uint16_t *)(uintptr_t)0x934eU)[i],table[i]);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        if(((volatile uint32_t *)(uintptr_t)0x4f460U)[i]!=pools[i])
            return fail(i,"five pools and two declared RAM translations",
                ((volatile uint32_t *)(uintptr_t)0x4f460U)[i],pools[i]);
    return 1;
}

static void seed(unsigned long index,const struct main_rpm_case *test)
{
    unsigned i,j,at=0;
    for(i=0;i<65536U;++i)
        ((volatile uint8_t *)(uintptr_t)RAM_BASE)[i]=(uint8_t)(0x5dU+i*29U+(i>>8)+index);
    ram(FUEL_INHIBIT)[0]=(uint8_t)test->flags;
    ram(PAIR_SELECTOR)[0]=(uint8_t)test->selector;
    ram(DELAY_COUNTER)[0]=(uint8_t)test->counter;
    set_word(ENGINE_SPEED,(uint16_t)test->speed);
    for(i=0;i<65536U;++i)
        ram_before[i]=((volatile uint8_t *)(uintptr_t)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(bound_data);++i)
        for(j=0;j<bound_data[i].size;++j)
            rom_before[at++]=((volatile uint8_t *)(uintptr_t)bound_data[i].address)[j];
}

static int preservation(unsigned long index,const struct main_rpm_case *test)
{
    unsigned i,j,at=0;
    if(ram(FUEL_INHIBIT)[0]!=test->expected_flags)
        return fail(index,"raw flags",ram(FUEL_INHIBIT)[0],test->expected_flags);
    if(ram(DELAY_COUNTER)[0]!=test->expected_counter)
        return fail(index,"raw delay counter",ram(DELAY_COUNTER)[0],test->expected_counter);
    for(i=0;i<65536U;++i){
        if(i==(FUEL_INHIBIT&0xffffU) || i==(DELAY_COUNTER&0xffffU))continue;
        if(((volatile uint8_t *)(uintptr_t)RAM_BASE)[i]!=ram_before[i])
            return fail(index,"complete RAM and neighboring-cell preservation",
                ((volatile uint8_t *)(uintptr_t)RAM_BASE)[i],ram_before[i]);
    }
    for(i=0;i<ARRAY_SIZE(bound_data);++i)
        for(j=0;j<bound_data[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)bound_data[i].address)[j]!=rom_before[at])
                return fail(index,"all34 pool/configuration/threshold bytes preserved",
                    ((volatile uint8_t *)(uintptr_t)bound_data[i].address)[j],rom_before[at]);
    return 1;
}

static int run_case(unsigned long index,const struct main_rpm_case *test)
{
    struct context context,before;
    struct observation out;
    unsigned i;
    memcpy(context.r,test->incoming,sizeof(context.r));
    context.gbr=test->gbr;context.mach=test->mach;context.macl=test->macl;context.sr=test->sr;
    before=context;
    if(context.r[7]!=REGION_ENTRY)return fail(index,"declared driver R7 target",context.r[7],REGION_ENTRY);
    seed(index,test);
    memset(&out,0xa6,sizeof(out));
    stock_invoke_main_rpm_fuel_cut(REGION_ENTRY,&context,&out);
    if(out.observed_context!=(uint32_t)(uintptr_t)&context || out.observed_word!=before.r[3])
        return fail(index,"independent incoming context after status preparation",1,0);
    if(out.prepared_r3!=before.r[3])
        return fail(index,"independently observed prepared R3",out.prepared_r3,before.r[3]);
    if(memcmp(&context,&before,sizeof(before)))return fail(index,"entry context preservation",1,0);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=test->expected[i]){
            fprintf(stderr,"first GPR mismatch R%u flags=%02lx counter=%02lx speed=%04lx selector=%02lx\n",
                i,(unsigned long)test->flags,(unsigned long)test->counter,
                (unsigned long)test->speed,(unsigned long)test->selector);
            return fail(index,"complete literal GPR result",reg(&out,i),test->expected[i]);
        }
    if(out.context_before_ldc!=(uint32_t)(uintptr_t)&context || out.word_before_ldc!=before.r[3])
        return fail(index,"independent incoming context before status preparation",1,0);
    if(out.sr_before!=((out.original_sr&~0x3f1U)|test->sr))
        return fail(index,"all declared SR controls and retained original status",out.sr_before,
            (out.original_sr&~0x3f1U)|test->sr);
    if(out.exit[0]!=((out.original_sr&~0x3f1U)|test->expected_sr))
        return fail(index,"complete exit SR/MQT",out.exit[0],
            (out.original_sr&~0x3f1U)|test->expected_sr);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(index,"natural MACL/MACH/GBR preservation",1,0);
    if(out.sp!=out.abi_before[10]-164U)
        return fail(index,"natural SP restoration",out.sp,out.abi_before[10]-164U);
    if(out.exit[1]!=out.continuation)
        return fail(index,"natural PR return",out.exit[1],out.continuation);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))
        return fail(index,"distinct C caller ABI restoration",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])
            return fail(index,"C caller ABI sentinel",out.abi_before[i],abi_expected[i]);
    if(frame_word(out.frame_after,44)!=context.gbr)
        return fail(index,"exact four-byte saved GBR",frame_word(out.frame_after,44),context.gbr);
    for(i=0;i<80U;++i)
        if((i<44U || i>=48U) && out.frame_before[i]!=out.frame_after[i])
            return fail(index,"SP-48..SP+31 frame and neighbor preservation",
                out.frame_after[i],out.frame_before[i]);
    if(frame_word(out.frame_before,72)!=out.continuation ||
       frame_word(out.frame_after,72)!=out.continuation)
        return fail(index,"independent local continuation",1,0);
    return preservation(index,test);
}

int main(void)
{
    unsigned long index;
    unsigned long limit=EARLY_ONLY?MAIN_RPM_EARLY_COUNT:MAIN_RPM_CASE_COUNT;
    if(!initial_contract())return 1;
    for(index=0;index<limit;++index)
        if(!run_case(index,&main_rpm_cases[index]))return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,limit);
    return 0;
}
