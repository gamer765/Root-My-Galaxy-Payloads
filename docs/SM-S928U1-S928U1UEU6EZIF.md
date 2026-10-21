# SM-S928U1 / S928U1UEU6EZIF build record

This record documents the EZIF target reconstructed from the supplied OTA update.

## Firmware and kernel

| Item | Value |
| --- | --- |
| Package | `S928U1UEU6EZIF` |
| Internal build | `S928USQU6EZIF` |
| Kernel release | `6.1.162-android14-11-34343818-abS928USQU6EZIF` |
| Android | 17 / SDK 37 |
| Security patch | 2026-09-05 |
| OTA SHA-256 | `198c3ddcc58f9a048802bd171ffcb99987cf1be9990a5fd8809f80e412c5c5d9` |
| Target vendor_boot SHA-256 | `90652648d3281036412573f9269ce8c59a18eefe6dd8982baf0305ce899f4258` |
| Target init_boot SHA-256 | `5f89256ebc4d51f7f31060abc0f631f9d7b8d1aafdc83ec02351f4280de7c869` |
| Reconstructed boot SHA-256 | `eeebc1467204f2153d05a749686cc75895e42ba911c38f4437b666629c2d4a49` |
| Kernel image SHA-256 | `80220a6eb593f4e8d6957fb0c8950bd34b83c618009b42faf14b915c5cf5d171` |
| P0 probe | `0x1f0000` |
| P0 fingerprint header SHA-256 | `f1c6d91550841766c4a7c9765318801552693d50103cebf2ef11441712200b8a` |

The OTA is incremental from ZZI4. Its `boot.img.p` patch was applied to the
complete ZZI4 boot image before extracting the kernel and reconstructing the
EZIF ELF.

## Offset verification

The reconstructed EZIF ELF contains 107,568 kallsyms entries. The recovered
ELF base is `0xffffffc008000000`. All 103,784 symbols common to the ZZI4 and
EZIF reconstructed ELFs resolve to the same address except five unrelated
data symbols; the exploit-relevant KernelSU and S928 symbols retain the ZZI4
offsets.

## Build lineage

- Legacy S928 exploit engine:
  `139c6dad8cc81be7f4ab2ef03c6a1463cd60f000`
- KernelSU-Next v3.4.2:
  `4c706b5938665866ebe16944a481a7b91e3396af`
- Samsung kernel compatibility commit:
  `b62019e7ac452d73f3198e0f4cc60963d18d3283`
- Samsung userspace compatibility commit:
  `00a165704e9330bca4db6838e63555153edbe01a`
- Samsung late-load PR #1507 merge:
  `b8dafae390eba00cba9983e8ef1e1eaad74ba4ed`

## Completed build

The EZIF branch workflow completed successfully:

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| legacy S928 exploit | 104,128 bytes | `b3470c80cb33738a9dbc516244ff18ea6d4d551b5e9aee83e03e4b35f87991e5` |
| android14-6.1 module | 557,168 bytes | `6935477d3be20281bbc223584cb18d553b677c73c54af3c368fc220ce687752d` |
| KernelSU-Next daemon | 4,179,384 bytes | `3bfe39976c35a3d737bcb2e485f103cd30c8586b67fbc7cbfd696b4af7ecc649` |

The branch copy of `support/targets-v3.json` contains an isolated EZIF test
entry. The confirmed main feed remains unchanged, and SUSFS/regular KernelSU
variants are excluded pending hardware validation of this exact pair.
