/* Actual bounded caller observations; independent semantic checks run on the host. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#include "coherent-copy-cases.h"

#define RAM_BASE 0x01000000U
#define ALIAS(a) (RAM_BASE+((a)&65535U))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
struct context { uint32_t r[15], gbr, mach, macl, entry_t; };
struct observation {
    uint32_t exit[20], sp, continuation, abi_before[12], abi_after[12];
    uint8_t frame_before[96], frame_after[96];
    uint32_t sr_before;
};
_Static_assert(sizeof(struct context)==76U,"complete prepared context");
_Static_assert(offsetof(struct context,entry_t)==72U,"prepared SR offset");
_Static_assert(sizeof(struct observation)==380U,"complete observer boundary");
_Static_assert(offsetof(struct observation,frame_before)==184U,"frame input offset");
_Static_assert(offsetof(struct observation,frame_after)==280U,"frame output offset");
_Static_assert(offsetof(struct observation,sr_before)==376U,"prepared SR offset");
_Static_assert(COHERENT_WINDOW_COUNT==15U,"bounded caller count");
_Static_assert(COHERENT_CASE_COUNT==17228U,"complete case count");
extern void stock_invoke_injection_start_delay(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[65536],pools_before[32];
static unsigned completed;
static const struct coherent_window *window=coherent_windows+WINDOW_INDEX;

static volatile uint8_t *ram(uint32_t address) {
    return (volatile uint8_t *)(uintptr_t)ALIAS(address);
}
static void words(const uint32_t *values,unsigned count) {
    unsigned i;
    putchar('[');
    for(i=0;i<count;++i)printf("%s%lu",i?",":"",(unsigned long)values[i]);
    putchar(']');
}
static void bytes(const uint8_t *values,unsigned count) {
    unsigned i;
    putchar('"');
    for(i=0;i<count;++i)printf("%02x",(unsigned)values[i]);
    putchar('"');
}
static void read_lanes(int before) {
    unsigned i;
    putchar('"');
    for(i=0;i<window->read_count;++i) {
        uint32_t address=coherent_read_addresses[window->read_start+i];
        uint8_t value=before?ram_before[address&65535U]:*ram(address);
        printf("%02x",(unsigned)value);
    }
    putchar('"');
}
static void destination(int before) {
    unsigned i;
    putchar('"');
    for(i=0;i<window->length;++i) {
        uint32_t address=window->destination+i;
        uint8_t value=before?ram_before[address&65535U]:*ram(address);
        printf("%02x",(unsigned)value);
    }
    putchar('"');
}
static void seed(const struct coherent_case *test) {
    unsigned i,j;
    if(!test->carry)
        for(i=0;i<65536U;++i)
            ((volatile uint8_t *)RAM_BASE)[i]=(uint8_t)(0x5dU+i*19U+(i>>8)+test->index);
    for(i=0;i<window->read_count;++i) {
        uint32_t address=coherent_read_addresses[window->read_start+i];
        *ram(address)=test->isolated!=0xffffffffU?(address==test->isolated?0x81U:0U):
            (uint8_t)(test->seed+i*29U);
    }
    for(i=0;i<65536U;++i)ram_before[i]=((volatile uint8_t *)RAM_BASE)[i];
    for(i=0;i<window->pool_count;++i) {
        uint32_t address=coherent_pool_addresses[window->pool_start+i];
        for(j=0;j<4U;++j)pools_before[i*4U+j]=((volatile uint8_t *)(uintptr_t)address)[j];
    }
}
static void run_case(unsigned local_index) {
    const struct coherent_case *test=coherent_cases+window->case_start+local_index;
    struct context context,before;
    struct observation out;
    unsigned i,j,changed=0;
    for(i=0;i<15U;++i)
        context.r[i]=test->variant?0xa9876543U+i*0x00130709U:0x28765430U+i*0x01030507U;
    context.r[7]=window->entry;
    for(i=0;i<15U;++i)
        if(window->context_mask&(1U<<i))context.r[i]=window->context[i];
    context.gbr=test->variant?0xd8b6a491U:0x456789abU;
    context.mach=test->variant?0xf1e2d3c4U:0x13579bdfU;
    context.macl=test->variant?0x9274b6d8U:0x2468ace0U;
    context.entry_t=test->entry_t;
    before=context;
    seed(test);
    memset(&out,0xa6,sizeof(out));
    stock_invoke_injection_start_delay(window->entry,&context,&out);
    printf("kb-coherent-copy-observation {\"index\":%u,\"call\":%lu,\"entry\":%lu,"
        "\"source\":%lu,\"destination\":%lu,\"length\":%lu,\"incoming\":",
        (unsigned int)test->index,(unsigned long)window->call,(unsigned long)window->entry,
        (unsigned long)window->source,(unsigned long)window->destination,(unsigned long)window->length);
    words(before.r,15U);
    printf(",\"incoming_after\":");words(context.r,15U);
    printf(",\"gbr\":%lu,\"mach\":%lu,\"macl\":%lu,\"entry_t\":%lu,"
        "\"gbr_after\":%lu,\"mach_after\":%lu,\"macl_after\":%lu,\"entry_t_after\":%lu,\"exit\":",
        (unsigned long)before.gbr,(unsigned long)before.mach,(unsigned long)before.macl,
        (unsigned long)before.entry_t,(unsigned long)context.gbr,(unsigned long)context.mach,
        (unsigned long)context.macl,(unsigned long)context.entry_t);
    words(out.exit,20U);
    printf(",\"sp\":%lu,\"continuation\":%lu,\"sr_before\":%lu,\"abi_before\":",
        (unsigned long)out.sp,(unsigned long)out.continuation,(unsigned long)out.sr_before);
    words(out.abi_before,12U);printf(",\"abi_after\":");words(out.abi_after,12U);
    printf(",\"frame_before\":");bytes(out.frame_before,96U);
    printf(",\"frame_after\":");bytes(out.frame_after,96U);
    printf(",\"read_before\":");read_lanes(1);
    printf(",\"read_after\":");read_lanes(0);
    printf(",\"destination_before\":");destination(1);
    printf(",\"destination_after\":");destination(0);
    printf(",\"pools_before\":");bytes(pools_before,window->pool_count*4U);
    printf(",\"pools_after\":\"");
    for(i=0;i<window->pool_count;++i) {
        uint32_t address=coherent_pool_addresses[window->pool_start+i];
        for(j=0;j<4U;++j)printf("%02x",(unsigned)((volatile uint8_t *)(uintptr_t)address)[j]);
    }
    printf("\",\"outside_changes\":[");
    for(i=0;i<65536U;++i) {
        unsigned destination=window->destination&65535U;
        uint8_t actual=((volatile uint8_t *)RAM_BASE)[i];
        if((i<destination||i>=destination+window->length)&&actual!=ram_before[i]) {
            printf("%s[%u,%u,%u]",changed?",":"",i,(unsigned)ram_before[i],(unsigned)actual);
            ++changed;
        }
    }
    printf("]}\n");
    ++completed;
}
int main(void) {
    unsigned i,expected;
    if(WINDOW_INDEX>=COHERENT_WINDOW_COUNT||window->pool_count*4U>sizeof(pools_before))return 1;
#if EARLY_ONLY
    expected=window->early_count;
    for(i=0;i<expected;++i)run_case(coherent_early_indices[window->early_start+i]);
#else
    expected=window->case_count;
    for(i=0;i<expected;++i)run_case(i);
#endif
    if(completed!=expected)return 1;
    printf("VQ_SH_ELF_COHERENT_COPY_CAPTURE call=%08lx cases=%u early=%s\n",
        (unsigned long)window->call,completed,EARLY_ONLY?"true":"false");
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%u\n",REGION_KEY,completed);
    return 0;
}
