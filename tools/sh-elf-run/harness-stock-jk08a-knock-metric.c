/* Exact stock post-acquisition arithmetic with complete scoped preservation. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "stock-jk08a-knock-metric-cases.h"
#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&0xffffU))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[112],frame_after[112];
    uint32_t sr_before;
};
extern void stock_invoke_knock_metric(uint32_t entry,const struct context *,struct observation *);
static uint8_t ram_before[65536],calibration_before[150];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } calibrations[]={
    {0x49fc0U,60},{0x4a4c8U,4},{0x4a4ccU,4},{0x4a4d0U,4},
    {0x4a4d8U,4},{0x4a4dcU,4},{0x4a4e0U,4},{0x2219cU,32},{0x221d8U,8},
    {0x4a24cU,12},{0x4a296U,2},{0x4a29cU,2},{0x4a3daU,2},{0x4a3e0U,2},
    {0x8618U,1},{0x8870U,1},{0x8b3dU,1},{0x86a7U,1},{0x8694U,1},{0x86acU,1}
};
static volatile uint8_t *ram(uint32_t a){return (volatile uint8_t *)ALIAS(a);}
static uint32_t reg(const struct observation *o,unsigned n){return o->exit[19U-n];}
static uint32_t word(const uint8_t *p,unsigned at){
    return (uint32_t)p[at]<<24|(uint32_t)p[at+1]<<16|(uint32_t)p[at+2]<<8|p[at+3];
}
static void frame_set(uint8_t *p,unsigned at,uint32_t v){
    p[at]=(uint8_t)(v>>24);p[at+1]=(uint8_t)(v>>16);p[at+2]=(uint8_t)(v>>8);p[at+3]=(uint8_t)v;
}
static void set16(uint32_t a,uint16_t v){volatile uint8_t *p=ram(a);p[0]=(uint8_t)(v>>8);p[1]=(uint8_t)v;}
static void set32(uint32_t a,uint32_t v){
    volatile uint8_t *p=ram(a);p[0]=(uint8_t)(v>>24);p[1]=(uint8_t)(v>>16);p[2]=(uint8_t)(v>>8);p[3]=(uint8_t)v;
}
static uint32_t get32(uint32_t a){
    volatile uint8_t *p=ram(a);return (uint32_t)p[0]<<24|(uint32_t)p[1]<<16|(uint32_t)p[2]<<8|p[3];
}
static int fail(unsigned long i,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"metric[%lu] %s actual=%08lx expected=%08lx\n",i,field,(unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;
    static const struct { uint32_t at,v; } pools[]={
        {0x49fd0U,0x01001ff4U},{0x49fd4U,0x01002274U},{0x49fd8U,0x01002158U},{0x49fdcU,0x010011d4U},
        {0x49ff0U,0x010021f8U},{0x49ff4U,0x010021d8U},{0x4a4ccU,0x010011d4U},{0x4a4d0U,0x01001ff4U},
        {0x4a4d8U,0x010020c2U},{0x4a4dcU,0x01002178U},{0x4a4e0U,0x01002158U}
    };
    if(*(volatile uint8_t *)0x8618U!=0 || *(volatile uint8_t *)0x8870U!=3 ||
       *(volatile uint8_t *)0x8b3dU!=0x82U || *(volatile uint8_t *)0x86a7U!=128 ||
       *(volatile uint8_t *)0x8694U!=128 || *(volatile uint8_t *)0x86acU!=128)
        return fail(0,"factory calibration",1,0);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        if(*(volatile uint32_t *)pools[i].at!=pools[i].v)
            return fail(i,"declared RAM alias",*(volatile uint32_t *)pools[i].at,pools[i].v);
    return 1;
}
static void seed(unsigned long index,const struct metric_case *t){
    unsigned i,j,at=0;
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*29U+(i>>8)+index);
    for(i=0;i<48U;++i)set16(0xffff2178U+2U*i,(uint16_t)(0x9187U+i*0x1d35U+index*17U));
    for(i=0;i<8U;++i){
        set16(0xffff20c2U+2U*i,t->sample[i]);
        set16(0xffff2178U+16U*(t->channel-1U)+2U*i,t->reference[i]);
        set32(0xffff2158U+4U*i,t->scope==0?0xb17c9283U+i*0x03150709U:t->difference[i]);
    }
    set32(0xffff2274U+4U*(t->channel-1U),t->scope==2?t->sum:0x456789abU);
    *ram(0xffff11deU)=(t->selector&8U)?(uint8_t)(7U-t->channel):t->channel;
    *ram(0xffff2143U)=(t->selector&8U)?t->channel:(uint8_t)(7U-t->channel);
    *(volatile uint8_t *)0x8618U=t->mask;
    *(volatile uint8_t *)0x8870U=t->count;
    *(volatile uint8_t *)0x8b3dU=t->selector;
    *(volatile uint8_t *)0x86a7U=t->gain[0];
    *(volatile uint8_t *)0x8694U=t->gain[1];
    *(volatile uint8_t *)0x86acU=t->gain[2];
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j)
            calibration_before[at++]=((volatile uint8_t *)calibrations[i].at)[j];
}
static struct context make_context(const struct metric_case *t){
    struct context c;unsigned i;
    for(i=0;i<15U;++i)c.r[i]=0x28765430U+i*0x01030507U;
    c.r[7]=t->scope==0?REGION_ENTRY:t->scope==1?TOP_THREE_ENTRY:SCALER_ENTRY;
    if(t->scope==0)c.r[11]=(t->selector&8U)?8U:0U;
    c.gbr=0x456789abU;c.mach=0x13579bdfU;c.macl=0x2468ace0U;
    c.sr=(uint32_t)(completed&1U);
    return c;
}
static int writable(unsigned i,const struct metric_case *t){
    uint32_t at=t->channel-1U;
    if(t->scope==0 && i>=0x2158U && i<0x2178U)return 1;
    if(t->scope!=2 && i>=0x2274U+4U*at && i<0x2278U+4U*at)return 1;
    if(t->scope!=1 && ((i>=0x21f8U+4U*at && i<0x21fcU+4U*at) ||
                      (i>=0x21d8U+4U*at && i<0x21dcU+4U*at)))return 1;
    return 0;
}
static int preservation(unsigned long index,const struct metric_case *t){
    unsigned i,j,at=0;
    for(i=0;i<65536U;++i)
        if(!writable(i,t) && ((volatile uint8_t *)RAM_BASE)[i]!=ram_before[i])
            return fail(index,"full RAM/input/sibling preservation",i,ram_before[i]);
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j,++at)
            if(((volatile uint8_t *)calibrations[i].at)[j]!=calibration_before[at])
                return fail(index,"all calibration/pool/static-anchor preservation",
                    ((volatile uint8_t *)calibrations[i].at)[j],calibration_before[at]);
    return 1;
}
static int run_case(unsigned long index,const struct metric_case *t){
    struct context c=make_context(t),before=c;
    struct observation out;
    uint8_t expected_frame[112];unsigned i;
    seed(index,t);memset(&out,0xa6,sizeof(out));
    stock_invoke_knock_metric(c.r[7],&c,&out);
    if(memcmp(&c,&before,sizeof(c)))return fail(index,"entry context preservation",1,0);
    for(i=0;i<15U;++i){
        uint32_t expected=t->expected[i];
        if(t->scope==0 && i==1)expected=out.continuation;
        if(reg(&out,i)!=expected)return fail(index,"literal full GPR vector",reg(&out,i),expected);
    }
    if((out.sr_before&0x301U)!=c.sr)
        return fail(index,"prepared full SR and independent T",out.sr_before&0x301U,c.sr);
    if(out.exit[0]!=((out.sr_before&~1U)|t->expected_t))
        return fail(index,"literal full SR with retained mode bits",out.exit[0],(out.sr_before&~1U)|t->expected_t);
    if(out.exit[2]!=c.macl || out.exit[3]!=c.mach || out.exit[4]!=c.gbr)
        return fail(index,"stock MACL/MACH/GBR preservation",1,0);
    if(out.sp!=out.abi_before[10]-164U)return fail(index,"stock SP",out.sp,out.abi_before[10]-164U);
    if(out.exit[1]!=out.continuation)return fail(index,"natural/direct or external-boundary PR",out.exit[1],out.continuation);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"distinct C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    if(t->scope==0)
        for(i=0;i<8U;++i)
            if(get32(0xffff2158U+4U*i)!=t->difference[i])
                return fail(index,"all eight literal word differences",get32(0xffff2158U+4U*i),t->difference[i]);
    if(t->scope!=2 && get32(0xffff2274U+4U*(t->channel-1U))!=t->sum)
        return fail(index,"literal selected sum",get32(0xffff2274U+4U*(t->channel-1U)),t->sum);
    if(t->scope!=1){
        if(get32(0xffff21f8U+4U*(t->channel-1U))!=t->metric)
            return fail(index,"literal signed metric",get32(0xffff21f8U+4U*(t->channel-1U)),t->metric);
        if(get32(0xffff21d8U+4U*(t->channel-1U))!=t->biased)
            return fail(index,"literal offset-binary metric",get32(0xffff21d8U+4U*(t->channel-1U)),t->biased);
    }
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    if(t->scope!=2){
        for(i=0;i<8U;++i)frame_set(expected_frame,16U+4U*i,t->sorted[i]);
        frame_set(expected_frame,12,(t->mask&64U)?0x80000000U:t->difference[6]);
        for(i=0;i<7U;++i)frame_set(expected_frame,76U-4U*i,c.r[8U+i]);
        frame_set(expected_frame,48,t->scope==0?0x4a2eaU:out.continuation);
        if(t->scope==0)frame_set(expected_frame,52,ALIAS(0xffff2158U)+32U);
    }
    if(t->scope!=1){
        frame_set(expected_frame,72,c.macl);
        frame_set(expected_frame,76,t->scope==0?ALIAS(0xffff2158U)+32U:c.r[14]);
    }
    for(i=0;i<112U;++i)
        if(out.frame_after[i]!=expected_frame[i])
            return fail(index,"literal complete stack/local/neighbors",out.frame_after[i],expected_frame[i]);
    if(word(out.frame_before,80)!=ALIAS(0xffff20c2U) ||
       word(out.frame_before,104)!=out.continuation ||
       word(out.frame_after,104)!=out.continuation)
        return fail(index,"independent sample pointer/continuation frame",1,0);
    if(!preservation(index,t))return 0;
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(!initial())return 1;
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
    static const unsigned early_indices[]={0U,240U,6488U,6974U,7460U,7996U,7461U,7997U,1U,2U,3U,4U,5U,6U,7U,8U};
    if(EARLY_ONLY){
        for(i=0;i<ARRAY_SIZE(early_indices);++i)
            if(!run_case(early_indices[i],&metric_cases[early_indices[i]]))return 1;
    }else{
        for(i=0;i<ARRAY_SIZE(metric_cases);++i)if(!run_case(i,&metric_cases[i]))return 1;
    }
    if(completed!=(EARLY_ONLY?ARRAY_SIZE(early_indices):KNOCK_METRIC_CASE_COUNT))
        return !fail(0,"case count",completed,EARLY_ONLY?ARRAY_SIZE(early_indices):KNOCK_METRIC_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-knock-metric cases=%lu\n",completed);
    return 0;
}
