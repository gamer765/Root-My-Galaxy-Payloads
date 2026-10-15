# ZZI4 Samsung-safe SUSFS test entry

This entry is separate from the working KernelSU Next 3.4.2 profile and the
3.4.0 fallback. It is placed after the working 3.4.2 profile so automatic
matching continues to select the known-good daemon; advanced/manual selection
is required to choose this profile.

The daemon embeds both the target KernelSU Next module and the matching
android14-6.1 SUSFS guard LKM. The guard defaults to `samsung_safe=1`, and
the Manager-triggered `ksud susfs load` path passes the same parameter.

Samsung-safe mode disables the SUSFS layers that write protected LSM or
syscall-table locations:

- `lsm_hook`
- `sus_path`
- `opath`
- `kstat`

The remaining kprobe-based baseline is built against the exact ZZI4 KMI. This
is intentionally a compatibility test, not a claim that every upstream SUSFS
feature is available on this Samsung kernel. Do not enable automatic SUSFS
autoload until the device survives a manual load and the feature report is
reviewed.
