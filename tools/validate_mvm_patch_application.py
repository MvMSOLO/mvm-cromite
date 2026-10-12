#!/usr/bin/env python3
"""Apply-check MVM overlays against the exact Chromium source-file snapshot.

This is a target-file integration preflight, not a full Cromite patch-stack
checkout, Chromium compile, or APK build. The two one-line setup edits model
the prerequisites owned by upstream Cromite's branding and package patches.
"""
from __future__ import annotations

import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "build/RELEASE").read_text(encoding="utf-8").strip()
RAW_BASE = f"https://raw.githubusercontent.com/chromium/chromium/{VERSION}/"
SOURCE_FILES = (
    "chrome/android/BUILD.gn",
    "chrome/android/java/res_base/drawable/ic_launcher.xml",
    "chrome/android/java/res_base/drawable/ic_launcher_round.xml",
    "chrome/android/java/res_chromium_base/values/channel_constants.xml",
    "chrome/android/java/res/layout/new_tab_page_layout.xml",
    "chrome/android/java/AndroidManifest.xml",
    "chrome/android/chrome_public_apk_tmpl.gni",
)
PATCHES = (
    "MVM-App-Icon.patch",
    "MVM-NTP-Branding.patch",
    "MVM-App-Label.patch",
    "MVM-Package-Name.patch",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def run_git(args: list[str], cwd: Path) -> None:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        fail(f"git {' '.join(args)} failed: {detail}")


def download_source(path: str) -> str:
    request = urllib.request.Request(
        RAW_BASE + path,
        headers={"User-Agent": "MVM-Cromite-Target-Patch-Preflight/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            source = response.read().decode("utf-8")
    except (OSError, UnicodeError, urllib.error.URLError) as exc:
        fail(f"could not fetch pinned Chromium {VERSION} file {path}: {exc}")
    if not source.strip():
        fail(f"empty source response for {path}")
    return source


def replace_exactly_once(source: str, old: str, new: str, description: str) -> str:
    count = source.count(old)
    if count != 1:
        fail(f"expected exactly one {description}, found {count}")
    return source.replace(old, new, 1)


def main() -> None:
    print(f"Fetching target-file snapshots for Chromium {VERSION}")
    sources = {path: download_source(path) for path in SOURCE_FILES}

    # Model only the known upstream prerequisite lines used by the downstream
    # overlays; this deliberately does not claim that the full Cromite stack ran.
    manifest = sources["chrome/android/java/AndroidManifest.xml"]
    sources["chrome/android/java/AndroidManifest.xml"] = replace_exactly_once(
        manifest,
        'android:label="{% block application_label %}@string/app_name{% endblock %}"',
        'android:label="Cromite"',
        "upstream Cromite application-label baseline",
    )

    package_template = sources["chrome/android/chrome_public_apk_tmpl.gni"]
    package_template = replace_exactly_once(
        package_template,
        'chrome_public_manifest_package = "org.chromium.chrome"',
        'chrome_public_manifest_package = "org.bromite.bromite"',
        "upstream Bromite package-name baseline",
    )
    sources["chrome/android/chrome_public_apk_tmpl.gni"] = replace_exactly_once(
        package_template,
        '} else if (android_channel != "default") {',
        '} else if (android_channel != "default" && android_channel != "stable") {',
        "upstream Cromite stable-channel suffix condition",
    )

    with tempfile.TemporaryDirectory(prefix="mvm-cromite-target-apply-") as temp:
        checkout = Path(temp)
        for relative, content in sources.items():
            target = checkout / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

        run_git(["init", "-q"], checkout)
        run_git(["config", "user.name", "MVM source patch validator"], checkout)
        run_git(["config", "user.email", "mvm-source-patch-validator@example.invalid"], checkout)
        run_git(["add", *SOURCE_FILES], checkout)
        run_git(["commit", "-q", "-m", "Pinned Chromium target-file baseline"], checkout)

        for name in PATCHES:
            patch = ROOT / "build" / "patches" / name
            if not patch.is_file():
                fail(f"required patch missing: {patch.relative_to(ROOT)}")
            print(f"Checking {name}")
            run_git(["apply", "--check", "--whitespace=nowarn", str(patch)], checkout)
            run_git(["apply", "--whitespace=nowarn", str(patch)], checkout)
            print(f"PASS: {name} applies to the prepared Chromium {VERSION} target-file context")

    print("PASS: all four MVM overlays apply in the configured order")
    print("LIMIT: targeted files and three prerequisite line changes only; no full source build or APK verification")


if __name__ == "__main__":
    main()
