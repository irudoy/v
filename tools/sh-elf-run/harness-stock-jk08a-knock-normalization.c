/* Exact software-bin normalization with complete literal and preservation scopes. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "stock-jk08a-knock-normalization-cases.h"
#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&0xffffU))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_t; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[64],frame_after[64];
    uint32_t sr_before;
};
extern void stock_invoke_knock_normalization(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[65536],calibration_before[99];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } calibrations[]={
    {0x4a4ccU,4},{0x4a4d0U,4},{0x4a4d4U,4},{0x4a4d8U,4},{0x4a4f4U,4},{0x4a4f8U,4},
    {0x4a590U,4},{0x4a594U,4},{0x4a598U,4},{0x4a59cU,4},{0x4a5a0U,4},{0x4a5a4U,4},{0x4a5a8U,4},
    {0x4a24cU,12},{0x4a25cU,14},{0x4a3a0U,16},{0x4a4c8U,4},{0x8b3dU,1}
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
static uint16_t get16(uint32_t a){volatile uint8_t *p=ram(a);return (uint16_t)((uint16_t)p[0]<<8|p[1]);}
static int fail(unsigned long i,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"normalization[%lu] %s actual=%08lx expected=%08lx\n",i,field,(unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;
    static const struct { uint32_t at,v; } pools[]={
        {0x4a4ccU,0x010011d4U},{0x4a4d0U,0x01001ff4U},{0x4a4d4U,0x010020d2U},{0x4a4d8U,0x010020c2U},
        {0x4a4f4U,0x01002132U},{0x4a590U,0x010087e1U},{0x4a594U,0x010020d2U},{0x4a598U,0x01001ff4U},
        {0x4a59cU,0x010020c2U},{0x4a5a0U,0x01002132U},{0x4a5a8U,0x010011d4U},
        {0x4a4f8U,0x21ce0U},{0x4a5a4U,0x21ce0U}
    };
    if(*(volatile uint8_t *)0x8b3dU!=0x82U)return fail(0,"factory selector",*(volatile uint8_t *)0x8b3dU,0x82U);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        if(*(volatile uint32_t *)pools[i].at!=pools[i].v)
            return fail(i,"bound stock pointer/declared RAM alias",*(volatile uint32_t *)pools[i].at,pools[i].v);
    return 1;
}
static void seed(unsigned long index,const struct normalization_case *t){
    unsigned i,j,at=0;
    uint32_t selected=0xffff20d2U+16U*(t->channel-1U);
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*29U+(i>>8)+index);
    for(i=0;i<8U;++i){
        set16(0xffff2132U+2U*i,t->bin[i]);
        set16(0xffff20c2U+2U*i,(uint16_t)(0xb17cU+i*0x1537U));
        set16(selected+2U*i,(uint16_t)(0xca53U+i*0x2715U));
    }
    set16(0xffff2152U,t->multiplier);
    *ram(0xffff2154U)=t->blocks;
    *ram(0xffff87e1U)=t->flag;
    *ram(0xffff11deU)=t->mode?t->other:t->channel;
    *ram(0xffff2143U)=t->mode?t->channel:t->other;
    *(volatile uint8_t *)0x8b3dU=t->selector;
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j)
            calibration_before[at++]=((volatile uint8_t *)calibrations[i].at)[j];
}
static struct context make_context(const struct normalization_case *t){
    struct context c;unsigned i;
    for(i=0;i<15U;++i)c.r[i]=0x28765430U+i*0x01030507U;
    c.r[7]=t->mode?ALTERNATE_ENTRY:REGION_ENTRY;
    c.r[11]=t->mode?8U:0U;
    if(t->mode)c.r[14]=t->channel;else c.r[5]=t->channel;
    c.gbr=0x456789abU;c.mach=0x13579bdfU;c.macl=0x2468ace0U;c.entry_t=t->entry_t;
    return c;
}
static int preservation(unsigned long index,const struct normalization_case *t){
    unsigned i,j,at=0;uint32_t selected=0x20d2U+16U*(t->channel-1U);
    for(i=0;i<65536U;++i){
        if((i>=0x20c2U && i<0x20d2U) || (i>=selected && i<selected+16U))continue;
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_before[i])
            return fail(index,"full RAM/input/sibling preservation",i,ram_before[i]);
    }
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j,++at)
            if(((volatile uint8_t *)calibrations[i].at)[j]!=calibration_before[at])
                return fail(index,"all pool/selector/static-anchor preservation",
                    ((volatile uint8_t *)calibrations[i].at)[j],calibration_before[at]);
    return 1;
}
static int run_case(unsigned long index,const struct normalization_case *t){
    struct context c=make_context(t),before=c;
    struct observation out;
    uint8_t expected_frame[64];unsigned i;char field[40];
    uint32_t expected_sr;
    seed(index,t);memset(&out,0xa6,sizeof(out));
    stock_invoke_knock_normalization(c.r[7],&c,&out);
    if(memcmp(&c,&before,sizeof(c)))return fail(index,"entry context preservation",1,0);
    for(i=0;i<15U;++i){
        uint32_t expected=i==1?out.continuation:t->expected[i];
        if(reg(&out,i)!=expected){
            snprintf(field,sizeof(field),"literal GPR R%u",i);
            return fail(index,field,reg(&out,i),expected);
        }
    }
    if((out.sr_before&0x301U)!=t->entry_t)
        return fail(index,"prepared incoming M/Q/T",out.sr_before&0x301U,t->entry_t);
    expected_sr=(out.sr_before&~0x301U)|t->sr_controlled;
    if(out.exit[0]!=expected_sr)return fail(index,"literal full SR with retained mode bits",out.exit[0],expected_sr);
    if(out.exit[2]!=t->macl || out.exit[3]!=c.mach || out.exit[4]!=c.gbr)
        return fail(index,"literal MACL/MACH/GBR",out.exit[2],t->macl);
    if(out.sp!=out.abi_before[10]-164U)return fail(index,"fragment SP",out.sp,out.abi_before[10]-164U);
    if(out.exit[1]!=out.continuation)return fail(index,"external boundary PR continuation",out.exit[1],out.continuation);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"distinct C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    for(i=0;i<8U;++i){
        if(get16(0xffff20c2U+2U*i)!=t->output[i])
            return fail(index,"all eight literal normalized words",get16(0xffff20c2U+2U*i),t->output[i]);
        if(get16(0xffff20d2U+16U*(t->channel-1U)+2U*i)!=t->output[i])
            return fail(index,"all eight literal selected cache words",get16(0xffff20d2U+16U*(t->channel-1U)+2U*i),t->output[i]);
    }
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    frame_set(expected_frame,32,ALIAS(0xffff20c2U));
    if(t->blocks){
        frame_set(expected_frame,28,t->bin[7]);
        if(t->has_long)frame_set(expected_frame,24,t->saved_r3);
        frame_set(expected_frame,t->flag?36U:40U,ALIAS(0xffff20c2U));
    }
    for(i=0;i<64U;++i)
        if(out.frame_after[i]!=expected_frame[i])
            return fail(index,"literal complete stack/local/neighbors",out.frame_after[i],expected_frame[i]);
    if(word(out.frame_before,56)!=out.continuation || word(out.frame_after,56)!=out.continuation)
        return fail(index,"independent local continuation preservation",1,0);
    if(!preservation(index,t))return 0;
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(!initial())return 1;
    for(i=0;i<ARRAY_SIZE(normalization_cases);++i)if(!run_case(i,&normalization_cases[i]))return 1;
    if(completed!=KNOCK_NORMALIZATION_CASE_COUNT)return !fail(0,"case count",completed,KNOCK_NORMALIZATION_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-knock-normalization cases=%lu\n",completed);
    return 0;
}
