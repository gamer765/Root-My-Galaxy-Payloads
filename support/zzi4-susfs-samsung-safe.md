# ZZI4 Samsung-safe SUSFS test entry

This entry is separate from the working KernelSU Next 3.4.2 profile and the
3.4.0 fallback. It is placed after the working 3.4.2 profile so automatic
matching continues to select the known-good daemon; advanced/manual selection
is required to choose this profile.

The daemon embeds both the target KernelSU Next module and the matching
android14-6.1 SUSFS guard LKM. The guard defaults to `samsung_safe=1`, and
the Manager-triggered `ksud susfs load` path passes the same parameter.

In this revision, Samsung-safe mode is deliberately probe-free: it skips every
SUSFS runtime layer, including the LSM/syscall-table writers, the reboot
supercall, symbol-hiding probes, and feature kprobes. This is a load-isolation
test only; it does not advertise usable SUSFS features yet.

If this profile loads without a freeze, the next build can add one compatible
hook family at a time. Do not enable automatic SUSFS autoload or treat this
profile as a functional SUSFS deployment until the device survives the load
and the feature report is reviewed.
