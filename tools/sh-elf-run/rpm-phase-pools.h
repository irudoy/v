/* Exact independently declared pool spans of each RPM view. */
#if VIEW_KIND == 0
static const struct { uint32_t at,size; } pools[]={
{0x8743U,1U},
{0x385a8U,4U},
{0x385b4U,8U},
};
#elif VIEW_KIND == 1
static const struct { uint32_t at,size; } pools[]={
{0x385a8U,4U},
};
#elif VIEW_KIND == 2
static const struct { uint32_t at,size; } pools[]={
{0x21154U,12U},
{0x22110U,4U},
{0x22190U,4U},
};
#endif
