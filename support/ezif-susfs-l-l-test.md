# EZIF S24 Ultra Samsung SUSFS L-L test build

This manual-only build adapts the Samsung RKP/KDP/DEFEX-aware SUSFS LKM from
[`yettocom/susfs-lkm-L-L-module`](https://github.com/yettocom/susfs-lkm-L-L-module)
for the Galaxy S24 Ultra `SM-S928U1` on firmware `S928U1UEU6EZIF`.

It builds against the exact kernel release
`6.1.162-android14-11-34343818-abS928USQU6EZIF`, with
`SUSFS_SAMSUNG_NO_PATCH_TEXT=1`, and produces an EZIF-only KernelSU module ZIP.
The build reuses the pinned L-L package's loader and probe binaries after
checking the published ZIP hash. Its only packaged KMI is `android14-6.1`, and
the module's release check is pinned to the EZIF kernel string.

## Scope and status

- This is a separate test artifact. It is not in `support/targets-v3.json` and
  does not alter the confirmed KernelSU Next payload or its feed entry.
- The build prevents the module from using its default Samsung text/rodata
  patch paths. The reference implementation uses its own guarded RKP branch
  route and fallback hooks; these still need testing on this exact firmware.
- A successful build does not confirm safe loading or compatibility with the
  current Nyx/Vector/Zygisk Next/LSPosed module stack.
- Do not install it alongside another active SUSFS implementation. Its package
  is designed to load on KernelSU's late-load or soft-reboot path.

Run `.github/workflows/ezif-susfs-l-l-test.yml` with **Actions → Run workflow**.
The workflow uploads the `.ko`, an EZIF-only KernelSU module ZIP, and a build
report for review. It does not publish a GitHub release or enable app-feed
selection.
