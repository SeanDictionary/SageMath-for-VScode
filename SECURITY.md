# Security Policy

## Supported Versions

The following versions of SageMath for VScode are currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of SageMath for VScode seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to the maintainers or through GitHub's private vulnerability reporting feature:

1. Go to the [Security tab](https://github.com/SeanDictionary/SageMath-for-VScode/security) of the repository
2. Click "Report a vulnerability"
3. Fill out the form with details about the vulnerability

### What to Include

Please include the following information in your report:

- Type of issue (e.g., code injection, information disclosure, etc.)
- Full paths of source file(s) related to the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours, we will acknowledge receipt of your report
- **Status Update**: Within 7 days, we will provide an initial assessment
- **Resolution**: We aim to resolve critical vulnerabilities within 30 days

### What to Expect

- We will keep you informed of the progress towards fixing the vulnerability
- We will notify you when the vulnerability is fixed
- We will publicly acknowledge your responsible disclosure (unless you prefer to remain anonymous)

## Security Best Practices for Users

When using this extension:

1. **Keep the extension updated** to the latest version
2. **Only install from trusted sources** (VS Code Marketplace or official GitHub releases)
3. **Review the SageMath executable path** in settings to ensure it points to a legitimate installation
4. **Be cautious with untrusted `.sage` files** as they may execute arbitrary code when run

## Scope

This security policy applies to:

- The SageMath for VScode extension source code
- The bundled Language Server Protocol (LSP) implementation
- Any official releases published to VS Code Marketplace

This policy does not cover:

- SageMath itself (report issues to [SageMath](https://www.sagemath.org/))
- Third-party dependencies (report to respective maintainers)
- VS Code itself (report to [Microsoft](https://github.com/microsoft/vscode))
