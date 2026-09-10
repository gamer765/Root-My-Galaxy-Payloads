# SM-S928U1 S928U1UES6ZZHL build report

## Target evidence

| Item | Value |
|---|---|
| Base firmware image | DZH3 `boot.img` (full 100,663,296-byte image) |
| Diff | `boot.img.p` (`BSDIFF40`, output 100,663,296 bytes) |
| Result kernel release | `6.1.162-android14-11-34343818-abS928USQU6ZZHL` |
| Result kernel size | 38,140,416 bytes |
| Result kernel SHA-256 | `b38f6c102aef3dae5d475c3a645e36b2e5fbbb3cad57f51c09d7f64b22dcba87` |
| Result BTF range | `0x1820e90-0x1dd7cb8` (5,991,976 bytes) |
| Result BTF SHA-256 | `00f86d507632aa76102e8b7bf783fb778373529e2c5d88f9fa2e53aa7442bea0` |

## Build inputs

- Android NDK r29 (Clang 21.0.0)
- Legacy S928 app engine from Root-My-Galaxy commit `139c6dad8cc81be7f4ab2ef03c6a1463cd60f000`
- AOSP common kernel `android14-6.1.162_r00` headers/config
- KernelSU Next userspace v3.3.0, source commit `3b18216f71df189ab3d1b1ce0bdb21be1268e771`
- Samsung KDP/RKP/DEFEX patch applied to the KernelSU v3.2.5 kernel module
- `CONFIG_KSU_SAMSUNG_NO_PATCH_TEXT=y`
- `KCFLAGS=-fno-stack-protector`
- Manual-relocation module (`__versions` size 0)

## Exploit payload rebuild

The ZZHL app payload was rebuilt with the legacy S928 stable-race build path,
using the ZZHL-specific target constants and P0 fingerprint. The resulting
104,128-byte payload has SHA-256
`57cc42bf24a8e4ece40fbed4ae90cc91f2c1badb4f7cd5493bc6ac04de6b29b5`.

The prior current-engine experimental payload is retained at
`artifacts/e3q-S928USQU6ZZHL/cve-2026-43499-app.experimental.previous.so` for
rollback. The KernelSU Next daemon and module were not changed by this rebuild.

## Verification performed

- The rebuilt app payload is a stripped AArch64 shared object and is exactly
  104,128 bytes.
- The same legacy stable build reproduces the archived device-tested DZF2 app
  payload byte-for-byte, providing a source/build sanity check for the ZZHL
  rebuild.
- The module `vermagic` exactly matches the ZZHL release string.
- The module’s undefined symbols pass the project `check_symbol` check against
  the recovered ZZHL `vmlinux.elf`.
- The daemon is a stripped AArch64 PIE and embeds the newly built module under
  the Android 14/6.1 asset name `android14-6.1_kernelsu.ko`.

These checks do not substitute for a hardware run. Samsung’s unpublished
vendor configuration and runtime KDP/RKP behavior can still differ from the
AOSP common headers used for this experimental module.
