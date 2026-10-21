# e3q-S928USQU6EZIF target profile

This profile targets the Samsung Galaxy S24 Ultra SM-S928U1 package
`S928U1UEU6EZIF`, with kernel release:

`6.1.162-android14-11-34343818-abS928USQU6EZIF`

The EZIF target boot image was reconstructed by applying the supplied
`boot.img.p` BSDIFF40 patch to the complete ZZI4 `boot.img`. The resulting
kernel image is 38,140,416 bytes with SHA-256:

`80220a6eb593f4e8d6957fb0c8950bd34b83c618009b42faf14b915c5cf5d171`

The P0 oracle uses probe offset `0x1f0000`. Its generated fingerprint header
has SHA-256:

`f1c6d91550841766c4a7c9765318801552693d50103cebf2ef11441712200b8a`

The reconstructed EZIF ELF resolves the exploit-relevant symbols at the same
offsets as the confirmed ZZI4 6.1.162 kernel. The target-specific profile
therefore updates the release fingerprint and P0 table while retaining the
verified compact waiter, KASLR, physical load, and symbol/layout constants.

The app payload is built from the legacy S928 engine at commit
`139c6dad8cc81be7f4ab2ef03c6a1463cd60f000`. The KernelSU side is the initial
KernelSU-Next v3.4.2 lineage at commit
`4c706b5938665866ebe16944a481a7b91e3396af`, with Samsung late-load PR #1507
merge `b8dafae390eba00cba9983e8ef1e1eaad74ba4ed`. SUSFS and regular KernelSU
variants are excluded.

The completed branch build produced:

- exploit: `b3470c80cb33738a9dbc516244ff18ea6d4d551b5e9aee83e03e4b35f87991e5`
- android14-6.1 module: `6935477d3be20281bbc223584cb18d553b677c73c54af3c368fc220ce687752d`
- KernelSU-Next daemon: `3bfe39976c35a3d737bcb2e485f103cd30c8586b67fbc7cbfd696b4af7ecc649`

The artifacts are published on branch `ezif-ksun-342`. The automatic support
feed remains unchanged pending hardware validation of this exact pair.
