/* Independent natural conversion, register, frame and memory expectations. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&65535U))
#define COUNT(a) (sizeof(a)/sizeof((a)[0]))
struct context {uint32_t r[15],gbr,mach,macl,sr;};
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[160],frame_after[160];uint32_t sr_before;
};
struct span {uint32_t at,size;};
struct sample {
    uint32_t x1,x2,speed_gate,coefficient_input,row_input,load,adjust1,adjust2;
    uint32_t mode,permits,offset,midpoint,coefficient_override,map_override,curve_profile,entry_t,coefficient;
    uint32_t x[2],z[2],output[2],maps[2],lookups[2],signed_offsets[2],sums[2];
    uint32_t difference[2],scaled[2],candidates[2],workspace_quotient,last_fraction,divided,exit_q;
    uint32_t admitted,coefficient_fraction,coefficient_left,coefficient_next;
    uint32_t fractions[2],curve_left[2],curve_next[2];
};
#include "stock-jk08a-closed-loop-conversion-cases.h"
extern void stock_invoke_closed_loop_conversion(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[65536],bound_before[CONVERSION_BOUND_BYTES];
static uint8_t low_before[128];
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static volatile uint8_t *ram(uint32_t a){return (volatile uint8_t *)ALIAS(a);}
static void word(uint32_t at,uint32_t v){volatile uint8_t *p=(volatile uint8_t *)at;p[0]=(uint8_t)(v>>8);p[1]=(uint8_t)v;}
static uint32_t readword(uint32_t at){volatile uint8_t *p=(volatile uint8_t *)at;return (uint32_t)p[0]*256U+p[1];}
static void put32(uint8_t *p,unsigned at,uint32_t v){p[at]=(uint8_t)(v>>24);p[at+1]=(uint8_t)(v>>16);p[at+2]=(uint8_t)(v>>8);p[at+3]=(uint8_t)v;}
static void put16(uint8_t *p,unsigned at,uint32_t v){p[at]=(uint8_t)(v>>8);p[at+1]=(uint8_t)v;}
static int fail(unsigned index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"conversion[%u] %s actual=%08lx expected=%08lx\n",index,field,(unsigned long)actual,(unsigned long)expected);return 0;
}
static void seed(unsigned index,const struct sample *s){
    unsigned i,j,n=0;uint32_t v;
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x51U+29U*i+(i>>8)+index);
    for(i=0;i<128U;++i)((volatile uint8_t *)0x7ce0U)[i]=(uint8_t)(0x91U+13U*i+index);
    word(ALIAS(0x267cU),s->x1);word(ALIAS(0x267eU),s->x2);
    word(ALIAS(0x2882U),s->x1);word(ALIAS(0x2884U),s->x2);
    word(ALIAS(0x110aU),s->speed_gate);word(ALIAS(0x4524U),s->coefficient_input);
    word(ALIAS(0x11bcU),s->row_input);word(ALIAS(0x1024U),s->load);
    word(ALIAS(0x45a0U),s->adjust1);word(ALIAS(0x45a2U),s->adjust2);
    *ram(0x2b4dU)=(uint8_t)s->permits;*(volatile uint8_t *)0x8978U=(uint8_t)s->mode;
    word(0x8ea4U,s->offset);word(0x8f98U,s->midpoint);
    for(i=0;i<17U;++i)((volatile uint8_t *)0x12292U)[i]=(uint8_t)(i<16U&&s->coefficient_override<256U?s->coefficient_override:stock_12292[i]);
    for(i=0;i<17U;++i){
        v=stock_148fa[i];if(s->curve_profile==1U)v=i<16U?65535U-4095U*i:0U;
        if(s->curve_profile==2U)v=i&1U?65535U:0U;
        word(0x148faU+2U*i,v);
    }
    for(i=0;i<64U;++i){word(0xc10eU+2U*i,s->map_override<65536U?s->map_override:stock_c10e[i]);word(0xc18eU+2U*i,s->map_override<65536U?s->map_override:stock_c18e[i]);}
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<128U;++i)low_before[i]=((volatile uint8_t *)0x7ce0U)[i];
    for(i=0;i<COUNT(bound);++i)for(j=0;j<bound[i].size;++j)bound_before[n++]=((volatile uint8_t *)bound[i].at)[j];
}
static int memory(unsigned index,const struct sample *s){
    uint8_t expected[128];unsigned i,j,n=0;
    for(i=0;i<65536U;++i){
        if(i==0x2f8eU||(i>=0x322cU&&i<0x3230U)||(i>=0x2b54U&&i<0x2b58U)||(i>=0x29e2U&&i<0x29e6U))continue;
        if(((volatile uint8_t *)RAM_BASE)[i]!=ram_before[i])return fail(index,"remaining RAM",i,ram_before[i]);
    }
    if(*ram(0x2f8eU)!=s->coefficient)return fail(index,"coefficient publication",*ram(0x2f8eU),s->coefficient);
    for(i=0;i<2U;++i){
        if(readword(ALIAS(0x322cU)+2U*i)!=s->z[i])return fail(index,"admitted or retained coordinate",readword(ALIAS(0x322cU)+2U*i),s->z[i]);
        if(readword(ALIAS(0x2b54U)+2U*i)!=(s->signed_offsets[i]&65535U))return fail(index,"signed offset publication",readword(ALIAS(0x2b54U)+2U*i),s->signed_offsets[i]&65535U);
        if(readword(ALIAS(0x29e2U)+2U*i)!=s->output[i])return fail(index,"bounded final conversion",readword(ALIAS(0x29e2U)+2U*i),s->output[i]);
    }
    memcpy(expected,low_before,sizeof(expected));
    put32(expected,32U,s->sums[1]);put32(expected,36U,s->sums[1]-s->signed_offsets[1]);put32(expected,40U,s->sums[0]);
    put16(expected,44U,s->maps[1]);put16(expected,46U,s->maps[0]);
    put16(expected,48U,s->x[0]);put16(expected,50U,s->x[1]);put16(expected,52U,s->z[0]);put16(expected,54U,s->z[1]);
    expected[56]=(s->mode>>3)&1U;expected[57]=s->permits&1U;expected[58]=(s->permits>>1)&1U;expected[59]=(uint8_t)s->coefficient;
    put32(expected,96U,s->candidates[0]);put32(expected,100U,s->candidates[1]);put32(expected,104U,s->workspace_quotient);
    put16(expected,108U,s->scaled[0]);put16(expected,110U,s->scaled[1]);put16(expected,112U,s->difference[0]);put16(expected,114U,s->difference[1]);
    for(i=0;i<128U;++i)if(((volatile uint8_t *)0x7ce0U)[i]!=expected[i])return fail(index,"both aliased workspaces and neighbors",i,expected[i]);
    for(i=0;i<COUNT(bound);++i)for(j=0;j<bound[i].size;++j,++n)
        if(((volatile uint8_t *)bound[i].at)[j]!=bound_before[n])return fail(index,"all bound bytes",((volatile uint8_t *)bound[i].at)[j],bound_before[n]);
    return 1;
}
static int run_case(unsigned index,const struct sample *s){
    struct context c,before;struct observation out;uint32_t expected[15],sum=s->sums[1],t,mq;unsigned i;
    uint8_t frame[160],initial[160];int32_t numerator;uint32_t magnitude;
    for(i=0;i<15U;++i)c.r[i]=0x28765430U+0x01030507U*i+0x12345U*index;
    c.gbr=0x456789abU^index;c.mach=0x13579bdfU^index;c.macl=0x2468ace0U^index;
    c.sr=s->entry_t|((index&3U)<<8);before=c;memcpy(expected,c.r,sizeof(expected));
    expected[0]=236U;expected[1]=c.macl;expected[3]=s->last_fraction;expected[4]=98303U;expected[5]=s->maps[1];expected[7]=ALIAS(0x4558U);
    if((int32_t)sum>98303){expected[2]=0xffffffffU;expected[6]=sum;t=1U;}
    else if((int32_t)sum<32768){expected[2]=0U;expected[6]=32768U;t=0U;}
    else{expected[2]=sum+32768U;expected[6]=0xffff8000U;t=1U;}
    seed(index,s);memset(&out,0xa6,sizeof(out));stock_invoke_closed_loop_conversion(REGION_ENTRY,&c,&out);
    if(memcmp(&c,&before,sizeof(c)))return fail(index,"incoming context",1U,0U);
    for(i=0;i<15U;++i)if(out.exit[19U-i]!=expected[i])return fail(index,"fifteen GPR",out.exit[19U-i],expected[i]);
    if((out.sr_before&0x301U)!=c.sr)return fail(index,"prepared M/Q/T",out.sr_before&0x301U,c.sr);
    mq=s->divided?s->exit_q*256U:(out.sr_before&0x300U);
    if(out.exit[0]!=((out.sr_before&~0x301U)|mq|t))return fail(index,"literal full SR",out.exit[0],(out.sr_before&~0x301U)|mq|t);
    if(out.exit[2]!=c.macl||out.exit[3]!=c.mach||out.exit[4]!=c.gbr)return fail(index,"special register preservation",1U,0U);
    if(out.sp!=out.abi_before[10]-164U||out.exit[1]!=out.continuation)return fail(index,"natural PR/SP",1U,0U);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"outer ABI",1U,0U);
    for(i=0;i<COUNT(abi_expected);++i)if(out.abi_before[i]!=abi_expected[i])return fail(index,"ABI sentinel",out.abi_before[i],abi_expected[i]);
    for(i=0;i<40U;++i)put32(initial,4U*i,0xa3b4c5d6U+17U*i);
    if(memcmp(initial,out.frame_before,sizeof(initial)))return fail(index,"complete initial frame",1U,0U);
    memcpy(frame,initial,sizeof(frame));
    for(i=0;i<5U;++i)put32(frame,124U-4U*i,c.r[10U+i]);
    put32(frame,104U,out.continuation);put32(frame,100U,c.gbr);put32(frame,96U,0x7d1bU);
    put32(frame,92U,c.r[8]);put32(frame,88U,c.r[9]);
    put32(frame,84U,ALIAS(0x1024U));put32(frame,80U,ALIAS(0x119cU));
    put32(frame,76U,0x148faU);put32(frame,72U,0x15d20U);put32(frame,68U,1U);
    put32(frame,64U,0x3ee7eU);put32(frame,60U,0x7d00U);
    put16(frame,44U,s->x[0]);put16(frame,48U,s->difference[1]);put16(frame,52U,s->difference[0]);
    if(s->admitted)put32(frame,56U,s->candidates[0]);
    put32(frame,40U,0x3efaaU);put32(frame,36U,0x12292U);
    if(s->coefficient_fraction){put32(frame,32U,0x264aeU);put32(frame,28U,0x26c78U);}
    if(s->coefficient_left>s->coefficient_next)put32(frame,40U,s->coefficient_left);
    if(s->coefficient){
        for(i=0;i<2U;++i){
            put32(frame,40U,0x21bbcU);put32(frame,36U,s->coefficient_fraction);
            numerator=(int32_t)s->difference[i]*128;magnitude=(uint32_t)(numerator<0?-numerator:numerator);
            if(magnitude>=s->coefficient*256U)put32(frame,32U,i?s->coefficient:(uint32_t)numerator);
        }
    }
    for(i=0;i<2U;++i){
        put32(frame,92U,i?0x3ee9cU:0x3ee8aU);put32(frame,88U,0x148faU);
        if(s->fractions[i]){put32(frame,84U,0x26506U);put32(frame,80U,0x26c78U);}
        if(s->curve_left[i]>s->curve_next[i])put32(frame,92U,s->curve_left[i]);
    }
    for(i=0;i<160U;++i)if(out.frame_after[i]!=frame[i])return fail(index,"complete nested frame and neighbors",i,frame[i]);
    return memory(index,s);
}
int main(void){
    unsigned i,count=EARLY_ONLY?16U:CONVERSION_CASE_COUNT;
    if(COUNT(samples)!=CONVERSION_CASE_COUNT)return 1;
    for(i=0;i<count;++i)if(!run_case(i,&samples[i]))return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-closed-loop-conversion cases=%u\n",count);return 0;
}
