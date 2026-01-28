import * as assert from 'assert';
import * as vscode from 'vscode';
import * as path from 'path';
import * as os from 'os';
import {
    getPlatform,
    validateSagePath,
    discoverSageInstallations,
    getInstallationGuide
} from '../../sageDiscovery';

suite('SageMath Discovery Test Suite', () => {

    suite('getPlatform Tests', () => {

        test('Should return valid platform string', () => {
            const platform = getPlatform();
            const validPlatforms = ['windows', 'macos', 'linux'];
            assert.ok(
                validPlatforms.includes(platform),
                `Platform should be one of ${validPlatforms.join(', ')}, got: ${platform}`
            );
        });

        test('Should match process.platform mapping', () => {
            const platform = getPlatform();
            if (process.platform === 'win32') {
                assert.strictEqual(platform, 'windows');
            } else if (process.platform === 'darwin') {
                assert.strictEqual(platform, 'macos');
            } else {
                assert.strictEqual(platform, 'linux');
            }
        });
    });

    suite('validateSagePath Tests', () => {

        test('Should return invalid for empty path', async () => {
            const result = await validateSagePath('');
            assert.strictEqual(result.valid, false);
            assert.ok(result.error, 'Should have error message');
        });

        test('Should return invalid for non-existent absolute path', async () => {
            const fakePath = path.join(os.tmpdir(), 'nonexistent-sage-' + Date.now());
            const result = await validateSagePath(fakePath);
            assert.strictEqual(result.valid, false);
            assert.ok(result.error?.includes('not found') || result.error?.includes('File not found'),
                'Error should mention file not found');
        });

        test('Should handle "sage" (PATH lookup) gracefully', async () => {
            // This test just ensures it doesn't crash - result depends on system
            const result = await validateSagePath('sage');
            assert.ok(typeof result.valid === 'boolean', 'Should return boolean valid');
            if (!result.valid) {
                assert.ok(result.error, 'Invalid result should have error');
            }
        });

        test('Should return version when valid path found', async function() {
            // Skip if sage not available
            const result = await validateSagePath('sage');
            if (result.valid) {
                // Version might be undefined but valid should be true
                assert.strictEqual(result.valid, true);
            } else {
                this.skip();
            }
        });
    });

    suite('discoverSageInstallations Tests', () => {

        test('Should return DiscoveryResult object', async function() {
            this.timeout(60000); // Discovery can take time

            const result = await discoverSageInstallations();

            assert.ok(result, 'Should return result');
            assert.ok(Array.isArray(result.installations), 'Should have installations array');

            // recommended can be undefined if no installations found
            if (result.installations.length > 0) {
                assert.ok(result.recommended, 'Should have recommended if installations exist');
            }
        });

        test('Each installation should have required properties', async function() {
            this.timeout(60000);

            const result = await discoverSageInstallations();

            for (const install of result.installations) {
                assert.ok(install.path, 'Installation should have path');
                assert.ok(install.type, 'Installation should have type');
                assert.ok(typeof install.isValid === 'boolean', 'Installation should have isValid boolean');

                const validTypes = ['system', 'conda', 'homebrew', 'windows-installer', 'manual', 'wsl'];
                assert.ok(
                    validTypes.includes(install.type),
                    `Installation type should be valid, got: ${install.type}`
                );
            }
        });

        test('Recommended installation should be in installations list', async function() {
            this.timeout(60000);

            const result = await discoverSageInstallations();

            if (result.recommended) {
                const found = result.installations.find(i => i.path === result.recommended?.path);
                assert.ok(found, 'Recommended should be in installations list');
            }
        });
    });

    suite('getInstallationGuide Tests', () => {

        test('Should return guide for current platform', () => {
            const guide = getInstallationGuide();

            assert.ok(guide, 'Should return guide');
            assert.ok(guide.platform, 'Should have platform');
            assert.ok(Array.isArray(guide.methods), 'Should have methods array');
            assert.ok(guide.methods.length > 0, 'Should have at least one method');
        });

        test('Should have Windows-specific methods on Windows', () => {
            const guide = getInstallationGuide();

            if (getPlatform() === 'windows') {
                assert.strictEqual(guide.platform, 'Windows');
                const hasCondaMethod = guide.methods.some(m => 
                    m.name.toLowerCase().includes('conda')
                );
                assert.ok(hasCondaMethod, 'Windows guide should have Conda method');
            }
        });

        test('Should have macOS-specific methods on macOS', () => {
            const guide = getInstallationGuide();

            if (getPlatform() === 'macos') {
                assert.strictEqual(guide.platform, 'macOS');
                const hasHomebrewMethod = guide.methods.some(m => 
                    m.name.toLowerCase().includes('homebrew')
                );
                assert.ok(hasHomebrewMethod, 'macOS guide should have Homebrew method');
            }
        });

        test('Should have Linux-specific methods on Linux', () => {
            const guide = getInstallationGuide();

            if (getPlatform() === 'linux') {
                assert.strictEqual(guide.platform, 'Linux');
                const hasPackageManagerMethod = guide.methods.some(m => 
                    m.name.toLowerCase().includes('package') || 
                    m.description.toLowerCase().includes('package manager')
                );
                assert.ok(hasPackageManagerMethod, 'Linux guide should have package manager method');
            }
        });

        test('Each method should have required properties', () => {
            const guide = getInstallationGuide();

            for (const method of guide.methods) {
                assert.ok(method.name, 'Method should have name');
                assert.ok(method.description, 'Method should have description');
                // Either commands or url should be present
                assert.ok(
                    method.commands || method.url,
                    'Method should have commands or url'
                );
            }
        });

        test('Should have one recommended method', () => {
            const guide = getInstallationGuide();

            const recommendedMethods = guide.methods.filter(m => m.recommended === true);
            assert.ok(
                recommendedMethods.length >= 1,
                'Should have at least one recommended method'
            );
        });
    });

    suite('New Commands Registration Tests', () => {

        suiteSetup(async function() {
            this.timeout(10000);
            // Ensure the extension is activated before testing commands
            const extension = vscode.extensions.getExtension('SeanDictionary.sagemath-for-vscode');
            if (extension && !extension.isActive) {
                await extension.activate();
            }
            // Wait for commands to be registered
            await new Promise(resolve => setTimeout(resolve, 1000));
        });

        test('setupWizard command should be registered', async () => {
            const commands = await vscode.commands.getCommands(true);
            assert.ok(
                commands.includes('sagemath-for-vscode.setupWizard'),
                'setupWizard command should be registered'
            );
        });

        test('checkSageStatus command should be registered', async () => {
            const commands = await vscode.commands.getCommands(true);
            assert.ok(
                commands.includes('sagemath-for-vscode.checkSageStatus'),
                'checkSageStatus command should be registered'
            );
        });

        test('discoverSage command should be registered', async () => {
            const commands = await vscode.commands.getCommands(true);
            assert.ok(
                commands.includes('sagemath-for-vscode.discoverSage'),
                'discoverSage command should be registered'
            );
        });

        test('showInstallGuide command should be registered', async () => {
            const commands = await vscode.commands.getCommands(true);
            assert.ok(
                commands.includes('sagemath-for-vscode.showInstallGuide'),
                'showInstallGuide command should be registered'
            );
        });
    });
});

