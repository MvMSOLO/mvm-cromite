# MVM Browser source-fork plan

## Current source base

This repository is the MVM downstream fork of [Cromite](https://github.com/uazo/cromite), itself a Chromium-based browser. The fork began from upstream `master` at commit `3724efc6ede3d2d94611c1fe71d1b090ebbb40a7` on 2026-10-11. The checked-in `build/RELEASE` currently says `153.0.8010.37`; review upstream security freshness before any device test or release.

## First downstream code change

Four MVM-specific patches are now appended after the upstream Cromite patch stack in this order: `MVM-App-Icon.patch` replaces adaptive launcher art with a dark navy/cyan MVM monogram; `MVM-NTP-Branding.patch` adds a compact MVM signature to the native Android New Tab Page while preserving Chromium’s search box and site modules; `MVM-App-Label.patch` changes the app label from `Cromite` to `MVM Browser`; `MVM-Package-Name.patch` sets the Android package ID to `com.mvmsolo.mvmbrowser`, matching the current MVM Browser Gradle `applicationId`. The package-ID patch remains last. These are source patches only: the complete stack has not been applied to a full Chromium checkout, and no APK has been built or device-tested. Provider authorities, signing, and MVM feature-porting still require inspection and tests.

Run the quick static check with:

```bash
python3 tools/validate_mvm_patch_stack.py
```

GitHub Actions runs the same check. It verifies patch-list order and patch text only; it does not prove the patch applies to a complete Chromium checkout or that an APK builds.

## Downstream CI scope

The inherited upstream `Check git apply` workflow is a patch-rebase automation that downloads external helper tools and may run before a downstream build tree exists. It is excluded from `mvm-branding-bootstrap`; its latest inherited run failed during helper bootstrap before Chromium checkout or patch application, so that result is **not** evidence that the MVM package patch applies or fails. The `MVM Cromite overlay validation` workflow remains active and checks the static patch stack. A complete Chromium-source patch-apply check and a compiled ARM64 APK are still release gates.

## Build limitations

- Chromium/Cromite is a full browser source build, not an Android library that can be dropped into the current Kotlin WebView app.
- The release build workflow upstream uses custom runner labels and image-building steps. A fork does not inherit the upstream owner's private/self-hosted runners or secrets.
- Do not run a multi-hour build unless a suitable x86-64 Linux/Docker host with adequate disk/RAM is available and the image/source revision is pinned.
- The MVM Browser app in `MvMSOLO/mvmbrowser` still uses Android System WebView; this source fork does not replace that implementation yet.
- The tested upstream reference APK is not an MVM-branded APK and must not be relabeled or redistributed as one.

## License and security gates

Cromite's source identifies GPL-3.0 licensing for its patches. Preserve all copyright and third-party notices, evaluate source-availability obligations for any distributed derivative, and keep the exact Chromium revision, patch stack, build-image digest, GN args, signing identity, and artifact checksum with each build. The current base (`153.0.8010.37`) is not assumed to be the latest secure Chromium build; verify a fresher supported upstream revision before public release.

## Next implementation gates

1. Apply all four MVM overlays to the exact Cromite source revision and verify no patch conflicts.
2. Add and verify an MVM new-tab/start-page experience as a separate source change; do not rewrite unrelated upstream patches.
3. Run a source build on a suitable runner, inspect package metadata and signing, then install and manually smoke-test on Android 10+ ARM64.
4. Port MVM-specific tabs, saved pages, bookmarks/history, downloads, and ad/tracker controls with tests; do not claim feature parity until each item passes.
5. Keep this fork synchronized with upstream security updates and repeat the gates before distribution.
