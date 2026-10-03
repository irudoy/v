#ifndef VQ_STOCK_CRANK_PERIOD_H
#define VQ_STOCK_CRANK_PERIOD_H

#include <stddef.h>
#include <stdint.h>

struct crank_period_context {
    uint32_t r8, r9, r10, r13, r6, sync, r11;
};

_Static_assert(offsetof(struct crank_period_context, r8) == 0, "R8 context offset");
_Static_assert(offsetof(struct crank_period_context, r9) == 4, "R9 context offset");
_Static_assert(offsetof(struct crank_period_context, r10) == 8, "R10 context offset");
_Static_assert(offsetof(struct crank_period_context, r13) == 12, "R13 context offset");
_Static_assert(offsetof(struct crank_period_context, r6) == 16, "R6 context offset");
_Static_assert(offsetof(struct crank_period_context, sync) == 20, "sync context offset");
_Static_assert(offsetof(struct crank_period_context, r11) == 24, "R11 context offset");

extern uint32_t stock_invoke_crank_period(uint32_t entry,
                                        const struct crank_period_context *context);

#endif
