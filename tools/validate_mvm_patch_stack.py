#!/usr/bin/env python3
"""Static checks for the MVM downstream overlay in the Cromite patch stack."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ID = "com.mvmsolo.mvmbrowser"
PATCH_NAME = "MVM-Package-Name.patch"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    release_path = ROOT / "build/RELEASE"
    patch_list_path = ROOT / "build/cromite_patches_list.txt"
    patch_path = ROOT / "build/patches" / PATCH_NAME
    for path in (release_path, patch_list_path, patch_path, ROOT / "LICENSE"):
        if not path.is_file():
            fail(f"required upstream or MVM file is missing: {path.relative_to(ROOT)}")

    version = release_path.read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+\.\d+", version):
        fail(f"build/RELEASE is not a four-part Chromium version: {version!r}")

    lines = patch_list_path.read_text(encoding="utf-8").splitlines()
    entries = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    if entries.count("Bromite-package-name.patch") != 1:
        fail("expected exactly one upstream Bromite-package-name.patch entry")
    if entries.count(PATCH_NAME) != 1:
        fail(f"expected exactly one {PATCH_NAME} entry")
    if entries.index(PATCH_NAME) <= entries.index("Bromite-package-name.patch"):
        fail("MVM package overlay must run after the upstream package-name patch")
    if entries[-1] != PATCH_NAME:
        fail("MVM package overlay must remain after all current upstream patches")

    patch = patch_path.read_text(encoding="utf-8")
    required = (
        "diff --git a/chrome/android/chrome_public_apk_tmpl.gni b/chrome/android/chrome_public_apk_tmpl.gni",
        '-  chrome_public_manifest_package = "org.bromite.bromite"',
        f'+  chrome_public_manifest_package = "{PACKAGE_ID}"',
        "License: GPL-3.0-only",
    )
    for marker in required:
        if marker not in patch:
            fail(f"MVM package patch does not contain expected marker: {marker}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8", errors="replace")
    if "GNU GENERAL PUBLIC LICENSE" not in license_text and "GNU General Public License" not in license_text:
        fail("upstream LICENSE no longer looks like a GPL license; review obligations")

    print(f"PASS: Chromium source base version is {version}")
    print(f"PASS: {PATCH_NAME} is listed exactly once after the upstream package patch")
    print(f"PASS: downstream Android package ID is {PACKAGE_ID}")
    print("NOTE: this is a static patch-stack check; it does not compile Chromium or apply the patch to a full source checkout.")


if __name__ == "__main__":
    main()
