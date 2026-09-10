# Samsung KernelSU late-load builds

The files in this directory are built from KernelSU `v3.2.5`, commit
`b0bc817b4e966aa6aa830834eaf6ef765d821d40`. They are not interchangeable
between KMIs.

## ZZHL KernelSU Next artifacts — automatic testing enabled

The ZZHL Android 17 beta pair is published for the exact SM-S928U1 +
6.1.162 support-feed match. Automatic installation is enabled for that
profile.

- kernelsu/ksud-e3q-S928USQU6ZZHL-kdp-ksun-3.3.0 — KernelSU Next 3.3.0
  AArch64 daemon, 3,762,384 bytes, SHA-256
  f1fe1704644bc00fa986d96ca1c58937d1be5172a38e3056ef9a74d969002485.
- kernelsu/android14-6.1_kernelsu-e3q-S928USQU6ZZHL-kdp.ko — standalone audit
  copy of the module embedded in that daemon, 435,088 bytes, SHA-256
  289dc3e491599278544ec6ba91a40e501542162a875616c2915ea9a8e0cb9d2f.
- artifacts/e3q-S928USQU6ZZHL/cve-2026-43499-app.so — legacy S928 exploit
  payload for the ZZHL profile.

The module was freshly built from KernelSU Next commit
3b18216f71df189ab3d1b1ce0bdb21be1268e771, with only the kernel-side Samsung
KDP/RKP/DEFEX compatibility layer applied. The daemon uses the Next userspace
late-load/control logic; its only userspace source adjustment is a
build-metadata override. No original KernelSU module or daemon is part of the
active pair.

The standalone .ko is for auditing and debugging. Root My Galaxy consumes the
embedded module from ksud. The earlier ZZHL candidates remain in
kernelsu/quarantine/ for forensic comparison. The active pair is statically
verified but has not yet been hardware-tested on ZZHL.

## Versioned artifacts

