#!/usr/bin/env python3
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "appsrc"
PAYLOADS = ROOT / "payloads"
ASSETS = APP / "app/src/main/assets/offline"
MANIFEST_SRC = PAYLOADS / "support/targets-v3.json"

if not APP.exists() or not MANIFEST_SRC.exists():
    raise SystemExit("Expected appsrc/ and payloads/support/targets-v3.json")

manifest = json.loads(MANIFEST_SRC.read_text(encoding="utf-8"))
if manifest.get("schemaVersion") != 3:
    raise SystemExit("Expected support manifest schemaVersion 3")

ASSETS.mkdir(parents=True, exist_ok=True)
(ASSETS / "support").mkdir(parents=True, exist_ok=True)
shutil.copy2(MANIFEST_SRC, ASSETS / "support/targets-v3.json")

raw_prefix = "/gamer765/Root-My-Galaxy-Payloads/main/"
paths = set()
for profile in manifest.get("payloads", []):
    for key in ("exploit", "kernelsu"):
        artifact = profile[key]
        parsed = urlparse(artifact["url"])
        if raw_prefix not in parsed.path:
            raise SystemExit(f"Unsupported artifact URL: {artifact['url']}")
        rel = parsed.path.split(raw_prefix, 1)[1]
        paths.add(rel)

checksums = {}
for rel in sorted(paths):
    source = PAYLOADS / rel
    if not source.is_file():
        raise SystemExit(f"Manifest references missing file: {rel}")
    destination = ASSETS / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    checksums[rel] = hashlib.sha256(source.read_bytes()).hexdigest()

(ASSETS / "checksums.json").write_text(
    json.dumps(checksums, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

repo_kt = APP / "app/src/main/java/dev/busung/s25uroot/PayloadRepository.kt"
repo_kt.write_text(r'''package dev.busung.s25uroot

import android.content.Context
import android.system.Os
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import org.json.JSONObject

data class VerifiedPayloads(
    val profile: TargetProfile,
    val exploit: File,
    val kernelSu: File,
)

class PayloadRepository(private val context: Context) {
    private val checksums: Map<String, String> by lazy { loadChecksums() }

    fun loadTargets(): List<TargetProfile> =
        context.assets.open(MANIFEST_ASSET).use { SupportManifest.parse(it.readBytes()) }.targets

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
        val relativePath = artifactPath(artifact.url)
        val expectedSha256 = checksums[relativePath]
            ?: error("Missing embedded checksum for $relativePath")

        if (destination.isFile &&
            destination.length() == artifact.size &&
            sha256(destination).equals(expectedSha256, ignoreCase = true)
        ) {
            onProgress("Using bundled $label")
            return destination
        }

        onProgress("Extracting bundled $label")
        val temporary = File(destination.parentFile, "${destination.name}.part")
        if (temporary.exists()) temporary.delete()

        var total = 0L
        context.assets.open("$ASSET_ROOT/$relativePath").use { input ->
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

        require(total == artifact.size) { context.getString(R.string.repo_incomplete, label) }
        require(sha256(temporary).equals(expectedSha256, ignoreCase = true)) {
            "Bundled $label checksum mismatch"
        }
        if (destination.exists()) destination.delete()
        require(temporary.renameTo(destination)) {
            context.getString(R.string.repo_finalize_failed, label)
        }
        onProgress("Verified bundled $label")
        return destination
    }

    private fun artifactPath(url: String): String {
        val marker = "/gamer765/Root-My-Galaxy-Payloads/main/"
        val index = url.indexOf(marker)
        require(index >= 0) { context.getString(R.string.repo_url_invalid) }
        return url.substring(index + marker.length)
    }

    private fun loadChecksums(): Map<String, String> {
        val root = context.assets.open(CHECKSUM_ASSET).use {
            JSONObject(it.readBytes().toString(Charsets.UTF_8))
        }
        return buildMap {
            val keys = root.keys()
            while (keys.hasNext()) {
                val key = keys.next()
                put(key, root.getString(key))
            }
        }
    }

    private fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(8192)
            while (true) {
                val count = input.read(buffer)
                if (count < 0) break
                digest.update(buffer, 0, count)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    companion object {
        private const val ASSET_ROOT = "offline"
        private const val MANIFEST_ASSET = "$ASSET_ROOT/support/targets-v3.json"
        private const val CHECKSUM_ASSET = "$ASSET_ROOT/checksums.json"
    }
}
''', encoding="utf-8")

android_manifest = APP / "app/src/main/AndroidManifest.xml"
text = android_manifest.read_text(encoding="utf-8")
text = re.sub(r'\s*<uses-permission android:name="android\.permission\.INTERNET"\s*/>\s*', '\n', text, count=1)
android_manifest.write_text(text, encoding="utf-8")

app_updater = APP / "app/src/main/java/dev/busung/s25uroot/AppUpdater.kt"
app_updater.write_text(r'''package dev.busung.s25uroot

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import androidx.core.content.FileProvider
import java.io.File

data class UpdateInfo(
    val versionName: String,
    val apkUrl: String?,
    val releaseUrl: String,
)

const val ROOT_MY_GALAXY_URL = ""

object AppUpdater {
    suspend fun fetchLatestRelease(): UpdateInfo? =
        UpdateInfo(BuildConfig.VERSION_NAME, null, "")

    fun isUpdateAvailable(latestVersion: String, currentVersion: String): Boolean = false

    suspend fun downloadApk(
        context: Context,
        url: String,
        onProgress: (Float) -> Unit = {},
    ): File? = null

    fun installApk(context: Context, apk: File): Boolean {
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", apk)
        return try {
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
            context.startActivity(intent)
            true
        } catch (_: ActivityNotFoundException) {
            false
        }
    }

    fun openReleasesPage(context: Context) = Unit
}
''', encoding="utf-8")

main_activity = APP / "app/src/main/java/dev/busung/s25uroot/MainActivity.kt"
text = main_activity.read_text(encoding="utf-8")
text = text.replace('LaunchedEffect(Unit) { checkForUpdate() }', '// Offline build: automatic update checks are disabled.')
main_activity.write_text(text, encoding="utf-8")

build_gradle = APP / "app/build.gradle.kts"
text = build_gradle.read_text(encoding="utf-8")
text = text.replace('applicationId = "dev.busung.s25uroot"', 'applicationId = "dev.busung.s25uroot.offline"')
match = re.search(r'versionName = "([^"]+)"', text)
if match:
    original = match.group(1)
    text = text[:match.start()] + f'versionName = "{original}-offline.1"' + text[match.end():]
build_gradle.write_text(text, encoding="utf-8")

strings = APP / "app/src/main/res/values/strings.xml"
text = strings.read_text(encoding="utf-8")
text = re.sub(r'(<string name="app_name">).*?(</string>)', r'\1Root My Galaxy Offline\2', text)
text = text.replace('Checking support manifest on GitHub', 'Checking bundled support manifest')
text = text.replace('Checking support profile on GitHub', 'Checking bundled support profile')
text = text.replace('Downloading payload', 'Preparing bundled payload')
text = text.replace('download and run the exploit and KernelSU payload from GitHub', 'verify and run the bundled exploit and KernelSU payload')
strings.write_text(text, encoding="utf-8")

summary = {
    "profiles": len(manifest.get("payloads", [])),
    "uniqueEmbeddedArtifacts": len(paths),
    "embeddedBytes": sum((PAYLOADS / rel).stat().st_size for rel in paths),
}
(APP / "OFFLINE_BUILD.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary))
