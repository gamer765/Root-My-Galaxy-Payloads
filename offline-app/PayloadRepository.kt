package dev.busung.s25uroot

import android.content.Context
import android.system.Os
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.security.MessageDigest
import java.util.Locale

data class VerifiedPayloads(
    val profile: TargetProfile,
    val exploit: File,
    val kernelSu: File,
)

private data class BundledArtifact(
    val assetPath: String,
    val size: Long,
    val sha256: String,
)

/**
 * Offline payload repository.
 *
 * The support manifest and every artifact referenced by it are packaged under
 * app/src/main/assets/offline at build time. Remote-looking URLs in the
 * manifest are used only as stable keys into the bundled artifact index; this
 * class never opens a network connection.
 */
class PayloadRepository(private val context: Context) {
    private val manifest: SupportManifest by lazy {
        val bytes = context.assets.open(MANIFEST_ASSET).use { it.readBytes() }
        SupportManifest.parse(bytes)
    }

    private val bundledArtifacts: Map<String, BundledArtifact> by lazy {
        val text = context.assets.open(INDEX_ASSET).bufferedReader().use { it.readText() }
        val root = JSONObject(text).getJSONObject("artifacts")
        buildMap {
            val keys = root.keys()
            while (keys.hasNext()) {
                val url = keys.next()
                val item = root.getJSONObject(url)
                put(
                    url,
                    BundledArtifact(
                        assetPath = item.getString("assetPath"),
                        size = item.getLong("size"),
                        sha256 = item.getString("sha256").lowercase(Locale.ROOT),
                    ),
                )
            }
        }
    }

    fun loadTargets(): List<TargetProfile> = manifest.targets

    fun resolveTarget(snapshot: DeviceSnapshot): TargetProfile {
        val candidates = loadTargets().filter { it.matches(snapshot) }
        if (candidates.isEmpty()) error(context.getString(R.string.repo_no_profile))
        if (candidates.size == 1) return candidates.single()

        // Several Samsung firmware revisions can share the same model and
        // kernel version. Prefer the firmware suffix embedded in Build.DISPLAY
        // / fingerprint (DZF2, DZG1, DZH3, ZZHL, ZZI4, BZG3, etc.) rather than
        // silently selecting the first model+kernel match.
        val buildIdentity = "${snapshot.buildId} ${snapshot.fingerprint}"
            .uppercase(Locale.ROOT)
        val exact = candidates.filter { profile ->
            val suffix = firmwareSuffix(profile)
            suffix != null && buildIdentity.contains(suffix)
        }
        if (exact.size == 1) return exact.single()

        error(
            "Multiple bundled payloads match ${snapshot.model} / ${snapshot.kernelVersion}. " +
                "Select the exact firmware profile manually.",
        )
    }

    fun resolveTarget(profileId: String): TargetProfile = loadTargets()
        .firstOrNull { it.profileId == profileId }
        ?: error(context.getString(R.string.repo_profile_missing, profileId))

    fun download(profile: TargetProfile, onProgress: (String) -> Unit): VerifiedPayloads {
        val directory = File(context.filesDir, "payloads/${profile.profileId}").apply { mkdirs() }
        val exploit = copyBundledArtifact(
            profile.exploit,
            File(directory, "cve-2026-43499-app.so"),
            context.getString(R.string.artifact_exploit),
            onProgress,
        )
        val kernelSu = copyBundledArtifact(
            profile.kernelSu,
            File(directory, "ksud-s25u-kdp"),
            context.getString(R.string.artifact_kernelsu),
            onProgress,
        )
        Os.chmod(exploit.absolutePath, 0b100100100)
        Os.chmod(kernelSu.absolutePath, 0b100100100)
        return VerifiedPayloads(profile, exploit, kernelSu)
    }

    private fun copyBundledArtifact(
        artifact: RemoteArtifact,
        destination: File,
        label: String,
        onProgress: (String) -> Unit,
    ): File {
        val bundled = bundledArtifacts[artifact.url]
            ?: error("Bundled artifact is missing from the offline index: ${artifact.url}")
        require(bundled.size == artifact.size) {
            context.getString(R.string.repo_size_mismatch, label)
        }

        onProgress(context.getString(R.string.repo_downloading, label))
        val temporary = File(destination.parentFile, "${destination.name}.part")
        temporary.delete()

        val digest = MessageDigest.getInstance("SHA-256")
        var total = 0L
        context.assets.open(bundled.assetPath).use { input ->
            FileOutputStream(temporary).use { output ->
                val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    total += count
                    require(total <= bundled.size) {
                        context.getString(R.string.repo_size_exceeded, label)
                    }
                    digest.update(buffer, 0, count)
                    output.write(buffer, 0, count)
                }
                output.fd.sync()
            }
        }

        require(total == bundled.size) { context.getString(R.string.repo_incomplete, label) }
        val actualSha256 = digest.digest().joinToString("") { "%02x".format(it) }
        require(actualSha256.equals(bundled.sha256, ignoreCase = true)) {
            "$label SHA-256 does not match the bundled build index"
        }

        if (destination.exists()) destination.delete()
        require(temporary.renameTo(destination)) {
            context.getString(R.string.repo_finalize_failed, label)
        }
        onProgress(context.getString(R.string.repo_verified, label))
        return destination
    }

    private fun firmwareSuffix(profile: TargetProfile): String? {
        val tail = profile.profileId.substringAfterLast('-')
            .uppercase(Locale.ROOT)
            .takeLast(4)
        return tail.takeIf { value ->
            value.length == 4 && value.any(Char::isLetter) && value.any(Char::isDigit)
        }
    }

    companion object {
        private const val MANIFEST_ASSET = "offline/support/targets-v3.json"
        private const val INDEX_ASSET = "offline/artifact-index.json"
    }
}