| File | Target | KMI | Purpose |
| --- | --- | --- | --- |
| `android15-6.6_kernelsu-s25u-kdp.ko` | `SM-S938N`, `S938NKSUACZF1` | `android15-6.6` | Standalone reference module from the previously deployed S25U build |
| `ksud-s25u-kdp` | `SM-S938N`, `S938NKSUACZF1` | `android15-6.6` | Late-load binary embedding the 6.6 module |
| `android15-6.6_kernelsu-A566EXXSCCZG6-kdp.ko` | `SM-A566E`, `A566EXXSCCZG6` | `android15-6.6` | Exact A56 module with target `vermagic`, audited for manual relocation; live text patching disabled for Exynos EL2 |
| `ksud-A566EXXSCCZG6-kdp` | Same exact A56 build | `android15-6.6` | Device-tested late-load binary embedding the A56 6.6 no-patch-text module |
| `android15-6.6_kernelsu-A366WVLS3AYG1-kdp.ko` | `SM-A366W`, `A366WVLS3AYG1` | `android15-6.6` | Exact A36 module with target `vermagic`, audited for manual relocation; live text patching disabled for Samsung KDP/RKP |
| `ksud-A366WVLS3AYG1-kdp` | Same exact A36 build | `android15-6.6` | Device-tested late-load binary embedding the exact A36 no-patch-text module |
| `android14-6.1_kernelsu-e3q-S928USQS6DZF2-kdp.ko` | `SM-S928U/SM-S928U1`, `S928USQS6DZF2` | `android14-6.1` | Exact E3Q module with target `vermagic`, audited for manual relocation |
| `ksud-e3q-S928USQS6DZF2-kdp` | Same exact E3Q build | `android14-6.1` | Device-tested late-load binary embedding the E3Q module |
| `android14-6.1_kernelsu-e3q-S928BXXS6DZF2-kdp.ko` | `SM-S928B`, `S928BXXS6DZF2` | `android14-6.1` | Exact S928B no-patch-text module with target `vermagic`, audited for manual relocation |
| `ksud-e3q-S928BXXS6DZF2-kdp` | Same exact S928B build | `android14-6.1` | Late-load binary embedding the S928B no-patch-text module; module-load hardware-tested |
| `android14-6.1_kernelsu-e2s-S926BXXUEDZDR-kdp.ko` | `SM-S926B`, `S926BXXUEDZDR` | `android14-6.1` | Exact E2S no-patch-text module with target `vermagic`, audited for manual relocation |
| `ksud-e2s-S926BXXUEDZDR-kdp` | Same exact E2S build | `android14-6.1` | Device-tested late-load binary embedding the E2S no-patch-text module |
| `android14-6.1_kernelsu-e1s-S921NKSSFDZF3-kdp.ko` | `SM-S921N`, `S921NKSSFDZF3` | `android14-6.1` | Exact S921N no-patch-text module with target `vermagic`, audited for manual relocation |
| `ksud-e1s-S921NKSSFDZF3-kdp` | Same exact S921N build | `android14-6.1` | Device-tested late-load binary embedding the S921N no-patch-text module |
| `android14-6.1_kernelsu-e1s-S921BXXSFDZE1-kdp.ko` | `SM-S921B`, `S921BXXSFDZE1` | `android14-6.1` | Exact E1S no-patch-text module with target `vermagic`, audited for manual relocation |
| `ksud-e1s-S921BXXSFDZE1-kdp` | Same exact E1S build | `android14-6.1` | Device-tested late-load binary embedding the E1S no-patch-text module |
| `android14-6.1_kernelsu-samsung-kdp.ko` | `SM-S721N` `S721NKSSCDZF3`; `SM-S921B` `S921BXXSFDZF2` | `android14-6.1` | Standalone Samsung KDP/RKP/DEFEX module with target `vermagic` |
| `ksud-samsung-android14-6.1-kdp` | Same verified 6.1 targets | `android14-6.1` | Late-load binary embedding the 6.1 module |
| `android12-5.10_kernelsu-samsung-kdp.ko` | `SM-A155N` `A155NKSS6BYH1` | `android12-5.10` | Standalone Samsung KDP/RKP/DEFEX module built against the exact A15 kernel |
| `ksud-samsung-android12-5.10-kdp` | `SM-A155N` `A155NKSS6BYH1` | `android12-5.10` | Late-load binary embedding the 5.10 module |
| `android13-5.15.189_kernelsu-dm2q-S916BXXSAFZG1.ko` | `SM-S916B`, `S916BXXSAFZG1` | `android13-5.15` | Exact-source FZG1 module; RKP syscall-table and live text patching disabled; hardware load untested |
| `ksud-dm2q-S916BXXSAFZG1-kdp` | Same exact S916B build | `android13-5.15` | Kallsyms-aware late-load binary embedding the exact-source FZG1 module; hardware load untested |
| `android13-5.15.153_kernelsu-dm1q-S911U1UES6DYI3-kdp.ko` | `SM-S911U1`, `S911U1UES6DYI3` | `android13-5.15.153` | Exact DYI3 module with target `vermagic`, audited for manual relocation; no-patch-text build (RKP) with kretprobe fallback hooks |
| `ksud-dm1q-S911U1UES6DYI3-kdp` | Same exact DYI3 build | `android13-5.15.153` | Device-tested late-load binary embedding the exact DYI3 no-patch-text module |
| `android12-5.10_kernelsu-A536EXXSNGZG3-kdp.ko` | `SM-A536E`, `A536EXXSNGZG3` | `android12-5.10` | Device-tested exact A53 module with Samsung KDP/RKP/DEFEX support and live text/table patching disabled |
| `ksud-A536EXXSNGZG3-kdp` | Same exact A53 build | `android12-5.10` | Device-tested late-load binary embedding the exact A53 module |

The standalone `.ko` files are retained for auditing. Root My Galaxy downloads
the corresponding `ksud-*` file because `ksud late-load` loads its embedded
`<kmi>_kernelsu.ko` asset.

The S916B FZG1 pair is built from Samsung's released `SM-S916B_16_Opensource` tree with the live FZG1 config and Android clang `r450784e`. Its zero-length `__versions` section and retained symbol tables are intended for KernelSU's kallsyms-aware manual loader. Audit against the exact recovered FZG1 `vmlinux.elf` found all 200 undefined names. Plain `insmod` is not supported. The target patch [`KernelSU-v3.2.5-dm2q-fzg1.patch`](patches/KernelSU-v3.2.5-dm2q-fzg1.patch) selects the exact FZG1 `enum ucount_type` ABI and hard-stops RKP syscall-table writes; the build also sets `CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT=y`. Use the root helper's guarded `--late-load` operation so the loader's security-domain and stdio transition can complete safely. Module initialization is not yet confirmed on S916B hardware.

