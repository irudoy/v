/* Explicit natural fine-gopher inputs and complete actual state observations. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>

#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define GBR_BASE 0xFFFF8C00U
#define GBR_SIZE 256U
#define BLOCK_BASE 0xFFFF9900U
#define BLOCK_SIZE 512U
#define ARRAY_SIZE(value) (sizeof(value)/sizeof((value)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr,fifth; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
struct path_case {
    uint32_t entry,curve_c,curve_d,curve_a,curve_b,curve_e,coordinate,byte_coordinate,gate,left,right;
    uint32_t word_a,word_b,divisor,rom_ec,rom_66,block0,block8,blockc,block10,block14,block18,block1a;
    uint32_t block1c,block20,block24,port,variant,sr;
};
#include "fine-gopher-path-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"independent lookup fifth argument ABI");
_Static_assert(offsetof(struct context,fifth)==76U,"independent fifth argument offset");
_Static_assert(sizeof(struct observation)==572U,"complete observer ABI");
_Static_assert(offsetof(struct observation,frame_before)==184U,"entry frame offset");
_Static_assert(offsetof(struct observation,frame_after)==376U,"exit frame offset");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t ram_before[RAM_SIZE],gbr_before[GBR_SIZE],gbr_after[GBR_SIZE],block_before[BLOCK_SIZE],block_after[BLOCK_SIZE];
static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer; size_t index;
    for (index=0;index<size;++index) printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *bytes,size_t size)
{
    size_t start=0;
    while (start<size) {
        size_t end=start+1U;
        while (end<size && bytes[end]==bytes[start]) ++end;
        printf("%s%lu:%02x",start ? "," : "",(unsigned long)(end-start),(unsigned)bytes[start]);
        start=end;
    }
}
static uint8_t calibration_before[sizeof(fine_gopher_stock_calibrations)];
static void put_word(uint32_t address,uint32_t value)
{ *(volatile uint16_t *)(uintptr_t)address=(uint16_t)value; }
static void put_long(uint32_t address,uint32_t value)
{ *(volatile uint32_t *)(uintptr_t)address=value; }
static void write_curve(uint32_t address,uint32_t pattern)
{
    uint32_t index;
    if (pattern==0U) return;
    for (index=0;index<8U;++index) {
        uint32_t value=pattern==1U ? 0U : pattern==2U ? index*200U : pattern==3U ? 1000U : 4000U;
        put_word(address+index*2U,value);
    }
}
static void prepare(const struct path_case *input)
{
    static const uint32_t starts[]={0x1453aU,0x1454aU,0x14f42U,0x14f52U,0x15002U,0x15012U,0x13c38U,0x13c58U,0x13bd8U,0x13be8U,0x93e8U,0x93ecU,0x9066U};
    static const uint32_t sizes[]={16U,18U,16U,18U,16U,18U,16U,16U,16U,16U,2U,2U,2U};
    volatile uint8_t *ram=(volatile uint8_t *)(uintptr_t)RAM_BASE;
    unsigned index,offset=0;
    memset((void *)(uintptr_t)RAM_BASE,0,RAM_SIZE);
    memset((void *)(uintptr_t)GBR_BASE,0,GBR_SIZE);
    memset((void *)(uintptr_t)BLOCK_BASE,0,BLOCK_SIZE);
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy((void *)(uintptr_t)starts[index],fine_gopher_stock_calibrations+offset,sizes[index]);
        offset+=sizes[index];
    }
    write_curve(0x1453aU,input->curve_c); write_curve(0x1454aU,input->curve_d);
    write_curve(0x14f42U,input->curve_a); write_curve(0x14f52U,input->curve_b);
    write_curve(0x15002U,input->curve_e);
    put_word(0x93e8U,input->divisor); put_word(0x93ecU,input->rom_ec); put_word(0x9066U,input->rom_66);
    ram[0x4185U]=(uint8_t)(input->gate?0x40U:0U);
    ram[0x11d4U]=(uint8_t)input->left; ram[0x2365U]=(uint8_t)input->right; ram[0x1076U]=(uint8_t)input->byte_coordinate;
    ram[0x423eU]=(uint8_t)input->port;
    put_word(RAM_BASE+0x11f4U,input->coordinate);
    put_word(RAM_BASE+0x1026U,input->word_a); put_word(RAM_BASE+0x22e6U,input->word_b);
    put_long(RAM_BASE+0x9818U,0xa5c3d2e1U);
    put_long(RAM_BASE+0x99fcU,input->block0); put_long(RAM_BASE+0x9a04U,input->block8);
    put_long(RAM_BASE+0x9a08U,input->blockc); put_long(RAM_BASE+0x9a0cU,input->block10);
    put_long(RAM_BASE+0x9a10U,input->block14); put_word(RAM_BASE+0x9a14U,input->block18);
    put_word(RAM_BASE+0x9a16U,input->block1a); put_word(RAM_BASE+0x9a18U,input->block1c);
    put_long(RAM_BASE+0x9a1cU,input->block20); put_long(RAM_BASE+0x9a20U,input->block24);
    memcpy((void *)(uintptr_t)GBR_BASE,(const void *)(uintptr_t)(RAM_BASE+0x8c00U),GBR_SIZE);
    memcpy((void *)(uintptr_t)BLOCK_BASE,(const void *)(uintptr_t)(RAM_BASE+0x9900U),BLOCK_SIZE);
    offset=0;
    for (index=0;index<ARRAY_SIZE(starts);++index) {
        memcpy(calibration_before+offset,(const void *)(uintptr_t)starts[index],sizes[index]);
        offset+=sizes[index];
    }
}
static void calibration_after(void)
{
    hex((const void *)(uintptr_t)0x1453aU,16U); hex((const void *)(uintptr_t)0x1454aU,18U);
    hex((const void *)(uintptr_t)0x14f42U,16U); hex((const void *)(uintptr_t)0x14f52U,18U);
    hex((const void *)(uintptr_t)0x15002U,16U); hex((const void *)(uintptr_t)0x15012U,18U);
    hex((const void *)(uintptr_t)0x13c38U,16U); hex((const void *)(uintptr_t)0x13c58U,16U);
    hex((const void *)(uintptr_t)0x13bd8U,16U); hex((const void *)(uintptr_t)0x13be8U,16U);
    hex((const void *)(uintptr_t)0x93e8U,2U); hex((const void *)(uintptr_t)0x93ecU,2U); hex((const void *)(uintptr_t)0x9066U,2U);
}
static int observe(size_t index)
{
    const struct path_case *input=&fine_gopher_cases[index];
    struct context context,initial; struct observation observation; unsigned reg;
    prepare(input);
    for (reg=0;reg<15U;++reg) context.r[reg]=0x1728394aU+reg*0x110203U+input->variant*0x1000101U;
    context.gbr=0x12344321U; context.mach=0x13579bdfU; context.macl=0x2468ace0U;
    context.entry_sr=input->sr; context.fifth=0xb6c70000U|input->coordinate;
    initial=context;
    memcpy(ram_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
    memcpy(gbr_before,(const void *)(uintptr_t)GBR_BASE,GBR_SIZE);
    memcpy(block_before,(const void *)(uintptr_t)BLOCK_BASE,BLOCK_SIZE);
    memset(&observation,0xa6,sizeof(observation));
    stock_invoke_ignition_consumer(input->entry,&context,&observation);
    memcpy(gbr_after,(const void *)(uintptr_t)GBR_BASE,GBR_SIZE);
    memcpy(block_after,(const void *)(uintptr_t)BLOCK_BASE,BLOCK_SIZE);
    if (memcmp(&initial,&context,sizeof(context))) return 0;
    printf("kb-fine-gopher-observation {\"schema\":1,\"index\":%lu,\"kind\":0,\"entry\":%lu,\"context\":\"",
           (unsigned long)index,(unsigned long)input->entry);
    hex(&initial,sizeof(initial));
    printf("\",\"context_after\":\""); hex(&context,sizeof(context));
    printf("\",\"observation\":\""); hex(&observation,sizeof(observation));
    printf("\",\"ram_before\":\""); rle(ram_before,RAM_SIZE);
    printf("\",\"ram_after\":\""); rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
    printf("\",\"gbr_before\":\""); hex(gbr_before,GBR_SIZE);
    printf("\",\"gbr_after\":\""); hex(gbr_after,GBR_SIZE);
    printf("\",\"block_before\":\""); hex(block_before,BLOCK_SIZE);
    printf("\",\"block_after\":\""); hex(block_after,BLOCK_SIZE);
    printf("\",\"calibration_before\":\""); hex(calibration_before,sizeof(calibration_before));
    printf("\",\"calibration_after\":\""); calibration_after();
    printf("\"}\n");
    return 1;
}
int main(void)
{
    size_t index;
    for (index=0;index<ARRAY_SIZE(fine_gopher_cases);++index)
        if (!observe(index)) return 1;
    printf("VQ_SH_ELF_FINE_GOPHER status=PASS region=%s cases=%lu\n",
           FINE_GOPHER_REGION,(unsigned long)ARRAY_SIZE(fine_gopher_cases));
    return 0;
}
