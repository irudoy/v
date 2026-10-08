/* Exact bounded RPM word/byte publishers and 56-byte scheduler copy. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "rpm-phase-pools.h"
#ifndef EARLY_ONLY
#define EARLY_ONLY 0
#endif
#define RAM_BASE 0x01000000U
#define RAM_WORDS 16384U
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define ACTIVE_CASE_COUNT (EARLY_ONLY ? 16U : (VIEW_KIND==2U ? 2048U : 65536U))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete entry context");
_Static_assert(sizeof(struct observation)==572U,"complete observation");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame before offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"frame after offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"full SR offset");
extern void stock_invoke_oneshot(uint32_t,const struct context *,struct observation *);
static uint32_t ram_template[RAM_WORDS],ram_before[RAM_WORDS],ram_expected[RAM_WORDS];
static uint8_t pools_before[20];
static unsigned long completed;
static const uint32_t abi_expected[10]={
    0x18283848U,0x19293949U,0x1a2a3a4aU,0x1b2b3b4bU,
    0x1c2c3c4cU,0x1d2d3d4dU,0x1e2e3e4eU,0x12344321U,0x10203040U,0x50607080U
};
static volatile uint8_t *ram(uint32_t address){return (volatile uint8_t *)(uintptr_t)(RAM_BASE+(address&65535U));}
static uint32_t reg(const struct observation *out,unsigned index){return out->exit[19U-index];}
static void set16(volatile uint8_t *p,uint32_t value){p[0]=(uint8_t)(value>>8);p[1]=(uint8_t)value;}
static uint32_t get32(const uint8_t *p){return (uint32_t)p[0]<<24|(uint32_t)p[1]<<16|(uint32_t)p[2]<<8|p[3];}
static void frame_set(uint8_t *p,unsigned at,uint32_t value){
    p[at]=(uint8_t)(value>>24);p[at+1]=(uint8_t)(value>>16);
    p[at+2]=(uint8_t)(value>>8);p[at+3]=(uint8_t)value;
}
static int fail(unsigned long index,const char *field,uint32_t actual,uint32_t expected){
    fprintf(stderr,"rpm_phase_%u[%lu] %s actual=%08lx expected=%08lx\n",VIEW_KIND,index,field,
            (unsigned long)actual,(unsigned long)expected);return 0;
}
static int initial(void){
    unsigned i;uint8_t *bytes=(uint8_t *)ram_template;
    if(INPUT_WORD!=0xffff1196U || WORK_WORD!=0xffff11e8U || WORK_BYTE!=0xffff11ebU || SNAPSHOT_BYTE!=0xffff11b3U)return 0;
    for(i=0;i<sizeof(ram_template);++i)bytes[i]=(uint8_t)(0x5dU+i*19U+(i>>8));
    if(VIEW_KIND==0U)return REGION_ENTRY==0x38506U && *(volatile uint32_t *)0x385a8U==0x010011d4U
        && *(volatile uint32_t *)0x385b4U==0x01001196U && *(volatile uint32_t *)0x385b8U==0x8743U
        && *(volatile uint8_t *)0x8743U==255U;
    if(VIEW_KIND==1U)return REGION_ENTRY==0x384ccU && *(volatile uint32_t *)0x385a8U==0x010011d4U;
    return REGION_ENTRY==0x20f60U && *(volatile uint32_t *)0x21154U==0x0100119cU
        && *(volatile uint32_t *)0x21158U==0x01001196U && *(volatile uint32_t *)0x2115cU==0x010011d4U
        && *(volatile uint32_t *)0x22110U==0x22158U && *(volatile uint32_t *)0x22190U==0x2211eU;
}
static int run_case(unsigned long index){
    struct context context,before;struct observation out;
    uint32_t expected[15],word=(uint32_t)index,expected_sr,value,variant=(uint32_t)index&1U;
    uint8_t expected_frame[192],*expected_bytes=(uint8_t *)ram_expected;
    unsigned i,j,at=0;uint32_t coefficient=(uint32_t)index&255U;
    static const uint16_t early[16]={0,1,7,8,15,16,127,128,1919,1920,4095,4096,32767,32768,65534,65535};
    if(EARLY_ONLY)word=early[index];
    else if(VIEW_KIND==2U)word=((uint32_t)index&511U)*128U+((uint32_t)index>>9);
    for(i=0;i<15U;++i)context.r[i]=0x1728394aU+i*0x1020305U+(uint32_t)index*0x101U;
    context.gbr=variant?0x01004567U:0x01003579U;
    context.mach=variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=variant?0x9274b6d8U:0x2468ace0U;
    context.entry_sr=((uint32_t)index&1U)|(((uint32_t)index&30U)<<3)|(((uint32_t)index&96U)<<3);
    memcpy((void *)(uintptr_t)RAM_BASE,ram_template,sizeof(ram_template));
    if(VIEW_KIND==0U){set16(ram(0x1196U),word);*(volatile uint8_t *)0x8743U=(uint8_t)coefficient;}
    if(VIEW_KIND==1U)set16(ram(0x11e8U),word);
    if(VIEW_KIND==2U){
        context.r[4]=0x01001194U;context.r[6]=0x01001198U;context.r[14]=0x220f8U;
        for(i=0;i<56U;++i)ram(0x11d4U)[i]=(uint8_t)(i*37U+(uint32_t)index*19U+((uint32_t)index>>8));
        value=word/128U;if(value>255U)value=255U;*ram(0x11ebU)=(uint8_t)value;
        set16(ram(0x1196U),word);
    }
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,sizeof(ram_before));
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j)pools_before[at++]=((volatile uint8_t *)(uintptr_t)pools[i].at)[j];
    before=context;memcpy(expected,context.r,sizeof(expected));memset(&out,0xa6,sizeof(out));
    stock_invoke_oneshot(REGION_ENTRY,&context,&out);
    if(memcmp(&context,&before,sizeof(context)))return fail(index,"immutable complete entry context",1,0);
    if((out.sr_before&0x3f1U)!=context.entry_sr)
        return fail(index,"actual prepared I/M/Q/T",out.sr_before&0x3f1U,context.entry_sr);
    memcpy(ram_expected,ram_before,sizeof(ram_expected));
    memcpy(expected_frame,out.frame_before,sizeof(expected_frame));
    expected_sr=out.sr_before;
    if(VIEW_KIND==0U){
        value=word/8U;expected[0]=value;expected[2]=coefficient<128U?coefficient:coefficient-256U;
        expected[6]=0x8743U;expected[13]=value;set16(expected_bytes+0x11e8U,value);
        expected_sr=(out.sr_before&~1U)|((word/4U)&1U);
    }else if(VIEW_KIND==1U){
        value=word/16U;expected_sr=(out.sr_before&~1U)|(value>255U);
        if(value>255U)value=255U;
        expected[0]=23U;expected[2]=255U;expected[5]=0x010011d4U;expected[6]=value;
        expected_bytes[0x11ebU]=(uint8_t)value;
    }else{
        memcpy(expected_bytes+0x119cU,((uint8_t *)ram_before)+0x11d4U,56U);
        set16(expected_bytes+0x1198U,context.r[2]);set16(expected_bytes+0x1194U,word);
        expected[0]=get32(((uint8_t *)ram_before)+0x11d8U);expected[1]=0x0100119cU;
        expected[2]=0x010011d4U;expected[6]=0x01001196U;expected[11]=out.continuation;
        frame_set(expected_frame,156,context.r[3]);
    }
    for(i=0;i<15U;++i)
        if(reg(&out,i)!=expected[i])return fail(index,"complete GPR",reg(&out,i),expected[i]);
    if(out.exit[0]!=expected_sr)return fail(index,"complete SR",out.exit[0],expected_sr);
    if(out.exit[2]!=context.macl || out.exit[3]!=context.mach
       || out.exit[4]!=(VIEW_KIND==0U?0x010011d4U:context.gbr))
        return fail(index,"complete MACL/MACH/GBR state",1,0);
    if(out.sp!=out.abi_before[10]-164U || out.exit[1]!=out.continuation)
        return fail(index,"exact boundary or natural PR and SP",1,0);
    if(memcmp(out.abi_before,out.abi_after,sizeof(out.abi_before)))return fail(index,"independent C caller ABI",1,0);
    for(i=0;i<ARRAY_SIZE(abi_expected);++i)
        if(out.abi_before[i]!=abi_expected[i])return fail(index,"outer ABI sentinel",out.abi_before[i],abi_expected[i]);
    if(memcmp(out.frame_after,expected_frame,sizeof(expected_frame)))
        for(i=0;i<sizeof(expected_frame);++i)
            if(out.frame_after[i]!=expected_frame[i])return fail(index,"complete frame and neighbors",i,expected_frame[i]);
    for(i=0;i<RAM_WORDS;++i)
        if(((volatile uint32_t *)(uintptr_t)RAM_BASE)[i]!=ram_expected[i])
            return fail(index,"all 65536 RAM bytes and exact copy destinations",4U*i,ram_expected[i]);
    at=0;
    for(i=0;i<ARRAY_SIZE(pools);++i)
        for(j=0;j<pools[i].size;++j,++at)
            if(((volatile uint8_t *)(uintptr_t)pools[i].at)[j]!=pools_before[at])
                return fail(index,"all bound ROM inputs and pools",pools[i].at+j,pools_before[at]);
    ++completed;return 1;
}
int main(void){
    unsigned long i;
    if(!initial())return 1;
    for(i=0;i<ACTIVE_CASE_COUNT;++i)if(!run_case(i))return 1;
    if(completed!=ACTIVE_CASE_COUNT)return 1;
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\n",REGION_KEY,completed);return 0;
}
