# Git Conventions

This document provides a high-level summary and pointers to source-of-truth information about this project's git workflow and conventions.

## 1. Core Summary

This project follows a GitHub-centric workflow using pull requests for integration. Development occurs on feature branches (typically `dev`) which are merged into `main` via pull requests. Commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/) specification. Versioning follows semantic versioning with releases tagged in commit messages and documented in CHANGELOG.md.

## 2. Source of Truth

- **Primary Git Workflow:** `git log` - Evidence of PR-based merges from `dev` to `main` branches
- **Commit Message Format:** `docs/CONTRIBUTING.md` - Conventional Commits specification with defined types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`. Example: `feat: add auto-completion for SageMath functions`
- **Version Management:** `package.json` - Current version stored in version field (currently 1.3.0)
- **Release Documentation:** `CHANGELOG.md` - Maintained using Keep a Changelog format with semantic versioning
- **Branch Structure:** `git branch -a` - Main branches: `main` (production), `dev` (development), `rebuild` (build artifacts)
