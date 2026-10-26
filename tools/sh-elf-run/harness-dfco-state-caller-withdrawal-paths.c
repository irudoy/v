/* Input driver defined by defs/JK08A.dfco-state-caller-withdrawal-paths.toml. */
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
#include "dfco-state-caller-withdrawal-cases.h"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[DFCO_STATE_CALLER_WITHDRAWAL_CALIBRATION_SIZE];
static uint8_t bound_before[DFCO_STATE_CALLER_WITHDRAWAL_BOUND_SIZE];
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
    if((input->entry!=0x503e0U && input->entry!=0x50018U) || input->kind>=2U || input->byte_106a>0xffU || input->byte_110e>0xffU || input->byte_11b3>0xffU || input->word_11b6>0xffffU || input->byte_14c1>0xffU || input->byte_14c4>0xffU || input->byte_1517>0xffU || input->byte_153c>0xffU || input->byte_17bd>0xffU || input->byte_1936>0xffU || input->byte_1937>0xffU || input->byte_1938>0xffU || input->byte_1939>0xffU || input->byte_193a>0xffU || input->byte_2458>0xffU || input->byte_2468>0xffU || input->byte_248f>0xffU || input->byte_249f>0xffU || input->byte_24cf>0xffU || input->byte_251b>0xffU || input->byte_2571>0xffU || input->byte_2572>0xffU || input->byte_2573>0xffU || input->byte_259c>0xffU || input->byte_4250>0xffU || input->config_85f6>0xffU || input->config_8711>0xffU || input->config_8a40>0xffU || input->config_8b3f>0xffU || input->config_8c1a>0xffU || input->config_8c1b>0xffU || input->config_8c1c>0xffU || input->config_8c1d>0xffU || input->config_8c1e>0xffU || input->delay_byte_1269a>0xffU || input->delay_byte_1269b>0xffU || input->delay_byte_1269c>0xffU || input->delay_byte_1269d>0xffU || input->delay_byte_1269e>0xffU || input->delay_byte_1269f>0xffU || input->state_byte_000>0xffU || input->state_byte_001>0xffU || input->state_byte_002>0xffU || input->state_byte_003>0xffU || input->state_byte_004>0xffU || input->state_byte_005>0xffU || input->state_byte_006>0xffU || input->state_byte_007>0xffU || input->state_byte_008>0xffU || input->state_byte_009>0xffU || input->state_byte_010>0xffU || input->state_byte_011>0xffU || input->state_byte_012>0xffU || input->state_byte_013>0xffU || input->state_byte_014>0xffU || input->state_byte_015>0xffU || input->state_byte_016>0xffU || input->state_byte_017>0xffU || input->state_byte_018>0xffU || input->state_byte_019>0xffU || input->state_byte_020>0xffU || input->state_byte_021>0xffU || input->state_byte_022>0xffU || input->state_byte_023>0xffU || input->state_byte_024>0xffU || input->state_byte_025>0xffU || input->state_byte_026>0xffU || input->state_byte_027>0xffU || input->state_byte_028>0xffU || input->state_byte_029>0xffU || input->state_byte_030>0xffU || input->state_byte_031>0xffU || input->state_byte_032>0xffU || input->state_byte_033>0xffU || input->state_byte_034>0xffU || input->state_byte_035>0xffU || input->state_byte_036>0xffU || input->state_byte_037>0xffU || input->state_byte_038>0xffU || input->state_byte_039>0xffU || input->state_byte_040>0xffU || input->state_byte_041>0xffU || input->state_byte_042>0xffU || input->state_byte_043>0xffU || input->state_byte_044>0xffU || input->state_byte_045>0xffU || input->state_byte_046>0xffU || input->state_byte_047>0xffU || input->state_byte_048>0xffU || input->state_byte_049>0xffU || input->state_byte_050>0xffU || input->state_byte_051>0xffU || input->state_byte_052>0xffU || input->state_byte_053>0xffU || input->state_byte_054>0xffU || input->state_byte_055>0xffU || input->state_byte_056>0xffU || input->state_byte_057>0xffU || input->state_byte_058>0xffU || input->state_byte_059>0xffU || input->state_byte_060>0xffU || input->state_byte_061>0xffU || input->state_byte_062>0xffU || input->state_byte_063>0xffU || input->state_byte_064>0xffU || input->state_byte_065>0xffU || input->state_byte_066>0xffU || input->state_byte_067>0xffU || input->state_byte_068>0xffU || input->state_byte_069>0xffU || input->state_byte_070>0xffU || input->state_byte_071>0xffU || input->state_byte_072>0xffU || input->state_byte_073>0xffU || input->state_byte_074>0xffU || input->state_byte_075>0xffU || input->state_byte_076>0xffU || input->state_byte_077>0xffU || input->state_byte_078>0xffU || input->state_byte_079>0xffU || input->state_byte_080>0xffU || input->state_byte_081>0xffU || input->state_byte_082>0xffU || input->state_byte_083>0xffU || input->state_byte_084>0xffU || input->state_byte_085>0xffU || input->state_byte_086>0xffU || input->state_byte_087>0xffU || input->state_byte_088>0xffU || input->state_byte_089>0xffU || input->state_byte_090>0xffU || input->state_byte_091>0xffU || input->state_byte_092>0xffU || input->state_byte_093>0xffU || input->state_byte_094>0xffU || input->state_byte_095>0xffU || input->state_byte_096>0xffU || input->state_byte_097>0xffU || input->state_byte_098>0xffU || input->state_byte_099>0xffU || input->state_byte_100>0xffU || input->state_byte_101>0xffU || input->state_byte_102>0xffU || input->state_byte_103>0xffU || input->state_byte_104>0xffU || input->state_byte_105>0xffU || input->state_byte_106>0xffU || input->state_byte_107>0xffU || input->state_byte_108>0xffU || input->state_byte_109>0xffU || input->state_byte_110>0xffU || input->state_byte_111>0xffU || input->state_byte_112>0xffU || input->state_byte_113>0xffU || input->state_byte_114>0xffU || input->state_byte_115>0xffU || input->state_byte_116>0xffU || input->state_byte_117>0xffU || input->state_byte_118>0xffU || input->state_byte_119>0xffU || input->state_byte_120>0xffU || input->state_byte_121>0xffU || input->state_byte_122>0xffU || input->state_byte_123>0xffU || input->state_byte_124>0xffU || input->state_byte_125>0xffU || input->state_byte_126>0xffU || input->state_byte_127>0xffU || input->state_byte_128>0xffU || input->state_byte_129>0xffU || input->state_byte_130>0xffU || input->state_byte_131>0xffU || input->state_byte_132>0xffU || input->state_byte_133>0xffU || input->state_byte_134>0xffU || input->state_byte_135>0xffU || input->state_byte_136>0xffU || input->state_byte_137>0xffU || input->state_byte_138>0xffU || input->state_byte_139>0xffU || input->state_byte_140>0xffU || input->state_byte_141>0xffU || input->state_byte_142>0xffU || input->state_byte_143>0xffU || input->state_byte_144>0xffU || input->state_byte_145>0xffU || input->state_byte_146>0xffU || input->state_byte_147>0xffU || input->state_byte_148>0xffU || input->state_byte_149>0xffU || input->state_byte_150>0xffU || input->state_byte_151>0xffU || input->state_byte_152>0xffU || input->state_byte_153>0xffU || input->state_byte_154>0xffU || input->state_byte_155>0xffU || input->state_byte_156>0xffU || input->state_byte_157>0xffU || input->state_byte_158>0xffU || input->state_byte_159>0xffU || input->state_byte_160>0xffU || input->state_byte_161>0xffU || input->state_byte_162>0xffU || input->state_byte_163>0xffU || input->state_byte_164>0xffU || input->state_byte_165>0xffU || input->state_byte_166>0xffU || input->state_byte_167>0xffU || input->state_byte_168>0xffU || input->state_byte_169>0xffU || input->state_byte_170>0xffU || input->state_byte_171>0xffU || input->state_byte_172>0xffU || input->state_byte_173>0xffU || input->state_byte_174>0xffU || input->state_byte_175>0xffU || input->state_byte_176>0xffU || input->state_byte_177>0xffU || input->state_byte_178>0xffU || input->state_byte_179>0xffU || input->state_byte_180>0xffU || input->state_byte_181>0xffU || input->state_byte_182>0xffU || input->state_byte_183>0xffU || input->state_byte_184>0xffU || input->state_byte_185>0xffU || input->state_byte_186>0xffU || input->state_byte_187>0xffU || input->state_byte_188>0xffU || input->state_byte_189>0xffU || input->state_byte_190>0xffU || input->state_byte_191>0xffU || input->state_byte_192>0xffU || input->state_byte_193>0xffU || input->state_byte_194>0xffU || input->state_byte_195>0xffU || input->state_byte_196>0xffU || input->state_byte_197>0xffU || input->state_byte_198>0xffU || input->state_byte_199>0xffU || input->state_byte_200>0xffU || input->state_byte_201>0xffU || input->state_byte_202>0xffU || input->state_byte_203>0xffU || input->state_byte_204>0xffU || input->state_byte_205>0xffU || input->state_byte_206>0xffU || input->state_byte_207>0xffU || input->state_byte_208>0xffU || input->state_byte_209>0xffU || input->state_byte_210>0xffU || input->state_byte_211>0xffU || input->state_byte_212>0xffU || input->state_byte_213>0xffU || input->state_byte_214>0xffU || input->state_byte_215>0xffU || input->state_byte_216>0xffU || input->state_byte_217>0xffU || input->state_byte_218>0xffU || input->state_byte_219>0xffU || input->state_byte_220>0xffU || input->state_byte_221>0xffU || input->state_byte_222>0xffU || input->state_byte_223>0xffU || input->state_byte_224>0xffU || input->state_byte_225>0xffU || input->state_byte_226>0xffU || input->state_byte_227>0xffU || input->state_byte_228>0xffU || input->state_byte_229>0xffU || input->state_byte_230>0xffU || input->state_byte_231>0xffU || input->state_byte_232>0xffU || input->state_byte_233>0xffU || input->state_byte_234>0xffU || input->state_byte_235>0xffU || input->state_byte_236>0xffU || input->state_byte_237>0xffU || input->state_byte_238>0xffU || input->state_byte_239>0xffU || input->state_byte_240>0xffU || input->state_byte_241>0xffU || input->state_byte_242>0xffU || input->state_byte_243>0xffU || input->state_byte_244>0xffU || input->state_byte_245>0xffU || input->state_byte_246>0xffU || input->state_byte_247>0xffU || input->state_byte_248>0xffU || input->state_byte_249>0xffU || input->state_byte_250>0xffU || input->state_byte_251>0xffU || input->state_byte_252>0xffU || input->state_byte_253>0xffU || input->state_byte_254>0xffU || input->state_byte_255>0xffU || input->variant>0xffU || input->initial_sr>0x3ffU || input->byte_106f>0xffU || input->byte_1083>0xffU || input->byte_14ec>0xffU || input->byte_16aa>0xffU || input->byte_1778>0xffU || input->byte_2450>0xffU || input->byte_245d>0xffU || input->byte_249d>0xffU || input->byte_2978>0xffU || input->byte_41d0>0xffU || input->byte_41d1>0xffU || input->byte_48e1>0xffU || input->byte_5a95>0xffU || input->byte_5a98>0xffU || input->config_84e8>0xffU || input->config_85fa>0xffU || input->config_85fc>0xffU || input->config_870c>0xffU || input->config_8a2f>0xffU || input->config_8a3a>0xffU || input->config_8a3b>0xffU || input->config_8a3c>0xffU || input->config_8a3d>0xffU || input->config_8a3e>0xffU || input->config_8a3f>0xffU || input->restore_byte_12818>0xffU || input->restore_byte_12819>0xffU || input->restore_byte_1281a>0xffU || input->restore_byte_1281b>0xffU || input->restore_byte_1281c>0xffU || input->restore_byte_1281d>0xffU || input->restore_byte_1281e>0xffU || input->restore_byte_1281f>0xffU || input->restore_byte_12820>0xffU || input->restore_byte_12821>0xffU || input->restore_byte_12822>0xffU || input->restore_byte_12823>0xffU || input->restore_byte_12824>0xffU || input->restore_byte_12825>0xffU || input->restore_byte_12826>0xffU || input->restore_byte_12827>0xffU || input->restore_byte_1298c>0xffU || input->restore_byte_1298d>0xffU || input->restore_byte_1298e>0xffU || input->restore_byte_1298f>0xffU || input->restore_byte_12990>0xffU || input->restore_byte_12991>0xffU || input->restore_byte_12992>0xffU || input->restore_byte_12993>0xffU || input->restore_byte_12994>0xffU || input->restore_byte_12995>0xffU || input->restore_byte_12996>0xffU || input->restore_byte_12997>0xffU || input->restore_byte_12998>0xffU || input->restore_byte_12999>0xffU || input->restore_byte_1299a>0xffU || input->restore_byte_1299b>0xffU || input->restore_byte_11cb5>0xffU || input->restore_byte_11cb6>0xffU || input->restore_byte_11cb7>0xffU || input->restore_byte_11cb8>0xffU || input->restore_byte_1299c>0xffU || input->restore_byte_1299d>0xffU || input->restore_byte_1299e>0xffU || input->restore_byte_1299f>0xffU)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x106aU)=(uint8_t)input->byte_106a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x110eU)=(uint8_t)input->byte_110e;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x11b3U)=(uint8_t)input->byte_11b3;
    *(volatile uint16_t *)(uintptr_t)(RAM_BASE+0x11b6U)=(uint16_t)input->word_11b6;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x14c1U)=(uint8_t)input->byte_14c1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x14c4U)=(uint8_t)input->byte_14c4;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1517U)=(uint8_t)input->byte_1517;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x153cU)=(uint8_t)input->byte_153c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x17bdU)=(uint8_t)input->byte_17bd;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1936U)=(uint8_t)input->byte_1936;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1937U)=(uint8_t)input->byte_1937;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1938U)=(uint8_t)input->byte_1938;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1939U)=(uint8_t)input->byte_1939;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x193aU)=(uint8_t)input->byte_193a;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2458U)=(uint8_t)input->byte_2458;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2468U)=(uint8_t)input->byte_2468;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x248fU)=(uint8_t)input->byte_248f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x249fU)=(uint8_t)input->byte_249f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x24cfU)=(uint8_t)input->byte_24cf;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x251bU)=(uint8_t)input->byte_251b;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2571U)=(uint8_t)input->byte_2571;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2572U)=(uint8_t)input->byte_2572;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2573U)=(uint8_t)input->byte_2573;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x259cU)=(uint8_t)input->byte_259c;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x4250U)=(uint8_t)input->byte_4250;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x106fU)=(uint8_t)input->byte_106f;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1083U)=(uint8_t)input->byte_1083;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x14ecU)=(uint8_t)input->byte_14ec;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x16aaU)=(uint8_t)input->byte_16aa;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x1778U)=(uint8_t)input->byte_1778;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2450U)=(uint8_t)input->byte_2450;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x245dU)=(uint8_t)input->byte_245d;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x249dU)=(uint8_t)input->byte_249d;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x2978U)=(uint8_t)input->byte_2978;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41d0U)=(uint8_t)input->byte_41d0;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x41d1U)=(uint8_t)input->byte_41d1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x48e1U)=(uint8_t)input->byte_48e1;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5a95U)=(uint8_t)input->byte_5a95;
    *(volatile uint8_t *)(uintptr_t)(RAM_BASE+0x5a98U)=(uint8_t)input->byte_5a98;
    for(index=0;index<ARRAY_SIZE(dfco_state_caller_withdrawal_controlled);++index){
        memcpy((void *)(uintptr_t)dfco_state_caller_withdrawal_controlled[index].address,input->calibration+offset,
            dfco_state_caller_withdrawal_controlled[index].size);
        offset+=dfco_state_caller_withdrawal_controlled[index].size;
    }
    if(offset!=DFCO_STATE_CALLER_WITHDRAWAL_CALIBRATION_SIZE)return 0;
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(dfco_state_caller_withdrawal_cases);++index){
        const struct path_case *input=&dfco_state_caller_withdrawal_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,dfco_state_caller_withdrawal_controlled,ARRAY_SIZE(dfco_state_caller_withdrawal_controlled));
        snapshot(bound_before,dfco_state_caller_withdrawal_bound,ARRAY_SIZE(dfco_state_caller_withdrawal_bound));
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("kb-dfco-state-caller-withdrawal-observation {\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(dfco_state_caller_withdrawal_controlled,ARRAY_SIZE(dfco_state_caller_withdrawal_controlled));
        printf("\",\"bound_before\":\"");hex(bound_before,sizeof(bound_before));
        printf("\",\"bound_after\":\"");print_spans(dfco_state_caller_withdrawal_bound,ARRAY_SIZE(dfco_state_caller_withdrawal_bound));
        printf("\"}\n");
    }
    printf("VQ_SH_ELF_DFCO_STATE_CALLER_WITHDRAWAL status=PASS region=%s cases=%lu\n",DFCO_STATE_CALLER_WITHDRAWAL_REGION,index);
    return 0;
}
