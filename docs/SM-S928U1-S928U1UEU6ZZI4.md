# SM-S928U1 S928U1UEU6ZZI4 source update

This report records the source update for Samsung package release
`S928U1UEU6ZZI4`. The outer package identifier is retained here alongside the
internal boot/kernel identifier, `S928USQU6ZZI4`.

## Rebuilt image chain

The new `boot.img.p` is a BSDIFF40 patch with a 100,663,296-byte output. It
was applied to the previously rebuilt full `boot.zzhl.img`, whose SHA-256 is
`dc6c096d21a6798bc16bcb69e0eebdc9eec14c7a5bcbb94bab0b6994226e476f`.
The patch SHA-256 is
`61ac809af80695a0f269c8a155681cf84dbdf4645ef22fb16fc03cea53b3cb04`.

The result and the supplied matching companion images are:

| Object | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `boot.zzi4.img` | 100,663,296 | `2ca1399a762c28846f989214116be54ae0c86a5ebf0720872947a690fd54389c` |
| `vendor_boot.zzi4.img` | 100,663,296 | `2ed8a6a80ed8d128dc576c4adcf66ce5cb6543172893906615f08b6aa385ac5d` |
| `abl.zzi4.elf` | 2,441,528 | `a110094a827db2d01d2755c5581b5c73dada2ab063d0741ced5ce9967758ef36` |

The patch was applied to `boot.zzhl.img` only; `vendor_boot.zzi4.img` and
`abl.zzi4.elf` are the supplied ZZI4 companion binaries.

The rebuilt boot image contains:

`6.1.162-android14-11-34343818-abS928USQU6ZZI4`

The companion `vendor_boot` and ABL inputs contain the corresponding
`S928USQU6ZZI4` marker.

## Kernel evidence used for the profile

| Item | Value |
| --- | --- |
| Kernel image size | 38,140,416 bytes |
| Kernel image SHA-256 | `4b5bb61e4300bed707b9d82d0662148f16e17d6365f50ad92ffeae9df3a7f6cd` |
| Recovered ELF base | `0xffffffc008000000` |
| BTF range | `0x1820e90-0x1dd7cb8` |
| BTF size | 5,991,976 bytes |
| BTF SHA-256 | `00f86d507632aa76102e8b7bf783fb778373529e2c5d88f9fa2e53aa7442bea0` |
| P0 probe offset | `0x1f0000` |
| P0 fingerprint SHA-256 | `575d1e4279792ccef821a39a818bd58b2a4f482aeb2caff34e882a5633228a93` |

The BTF matches the prior ZZHL kernel byte-for-byte, so the verified
structure-layout constants were retained. The ZZI4 target header updates the
firmware-specific ashmem, allocator, and netfilter logger offsets and keeps
the compact `rt_mutex_waiter` ABI selection used by the S928 source path.

## Exploit source update

The app payload was rebuilt with the legacy S928 stable-race path and the new
ZZI4 profile:

| Artifact | Size (bytes) | SHA-256 |
| --- | ---: | --- |
| `artifacts/e3q-S928USQU6ZZI4/cve-2026-43499-app.so` | 104,128 | `dcce58c0e130ec276a8e56f99cc124d002982ab32aedac5bc319cc9088de1cfa` |

The resulting ELF is a stripped AArch64 shared object. Its source profile is
`src/targets/e3q-S928USQU6ZZI4`; it is not a copy of the ZZHL artifact.

## Release status

- ZZI4 image set: rebuilt and hash-verified.
- ZZI4 target profile: added and compiled.
- Legacy S928 app payload: rebuilt and statically validated.
- KernelSU Next module/daemon: not yet rebuilt for ZZI4.
- Automatic installation feed: unchanged pending hardware validation.
