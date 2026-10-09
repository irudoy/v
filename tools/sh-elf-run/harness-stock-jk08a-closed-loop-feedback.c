/* Whole feedback verification with independent memory, terminal CPU and frame expectations. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define WORK_BASE 0x00005ffcU
#define COUNT(a) (sizeof(a)/sizeof((a)[0]))
struct context {uint32_t r[15],gbr,mach,macl,sr;};
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[352],frame_after[352];uint32_t sr_before;
};
struct span {uint32_t at,size;};
struct change {uint16_t offset;uint8_t value;};
struct memory_sample {uint32_t zero,input_begin,input_count,output_begin,output_count;uint8_t workspace[302];};
struct cpu_sample {uint32_t terminal[8],exit_q;uint8_t frame[352];};
#include "stock-jk08a-closed-loop-feedback-cases.h"
extern void stock_invoke_closed_loop_feedback(uint32_t,const struct context *,struct observation *);
static uint8_t expected[65536],bound_before[FEEDBACK_BOUND_BYTES],neighbors[366];
static const uint32_t abi_expected[10]={0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U};
static int fail(unsigned index,const char *field,uint32_t at,uint32_t actual,uint32_t wanted){
    fprintf(stderr,"feedback[%u] %s at=%08lx actual=%08lx expected=%08lx\n",
        index,field,(unsigned long)at,(unsigned long)actual,(unsigned long)wanted);return 0;
}
static void put32(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static void seed(unsigned index,const struct memory_sample *s){
    unsigned i,j,n=0;volatile uint8_t *ram=(volatile uint8_t *)RAM_BASE;
    volatile uint8_t *work=(volatile uint8_t *)WORK_BASE;
    for(i=0;i<65536U;++i){expected[i]=s->zero?0U:(uint8_t)(0x51U+29U*i+(i>>8)+index);ram[i]=expected[i];}
    for(i=0;i<s->input_count;++i){const struct change *c=&inputs[s->input_begin+i];ram[c->offset]=c->value;expected[c->offset]=c->value;}
    for(i=0;i<366U;++i){neighbors[i]=(uint8_t)(0x91U+13U*i+index);((volatile uint8_t *)(WORK_BASE-32U))[i]=neighbors[i];}
    for(i=0;i<302U;++i)work[i]=ram[0x88b0U+i];
    for(i=0;i<COUNT(bound);++i)for(j=0;j<bound[i].size;++j)bound_before[n++]=((volatile uint8_t *)bound[i].at)[j];
}
static int memory(unsigned index,const struct memory_sample *s){
    unsigned i,j,n=0;volatile uint8_t *ram=(volatile uint8_t *)RAM_BASE;
    volatile uint8_t *work=(volatile uint8_t *)WORK_BASE;
    for(i=0;i<s->output_count;++i){const struct change *c=&outputs[s->output_begin+i];expected[c->offset]=c->value;}
    for(i=0;i<65536U;++i)if(ram[i]!=expected[i])return fail(index,"complete RAM",i,ram[i],expected[i]);
    for(i=0;i<302U;++i)if(work[i]!=s->workspace[i])return fail(index,"shared workspace",i,work[i],s->workspace[i]);
    for(i=0;i<32U;++i){
        if(((volatile uint8_t *)(WORK_BASE-32U))[i]!=neighbors[i])return fail(index,"low neighbor",i,((volatile uint8_t *)(WORK_BASE-32U))[i],neighbors[i]);
        if(work[302U+i]!=neighbors[334U+i])return fail(index,"high neighbor",i,work[302U+i],neighbors[334U+i]);
    }
    for(i=0;i<COUNT(bound);++i)for(j=0;j<bound[i].size;++j,++n)
        if(((volatile uint8_t *)bound[i].at)[j]!=bound_before[n])return fail(index,"all bound bytes",bound[i].at+j,((volatile uint8_t *)bound[i].at)[j],bound_before[n]);
    return 1;
}
static int run_case(unsigned index){
    const struct memory_sample *s=&memory_samples[index];const struct cpu_sample *cpu=&cpu_samples[index];
    struct context c,before;struct observation out;uint8_t initial[352],frame[352];unsigned i;uint32_t wanted;
    for(i=0;i<15U;++i)c.r[i]=0x28765430U+0x01030507U*i+0x12345U*index;
    c.gbr=0x456789abU^index;c.mach=0x13579bdfU^index;c.macl=0x2468ace0U^index;
    c.sr=((index&3U)<<8)|((index>>2)&1U);before=c;
    seed(index,s);memset(&out,0xa6,sizeof(out));stock_invoke_closed_loop_feedback(REGION_ENTRY,&c,&out);
    if(memcmp(&c,&before,sizeof(c)))return fail(index,"incoming context",0U,1U,0U);
    for(i=0;i<15U;++i){
        wanted=i<8U?cpu->terminal[i]:c.r[i];
        if(out.exit[19U-i]!=wanted)return fail(index,"fifteen GPR",i,out.exit[19U-i],wanted);
    }
    wanted=(out.sr_before&~0x301U)|(cpu->exit_q<<8)|1U;
    if(out.exit[0]!=wanted)return fail(index,"complete SR",0U,out.exit[0],wanted);
    if((out.sr_before&0x301U)!=c.sr)return fail(index,"prepared M/Q/T",0U,out.sr_before&0x301U,c.sr);
    if(out.exit[2]!=c.macl||out.exit[3]!=c.mach||out.exit[4]!=c.gbr)return fail(index,"special registers",0U,1U,0U);
    if(out.sp!=out.abi_before[10]-164U||out.exit[1]!=out.continuation)return fail(index,"natural PR/SP",0U,1U,0U);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"outer ABI",0U,1U,0U);
    for(i=0;i<COUNT(abi_expected);++i)if(out.abi_before[i]!=abi_expected[i])return fail(index,"ABI sentinel",i,out.abi_before[i],abi_expected[i]);
    for(i=0;i<88U;++i)put32(initial,4U*i,0xa3b4c5d6U+17U*i);
    if(memcmp(initial,out.frame_before,sizeof(initial)))return fail(index,"complete initial frame",0U,1U,0U);
    memcpy(frame,cpu->frame,sizeof(frame));put32(frame,288U,out.continuation);
    for(i=0;i<352U;++i)if(out.frame_after[i]!=frame[i])return fail(index,"complete nested frame",i,out.frame_after[i],frame[i]);
    return memory(index,s);
}
int main(void){
    unsigned i;
    if(COUNT(memory_samples)!=FEEDBACK_CASE_COUNT||COUNT(cpu_samples)!=FEEDBACK_CASE_COUNT)return 1;
    for(i=0;i<FEEDBACK_CASE_COUNT;++i)if(!run_case(i))return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%u\n",REGION_KEY,FEEDBACK_CASE_COUNT);
    return 0;
}
