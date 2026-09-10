# SM-S928U1 ZZHL legacy-S928 Root My Galaxy build

This bundle targets the Android 17 beta kernel identified in the supplied
files as:

`6.1.162-android14-11-34343818-abS928USQU6ZZHL`

The beta `boot.img.p` is a BSDIFF patch whose base is the complete DZH3
`boot.img`. Applying it to the full DZH3 image produces the ZZHL kernel. The
vendor boot image independently contains the same `USQU6ZZHL` release string.

## Files

- `artifacts/e3q-S928USQU6ZZHL/cve-2026-43499-app.so` — app-domain CVE-2026-43499 payload, rebuilt with the legacy S928 engine for the ZZHL profile.
- `artifacts/e3q-S928USQU6ZZHL/cve-2026-43499-app-previous.so` — the prior current-engine payload, retained as a rollback copy.
- `kernelsu/ksud-e3q-S928USQU6ZZHL-kdp-ksun-3.3.0` — AArch64 KernelSU Next 3.3.0 userspace daemon with synchronous late-load and the matching legacy S928-shaped module embedded.
- `kernelsu/ksud-e3q-S928USQU6ZZHL-kdp-ksun-3.3.0-regular-module-previous` — the prior daemon paired with the regular KernelSU module, retained for rollback.
- `kernelsu/android14-6.1_kernelsu-e3q-S928USQU6ZZHL-kdp.ko` — the embedded module as a standalone audit/debug copy.
- `profile/target.h` and `profile/p0_fingerprint.h` — generated target profile and P0 fingerprint table.

## Important status

The active ZZHL bundle uses the legacy S928 stable-race engine for the app
payload and KernelSU Next 3.3.0 for the kernel pair. The app payload was
rebuilt in upstream Root-My-Galaxy commit
`139c6dad8cc81be7f4ab2ef03c6a1463cd60f000`, the source path used for the
device-tested DZF2 payload. The ZZHL target constants and P0 fingerprint are
ZZHL-specific. The rebuilt KernelSU pair is CI-verified, but its module uses
the legacy S928 DZG1 shape with a same-length ZZHL vermagic retarget rather
than a source-identical ZZHL vendor-module build; device validation remains
pending. No boot/recovery image is included and nothing here should be flashed
directly.

The rebuilt app is 104,128 bytes with SHA-256
`57cc42bf24a8e4ece40fbed4ae90cc91f2c1badb4f7cd5493bc6ac04de6b29b5`. As a
build sanity check, rebuilding the archived DZF2 target through the same
legacy stable path reproduces its known device-tested app byte-for-byte
(SHA-256 `b2931d8980f969b5a0cb05bd67f6804f445ad4a4c867a7b4c4081c2ffac5b36a`).

The exploit profile and P0 table were derived from the patched ZZHL kernel
image. The daemon was built from KernelSU Next source commit
`3b18216f71df189ab3d1b1ce0bdb21be1268e771` with the Samsung KDP/RKP/DEFEX
compatibility port. Its embedded module is the preserved stripped legacy S928
DZG1 KernelSU Next shape, retargeted to the ZZHL release string; it has an
empty `__versions` section, `this_module=0x400`, and no `.printk_index`.
It is intended for the project’s manual-relocation late-load path.

The daemon was rebuilt from KernelSU Next source commit
`3b18216f71df189ab3d1b1ce0bdb21be1268e771` with the Samsung synchronous
late-load/staging patch. It is 3,727,928 bytes with SHA-256
`556b8c3f0eabd1de73a7dba26187ebcbcb4d70b627981246ac3fcbdbf35c2487`; its
embedded module matches the standalone module byte-for-byte
(`39c87e32d5c083dc3043e324065aab6e535df5214e644823c89de1613e56f987`).

The support feed entry follows the DZG1/DZH3 naming pattern and points to the
active ZZHL pair. Verify the exact device fingerprint and capture
`/sys/fs/pstore`/bugreport output if it hangs or reboots while the corrected
pair is being device-validated.