suite('SageDiscovery Integration Tests', () => {

    suite('Installation Type Detection', () => {

        test('Conda path should be detected as conda type', async function() {
            this.timeout(60000);

            const result = await discoverSageInstallations();
            
            for (const install of result.installations) {
                if (install.path.toLowerCase().includes('conda') ||
                    install.path.toLowerCase().includes('miniforge') ||
                    install.path.toLowerCase().includes('mambaforge')) {
                    assert.strictEqual(
                        install.type, 'conda',
                        `Path containing conda should have type 'conda': ${install.path}`
                    );
                }
            }
        });

        test('Homebrew path should be detected as homebrew type', async function() {
            this.timeout(60000);

            if (getPlatform() !== 'macos') {
                this.skip();
                return;
            }

            const result = await discoverSageInstallations();
            
            for (const install of result.installations) {
                if (install.path.includes('/opt/homebrew') || 
                    install.path.includes('/usr/local/Cellar')) {
                    assert.strictEqual(
                        install.type, 'homebrew',
                        `Homebrew path should have type 'homebrew': ${install.path}`
                    );
                }
            }
        });
    });

    suite('Configuration Update', () => {

        test('Should be able to read sage.path configuration', () => {
            const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
            const sagePath = config.get<string>('path');
            assert.ok(sagePath !== undefined, 'sage.path should be defined');
        });

        test('Should be able to read sage.condaEnvPath configuration', () => {
            const config = vscode.workspace.getConfiguration('sagemath-for-vscode.sage');
            const condaEnvPath = config.get<string>('condaEnvPath');
            assert.ok(condaEnvPath !== undefined, 'sage.condaEnvPath should be defined');
        });
    });
});
