/* Post-feedback word publication, full caller-frame return and input preservation. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&0xffffU))
#define COUNT(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_t; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[64],frame_after[64];
    uint32_t sr_before;
};
struct sample { uint8_t mode,forced,t; uint16_t working[2],output[2]; uint32_t changed[4]; uint8_t exit_t; };
#include "stock-jk08a-stft-publication-cases.h"
extern void stock_invoke_stft_publication(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[65536],bound_before[98];
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } bound[]={
    {0x5ca08U,86U},{0x5ca5eU,2U},{0x5ca6cU,2U},{0x5ca84U,4U},{0x5ca88U,4U}
};
static volatile uint8_t *ram(uint32_t a){return (volatile uint8_t *)ALIAS(a);}
static void set16(uint32_t a,uint16_t v){volatile uint8_t *p=ram(a);p[0]=(uint8_t)(v>>8);p[1]=(uint8_t)v;}
static uint16_t get16(uint32_t a){volatile uint8_t *p=ram(a);return (uint16_t)((uint16_t)p[0]<<8|p[1]);}
static uint32_t reg(const struct observation *o,unsigned n){return o->exit[19U-n];}
static void put32(uint8_t *p,unsigned at,uint32_t v){
    p[at]=(uint8_t)(v>>24);p[at+1]=(uint8_t)(v>>16);p[at+2]=(uint8_t)(v>>8);p[at+3]=(uint8_t)v;
}
static int fail(unsigned index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"stft[%u] %s actual=%08lx expected=%08lx\n",index,field,(unsigned long)actual,(unsigned long)expected);
    return 0;
}
static int initial(void){
    if(*(volatile uint16_t *)0x5ca5eU!=MODE_ALIAS || *(volatile uint16_t *)0x5ca6cU!=FORCE_ALIAS)
        return fail(0,"declared RAM word aliases",*(volatile uint16_t *)0x5ca5eU,MODE_ALIAS);
    if(*(volatile uint32_t *)0x5ca84U!=ALIAS(0xffff40acU) || *(volatile uint32_t *)0x5ca88U!=ALIAS(0xffff22dcU))
        return fail(0,"declared long RAM aliases",*(volatile uint32_t *)0x5ca84U,ALIAS(0xffff40acU));
    return 1;
}
static void seed(unsigned index,const struct sample *sample){
    unsigned i,j,n=0;
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x51U+29U*i+(i>>8)+index);
    set16(0xffff40acU,sample->working[0]);set16(0xffff40aeU,sample->working[1]);
    *ram(0xffff99c4U)=sample->mode;*ram(0xffff9925U)=sample->forced;
    *(volatile uint8_t *)MODE_ALIAS=sample->mode;
    *(volatile uint8_t *)FORCE_ALIAS=*ram(0xffff9924U);
    *(volatile uint8_t *)(FORCE_ALIAS+1U)=sample->forced;
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<COUNT(bound);++i)
        for(j=0;j<bound[i].size;++j)bound_before[n++]=((volatile uint8_t *)bound[i].at)[j];
}
static int preservation(unsigned index,const struct sample *sample){
    unsigned i,j,n=0;
    for(i=0;i<65536U;++i){
        if(i>=0x22dcU && i<0x22e0U)continue;
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_before[i])return fail(index,"all other RAM",i,ram_before[i]);
    }
    for(i=0;i<COUNT(bound);++i)
        for(j=0;j<bound[i].size;++j,++n)
            if(((volatile uint8_t *)bound[i].at)[j]!=bound_before[n])
                return fail(index,"bound instruction/pool bytes",((volatile uint8_t *)bound[i].at)[j],bound_before[n]);
    if(*(volatile uint8_t *)MODE_ALIAS!=sample->mode || *(volatile uint8_t *)FORCE_ALIAS!=ram_before[0x9924U]
        || *(volatile uint8_t *)(FORCE_ALIAS+1U)!=sample->forced)return fail(index,"word alias windows",1,0);
    return 1;
}
static int run_case(unsigned index,const struct sample *sample){
    struct context c,before;struct observation out;
    uint32_t expected[15],result[2],final_t;uint8_t frame[64];unsigned i;
    for(i=0;i<15U;++i)c.r[i]=0x28765430U+0x01030507U*i+0x12345U*index;
    c.gbr=0x456789abU^index;c.mach=0x13579bdfU^index;c.macl=0x2468ace0U^index;c.entry_t=sample->t;
    before=c;memcpy(expected,c.r,sizeof(expected));
    result[0]=sample->output[0];result[1]=sample->output[1];final_t=sample->exit_t;
    expected[0]=sample->changed[0];expected[2]=sample->changed[1];
    expected[5]=sample->changed[2];expected[6]=sample->changed[3];
    for(i=8;i<15U;++i)expected[i]=abi_expected[i-8U];
    seed(index,sample);memset(&out,0xa6,sizeof(out));
    stock_invoke_stft_publication(REGION_ENTRY,&c,&out);
    if(memcmp(&c,&before,sizeof(c)))return fail(index,"incoming context",1,0);
    for(i=0;i<15U;++i)if(reg(&out,i)!=expected[i])return fail(index,"all fifteen GPR",reg(&out,i),expected[i]);
    if((out.sr_before&0x301U)!=sample->t)return fail(index,"prepared M/Q/T",out.sr_before&0x301U,sample->t);
    if(out.exit[0]!=((out.sr_before&~1U)|final_t))return fail(index,"full retained SR",out.exit[0],(out.sr_before&~1U)|final_t);
    if(out.exit[2]!=c.macl || out.exit[3]!=c.mach || out.exit[4]!=c.gbr)return fail(index,"MACL/MACH/GBR",out.exit[2],c.macl);
    if(out.sp!=out.abi_before[10]-132U)return fail(index,"real 32-byte stack return",out.sp,out.abi_before[10]-132U);
    if(out.exit[1]!=out.continuation)return fail(index,"real restored PR",out.exit[1],out.continuation);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"outer ABI",1,0);
    for(i=0;i<COUNT(abi_expected);++i)if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    for(i=0;i<8U;++i)put32(frame,4U*i,0xa3b4c5d6U+17U*i);
    put32(frame,32U,out.continuation);
    for(i=0;i<7U;++i)put32(frame,36U+4U*i,abi_expected[6U-i]);
    for(i=0;i<64U;++i)
        if(out.frame_before[i]!=frame[i] || out.frame_after[i]!=frame[i])return fail(index,"complete supplied frame and neighbors",out.frame_after[i],frame[i]);
    for(i=0;i<2U;++i)if(get16(0xffff22dcU+2U*i)!=result[i])return fail(index,"both STFT words",get16(0xffff22dcU+2U*i),result[i]);
    return preservation(index,sample);
}
int main(void){
    unsigned i,count=EARLY_ONLY?16U:STFT_PUBLICATION_CASE_COUNT;if(!initial())return 1;
    if(COUNT(samples)!=STFT_PUBLICATION_CASE_COUNT)return 1;
    for(i=0;i<count;++i)if(!run_case(i,&samples[i]))return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-stft-publication cases=%u\n",count);
    return 0;
}
