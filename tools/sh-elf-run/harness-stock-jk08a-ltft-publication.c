/* Complete LTFT publication with the real natural diagnostic predicate. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#include "stock-jk08a-ltft-publication-cases.h"

#define RAM_BASE 0x01000000U
#define DIAGNOSTIC (DIAGNOSTIC_RECORD + DIAGNOSTIC_BYTE1_OFFSET)
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))

struct context { uint32_t r[15],gbr,mach,macl,sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[80],frame_after[80];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete context layout");
_Static_assert(offsetof(struct context,sr)==72U,"independent incoming T offset");
_Static_assert(sizeof(struct observation)==348U,"complete observation layout");
_Static_assert(offsetof(struct observation,sp)==80U,"natural SP offset");
_Static_assert(offsetof(struct observation,continuation)==84U,"continuation offset");
_Static_assert(offsetof(struct observation,abi_before)==88U,"outer ABI before offset");
_Static_assert(offsetof(struct observation,abi_after)==136U,"outer ABI after offset");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before offset");
_Static_assert(offsetof(struct observation,frame_after)==264U,"frame after offset");
_Static_assert(offsetof(struct observation,sr_before)==344U,"prepared full SR offset");
extern void stock_invoke_ltft_publication(uint32_t entry,
    const struct context *context,struct observation *observation);

static uint8_t ram_before[65536],calibration_before[52];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,
    0x10203040U,0x50607080U
};
static const struct { uint32_t address,size; } calibrations[]={
    {0x8e5aU,1},{0x8e5bU,1},{0x25f10U,4},
    {0x57b7aU,2},{0x57b7cU,2},{0x57bc0U,4},{0x57bc4U,4},
    {0x57bc8U,4},{0x57bccU,4},{0x57bd0U,4},{0x57d1aU,2},
    {0x57e34U,4},{0x57e38U,4},{0x57e3cU,4},{0x57e40U,4},{0x57e44U,4}
};

static volatile uint8_t *ram(uint32_t address)
{ return (volatile uint8_t *)(RAM_BASE+(address&0xffffU)); }

static uint32_t reg(const struct observation *out,unsigned n)
{ return out->exit[19U-n]; }

static uint32_t frame_word(const uint8_t *p,unsigned at)
{
    return (uint32_t)p[at]<<24 | (uint32_t)p[at+1]<<16 |
           (uint32_t)p[at+2]<<8 | p[at+3];
}

static int fail(const char *scope,unsigned long index,const char *field,
                uint32_t actual,uint32_t expected)
{
    fprintf(stderr,"%s[%lu] %s actual=%08lx expected=%08lx\n",scope,index,field,
            (unsigned long)actual,(unsigned long)expected);
    return 0;
}

static void set_word(uint32_t address,uint16_t value)
{
    volatile uint8_t *p=ram(address);
    p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;
}

static uint16_t get_word(uint32_t address)
{
    volatile uint8_t *p=ram(address);
    return (uint16_t)((uint16_t)p[0]<<8|p[1]);
}

static int verify_initial_calibration(void)
{
    unsigned i;
    static const struct { uint32_t at,value; } pools[]={
        {0x25f10U,0x01005718U},{0x57bc0U,0x01002306U},
        {0x57bc4U,0x01005648U},{0x57bc8U,0x010022f8U},
        {0x57bccU,0x0100128cU},{0x57bd0U,0x8e5bU},
        {0x57e34U,0x8e5aU},{0x57e38U,0x25e20U},
        {0x57e3cU,0x010041a9U},{0x57e40U,0x01002470U},{0x57e44U,0x01002302U}
    };
    if(*(volatile uint8_t *)LOWER!=90U || *(volatile uint8_t *)UPPER!=110U ||
       *(volatile uint16_t *)0x57b7aU!=0x370U || *(volatile uint16_t *)0x57b7cU!=0x372U ||
       *(volatile uint16_t *)0x57d1aU!=0x129U)
        return fail("initial",0,"factory bounds and unchanged word operands",1,0);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        if(*(volatile uint32_t *)pools[i].at!=pools[i].value)
            return fail("initial",i,"eight aliases and unchanged ROM/helper pointers",
                        *(volatile uint32_t *)pools[i].at,pools[i].value);
    return 1;
}

static void seed_pair(uint32_t first,unsigned bank,uint16_t selected)
{
    set_word(first+2U*bank,selected);
    set_word(first+2U*(1U-bank),(uint16_t)(selected^0x5aa5U));
}

static void seed_and_snapshot(unsigned long index,const struct ltft_publication_case *test)
{
    unsigned i,j,at=0,bank=test->raw_r4&0xffU;
    for(i=0;i<65536U;++i)
        ((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*29U+(i>>8)+index);
    seed_pair(SELECTED,bank,test->l);
    seed_pair(ADJUSTMENT,bank,test->a);
    seed_pair(OUTPUT,bank,(uint16_t)(test->output^0xa55aU));
    set_word(COMPARE_U,test->u);
    set_word(COMPARE_V,(uint16_t)test->v);
    *ram(MASK)=test->mask;
    *ram(DIAGNOSTIC)=test->diagnostic;
    *ram(CONTROL_F)=test->f;
    *ram(CONTROL_G)=test->g;
    *ram(CONTROL_H)=test->h;
    *ram(CONTROL_K)=test->k;
    *(volatile uint8_t *)LOWER=test->lower;
    *(volatile uint8_t *)UPPER=test->upper;
    for(i=0;i<65536U;++i)
        ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j)
            calibration_before[at++]=((volatile uint8_t *)calibrations[i].address)[j];
}

static struct context new_context(const struct ltft_publication_case *test)
{
    struct context context;
    unsigned i;
    for(i=0;i<15U;++i)
        context.r[i]=0x28765430U+i*0x01030507U+test->variant*0x00102040U;
    context.r[4]=test->raw_r4;
    context.r[7]=REGION_ENTRY;
    context.gbr=0x456789abU^test->variant*0x10203040U;
    context.mach=0x13579bdfU^test->variant*0x01234567U;
    context.macl=0x2468ace0U^test->variant*0x76543210U;
    context.sr=test->initial_t;
    return context;
}

static int preserve(const char *scope,unsigned long index,const struct ltft_publication_case *test)
{
    unsigned i,j,at=0;
    uint32_t first=0x2302U+2U*(test->raw_r4&0xffU);
    for(i=0;i<65536U;++i){
        if(i>=first && i<first+2U)continue;
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_before[i])
            return fail(scope,index,"full RAM/input/other bank/diagnostic neighbor preservation",
                        ((volatile uint8_t *)RAM_BASE)[i],ram_before[i]);
    }
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j,++at)
            if(((volatile uint8_t *)calibrations[i].address)[j]!=calibration_before[at])
                return fail(scope,index,"all52 calibration/pool bytes preserved",
                            ((volatile uint8_t *)calibrations[i].address)[j],calibration_before[at]);
    return 1;
}

static int run_case(unsigned long index,const struct ltft_publication_case *test)
{
    const char *scope=ltft_publication_groups[test->group];
    struct context context=new_context(test),before=context;
    struct observation out;
    unsigned i;
    uint32_t address=OUTPUT+2U*(test->raw_r4&0xffU);
    seed_and_snapshot(index,test);
    memset(&out,0xa6,sizeof(out));
    stock_invoke_ltft_publication(REGION_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(before)))
        return fail(scope,index,"entry context preservation",1,0);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=test->expected[i]){
            unsigned j;
            fprintf(stderr,"first mismatch register R%u\n",i);
            for(j=0;j<15U;++j)
                fprintf(stderr,"R%u incoming=%08lx captured=%08lx literal=%08lx\n",j,
                    (unsigned long)context.r[j],(unsigned long)reg(&out,j),
                    (unsigned long)test->expected[j]);
            fprintf(stderr,"L=%u A=%u U=%u V=%d mask=%02x diagnostic=%02x F/G/H/K=%02x/%02x/%02x/%02x bounds=%u/%u output=%u\n",
                test->l,test->a,test->u,test->v,test->mask,test->diagnostic,
                test->f,test->g,test->h,test->k,test->lower,test->upper,test->output);
            return fail(scope,index,"literal natural exit GPR",reg(&out,i),test->expected[i]);
        }
    if((out.sr_before&1U)!=test->initial_t)
        return fail(scope,index,"independent incoming T",out.sr_before&1U,test->initial_t);
    if(out.exit[0]!=((out.sr_before&~1U)|test->expected_t))
        return fail(scope,index,"full SR nonT preservation and literal terminal T",out.exit[0],
                    (out.sr_before&~1U)|test->expected_t);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(scope,index,"natural MACL/MACH/GBR preservation",1,0);
    if(out.sp!=out.abi_before[10]-164U)
        return fail(scope,index,"natural SP restoration",out.sp,out.abi_before[10]-164U);
    if(out.exit[1]!=out.continuation)
        return fail(scope,index,"natural PR return",out.exit[1],out.continuation);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))
        return fail(scope,index,"distinct C caller ABI restoration",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])
            return fail(scope,index,"C caller ABI sentinel",out.abi_before[i],abi_expected[i]);
    if(get_word(address)!=test->output)
        return fail(scope,index,"literal selected-bank output bytes",get_word(address),test->output);
    if(frame_word(out.frame_after,44)!=context.r[13] ||
       frame_word(out.frame_after,40)!=context.r[14] ||
       frame_word(out.frame_after,36)!=out.continuation)
        return fail(scope,index,"exact12-byte saved R13/R14/PR frame",1,0);
    for(i=0;i<80U;++i)
        if((i<36U || i>=48U) && out.frame_before[i]!=out.frame_after[i])
            return fail(scope,index,"SP-48..SP+31 neighbor preservation",
                        out.frame_after[i],out.frame_before[i]);
    if(frame_word(out.frame_before,72)!=out.continuation ||
       frame_word(out.frame_after,72)!=out.continuation)
        return fail(scope,index,"independent local continuation",1,0);
    if(!preserve(scope,index,test))return 0;
    ++completed;
    return 1;
}

int main(void)
{
    unsigned long i;
    if(!verify_initial_calibration())return 1;
    for(i=0;i<ARRAY_SIZE(ltft_publication_cases);++i)
        if(!run_case(i,&ltft_publication_cases[i]))return 1;
    if(completed!=LTFT_PUBLICATION_CASE_COUNT)
        return !fail("total",0,"literal case count",completed,LTFT_PUBLICATION_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-ltft-publication cases=%lu\n",completed);
    return 0;
}
