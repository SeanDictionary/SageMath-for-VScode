import * as vscode from 'vscode';
import { exec } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';
import * as os from 'os';

// ============== Types ==============

export interface SageInstallation {
    path: string;
    version?: string;
    type: 'system' | 'conda' | 'homebrew' | 'windows-installer' | 'manual' | 'wsl';
    isValid: boolean;
}

export interface DiscoveryResult {
    installations: SageInstallation[];
    recommended?: SageInstallation;
}

export interface InstallationGuide {
    platform: string;
    methods: InstallMethod[];
}

export interface InstallMethod {
    name: string;
    description: string;
    commands?: string[];
    url?: string;
    recommended?: boolean;
}

// ============== Platform Detection ==============

export function getPlatform(): 'windows' | 'macos' | 'linux' {
    switch (process.platform) {
        case 'win32': return 'windows';
        case 'darwin': return 'macos';
        default: return 'linux';
    }
}

// ============== Common Installation Paths ==============

function getCommonSagePaths(): string[] {
    const platform = getPlatform();
    const home = os.homedir();
    const paths: string[] = [];

    switch (platform) {
        case 'windows':
            // Windows common paths
            paths.push(
                // Conda environments (common locations)
                join(home, 'miniconda3', 'Scripts', 'sage.exe'),
                join(home, 'anaconda3', 'Scripts', 'sage.exe'),
                join(home, 'miniconda3', 'envs', 'sage', 'Scripts', 'sage.exe'),
                join(home, 'anaconda3', 'envs', 'sage', 'Scripts', 'sage.exe'),
                // Mambaforge
                join(home, 'mambaforge', 'Scripts', 'sage.exe'),
                join(home, 'mambaforge', 'envs', 'sage', 'Scripts', 'sage.exe'),
                // ProgramData conda
                'C:\\ProgramData\\miniconda3\\Scripts\\sage.exe',
                'C:\\ProgramData\\anaconda3\\Scripts\\sage.exe',
                // Cygwin
                'C:\\cygwin64\\usr\\bin\\sage',
                // WSL (checked separately)
            );
            break;

        case 'macos':
            // macOS common paths
            paths.push(
                // Homebrew
                '/opt/homebrew/bin/sage',
                '/usr/local/bin/sage',
                // Conda
                join(home, 'miniconda3', 'bin', 'sage'),
                join(home, 'anaconda3', 'bin', 'sage'),
                join(home, 'miniforge3', 'bin', 'sage'),
                join(home, 'mambaforge', 'bin', 'sage'),
                join(home, 'miniconda3', 'envs', 'sage', 'bin', 'sage'),
                join(home, 'anaconda3', 'envs', 'sage', 'bin', 'sage'),
                // App bundle
                '/Applications/SageMath/sage',
                '/Applications/SageMath-*.app/Contents/Resources/sage/sage',
                // System
                '/usr/bin/sage',
            );
            break;

        case 'linux':
            // Linux common paths
            paths.push(
                // System packages
                '/usr/bin/sage',
                '/usr/local/bin/sage',
                // Conda
                join(home, 'miniconda3', 'bin', 'sage'),
                join(home, 'anaconda3', 'bin', 'sage'),
                join(home, 'miniforge3', 'bin', 'sage'),
                join(home, 'mambaforge', 'bin', 'sage'),
                join(home, 'miniconda3', 'envs', 'sage', 'bin', 'sage'),
                join(home, 'anaconda3', 'envs', 'sage', 'bin', 'sage'),
                // Local installation
                join(home, 'sage', 'sage'),
                join(home, 'SageMath', 'sage'),
                '/opt/sage/sage',
                '/opt/sagemath/sage',
            );
            break;
    }

    return paths;
}

// ============== Path Validation ==============

export async function validateSagePath(sagePath: string): Promise<{ valid: boolean; version?: string; error?: string }> {
    return new Promise((resolve) => {
        if (!sagePath) {
            resolve({ valid: false, error: 'Path is empty' });
            return;
        }

        // Check if file exists (for absolute paths)
        if (sagePath !== 'sage' && !existsSync(sagePath)) {
            resolve({ valid: false, error: `File not found: ${sagePath}` });
            return;
        }

        // Try to get version
        const command = `"${sagePath}" --version`;
        exec(command, { timeout: 30000 }, (error, stdout, _stderr) => {
            if (error) {
                // Try alternative version check
                exec(`"${sagePath}" -c "print(version())"`, { timeout: 30000 }, (error2, stdout2) => {
                    if (error2) {
                        resolve({ valid: false, error: `Cannot execute SageMath: ${error.message}` });
                    } else {
                        const version = stdout2.trim();
                        resolve({ valid: true, version });
                    }
                });
                return;
            }

            const versionMatch = stdout.match(/SageMath version ([\d.]+)/i) || 
                                stdout.match(/sage-?([\d.]+)/i);
            const version = versionMatch ? versionMatch[1] : stdout.trim().split('\n')[0];
            resolve({ valid: true, version });
        });
    });
}

