# SM-S928U1 S928U1UEU6ZZI4 build profile

This profile targets the Samsung package release `S928U1UEU6ZZI4`. The
matching boot metadata and kernel release use Samsung's internal US variant
identifier:

`6.1.162-android14-11-34343818-abS928USQU6ZZI4`

The attached `BSDIFF40` patch was applied to the complete DZH3-derived
`boot.zzhl.img`, producing `boot.zzi4.img`. The supplied `vendor_boot.img`
and `abl.elf` independently contain the same `S928USQU6ZZI4` release marker.

## Repository contents

- `target.h` — ZZI4-specific physical P0, slide, ABI, symbol, and layout
  constants.
- `p0_fingerprint.h` — generated from `boot.zzi4.img` at probe offset
  `0x1f0000`.
- `artifacts/e3q-S928USQU6ZZI4/cve-2026-43499-app.so` — legacy S928
  stable-race CVE-2026-43499 app payload for this exact target.

The payload source is configured for KernelSU Next handoff only. No original
KernelSU module or daemon is part of this target.

## Validation status

The target profile has passed local compilation, exact symbol-offset checks
against the recovered ZZI4 ELF, and payload size/format checks. The matching
KernelSU Next module and daemon still require an exact build and hardware
test. This profile is therefore not in the automatic support feed yet.

The full image inputs and their hashes are recorded in
`docs/SM-S928U1-S928U1UEU6ZZI4.md`.
