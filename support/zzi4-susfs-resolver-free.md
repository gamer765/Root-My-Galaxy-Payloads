# ZZI4 resolver-free Samsung-safe SUSFS diagnostic

This is a separate, manual-only entry for the SM-S928U1 ZZI4 / 6.1.162 target.
The working KernelSU Next 3.4.2 entry, the earlier Samsung-safe load-isolation
entry, and the 3.4.0 fallback remain separate and unchanged.

This diagnostic changes only the SUSFS LKM init path. The module validates that
KernelSU Next userspace relocation supplied nonzero imports, then returns from
module_init() before entering the SUSFS kallsyms resolver, patch-memory setup,
kprobes, LSM/syscall-table writers, control nodes, or feature layers.

A successful load proves that the remaining failure is inside the resolver or
SUSFS initialization path. It does not provide SUSFS functionality and must
not be used with SUSFS autoload or feature toggles.

Select this entry only through Root My Galaxy Advanced/manual mode. After the
required soft reboot, verify root and device stability first. The LKM load
button should be tested only once, with the phone connected to a log capture
session; stop immediately if the device freezes or reboots.