// ============== Discovery Functions ==============

export async function discoverSageInstallations(): Promise<DiscoveryResult> {
    const installations: SageInstallation[] = [];
    const checkedPaths = new Set<string>();

    // 1. Check PATH environment
    const pathInstall = await findSageInPath();
    if (pathInstall) {
        installations.push(pathInstall);
        checkedPaths.add(pathInstall.path);
    }

    // 2. Check Conda environments
    const condaInstalls = await findSageInConda();
    for (const install of condaInstalls) {
        if (!checkedPaths.has(install.path)) {
            installations.push(install);
            checkedPaths.add(install.path);
        }
    }

    // 3. Check common paths
    const commonPaths = getCommonSagePaths();
    for (const path of commonPaths) {
        if (!checkedPaths.has(path) && existsSync(path)) {
            const validation = await validateSagePath(path);
            if (validation.valid) {
                installations.push({
                    path,
                    version: validation.version,
                    type: detectInstallationType(path),
                    isValid: true
                });
                checkedPaths.add(path);
            }
        }
    }

    // 4. Check WSL on Windows
    if (getPlatform() === 'windows') {
        const wslInstall = await findSageInWSL();
        if (wslInstall && !checkedPaths.has(wslInstall.path)) {
            installations.push(wslInstall);
        }
    }

    // Determine recommended installation
    const recommended = selectRecommendedInstallation(installations);

    return { installations, recommended };
}

async function findSageInPath(): Promise<SageInstallation | null> {
    return new Promise((resolve) => {
        const command = getPlatform() === 'windows' ? 'where sage' : 'which sage';
        exec(command, (error, stdout) => {
            if (error || !stdout.trim()) {
                resolve(null);
                return;
            }

            const sagePath = stdout.trim().split('\n')[0];
            validateSagePath(sagePath).then(validation => {
                if (validation.valid) {
                    resolve({
                        path: sagePath,
                        version: validation.version,
                        type: 'system',
                        isValid: true
                    });
                } else {
                    resolve(null);
                }
            });
        });
    });
}

export async function findSageInConda(): Promise<SageInstallation[]> {

    return new Promise((resolve) => {
        exec('conda env list --json', (error, stdout) => {
            if (error) {
                resolve([]);
                return;
            }

            try {
                const data = JSON.parse(stdout);
                if (data.envs) {
                    const promises = data.envs.map(async (envPath: string) => {
                        const platform = getPlatform();
                        const sagePath = platform === 'windows'
                            ? join(envPath, 'Scripts', 'sage.exe')
                            : join(envPath, 'bin', 'sage');

                        if (existsSync(sagePath)) {
                            const validation = await validateSagePath(sagePath);
                            if (validation.valid) {
                                return {
                                    path: sagePath,
                                    version: validation.version,
                                    type: 'conda' as const,
                                    isValid: true
                                };
                            }
                        }
                        return null;
                    });

                    Promise.all(promises).then(results => {
                        resolve(results.filter((r): r is SageInstallation => r !== null));
                    });
                } else {
                    resolve([]);
                }
            } catch {
                resolve([]);
            }
        });
    });
}

async function findSageInWSL(): Promise<SageInstallation | null> {
    return new Promise((resolve) => {
        exec('wsl which sage', { timeout: 10000 }, (error, stdout) => {
            if (error || !stdout.trim()) {
                resolve(null);
                return;
            }

            // WSL sage found - create a wrapper path
            const wslPath = 'wsl sage';
            resolve({
                path: wslPath,
                version: undefined,
                type: 'wsl',
                isValid: true
            });
        });
    });
}

function detectInstallationType(path: string): SageInstallation['type'] {
    const lowerPath = path.toLowerCase();
    
    if (lowerPath.includes('conda') || lowerPath.includes('miniforge') || lowerPath.includes('mambaforge')) {
        return 'conda';
    }
    if (lowerPath.includes('homebrew') || lowerPath.includes('/opt/homebrew')) {
        return 'homebrew';
    }
    if (lowerPath.includes('wsl')) {
        return 'wsl';
    }
    if (lowerPath.includes('program files') || lowerPath.includes('programdata')) {
        return 'windows-installer';
    }
    if (lowerPath.includes('/usr/bin') || lowerPath.includes('/usr/local/bin')) {
        return 'system';
    }
    return 'manual';
}

