#include <stdint.h>
#include <stdio.h>

#define TEST_RAM_BASE 0x01000000U
#define ARRAY_SIZE(values) (sizeof(values)/sizeof((values)[0]))
extern uint32_t stock_invoke_fuel_compensation(uint32_t,const uint32_t *,uint32_t *);
extern uint32_t stock_invoke_surface(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t *);
extern uint32_t stock_invoke_r1(uint32_t,uint32_t,uint32_t);

static const uint8_t patterns[4][256] = {
    {127,127,127,127,127,127,127,128,129,131,132,133,134,127,127,127,127,127,127,127,127,127,129,129,130,131,132,133,134,127,127,127,127,127,127,127,129,129,130,130,130,131,132,132,128,128,128,128,127,127,127,127,128,129,130,130,130,130,130,130,128,128,128,128,128,128,128,128,128,129,129,129,129,129,129,129,129,129,129,129,128,128,128,128,128,128,128,128,128,128,129,129,130,130,130,130,128,128,128,128,128,128,128,128,128,128,129,129,128,128,128,128,129,129,129,129,129,129,129,130,130,130,130,130,127,127,127,127,129,129,129,129,129,129,129,129,130,130,131,131,129,129,129,129,129,129,129,129,129,129,129,129,129,130,131,132,128,128,128,128,128,128,128,128,128,128,129,129,129,129,129,129,128,129,129,129,127,127,127,127,127,127,128,129,129,129,129,131,130,130,130,130,127,127,127,127,127,127,128,129,129,129,129,132,129,129,129,129,127,127,127,127,127,127,128,129,129,129,129,131,131,131,131,131,127,127,127,127,128,128,129,129,129,129,129,130,127,127,127,127,128,128,128,128,129,129,129,130,130,130,131,132,129,129,129,129},
    {0,7,14,21,28,35,42,49,56,63,70,77,84,91,98,105,5,12,19,26,33,40,47,54,61,68,75,82,89,96,103,110,10,17,24,31,38,45,52,59,66,73,80,87,94,101,108,115,15,22,29,36,43,50,57,64,71,78,85,92,99,106,113,120,20,27,34,41,48,55,62,69,76,83,90,97,104,111,118,125,25,32,39,46,53,60,67,74,81,88,95,102,109,116,123,130,30,37,44,51,58,65,72,79,86,93,100,107,114,121,128,135,35,42,49,56,63,70,77,84,91,98,105,112,119,126,133,140,40,47,54,61,68,75,82,89,96,103,110,117,124,131,138,145,45,52,59,66,73,80,87,94,101,108,115,122,129,136,143,150,50,57,64,71,78,85,92,99,106,113,120,127,134,141,148,155,55,62,69,76,83,90,97,104,111,118,125,132,139,146,153,160,60,67,74,81,88,95,102,109,116,123,130,137,144,151,158,165,65,72,79,86,93,100,107,114,121,128,135,142,149,156,163,170,70,77,84,91,98,105,112,119,126,133,140,147,154,161,168,175,75,82,89,96,103,110,117,124,131,138,145,152,159,166,173,180},
    {255,248,241,234,227,220,213,206,199,192,185,178,171,164,157,150,250,243,236,229,222,215,208,201,194,187,180,173,166,159,152,145,245,238,231,224,217,210,203,196,189,182,175,168,161,154,147,140,240,233,226,219,212,205,198,191,184,177,170,163,156,149,142,135,235,228,221,214,207,200,193,186,179,172,165,158,151,144,137,130,230,223,216,209,202,195,188,181,174,167,160,153,146,139,132,125,225,218,211,204,197,190,183,176,169,162,155,148,141,134,127,120,220,213,206,199,192,185,178,171,164,157,150,143,136,129,122,115,215,208,201,194,187,180,173,166,159,152,145,138,131,124,117,110,210,203,196,189,182,175,168,161,154,147,140,133,126,119,112,105,205,198,191,184,177,170,163,156,149,142,135,128,121,114,107,100,200,193,186,179,172,165,158,151,144,137,130,123,116,109,102,95,195,188,181,174,167,160,153,146,139,132,125,118,111,104,97,90,190,183,176,169,162,155,148,141,134,127,120,113,106,99,92,85,185,178,171,164,157,150,143,136,129,122,115,108,101,94,87,80,180,173,166,159,152,145,138,131,124,117,110,103,96,89,82,75},
    {7,48,89,130,171,212,253,38,79,120,161,202,243,28,69,110,90,131,172,213,254,39,80,121,162,203,244,29,70,111,152,193,173,214,255,40,81,122,163,204,245,30,71,112,153,194,235,20,0,41,82,123,164,205,246,31,72,113,154,195,236,21,62,103,83,124,165,206,247,32,73,114,155,196,237,22,63,104,145,186,166,207,248,33,74,115,156,197,238,23,64,105,146,187,228,13,249,34,75,116,157,198,239,24,65,106,147,188,229,14,55,96,76,117,158,199,240,25,66,107,148,189,230,15,56,97,138,179,159,200,241,26,67,108,149,190,231,16,57,98,139,180,221,6,242,27,68,109,150,191,232,17,58,99,140,181,222,7,48,89,69,110,151,192,233,18,59,100,141,182,223,8,49,90,131,172,152,193,234,19,60,101,142,183,224,9,50,91,132,173,214,255,235,20,61,102,143,184,225,10,51,92,133,174,215,0,41,82,62,103,144,185,226,11,52,93,134,175,216,1,42,83,124,165,145,186,227,12,53,94,135,176,217,2,43,84,125,166,207,248,228,13,54,95,136,177,218,3,44,85,126,167,208,249,34,75},
};
static const uint8_t row_axis[16] = {8,16,24,32,40,56,64,72,88,96,104,120,128,132,140,148};
static const uint8_t col_axis[16] = {16,32,48,64,80,96,112,128,144,160,176,192,208,224,240,255};


