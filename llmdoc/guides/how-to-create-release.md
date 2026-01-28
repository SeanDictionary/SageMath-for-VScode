# How to Create a Release

1. **Update Version**: Bump version in both `package.json` and `src/server/pyproject.toml` to matching values (e.g., `1.4.0`). Versions must align for release validation to pass.
2. **Update CHANGELOG**: Add entry for new version in `CHANGELOG.md` following Keep a Changelog format. Release workflow validates this exists (warns if missing).
3. **Commit Changes**: Commit version bump and CHANGELOG with conventional commit message: `chore: release version 1.4.0`.
4. **Push to Main**: Merge changes to `main` branch via pull request. Ensure CI passes all checks (lint, format, build, tests).
5. **Create Tag**: Run `git tag v1.4.0` and push with `git push origin v1.4.0`. This triggers the release workflow automatically.
6. **Monitor Release**: GitHub Actions runs validation, tests, build, release creation, and marketplace publishing. Check Actions tab for progress.
7. **Verify Release**: Confirm GitHub Release created at https://github.com/SeanDictionary/SageMath-for-VScode/releases with VSIX artifact attached.

## Manual Release (Alternative)

For manual control or pre-releases, use workflow dispatch:
1. Go to Actions → Release workflow
2. Click "Run workflow"
3. Select branch and optionally enter pre-release suffix (e.g., `beta.1`, `rc.2`)
4. Enable "dry run" to package without publishing
5. Monitor execution in Actions tab

## Pre-release Versions

For alpha/beta/rc releases, append suffix to version: `1.4.0-beta.1`. Pre-releases skip marketplace publishing but create GitHub Release. Use manual dispatch with pre-release input or tag pre-release version directly.
