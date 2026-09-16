#!/usr/bin/env python3
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

PAYLOADS = Path(os.environ.get("PAYLOAD_REPO", "payloads")).resolve()
APP = Path(os.environ.get("APP_REPO", "appsrc")).resolve()
PREFIX = "https://raw.githubusercontent.com/gamer765/Root-My-Galaxy-Payloads/main/"
MANIFEST_REL = Path("support/targets-v3.json")
OFFLINE_ASSETS = APP / "app/src/main/assets/offline"
KOTLIN_DIR = APP / "app/src/main/java/dev/busung/s25uroot"


def git_sha(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def replace_string(xml: str, name: str, value: str) -> str:
    pattern = rf'(<string\s+name="{re.escape(name)}"[^>]*>).*?(</string>)'
    return re.sub(pattern, lambda m: m.group(1) + value + m.group(2), xml, count=1, flags=re.S)


def remove_string(xml: str, name: str) -> str:
    pattern = rf'\s*<string\s+name="{re.escape(name)}"[^>]*>.*?</string>'
    return re.sub(pattern, "", xml, flags=re.S)


def main() -> None:
    manifest_path = PAYLOADS / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schemaVersion") != 3 or not manifest.get("payloads"):
        raise SystemExit("support/targets-v3.json is missing or has an unsupported schema")

    if OFFLINE_ASSETS.exists():
        shutil.rmtree(OFFLINE_ASSETS)
    (OFFLINE_ASSETS / "support").mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest_path, OFFLINE_ASSETS / "support/targets-v3.json")

    index = {
        "schemaVersion": 1,
        "payloadRepository": "gamer765/Root-My-Galaxy-Payloads",
        "payloadCommit": git_sha(PAYLOADS),
        "upstreamRepository": "BuSung-dev/Root-My-Galaxy",
        "upstreamCommit": git_sha(APP),
        "artifacts": {},
    }

    unique_urls = set()
    for profile in manifest["payloads"]:
        for field in ("exploit", "kernelsu"):
            artifact = profile[field]
            url = artifact["url"]
            if not url.startswith(PREFIX):
                raise SystemExit(f"Refusing non-local payload URL in offline manifest: {url}")
            unique_urls.add(url)

    total_bytes = 0
    for url in sorted(unique_urls):
        rel = Path(url.removeprefix(PREFIX))
        source = PAYLOADS / rel
        if not source.is_file():
            raise SystemExit(f"Manifest references missing file: {rel}")
        expected_sizes = {
            int(profile[field]["size"])
            for profile in manifest["payloads"]
            for field in ("exploit", "kernelsu")
            if profile[field]["url"] == url
        }
        if len(expected_sizes) != 1:
            raise SystemExit(f"Conflicting manifest sizes for {url}: {sorted(expected_sizes)}")
        expected_size = expected_sizes.pop()
        actual_size = source.stat().st_size
        if actual_size != expected_size:
            raise SystemExit(f"Size mismatch for {rel}: manifest={expected_size} file={actual_size}")

        destination = OFFLINE_ASSETS / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        digest = sha256(destination)
        index["artifacts"][url] = {
            "assetPath": f"offline/{rel.as_posix()}",
            "size": actual_size,
            "sha256": digest,
        }
        total_bytes += actual_size

    (OFFLINE_ASSETS / "artifact-index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # Replace network-backed app components with offline implementations.
    shutil.copy2(PAYLOADS / "offline-app/PayloadRepository.kt", KOTLIN_DIR / "PayloadRepository.kt")
    shutil.copy2(PAYLOADS / "offline-app/AppUpdater.kt", KOTLIN_DIR / "AppUpdater.kt")

    # A true offline build should not be able to make network requests itself.
    android_manifest = APP / "app/src/main/AndroidManifest.xml"
    text = android_manifest.read_text(encoding="utf-8")
    text = text.replace('    <uses-permission android:name="android.permission.INTERNET" />\n', "")
    text = text.replace('    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />\n', "")
    android_manifest.write_text(text, encoding="utf-8")

    # Give the offline build a distinct package ID so it can coexist with upstream.
    gradle = APP / "app/build.gradle.kts"
    text = gradle.read_text(encoding="utf-8")
    text = re.sub(r'applicationId\s*=\s*"[^"]+"', 'applicationId = "com.gamer765.rootmygalaxy.offline"', text, count=1)
    version_match = re.search(r'versionName\s*=\s*"([^"]+)"', text)
    if version_match:
        base_version = version_match.group(1).removesuffix("-offline")
        text = text[:version_match.start(1)] + base_version + "-offline" + text[version_match.end(1):]
    gradle.write_text(text, encoding="utf-8")

    # Update the English copy. Remove these same keys from translations so they
    # fall back to the accurate offline wording instead of saying "GitHub".
    base_strings = APP / "app/src/main/res/values/strings.xml"
    base = base_strings.read_text(encoding="utf-8")
    replacements = {
        "app_name": "Root My Galaxy Offline",
        "status_checking_github": "Checking bundled support manifest",
        "status_downloading_payload": "Loading bundled payload",
        "phase_downloading": "Loading bundled payloads",
        "install_confirm_body": "The app will verify the bundled support profile, then run the embedded exploit and KernelSU payload. No internet connection is required.",
        "repo_downloading": "Loading bundled %1$s",
        "repo_incomplete": "Bundled %1$s is incomplete",
        "repo_verified": "Bundled %1$s verified",
        "step_download_title": "Load payload",
        "step_download_detail": "Load bundled support files",
        "log_download_verified": "Bundled payload verified",
    }
    for name, value in replacements.items():
        base = replace_string(base, name, value)
    base_strings.write_text(base, encoding="utf-8")

    for values_dir in (APP / "app/src/main/res").glob("values-*"):
        translated = values_dir / "strings.xml"
        if not translated.exists():
            continue
        localized = translated.read_text(encoding="utf-8")
        for name in replacements:
            localized = remove_string(localized, name)
        translated.write_text(localized, encoding="utf-8")

    print(f"Bundled {len(manifest['payloads'])} profiles and {len(unique_urls)} unique artifacts")
    print(f"Embedded payload bytes: {total_bytes:,}")
    print(f"Payload source commit: {index['payloadCommit']}")
    print(f"Upstream source commit: {index['upstreamCommit']}")


if __name__ == "__main__":
    main()