static volatile uint8_t *ram(uint32_t address)
{
    return (volatile uint8_t *)(uintptr_t)(TEST_RAM_BASE+(address&65535U));
}

static uint8_t cell(unsigned pattern,unsigned row,unsigned col)
{
    return patterns[pattern][16U*row+col];
}

static void coordinate(const uint8_t *axis,uint32_t value,unsigned multiplier,
                       unsigned *index,uint32_t *fraction)
{
    unsigned i=0;
    while (i<15U && value>=(unsigned)axis[i+1U]*multiplier) ++i;
    *index=i;
    *fraction=(i==15U || value<=(unsigned)axis[i]*multiplier) ? 0U
        : (value-(unsigned)axis[i]*multiplier)*65536U/((axis[i+1U]-axis[i])*multiplier);
}

static uint32_t linear(uint32_t a,uint32_t b,uint32_t f)
{
    return b>=a ? a+(b-a)*f/65536U : a-(a-b)*f/65536U;
}

static uint32_t lookup(unsigned pattern,uint32_t row,uint32_t col,int raw)
{
    unsigned r,c;
    uint32_t rf,cf,top,bottom;
    coordinate(row_axis,row&65535U,4,&r,&rf);
    coordinate(col_axis,col&255U,1,&c,&cf);
    top=cell(pattern,r,c);
    if (cf) top=linear(top,cell(pattern,r,c+1U),cf);
    if (rf) {
        bottom=cell(pattern,r+1U,c);
        if (cf) bottom=linear(bottom,cell(pattern,r+1U,c+1U),cf);
        top=linear(top,bottom,rf);
    }
    return raw && !rf && !cf && top>=128U ? top|0xffffff00U : top;
}

static int fail(const char *name,const char *field,uint32_t actual,uint32_t expected)
{
    printf("VQ_SH_ELF_STOCK_CODE status=FAIL case=%s field=%s actual=%08lx expected=%08lx\n",
           name,field,(unsigned long)actual,(unsigned long)expected);
    return 0;
}

static void pattern_set(unsigned pattern)
{
    unsigned i;
    for (i=0;i<256U;++i) *(volatile uint8_t *)(uintptr_t)(TABLE+i)=patterns[pattern][i];
}

