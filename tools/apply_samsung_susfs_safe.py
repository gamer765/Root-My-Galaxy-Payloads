#!/usr/bin/env python3
"""Apply the Samsung-safe SUSFS test policy to a KernelSU Next checkout."""

from pathlib import Path
import sys

root = Path(sys.argv[1])
susfs_main = root / "kernel/susfs/susfs_main.c"
source = susfs_main.read_text()

if "SUSFS_SAMSUNG_SAFE_TEST" not in source:
    marker = (
        "static int fail_layer;\n"
        "module_param_named(fail_layer, fail_layer, int, 0644);\n"
    )
    addition = r'''
/*
 * Samsung-safe SUSFS test policy.
 *
 * Samsung EL2/RKP protects the kernel text and syscall/LSM tables.  The
 * upstream LKM layers below use ksu_patch_text() against those protected
 * locations, so treating a write refusal as a normal load failure is not
 * enough: the attempted path itself has already been observed to crash this
 * device.  The test build therefore defaults to the kprobe-only baseline.
 */
#define SUSFS_SAMSUNG_SAFE_TEST 1
static bool samsung_safe = true;
module_param_named(samsung_safe, samsung_safe, bool, 0600);
MODULE_PARM_DESC(samsung_safe,
                 "Samsung-safe mode: skip LSM and syscall-table patch layers");

static bool susfs_samsung_unsafe_layer(const char *name)
{
    return !strcmp(name, "lsm_hook") ||
           !strcmp(name, "sus_path") ||
           !strcmp(name, "opath") ||
           !strcmp(name, "kstat");
}
'''
    if source.count(marker) != 1:
        raise SystemExit("unexpected susfs_main.c fail_layer layout")
    source = source.replace(marker, marker + addition, 1)

    armed_marker = "        susfs_layers[i].armed = true;\n"
    safe_gate = r'''        if (samsung_safe &&
            susfs_samsung_unsafe_layer(susfs_layers[i].name)) {
            pr_warn("susfs_guard_lkm: samsung_safe=1 - %s disabled "
                    "(protected LSM/syscall-table write path)\n",
                    susfs_layers[i].name);
            susfs_layers[i].armed = false;
            continue;
        }

'''
    if source.count(armed_marker) != 1:
        raise SystemExit("unexpected susfs_main.c layer loop layout")
    source = source.replace(armed_marker, safe_gate + armed_marker, 1)

    hide_marker = "    susfs_self_hide_nodes();\n"
    safe_hide = r'''    if (samsung_safe) {
        pr_info("susfs_guard_lkm: Samsung-safe mode active; "
                "LSM/syscall-table layers and their self-hide rules are off\n");
    } else {
        susfs_self_hide_nodes();
    }
'''
    if source.count(hide_marker) != 1:
        raise SystemExit("unexpected susfs_main.c self-hide layout")
    source = source.replace(hide_marker, safe_hide, 1)

    susfs_main.write_text(source)

susfsd = root / "userspace/ksud/src/susfsd.rs"
userspace = susfsd.read_text()
old_params = 'let params = CString::new("").expect("empty module parameters are valid");'
new_params = 'let params = CString::new("samsung_safe=1").expect("Samsung-safe SUSFS parameters are valid");'
if old_params in userspace:
    userspace = userspace.replace(old_params, new_params, 1)
elif new_params not in userspace:
    raise SystemExit("unexpected susfsd.rs module parameter layout")
susfsd.write_text(userspace)
