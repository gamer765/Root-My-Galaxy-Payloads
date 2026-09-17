#!/usr/bin/env python3
"""Convert upstream Root My Galaxy into a fully offline build.

The payload manifest and all referenced exploit/KernelSU artifacts are copied from
this repository into the Android app assets. A KernelSU Next manager APK supplied
by the build workflow is also bundled so the manager can be installed without a
network connection.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil

SOURCE_PREFIX = "https://raw.githubusercontent.com/gamer765/Root-My-Galaxy-Payloads/main/"


def replace_once(text: str, old: str, new: str, description: str) -> str:
    if old not in text:
        raise SystemExit(f"Could not locate upstream {description}")
    return text.replace(old, new, 1)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--payload-repo", type=pathlib.Path, required=True)
    parser.add_argument("--app", type=pathlib.Path, required=True)
    parser.add_argument("--manager-apk", type=pathlib.Path, required=True)
    parser.add_argument("--manager-metadata", type=pathlib.Path, required=True)
    args = parser.parse_args()

    payload_repo = args.payload_repo.resolve()
    app = args.app.resolve()
    manager_apk = args.manager_apk.resolve()
    manager_metadata_path = args.manager_metadata.resolve()

    manifest_path = payload_repo / "support" / "targets-v3.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != 3:
        raise SystemExit("Expected support manifest schemaVersion 3")

    manager_metadata = json.loads(manager_metadata_path.read_text(encoding="utf-8"))
    if not manager_apk.is_file():
        raise SystemExit(f"Missing KernelSU Next manager APK: {manager_apk}")
    if manager_apk.stat().st_size != int(manager_metadata["size"]):
        raise SystemExit("KernelSU Next manager size does not match metadata")

    asset_root = app / "app" / "src" / "main" / "assets" / "offline"
    asset_root.mkdir(parents=True, exist_ok=True)

    copied: dict[str, int] = {}
    for profile in manifest["payloads"]:
        for key in ("exploit", "kernelsu"):
            item = profile[key]
            url = item["url"]
            if not url.startswith(SOURCE_PREFIX):
                raise SystemExit(f"Unexpected artifact URL for {profile['payloadId']}: {url}")
            rel = url[len(SOURCE_PREFIX):]
            parts = pathlib.PurePosixPath(rel).parts
            if not rel or ".." in parts:
                raise SystemExit(f"Unsafe artifact path: {rel}")
            src = payload_repo / rel
            if not src.is_file():
                raise SystemExit(f"Missing artifact: {rel}")
            expected = int(item["size"])
            actual = src.stat().st_size
            if actual != expected:
                raise SystemExit(
                    f"Size mismatch for {profile['payloadId']} {key}: {rel}: {actual} != {expected}"
                )
            if rel not in copied:
                dst = asset_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied[rel] = actual

    support_dir = asset_root / "support"
    support_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest_path, support_dir / "targets-v3.json")

    manager_dir = asset_root / "manager"
    manager_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manager_apk, manager_dir / "KernelSU-Next.apk")
    shutil.copy2(manager_metadata_path, manager_dir / "manager.json")

    (asset_root / "artifact-index.json").write_text(
        json.dumps(
            {
                "mode": "offline",
                "profileCount": len(manifest["payloads"]),
                "artifactCount": len(copied),
                "bundledPayloadBytes": sum(copied.values()),
                "artifacts": copied,
                "kernelSuNextManager": manager_metadata,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    # Give the offline build a separate package id so it can coexist with upstream.
    gradle = app / "app" / "build.gradle.kts"
    g = gradle.read_text(encoding="utf-8")
    g, app_id_count = re.subn(
        r'applicationId\s*=\s*"dev\.busung\.s25uroot"',
        'applicationId = "dev.busung.s25uroot.offline"',
        g,
        count=1,
    )
    if app_id_count != 1:
        raise SystemExit("Could not replace upstream applicationId")
    g, version_count = re.subn(
        r'versionName\s*=\s*"([^"]+)"',
        lambda m: f'versionName = "{m.group(1)}-offline-ksunext"',
        g,
        count=1,
    )
    if version_count != 1:
        raise SystemExit("Could not append offline version suffix")
    gradle.write_text(g, encoding="utf-8")

    # Remove app-level networking and query the real KernelSU Next package.
    android_manifest = app / "app" / "src" / "main" / "AndroidManifest.xml"
    a = android_manifest.read_text(encoding="utf-8")
    a, permission_count = re.subn(
        r'\s*<uses-permission android:name="android\.permission\.INTERNET"\s*/>\s*',
        "\n",
        a,
        count=1,
    )
    if permission_count != 1:
        raise SystemExit("Could not remove INTERNET permission")
    a = replace_once(
        a,
        '<package android:name="me.weishu.kernelsu" />',
        '<package android:name="com.rifsxd.ksunext" />',
        "KernelSU package query",
    )
    android_manifest.write_text(a, encoding="utf-8")

    # Replace the network payload repository with bundled-asset extraction.
    repo = app / "app" / "src" / "main" / "java" / "dev" / "busung" / "s25uroot" / "PayloadRepository.kt"
    repo.write_text(
        '''package dev.busung.s25uroot

import android.content.Context
import android.system.Os
import java.io.File
import java.io.FileOutputStream

data class VerifiedPayloads(
    val profile: TargetProfile,
    val exploit: File,
    val kernelSu: File,
)

class PayloadRepository(private val context: Context) {
    fun loadTargets(): List<TargetProfile> {
        val bytes = context.assets.open(MANIFEST_ASSET).use { it.readBytes() }
        return SupportManifest.parse(bytes).targets
    }

    fun resolveTarget(snapshot: DeviceSnapshot): TargetProfile = loadTargets()
        .firstOrNull { it.matches(snapshot) }
        ?: error(context.getString(R.string.repo_no_profile))

    fun resolveTarget(profileId: String): TargetProfile = loadTargets()
        .firstOrNull { it.profileId == profileId }
        ?: error(context.getString(R.string.repo_profile_missing, profileId))

    fun download(profile: TargetProfile, onProgress: (String) -> Unit): VerifiedPayloads {
        val directory = File(context.filesDir, "payloads/${profile.profileId}").apply { mkdirs() }
        val exploit = extractArtifact(
            profile.exploit,
            File(directory, "cve-2026-43499-app.so"),
            context.getString(R.string.artifact_exploit),
            onProgress,
        )
        val kernelSu = extractArtifact(
            profile.kernelSu,
            File(directory, "ksud-s25u-kdp"),
            context.getString(R.string.artifact_kernelsu),
            onProgress,
        )
        Os.chmod(exploit.absolutePath, 0b100100100)
        Os.chmod(kernelSu.absolutePath, 0b100100100)
        return VerifiedPayloads(profile, exploit, kernelSu)
    }

    private fun extractArtifact(
        artifact: RemoteArtifact,
        destination: File,
        label: String,
        onProgress: (String) -> Unit,
    ): File {
        onProgress("Loading bundled $label")
        val temporary = File(destination.parentFile, "${destination.name}.part")
        if (temporary.exists()) temporary.delete()

        var total = 0L
        context.assets.open(assetPath(artifact.url)).use { input ->
            FileOutputStream(temporary).use { output ->
                val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    total += count
                    require(total <= artifact.size) {
                        context.getString(R.string.repo_size_exceeded, label)
                    }
                    output.write(buffer, 0, count)
                }
                output.fd.sync()
            }
        }

        require(total == artifact.size) {
            context.getString(R.string.repo_incomplete, label)
        }
        if (destination.exists()) destination.delete()
        require(temporary.renameTo(destination)) {
            context.getString(R.string.repo_finalize_failed, label)
        }
        onProgress(context.getString(R.string.repo_verified, label))
        return destination
    }

    private fun assetPath(url: String): String {
        require(url.startsWith(SOURCE_PREFIX)) {
            context.getString(R.string.repo_url_invalid)
        }
        val relative = url.removePrefix(SOURCE_PREFIX)
        require(relative.isNotBlank() && relative.split('/').none { it == ".." }) {
            context.getString(R.string.repo_url_invalid)
        }
        return "offline/$relative"
    }

    companion object {
        private const val MANIFEST_ASSET = "offline/support/targets-v3.json"
        private const val SOURCE_PREFIX =
            "https://raw.githubusercontent.com/gamer765/Root-My-Galaxy-Payloads/main/"
    }
}
''',
        encoding="utf-8",
    )

    # Disable Root My Galaxy's own network updater in the offline variant.
    updater = app / "app" / "src" / "main" / "java" / "dev" / "busung" / "s25uroot" / "AppUpdater.kt"
    updater.write_text(
        '''package dev.busung.s25uroot

import android.content.Context
import android.content.Intent
import android.net.Uri
import java.io.File

data class UpdateInfo(
    val versionName: String,
    val apkUrl: String?,
    val releaseUrl: String,
)

const val ROOT_MY_GALAXY_URL = "https://github.com/BuSung-dev/Root-My-Galaxy"

object AppUpdater {
    suspend fun fetchLatestRelease(): UpdateInfo = UpdateInfo(
        versionName = BuildConfig.VERSION_NAME,
        apkUrl = null,
        releaseUrl = ROOT_MY_GALAXY_URL,
    )

    fun isUpdateAvailable(latestVersion: String, currentVersion: String): Boolean = false

    suspend fun downloadApk(
        context: Context,
        url: String,
        onProgress: (Float) -> Unit = {},
    ): File? = null

    fun installApk(context: Context, apk: File): Boolean = false

    fun openReleasesPage(context: Context) {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(ROOT_MY_GALAXY_URL)))
    }
}
''',
        encoding="utf-8",
    )

    # Replace standard KernelSU manager integration with bundled KernelSU Next.
    main_activity = app / "app" / "src" / "main" / "java" / "dev" / "busung" / "s25uroot" / "MainActivity.kt"
    m = main_activity.read_text(encoding="utf-8")
    old_constants = '''private const val KERNEL_SU_MANAGER_URL =
    "https://github.com/tiann/KernelSU/releases/download/v3.2.5/KernelSU_v3.2.5_32525-release.apk"
private const val KERNEL_SU_MANAGER_PACKAGE = "me.weishu.kernelsu"
private const val KERNEL_SU_HOME_URL = "https://kernelsu.org/"'''
    new_constants = '''private const val KERNEL_SU_MANAGER_PACKAGE = "com.rifsxd.ksunext"
private const val KERNEL_SU_MANAGER_ASSET = "offline/manager/KernelSU-Next.apk"
private const val KERNEL_SU_HOME_URL = "https://kernelsu-next.github.io/webpage/"'''
    m = replace_once(m, old_constants, new_constants, "KernelSU manager constants")

    old_manager_function = '''private fun openKernelSuManager(context: Context) {
    val launch = context.packageManager.getLaunchIntentForPackage(KERNEL_SU_MANAGER_PACKAGE)
    if (launch != null) {
        context.startActivity(launch)
    } else {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(KERNEL_SU_MANAGER_URL)))
    }
}'''
    new_manager_function = '''private fun openKernelSuManager(context: Context) {
    val launch = context.packageManager.getLaunchIntentForPackage(KERNEL_SU_MANAGER_PACKAGE)
    if (launch != null) {
        context.startActivity(launch)
        return
    }

    try {
        val directory = java.io.File(context.cacheDir, "updates").apply { mkdirs() }
        val apk = java.io.File(directory, "KernelSU-Next.apk")
        context.assets.open(KERNEL_SU_MANAGER_ASSET).use { input ->
            apk.outputStream().use { output -> input.copyTo(output) }
        }
        val uri = androidx.core.content.FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            apk,
        )
        context.startActivity(
            Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            },
        )
    } catch (error: Throwable) {
        Toast.makeText(
            context,
            "Unable to install bundled KernelSU Next manager: ${error.message ?: error.javaClass.simpleName}",
            Toast.LENGTH_LONG,
        ).show()
    }
}'''
    m = replace_once(m, old_manager_function, new_manager_function, "KernelSU manager launcher")

    # Upstream has a second manager button path which formerly opened the URL directly.
    # Route it through the same local installer so no manager action requires networking.
    m = m.replace(
        "uriHandler.openUri(KERNEL_SU_MANAGER_URL)",
        "openKernelSuManager(context)",
    )
    if "KERNEL_SU_MANAGER_URL" in m:
        raise SystemExit("An upstream KernelSU manager URL reference remains after conversion")
    main_activity.write_text(m, encoding="utf-8")

    strings = app / "app" / "src" / "main" / "res" / "values" / "strings.xml"
    s = strings.read_text(encoding="utf-8")
    replacements = {
        '<string name="app_name">Root My Galaxy</string>': '<string name="app_name">Root My Galaxy Offline</string>',
        "The app will verify the support profile, then download and run the exploit and KernelSU payload from GitHub.": "The app will verify the support profile, then load and run the exploit and KernelSU payload bundled inside this APK.",
        '<string name="step_download_title">Download</string>': '<string name="step_download_title">Payloads</string>',
        '<string name="step_download_detail">Load the support manifest</string>': '<string name="step_download_detail">Load bundled manifest and payloads</string>',
        '<string name="phase_downloading">Downloading commit-pinned payloads from GitHub</string>': '<string name="phase_downloading">Loading bundled offline payloads</string>',
        '<string name="status_checking_github">Checking GitHub support manifest</string>': '<string name="status_checking_github">Checking bundled support manifest</string>',
        '<string name="status_downloading_payload">Downloading payloads</string>': '<string name="status_downloading_payload">Loading bundled payloads</string>',
        '<string name="log_download_verified">[+] Payload download complete</string>': '<string name="log_download_verified">[+] Bundled payload verified</string>',
        '<string name="repo_downloading">Downloading %1$s</string>': '<string name="repo_downloading">Loading bundled %1$s</string>',
        '<string name="repo_incomplete">%1$s download is incomplete</string>': '<string name="repo_incomplete">Bundled %1$s is incomplete</string>',
        '<string name="updater_check">Check for updates</string>': '<string name="updater_check">Offline build</string>',
        "Tap to install KernelSU Manager": "Tap to install KernelSU Next Manager",
        "Tap to open KernelSU Manager": "Tap to open KernelSU Next Manager",
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    strings.write_text(s, encoding="utf-8")

    print(f"Profiles: {len(manifest['payloads'])}")
    print(f"Unique bundled payload artifacts: {len(copied)}")
    print(f"Bundled payload bytes: {sum(copied.values())}")
    print(f"KernelSU Next manager: {manager_metadata['release']} / {manager_metadata['asset']}")


if __name__ == "__main__":
    main()