static int preserved_calibration(const char *name,unsigned pattern,
                                 uint8_t a,uint8_t b,uint8_t c,uint8_t scalar)
{
    unsigned i;
    for (i=0;i<256U;++i)
        if (*(const volatile uint8_t *)(uintptr_t)(TABLE+i)!=patterns[pattern][i])
            return fail(name,"read-only-table",i,0);
    for (i=0;i<16U;++i)
        if (*(const volatile uint8_t *)(uintptr_t)(ROW_AXIS+i)!=row_axis[i]
            || *(const volatile uint8_t *)(uintptr_t)(COL_AXIS+i)!=col_axis[i])
            return fail(name,"read-only-axis",i,0);
    if (*(const volatile uint8_t *)(uintptr_t)MODE_A!=a
        || *(const volatile uint8_t *)(uintptr_t)MODE_B!=b
        || *(const volatile uint8_t *)(uintptr_t)SOURCE_MODE!=c
        || *(const volatile uint8_t *)(uintptr_t)BYPASS_SCALAR!=scalar)
        return fail(name,"read-only-bypass-control",0,1);
    return 1;
}

struct window {uint32_t start;unsigned size;uint8_t before[128];};
static struct window windows[]={{0xffff1100U,128,{0}},{0xffff5620U,16,{0}},{0xffff2830U,16,{0}}};

static int publication(const char *name,uint32_t row,uint32_t col,unsigned pattern,
                       uint8_t a,uint8_t b,uint8_t c,uint8_t scalar,uint8_t first,uint8_t second)
{
    uint32_t state[5],result,expected,context[]={
        (uint32_t)(uintptr_t)ram(PRIMARY_BASE),row,0x12345678U,0x76543210U};
    unsigned w,i;
    for (w=0;w<ARRAY_SIZE(windows);++w)
        for (i=0;i<windows[w].size;++i) ram(windows[w].start)[i]=(uint8_t)(19U*i+31U*w+7U);
    *(volatile uint16_t *)ram(RPM_SOURCE)=(uint16_t)row;
    ram(COL_SOURCE)[0]=(uint8_t)col;
    ram(OUTPUT)[0]=0xa5;
    ram(FIRST_SOURCE)[0]=first;
    ram(SECOND_SOURCE)[0]=second;
    *(volatile uint8_t *)(uintptr_t)MODE_A=a;
    *(volatile uint8_t *)(uintptr_t)MODE_B=b;
    *(volatile uint8_t *)(uintptr_t)SOURCE_MODE=c;
    *(volatile uint8_t *)(uintptr_t)BYPASS_SCALAR=scalar;
    pattern_set(pattern);
    for (w=0;w<ARRAY_SIZE(windows);++w)
        for (i=0;i<windows[w].size;++i) windows[w].before[i]=ram(windows[w].start)[i];
    if ((a&32U) || !(b&16U) || (!(a&1U) && (b&2U))) expected=lookup(pattern,row,col,0);
    else {
        expected=(a&1U) ? ((c&2U) ? scalar:first):second;
        if (expected<64U) expected=64U;
        if (expected>192U) expected=192U;
    }
    result=stock_invoke_fuel_compensation(SELECTOR_ENTRY,context,state);
    if (result!=0x4cU) return fail(name,"boundary-r0",result,0x4cU);
    if (ram(OUTPUT)[0]!=expected)
        return fail(name,"published-byte",ram(OUTPUT)[0],expected);
    if (state[0]!=context[2] || state[1]!=context[3] || state[2]!=context[0] || state[3]!=row)
        return fail(name,"macl-gbr-input-base-or-cached-rpm",state[0],context[2]);
    for (w=0;w<ARRAY_SIZE(windows);++w)
        for (i=0;i<windows[w].size;++i)
            if (windows[w].start+i!=OUTPUT && ram(windows[w].start)[i]!=windows[w].before[i])
                return fail(name,"read-only-input-or-neighbor",windows[w].start+i,0);
    return preserved_calibration(name,pattern,a,b,c,scalar);
}

