# CI/CD Workflows Reference

## 1. Core Summary

GitHub Actions workflows for continuous integration, testing, packaging, and release automation. CI runs on push/PR to main branches; release triggers on version tags.

## 2. Source of Truth

- **CI Workflow**: `.github/workflows/ci.yml` - Build, test, and packaging pipeline
- **Release Workflow**: `.github/workflows/release.yml` - Marketplace publishing pipeline
- **Package Scripts**: `package.json:140-150` - NPM scripts used by CI

## Workflow: CI (`.github/workflows/ci.yml`)

**Trigger**: Push to `main`/`master`, pull requests to `main`/`master`

**Build Job**:
- Matrix: Node 18.x, 20.x
- Steps: Checkout, Setup Node, `npm ci`, `npm run lint`, `npm run compile`, `xvfb-run -a npm test`

**Package Job** (depends on build):
- Node 20.x
- Steps: Checkout, Setup Node, `npm ci`, Install `@vscode/vsce`, `vsce package`, Upload VSIX artifact

## Workflow: Release (`.github/workflows/release.yml`)

**Trigger**: Push tags matching `v*` (e.g., `v1.1.3`)

**Steps**:
1. Checkout, Setup Node 20.x, `npm ci`
2. `npm run compile`
3. `vsce package`
4. Create GitHub Release with VSIX artifact
5. Publish to VS Code Marketplace (`VSCE_PAT` required)
6. Publish to Open VSX Registry (`OVSX_PAT` required)

**Secrets Required**:
- `VSCE_PAT` - VS Code Marketplace Personal Access Token
- `OVSX_PAT` - Open VSX Registry Personal Access Token
- `GITHUB_TOKEN` - Auto-provided for releases