function selectRecommendedInstallation(installations: SageInstallation[]): SageInstallation | undefined {
    if (installations.length === 0) {
        return undefined;
    }
    if (installations.length === 1) {
        return installations[0];
    }

    // Priority: conda > homebrew > system > manual > wsl
    const priority: Record<string, number> = {
        'conda': 1,
        'homebrew': 2,
        'system': 3,
        'manual': 4,
        'windows-installer': 5,
        'wsl': 6
    };

    return installations.sort((a, b) => {
        const priorityDiff = priority[a.type] - priority[b.type];
        if (priorityDiff !== 0) {
            return priorityDiff;
        }
        
        // Prefer newer versions
        if (a.version && b.version) {
            return b.version.localeCompare(a.version, undefined, { numeric: true });
        }
        return 0;
    })[0];
}

// ============== Installation Guides ==============

export function getInstallationGuide(): InstallationGuide {
    const platform = getPlatform();

    switch (platform) {
        case 'windows':
            return {
                platform: 'Windows',
                methods: [
                    {
                        name: 'Conda (Recommended)',
                        description: 'Install via Conda/Mamba package manager - best Windows experience',
                        commands: [
                            'conda create -n sage sage -c conda-forge',
                            'conda activate sage'
                        ],
                        recommended: true
                    },
                    {
                        name: 'WSL (Windows Subsystem for Linux)',
                        description: 'Run SageMath in WSL for full Linux compatibility',
                        commands: [
                            'wsl --install',
                            'wsl sudo apt update && sudo apt install sagemath'
                        ]
                    },
                    {
                        name: 'Download Installer',
                        description: 'Download pre-built SageMath for Windows',
                        url: 'https://github.com/sagemath/sage-windows/releases'
                    }
                ]
            };

        case 'macos':
            return {
                platform: 'macOS',
                methods: [
                    {
                        name: 'Homebrew (Recommended)',
                        description: 'Install via Homebrew package manager',
                        commands: [
                            'brew install --cask sage'
                        ],
                        recommended: true
                    },
                    {
                        name: 'Conda',
                        description: 'Install via Conda/Mamba package manager',
                        commands: [
                            'conda create -n sage sage -c conda-forge',
                            'conda activate sage'
                        ]
                    },
                    {
                        name: 'Download App',
                        description: 'Download SageMath.app from official website',
                        url: 'https://www.sagemath.org/download-mac.html'
                    }
                ]
            };

        case 'linux':
        default:
            return {
                platform: 'Linux',
                methods: [
                    {
                        name: 'System Package Manager (Recommended)',
                        description: 'Install via your distribution package manager',
                        commands: [
                            '# Ubuntu/Debian:',
                            'sudo apt update && sudo apt install sagemath',
                            '',
                            '# Fedora:',
                            'sudo dnf install sagemath',
                            '',
                            '# Arch Linux:',
                            'sudo pacman -S sagemath'
                        ],
                        recommended: true
                    },
                    {
                        name: 'Conda',
                        description: 'Install via Conda/Mamba package manager',
                        commands: [
                            'conda create -n sage sage -c conda-forge',
                            'conda activate sage'
                        ]
                    },
                    {
                        name: 'Build from Source',
                        description: 'Build SageMath from source code',
                        url: 'https://doc.sagemath.org/html/en/installation/source.html'
                    }
                ]
            };
    }
}

// ============== Setup Wizard ==============

