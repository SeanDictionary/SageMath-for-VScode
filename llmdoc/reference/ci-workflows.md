# CI/CD Workflows Reference

## 1. Core Summary

GitHub Actions workflows for continuous integration, testing, packaging, and release automation. CI runs on push/PR to main/master; release triggers on version tags or manual dispatch. Includes Dependabot for automated dependency updates.

## 2. Source of Truth

- **CI Workflow**: `.github/workflows/ci.yml` - Lint, format, build, test matrix (Node 18/20, Python 3.10/3.11/3.12), and package
- **Release Workflow**: `.github/workflows/release.yml` - Version validation, multi-marketplace publishing, pre-release support
- **Dependabot**: `.github/dependabot.yml` - Automated dependency updates (npm weekly, pip weekly, GitHub Actions monthly)
- **Issue Templates**: `.github/ISSUE_TEMPLATE/` - Structured bug report and feature request forms
- **PR Template**: `.github/PULL_REQUEST_TEMPLATE.md` - Standardized pull request checklist
- **Package Scripts**: `package.json` - NPM scripts used by CI

## CI Workflow (`.github/workflows/ci.yml`)

**Trigger**: Push to `main`/`master`, pull requests to `main`/`master`

**Jobs**:
1. **lint-and-format**: Format check (`npm run format:check`), ESLint (`npm run lint`)
2. **build**: Matrix (Node 18.x, 20.x) - `npm ci`, `npm run compile`, `xvfb-run -a npm test`
3. **python-tests**: Matrix (Python 3.10, 3.11, 3.12) - `uv sync --dev`, `uv run pytest tests/ -v`
4. **package**: Node 20.x - `vsce package --no-yarn`, upload VSIX artifact (7-day retention)

## Release Workflow (`.github/workflows/release.yml`)

**Triggers**:
- Push tags matching `v*` (e.g., `v1.3.0`)
- Manual workflow dispatch (supports pre-release suffix, dry-run mode)

**Jobs**:
1. **validate**: Version matching (package.json vs pyproject.toml), tag validation, CHANGELOG check
2. **test**: Lint, TypeScript compile, TypeScript tests, Python tests
3. **build**: Package extension, upload VSIX artifact (30-day retention)
4. **release**: Create GitHub Release with VSIX, auto-generate notes
5. **publish**: VS Code Marketplace (`VSCE_PAT`), Open VSX Registry (`OVSX_PAT`) - skipped for pre-releases
6. **notify**: Summary of release status

**Secrets Required**:
- `VSCE_PAT` - VS Code Marketplace Personal Access Token
- `OVSX_PAT` - Open VSX Registry Personal Access Token

## Dependabot (`.github/dependabot.yml`)

**Update Schedule**:
- **npm**: Weekly (Monday), 10 concurrent PRs, labels: `dependencies`, `npm`
- **pip** (src/server): Weekly (Monday), 5 concurrent PRs, labels: `dependencies`, `python`
- **GitHub Actions**: Monthly, labels: `dependencies`, `github-actions`

**Commit Format**: `chore(deps)` prefix

## Issue and PR Templates

**Bug Report** (`.github/ISSUE_TEMPLATE/bug_report.yml`):
- Description, reproduction steps, expected/actual behavior
- OS, VS Code version, extension version, SageMath version
- Log output, additional context

**Feature Request** (`.github/ISSUE_TEMPLATE/feature_request.yml`):
- Problem statement, proposed solution, alternatives
- Feature category (syntax/semantic highlighting, LSP, execution, Conda, UI/UX, docs)
- Contribution willingness

**Pull Request** (`.github/PULL_REQUEST_TEMPLATE.md`):
- Description, issue reference, change type
- Changes list, testing methodology, checklist
