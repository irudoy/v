/* Literal learned-cell publication, complete bank reset and natural return. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&0xffffU))
#define COUNT(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[112],frame_after[112];
    uint32_t sr_before;
};
struct calibration { uint8_t load[8],speed[8],load_hysteresis,speed_hysteresis; };
struct sample {
    uint32_t bank_register;
    uint16_t load;
    uint8_t speed,packed;
    uint16_t cell;
    uint8_t flag,diagnostic,entry_t,profile,lower,upper,load_index,speed_index,index;
    uint16_t output;
    uint8_t reset,predicate_called,r3_speed_base,packed_output;
};
#include "stock-jk08a-grid-selection-cases.h"
#include "grid-bound-spans.h"
extern void stock_invoke_grid_selection(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[65536],bound_before[765];
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static volatile uint8_t *ram(uint32_t a){return (volatile uint8_t *)ALIAS(a);}
static void set16(uint32_t a,uint16_t v){volatile uint8_t *p=ram(a);p[0]=(uint8_t)(v>>8);p[1]=(uint8_t)v;}
static uint16_t get16(uint32_t a){volatile uint8_t *p=ram(a);return (uint16_t)((uint16_t)p[0]<<8|p[1]);}
static uint32_t reg(const struct observation *o,unsigned n){return o->exit[19U-n];}
static void put32(uint8_t *p,unsigned at,uint32_t v){
    p[at]=(uint8_t)(v>>24);p[at+1]=(uint8_t)(v>>16);p[at+2]=(uint8_t)(v>>8);p[at+3]=(uint8_t)v;
}
static int fail(unsigned index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"grid[%u] %s actual=%08lx expected=%08lx\n",index,field,(unsigned long)actual,(unsigned long)expected);return 0;
}
static void seed(unsigned index,const struct sample *s){
    unsigned i,j,n=0,b=s->bank_register&255U;
    const struct calibration *c=&calibrations[s->profile];
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x51U+29U*i+(i>>8)+index);
    for(i=0;i<64U;++i){set16(0xffff4b90U+2U*i,(uint16_t)(23100U+17U*i));set16(0xffff4b10U+2U*i,(uint16_t)(23600U+17U*i));}
    set16(0xffff1024U,s->load);*ram(0xffff11aeU)=s->speed;
    *ram(0xffff130aU+b)=s->packed;
    set16((b?0xffff4b10U:0xffff4b90U)+2U*s->index,s->cell);
    *ram(0xffff41b5U)=s->flag;*ram(0xffff5a94U)=s->diagnostic;
    for(i=0;i<8U;++i){((volatile uint8_t *)0x12592U)[i]=c->load[i];((volatile uint8_t *)0x126dcU)[i]=c->speed[i];}
    *(volatile uint8_t *)0x881bU=c->load_hysteresis;*(volatile uint8_t *)0x881aU=c->speed_hysteresis;
    *(volatile uint8_t *)0x8a9eU=s->lower;*(volatile uint8_t *)0x8a9fU=s->upper;
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<COUNT(bound);++i)for(j=0;j<bound[i].size;++j)bound_before[n++]=((volatile uint8_t *)bound[i].at)[j];
}
static int preservation(unsigned index,const struct sample *s){
    unsigned i,j,n=0,b=s->bank_register&255U,base=b?0x4b10U:0x4b90U,aux=b?0x49b0U:0x49f0U;
    for(i=0;i<65536U;++i){
        if(i==0x130aU+b || (i>=0x2306U+2U*b && i<0x2308U+2U*b))continue;
        if(s->reset && ((i>=base && i<base+128U) || (i>=aux && i<aux+64U) || (i>=0x45a0U+2U*b && i<0x45a2U+2U*b)))continue;
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_before[i])return fail(index,"all other RAM and sibling bank",i,ram_before[i]);
    }
    if(s->reset){
        for(i=0;i<64U;++i){
            if(get16(0xffff0000U+base+2U*i)!=25600U)return fail(index,"all sixty-four reset cells",get16(0xffff0000U+base+2U*i),25600U);
            if(((volatile uint8_t *)RAM_BASE)[aux+i]!=0)return fail(index,"all sixty-four auxiliary reset bytes",((volatile uint8_t *)RAM_BASE)[aux+i],0);
        }
        if(get16(0xffff45a0U+2U*b)!=0)return fail(index,"bank adjustment reset",get16(0xffff45a0U+2U*b),0);
    }
    for(i=0;i<COUNT(bound);++i)for(j=0;j<bound[i].size;++j,++n)
        if(((volatile uint8_t *)bound[i].at)[j]!=bound_before[n])return fail(index,"all bound bytes and calibration",((volatile uint8_t *)bound[i].at)[j],bound_before[n]);
    return 1;
}
static int run_case(unsigned index,const struct sample *s){
    struct context c,before;struct observation out;
    uint32_t expected[15];uint8_t frame[112],initial[112];unsigned i,b=s->bank_register&255U;
    for(i=0;i<15U;++i)c.r[i]=0x28765430U+0x01030507U*i+0x12345U*index;
    c.r[4]=s->bank_register;c.gbr=0x456789abU^index;c.mach=0x13579bdfU^index;c.macl=0x2468ace0U^index;
    c.sr=s->entry_t|((index&3U)<<8);before=c;memcpy(expected,c.r,sizeof(expected));
    expected[0]=b;expected[2]=ALIAS(0xffff2306U);expected[6]=ALIAS(0xffff130aU);
    expected[7]=(s->output&32768U)?0xffff0000U|s->output:s->output;
    if(s->reset){expected[1]=255U;expected[3]=255U;expected[4]=ALIAS(b?0xffff49b0U:0xffff49f0U);expected[5]=0;}
    else {expected[1]=ALIAS(0xffff5718U);if(s->r3_speed_base)expected[3]=ALIAS(0xffff119cU);expected[4]=0x129U;expected[5]=0x8a9fU;}
    seed(index,s);memset(&out,0xa6,sizeof(out));stock_invoke_grid_selection(REGION_ENTRY,&c,&out);
    if(memcmp(&c,&before,sizeof(c)))return fail(index,"incoming context",1,0);
    for(i=0;i<15U;++i)if(reg(&out,i)!=expected[i])return fail(index,"all fifteen GPR",reg(&out,i),expected[i]);
    if((out.sr_before&0x301U)!=c.sr)return fail(index,"independent prepared M/Q/T",out.sr_before&0x301U,c.sr);
    if(out.exit[0]!=(out.sr_before&~1U))return fail(index,"full SR with final T zero",out.exit[0],out.sr_before&~1U);
    if(out.exit[2]!=c.macl || out.exit[3]!=c.mach || out.exit[4]!=c.gbr)return fail(index,"MACL/MACH/GBR",out.exit[2],c.macl);
    if(out.sp!=out.abi_before[10]-164U)return fail(index,"stock SP",out.sp,out.abi_before[10]-164U);
    if(out.exit[1]!=out.continuation)return fail(index,"natural restored PR",out.exit[1],out.continuation);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"outer ABI",1,0);
    for(i=0;i<COUNT(abi_expected);++i)if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    for(i=0;i<28U;++i)put32(initial,4U*i,0xa3b4c5d6U+17U*i);
    if(memcmp(initial,out.frame_before,sizeof(initial)))return fail(index,"independent complete initial frame",1,0);
    memcpy(frame,initial,sizeof(frame));
    for(i=0;i<7U;++i)put32(frame,76U-4U*i,c.r[8U+i]);
    put32(frame,48U,out.continuation);
    frame[44]=(uint8_t)(s->output>>8);frame[45]=(uint8_t)s->output;
    if(s->reset)put32(frame,40U,s->speed_index);
    for(i=0;i<112U;++i)if(out.frame_after[i]!=frame[i])return fail(index,"complete stock frame and neighbors",out.frame_after[i],frame[i]);
    if(get16(0xffff2306U+2U*b)!=s->output)return fail(index,"literal selected publication",get16(0xffff2306U+2U*b),s->output);
    if(*ram(0xffff130aU+b)!=s->packed_output)return fail(index,"literal packed index",*ram(0xffff130aU+b),s->packed_output);
    return preservation(index,s);
}
int main(void){
    unsigned i,count=EARLY_ONLY?16U:GRID_SELECTION_CASE_COUNT;
    if(COUNT(samples)!=GRID_SELECTION_CASE_COUNT || sizeof(bound_before)!=GRID_BOUND_BYTES)return 1;
    for(i=0;i<count;++i)if(!run_case(i,&samples[i]))return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-grid-selection cases=%u\n",count);return 0;
}
