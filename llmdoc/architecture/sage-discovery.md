# SageMath Discovery Architecture

## 1. Identity

- **What it is:** Cross-platform SageMath installation detection and setup wizard system.
- **Purpose:** Automates SageMath environment discovery, validation, and configuration for first-time users.

## 2. Core Components

- `src/sageDiscovery.ts` (discoverSageInstallations): Scans common paths for SageMath binaries across Windows, macOS, and Linux.
- `src/sageDiscovery.ts` (runSetupWizard): Multi-step wizard guiding users through SageMath setup and configuration.
- `src/sageDiscovery.ts` (checkSageStatus): Validates configured SageMath path and reports version/status.
- `src/sageDiscovery.ts` (getInstallationGuide): Platform-specific installation instructions with commands.
- `src/sageDiscovery.ts` (validateSagePath): Executes `sage --version` to verify installation validity.

## 3. Execution Flow (LLM Retrieval Map)

**Discovery Flow:**
- **Platform Detection:** Determines OS (windows/macos/linux) via `process.platform` (`src/sageDiscovery.ts:36-42`).
- **Path Generation:** Builds list of common installation paths including Conda, Homebrew, system paths, WSL (`src/sageDiscovery.ts:46-145`).
- **Validation:** Checks each path for existence using `existsSync()` and validates via `sage --version` (`src/sageDiscovery.ts:147-175`).
- **Recommendation:** Marks preferred installation (Conda > Homebrew > system) based on type and version (`src/sageDiscovery.ts:177-185`).
- **User Selection:** Displays QuickPick with discovered installations, auto-configures selected path (`src/extension.ts:357-383`).

**Setup Wizard Flow:**
- **Welcome:** Displays initial welcome message with option to proceed or cancel (`src/sageDiscovery.ts:195-220`).
- **Discovery Step:** Runs `discoverSageInstallations()` with progress notification (`src/sageDiscovery.ts:222-245`).
- **Configuration Step:** If installations found, prompts user to select; if none, offers installation guide (`src/sageDiscovery.ts:247-270`).
- **Completion:** Updates VS Code settings and confirms successful configuration (`src/sageDiscovery.ts:272-285`).

**Status Check Flow:**
- **Path Validation:** Retrieves configured SageMath path and checks file existence (`src/sageDiscovery.ts:300-310`).
- **Version Detection:** Executes `sage --version` command and parses output (`src/sageDiscovery.ts:287-298`).
- **Status Display:** Shows information message with version, location, and validity status (`src/sageDiscovery.ts:312-324`).

**Installation Guide Flow:**
- **Platform Selection:** Returns platform-specific installation methods (Conda, Docker, source) (`src/sageDiscovery.ts:329-380`).
- **Method Display:** Shows QuickPick with installation methods, descriptions, and commands (`src/extension.ts:392-401`).
- **Webview Panel:** Creates clickable webview with commands that copy to clipboard (`src/extension.ts:406-499`).

## 4. Design Rationale

- **Cross-Platform Support:** Separate path lists for Windows (Conda, Cygwin, WSL), macOS (Homebrew, Conda, app bundles), and Linux (system packages, Conda).
- **Non-Destructive:** Discovery only reads filesystem; never modifies SageMath installation.
- **Wizard Over Auto-Detection:** Interactive setup wizard preferred over silent auto-configuration to avoid unexpected changes.
- **Graceful Degradation:** If no SageMath found, provides installation guide instead of failing with error.
- **VS Code Settings Integration:** Configuration stored in global VS Code settings for persistence across workspaces.
