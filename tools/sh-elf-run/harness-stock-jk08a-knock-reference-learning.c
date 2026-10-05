/* RAM-only weighted reference learning with natural stock returns. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "stock-jk08a-knock-reference-learning-cases.h"

#define RAM_BASE 0x01000000U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))

struct context { uint32_t r[15], gbr, mach, macl; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[80], frame_after[80];
};
extern void stock_invoke_knock_reference_learning(uint32_t entry,
    const struct context *context, struct observation *observation);

static uint8_t ram_before[65536], calibration_before[40];
static unsigned long completed;
static const uint32_t abi_expected[10] = {
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,
    0x10203040U,0x50607080U
};
static const struct { uint32_t address,size; } calibrations[] = {
    {0x884bU,1},{0x8b3dU,1},{0x9282U,2},{0x25f10U,4},
    {0x4a1fcU,4},{0x4a200U,4},{0x4a208U,4},{0x4a224U,4},
    {0x4a228U,4},{0x4a22cU,4},{0x4a230U,4},{0x4a234U,4}
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
    fprintf(stderr,"%s[%lu] %s actual=%08lx expected=%08lx\n",
            scope,index,field,(unsigned long)actual,(unsigned long)expected);
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
    static const struct { uint32_t at,value; } pools[] = {
        {0x25f10U,0x01005718U},{0x4a1fcU,0x8b3dU},
        {0x4a200U,0x01001ff4U},{0x4a208U,0x010011d4U},
        {0x4a224U,0x25e20U},{0x4a228U,0x9282U},
        {0x4a22cU,0x01002178U},{0x4a230U,0x884bU},
        {0x4a234U,0x010020c2U}
    };
    if (*(volatile uint8_t *)SELECTOR!=0x82U ||
        *(volatile uint8_t *)WEIGHT!=224U ||
        *(volatile uint16_t *)RESET_WORD!=0xffffU)
        return fail("initial",0,"factory selector/weight/reset",1,0);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        if(*(volatile uint32_t *)pools[i].at!=pools[i].value)
            return fail("initial",i,"bound pool/declared RAM alias",
                        *(volatile uint32_t *)pools[i].at,pools[i].value);
    return 1;
}

static void seed_and_snapshot(unsigned long index,const struct reference_case *test)
{
    unsigned i,j,at=0;
    uint32_t selected=REFERENCES+16U*(test->channel-1U);
    for(i=0;i<65536U;++i)
        ((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*29U+(i>>8)+index);
    for(i=0;i<48U;++i)
        set_word(REFERENCES+2U*i,(uint16_t)(0x9187U+i*0x1d35U+index*17U));
    for(i=0;i<8U;++i){
        set_word(SAMPLES+2U*i,test->sample[i]);
        set_word(selected+2U*i,test->old[i]);
    }
    *ram(PRIMARY)=(test->selector&8U)?(uint8_t)(7U-test->channel):test->channel;
    *ram(ALTERNATE)=(test->selector&8U)?test->channel:(uint8_t)(7U-test->channel);
    *ram(0xffff5aa0U)=test->first;
    *ram(0xffff5ad6U)=test->second;
    if(test->direct && (test->raw_id&0xffffU)!=0xffffU)
        *ram(DIAGNOSTICS+3U*(test->raw_id&0xffffU)+1U)=test->record;
    *(volatile uint8_t *)SELECTOR=test->selector;
    *(volatile uint8_t *)WEIGHT=test->weight;
    *(volatile uint16_t *)RESET_WORD=test->reset;
    for(i=0;i<65536U;++i)
        ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j)
            calibration_before[at++]=((volatile uint8_t *)calibrations[i].address)[j];
}

static struct context new_context(const struct reference_case *test)
{
    struct context context;
    unsigned i;
    for(i=0;i<15U;++i)context.r[i]=0x28765430U+i*0x01030507U;
    context.r[7]=test->direct?PREDICATE_ENTRY:REGION_ENTRY;
    if(test->direct)context.r[4]=test->raw_id;
    context.gbr=0x456789abU;
    context.mach=0x13579bdfU;
    context.macl=0x2468ace0U;
    return context;
}

static int preserve(const char *scope,unsigned long index,const struct reference_case *test)
{
    unsigned i,j,at=0;
    uint32_t first=0x2178U,last=first+96U;
    if(!test->forced){first+=16U*(test->channel-1U);last=first+16U;}
    for(i=0;i<65536U;++i){
        if(!test->direct && i>=first && i<last)continue;
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_before[i])
            return fail(scope,index,"full RAM/input/sibling preservation",
                        ((volatile uint8_t *)RAM_BASE)[i],ram_before[i]);
    }
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j,++at)
            if(((volatile uint8_t *)calibrations[i].address)[j]!=calibration_before[at])
                return fail(scope,index,"calibration/pool preservation",
                            ((volatile uint8_t *)calibrations[i].address)[j],calibration_before[at]);
    return 1;
}

static int run_case(unsigned long index,const struct reference_case *test)
{
    const char *scope=test->direct?"direct-real-predicate":
        test->forced?"natural-forced-bank-reset":"natural-weighted-learning";
    struct context context=new_context(test),before=context;
    struct observation out;
    unsigned i;
    uint32_t first=REFERENCES+16U*(test->channel-1U);
    seed_and_snapshot(index,test);
    memset(&out,0xa6,sizeof(out));
    stock_invoke_knock_reference_learning(context.r[7],&context,&out);
    if(memcmp(&context,&before,sizeof(before)))
        return fail(scope,index,"entry context preservation",1,0);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=test->expected[i])
            return fail(scope,index,"literal natural exit register",reg(&out,i),test->expected[i]);
    if((out.exit[0]&1U)!=test->expected_t)
        return fail(scope,index,"literal SR.T",out.exit[0]&1U,test->expected_t);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach || out.exit[4]!=context.gbr)
        return fail(scope,index,"natural MACL/MACH/GBR preservation",1,0);
    if(out.sp!=out.abi_before[10]-164U)
        return fail(scope,index,"natural SP preservation",out.sp,out.abi_before[10]-164U);
    if(out.exit[1]!=out.continuation)
        return fail(scope,index,"natural PR return",out.exit[1],out.continuation);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))
        return fail(scope,index,"distinct C caller ABI restoration",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])
            return fail(scope,index,"C caller ABI sentinel",out.abi_before[i],abi_expected[i]);
    if(!test->direct){
        if(test->forced){
            for(i=0;i<48U;++i)
                if(get_word(REFERENCES+2U*i)!=test->reset)
                    return fail(scope,index,"all 48 literal reset words",get_word(REFERENCES+2U*i),test->reset);
        }else{
            for(i=0;i<8U;++i)
                if(get_word(first+2U*i)!=test->expected_words[i])
                    return fail(scope,index,"all eight literal learned words",get_word(first+2U*i),test->expected_words[i]);
        }
        for(i=0;i<7U;++i)
            if(frame_word(out.frame_after,44U-4U*i)!=context.r[8U+i])
                return fail(scope,index,"natural saved R8..R14 frame",
                            frame_word(out.frame_after,44U-4U*i),context.r[8U+i]);
        if(frame_word(out.frame_after,16)!=out.continuation ||
           frame_word(out.frame_after,12)!=context.macl)
            return fail(scope,index,"natural saved PR/MACL frame",1,0);
    }
    for(i=0;i<80U;++i)
        if((test->direct || i<12U || i>=48U) &&
           out.frame_before[i]!=out.frame_after[i])
            return fail(scope,index,"stack/local neighbor preservation",out.frame_after[i],out.frame_before[i]);
    if(frame_word(out.frame_before,72)!=out.continuation ||
       frame_word(out.frame_after,72)!=out.continuation)
        return fail(scope,index,"independent local continuation preservation",1,0);
    if(!preserve(scope,index,test))return 0;
    ++completed;
    return 1;
}

int main(void)
{
    unsigned long i;
    if(!verify_initial_calibration())return 1;
    for(i=0;i<ARRAY_SIZE(reference_cases);++i)
        if(!run_case(i,&reference_cases[i]))return 1;
    if(completed!=KNOCK_REFERENCE_LEARNING_CASE_COUNT)
        return !fail("total",0,"literal case count",completed,KNOCK_REFERENCE_LEARNING_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-knock-reference-learning cases=%lu\n",completed);
    return 0;
}
