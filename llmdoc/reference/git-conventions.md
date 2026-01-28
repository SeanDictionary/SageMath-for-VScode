# Git Conventions

This document provides a high-level summary and pointers to source-of-truth information about this project's git workflow and conventions.

## 1. Core Summary

This project follows a GitHub-centric workflow using pull requests for integration. Development occurs on feature branches (typically `dev`) which are merged into `main` via pull requests. Commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) specification. Versioning follows semantic versioning with releases tagged in commit messages and documented in CHANGELOG.md.

## 2. Source of Truth

- **Primary Git Workflow:** `git log` - Evidence of PR-based merges from `dev` to `main` branches
- **Commit Message Format:** `docs/CONTRIBUTING.md` - Conventional Commits specification with defined types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`. Example: `feat: add auto-completion for SageMath functions`
- **Version Management:** `package.json`, `src/server/pyproject.toml` - Version must match in both files for release
- **Release Documentation:** `CHANGELOG.md` - Maintained using Keep a Changelog format with semantic versioning
- **Branch Structure:** `git branch -a` - Main branches: `main` (production), `dev` (development), `rebuild` (build artifacts)
- **Issue Templates:** `.github/ISSUE_TEMPLATE/bug_report.yml`, `.github/ISSUE_TEMPLATE/feature_request.yml` - Structured issue reporting
- **PR Template:** `.github/PULL_REQUEST_TEMPLATE.md` - Standardized PR format with checklist
- **Release Automation:** `.github/workflows/release.yml` - Automated release and marketplace publishing