The generic 6.1 files remain build-verified only. The E3Q pair is
device-tested and tied to the full S928U DZF2 release string; it must not be replaced
with the generic 6.1 pair. The S928B pair is tied to the full S928B DZF2 release,
uses the no-patch-text Samsung path, is statically audited, and has now been
hardware-tested through module load: the exact `ksud` loaded `kernelsu.ko`,
entered `u:r:ksu:s0`, and survived without a reboot. KernelSU Manager and
Root Checker were then verified: Manager reported `Working <LKM> [Jailbreak
mode]`, version `32525-2`, and one superuser, while Root Checker reported root
access installed. The root remains per-boot because no boot image was
modified; reboot survival is untested.
The earlier ZZHL KernelSU candidates remain quarantined after crashing during
on-device module late-load. The current pure KernelSU Next pair is published
separately for the exact ZZHL automatic-test feed match; it has passed static
provenance checks but is not yet hardware-tested on ZZHL.
The E2S pair is tied to the S926B DZDR release,
static-audited, and device-tested: late-load reports version code `32525`, and
the loader runs in `u:r:ksu:s0`. The E1S pair is tied to the S921B DZE1 release,
static-audited against the recovered DZE1 `vmlinux` (202 undefined symbols, zero
missing, zero CRC mismatches, no `stop_machine`), and device-tested: the
no-patch-text module late-loads cleanly and reports KernelSU active. On the same
Exynos 2400 the generic 6.1 module panics in Samsung/Exynos EL2 while attempting
live text patching, so DZE1 uses the no-patch-text build. The A56 CCZG6 pair is
exact-release,
static-audited, and
device-tested. Its first hardware late-load builds panicked in Samsung/Exynos
EL2 while KernelSU tried live text patching; the current A56 build disables
that path, uses the Samsung fallback hooks, loads successfully, and reports
KernelSU version code `32525` for manager compatibility. The A36 AYG1 pair
uses the same fail-closed Samsung path, reports the exact A36 kernel release,
passes the recovered-target symbol audit, and was loaded on hardware with
KernelSU Manager reporting `Working <LKM> [Jailbreak mode]` and version
`32525-2`. The A536E GZG3 5.10 pair was also loaded from the normal Root My
Galaxy app flow; KernelSU Manager reported `Working <LKM> [Jailbreak mode]`
and version `32525-2`. The older A15 5.10 pair remains device-untested.

## Why the stock module crashes on Samsung

The original S25U failure was captured in
`ksu_mark_running_process_locked+0x154`: a generic inline `put_cred()` wrote
directly to a KDP-protected credential reference count. Samsung's kernel uses
`kdp_usecount_inc_not_zero()` and `kdp_usecount_dec_and_test()` for those
objects; bypassing that path caused a synchronous external abort.

Three other Samsung-specific conflicts were confirmed during the 6.6 port:

1. RKP rejected KernelSU's write to an unused syscall-table slot. The generic
   code nevertheless treated the dispatcher as installed, which redirected
   marked syscalls to the unchanged `ni_syscall` entry.
2. DEFEX retained its own task credential tuple. A KernelSU UID transition
   without synchronizing that tuple triggered credential violations, while
   Safeplace/Immutable-root killed KSU-domain helpers.
3. Late-load could not write a new `/data/adb/ksud` after the module changed the
   loader's security context. The failed destination remained a zero-byte file.

## Patch contents

[`patches/KernelSU-v3.2.5-samsung-kdp-rkp-defex.patch`](patches/KernelSU-v3.2.5-samsung-kdp-rkp-defex.patch)
contains the complete source delta from the tagged v3.2.5 tree:

- resolve Samsung KDP credential helpers and release protected credentials with
  `kdp_usecount_dec_and_test()` plus `__put_cred()`;
- install KDP credentials through `prepare_ro_creds()` on a root workqueue and
  update the target task with the firmware-native `kdp_assign_pgd()` path;
- synchronize the DEFEX task credential record after a successful transition;
- limit the DEFEX allow path to the current UID-0 task already in `u:r:ksu:s0`;
- record a syscall-table hook only if the RKP-protected write succeeds;
- when the dispatcher is unavailable, preserve Manager FD delivery with a
  `__arm64_sys_setresuid` kretprobe and provide sucompat through address-based
  syscall kprobes without modifying the syscall table;
- mark nested sucompat calls so a handler invoking the original syscall cannot
  recursively enter the same kprobe;
- stage `ksud` at `/data/local/tmp/.ksud-stage`, rename it onto the same
  `/data` filesystem before loading the module, then finish labels/assets after
  the module is active.

## 6.1 generalization

The first 6.6 implementation invoked an S25U-specific secure monitor command to
assign the task PGD and linked directly against the 6.6 DDK's
`kdp_usecount_dec_and_test` export. The 6.1 build removes both target-specific
assumptions:

- `kdp_assign_pgd(struct task_struct *)` is resolved from the running kernel and
  used as the firmware-native PGD update entry point;
- `kdp_usecount_dec_and_test(struct cred *)` is resolved at runtime, avoiding a
  dependency on a DDK-specific exported-symbol CRC.

Both function prototypes were verified against each target's own BTF before
building. SM-S921B is an Exynos 2400 target and is not compatibility evidence
for Snapdragon E3Q. The E3Q module was therefore rebuilt with the exact
S928U DZF2 release and audited independently against its recovered
`vmlinux.elf`.

## 5.10 generalization

Samsung 5.10 predates the `cred->ucounts` RLIMIT conversion used by the 6.1
