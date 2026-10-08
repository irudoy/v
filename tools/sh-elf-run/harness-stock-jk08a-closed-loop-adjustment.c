/* Independent adjustment arithmetic, complete terminal CPU, frame and memory expectations. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&65535U))
#define COUNT(a) (sizeof(a)/sizeof((a)[0]))
struct context {uint32_t r[15],gbr,mach,macl,sr;};
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];uint32_t sr_before;
};
struct span {uint32_t at,size;};
struct sample {
    uint32_t masks[15],extra[4],control,previous[2][7],coordinate[2],state[2];
    uint32_t up_table[9],down_table[9],scalars[7];
    uint32_t initial_workspace[122],workspace[122],output[2],counters[2],up_selector[2],down_selector[2];
    uint32_t cpu[13];uint8_t frame[192];
};
#include "stock-jk08a-closed-loop-adjustment-cases.h"
extern void stock_invoke_closed_loop_adjustment(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[65536],bound_before[ADJUSTMENT_BOUND_BYTES],low_before[192];
static const uint32_t inputs[15]={0x48c0U,0x48beU,0x48b7U,0x302eU,0x326aU,0x2a89U,0x48b4U,
    0x32ceU,0x32cfU,0x334cU,0x334dU,0x3522U,0x3523U,0x2fd1U,0x2fd2U};
static const uint32_t extra_inputs[4]={0x14e8U,0x14e9U,0x2f1cU,0x2f1dU};
static const uint32_t abi_expected[10]={0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U};
static volatile uint8_t *ram(uint32_t at){return (volatile uint8_t *)ALIAS(at);}
static void word(uint32_t at,uint32_t value){volatile uint8_t *p=(volatile uint8_t *)at;p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static uint32_t readword(uint32_t at){volatile uint8_t *p=(volatile uint8_t *)at;return (uint32_t)p[0]*256U+p[1];}
static void put32(uint8_t *p,unsigned at,uint32_t value){p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;}
static int fail(unsigned index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"adjustment[%u] %s actual=%08lx expected=%08lx\n",index,field,(unsigned long)actual,(unsigned long)expected);return 0;
}
static void seed(unsigned index,const struct sample *s){
    unsigned i,j,n=0;
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x51U+29U*i+(i>>8)+index);
    for(i=0;i<192U;++i)((volatile uint8_t *)0x7de0U)[i]=(uint8_t)(0x91U+13U*i+index);
    for(i=0;i<122U;++i)((volatile uint8_t *)0x7e00U)[i]=(uint8_t)s->initial_workspace[i];
    for(i=0;i<15U;++i)*ram(inputs[i])=(uint8_t)s->masks[i];
    for(i=0;i<4U;++i)*ram(extra_inputs[i])=(uint8_t)s->extra[i];
    *ram(0x424fU)=(uint8_t)s->control;
    for(i=0;i<2U;++i){word(ALIAS(0x2a92U)+2U*i,s->coordinate[i]);word(ALIAS(0x45a0U)+2U*i,s->state[i]);}
    word(0x8e7cU,s->scalars[0]);word(0x8e7eU,s->scalars[1]);
    word(0x8e78U,s->scalars[2]);word(0x8e7aU,s->scalars[3]);
    word(0x8fa2U,s->scalars[4]);word(0x8fa0U,s->scalars[5]);
    for(i=0;i<9U;++i)word(0x1462aU+2U*i,s->up_table[i]);
    for(i=0;i<9U;++i)word(0x1463aU+2U*i,s->down_table[i]);
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<192U;++i)low_before[i]=((volatile uint8_t *)0x7de0U)[i];
    for(i=0;i<COUNT(bound);++i)for(j=0;j<bound[i].size;++j)bound_before[n++]=((volatile uint8_t *)bound[i].at)[j];
}
static int memory(unsigned index,const struct sample *s){
    unsigned i,j,n=0;uint32_t expected;
    for(i=0;i<65536U;++i){
        expected=ram_before[i];
        if(i>=0x45a0U&&i<0x45a4U)expected=(s->output[(i-0x45a0U)/2U]>>((i&1U)?0U:8U))&255U;
        if(i==0x29f3U||i==0x29f4U)expected=s->counters[i-0x29f3U];
        if(((volatile uint8_t *)RAM_BASE)[i]!=expected)return fail(index,"complete RAM byte",i,expected);
    }
    for(i=0;i<192U;++i){
        expected=i>=32U&&i<154U?s->workspace[i-32U]:low_before[i];
        if(((volatile uint8_t *)0x7de0U)[i]!=expected)return fail(index,"complete workspace and neighbors",i,expected);
    }
    for(i=0;i<2U;++i)if(readword(ALIAS(0x45a0U)+2U*i)!=s->output[i])return fail(index,"bounded signed output",readword(ALIAS(0x45a0U)+2U*i),s->output[i]);
    for(i=0;i<COUNT(bound);++i)for(j=0;j<bound[i].size;++j,++n)
        if(((volatile uint8_t *)bound[i].at)[j]!=bound_before[n])return fail(index,"all bound bytes",((volatile uint8_t *)bound[i].at)[j],bound_before[n]);
    return 1;
}
static int run_case(unsigned index,const struct sample *s){
    struct context c,before;struct observation out;uint8_t initial[192],frame[192];uint32_t expected[15],mq;unsigned i;
    for(i=0;i<15U;++i)c.r[i]=0x28765430U+0x01030507U*i+0x12345U*index;
    c.gbr=0x456789abU^index;c.mach=0x13579bdfU^index;c.macl=0x2468ace0U^index;
    c.sr=s->scalars[6]|((index&3U)<<8);before=c;
    seed(index,s);memset(&out,0xa6,sizeof(out));stock_invoke_closed_loop_adjustment(REGION_ENTRY,&c,&out);
    if(memcmp(&c,&before,sizeof(c)))return fail(index,"incoming context",1U,0U);
    memcpy(expected,c.r,sizeof(expected));
    expected[0]=s->cpu[0];expected[2]=s->cpu[1];
    expected[4]=s->cpu[3]?out.sp+s->cpu[3]:s->cpu[2];
    expected[5]=s->cpu[4];expected[6]=s->cpu[5];
    expected[7]=s->cpu[7]?out.sp+s->cpu[7]:s->cpu[6];
    if(s->cpu[8]){expected[1]=c.macl;expected[3]=s->cpu[9];}
    for(i=0;i<15U;++i)if(out.exit[19U-i]!=expected[i])return fail(index,"fifteen GPR",out.exit[19U-i],expected[i]);
    mq=s->cpu[10]?s->cpu[11]*256U:(out.sr_before&0x300U);
    if(out.exit[0]!=((out.sr_before&~0x301U)|mq|s->cpu[12]))return fail(index,"literal full SR",out.exit[0],(out.sr_before&~0x301U)|mq|s->cpu[12]);
    if(out.exit[2]!=c.macl||out.exit[3]!=c.mach||out.exit[4]!=c.gbr)return fail(index,"special register preservation",1U,0U);
    if((out.sr_before&0x301U)!=c.sr)return fail(index,"prepared M/Q/T",out.sr_before&0x301U,c.sr);
    if(out.sp!=out.abi_before[10]-164U||out.exit[1]!=out.continuation)return fail(index,"natural PR/SP",1U,0U);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"outer ABI",1U,0U);
    for(i=0;i<COUNT(abi_expected);++i)if(out.abi_before[i]!=abi_expected[i])return fail(index,"ABI sentinel",out.abi_before[i],abi_expected[i]);
    for(i=0;i<48U;++i)put32(initial,4U*i,0xa3b4c5d6U+17U*i);
    if(memcmp(initial,out.frame_before,sizeof(initial)))return fail(index,"complete initial frame",1U,0U);
    memcpy(frame,s->frame,sizeof(frame));
    for(i=0;i<7U;++i)put32(frame,156U-4U*i,c.r[8U+i]);
    put32(frame,128U,out.continuation);put32(frame,124U,c.gbr);
    for(i=0;i<192U;++i)if(out.frame_after[i]!=frame[i])return fail(index,"complete nested frame and neighbors",i,frame[i]);
    return memory(index,s);
}
int main(void){
    unsigned i,count=EARLY_ONLY?16U:ADJUSTMENT_CASE_COUNT;
    if(COUNT(samples)!=ADJUSTMENT_CASE_COUNT)return 1;
    for(i=0;i<count;++i)if(!run_case(i,&samples[i]))return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-closed-loop-adjustment cases=%u\n",count);return 0;
}
