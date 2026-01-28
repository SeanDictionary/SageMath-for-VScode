# Contributing to SageMath for VScode

Thank you for considering contributing! This guide will help you get started.

## Code of Conduct

Please read our [Code of Conduct](../CODE_OF_CONDUCT.md) before contributing.

## Development Setup

### Prerequisites

- Node.js 18.x+, npm 9.x+
- SageMath installed
- VS Code 1.100.0+

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/SageMath-for-VScode.git
cd SageMath-for-VScode

# Install dependencies
npm install

# Compile
npm run compile

# Run linter
npm run lint
```

### Running the Extension

1. Open the project in VS Code
2. Press `F5` to launch Extension Development Host
3. Open a `.sage` file to test

## Project Structure

```
src/
├── extension.ts      # Main entry point
├── server/           # LSP server (Python)
│   ├── lsp.py
│   ├── utils.py
│   └── predefinition.py
└── test/             # Tests
```

## Commit Guidelines

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance

Example: `feat: add auto-completion for SageMath functions`

## Pull Request Process

1. Fork and create a feature branch
2. Make changes and add tests
3. Run `npm run lint` and `npm test`
4. Update documentation if needed
5. Submit PR with clear description

## Testing

```bash
# Run all tests
npm test

# Run linter
npm run lint
```

## Code Style

- Use TypeScript for extension code
- Follow existing code patterns
- Run Prettier before committing: `npm run format`

## Questions?

Open an issue or start a discussion on GitHub.
