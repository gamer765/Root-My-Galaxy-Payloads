package dev.busung.s25uroot

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

/** Offline build: never performs update checks or downloads. */
object AppUpdater {
    suspend fun fetchLatestRelease(): UpdateInfo =
        UpdateInfo(
            versionName = BuildConfig.VERSION_NAME,
            apkUrl = null,
            releaseUrl = ROOT_MY_GALAXY_URL,
        )

    fun isUpdateAvailable(latestVersion: String, currentVersion: String): Boolean = false

    suspend fun downloadApk(
        context: Context,
        url: String,
        onProgress: (Float) -> Unit = {},
    ): File? {
        onProgress(0f)
        return null
    }

    fun installApk(context: Context, apk: File): Boolean = false

    fun openReleasesPage(context: Context) {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(ROOT_MY_GALAXY_URL)))
    }
}