export async function runSetupWizard(_context: vscode.ExtensionContext): Promise<boolean> {
    // Step 1: Check if SageMath is already configured and valid
    const currentPath = vscode.workspace.getConfiguration('sagemath-for-vscode.sage').get<string>('path', 'sage');
    const validation = await validateSagePath(currentPath);
    
    if (validation.valid) {
        const action = await vscode.window.showInformationMessage(
            `✅ SageMath is already configured (${validation.version || 'version unknown'}).\n\nPath: ${currentPath}`,
            'Reconfigure',
            'Keep Current'
        );
        if (action !== 'Reconfigure') {
            return true;
        }
    }

    // Step 2: Auto-discover installations
    const discoverAction = await vscode.window.showInformationMessage(
        '🔍 SageMath Setup Wizard\n\nWould you like to automatically search for SageMath installations?',
        'Auto-Discover',
        'Manual Setup',
        'Installation Guide'
    );

    if (discoverAction === 'Installation Guide') {
        await showInstallationGuide();
        return false;
    }

    if (discoverAction === 'Manual Setup') {
        return await manualSetup();
    }

    // Auto-discover
    const result = await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: '🔍 Searching for SageMath installations...',
        cancellable: false
    }, async () => {
        return await discoverSageInstallations();
    });

    if (result.installations.length === 0) {
        // No installations found
        const action = await vscode.window.showWarningMessage(
            '⚠️ No SageMath installation found on your system.',
            'View Installation Guide',
            'Manual Setup',
            'Cancel'
        );

        if (action === 'View Installation Guide') {
            await showInstallationGuide();
        } else if (action === 'Manual Setup') {
            return await manualSetup();
        }
        return false;
    }

    // Found installations - let user choose
    if (result.installations.length === 1) {
        const install = result.installations[0];
        const action = await vscode.window.showInformationMessage(
            `✅ Found SageMath installation:\n\n` +
            `Path: ${install.path}\n` +
            `Version: ${install.version || 'Unknown'}\n` +
            `Type: ${install.type}`,
            'Use This',
            'Manual Setup'
        );

        if (action === 'Use This') {
            await applyInstallation(install);
            return true;
        } else if (action === 'Manual Setup') {
            return await manualSetup();
        }
        return false;
    }

    // Multiple installations found
    const items = result.installations.map(install => ({
        label: install.type === result.recommended?.type ? `$(star) ${install.path}` : install.path,
        description: `${install.version || 'Unknown version'} (${install.type})`,
        detail: install === result.recommended ? 'Recommended' : undefined,
        installation: install
    }));

    const selected = await vscode.window.showQuickPick(items, {
        placeHolder: 'Select SageMath installation to use',
        title: 'Multiple SageMath Installations Found'
    });

    if (selected) {
        await applyInstallation(selected.installation);
        return true;
    }

    return false;
}

async function applyInstallation(install: SageInstallation): Promise<void> {
    const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
    
    // Set the path
    await config.update('path', install.path, vscode.ConfigurationTarget.Global);
    
    // If it's a conda installation, also set the conda env path
    if (install.type === 'conda') {
        const envPath = install.path.includes('Scripts') 
            ? install.path.replace(/[/\\]Scripts[/\\]sage(\.exe)?$/i, '')
            : install.path.replace(/[/\\]bin[/\\]sage$/i, '');
        await config.update('condaEnvPath', envPath, vscode.ConfigurationTarget.Global);
    }

    vscode.window.showInformationMessage(
        `SageMath configured successfully! Path: ${install.path} Version: ${install.version || 'Unknown'}`
    );
}

async function manualSetup(): Promise<boolean> {
    const options: vscode.OpenDialogOptions = {
        canSelectMany: false,
        openLabel: 'Select SageMath Executable',
        filters: getPlatform() === 'windows' 
            ? { 'Executable': ['exe', 'bat', 'cmd'], 'All Files': ['*'] }
            : { 'All Files': ['*'] }
    };

    const fileUri = await vscode.window.showOpenDialog(options);
    if (!fileUri || fileUri.length === 0) {
        return false;
    }

    const sagePath = fileUri[0].fsPath;
    
    // Validate the selected path
    const validation = await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: '🔍 Validating SageMath installation...',
        cancellable: false
    }, async () => {
        return await validateSagePath(sagePath);
    });

    if (!validation.valid) {
        const retry = await vscode.window.showErrorMessage(
            `❌ Invalid SageMath installation: ${validation.error}`,
            'Try Again',
            'Use Anyway',
            'Cancel'
        );

        if (retry === 'Try Again') {
            return await manualSetup();
        } else if (retry === 'Use Anyway') {
            await vscode.workspace.getConfiguration('sagemath-for-vscode.sage')
                .update('path', sagePath, vscode.ConfigurationTarget.Global);
            vscode.window.showWarningMessage(`⚠️ SageMath path set to: ${sagePath} (unvalidated)`);
            return true;
        }
        return false;
    }

    await applyInstallation({
        path: sagePath,
        version: validation.version,
        type: detectInstallationType(sagePath),
        isValid: true
    });

    return true;
}

async function showInstallationGuide(): Promise<void> {
    const guide = getInstallationGuide();
    
    const items = guide.methods.map(method => ({
        label: method.recommended ? `$(star) ${method.name}` : method.name,
        description: method.description,
        detail: method.commands?.join(' | ') || method.url,
        method
    }));

    const selected = await vscode.window.showQuickPick(items, {
        placeHolder: `Select installation method for ${guide.platform}`,
        title: `🚀 SageMath Installation Guide - ${guide.platform}`
    });

    if (selected) {
        await showMethodDetails(selected.method);
    }
}

