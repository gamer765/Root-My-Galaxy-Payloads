/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef SUSFS_ARM64_H
#define SUSFS_ARM64_H

#include <linux/types.h>

/* AArch64 landing-pad and pointer-authentication instructions. */
#define SUSFS_ARM64_BTI_C 0xd503245fU
#define SUSFS_ARM64_PACIASP 0xd503233fU
#define SUSFS_ARM64_PACIBSP 0xd503237fU

static inline bool susfs_arm64_is_pac(u32 insn)
{
    return insn == SUSFS_ARM64_PACIASP || insn == SUSFS_ARM64_PACIBSP;
}

static inline bool susfs_arm64_is_landing_pad(u32 insn)
{
    return insn == SUSFS_ARM64_BTI_C || susfs_arm64_is_pac(insn);
}

static inline bool susfs_arm64_fn_has_landing_pad(const void *fn)
{
    const u32 *insns = fn;

    return susfs_arm64_is_landing_pad(insns[0]) ||
           susfs_arm64_is_landing_pad(insns[1]);
}

#endif
