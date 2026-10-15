#!/usr/bin/env python3
"""Apply the resolver-free Samsung-safe SUSFS load-isolation policy."""

from pathlib import Path
import sys

root = Path(sys.argv[1])
susfs_main = root / "kernel/susfs/susfs_main.c"
source = susfs_main.read_text()

marker = (
    "static int fail_layer;\n"
    "module_param_named(fail_layer, fail_layer, int, 0644);\n"
)
if "SUSFS_SAMSUNG_RESOLVER_FREE_TEST" not in source:
    addition = r'''
/*
 * Resolver-free Samsung-safe load-isolation test.
 *
 * The first Samsung-safe build proved that Root My Galaxy staging and the
 * KernelSU Next late-load handoff survive a soft reboot, but the SUSFS LKM
 * still faults while entering its init path.  This variant validates only
 * import relocation and module_init(): it returns immediately after the
 * zero-address import guard, before the SUSFS kallsyms bootstrap, patch-memory
 * setup, kprobes, LSM/syscall-table writers, control nodes, or feature layers.
 */
#define SUSFS_SAMSUNG_RESOLVER_FREE_TEST 1
static bool samsung_resolver_free = true;
module_param_named(samsung_resolver_free, samsung_resolver_free, bool, 0600);
MODULE_PARM_DESC(samsung_resolver_free,
                 "Samsung-safe resolver-free load-isolation mode");

'''
    if source.count(marker) != 1:
        raise SystemExit("unexpected susfs_main.c fail_layer layout")
    source = source.replace(marker, marker + addition, 1)

    guard = (
        "    if (susfs_imports_guard())\n"
        "        return -EINVAL;\n\n"
    )
    early_return = r'''    if (samsung_resolver_free) {
        pr_info("susfs_guard_lkm: resolver-free Samsung-safe mode; "
                "imports validated, no symbol resolver or SUSFS runtime layer is entered\n");
        return 0;
    }

'''
    if source.count(guard) != 1:
        raise SystemExit("unexpected susfs_main.c import-guard layout")
    source = source.replace(guard, guard + early_return, 1)
    susfs_main.write_text(source)

susfsd = root / "userspace/ksud/src/susfsd.rs"
userspace = susfsd.read_text()
old_params = 'let params = CString::new("").expect("empty module parameters are valid");'
new_params = 'let params = CString::new("samsung_resolver_free=1").expect("resolver-free Samsung-safe parameters are valid");'
if old_params in userspace:
    userspace = userspace.replace(old_params, new_params, 1)
elif new_params not in userspace:
    raise SystemExit("unexpected susfsd.rs module parameter layout")
susfsd.write_text(userspace)