int main(void)
{
    const uint32_t columns[]={0,15,16,17,32,47,128,239,240,254,255};
    const uint32_t bypass_values[]={0,63,64,128,192,193,255};
    const uint32_t direct[][2]={{0,0},{32,16},{33,17},{127,127},{511,254},{512,255},
                              {65535,255},{0x1234007fU,0xdead007fU},{0xffffffffU,0xffffffffU}};
    const uint8_t distinct[][3]={{0xe0,0x81,0xdc},{0,16,0},{1,16,0},{1,16,2},{255,255,255}};
    const uint32_t divides[][2]={{123,0},{0,1},{1,1},{0xffffffffU,17},{17,0xffffffffU}};
    uint32_t row_values[50],state[1],result,expected;
    unsigned p,r,c,i,j,k,n=0,cases=0;
    char name[80];
    row_values[n++]=0;
    row_values[n++]=65535;
    for (i=0;i<16U;++i) {
        row_values[n++]=(uint32_t)row_axis[i]*4U-1U;
        row_values[n++]=(uint32_t)row_axis[i]*4U;
        row_values[n++]=(uint32_t)row_axis[i]*4U+1U;
    }
    for (p=0;p<4U;++p) {
        for (r=0;r<n;++r) for (c=0;c<ARRAY_SIZE(columns);++c) {
            snprintf(name,sizeof(name),"grid-%u-%lu-%lu",p,(unsigned long)row_values[r],(unsigned long)columns[c]);
            if (!publication(name,row_values[r],columns[c],p,0xe0,0x81,0xdc,128,13,241)) return 1;
            ++cases;
        }
        for (c=0;c<256U;++c) {
            snprintf(name,sizeof(name),"column-%u-%u",p,c);
            if (!publication(name,127,c,p,0xe0,0x81,0xdc,128,13,241)) return 1;
            ++cases;
        }
    }
    for (i=0;i<4U;++i) for (j=0;j<4U;++j) for (k=0;k<2U;++k)
        for (c=0;c<ARRAY_SIZE(bypass_values);++c) {
            uint8_t a=(uint8_t)((i&1U)|((i&2U)<<4));
            uint8_t b=(uint8_t)(((j&1U)<<1)|((j&2U)<<3));
            uint8_t value=(uint8_t)bypass_values[c];
            snprintf(name,sizeof(name),"select-%u-%u-%u-%u",a,b,k*2U,value);
            if (!publication(name,127,127,0,a,b,(uint8_t)(k*2U),value,value,value)) return 1;
            ++cases;
        }
    for (i=0;i<ARRAY_SIZE(distinct);++i) {
        snprintf(name,sizeof(name),"distinct-%u",i);
        if (!publication(name,127,127,0,distinct[i][0],distinct[i][1],distinct[i][2],179,111,147)) return 1;
        ++cases;
    }
    for (p=0;p<4U;++p) for (i=0;i<ARRAY_SIZE(direct);++i) {
        snprintf(name,sizeof(name),"wrapper-%u-%u",p,i);
        pattern_set(p);
        expected=lookup(p,direct[i][0],direct[i][1],1);
        result=stock_invoke_surface(WRAPPER_ENTRY,TABLE,ROW_AXIS,COL_AXIS,direct[i][0],direct[i][1],state);
        if (result!=expected || state[0]!=0x12345678U) {
            fail(name,"natural-return-or-macl",result,expected);
            return 1;
        }
        if (!preserved_calibration(name,p,255,255,255,179)) return 1;
        ++cases;
    }
    for (i=0;i<ARRAY_SIZE(divides);++i) {
        expected=divides[i][1] ? divides[i][0]/divides[i][1]:0;
        result=stock_invoke_r1(DIVIDER_ENTRY,divides[i][0],divides[i][1]);
        if (result!=expected) {
            fail("divider","unsigned-or-zero-return",result,expected);
            return 1;
        }
        ++cases;
    }
    printf("VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%u\n",REGION_KEY,cases);
    return 0;
}
