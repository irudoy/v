/* One prepared stock-memory case and two complete ordinary observer phases. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(v) (sizeof(v)/sizeof((v)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr,fifth; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];uint32_t sr_before;
};
struct span { uint32_t address,size; };
#include "torque-correction-ratio-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete phase context");
_Static_assert(sizeof(struct observation)==572U,"unchanged ordinary observer");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete entry frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete exit frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete SR input");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
struct phase_record {
    struct context before,after;struct observation out;
    uint8_t ram_before[RAM_SIZE],ram_after[RAM_SIZE];
    uint8_t cal_before[QUANTITY_CALIBRATION_SIZE],cal_after[QUANTITY_CALIBRATION_SIZE];
    uint8_t bound_before[QUANTITY_BOUND_SIZE],bound_after[QUANTITY_BOUND_SIZE];
};
static struct phase_record phases[2];
static const uint32_t entries[2]={0x658A4U,0x64A1CU};
static const char *const names[2]={"producer","consumer"};

static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t n;
    for(n=0;n<size;++n)printf("%02x",(unsigned)data[n]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t start=0;
    while(start<size){size_t end=start+1U;while(end<size&&data[start]==data[end])++end;
        printf("%s%lu:%02x",start?",":"",(unsigned long)(end-start),(unsigned)data[start]);start=end;}
}
static void snapshot(uint8_t *output,const struct span *spans,size_t count)
{
    size_t i,offset=0;
    for(i=0;i<count;++i){memcpy(output+offset,(const void *)(uintptr_t)spans[i].address,spans[i].size);offset+=spans[i].size;}
}
static void prepare(const struct path_case *input)
{
    size_t i,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0xA5,RAM_SIZE);
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11BCU)=(uint16_t)input->word_11bc;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4181U)=(uint8_t)input->byte_4181;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1071U)=(uint8_t)input->byte_1071;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2772U)=(uint8_t)input->byte_2772;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11B3U)=(uint8_t)input->byte_11b3;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x199EU)=(uint16_t)input->word_199e;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19C6U)=(uint16_t)input->word_19c6;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2408U)=(uint16_t)input->word_2408;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x2410U)=(uint16_t)input->word_2410;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24A3U)=(uint8_t)input->byte_24a3;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x18D4U)=(uint16_t)input->word_18d4;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x16A3U)=(uint8_t)input->byte_16a3;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19CCU)=(uint16_t)input->word_19cc;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x34B8U)=(uint16_t)input->word_34b8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x14E2U)=(uint16_t)input->prior_14e2;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x14E4U)=(uint16_t)input->prior_14e4;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1608U)=(uint16_t)input->prior_1608;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19A0U)=(uint16_t)input->prior_19a0;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x34D6U)=(uint16_t)input->prior_34d6;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x186CU)=(uint8_t)input->prior_186c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1864U)=(uint8_t)input->prior_1864;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19F6U)=(uint16_t)input->history_0;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19F8U)=(uint16_t)input->history_1;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19FAU)=(uint16_t)input->history_2;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19FCU)=(uint16_t)input->history_3;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19FEU)=(uint16_t)input->history_4;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1A00U)=(uint16_t)input->history_5;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1A02U)=(uint16_t)input->history_6;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1A04U)=(uint16_t)input->history_7;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1A06U)=(uint16_t)input->history_8;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1A08U)=(uint16_t)input->history_9;
    for(i=0;i<ARRAY_SIZE(quantity_calibration);++i){
        memcpy((void *)(uintptr_t)quantity_calibration[i].address,
            quantity_calibration_inputs[input->calibration_index]+offset,quantity_calibration[i].size);
        offset+=quantity_calibration[i].size;
    }
}
static void invoke_phase(unsigned phase,const struct context *input)
{
    struct phase_record *record=&phases[phase];struct context context=*input;
    record->before=context;memset(&record->out,0xA6,sizeof(record->out));
    memcpy(record->ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot(record->cal_before,quantity_calibration,ARRAY_SIZE(quantity_calibration));
    snapshot(record->bound_before,quantity_bound,ARRAY_SIZE(quantity_bound));
    stock_invoke_ignition_consumer(entries[phase],&context,&record->out);
    record->after=context;
    memcpy(record->ram_after,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    snapshot(record->cal_after,quantity_calibration,ARRAY_SIZE(quantity_calibration));
    snapshot(record->bound_after,quantity_bound,ARRAY_SIZE(quantity_bound));
}
static void print_phase(size_t pair,unsigned phase)
{
    const struct phase_record *record=&phases[phase];
    printf("kb-torque-correction-ratio-observation {\"schema\":1,\"pair\":%lu,\"phase\":%u,\"phase_id\":\"%s\",\"entry\":%lu,\"context\":\"",
        (unsigned long)pair,phase,names[phase],(unsigned long)entries[phase]);
    hex(&record->before,sizeof(record->before));printf("\",\"context_after\":\"");hex(&record->after,sizeof(record->after));
    printf("\",\"observation\":\"");hex(&record->out,sizeof(record->out));
    printf("\",\"ram_before\":\"");rle(record->ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\"");rle(record->ram_after,RAM_SIZE);
    printf("\",\"calibration_before\":\"");hex(record->cal_before,sizeof(record->cal_before));
    printf("\",\"calibration_after\":\"");hex(record->cal_after,sizeof(record->cal_after));
    printf("\",\"bound_before\":\"");hex(record->bound_before,sizeof(record->bound_before));
    printf("\",\"bound_after\":\"");hex(record->bound_after,sizeof(record->bound_after));printf("\"}\n");
}
int main(void)
{
    size_t pair;
    for(pair=0;pair<ARRAY_SIZE(quantity_cases);++pair){
        const struct path_case *input=&quantity_cases[pair];
        prepare(input);
        invoke_phase(0U,&input->contexts[0]);
        invoke_phase(1U,&input->contexts[1]);
        print_phase(pair,0U);print_phase(pair,1U);
    }
    printf("VQ_SH_ELF_TORQUE_CORRECTION_RATIO status=PASS region=jk08a-torque-correction-ratio-paths pairs=%lu phases=%lu\n",
        (unsigned long)pair,(unsigned long)(2U*pair));return 0;
}
