/* Input driver defined by defs/JK08A.map-bias-division-caller-withdrawal-paths.toml. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(value) (sizeof(value)/sizeof((value)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr,fifth; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
struct span { uint32_t address,size; };
#include "map-bias-division-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[MAP_BIAS_DIVISION_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[MAP_BIAS_DIVISION_CALLER_WITHDRAWAL_BOUND_SIZE];
static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t index;
    for(index=0;index<size;++index)printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t first=0;
    while(first<size){
        size_t last=first+1U;
        while(last<size && data[last]==data[first])++last;
        printf("%s%lu:%02x",first ? "," : "",(unsigned long)(last-first),(unsigned)data[first]);
        first=last;
    }
}
static void snapshot(uint8_t *output,const struct span *spans,size_t count)
{
    size_t index,offset=0;
    for(index=0;index<count;++index){
        memcpy(output+offset,(const void *)(uintptr_t)spans[index].address,spans[index].size);
        offset+=spans[index].size;
    }
}
static void print_spans(const struct span *spans,size_t count)
{
    size_t index;
    for(index=0;index<count;++index)hex((const void *)(uintptr_t)spans[index].address,spans[index].size);
}
static int prepare(const struct path_case *input)
{
    size_t index,offset=0;
    if((input->entry!=0x702c6U) || input->kind>=1U || input->word_142a>0xffffU || input->word_1702>0xffffU || input->word_1878>0xffffU || input->byte_1880>0xffU || input->word_188c>0xffffU || input->byte_18b4>0xffU || input->word_19c4>0xffffU || input->word_243a>0xffffU || input->map_word_000>0xffffU || input->map_word_001>0xffffU || input->map_word_002>0xffffU || input->map_word_003>0xffffU || input->map_word_004>0xffffU || input->map_word_005>0xffffU || input->map_word_006>0xffffU || input->map_word_007>0xffffU || input->map_word_008>0xffffU || input->map_word_009>0xffffU || input->map_word_010>0xffffU || input->map_word_011>0xffffU || input->map_word_012>0xffffU || input->map_word_013>0xffffU || input->map_word_014>0xffffU || input->map_word_015>0xffffU || input->map_word_016>0xffffU || input->map_word_017>0xffffU || input->map_word_018>0xffffU || input->map_word_019>0xffffU || input->map_word_020>0xffffU || input->map_word_021>0xffffU || input->map_word_022>0xffffU || input->map_word_023>0xffffU || input->map_word_024>0xffffU || input->map_word_025>0xffffU || input->map_word_026>0xffffU || input->map_word_027>0xffffU || input->map_word_028>0xffffU || input->map_word_029>0xffffU || input->map_word_030>0xffffU || input->map_word_031>0xffffU || input->map_word_032>0xffffU || input->map_word_033>0xffffU || input->map_word_034>0xffffU || input->map_word_035>0xffffU || input->map_word_036>0xffffU || input->map_word_037>0xffffU || input->map_word_038>0xffffU || input->map_word_039>0xffffU || input->map_word_040>0xffffU || input->map_word_041>0xffffU || input->map_word_042>0xffffU || input->map_word_043>0xffffU || input->map_word_044>0xffffU || input->map_word_045>0xffffU || input->map_word_046>0xffffU || input->map_word_047>0xffffU || input->map_word_048>0xffffU || input->map_word_049>0xffffU || input->map_word_050>0xffffU || input->map_word_051>0xffffU || input->map_word_052>0xffffU || input->map_word_053>0xffffU || input->map_word_054>0xffffU || input->map_word_055>0xffffU || input->map_word_056>0xffffU || input->map_word_057>0xffffU || input->map_word_058>0xffffU || input->map_word_059>0xffffU || input->map_word_060>0xffffU || input->map_word_061>0xffffU || input->map_word_062>0xffffU || input->map_word_063>0xffffU || input->map_word_064>0xffffU || input->map_word_065>0xffffU || input->map_word_066>0xffffU || input->map_word_067>0xffffU || input->map_word_068>0xffffU || input->map_word_069>0xffffU || input->map_word_070>0xffffU || input->map_word_071>0xffffU || input->map_word_072>0xffffU || input->map_word_073>0xffffU || input->map_word_074>0xffffU || input->map_word_075>0xffffU || input->map_word_076>0xffffU || input->map_word_077>0xffffU || input->map_word_078>0xffffU || input->map_word_079>0xffffU || input->map_word_080>0xffffU || input->map_word_081>0xffffU || input->map_word_082>0xffffU || input->map_word_083>0xffffU || input->map_word_084>0xffffU || input->map_word_085>0xffffU || input->map_word_086>0xffffU || input->map_word_087>0xffffU || input->map_word_088>0xffffU || input->map_word_089>0xffffU || input->map_word_090>0xffffU || input->map_word_091>0xffffU || input->map_word_092>0xffffU || input->map_word_093>0xffffU || input->map_word_094>0xffffU || input->map_word_095>0xffffU || input->map_word_096>0xffffU || input->map_word_097>0xffffU || input->map_word_098>0xffffU || input->map_word_099>0xffffU || input->map_word_100>0xffffU || input->map_word_101>0xffffU || input->map_word_102>0xffffU || input->map_word_103>0xffffU || input->map_word_104>0xffffU || input->map_word_105>0xffffU || input->map_word_106>0xffffU || input->map_word_107>0xffffU || input->map_word_108>0xffffU || input->map_word_109>0xffffU || input->map_word_110>0xffffU || input->map_word_111>0xffffU || input->map_word_112>0xffffU || input->map_word_113>0xffffU || input->map_word_114>0xffffU || input->map_word_115>0xffffU || input->map_word_116>0xffffU || input->map_word_117>0xffffU || input->map_word_118>0xffffU || input->map_word_119>0xffffU || input->map_word_120>0xffffU || input->map_word_121>0xffffU || input->map_word_122>0xffffU || input->map_word_123>0xffffU || input->map_word_124>0xffffU || input->map_word_125>0xffffU || input->map_word_126>0xffffU || input->map_word_127>0xffffU || input->map_word_128>0xffffU || input->map_word_129>0xffffU || input->map_word_130>0xffffU || input->map_word_131>0xffffU || input->map_word_132>0xffffU || input->map_word_133>0xffffU || input->map_word_134>0xffffU || input->map_word_135>0xffffU || input->map_word_136>0xffffU || input->map_word_137>0xffffU || input->map_word_138>0xffffU || input->map_word_139>0xffffU || input->map_word_140>0xffffU || input->map_word_141>0xffffU || input->map_word_142>0xffffU || input->map_word_143>0xffffU || input->map_word_144>0xffffU || input->map_word_145>0xffffU || input->map_word_146>0xffffU || input->map_word_147>0xffffU || input->map_word_148>0xffffU || input->map_word_149>0xffffU || input->map_word_150>0xffffU || input->map_word_151>0xffffU || input->map_word_152>0xffffU || input->map_word_153>0xffffU || input->map_word_154>0xffffU || input->map_word_155>0xffffU || input->map_word_156>0xffffU || input->map_word_157>0xffffU || input->map_word_158>0xffffU || input->map_word_159>0xffffU || input->map_word_160>0xffffU || input->map_word_161>0xffffU || input->map_word_162>0xffffU || input->map_word_163>0xffffU || input->map_word_164>0xffffU || input->map_word_165>0xffffU || input->map_word_166>0xffffU || input->map_word_167>0xffffU || input->map_word_168>0xffffU || input->map_word_169>0xffffU || input->map_word_170>0xffffU || input->map_word_171>0xffffU || input->map_word_172>0xffffU || input->map_word_173>0xffffU || input->map_word_174>0xffffU || input->map_word_175>0xffffU || input->map_word_176>0xffffU || input->map_word_177>0xffffU || input->map_word_178>0xffffU || input->map_word_179>0xffffU || input->map_word_180>0xffffU || input->map_word_181>0xffffU || input->map_word_182>0xffffU || input->map_word_183>0xffffU || input->map_word_184>0xffffU || input->map_word_185>0xffffU || input->map_word_186>0xffffU || input->map_word_187>0xffffU || input->map_word_188>0xffffU || input->map_word_189>0xffffU || input->map_word_190>0xffffU || input->map_word_191>0xffffU || input->map_word_192>0xffffU || input->map_word_193>0xffffU || input->map_word_194>0xffffU || input->map_word_195>0xffffU || input->map_word_196>0xffffU || input->map_word_197>0xffffU || input->map_word_198>0xffffU || input->map_word_199>0xffffU || input->map_word_200>0xffffU || input->map_word_201>0xffffU || input->map_word_202>0xffffU || input->map_word_203>0xffffU || input->map_word_204>0xffffU || input->map_word_205>0xffffU || input->map_word_206>0xffffU || input->map_word_207>0xffffU || input->map_word_208>0xffffU || input->map_word_209>0xffffU || input->map_word_210>0xffffU || input->map_word_211>0xffffU || input->map_word_212>0xffffU || input->map_word_213>0xffffU || input->map_word_214>0xffffU || input->map_word_215>0xffffU || input->map_word_216>0xffffU || input->map_word_217>0xffffU || input->map_word_218>0xffffU || input->map_word_219>0xffffU || input->map_word_220>0xffffU || input->map_word_221>0xffffU || input->map_word_222>0xffffU || input->map_word_223>0xffffU || input->map_word_224>0xffffU || input->map_word_225>0xffffU || input->map_word_226>0xffffU || input->map_word_227>0xffffU || input->map_word_228>0xffffU || input->map_word_229>0xffffU || input->map_word_230>0xffffU || input->map_word_231>0xffffU || input->map_word_232>0xffffU || input->map_word_233>0xffffU || input->map_word_234>0xffffU || input->map_word_235>0xffffU || input->map_word_236>0xffffU || input->map_word_237>0xffffU || input->map_word_238>0xffffU || input->map_word_239>0xffffU || input->map_word_240>0xffffU || input->map_word_241>0xffffU || input->map_word_242>0xffffU || input->map_word_243>0xffffU || input->map_word_244>0xffffU || input->map_word_245>0xffffU || input->map_word_246>0xffffU || input->map_word_247>0xffffU || input->map_word_248>0xffffU || input->map_word_249>0xffffU || input->map_word_250>0xffffU || input->map_word_251>0xffffU || input->map_word_252>0xffffU || input->map_word_253>0xffffU || input->map_word_254>0xffffU || input->map_word_255>0xffffU || input->axis_byte_00>0xffU || input->axis_byte_01>0xffU || input->axis_byte_02>0xffU || input->axis_byte_03>0xffU || input->axis_byte_04>0xffU || input->axis_byte_05>0xffU || input->axis_byte_06>0xffU || input->axis_byte_07>0xffU || input->axis_byte_08>0xffU || input->axis_byte_09>0xffU || input->axis_byte_10>0xffU || input->axis_byte_11>0xffU || input->axis_byte_12>0xffU || input->axis_byte_13>0xffU || input->axis_byte_14>0xffU || input->axis_byte_15>0xffU || input->axis_word_00>0xffffU || input->axis_word_01>0xffffU || input->axis_word_02>0xffffU || input->axis_word_03>0xffffU || input->axis_word_04>0xffffU || input->axis_word_05>0xffffU || input->axis_word_06>0xffffU || input->axis_word_07>0xffffU || input->axis_word_08>0xffffU || input->axis_word_09>0xffffU || input->axis_word_10>0xffffU || input->axis_word_11>0xffffU || input->axis_word_12>0xffffU || input->axis_word_13>0xffffU || input->axis_word_14>0xffffU || input->axis_word_15>0xffffU || input->selected_scalar_word_942c>0xffffU || input->variant>0xffU || input->initial_sr>0x3ffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x142aU)=(uint16_t)input->word_142a;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1702U)=(uint16_t)input->word_1702;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x1878U)=(uint16_t)input->word_1878;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1880U)=(uint8_t)input->byte_1880;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x188cU)=(uint16_t)input->word_188c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x18b4U)=(uint8_t)input->byte_18b4;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x19c4U)=(uint16_t)input->word_19c4;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x243aU)=(uint16_t)input->word_243a;
    *(volatile uint32_t *)(uintptr_t)(RAM_BASE+0x9818U)=(uint32_t)input->dword_9818;
    for(index=0;index<ARRAY_SIZE(map_bias_division_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)map_bias_division_caller_withdrawal_controlled[index].address,input->calibration+offset,
            map_bias_division_caller_withdrawal_controlled[index].size);
        offset+=map_bias_division_caller_withdrawal_controlled[index].size;
    }
    if(offset!=MAP_BIAS_DIVISION_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(map_bias_division_caller_withdrawal_cases);++index){
        const struct path_case *input=&map_bias_division_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,map_bias_division_caller_withdrawal_controlled,ARRAY_SIZE(map_bias_division_caller_withdrawal_controlled));
        snapshot(bound_before,map_bias_division_caller_withdrawal_bound,ARRAY_SIZE(map_bias_division_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-map-bias-division-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(map_bias_division_caller_withdrawal_controlled,ARRAY_SIZE(map_bias_division_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(map_bias_division_caller_withdrawal_bound,ARRAY_SIZE(map_bias_division_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_MAP_BIAS_DIVISION_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",MAP_BIAS_DIVISION_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
