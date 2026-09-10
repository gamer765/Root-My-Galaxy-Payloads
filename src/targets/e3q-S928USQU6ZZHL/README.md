# SM-S928U1 ZZHL Root My Galaxy build

This bundle targets the Android 17 beta kernel identified in the supplied
files as:

6.1.162-android14-11-34343818-abS928USQU6ZZHL

The beta boot.img.p is a BSDIFF patch whose base is the complete DZH3
boot.img. Applying it to the full DZH3 image produces the ZZHL kernel. The
vendor boot image independently contains the same USQU6ZZHL release string.

## Files

- artifacts/e3q-S928USQU6ZZHL/cve-2026-43499-app.so — app-domain
  CVE-2026-43499 payload rebuilt with the legacy S928 exploit engine.
- artifacts/e3q-S928USQU6ZZHL/cve-2026-43499-app-previous.so — prior
  current-engine payload retained as a rollback copy.
- kernelsu/ksud-e3q-S928USQU6ZZHL-kdp-ksun-3.3.0 — published KernelSU Next
  3.3.0 daemon used by the automatic ZZHL feed entry.
- kernelsu/android14-6.1_kernelsu-e3q-S928USQU6ZZHL-kdp.ko — standalone
  audit copy of the module embedded in the daemon.
- kernelsu/quarantine/ — older ZZHL KernelSU candidates retained for forensic
  comparison only.
- profile/target.h and profile/p0_fingerprint.h — generated target profile and
  P0 fingerprint table.

## Automatic testing status

The support feed contains the exact match:

- Model: SM-S928U1
- Kernel version: 6.1.162
- Payload ID: e3q-S928USQU6ZZHL

The app payload is 104,128 bytes with SHA-256
57cc42bf24a8e4ece40fbed4ae90cc91f2c1badb4f7cd5493bc6ac04de6b29b5.
The published KernelSU Next daemon is 3,762,384 bytes with SHA-256
f1fe1704644bc00fa986d96ca1c58937d1be5172a38e3056ef9a74d969002485.
Its embedded module matches the standalone module byte-for-byte; the module
SHA-256 is
289dc3e491599278544ec6ba91a40e501542162a875616c2915ea9a8e0cb9d2f.

The active kernel pair is built exclusively from KernelSU Next commit
3b18216f71df189ab3d1b1ce0bdb21be1268e771. The Samsung compatibility changes
are limited to the Next kernel tree; the daemon uses Next userspace late-load
and control logic with a build-metadata-only version override. No original
KernelSU module or daemon is included.

The pair has passed static build and embedded-provenance checks but has not yet
been hardware-tested on ZZHL. No boot or recovery image is included, and
nothing in this directory should be flashed directly.