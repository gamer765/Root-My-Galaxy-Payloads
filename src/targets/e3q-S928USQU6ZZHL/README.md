# SM-S928U1 ZZHL legacy-S928 Root My Galaxy build

This bundle targets the Android 17 beta kernel identified in the supplied
files as:

`6.1.162-android14-11-34343818-abS928USQU6ZZHL`

The beta `boot.img.p` is a BSDIFF patch whose base is the complete DZH3
`boot.img`. Applying it to the full DZH3 image produces the ZZHL kernel. The
vendor boot image independently contains the same `USQU6ZZHL` release string.

## Files

- `artifacts/e3q-S928USQU6ZZHL/cve-2026-43499-app.so` — app-domain CVE-2026-43499 payload, rebuilt with the legacy S928 engine for the ZZHL profile.
- `artifacts/e3q-S928USQU6ZZHL/cve-2026-43499-app.experimental.previous.so` — the prior current-engine experimental payload, retained as a rollback copy.
- `kernelsu/ksud-e3q-S928USQU6ZZHL-kdp-ksun-3.3.0` — AArch64 KernelSU Next 3.3.0 userspace daemon with the matching module embedded.
- `kernelsu/android14-6.1_kernelsu-e3q-S928USQU6ZZHL-kdp.ko` — the embedded module as a standalone audit/debug copy.
- `profile/target.h` and `profile/p0_fingerprint.h` — generated target profile and P0 fingerprint table.

## Important status

This remains an **experimental, hardware-unvalidated** build. The app
payload was rebuilt from the legacy S928 stable-race engine in upstream
Root-My-Galaxy commit `139c6dad8cc81be7f4ab2ef03c6a1463cd60f000`, the source
path used for the device-tested DZF2 payload. The ZZHL target constants and P0
fingerprint are still ZZHL-specific. No boot/recovery image is included and
nothing here should be flashed directly.

The rebuilt app is 104,128 bytes with SHA-256
`57cc42bf24a8e4ece40fbed4ae90cc91f2c1badb4f7cd5493bc6ac04de6b29b5`. As a
build sanity check, rebuilding the archived DZF2 target through the same
legacy stable path reproduces its known device-tested app byte-for-byte
(SHA-256 `b2931d8980f969b5a0cb05bd67f6804f445ad4a4c867a7b4c4081c2ffac5b36a`).

The exploit profile and P0 table were derived from the patched ZZHL kernel
image. The KernelSU Next daemon and module are unchanged from the previous
ZZHL bundle; the module was compiled against AOSP common `android14-6.1.162`
headers because Samsung has not published a ZZHL vendor kernel tree. The
Samsung KDP/RKP/DEFEX compatibility layer is the project’s v3.2.5 kernel
patch, while the daemon is built from KernelSU Next v3.3.0. The module has an
empty `__versions` section and is intended for the project’s manual-relocation
late-load path.

The support feed entry is labeled experimental. Verify the exact device
fingerprint, run the app payload once with a USB recovery path available, and
capture `/sys/fs/pstore`/bugreport output if it hangs or reboots. Keep the
known-good DZH3/DZG1 entry unchanged while testing.
