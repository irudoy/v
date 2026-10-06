/* Natural stock start-delay publication with literal output and preservation contracts. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "stock-jk08a-injection-start-delay-cases.h"
#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&0xffffU))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_t; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[96],frame_after[96];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"context byte contract");
_Static_assert(offsetof(struct context,entry_t)==72U,"prepared SR input offset");
_Static_assert(sizeof(struct observation)==380U,"observation byte contract");
_Static_assert(offsetof(struct observation,sp)==80U,"SP observation offset");
_Static_assert(offsetof(struct observation,continuation)==84U,"continuation observation offset");
_Static_assert(offsetof(struct observation,abi_before)==88U,"caller ABI before offset");
_Static_assert(offsetof(struct observation,abi_after)==136U,"caller ABI after offset");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before offset");
_Static_assert(offsetof(struct observation,frame_after)==280U,"frame after offset");
_Static_assert(offsetof(struct observation,sr_before)==376U,"actual prepared SR observation offset");
extern void stock_invoke_injection_start_delay(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[65536],calibration_before[63];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static const struct { uint32_t at,size; } calibrations[]={
    {DELAY_CONFIG,1},{0x52296U,2},
    {0x52298U,4},{0x5229cU,4},{0x522a0U,4},{0x522a4U,4},{0x522a8U,4},
    {0x522acU,4},{0x522b0U,4},{0x522b4U,4},{0x522b8U,4},{0x522bcU,4},{0x522c0U,4},
    {0x21cd8U,4},{0x21cdcU,4},{0x21f38U,4},{0x21f3cU,4}
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
static int fail(unsigned long i,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"injection_start_delay[%lu] %s actual=%08lx expected=%08lx\n",i,field,(unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;
    static const struct { uint32_t at,value; } pools[]={
        {0x52298U,0x010023bcU},{0x5229cU,0x01004184U},{0x522a0U,0x01001094U},
        {0x522a4U,0x0100119cU},{0x522a8U,0x0000c49bU},{0x522acU,0x0100128cU},
        {0x522b0U,0x010024c8U},{0x522b4U,0x000083eaU},{0x522b8U,0x00021bbcU},
        {0x522bcU,0x00021e14U},{0x522c0U,0x0100424cU},
        {0x21cd8U,0x01009818U},{0x21cdcU,0x0000044eU},{0x21f38U,0x01009818U},{0x21f3cU,0x0000044eU}
    };
    if(*(volatile uint8_t *)DELAY_CONFIG!=30U || *(volatile uint16_t *)0x52296U!=0x06a2U)
        return fail(0,"bound factory byte/word",1,0);
    for(i=0;i<ARRAY_SIZE(pools);++i)
        if(*(volatile uint32_t *)pools[i].at!=pools[i].value)
            return fail(i,"stock constant/helper target/declared RAM alias",*(volatile uint32_t *)pools[i].at,pools[i].value);
    return 1;
}
static void seed(unsigned long index,const struct injection_start_delay_case *t){
    unsigned i,j,at=0;
    for(i=0;i<65536U;++i)((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*29U+(i>>8)+index);
    set16(PRIMARY_SPEED,t->speed[0]);set16(ALTERNATE_SPEED,t->speed[1]);
    for(i=0;i<6U;++i)set16(PULSES+2U*i,t->pulses[i]);
    set16(FLOOR,t->floor);set16(END,t->end);
    *ram(SPEED_SELECTOR)=t->flags[0];*ram(DELAY_CONTROL)=t->flags[1];*ram(LEAD_OVERRIDE)=t->flags[2];
    *(volatile uint8_t *)DELAY_CONFIG=t->delay_byte;
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j)
            calibration_before[at++]=((volatile uint8_t *)calibrations[i].at)[j];
}
static struct context make_context(const struct injection_start_delay_case *t){
    struct context c;unsigned i;
    for(i=0;i<15U;++i)c.r[i]=t->variant?0xa9876543U+i*0x00130709U:0x28765430U+i*0x01030507U;
    c.r[7]=REGION_ENTRY;
    c.gbr=t->variant?0xd8b6a491U:0x456789abU;
    c.mach=t->variant?0xf1e2d3c4U:0x13579bdfU;
    c.macl=t->variant?0x9274b6d8U:0x2468ace0U;
    c.entry_t=t->entry_t;
    return c;
}
static int preservation(unsigned long index){
    unsigned i,j,at=0;
    for(i=0;i<65536U;++i)
        if(i!=(ANGLE_OUTPUT&0xffffU) && i!=(LEAD_OUTPUT&0xffffU) && ((volatile uint8_t *)RAM_BASE)[i]!=ram_before[i])
            return fail(index,"full RAM/input/sibling/error-record preservation",i,ram_before[i]);
    for(i=0;i<ARRAY_SIZE(calibrations);++i)
        for(j=0;j<calibrations[i].size;++j,++at)
            if(((volatile uint8_t *)calibrations[i].at)[j]!=calibration_before[at])
                return fail(index,"all calibration/constant/pool preservation",
                            ((volatile uint8_t *)calibrations[i].at)[j],calibration_before[at]);
    return 1;
}
static int run_case(unsigned long index,const struct injection_start_delay_case *t){
    struct context c=make_context(t),before=c;
    struct observation out;
    uint8_t expected_frame[96];unsigned i;char field[40];
    uint32_t expected_sr=(uint32_t)t->sr_controlled;
    seed(index,t);memset(&out,0xa6,sizeof(out));
    stock_invoke_injection_start_delay(c.r[7],&c,&out);
    if(memcmp(&c,&before,sizeof(c)))return fail(index,"entry context preservation",1,0);
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=t->expected[i]){
            snprintf(field,sizeof(field),"literal full GPR R%u",i);
            return fail(index,field,reg(&out,i),t->expected[i]);
        }
    if((out.sr_before&0x301U)!=t->entry_t)
        return fail(index,"actual prepared incoming M/Q/T",out.sr_before&0x301U,t->entry_t);
    expected_sr|=out.sr_before&~0x301U;
    if(out.exit[0]!=expected_sr)return fail(index,"literal full SR with retained mode bits",out.exit[0],expected_sr);
    if(out.exit[2]!=c.macl || out.exit[3]!=c.mach || out.exit[4]!=c.gbr)
        return fail(index,"stock MACL/MACH/GBR preservation",1,0);
    if(out.sp!=out.abi_before[10]-164U)return fail(index,"natural stock SP",out.sp,out.abi_before[10]-164U);
    if(out.exit[1]!=out.continuation)return fail(index,"natural stock PR",out.exit[1],out.continuation);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"distinct C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    if(*ram(ANGLE_OUTPUT)!=t->angle)return fail(index,"literal angle byte",*ram(ANGLE_OUTPUT),t->angle);
    if(*ram(LEAD_OUTPUT)!=t->lead)return fail(index,"literal lead byte",*ram(LEAD_OUTPUT),t->lead);
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    frame_set(expected_frame,60,c.r[14]);
    frame_set(expected_frame,56,out.continuation);
    frame_set(expected_frame,52,c.macl);frame_set(expected_frame,48,c.gbr);
    frame_set(expected_frame,40,t->actual_delay);frame_set(expected_frame,44,t->expected[0]);
    frame_set(expected_frame,36,0x21e14U);frame_set(expected_frame,32,c.r[3]);
    if(t->long_path)frame_set(expected_frame,28,t->expected[4]);
    for(i=0;i<96U;++i)
        if(out.frame_after[i]!=expected_frame[i])
            return fail(index,"complete literal frame/save/local/neighbors",out.frame_after[i],expected_frame[i]);
    if(word(out.frame_before,88)!=out.continuation || word(out.frame_after,88)!=out.continuation)
        return fail(index,"disjoint independent continuation slot",1,0);
    if(!preservation(index))return 0;
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(!initial())return 1;
    for(i=0;i<ARRAY_SIZE(injection_start_delay_cases);++i)
        if(!run_case(i,&injection_start_delay_cases[i]))return 1;
    if(completed!=INJECTION_START_DELAY_CASE_COUNT)return !fail(0,"case count",completed,INJECTION_START_DELAY_CASE_COUNT);
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-injection-start-delay cases=%lu\n",completed);
    return 0;
}