async function showMethodDetails(method: InstallMethod): Promise<void> {
    const panel = vscode.window.createWebviewPanel(
        'sagemathInstallGuide',
        `Install SageMath - ${method.name}`,
        vscode.ViewColumn.One,
        { enableScripts: true }
    );

    const commandsHtml = method.commands 
        ? method.commands.map(cmd => 
            cmd.startsWith('#') 
                ? `<p class="comment">${cmd}</p>` 
                : cmd === '' 
                    ? '<br>' 
                    : `<code class="command">${cmd}</code>`
        ).join('\n')
        : '';

    const urlHtml = method.url 
        ? `<p><a href="${method.url}" class="link">📥 Download from official website</a></p>`
        : '';

    panel.webview.html = `<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            font-family: var(--vscode-font-family); 
            padding: 20px; 
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
        }
        h1 { color: var(--vscode-textLink-foreground); }
        .description { 
            margin: 16px 0; 
            padding: 12px;
            background: var(--vscode-textBlockQuote-background);
            border-left: 4px solid var(--vscode-textLink-foreground);
        }
        .command { 
            display: block;
            background: var(--vscode-terminal-background);
            color: var(--vscode-terminal-foreground);
            padding: 8px 12px;
            margin: 8px 0;
            border-radius: 4px;
            font-family: var(--vscode-editor-font-family);
            cursor: pointer;
        }
        .command:hover {
            background: var(--vscode-list-hoverBackground);
        }
        .comment { 
            color: var(--vscode-descriptionForeground);
            font-style: italic;
            margin: 16px 0 4px 0;
        }
        .link { 
            color: var(--vscode-textLink-foreground);
            text-decoration: none;
            padding: 8px 16px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border-radius: 4px;
            display: inline-block;
            margin: 16px 0;
        }
        .link:hover { background: var(--vscode-button-hoverBackground); }
        .tip {
            margin-top: 24px;
            padding: 12px;
            background: var(--vscode-inputValidation-infoBackground);
            border: 1px solid var(--vscode-inputValidation-infoBorder);
            border-radius: 4px;
        }
        .copy-hint {
            font-size: 0.85em;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 8px;
        }
    </style>
</head>
<body>
    <h1>🚀 ${method.name}</h1>
    <div class="description">${method.description}</div>
    
    ${method.commands ? '<p class="copy-hint">💡 Click on a command to copy it to clipboard</p>' : ''}
    ${commandsHtml}
    ${urlHtml}
    
    <div class="tip">
        <strong>💡 After installation:</strong><br>
        1. Close and reopen VS Code<br>
        2. Run command: <code>SageMath: Setup Wizard</code><br>
        3. The extension will auto-detect your new installation
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        document.querySelectorAll('.command').forEach(el => {
            el.addEventListener('click', () => {
                navigator.clipboard.writeText(el.textContent);
                el.style.background = 'var(--vscode-inputValidation-infoBackground)';
                setTimeout(() => {
                    el.style.background = '';
                }, 500);
            });
        });
    </script>
</body>
</html>`;
}

// ============== Status Check Command ==============

export async function checkSageStatus(): Promise<void> {
    const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
    const sagePath = config.get<string>('path', 'sage');
    const condaEnvPath = config.get<string>('condaEnvPath', '');

    const validation = await vscode.window.withProgress({
        location: vscode.ProgressLocation.Notification,
        title: '🔍 Checking SageMath status...',
        cancellable: false
    }, async () => {
        return await validateSagePath(sagePath);
    });

    const statusItems = [
        `**Path:** ${sagePath}`,
        `**Status:** ${validation.valid ? '✅ Valid' : '❌ Invalid'}`,
        validation.version ? `**Version:** ${validation.version}` : null,
        validation.error ? `**Error:** ${validation.error}` : null,
        condaEnvPath ? `**Conda Env:** ${condaEnvPath}` : null
    ].filter(Boolean).join('\n');

    if (validation.valid) {
        vscode.window.showInformationMessage(
            `SageMath Status\n\n${statusItems}`,
            'OK'
        );
    } else {
        const action = await vscode.window.showErrorMessage(
            `SageMath Status\n\n${statusItems}`,
            'Run Setup Wizard',
            'View Installation Guide'
        );

        if (action === 'Run Setup Wizard') {
            vscode.commands.executeCommand('sagemath-for-vscode.setupWizard');
        } else if (action === 'View Installation Guide') {
            await showInstallationGuide();
        }
    }
}
